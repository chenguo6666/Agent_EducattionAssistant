# Sprint 1 验收清单

## 1. 账号与认证

- 未登录访问 `/chat` 时会自动跳转到 `/login`
- 新用户可以注册成功
- 注册后会自动登录并进入工作台
- 已注册用户可以用用户名或手机号登录
- 错误密码登录时页面会显示“账号或密码错误”
- 无效 Token 会被识别并要求重新登录

## 2. 对话工作台

- 登录后可以进入主对话页
- 页面包含状态区、Agent 阶段区、执行计划区、结果区、输入区
- 输入空任务时会显示前端错误提示
- 模板按钮可以自动填充输入框

## 3. Agent 主链路

- 输入“总结 + 出题”类任务时，意图识别为 `summary_and_quiz`
- 输入“提取知识点/复习提纲”类任务时，意图识别为 `summary`
- 页面能看到阶段流转：
  - `submitted`
  - `analyzing`
  - `executing`
  - `completed`
- 执行计划中能看到工具调用顺序

## 4. 结果展示

- 摘要结果以独立卡片展示
- 题目结果以结构化题卡展示
- 错误结果以错误卡片展示
- 页面不会因为接口错误直接崩溃

## 5. 自动化与构建

运行下面命令应全部通过：

```powershell
cd frontend
npm run build
```

```powershell
cd backend
.\.venv\Scripts\python -m unittest tests.test_acceptance -v
```

```powershell
cd ..
.\scripts\dev-check.ps1
```
