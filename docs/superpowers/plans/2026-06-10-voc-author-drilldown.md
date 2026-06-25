# VOC Author Drilldown Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an author drilldown from the market dashboard Top authors list to a global author detail page with KOL profile, participated events, content list, comment quality, and author-event-user-profile Sankey evidence.

**Architecture:** Add one backend aggregate endpoint under `/api/voc/authors/{author_id}/detail`, backed by existing `dwd_author`, `dwd_content`, `dwd_comment`, `user_profile_kol`, and `user_profile_comment_result`. Add a Next.js detail route and small focused components; keep the market dashboard story-card style and avoid new database fields.

**Tech Stack:** FastAPI, psycopg, PostgreSQL, Next.js App Router, TypeScript, Tailwind CSS, lucide-react, lightweight SVG for Sankey.

---

### Task 1: Backend Author Detail Aggregate

**Files:**
- Modify: `app/services/event_voc_insights.py`
- Modify: `app/routers/tasks.py`
- Test: `tests/test_event_market_dashboard.py`
- Test: `tests/test_task_api.py`

- [ ] Add `get_voc_author_detail(author_id)` that returns author profile, global metrics, latest KOL profile, participated event rows, content rows, comment quality rows, and Sankey links.
- [ ] Add route `/api/voc/authors/{author_id}/detail`.
- [ ] Add tests for Sankey aggregation and route behavior.

### Task 2: Frontend Author Detail Page

**Files:**
- Modify: `frontend/src/types/vocMarket.ts`
- Modify: `frontend/src/components/voc/SubjectStoryCard.tsx`
- Create: `frontend/src/components/voc/AuthorSankey.tsx`
- Create: `frontend/src/components/voc/AuthorDetailPage.tsx`
- Create: `frontend/src/app/voc/authors/[authorId]/page.tsx`
- Test: `tests/test_next_frontend_architecture.py`

- [ ] Make Top author names clickable.
- [ ] Render author global profile and KOL fields.
- [ ] Render participated events, content list, comment quality, and SVG Sankey.
- [ ] Add architecture tests for route, link, and Sankey component.

### Task 3: Verification

**Commands:**
- `python -m pytest tests/test_event_market_dashboard.py tests/test_task_api.py tests/test_next_frontend_architecture.py -q`
- `npm run typecheck`
- `npm run build`
