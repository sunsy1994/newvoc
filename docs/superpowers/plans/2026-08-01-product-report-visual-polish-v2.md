# Product Report Visual Polish V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the product department chart mode as a polished 1-2-1-1 story layout without dense tick charts.

**Architecture:** Add four product-only report template IDs and a focused `ProductCharts.tsx` renderer while retaining the existing L6 evidence relationship component. Update the deterministic backend chart mapping and the shared report grid only through product chart IDs so market and sales reports remain unchanged.

**Tech Stack:** React, TypeScript, native SVG/HTML, Tailwind CSS, Python, pytest, Next.js.

## Global Constraints

- Do not change product Agent prompts, API shapes, source metrics, or calculations.
- Product focus and opportunity must not use F5 Tick Rows.
- Product sentiment must not use L15 Tick Ballot.
- Market, sales, summary mode, and evidence mode must remain unchanged.
- Use native SVG/HTML only; do not add a chart runtime or CDN.
- Preserve empty states, keyboard access, accessible labels, and reduced-motion behavior.

---

### Task 1: Product-only chart contracts

**Files:**
- Modify: `app/services/report_visuals.py`
- Modify: `frontend/src/components/voc/report-visuals/types.ts`
- Modify: `frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx`
- Create: `frontend/src/components/voc/report-visuals/ProductCharts.tsx`
- Test: `tests/test_report_visuals.py`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Produces template IDs `P1`, `P2`, `P3`, and `P4`.
- Maps product charts to `P1`, `P2`, `P3`, `L6`, `P4` in their existing order.

- [ ] Write failing backend and frontend registry tests for the four product IDs.
- [ ] Run focused tests and verify RED.
- [ ] Add the template IDs, registry entries, and minimal exported product chart components.
- [ ] Change only `build_product_report_charts` template mapping.
- [ ] Run focused tests and verify GREEN.

### Task 2: Product focus, sentiment, and opportunity visuals

**Files:**
- Modify: `frontend/src/components/voc/report-visuals/ProductCharts.tsx`
- Test: `tests/test_next_frontend_architecture.py`
- Test: `tests/test_product_report_agent.py`

**Interfaces:**
- `P1ProductFocusBars`: consumes aspect, mention rate, comment count, and positive rate.
- `P2SentimentStack`: consumes positive, neutral, and negative rates totaling 100.
- `P3OpportunityLanes`: consumes `point_type`, aspect, opportunity score, mention rate, and related available fields.

- [ ] Write failing mapping and server-render tests for real fields, zero values, long labels, empty data, and no tick markup.
- [ ] Verify RED.
- [ ] Implement continuous rounded focus bars with direct numeric labels.
- [ ] Implement continuous 100% sentiment bars with three color segments.
- [ ] Implement surprise/opportunity/risk lanes with deterministic ordering and direct values.
- [ ] Verify GREEN.

### Task 3: Full-width PKO matrix and report layout

**Files:**
- Modify: `frontend/src/components/voc/report-visuals/ProductCharts.tsx`
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Modify: `frontend/src/components/voc/report-visuals/NarrativeCharts.tsx`
- Test: `tests/test_next_frontend_architecture.py`
- Test: `tests/test_product_report_agent.py`

**Interfaces:**
- `P4PkoMatrix`: consumes existing dimension result matrix rows.
- Product grid layout is full, half/half, full, full based on chart IDs.

- [ ] Write failing tests for the 1-2-1-1 layout and matrix row/column rendering.
- [ ] Verify RED.
- [ ] Implement full-width matrix with sticky-readable first column and horizontal overflow.
- [ ] Give L6 a bounded full-width canvas and stable detail region without changing its data mapping.
- [ ] Implement product-specific grid spans without changing other departments.
- [ ] Verify GREEN.

### Task 4: Alignment polish and verification

**Files:**
- Modify only files above when required by verified layout issues.

- [ ] Add source/render assertions for aligned title, insight strip, chart body, and source footer.
- [ ] Run product report and frontend architecture tests.
- [ ] Run `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider`.
- [ ] Run `npm run typecheck` and `npm run build` in `frontend`.
- [ ] If local services are running, inspect the product AI summary chart mode at desktop and narrow widths.
- [ ] Run `git diff --check` and commit `feat: polish product report chart mode`.
