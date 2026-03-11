# 教育助手 AI Agent

一个面向课程项目的全栈 Web 应用。用户在前端输入高层级教育任务，例如“总结这篇历史课文并生成 5 个选择题”，后端 Agent 负责识别意图、拆解任务、调用模拟工具，并将执行结果和状态反馈给前端。

当前仓库阶段：Sprint 1 收尾。

## 1. 项目目标

- 理解 AI Agent 的基本工作流：接收任务、规划、工具调用、结果整合。
- 完成一个可演示的教育场景 Agent Web 应用。
- 以 Scrum 形式推进，分 3 个 Sprint 逐步迭代。

## 2. 技术选型

基于当前 backlog 和“从 0 开始、强调可落地演示”的目标，建议采用下面的组合：

- 前端：Vue 3 + Vite + TypeScript + Vue Router
- 状态管理：Pinia
- Markdown 渲染：`markdown-it`
- 后端：FastAPI + Pydantic + Uvicorn
- Agent：LangChain
- 认证：JWT
- 存储：SQLite

选择 `FastAPI` 而不是 `Spring Boot` 的原因：

- LangChain 与 Python 生态集成更直接。
- Mock Tool、Prompt、Agent 编排实现成本更低。
- 对课程项目更利于在有限时间内交付可演示版本。

## 3. Sprint 规划摘要

- Sprint 1：完成登录、对话界面、Agent 核心逻辑、任务状态反馈、基础联调
- Sprint 2：增加工具执行过程展示、参数化控制、模板任务、内容导出、异常提示
- Sprint 3：增加文件上传、简单 RAG、多轮记忆、错题推荐、重新生成

当前优先级：只锁定 Sprint 1 的架构和实现边界，避免一开始把 Sprint 2/3 的复杂度提前带入。

## 4. Sprint 1 MVP 范围

- 用户注册/登录
- 登录态持久化
- 类 ChatGPT 的对话输入区与结果展示区
- Markdown 结果渲染
- Agent 基础流程
- 两个 Mock Tool：
  - 摘要工具
  - 出题工具
- 任务状态流转：
  - `submitted`
  - `analyzing`
  - `executing`
  - `completed`
  - `failed`

## 5. 建议仓库结构

```text
Agent_EducattionAssistant/
├─ frontend/                # Vue 前端
├─ backend/                 # FastAPI 后端
├─ docs/                    # 前期准备与设计文档
├─ 产品待办列表.xlsx
├─ sprint1产品代办列表.xlsx
└─ README.md
```

后续代码阶段建议扩展为：

```text
frontend/
├─ src/
│  ├─ api/
│  ├─ components/
│  ├─ pages/
│  ├─ stores/
│  ├─ router/
│  └─ types/

backend/
├─ app/
│  ├─ api/
│  ├─ core/
│  ├─ agent/
│  ├─ tools/
│  ├─ models/
│  ├─ schemas/
│  └─ services/
└─ tests/
```

## 6. 当前文档

- [项目准备说明](E:/project/codex/Agent_EducattionAssistant/docs/project-preparation.md)
- [Sprint1 执行计划](E:/project/codex/Agent_EducattionAssistant/docs/sprint1-plan.md)
- [Sprint1 演示脚本](E:/project/codex/Agent_EducattionAssistant/docs/sprint1-demo-script.md)
- [Sprint1 验收清单](E:/project/codex/Agent_EducattionAssistant/docs/sprint1-acceptance.md)

## 7. 当前完成度

Sprint 1 当前已完成的能力：

- 注册/登录与 JWT 鉴权
- 登录态校验与 `/api/auth/me`
- 对话工作台
- Agent 阶段展示与执行计划展示
- Mock 摘要工具与出题工具
- 结构化结果卡片与错误卡片
- 预设任务模板
- Windows 下的一键联调启动与检查脚本
- 后端最小自动化验收测试

## 8. 本地启动

### 前端

```powershell
cd frontend
copy .env.example .env
npm install
npm run dev
```

默认地址：`http://127.0.0.1:5173`

### 后端

```powershell
cd backend
copy .env.example .env
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

默认地址：`http://127.0.0.1:8000`

健康检查：`GET /health`

### 一键联调启动

如果你希望在 Windows 下直接拉起前后端并做联调检查，可以使用仓库内脚本：

```powershell
.\scripts\dev-up.ps1
.\scripts\dev-check.ps1
.\scripts\dev-down.ps1
```

脚本说明：

- [dev-up.ps1](E:/project/codex/Agent_EducattionAssistant/scripts/dev-up.ps1)：后台启动前后端，并把日志写入 `.runtime/logs/`
- [dev-check.ps1](E:/project/codex/Agent_EducattionAssistant/scripts/dev-check.ps1)：通过真实 HTTP 请求验证注册、登录、鉴权和聊天接口
- [dev-down.ps1](E:/project/codex/Agent_EducattionAssistant/scripts/dev-down.ps1)：停止 `dev-up` 启动的两个进程

## 9. Sprint 1 验收

建议按下面顺序验收：

1. 运行 [dev-up.ps1](E:/project/codex/Agent_EducattionAssistant/scripts/dev-up.ps1)
2. 打开前端页面并手工验证登录、注册、模板任务、错误提示
3. 运行 [dev-check.ps1](E:/project/codex/Agent_EducattionAssistant/scripts/dev-check.ps1)
4. 运行后端自动化测试
5. 演示完成后运行 [dev-down.ps1](E:/project/codex/Agent_EducattionAssistant/scripts/dev-down.ps1)

详细清单见：

- [Sprint1 验收清单](E:/project/codex/Agent_EducattionAssistant/docs/sprint1-acceptance.md)

## 10. 演示建议

如果要做课程演示，建议直接按下面文档执行：

- [Sprint1 演示脚本](E:/project/codex/Agent_EducattionAssistant/docs/sprint1-demo-script.md)

## 11. 提交前准备

提交前建议执行：

```powershell
cd frontend
npm run build
```

```powershell
cd ..\backend
.\.venv\Scripts\python -m unittest tests.test_acceptance -v
```

```powershell
cd ..
.\scripts\dev-down.ps1
git status --short
```

说明：

- `.runtime/` 已加入忽略，不需要提交联调日志
- `frontend/dist/`、`node_modules/`、`backend/.venv/` 不应提交
- 如果只提交项目源码与文档，当前最核心的目录是 `frontend/`、`backend/`、`docs/`、`scripts/`
