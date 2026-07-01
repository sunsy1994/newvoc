# Product and Sales Visual Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Visually align the product and sales dashboards with the market dashboard while preserving all existing data, calculations, and interactions.

**Architecture:** Keep the existing page routes and API payloads. Recompose the current story components with market-aligned card primitives and department-specific grids; make no backend changes and introduce no new dependencies.

**Tech Stack:** Next.js 14, React 18, TypeScript, Tailwind CSS, Lucide React.

## Global Constraints

- Do not change API calls, payload types, formulas, or event selection behavior.
- Reuse only current product and sales payload fields.
- Preserve all filters, drawers, modals, tooltips, and AI summary actions.
- Commit product, sales, and final QA separately.

---

### Task 1: Shared dashboard hierarchy

**Files:**
- Modify: `frontend/src/components/voc/VocDashboardHeader.tsx`
- Modify: `frontend/src/app/voc/events/product/page.tsx`
- Modify: `frontend/src/app/voc/events/sales/page.tsx`

- [ ] Record the existing product and sales screenshots as the visual baseline.
- [ ] Add department-specific header descriptions without changing controls.
- [ ] Apply the market dashboard's maximum width and spacing rhythm to both routes.
- [ ] Run `npm run typecheck`; expect exit code 0.

### Task 2: Product dashboard refresh

**Files:**
- Modify: `frontend/src/components/voc/ProductFocusStoryCard.tsx`
- Modify: `frontend/src/components/voc/ProductOpportunityStoryCard.tsx`
- Modify: `frontend/src/components/voc/ProductPkoStoryCard.tsx`

- [ ] Recompose product focus into conclusion, compact KPI strip, quadrant, and ranked aspect rail using existing `aspects`.
- [ ] Recompose opportunity priority into one lead decision card plus compact ranked alternatives while preserving filters and evidence.
- [ ] Recompose PKO into KPI strip, dynamic target ranking, dimension matrix, and evidence workspace.
- [ ] Run `npm run typecheck`; expect exit code 0.
- [ ] Commit product-only changes.

### Task 3: Sales dashboard refresh

**Files:**
- Modify: `frontend/src/components/voc/SalesLeadQualityStoryCard.tsx`
- Modify: `frontend/src/components/voc/SalesLeadSourceEfficiencyPanel.tsx`

- [ ] Add a five-item KPI strip from the existing summary fields.
- [ ] Widen and rebalance the lead funnel and profile layout; stack it below the desktop breakpoint.
- [ ] Align the source-efficiency header, filters, channel view, content list, and follow-up users with the market card system.
- [ ] Run `npm run typecheck`; expect exit code 0.
- [ ] Commit sales-only changes.

### Task 4: Browser and production verification

**Files:**
- Create: `docs/audits/2026-07-01-product-sales-refresh/product-after.png`
- Create: `docs/audits/2026-07-01-product-sales-refresh/sales-after.png`
- Create: `docs/audits/2026-07-01-product-sales-refresh/design-qa.md`

- [ ] Run `npm run typecheck` and `npm run build`; both must exit 0.
- [ ] Cleanly restart the frontend and open both routes with real backend data.
- [ ] Verify product filters/evidence/PKO interactions and sales funnel/source/user interactions.
- [ ] Capture both pages and compare them with the market baseline for hierarchy, spacing, typography, colors, and readability.
- [ ] Fix every P0/P1/P2 issue, recapture, and write `design-qa.md` with `final result: passed`.
- [ ] Commit only the dashboard refresh and QA artifacts; exclude user workbook and sample-data changes.
