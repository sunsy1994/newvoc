# VOC Event Product Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add the second `VOC看事件` submenu, `产品看板`, starting with the first story card: product focus overview based on real `comment_label_json` data.

**Architecture:** Reuse the market dashboard story-card pattern. Add a backend product dashboard API that aggregates event comments by `mentioned_aspect` and sentiment, then render one Next.js App Router page with event selection and a product-focus story card.

**Tech Stack:** FastAPI, psycopg, PostgreSQL JSONB, Next.js App Router, TypeScript, Tailwind CSS, lucide-react.

---

### Task 1: Product Focus Backend

**Files:**
- Modify: `app/services/event_voc_insights.py`
- Modify: `app/routers/tasks.py`
- Test: `tests/test_event_market_dashboard.py`
- Test: `tests/test_task_api.py`

- [ ] Add `build_product_focus_story(rows)` with a rule-based conclusion.
- [ ] Add `fetch_event_product_focus_story(conn, event_id)` reading `comment_label_json.mentioned_aspect`.
- [ ] Add `get_voc_event_product_dashboard(event_id)`.
- [ ] Expose `/api/voc/events/{event_id}/product-dashboard`.

### Task 2: Product Dashboard Frontend

**Files:**
- Modify: `frontend/src/config/navigation.ts`
- Modify: `frontend/src/types/vocMarket.ts`
- Create: `frontend/src/components/voc/ProductFocusStoryCard.tsx`
- Create: `frontend/src/app/voc/events/product/page.tsx`
- Test: `tests/test_next_frontend_architecture.py`

- [ ] Add `产品看板` under `VOC看事件`.
- [ ] Render event selector and product focus story card.
- [ ] Use existing AutoVOC card style and real API data only.

### Task 3: Verification

**Commands:**
- `python -m pytest tests/test_event_market_dashboard.py tests/test_task_api.py::test_voc_event_product_dashboard_api_returns_focus_story tests/test_next_frontend_architecture.py -q`
- `npm run typecheck`
- `npm run build`
