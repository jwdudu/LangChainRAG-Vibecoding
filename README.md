# 基于 LangChain 的电商商品知识库 RAG 问答系统

毕业设计项目：面向电商平台商品知识库的企业级问答系统。用户通过浏览器进行知识库管理与问答，问答时基于 **RAG（检索增强生成）** 引用知识库原文片段并展示溯源。

## 技术栈

| 层 | 技术 |
|---|---|
| 大模型 | 通义千问 Qwen（阿里云百炼 DashScope）|
| Embedding | 本地 BGE（bge-m3，免费离线）|
| 向量库 | Chroma（持久化）|
| 后端 | Python + FastAPI + LangChain + SQLAlchemy + SQLite |
| 认证 | JWT + bcrypt + RBAC 权限 |
| 前端 | React 18 + TypeScript + Vite + Ant Design 5 + Zustand |

## 目录结构

```
├── backend/          # FastAPI 后端（RAG 核心）
│   ├── app/
│   │   ├── main.py           # 应用入口
│   │   ├── config.py         # 配置（读 .env）
│   │   ├── database.py       # SQLAlchemy
│   │   ├── models.py         # ORM 模型（用户/会话/消息/文档）
│   │   ├── schemas.py        # Pydantic 出入参
│   │   ├── core/             # JWT / bcrypt / RBAC
│   │   ├── api/              # auth / sessions / users / kb / chat
│   │   ├── rag/              # embeddings / 向量库 / 解析 / 分块 / 检索 / 生成
│   │   └── services/         # 知识库入库处理
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # React 18 + TS 前端
│   └── src/
│       ├── router/           # 路由 + 权限守卫
│       ├── stores/           # Zustand 状态
│       ├── api/              # axios + SSE
│       ├── views/            # 登录/注册/问答/知识库/个人中心
│       └── components/
└── sample_data/      # 测试用商品知识库样例
```

## 快速开始

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

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 <http://localhost:5173>

### 3. 默认账号

- 管理员：`admin` / `123456`（可进入知识库管理页）
- 普通用户：自行在注册页注册

### 4. 测试流程

1. 用 `admin/123456` 登录，进入「知识库管理」，上传 `sample_data/商品知识库示例.txt`
2. 等待文档状态变为「已完成」
3. 注册一个普通用户登录，新建会话，提问如「这款耳机支持退换吗？」「手表续航多久？」
4. 观察流式回答 + 底部「引用来源」展示的原文片段

## 环境变量（backend/.env）

| 变量 | 说明 |
|---|---|
| `DASHSCOPE_API_KEY` | 阿里云百炼 API Key（必填）|
| `LLM_MODEL` | 大模型，默认 `qwen3.8-max-0902` |
| `EMBEDDING_MODEL` | 向量模型，默认 `BAAI/bge-m3` |
| `DATABASE_URL` | 数据库连接，默认 SQLite |
| `SECRET_KEY` | JWT 签名密钥 |

> ⚠️ `.env` 含密钥，已加入 `.gitignore`，请勿提交到 Git。
