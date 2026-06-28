# Agent Capability Dispatcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 AutoVOC 四类 AI 能力建立统一、确定性的后端分发入口，并把现有问数 Agent 接入。

**Architecture:** 使用轻量注册表将前端显式传入的能力名称映射到专业 Agent Runner。统一 API 和旧问数 API 共用该分发器；不使用 LLM 路由，也不创建尚未实现的 Agent。

**Tech Stack:** Python 3.11、FastAPI、Pydantic、pytest、LangGraph（仅存在于专业 Agent 内部）

## Global Constraints

- 只修改 Agent 分发、路由和对应测试。
- 保留现有 `/api/agents/data-question/run` 契约。
- 第一版只注册 `data_question`。
- 所有中文文件使用 UTF-8。

---

### Task 1: Capability Dispatcher

**Files:**
- Create: `app/agents/core/__init__.py`
- Create: `app/agents/core/dispatcher.py`
- Test: `tests/test_agent_dispatcher.py`

**Interfaces:**
- Consumes: `run_data_question_agent(message, event_id=None, history=None)`
- Produces: `dispatch_agent(capability, message, event_id=None, history=None)`

- [x] **Step 1: Write failing dispatcher tests**

覆盖问数 Runner 被准确调用，以及未注册能力被明确拒绝。

- [x] **Step 2: Run tests and verify RED**

Run: `pytest tests/test_agent_dispatcher.py -q`

Expected: FAIL because `app.agents.core.dispatcher` does not exist.

- [x] **Step 3: Implement the minimal registry and dispatcher**

注册表只包含 `data_question`；能力枚举包含四种前端选项。

- [x] **Step 4: Run tests and verify GREEN**

Run: `pytest tests/test_agent_dispatcher.py -q`

Expected: PASS.

### Task 2: Unified Agent API

**Files:**
- Modify: `app/routers/tasks.py`
- Modify: `tests/test_data_question_agent.py`

**Interfaces:**
- Consumes: `dispatch_agent(...)`
- Produces: `POST /api/agents/run` and compatible `POST /api/agents/data-question/run`

- [x] **Step 1: Write failing API tests**

覆盖统一入口的问数分发、未接入能力的 `501`，并确认旧接口仍可用。

- [x] **Step 2: Run tests and verify RED**

Run: `pytest tests/test_agent_dispatcher.py tests/test_data_question_agent.py -q`

Expected: FAIL because the unified endpoint is absent.

- [x] **Step 3: Implement the minimal API changes**

新增统一请求模型和端点，抽取共同异常映射；旧端点固定分发到 `data_question`。

- [x] **Step 4: Run focused and regression tests**

Run: `pytest tests/test_agent_dispatcher.py tests/test_data_question_agent.py -q`

Expected: PASS.

Run: `pytest -q`

Expected: existing suite remains green.
