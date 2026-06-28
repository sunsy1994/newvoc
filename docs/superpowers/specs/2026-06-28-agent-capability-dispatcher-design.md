# AutoVOC Agent 能力分发设计

## 目标

为“问数、问答、报告、洞察”建立统一的后端能力入口。前端已经明确选择能力，因此后端只做确定性分发，不调用 LLM 猜测意图。

## 边界

- 支持四个能力名称：`data_question`、`qa`、`report`、`insight`。
- 第一版只注册已经存在的 `data_question` Agent。
- 未实现的已知能力返回明确的“尚未接入”错误。
- 保留 `/api/agents/data-question/run`，避免破坏现有前端。
- 新增 `/api/agents/run` 作为后续四类能力的统一入口。
- 不建立跨能力巨型 LangGraph，不创建空 Agent 包。

## 调用链

```text
前端能力选择
  -> Agent API
  -> Capability Dispatcher
  -> 专业 Agent
  -> 专业 Agent 自己的 Graph / Tools / Prompts
```

统一请求使用 `capability`、`message`、`event_id` 和 `history`。Dispatcher 只验证能力并调用已注册的 Runner，不承担会话、意图识别或业务推理。

## 错误规则

- 非法能力名称由 Pydantic 拒绝并返回 `422`。
- 合法但尚未实现的能力返回 `501`。
- 专业 Agent 参数错误、AI 服务错误和 PostgreSQL 错误继续沿用现有映射。

## 验收

- `data_question` 可通过统一入口调用。
- 旧问数接口行为不变，但内部通过 Dispatcher 执行。
- `qa`、`report`、`insight` 不会误调用问数 Agent。
- 分发和 API 契约有自动化测试。
