# 教育助手 AI Agent

一个面向课程项目交付的全栈 Web 应用。用户可以登录后上传学习资料，向 Agent 提交高层级教育任务，例如“总结这份历史资料并生成 5 道选择题”或“根据当前资料回答工业革命带来的社会问题”。系统会完成任务识别、执行规划、工具调用、检索增强和结果整理，并在前端展示执行状态、资料来源、错题记录与可导出的结果。

当前仓库状态：已完成 Sprint 1、Sprint 2 与 Sprint 3 的核心开发，进入最终交付整理阶段。

## 项目亮点

- 登录注册与 JWT 鉴权
- 会话历史与任务记录持久化
- 上传资料并自动抽取文本
- 文档分块、混合检索、追问式轻量 RAG
- 摘要、题目生成、资料问答、复习提纲等教育场景任务
- 结构化结果展示、来源片段展示、Markdown 导出
- 错题整理与最近错题本
- Windows 下的一键本地联调与公网临时分享脚本

## 技术栈

- 前端：Vue 3、Vite、TypeScript、Vue Router、Pinia
- 后端：FastAPI、SQLAlchemy、SQLite、Uvicorn
- Agent 层：LangChain Tool Calling Agent + 6 个预设工具 + fallback 规划
- AI 能力：Gemini `generateContent`、`ChatGoogleGenerativeAI` 与 `text-embedding-004`
- 文档处理：`pypdf`、`python-docx`

说明：
- 如果本地配置了 `GEMINI_API_KEY`，系统会优先使用 Gemini 生成摘要、题目、问答与向量嵌入。
- 如果没有配置，系统会自动回退到本地 Mock 工具和关键词检索，保证主流程仍然可运行。

## 当前能力清单

### 用户与会话

- 注册、登录、获取当前用户
- 登录态持久化
- 会话列表、历史任务回放
- 新建会话与会话标题自动生成

### Agent 与教育任务

- 任务意图识别：`assistant_chat`、`summary`、`quiz`、`summary_and_quiz`、`key_points`、`study_outline`、`rag_answer`
- 聊天框内联展示：`任务已提交 / 分析中 / 执行中 / 完成`、任务意图、工具调用轨迹
- 结构化摘要结果
- 多题选择题生成与提交作答
- 基于当前资料的追问式问答

### 资料与 RAG

- 支持上传 `txt`、`md`、`pdf`、`docx`
- 文本抽取与文档分块持久化
- 关键词召回 + 向量相似度混合检索
- chunk rerank 与来源片段回显
- 会话级资料上下文自动挂载

### 学习辅助

- 任务结果导出为 Markdown
- 答题后自动记录错题
- 最近错题本侧栏展示

## 系统架构

完整说明见 [docs/final-architecture.md](docs/final-architecture.md)。

系统主链路：

1. 用户在前端登录后进入对话工作台。
2. 用户可先上传资料，再提交总结、出题或资料追问任务。
3. 后端为任务绑定会话，读取当前会话资料与最近历史消息。
4. 检索服务对文档分块执行关键词召回、向量相似度计算与 rerank。
5. LangChain Agent 识别任务类型，调用摘要、出题、知识点、提纲、检索、资料问答等工具执行。
6. 结果、来源片段、步骤时间线、错题记录等信息写入数据库并返回前端。

## 目录结构

```text
frontend/                  Vue 前端
backend/                   FastAPI 后端
docs/                      项目说明、计划、验收、架构文档
scripts/                   本地联调、构建、分享脚本
uploads/                   本地上传资料目录
```

## 本地启动

### 方式一：一键联调

```powershell
.\scripts\dev-up.ps1
.\scripts\dev-check.ps1
```

默认地址：

- 前端：`http://127.0.0.1:5173`
- 后端：`http://127.0.0.1:8000`

停止服务：

```powershell
.\scripts\dev-down.ps1
```

### 方式二：手动启动

前端：

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

后端：

```powershell
cd backend
copy .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

健康检查：

- `GET /health`

## 环境变量

前端：

- `frontend/.env`
  - `VITE_API_BASE_URL`

后端：

- `backend/.env`
  - `APP_NAME`
  - `JWT_SECRET_KEY`
  - `JWT_ALGORITHM`
  - `ACCESS_TOKEN_EXPIRE_MINUTES`
  - `DATABASE_URL`
  - `UPLOADS_DIR`
  - `GEMINI_API_KEY`
  - `GEMINI_MODEL`

参考样例：

- [frontend/.env.example](frontend/.env.example)
- [backend/.env.example](backend/.env.example)

## 核心接口

认证：

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

会话与任务：

- `POST /api/chat/execute`
- `GET /api/chat/sessions`
- `GET /api/chat/sessions/{session_id}`
- `GET /api/chat/records/{record_id}/export`
- `POST /api/chat/records/{record_id}/quiz-attempt`
- `GET /api/chat/mistakes`

资料：

- `POST /api/documents/upload`
- `GET /api/documents/sessions/{session_id}`

## 验收与测试

前端构建：

```powershell
cd frontend
npm run build
```

后端自动化验收：

```powershell
cd backend
.\.venv\Scripts\python -m unittest tests.test_acceptance -v
```

当前验收覆盖：

- 注册、登录、当前用户鉴权
- 错误密码处理
- 文档上传
- 摘要 + 出题任务
- 结果导出
- 基于资料追问
- 错题提交与错题本查询

## 演示与分享

如果要以单端口形式运行生产构建：

```powershell
.\scripts\start-production.ps1
```

如果要临时给队友或老师远程访问：

```powershell
.\scripts\share-public.ps1
```

当前脚本使用 Cloudflare Quick Tunnel 生成临时公网链接。它适合演示，不适合作为长期部署方案。

## 相关文档

- [docs/project-preparation.md](docs/project-preparation.md)
- [docs/sprint1-plan.md](docs/sprint1-plan.md)
- [docs/sprint1-demo-script.md](docs/sprint1-demo-script.md)
- [docs/sprint1-acceptance.md](docs/sprint1-acceptance.md)
- [docs/final-architecture.md](docs/final-architecture.md)

## 提交前检查

```powershell
cd frontend
npm run build
cd ..\backend
.\.venv\Scripts\python -m unittest tests.test_acceptance -v
cd ..
.\scripts\dev-down.ps1
git status --short
```

不应提交：

- `frontend/.env`
- `backend/.env`
- `frontend/dist`
- `backend/.venv`
- `node_modules`
- `.runtime`
- `.cursorindexingignore`
- Excel 原始需求文件
