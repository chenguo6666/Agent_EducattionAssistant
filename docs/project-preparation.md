# 项目准备说明

## 1. 项目定位

项目名称：教育助手 AI Agent

项目目标：构建一个可演示的教育场景 AI Agent Web 应用，支持用户提交高层级学习任务，由系统自动识别任务类型、拆解执行步骤、调用模拟工具，并将过程与结果反馈给用户。

## 2. 当前 backlog 结论

根据产品 backlog 与 Sprint 1 backlog，当前需求已经足够进入开发前准备阶段。结论如下：

- 产品 backlog 已经明确分为 3 个 Sprint。
- Sprint 1 已经覆盖 MVP 所需的核心能力。
- Sprint 2、Sprint 3 属于增强项，应先冻结，不应提前耦合到 Sprint 1 的实现中。

Sprint 1 实际要做的最小闭环是：

1. 用户登录
2. 用户输入教育任务
3. 后端 Agent 识别任务意图
4. 调用摘要/出题 Mock Tool
5. 返回状态与结果

## 3. 系统边界

### 前端负责

- 登录/注册页面
- 对话页面
- 任务输入与提交
- 任务状态展示
- Markdown 结果展示
- Token 持久化与路由守卫

### 后端负责

- 用户认证
- Agent 调度
- Prompt 模板管理
- 工具注册与调用
- 任务状态流转
- 返回结构化执行结果

### 当前阶段暂不处理

- 真正复杂的 RAG 检索链
- 多轮记忆
- 文件导出
- 错题分析推荐
- 重新规划策略比较

## 4. 技术架构

### 4.1 总体架构

```text
Vue Web 前端
   ↓ HTTP / JSON
FastAPI 后端
   ↓
LangChain Agent 调度层
   ↓
Mock Tools（摘要工具 / 出题工具）
   ↓
结果整合后返回前端
```

### 4.2 核心模块

#### 前端模块

- `auth`：登录、注册、Token 管理
- `chat`：对话输入、消息列表、任务发起
- `status`：状态条、步骤提示
- `api`：后端接口封装

#### 后端模块

- `api/auth`：认证接口
- `api/chat`：任务提交接口
- `agent/planner`：任务识别与路由
- `tools/summary_tool.py`：摘要工具
- `tools/quiz_tool.py`：出题工具
- `services/task_service.py`：任务状态与结果整合

## 5. Agent 工作流

Sprint 1 中不追求复杂自治，只实现“轻量 Agent 流程”：

1. 接收用户任务
2. 用 Prompt 判断任务类型
3. 生成一个简单执行计划
4. 调用一个或多个本地 Mock Tool
5. 汇总结果返回前端

建议的任务类型：

- `summary`
- `quiz`
- `summary_and_quiz`
- `unknown`

建议的状态流转：

- `submitted`：前端已提交
- `analyzing`：后端识别任务意图
- `executing`：后端调用工具
- `completed`：执行成功
- `failed`：执行失败

## 6. 接口草案

### 6.1 认证接口

#### `POST /api/auth/register`

请求体：

```json
{
  "username": "student1",
  "phone": "13800000000",
  "password": "123456"
}
```

响应体：

```json
{
  "message": "register success"
}
```

#### `POST /api/auth/login`

请求体：

```json
{
  "account": "student1",
  "password": "123456"
}
```

响应体：

```json
{
  "token": "jwt-token",
  "user": {
    "id": 1,
    "username": "student1"
  }
}
```

### 6.2 任务接口

#### `POST /api/chat/execute`

请求体：

```json
{
  "message": "总结这篇历史课文并生成5个选择题"
}
```

响应体：

```json
{
  "taskId": "task_001",
  "intent": "summary_and_quiz",
  "status": "completed",
  "steps": [
    "识别任务类型：总结+出题",
    "调用摘要工具",
    "调用出题工具"
  ],
  "result": {
    "summary": "......",
    "quiz": [
      {
        "question": "......",
        "options": ["A", "B", "C", "D"],
        "answer": "A"
      }
    ]
  }
}
```

## 7. 数据模型建议

Sprint 1 只保留最小必要数据表。

### `users`

- `id`
- `username`
- `phone`
- `password_hash`
- `created_at`

### `task_records`

- `id`
- `user_id`
- `message`
- `intent`
- `status`
- `result_json`
- `created_at`

如果时间紧，`task_records` 甚至可以先不持久化，只保留内存或日志，优先保证主流程可运行。

## 8. 风险与控制

### 风险 1：一开始做太多

控制方式：Sprint 1 只做登录、对话、Agent、Mock Tool、状态反馈。

### 风险 2：LangChain 集成耗时

控制方式：先封装普通 Python 路由逻辑，再接入 LangChain；保证 Agent 层可替换。

### 风险 3：前后端接口反复修改

控制方式：先固定 `auth` 和 `chat/execute` 两类接口结构，再开始写页面。

### 风险 4：把“思考过程”做得过深

控制方式：Sprint 1 只展示可控的步骤列表，不展示真实 CoT 内容。

## 9. 开发前必须先确认的约定

- 后端框架固定为 `FastAPI`
- 数据库固定为 `SQLite`
- Sprint 1 的 Agent 仅支持两类工具：摘要、出题
- 前端对“思考中”的展示采用状态步骤，不暴露真实大模型推理内容
- 先做单会话任务执行，不做多会话历史页面

## 10. 进入代码阶段前的完成标准

满足下面几点即可进入正式开发：

- Sprint 1 范围冻结
- 前后端技术栈冻结
- 接口字段命名冻结
- 目录结构方案冻结
- 任务状态枚举冻结

这些条件现在已经具备，可以开始初始化工程。
