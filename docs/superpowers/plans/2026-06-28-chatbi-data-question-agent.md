# AutoVOC ChatBI Data Question Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the existing deterministic data-question workflow into a constrained LLM tool workflow and present its answers as a persistent ChatBI conversation.

**Architecture:** LangGraph keeps control of the sequence. The configured OpenAI-compatible model produces a validated action JSON, deterministic Python tools fetch real data, and a second model call turns only that tool result into a user-facing answer. The homepage owns one shared conversation used by compact and expanded views and persists it in versioned `localStorage`.

**Tech Stack:** Python, FastAPI, LangGraph, PostgreSQL-backed runtime AI settings, OpenAI-compatible JSON responses, Next.js App Router, React, TypeScript, Tailwind CSS.

## Global Constraints

- Reuse the default LLM configured in system management; do not add another API-key configuration path.
- “近期” defaults to 30 days.
- Clarify only when event or metric ambiguity changes the result.
- Never show event IDs, API paths, database fields, or LangGraph traces in normal chat messages.
- Keep the first version to one browser-local conversation; no login, server-side conversation table, multiple sessions, or token streaming.

---

### Task 1: Constrained LLM Tool Workflow

**Files:**
- Modify: `app/services/data_question_agent.py`
- Test: `tests/test_data_question_agent.py`

**Interfaces:**
- Consumes: `get_runtime_ai_config()`, `call_openai_compatible_json()`, existing VOC service functions.
- Produces: `run_data_question_agent(question, event_id=None, history=None) -> dict` with `status`, `answer`, `suggested_questions`, and `requires_clarification`.

- [ ] **Step 1: Write failing tests**

Add tests with a sequential fake LLM response: first response selects `list_events` with `days=30`; second response returns a natural answer and suggestions. Assert the tool result is real, the answer contains no `event_id`, and both prompts are sent through the configured runtime model. Add tests for metric lookup, ambiguous-event clarification, invalid actions, and ranking.

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_data_question_agent.py -q`

Expected: failures because the current function has no LLM action protocol, history, suggestions, or clarification flag.

- [ ] **Step 3: Implement minimal workflow**

Add a fixed action catalog (`list_events`, `resolve_event`, `get_event_metric`, `rank_events`), JSON prompt builders, strict action validation, deterministic tool execution, and a JSON answer composer. Build LangGraph nodes `understand`, `validate`, `clarify`, `execute_tool`, and `compose` with conditional routing. Resolve runtime credentials exclusively through `get_runtime_ai_config()`.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python -m pytest tests/test_data_question_agent.py -q`

Expected: all data-question tests pass.

### Task 2: Conversation API Contract

**Files:**
- Modify: `app/routers/tasks.py`
- Test: `tests/test_data_question_agent.py`

**Interfaces:**
- Consumes: Task 1 `run_data_question_agent`.
- Produces: `POST /api/agents/data-question/run` accepting `question`, optional `event_id`, and up to 10 recent `{role, content}` messages.

- [ ] **Step 1: Write failing API test**

Post a request with history and assert the router forwards it. Assert the response exposes only user-facing chat fields and maps model/configuration errors to HTTP 400 or 503 with readable Chinese detail.

- [ ] **Step 2: Run test and verify RED**

Run: `python -m pytest tests/test_data_question_agent.py::test_data_question_agent_api_forwards_chat_history -q`

- [ ] **Step 3: Implement request models and forwarding**

Add a typed history item model with `role` restricted to `user | assistant`, trim history to the last 10 messages, and forward `history` to the agent. Preserve PostgreSQL error handling and add `ValueError` handling.

- [ ] **Step 4: Run tests and verify GREEN**

Run: `python -m pytest tests/test_data_question_agent.py -q`

### Task 3: Shared ChatBI Conversation UI

**Files:**
- Modify: `frontend/src/components/home/AutoVocHomePage.tsx`
- Modify: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: Task 2 chat response.
- Produces: compact and expanded chat views sharing `messages`, input, submit, loading, suggestions, and `localStorage` persistence.

- [ ] **Step 1: Write failing frontend structure tests**

Assert the homepage defines a typed `ChatMessage`, uses `auto-voc-chat-history-v1`, renders user and assistant message collections, sends history, omits trace rendering, and passes the same messages to compact and expanded views.

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_next_frontend_architecture.py -k "chatbi or data_question" -q`

- [ ] **Step 3: Implement minimal shared conversation**

Replace the single result card with a scrollable message stream. On submit, append the user message, send the previous 10 messages plus current question, append the assistant response, clear the input, and persist messages. Render clarification as a normal assistant response and suggestions as clickable chips. Use a loading assistant bubble and a retryable error message; do not render technical trace fields.

- [ ] **Step 4: Run frontend verification**

Run:

```powershell
python -m pytest tests/test_next_frontend_architecture.py -k "chatbi or data_question" -q
cd frontend
npm run typecheck
npm run build
```

Expected: focused tests, TypeScript, and production build pass.

### Task 4: End-to-End Verification

**Files:**
- No production changes expected.

- [ ] **Step 1: Run backend regression tests**

Run: `python -m pytest tests/test_data_question_agent.py -q`

- [ ] **Step 2: Verify UTF-8 and diff quality**

Run: `git diff --check` and read all touched Chinese files with UTF-8.

- [ ] **Step 3: Start services and smoke-test**

Clean `frontend/.next`, start the frontend on `127.0.0.1:3000`, and verify `/auto-voc` responds. Submit “近期有哪些事件” against the configured backend model and confirm the response is a chat message with no internal IDs.
