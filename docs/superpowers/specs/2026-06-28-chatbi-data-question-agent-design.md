# AutoVOC ChatBI 问数 Agent 设计

## 目标

把现有“关键词匹配 + 结果卡片”的问数功能升级为连续对话式 ChatBI：LLM 理解用户问题并选择受控工具，后端确定性查询真实数据，LLM 只基于工具结果组织自然回答；必要时追问缺失条件。

## 第一版范围

- 支持首页右侧紧凑对话框和展开后的完整 ChatBI 工作区。
- 两种视图共享同一段消息历史和输入状态。
- 对话历史保存在浏览器 `localStorage`，刷新后保留。
- 暂不建设登录、用户权限、服务端会话表、多会话列表和流式输出。
- “近期”默认近 30 天；只有无法确定事件或指标时才追问。
- 页面不展示 `event_id`、接口路径、数据库字段和 LangGraph 执行轨迹。

## 后端架构

继续使用 LangGraph，但将现有固定节点升级为受约束工作流：

```text
understand -> validate -> clarify | execute_tool -> compose -> END
```

### 1. understand

调用系统已经维护的 OpenAI 兼容模型。模型通过 `response_format=json_object` 输出结构化动作，不直接查询数据库：

```json
{
  "action": "list_events",
  "arguments": {"days": 30},
  "needs_clarification": false,
  "clarification_question": ""
}
```

使用结构化动作协议，不依赖模型原生 function calling，兼容当前已经验证可用的 `response_format` 能力。

### 2. validate

代码校验动作名称、参数类型和允许的指标枚举。模型不能生成 SQL、接口地址或任意 Python 调用。

### 3. clarify

仅在结果会因缺少条件而明显变化时返回追问。例如“这个事件怎么样”且页面没有当前事件上下文时，追问具体事件；“近期有哪些事件”直接按近 30 天执行。

### 4. execute_tool

第一版工具保持小而明确：

- `list_events(days=30, brand=None)`：查询时间范围内的事件。
- `resolve_event(event_name)`：把用户说的事件名称解析为内部 `event_id`。
- `get_event_metric(event_id, metric)`：查询事件声量、帖子数、评论数、KOL 数和互动量。
- `rank_events(days, metric)`：按指定指标比较近期事件。

所有工具只调用现有 service 函数或确定性数据库查询，不允许 LLM 编造值。

### 5. compose

将用户问题、必要的最近会话和工具返回值交给 LLM，输出：

```json
{
  "answer": "近30天系统共记录3个重点事件，其中……",
  "suggested_questions": ["查看声量最高的事件", "比较各事件的KOL数量"]
}
```

Prompt 强制要求：只使用工具结果；不向用户暴露内部 ID、字段名和执行轨迹；口径需要解释时使用业务语言。

## API 契约

请求：

```json
{
  "question": "近期有哪些事件？",
  "event_id": null,
  "history": [
    {"role": "user", "content": "近期有哪些事件？"},
    {"role": "assistant", "content": "近30天……"}
  ]
}
```

响应：

```json
{
  "status": "answered",
  "answer": "近30天系统共记录3个重点事件……",
  "suggested_questions": ["哪个事件声量最高？"],
  "requires_clarification": false
}
```

`event_id` 只作为页面上下文传入，不在回答中展示。后端仅截取最近 10 条消息进入模型上下文，避免历史无限增长。

## 前端交互

### 消息流

- 用户消息右对齐，使用轻量主题浅底。
- 助手消息左对齐，支持段落、列表、强调文字和轻量数据块。
- 追问作为普通助手消息展示，用户直接在同一输入框回答。
- 请求期间显示助手加载状态；第一版等待完整结果后一次性显示，不实现 token 流式传输。
- `suggested_questions` 显示为可点击的小型问题建议，点击后填入并发送。

### 共享状态

- `AutoVocHomePage` 持有唯一会话状态。
- 紧凑右侧面板与展开工作区接收相同的 messages、question、loading 和 submit 方法。
- 展开和收起不销毁会话。
- `localStorage` 使用版本化 key，例如 `auto-voc-chat-history-v1`；损坏数据直接忽略并恢复空会话。

### 空状态

首次进入只展示简短欢迎语和四类能力入口，不预生成回答。用户选择“问数”后，推荐问题切换为事件、声量、KOL、评论等问数示例。

## 错误处理

- AI 配置缺失：助手消息提示先在系统管理维护模型参数。
- 模型理解失败：提示用户换一种问法，不执行未经校验的动作。
- 工具无数据：自然说明当前筛选范围没有数据，并给出可调整范围。
- 请求失败：保留用户消息并显示可重试状态，不清空历史。

## 测试与验收

- 单元测试覆盖默认近 30 天、事件解析、指标查询、排名、追问和非法动作拒绝。
- LLM 调用在测试中使用固定 JSON 响应，工具测试使用真实 service 边界而非让模型生成数据。
- 前端静态测试覆盖消息列表、共享会话、`localStorage` 恢复和隐藏内部字段。
- TypeScript 检查、后端聚焦测试和 Next.js 生产构建通过。

## 后续升级

登录体系确定后，将本地会话迁移到 PostgreSQL，并增加用户、部门、业务权限和多会话历史。第一版 API 的消息结构保持可迁移，不提前建设这些能力。
