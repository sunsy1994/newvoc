# VOC Event Comment Quality Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a real-data "传播质量与用户记忆" story card to the VOC event market dashboard.

**Architecture:** The backend will aggregate `dwd_comment.comment_label_json` by event and append a `comment_quality` object to the existing market-dashboard API. The frontend will add typed payload fields and render one full-width card with a decision sentence, compact metrics, and two lightweight horizontal distributions.

**Tech Stack:** FastAPI service functions, PostgreSQL JSONB SQL, Next.js App Router, TypeScript, Tailwind CSS.

---

### Task 1: Backend Aggregation

**Files:**
- Modify: `app/services/event_voc_insights.py`
- Test: `tests/test_task_api.py`

- [ ] Add `fetch_event_comment_quality(conn, event_id)` that filters comments by `dwd_content.event_id`, reads `comment_label_json`, supports `mentioned_aspect` as array or string, and returns summary plus distribution arrays.
- [ ] Add the result as `comment_quality` in `get_voc_event_market_dashboard`.
- [ ] Add a test that monkeypatches the dashboard service and verifies the API shape includes `comment_quality`.

### Task 2: Frontend Story Card

**Files:**
- Modify: `frontend/src/types/vocMarket.ts`
- Create: `frontend/src/components/voc/CommentQualityStoryCard.tsx`
- Modify: `frontend/src/app/voc/events/market/page.tsx`
- Test: `tests/test_next_frontend_architecture.py`

- [ ] Add TypeScript types for `comment_quality`.
- [ ] Create a single card component with conclusion text, effective rate, positive rate, purchase signal rate, user memory Top 8, and user intent Top 8.
- [ ] Insert the card under channel distribution and hot posts.
- [ ] Add architecture tests to confirm the component and payload field are wired.

### Task 3: Verification

- [ ] Run `python -m pytest tests/test_task_api.py tests/test_next_frontend_architecture.py -q`.
- [ ] Run `npm run typecheck`.
- [ ] Run `npm run build`.
