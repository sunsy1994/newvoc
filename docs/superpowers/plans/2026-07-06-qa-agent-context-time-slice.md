# QA Agent Context and Time Slice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make QA follow-up questions use bounded chat history and make non-event-period date ranges query genuinely time-filtered data.

**Architecture:** Keep the existing five QA Tool names and LangGraph loop. Add one focused `time_slice.py` repository with fixed parameterized queries, route explicit/default ranges through it, and include a bounded normalized history block in both LLM prompts.

**Tech Stack:** Python 3, pytest, psycopg 3, LangGraph, existing AutoVOC service/report builders.

## Global Constraints

- Keep existing dashboard APIs and default queries unchanged.
- Keep the existing five Tool names and the three-round ReAct maximum.
- Do not expose SQL to the model or add a general SQL Agent.
- Use content `published_at` for market scope and comment `published_at` for product, sales, and discussion evidence.
- Treat dates as an inclusive user range implemented as `[start_date, end_date + 1 day)`.

---

### Task 1: Bounded conversation context

**Files:**
- Modify: `app/agents/qa/parser.py`
- Modify: `app/agents/qa/prompts.py`
- Modify: `app/agents/qa/graph.py`
- Test: `tests/test_qa_agent.py`

**Interfaces:**
- Consumes: `history: list[dict[str, Any]] | None` passed to `run_qa_agent`.
- Produces: `normalize_qa_history(history, limit=6, max_chars=1200) -> list[dict[str, str]]` and prompt blocks containing the latest six valid messages.

- [ ] **Step 1: Write failing history tests**

Add tests asserting invalid roles are dropped, only the latest six messages remain, text is bounded, and both prompts include the follow-up context plus the rule `历史回答不是事实来源`.

- [ ] **Step 2: Verify the tests fail**

Run: `python -m pytest tests/test_qa_agent.py -k "history or follow_up" -q -p no:cacheprovider`

Expected: FAIL because QA prompts currently omit history and use the generic normalizer.

- [ ] **Step 3: Implement minimal history normalization and prompt rendering**

Implement the focused normalizer in `parser.py`, call it before graph invocation, and render history with `json.dumps(..., ensure_ascii=False)` in both prompts. State explicitly that history resolves references but observations are the only factual source.

- [ ] **Step 4: Verify history tests pass**

Run: `python -m pytest tests/test_qa_agent.py -k "history or follow_up" -q -p no:cacheprovider`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add app/agents/qa/parser.py app/agents/qa/prompts.py app/agents/qa/graph.py tests/test_qa_agent.py
git commit -m "feat: add bounded qa conversation context"
```

### Task 2: Parameterized QA time-slice repository

**Files:**
- Create: `app/agents/qa/time_slice.py`
- Test: `tests/test_qa_time_slice.py`

**Interfaces:**
- Consumes: `event_id: str`, `start_date: str`, `end_date: str`, and optional `aspect: str`.
- Produces: `get_market_slice`, `get_product_slice`, `get_sales_slice`, and `get_discussion_slice`; each returns JSON-serializable facts/evidence.

- [ ] **Step 1: Write failing validation and query-boundary tests**

Use a recording fake psycopg connection to assert all functions bind `event_id`, start midnight, and the next-day exclusive upper bound. Add validation tests for malformed dates and reversed ranges.

- [ ] **Step 2: Verify the tests fail**

Run: `python -m pytest tests/test_qa_time_slice.py -q -p no:cacheprovider`

Expected: FAIL because `app.agents.qa.time_slice` does not exist.

- [ ] **Step 3: Implement the minimal fixed-query repository**

Create `_date_bounds`, `_fetch_all`, and four public query functions. Use only `%s` parameters; market queries filter `c.published_at`, while product/sales/discussion queries filter `cm.published_at` after joining content by `event_id`. Aggregate rows in Python only where it keeps SQL smaller and clearer.

- [ ] **Step 4: Verify time-slice tests pass**

Run: `python -m pytest tests/test_qa_time_slice.py -q -p no:cacheprovider`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add app/agents/qa/time_slice.py tests/test_qa_time_slice.py
git commit -m "feat: add qa time slice queries"
```

### Task 3: Route QA Tools through real date scopes

**Files:**
- Modify: `app/agents/qa/tools.py`
- Modify: `app/agents/qa/graph.py`
- Test: `tests/test_qa_agent.py`

**Interfaces:**
- Consumes: existing `execute_qa_tool(tool_name, arguments, time_scope)`.
- Produces: the same Tool envelope shape, with `data_scope` explicitly identifying time-sliced data when `time_scope.mode != "event_period"`.

- [ ] **Step 1: Write failing Tool routing tests**

Assert an `explicit` scope calls the matching `time_slice` function with exact dates, an `event_period` scope keeps using the existing dashboard builder, and discussion evidence always receives the resolved dates.

- [ ] **Step 2: Verify the routing tests fail**

Run: `python -m pytest tests/test_qa_agent.py -k "time_slice or explicit_scope or discussion_scope" -q -p no:cacheprovider`

Expected: FAIL because all event Tools currently use full-period dashboard services.

- [ ] **Step 3: Implement minimal Tool routing**

Import `time_slice`, choose it for `explicit` and `default_30_days`, preserve the existing envelope, and keep `event_period` on existing dashboard/report builders. Validate explicit ranges in `resolve_time_scope` so reversed dates fail before a query runs.

- [ ] **Step 4: Run focused and regression tests**

Run: `python -m pytest tests/test_qa_time_slice.py tests/test_qa_agent.py tests/test_agent_dispatcher.py tests/test_data_question_agent.py -q -p no:cacheprovider`

Expected: PASS.

- [ ] **Step 5: Run frontend contract and type checks**

Run: `python -m pytest tests/test_next_frontend_architecture.py -k "auto_voc_home_copilot or shared_persistent_chatbi or qa_agent" -q -p no:cacheprovider`

Run: `npm run typecheck` from `frontend`.

Expected: both PASS.

- [ ] **Step 6: Commit**

```powershell
git add app/agents/qa/tools.py app/agents/qa/graph.py tests/test_qa_agent.py
git commit -m "feat: apply qa time scopes to tool data"
```

