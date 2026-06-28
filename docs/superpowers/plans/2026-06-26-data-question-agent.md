# Data Question Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first controlled "问数 Agent" API that parses simple metric questions, resolves them to a small metric catalog, calls existing dashboard tools, and returns a traceable answer.

**Architecture:** Use a lightweight LangGraph `StateGraph` as a fixed workflow: parse question -> resolve metric -> execute deterministic tool -> compose answer. The LLM is not used in v1; this keeps问数 fast and verifiable while leaving the graph shape ready for later LLM intent parsing.

**Tech Stack:** FastAPI, pytest, existing dashboard service functions, LangGraph.

## Global Constraints

- Do not let the model write SQL or invent metrics.
- Keep v1 metric coverage small: total volume, content count, comment count, KOL count, and total engagement for one event.
- Every response must include `answer`, `value`, `metric`, `filters`, `source`, and `trace`.
- Use existing `get_voc_event_market_dashboard` as the first deterministic data source.
- Avoid broad rewrites of files with Chinese literals; make narrow edits only.

---

### Task 1: Controlled问数 Service

**Files:**
- Create: `app/services/data_question_agent.py`
- Test: `tests/test_data_question_agent.py`
- Modify: `requirements.txt`

**Interfaces:**
- Produces: `run_data_question_agent(question: str, event_id: str | None = None) -> dict[str, Any]`
- Produces: `parse_data_question(question: str, event_id: str | None = None) -> dict[str, Any]`

- [ ] **Step 1: Write failing service tests**

Create tests that monkeypatch `get_voc_event_market_dashboard` and assert:
- asking "这个事件总声量是多少" resolves to `total_volume`
- asking "帖子数是多少" resolves to `content_count`
- missing `event_id` returns `needs_clarification`

- [ ] **Step 2: Verify tests fail**

Run: `pytest tests/test_data_question_agent.py -q`

- [ ] **Step 3: Implement minimal service**

Implement:
- a small keyword-based parser
- a fixed metric catalog
- a LangGraph workflow with nodes `parse`, `resolve`, `execute`, `compose`
- deterministic answers based on `overview_metrics`

- [ ] **Step 4: Verify tests pass**

Run: `pytest tests/test_data_question_agent.py -q`

### Task 2: FastAPI Endpoint

**Files:**
- Modify: `app/routers/tasks.py`
- Test: `tests/test_data_question_agent.py`

**Interfaces:**
- Produces: `POST /api/agents/data-question/run`
- Request body: `{ "question": "...", "event_id": "..." }`
- Response body: same shape as `run_data_question_agent`

- [ ] **Step 1: Write failing API test**

Use `TestClient(create_app(...))`, monkeypatch `app.routers.tasks.run_data_question_agent`, and assert the endpoint passes through `question` and `event_id`.

- [ ] **Step 2: Verify API test fails**

Run: `pytest tests/test_data_question_agent.py -q`

- [ ] **Step 3: Implement endpoint**

Add a small Pydantic request model and router function.

- [ ] **Step 4: Verify API test passes**

Run: `pytest tests/test_data_question_agent.py -q`

### Task 3: Final Verification

**Files:**
- No new files.

- [ ] **Step 1: Run focused tests**

Run: `pytest tests/test_data_question_agent.py -q`

- [ ] **Step 2: Run type/import sanity**

Run: `python -m compileall app/services/data_question_agent.py app/routers/tasks.py`

- [ ] **Step 3: Confirm no CopilotKit spike returned**

Run: `rg "@copilotkit|CopilotChat|CopilotSidebar|CopilotPopup" frontend/src app tests requirements.txt`

Expected: no matches.
