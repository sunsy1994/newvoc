# Market Report Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the first lightweight Report Agent for the market dashboard so users can generate a continuous Markdown market report from existing event VOC data.

**Architecture:** Keep business context construction inside AutoVOC services, reuse the existing OpenAI-compatible runtime config and JSON response pattern, and expose one market report endpoint. The frontend only triggers generation and renders the returned Markdown report.

**Tech Stack:** FastAPI, psycopg, existing `system_ai_config` / `system_prompt_template`, OpenAI-compatible `/chat/completions`, Next.js App Router, TypeScript.

---

## Market Report Story Contract

The market report Agent is intentionally a single-call, transparent report generator. It does not query data by itself and does not run multi-step reasoning yet.

### Output JSON

```json
{
  "report_markdown": "",
  "data_notes": []
}
```

`report_markdown` is the user-facing report body. It should be a coherent Markdown document with sections such as event overview, scale and rhythm, hot topics, KOL and audience, user feedback, and market judgment.

`data_notes` records only real data caveats from the provided context. The model must not request unsupported fields such as age, gender, income, or external demographics.

### Input Context Sent To LLM

- `event_overview`: event id, event name, brand, model, event type/status, start/end time.
- `scale`: total volume, content count, comment count, KOL count, KOL content count, total engagement.
- `rhythm`: rhythm type, active days, peak date/volume/rate, secondary peak signal, rule-based conclusion.
- `hot_topics`: top topic summary and top topic rows.
- `kol_and_authors`: KOL subject summary, top authors, KOL type distribution.
- `audience`: event-level user profile distribution.
- `feedback_quality`: effective comment, top aspect/intent, positive/negative, mid-high purchase signal, sentiment and purchase-signal distribution.
- `platform`: core platform summary and platform efficiency Top rows.
- `regional_response`: comment-location response summary.
- `evidence`: hot posts Top rows.

### Runtime Flow

1. Frontend market dashboard displays one `AI 总结` button.
2. Click opens the report modal and calls `GET /api/voc/events/{event_id}/market/report-agent/latest`.
3. If a cached report exists, frontend renders the latest Markdown report directly.
4. If no cached report exists, frontend shows an empty state and waits for the user to click `生成报告`.
5. User-triggered generation calls `POST /api/voc/events/{event_id}/market/report-agent/run`.
6. Backend calls the existing market dashboard service and compresses the payload into `market_context_json`.
7. Backend reads default prompt scene `market_report_summary` from `system_prompt_template`; if missing, it seeds a default prompt.
8. Backend renders prompt with `{{market_context_json}}`, calls the OpenAI-compatible JSON endpoint once, normalizes `report_markdown` and `data_notes`, saves the successful run to `data_asset.market_report_agent_run`, and returns `summary`, `context`, and `rendered_prompt`.
9. Frontend renders the Markdown document and provides collapsible `使用的 Prompt` and `输入给 AI 的结构化数据`.

---

### Task 1: Backend Agent Service

**Files:**
- Create: `app/services/report_agent.py`
- Modify: `app/routers/tasks.py`
- Test: `tests/test_market_report_agent.py`

- [x] Add tests for building market report context from dashboard payload.
- [x] Add tests for rendering prompt with `{{market_context_json}}`.
- [x] Add tests for parsing Markdown report JSON fields.
- [x] Add API test for `POST /api/voc/events/{event_id}/market/report-agent/run`.
- [x] Add API test for `GET /api/voc/events/{event_id}/market/report-agent/latest`.
- [x] Implement the minimal service and route to pass tests.

### Task 2: Frontend Summary Card

**Files:**
- Modify: `frontend/src/types/vocMarket.ts`
- Modify: `frontend/src/app/voc/events/market/page.tsx`
- Create: `frontend/src/components/voc/MarketAiSummaryCard.tsx`
- Test: `tests/test_next_frontend_architecture.py`

- [x] Add architecture test for the summary card and API path.
- [x] Implement client component with latest-result loading, manual regenerate, copy/error/loading states, and Markdown rendering.
- [x] Render the card near the top of market dashboard.
- [x] Run `npm run typecheck`.

### Task 3: Verification

- [x] Run `python -m pytest tests/test_market_report_agent.py -q`.
- [x] Run relevant existing frontend architecture and system settings tests.
- [x] Run `npm run typecheck`.
- [ ] Hit market dashboard route and backend report-agent endpoint.
- [x] Check Chinese strings with UTF-8-safe reads and avoid broad backend rewrites.
