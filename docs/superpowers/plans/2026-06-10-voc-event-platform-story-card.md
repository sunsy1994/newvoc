# VOC Event Platform Story Card Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a story-led "平台效率与渠道选择" card to complete the market dashboard story.

**Architecture:** The backend will aggregate platform-level volume, engagement, effective comments, and purchase signal metrics from existing DWD data and comment label JSON. The frontend will render one platform story card that reuses `ChannelStackedBars` and adds a compact platform efficiency ranking.

**Tech Stack:** FastAPI service functions, PostgreSQL JSONB aggregation, Next.js App Router, TypeScript, Tailwind CSS.

---

### Task 1: Backend Platform Story

**Files:**
- Modify: `app/services/event_voc_insights.py`
- Test: `tests/test_event_market_dashboard.py`

- [ ] Write a failing unit test for `build_platform_story`.
- [ ] Implement rules for core platform, volume contribution, per-post engagement, effective comment rate, and purchase signal rate.
- [ ] Add `fetch_event_platform_story(conn, event_id)` and include `platform_story` in `get_voc_event_market_dashboard`.

### Task 2: Frontend Platform Story Card

**Files:**
- Modify: `frontend/src/types/vocMarket.ts`
- Create: `frontend/src/components/voc/PlatformStoryCard.tsx`
- Modify: `frontend/src/app/voc/events/market/page.tsx`
- Test: `tests/test_next_frontend_architecture.py`

- [ ] Add TypeScript types for `platform_story`.
- [ ] Render conclusion, core platform metrics, platform efficiency ranking, and reused `ChannelStackedBars`.
- [ ] Replace the old standalone channel distribution card.

### Task 3: Verification

- [ ] Run `python -m pytest tests/test_event_market_dashboard.py tests/test_next_frontend_architecture.py -q`.
- [ ] Run `npm run typecheck`.
- [ ] Run `npm run build`.
