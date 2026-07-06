# QA Agent ReAct Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bounded three-round event QA Agent that uses existing dashboard tools, revises its previous draft, and always reports event and time scope.

**Architecture:** A focused `app/agents/qa` package owns time/event context, tool adapters, prompts, strict JSON parsing, and a LangGraph loop. The existing dispatcher and unified API expose it; the homepage routes the QA capability to that endpoint while leaving data-question unchanged.

**Tech Stack:** Python 3.11, LangGraph, FastAPI, pytest, Next.js, TypeScript.

## Global Constraints

- Maximum three ReAct rounds.
- Specified event uses its full event period; cross-event defaults to the 30 days ending at the Asia/Shanghai request time.
- Every answer states event name, time scope, and data scope.
- Existing dashboard services are the only data source; no free SQL and no invented numbers.
- Existing data-question and report endpoints remain compatible.

---

### Task 1: Time and event context

**Files:**
- Create: `app/agents/qa/__init__.py`
- Create: `app/agents/qa/state.py`
- Create: `app/agents/qa/tools.py`
- Test: `tests/test_qa_agent.py`

- [ ] Write failing tests for the package boundary, Asia/Shanghai default 30-day scope, explicit date override, and specified-event full-period scope.
- [ ] Run `python -m pytest tests/test_qa_agent.py -q`; expect failures for missing package/functions.
- [ ] Implement typed state, time-scope resolution, event resolution, and normalized tool envelopes.
- [ ] Run the same tests; expect them to pass.

### Task 2: Three-round ReAct graph

**Files:**
- Create: `app/agents/qa/prompts.py`
- Create: `app/agents/qa/parser.py`
- Create: `app/agents/qa/graph.py`
- Modify: `tests/test_qa_agent.py`

- [ ] Write failing tests proving each revision receives the prior draft, the graph stops when sufficient, invalid tools are rejected, and the tool loop never exceeds three rounds.
- [ ] Implement strict decisions, tool execution, draft revision, conditional routing, and final scope enforcement.
- [ ] Run `python -m pytest tests/test_qa_agent.py -q`; expect all QA tests to pass.

### Task 3: Dispatcher and API integration

**Files:**
- Modify: `app/agents/core/dispatcher.py`
- Modify: `tests/test_agent_dispatcher.py`

- [ ] Replace the old “qa unavailable” expectation with a failing QA dispatch test.
- [ ] Register `run_qa_agent` without changing the public dispatcher signature.
- [ ] Verify `/api/agents/run` forwards `event_id` and history and returns QA metadata.
- [ ] Run `python -m pytest tests/test_qa_agent.py tests/test_agent_dispatcher.py -q`.
- [ ] Commit the backend QA Agent.

### Task 4: Homepage QA entry

**Files:**
- Modify: `frontend/src/components/home/AutoVocHomePage.tsx`
- Modify: `tests/test_next_frontend_architecture.py`

- [ ] Add a failing architecture test requiring QA to call `/agents/run` with `capability: "qa"`, data-question to keep its old endpoint, and report/insight to remain unavailable.
- [ ] Route submit behavior by active skill and render returned event/time/data scope metadata.
- [ ] Disable unfinished report/insight submission with clear copy.
- [ ] Run `python -m pytest tests/test_next_frontend_architecture.py -k "chatbi or qa_agent or data_question" -q` and `npm run typecheck`.
- [ ] Commit the frontend QA entry.

### Task 5: Full verification

**Files:**
- No new production files.

- [ ] Run QA, dispatcher, data-question, and frontend architecture tests together.
- [ ] Run Python compile checks, frontend typecheck, and production build.
- [ ] Call the unified API with fixed mocked LLM responses and verify three-round behavior and visible scope metadata.
- [ ] Review `git diff --check` and commit only QA-related files.
