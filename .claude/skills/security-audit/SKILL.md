---
name: security-audit
description: This skill should be used when the user asks to "安全检查", "安全审计", "检查安全", "有没有安全问题", "查漏洞", "security audit", "security check", "review security", or wants to review code for security risks. 教 Claude 检查代码中是否有敏感信息泄露、SQL注入等危险漏洞、配置文件明文敏感信息,以及其他安全隐患。
---

# 安全审计(security-audit)

## 用途

检查代码和配置里的安全隐患,从四方面找问题:
1. 代码里有没有泄露敏感信息(API key、密钥、密码、token 等)
2. 有没有 SQL 注入等危险漏洞
3. 配置文件里有没有明文敏感信息
4. 其他值得注意的安全隐患

## 步骤

### 第 1 步:确定检查范围

- 先问用户「检查哪些文件 / 目录」。
- 用户说「随便 / 全部」时,检查本项目源码 + 配置文件,重点看:
  - 后端 `backend/app/`(尤其认证 `core/security.py`、`core/deps.py`、数据库、RAG/LLM 调用、文件上传)
  - 前端 `frontend/src/`(尤其 `api/` 请求、token 存储、Markdown 渲染)
  - 配置:`backend/.env`、`backend/.env.example`、`backend/app/config.py`、`.gitignore`

### 第 2 步:逐项检查

**① 敏感信息泄露(硬编码的密码 / 密钥)**

- 搜代码里有没有硬编码的敏感值:密码、API key、token、secret、私钥、数据库连接串(带账号密码)、access key 等。
- 常见关键字:`password`、`passwd`、`secret`、`token`、`api_key`、`apikey`、`private key`、`access key`、`密码`、`密钥`、`口令`。
- 本项目重点:JWT 的 `SECRET_KEY`、DashScope 的 `DASHSCOPE_API_KEY` 是否写死在代码里(应该只存在于 `.env`)。
- 判断:是真泄露(真实值),还是占位符 / 示例(如 `YOUR_KEY_HERE`、`xxxxxxxx`)。占位符不算泄露。

**② SQL 注入等危险漏洞**

- 检查数据库查询是「拼接字符串拼 SQL」(危险),还是「参数化查询」(安全)。
- 本项目用 SQLAlchemy:ORM 查询(`db.query(...).filter(...)`)是安全的;危险的是 `text()` 里用 f-string 拼用户输入。
- 顺带留意:命令注入(`os.system`/`subprocess` 拼用户输入)、XSS(React 里 `dangerouslySetInnerHTML`、把用户输入当 HTML 渲染)、路径遍历(文件路径拼接用户输入)、不安全的 `eval` / `pickle` 反序列化。

**③ 配置文件里的明文敏感信息**

- 检查 `.env`、`config.*`、`settings.*` 等配置里有没有明文密码 / 密钥 / 连接串。
- 本项目重点:`backend/.env` 里有**真实的** `DASHSCOPE_API_KEY`,必须确认它被 `.gitignore` 忽略、绝不提交;`.env.example` 里应是占位符。

**④ 其他安全隐患**

- 弱加密 / 过时算法:用 MD5 存密码(本项目用 bcrypt,正确)、硬编码加密密钥、ECB 模式等。
- CORS 全开(`allow_origins=["*"]`)——开发可接受,生产要收紧到具体域名。
- JWT 过期时间过长、日志里打印敏感信息、调试开关没关。
- 第三方依赖有已知高危漏洞:前端可跑 `npm audit`,后端可跑 `pip-audit` 或 `pip list --outdated`。
- 凡「感觉不安全」的地方都列出来,并说明风险。

### 第 3 步:出报告

按严重程度排序(**严重 → 高 → 中 → 低**),每条标出:

- `文件:行号`
- 问题类型 + 一句大白话说明风险
- 建议怎么改

没有问题时,也要明确说「没发现明显安全问题」。

### 第 4 步:问是否要帮忙修复

- 出完报告,问用户「要不要我帮忙修复这些问题?」。
- 涉及安全,动手前先讲清楚每个改动会做什么,用户同意再改。

## 注意

- 只读代码、不改代码,除非用户明确要求修复。
- 报告用大白话,用户是技术小白。
- 判断「是不是真泄露」时,区分真实敏感值 vs 占位符 / 示例,避免误报。
