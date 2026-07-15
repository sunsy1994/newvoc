# Evidence-Grounded Insight Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an independent AutoVOC `insight` Agent that retrieves similar historical events, enforces evidence thresholds in backend code, and renders evidence-grounded reaction cards only inside the AI conversation.

**Architecture:** Add a focused `app/agents/insight` LangGraph package with deterministic evidence gates around bounded LLM calls. Reuse existing event dashboard services for data access, register the Runner in the capability Dispatcher, and pass an independent `InsightResult` payload to a dedicated frontend card component.

**Tech Stack:** Python 3, FastAPI, LangGraph, OpenAI-compatible JSON calls, pytest, Next.js, React, TypeScript, Tailwind CSS.

## Global Constraints

- No evidence means no simulation; conclusions may not exceed the evidence.
- Prefer same-model events, then same-brand events, then cross-brand competitor events.
- Cross-brand evidence must be explicitly labeled.
- A full simulation requires at least one strong match or two medium matches, plus at least 10 relevant real comments.
- Do not generate precise reaction percentages, fabricated user quotes, or product and marketing recommendations.
- Insight output appears only in the AI conversation and is never written to report assets or a new database table.
- The graph performs at most three model rounds and allows at most one evidence-review correction.
- Reuse existing event and dashboard services; do not duplicate SQL.

---

### Task 1: Evidence Policy and Candidate Tools

**Files:**
- Create: `app/agents/insight/__init__.py`
- Create: `app/agents/insight/state.py`
- Create: `app/agents/insight/tools.py`
- Test: `tests/test_insight_agent.py`

**Interfaces:**
- Consumes: `list_voc_events()`, `get_voc_event_product_dashboard()`, and `build_product_report_context()`.
- Produces: `list_candidate_events(scenario, event_id=None)`, `get_event_reaction_evidence(candidate)`, `evaluate_evidence_gate(similar_events)` and `InsightAgentState`.

- [ ] **Step 1: Write failing policy tests**

Add tests proving the gate returns `completed` for one strong match with 10 comments, `completed` for two medium matches with 10 comments, `partial` for related but incomplete evidence, and `insufficient_data` when no candidates or fewer than 10 comments are available.

```python
def test_evidence_gate_accepts_one_strong_match_with_ten_comments():
    from app.agents.insight.tools import evaluate_evidence_gate

    result = evaluate_evidence_gate([
        {"similarity": "strong", "evidence_comments": [{"comment_text": str(i)} for i in range(10)]}
    ])

    assert result["status"] == "completed"
    assert result["comment_count"] == 10


def test_evidence_gate_rejects_fewer_than_ten_comments():
    from app.agents.insight.tools import evaluate_evidence_gate

    result = evaluate_evidence_gate([
        {"similarity": "strong", "evidence_comments": [{"comment_text": str(i)} for i in range(9)]}
    ])

    assert result["status"] == "insufficient_data"
```

- [ ] **Step 2: Run tests and verify RED**

Run: `python -m pytest tests/test_insight_agent.py -q -p no:cacheprovider`

Expected: collection fails with `ModuleNotFoundError: No module named 'app.agents.insight'`.

- [ ] **Step 3: Implement the minimal state and evidence policy**

Create `InsightAgentState` with question, history, scenario, candidates, similar events, gate result, draft result, review result and final result. Implement a deterministic policy equivalent to:

```python
MIN_RELEVANT_COMMENTS = 10


def evaluate_evidence_gate(similar_events: list[dict[str, Any]]) -> dict[str, Any]:
    strong_count = sum(item.get("similarity") == "strong" for item in similar_events)
    medium_count = sum(item.get("similarity") == "medium" for item in similar_events)
    comment_count = sum(len(item.get("evidence_comments") or []) for item in similar_events)
    if not similar_events or comment_count < MIN_RELEVANT_COMMENTS:
        status = "insufficient_data"
    elif strong_count >= 1 or medium_count >= 2:
        status = "completed"
    else:
        status = "partial"
    return {"status": status, "strong_count": strong_count, "medium_count": medium_count, "comment_count": comment_count}
```

Candidate tools must return compact event metadata and existing product evidence without persisting data.

- [ ] **Step 4: Run policy tests and verify GREEN**

Run: `python -m pytest tests/test_insight_agent.py -q -p no:cacheprovider`

Expected: policy and tool tests pass.

### Task 2: Bounded LangGraph and Evidence-Constrained Prompts

**Files:**
- Create: `app/agents/insight/parser.py`
- Create: `app/agents/insight/graph.py`
- Modify: `app/agents/insight/__init__.py`
- Test: `tests/test_insight_agent.py`

**Interfaces:**
- Consumes: Task 1 tools and state.
- Produces: `build_insight_graph()` and `run_insight_agent(message, event_id=None, history=None)` returning the independent `InsightResult` contract.

- [ ] **Step 1: Write failing graph tests**

Cover these observable behaviors:

```python
def test_insight_agent_returns_clarification_before_search(monkeypatch):
    monkeypatch.setattr("app.agents.insight.parser.parse_scenario", lambda *args, **kwargs: {
        "status": "needs_clarification",
        "clarification_question": "你准备减少哪项配置？",
    })
    result = run_insight_agent("我准备减配")
    assert result["status"] == "needs_clarification"
    assert result["answer"] == "你准备减少哪项配置？"


def test_insight_agent_does_not_generate_when_gate_rejects(monkeypatch):
    generated = False
    # Stub parsing and retrieval with no similar evidence.
    result = run_insight_agent("取消座椅通风")
    assert result["status"] == "insufficient_data"
    assert "暂无此类数据推演" in result["answer"]
    assert generated is False
```

Also test a completed payload contains reaction, audience, impact, expression, evidence, similar-event and limitation fields; cross-brand events retain `relation_type="cross_brand"`; and generated results contain no numeric reaction percentages.

- [ ] **Step 2: Run graph tests and verify RED**

Run: `python -m pytest tests/test_insight_agent.py -q -p no:cacheprovider`

Expected: failures identify missing parser, graph and Runner behavior.

- [ ] **Step 3: Implement parser and fixed graph**

The parser must use the configured OpenAI-compatible JSON client and return a normalized structure with `action_type`, `affected_aspects`, `compensation`, `target`, `expected_scope`, `status`, and `clarification_question`.

Build the fixed route:

```text
parse_scenario -> retrieve_candidates -> rank_similarity -> evidence_gate
evidence_gate -> clarify | insufficient | partial | simulate
simulate -> review -> finalize
```

`evidence_gate` is pure backend code. `simulate` receives only accepted events and evidence. `review` verifies evidence IDs, cross-brand labels, fabricated quotes, precise percentages, deterministic language and recommendations; it may request one correction only.

- [ ] **Step 4: Implement fixed result states**

Return one of:

```python
{
    "status": "completed|partial|insufficient_data|needs_clarification",
    "answer": "short conversation summary",
    "suggested_questions": [],
    "requires_clarification": False,
    "insight_result": {
        "scenario": {},
        "confidence": "high|medium|low|insufficient",
        "data_scope": {},
        "reaction_cards": [],
        "audience_cards": [],
        "impact_cards": [],
        "expression_themes": [],
        "evidence_comments": [],
        "similar_events": [],
        "limitations": [],
    },
    "react_rounds": 0,
}
```

For non-completed states, omit unsupported full-reaction sections rather than returning invented empty conclusions.

- [ ] **Step 5: Run graph tests and verify GREEN**

Run: `python -m pytest tests/test_insight_agent.py -q -p no:cacheprovider`

Expected: all insight tests pass.

### Task 3: Dispatcher and Unified API Routing

**Files:**
- Modify: `app/agents/core/dispatcher.py`
- Modify: `tests/test_agent_dispatcher.py`

**Interfaces:**
- Consumes: `run_insight_agent` from Task 2.
- Produces: unified `POST /api/agents/run` support for `capability="insight"`.

- [ ] **Step 1: Replace unavailable-capability tests with failing registration tests**

```python
def test_dispatcher_registers_insight_agent():
    from app.agents.core import dispatcher
    from app.agents.insight import run_insight_agent

    assert dispatcher.AGENT_RUNNERS["insight"] is run_insight_agent
```

Add an API test that stubs Dispatcher output and verifies `capability`, `message`, `event_id`, and `history` are forwarded unchanged.

- [ ] **Step 2: Run routing tests and verify RED**

Run: `python -m pytest tests/test_agent_dispatcher.py -q -p no:cacheprovider`

Expected: registration test fails because `insight` is absent.

- [ ] **Step 3: Register the Runner**

Import `run_insight_agent` and add `"insight": run_insight_agent` to `AGENT_RUNNERS`. Do not change other capability mappings or API schemas.

- [ ] **Step 4: Run routing tests and verify GREEN**

Run: `python -m pytest tests/test_agent_dispatcher.py -q -p no:cacheprovider`

Expected: all Dispatcher and unified API tests pass.

### Task 4: Conversation Insight Cards

**Files:**
- Create: `frontend/src/components/home/InsightResultCard.tsx`
- Modify: `frontend/src/types/vocMarket.ts`
- Modify: `frontend/src/components/home/ChatMessageList.tsx`
- Modify: `frontend/src/components/home/AutoVocHomePage.tsx`
- Modify: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: backend `insight_result` from Task 2.
- Produces: `InsightResult`, `InsightResultCard`, and `ChatMessage.insightPayload`.

- [ ] **Step 1: Write failing frontend architecture tests**

Assert that the home page enables `insight`, routes it through `/agents/run`, stores `result.insight_result` on the assistant message, and does not assign an event ID automatically. Assert that `ChatMessageList` renders `InsightResultCard`, while report modal behavior remains unchanged.

```python
assert 'activeSkillId === "insight"' in home
assert 'insightPayload' in home
assert 'InsightResultCard' in messages
assert 'message.insightPayload' in messages
assert '暂无此类数据推演' in card
assert '真实证据原话' in card
```

- [ ] **Step 2: Run frontend tests and verify RED**

Run: `python -m pytest tests/test_next_frontend_architecture.py -k "insight" -q -p no:cacheprovider`

Expected: tests fail because the types, routing and card do not exist.

- [ ] **Step 3: Add independent TypeScript types**

Define `InsightStatus`, `InsightScenario`, `InsightReactionCard`, `InsightAudienceCard`, `InsightImpactCard`, `InsightEvidenceComment`, `InsightSimilarEvent`, and `InsightResult`. Keep these independent from `StructuredReport`.

- [ ] **Step 4: Implement the card renderer**

Render:

- a scenario/status header;
- support, observe and oppose reaction cards for `completed` only;
- audience and impact cards when supported;
- separate expression themes from real evidence comments;
- event relation badges for same-model, same-brand and cross-brand;
- a single status card for `partial`, `insufficient_data`, or `needs_clarification`.

Reuse existing theme variables and card visual language. Do not add a report modal, asset action or persistence API.

- [ ] **Step 5: Wire the insight capability**

Enable insight in `isActiveSkillAvailable`, include it in unified Agent requests, keep `event_id` null for free scenario simulation, extend `DataQuestionResult` with `insight_result`, and attach it to assistant messages. Preserve the last 10 text messages as history.

- [ ] **Step 6: Run frontend tests and typecheck**

Run: `python -m pytest tests/test_next_frontend_architecture.py -k "insight or report_ai_summary_card or chat_message_can_open_generated_event_report" -q -p no:cacheprovider`

Run: `npm run typecheck` from `frontend`.

Expected: selected frontend tests and TypeScript typecheck pass.

### Task 5: Focused Regression Verification

**Files:**
- Verify only; no planned production changes.

**Interfaces:**
- Consumes: all previous tasks.
- Produces: evidence that insight works without changing QA, report, or asset behavior.

- [ ] **Step 1: Run focused backend suite**

Run: `python -m pytest tests/test_insight_agent.py tests/test_agent_dispatcher.py tests/test_qa_agent.py tests/test_event_report_agent.py -q -p no:cacheprovider`

Expected: all selected tests pass.

- [ ] **Step 2: Run focused frontend suite and typecheck**

Run: `python -m pytest tests/test_next_frontend_architecture.py -k "insight or report_ai_summary_card or chat_message_can_open_generated_event_report" -q -p no:cacheprovider`

Run: `npm run typecheck` from `frontend`.

Expected: tests and typecheck pass.

- [ ] **Step 3: Check diff integrity**

Run: `git diff --check`

Expected: exit code 0, with no whitespace errors. Review `git diff --stat` and confirm no report asset storage or unrelated dashboard files were added for insight.
