# VOC Event Subject Story Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a story-led "传播主体与KOL带动" card to the VOC event market dashboard.

**Architecture:** The backend will aggregate existing `dwd_content`, `dwd_author`, `dwd_comment`, and `user_profile_kol` data into a compact `subject_story` payload. The frontend will render one coherent card with a rule conclusion, key metrics, subject contribution bars, KOL type contribution, and top author evidence.

**Tech Stack:** FastAPI service functions, PostgreSQL SQL aggregation, Next.js App Router, TypeScript, Tailwind CSS.

---

### Task 1: Backend Subject Story

**Files:**
- Modify: `app/services/event_voc_insights.py`
- Test: `tests/test_event_market_dashboard.py`

- [ ] Write a failing unit test for `build_subject_story`.
- [ ] Implement `build_subject_story` using author type/KOL contribution rows.
- [ ] Add `fetch_event_subject_story(conn, event_id)` and include it in `get_voc_event_market_dashboard`.

### Task 2: Frontend Story Card

**Files:**
- Modify: `frontend/src/types/vocMarket.ts`
- Create: `frontend/src/components/voc/SubjectStoryCard.tsx`
- Modify: `frontend/src/app/voc/events/market/page.tsx`
- Test: `tests/test_next_frontend_architecture.py`

- [ ] Add TypeScript types for `subject_story`.
- [ ] Render one story card that reuses `KolTypeBars` instead of creating a duplicate KOL chart.
- [ ] Replace the old standalone KOL card with the new story card.

### Task 3: Verification

- [ ] Run `python -m pytest tests/test_event_market_dashboard.py tests/test_next_frontend_architecture.py -q`.
- [ ] Run `npm run typecheck`.
- [ ] Run `npm run build`.
