---
name: run-app
description: This skill should be used when the user asks to "启动APP", "启动应用", "运行这个项目", "打开这个应用", "跑一下", "跑起来", "start the app", "run the app", "launch the app", or wants to see a project's app actually running. 教 Claude 启动项目(后端 + 前端)并确认跑起来。
---

# 启动项目(run-app)

## 用途

把本项目真正跑起来。本项目是 Web 应用,分**前后端两个进程**,都要启动:

- 后端:FastAPI(`uvicorn`,端口 8000)
- 前端:Vite 开发服务器(端口 5173,通过代理把 `/api` 转发到后端)

## 步骤

### 第 1 步:确定要启动哪个项目

- 用户明确说了项目名或路径 → 用那个项目。
- 用户只说「启动 / 运行」→ 用当前打开、正在开发的项目。
- 不确定 → 先问一句「要启动哪个项目?」,不要猜。

### 第 2 步:启动后端(后台)

在 `backend/` 目录执行(Windows 用 `.venv\Scripts\python.exe`;Linux/Mac 用 `.venv/bin/python`):

```bash
cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000
```

- 用 Bash 工具时设 `run_in_background: true`(uvicorn 会一直运行,别干等它结束)。
- 后端启动前确认 `backend/.env` 已配好 `DASHSCOPE_API_KEY`(否则问答会报额度错误)。

### 第 3 步:启动前端(后台)

```bash
cd frontend && npm run dev
```

- 同样设 `run_in_background: true`。
- `frontend/` 没有 `node_modules` 就先 `npm install`。

### 第 4 步:确认启动成功

- 后端输出:`Uvicorn running on http://127.0.0.1:8000`
- 前端输出:`Local: http://localhost:5173/`
- 浏览器打开 http://localhost:5173 即可使用。

## 注意

- 前后端是**两个独立进程**,各占一个后台任务,都要开着。
- 前端 Vite 已配置代理(`/api` → 后端 8000),无需手动改跨域。
- 报「端口被占用」:提示用户关掉已开着的实例,或换端口。
- 本项目没有 Electron 环境变量坑,直接 `run_in_background` 即可,不需要 `sleep |` 技巧。
