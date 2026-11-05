---
name: package-app
description: This skill should be used when the user asks to "打包APP", "打包应用", "重新打包", "生成安装包", "打包成安装包", "重新打包为最新", "构建部署", "build the app", "package the app", or wants to produce the latest build/deployment artifact from the project's current code. 教 Claude 找到项目的构建命令并运行,产出最新部署产物。
---

# 打包 / 构建部署产物(package-app)

## 用途

把项目当前的代码构建成可部署的产物。本项目是 **Web 应用**(不是桌面 App,没有 `.exe` 安装包),「打包」指:

- 前端构建成静态资源:`npm run build` → `frontend/dist/`
- 可选:构建 Docker 镜像(`docker-compose.yml` 已提供)

## 步骤

### 第 1 步:确定要打包哪个项目

- 用户明确说了项目名或路径 → 用那个项目。
- 用户只说「打包」→ 用当前打开、正在开发的项目。
- 不确定 → 先问一句「要打包哪个项目?」,不要猜。

### 第 2 步:构建前端

- 检查 `frontend/` 里有没有 `node_modules`,没有就先 `npm install`。
- 执行:

```bash
cd frontend && npm run build
```

- 产物在 `frontend/dist/` 目录(静态资源,可直接由 Nginx / FastAPI 托管)。

### 第 3 步:可选 —— 构建 Docker 镜像

本项目根目录有 `docker-compose.yml`(后端 + 前端)。若本机已装 Docker,可执行:

```bash
docker compose build
```

### 第 4 步:确认结果

1. 看构建输出有没有报错。
2. 确认 `frontend/dist/` 目录已生成(`index.html` + 静态资源)。
3. 后端是 Python,无需构建,直接 `uvicorn` 运行即可。
4. 把产物路径 / 构建结果告诉用户。

## 注意

- **后端无需构建**:Python 直接运行,「打包」主要针对前端 + 可选 Docker。
- `frontend/dist/` 已被 `.gitignore` 忽略,不会被误提交。
- 后端 `backend/.env` 含 API Key 等密钥,部署 / 打包时不要提交或泄露。
