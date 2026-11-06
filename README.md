# 电商商品知识库 RAG 问答系统

基于 **LangChain** 的企业级知识库问答系统，面向电商平台商品知识库。用户通过浏览器进行知识库管理与问答，问答时基于 **RAG（检索增强生成）** 引用知识库原文片段并展示溯源。

## 技术栈

| 层 | 技术 |
|---|---|
| 大模型 | 通义千问 Qwen（阿里云百炼 DashScope，`qwen3.8-max-0902`）|
| Embedding | 本地 BGE（bge-small-zh-v1.5，免费离线）|
| 向量库 | Chroma（本地持久化）|
| 数据库 | **PostgreSQL**（Docker 容器部署，企业级）|
| 后端 | Python + FastAPI + LangChain + SQLAlchemy |
| 认证 | JWT + bcrypt + RBAC 权限 |
| 前端 | React 18 + TypeScript + Vite + Ant Design 5 + Zustand |
| 压测 | Locust（模拟 100 并发用户）|
| 部署 | Docker Compose（postgres + backend + frontend）|

## 目录结构

```
├── backend/               # FastAPI 后端（RAG 核心）
│   ├── app/               # 源码：api / core / rag / services / models
│   ├── tests/             # pytest 单元测试
│   ├── report/            # 压测报告（Locust 生成的 HTML）
│   ├── locustfile.py      # 压测脚本
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/              # React 18 + TS 前端
├── sample_data/           # 测试用商品知识库样例
├── docker-compose.yml     # 企业级部署编排（postgres + backend + frontend）
├── 启动后端.bat / 启动前端.bat   # 一键启动脚本
└── README.md
```

## 快速开始

### 0. 启动 PostgreSQL（Docker）

```bash
# 前提：已安装 Docker Desktop
docker compose up -d postgres
```

这会拉取 `postgres:16` 镜像并启动 `rag_postgres` 容器（端口 5432，数据持久化在卷 `pgdata`）。

### 1. 后端

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   （Linux/Mac: source .venv/bin/activate）
pip install -r requirements.txt
# 复制 .env.example 为 .env，填入 DASHSCOPE_API_KEY
uvicorn app.main:app --reload --port 8000
```

后端接口文档：<http://127.0.0.1:8000/docs>

> 也可以直接双击项目根的 `启动后端.bat`。

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 <http://localhost:5173>（双击 `启动前端.bat` 亦可）。

### 3. 默认账号

- 管理员：`admin` / `123456`（可进入知识库管理页）
- 普通用户：自行在注册页注册

### 4. 测试流程

1. `admin/123456` 登录 → 「知识库管理」上传 `sample_data/` 下的样例文档
2. 注册普通用户 → 登录 → 「知识库问答」新建会话提问

## 环境变量（backend/.env）

| 变量 | 说明 |
|---|---|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key（必填）|
| `LLM_MODEL` | 大模型，默认 `qwen3.8-max-0902` |
| `EMBEDDING_MODEL` | 向量模型，默认 `BAAI/bge-small-zh-v1.5` |
| `DATABASE_URL` | 数据库连接，默认 PostgreSQL |
| `SECRET_KEY` | JWT 签名密钥（随机值）|
| `HF_ENDPOINT` | HuggingFace 镜像（国内必配）|

> ⚠️ `.env` 含密钥，已加入 `.gitignore`，请勿提交到 Git。

---

## 性能优化历程（压测驱动）

用 **Locust 模拟 100 个并发用户**对系统压测，经历了四轮优化：

| 阶段 | 方案 | 失败率 |
|---|---|---|
| 1. 初始（SQLite）| 数据库用 SQLite | **27.85%** |
| 2. 快速修复 | 聊天接口提前释放数据库连接 | 11.72% |
| 3. 根本解决 | 换 PostgreSQL（Docker 部署）| 1.95% |
| 4. 连接池调优 | 连接池 15 → 50 | **0.07%（≈0）** |

### 问题与定位

- **现象**：SQLite 下 100 并发出现大量 500 错误、响应时间飙到 30~87 秒。
- **根因**：
  1. 聊天接口在 LLM 流式生成期间（5~15 秒）一直占着数据库连接，把连接池占满；
  2. SQLite 是"单写锁"，同一时刻只允许一个写操作，并发写大量冲突。
- **解决**：① `chat.py` 在流式前 `db.close()` 释放连接；② 数据库换成 PostgreSQL（支持并发读写）；③ 连接池从 15 调到 50。

### 最终压测结果（PostgreSQL + 连接池 50）

100 在线用户、2 分钟：登录/会话 **0 失败**，RAG 问答 **264 次请求 0 失败**，总失败率 0.07%（2 次失败为压测停机时的客户端断连，非服务端错误）。

详细数据见 `backend/report/` 下的 4 份 HTML 报告。

---

## 避坑记录（开发过程中踩过的坑）

1. **huggingface.co 国内无法直连**：下载 BGE 模型超时（WinError 10060）。解法：配 `HF_ENDPOINT=https://hf-mirror.com` 镜像。
2. **阿里云百炼模型命名**：新模型叫 `qwen3.x` 系列（如 `qwen3.8-max-0902`），不是旧名 `qwen-plus`，写错会报"免费额度耗尽"误导。
3. **Docker 装到用户目录导致 `docker` 命令找不到**：Docker Desktop 装到了 `AppData\Local\Programs\DockerDesktop`，PATH 已配但需重启终端；Git Bash 里要用 `/c/...` 格式的 PATH，或直接用 `docker.exe` 完整路径。
4. **Docker 拉镜像报 `docker-credential-desktop not found`**：Docker 的凭据助手也在 bin 目录，需把 Docker bin 加进 PATH。
5. **Windows Git Bash 下 curl 传中文 JSON 会 GBK/UTF-8 乱码**导致 FastAPI 解析失败：改用 Python httpx 或写文件 `--data-binary @file`。
6. **Locust 的 `with client.post()` 必须带 `catch_response=True`**，否则报 `LocustError`。
