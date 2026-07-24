# AutoVOC AI Report SVG Visuals Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build fixed, data-grounded SVG report templates for the event report and the market, product, and sales AI summaries.

**Architecture:** Python chart builders convert existing dashboard contexts into a versioned `chart_spec`; LLM output is normalized into fixed narrative fields and cannot alter chart values. React renders the saved specs through a closed SVG component registry derived from the selected Lieflat Lupi/Basics templates and recolored with AutoVOC theme tokens.

**Tech Stack:** Python 3.12, FastAPI, PostgreSQL JSONB, React 18, Next.js 14, TypeScript, native SVG, Tailwind CSS.

## Global Constraints

- Work only in `D:\voc\story1\.worktrees\lieflat-ai-report-visuals` on branch `codex/lieflat-ai-report-visuals`.
- Use only `F3`, `F4`, `F5`, `F6`, `F7`, `F8`, `L12`, `L13`, and `L14`; do not add ECharts, Chart.js, CDN scripts, or online fonts.
- Chart type, position, sorting, and source fields are deterministic code; LLM generates only fixed narrative text fields.
- Do not invent missing values, demo rows, competitors, dimensions, or trends.
- Use AutoVOC CSS theme variables rather than Lieflat Mono colors.
- Preserve Lieflat SVG data encoding and template geometry; retain noncommercial attribution and license notice.
- Product copy reports opportunities, risks, surprises, conversion signals, and PKO facts; it does not generate product recommendations.
- PKO L12 renders at most 50 real records with deterministic ordering and states `displayed / total`.
- Historical report rows must restore the saved narrative and chart spec without rerunning the LLM.
- Every task follows TDD and ends with a focused review and commit.

---

## File Structure

### Backend

- Create `app/services/report_visuals.py`: typed deterministic chart builders and fixed template order.
- Modify `app/services/report_agent.py`: structured department narratives, chart specs, persistence compatibility.
- Modify `app/agents/report/builder.py`: comprehensive report uses the shared fixed chart builders.
- Modify `app/services/system_settings.py`: versioned fixed-output prompt contracts.
- Modify `schema/data_access_schema.sql`: no new table; document JSONB payload compatibility only if schema comments exist.

### Frontend

- Create `frontend/src/components/voc/report-visuals/types.ts`: strict discriminated chart types.
- Create `frontend/src/components/voc/report-visuals/chartTheme.ts`: AutoVOC SVG theme helpers.
- Create `frontend/src/components/voc/report-visuals/ReportVisualShell.tsx`: title, insight, source, empty state, accessible fallback.
- Create `frontend/src/components/voc/report-visuals/BasicsCharts.tsx`: F3–F8 SVG components.
- Create `frontend/src/components/voc/report-visuals/NarrativeCharts.tsx`: L12–L14 SVG components.
- Create `frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx`: closed `template_id` registry.
- Modify `frontend/src/types/vocMarket.ts`: saved report narrative/chart contracts.
- Modify `frontend/src/components/voc/ReportAiSummaryCard.tsx`: summary/chart/evidence modes and registry rendering.

### Tests and notices

- Create `tests/test_report_visuals.py`: backend chart contracts and edge cases.
- Modify `tests/test_market_report_agent.py`.
- Modify `tests/test_product_report_agent.py`.
- Modify `tests/test_sales_report_agent.py`.
- Modify `tests/test_event_report_agent.py`.
- Modify `tests/test_next_frontend_architecture.py`.
- Create `docs/licenses/lieflat-charts-noncommercial.md`.

---

### Task 1: Deterministic Report Chart Contracts

**Files:**
- Create: `app/services/report_visuals.py`
- Create: `tests/test_report_visuals.py`
- Create: `docs/licenses/lieflat-charts-noncommercial.md`

**Interfaces:**
- Consumes: market, product, and sales context dictionaries already returned by `build_market_report_context`, `build_product_report_context`, and `build_sales_report_context`.
- Produces:
  - `build_market_report_charts(context: dict[str, Any]) -> list[dict[str, Any]]`
  - `build_product_report_charts(context: dict[str, Any]) -> list[dict[str, Any]]`
  - `build_sales_report_charts(context: dict[str, Any]) -> list[dict[str, Any]]`
  - `build_event_report_charts(market: dict[str, Any], product: dict[str, Any], sales: dict[str, Any]) -> list[dict[str, Any]]`

- [ ] **Step 1: Write fixed-order failing tests**

```python
from app.services.report_visuals import (
    build_event_report_charts,
    build_market_report_charts,
    build_product_report_charts,
    build_sales_report_charts,
)


def test_market_report_chart_order_is_fixed():
    charts = build_market_report_charts(
        {
            "volume_trend": [{"date": "2026-07-01", "total_volume": 12, "content_count": 2, "comment_count": 10}],
            "hot_topics": {"topics": [{"topic": "外观", "comment_count": 8, "content_count": 2}]},
            "platform": {"platform_efficiency": []},
            "feedback_quality": {"sentiment_distribution": [{"label": "正向", "count": 7, "rate": 70}]},
        }
    )
    assert [item["template_id"] for item in charts] == ["F3", "F5", "F8", "L14"]


def test_product_report_chart_order_is_fixed():
    charts = build_product_report_charts(
        {
            "product_focus": {"aspects": []},
            "product_opportunity": {"surprise_points": [], "pain_points": [], "conversion_points": []},
            "pko": {"evidence_comments": [], "dimension_result_matrix": []},
        }
    )
    assert [item["template_id"] for item in charts] == ["F5", "F6", "F5", "L12", "F7"]


def test_sales_report_chart_order_is_fixed():
    charts = build_sales_report_charts(
        {
            "lead_quality": {"summary": {}, "purchase_signal_distribution": [], "intent_distribution": []},
            "lead_source": {"platform_efficiency": []},
        }
    )
    assert [item["template_id"] for item in charts] == ["L13", "F4", "F5", "F6"]
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```powershell
python -m pytest tests/test_report_visuals.py -q -p no:cacheprovider
```

Expected: collection fails because `app.services.report_visuals` does not exist.

- [ ] **Step 3: Define the closed chart-spec builder**

Implement a private helper and the public fixed builders:

```python
from __future__ import annotations

from typing import Any


def _chart(
    chart_id: str,
    template_id: str,
    title: str,
    subtitle: str,
    source_label: str,
    data: list[dict[str, Any]],
    *,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "chart_id": chart_id,
        "template_id": template_id,
        "title": title,
        "subtitle": subtitle,
        "insight": "",
        "source_label": source_label,
        "data": data,
        "meta": meta or {},
    }
```

Each public builder returns the exact order asserted above. Use only the existing fields described in the design spec.

- [ ] **Step 4: Add transformation and empty-state tests**

```python
def test_l12_keeps_real_records_and_caps_at_fifty():
    rows = [
        {
            "comment_id": f"c-{index:03d}",
            "target": "竞品A",
            "dimension": "空间",
            "result": "优势",
            "comment_text": f"原声 {index}",
            "interaction_cnt": 100 - index,
            "published_at": f"2026-07-{(index % 28) + 1:02d}",
        }
        for index in range(60)
    ]
    chart = build_product_report_charts(
        {
            "product_focus": {"aspects": []},
            "product_opportunity": {"surprise_points": [], "pain_points": [], "conversion_points": []},
            "pko": {"evidence_comments": rows, "dimension_result_matrix": []},
        }
    )[3]
    assert len(chart["data"]) == 50
    assert chart["meta"] == {"displayed_count": 50, "total_count": 60, "unit": "条对比评论"}
    assert chart["data"][0]["comment_id"] == "c-000"


def test_missing_data_stays_empty():
    charts = build_market_report_charts({})
    assert all(chart["data"] == [] for chart in charts)
    assert all(chart["meta"]["empty_reason"] for chart in charts)
```

- [ ] **Step 5: Implement deterministic transformations**

Rules:

```python
PKO_RESULT_BUCKETS = {
    "优势": "advantage",
    "劣势": "disadvantage",
    "中性": "neutral",
}


def _pko_sort_key(row: dict[str, Any]) -> tuple[int, str, str]:
    return (
        -int(row.get("interaction_cnt") or 0),
        str(row.get("published_at") or ""),
        str(row.get("comment_id") or ""),
    )
```

Normalize missing PKO targets to `其他对象`, missing dimensions to `未明确维度`, and missing results to `unclear`. Do not synthesize a record when `evidence_comments` is empty.

- [ ] **Step 6: Add the noncommercial attribution**

Create `docs/licenses/lieflat-charts-noncommercial.md` with:

```markdown
# Lieflat Charts attribution

Selected SVG structures in `frontend/src/components/voc/report-visuals/` are adapted from Lieflat Charts by moxt and Codex.

Source: https://github.com/larashero3-dotcom/lieflat-charts
License: PolyForm Noncommercial License 1.0.0

AutoVOC is currently a personal, noncommercial project. Commercial use requires a separate license review.
```

- [ ] **Step 7: Run focused tests**

Run:

```powershell
python -m pytest tests/test_report_visuals.py -q -p no:cacheprovider
```

Expected: all Task 1 tests pass.

- [ ] **Step 8: Commit**

```powershell
git add app/services/report_visuals.py tests/test_report_visuals.py docs/licenses/lieflat-charts-noncommercial.md
git commit -m "feat: define fixed report visual contracts"
```

---

### Task 2: Basics SVG Components F3–F8

**Files:**
- Create: `frontend/src/components/voc/report-visuals/types.ts`
- Create: `frontend/src/components/voc/report-visuals/chartTheme.ts`
- Create: `frontend/src/components/voc/report-visuals/ReportVisualShell.tsx`
- Create: `frontend/src/components/voc/report-visuals/BasicsCharts.tsx`
- Modify: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: `ReportVisualChart` discriminated by `template_id`.
- Produces: `F3HairlineArea`, `F4TickDonut`, `F5TickRows`, `F6PairedRungs`, `F7StackedRungs`, and `F8PlumbScatter`.

- [ ] **Step 1: Add frontend contract tests**

```python
def test_report_visuals_use_native_svg_and_autovoc_tokens():
    root = Path("frontend/src/components/voc/report-visuals")
    source = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.tsx"))
    assert "<svg" in source
    assert "var(--theme-primary)" in source
    assert "echarts" not in source.lower()
    assert "chart.js" not in source.lower()
    assert "cdn.jsdelivr" not in source.lower()


def test_basics_chart_exports_are_closed():
    source = Path("frontend/src/components/voc/report-visuals/BasicsCharts.tsx").read_text(encoding="utf-8")
    for export_name in [
        "F3HairlineArea",
        "F4TickDonut",
        "F5TickRows",
        "F6PairedRungs",
        "F7StackedRungs",
        "F8PlumbScatter",
    ]:
        assert f"export function {export_name}" in source
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
python -m pytest tests/test_next_frontend_architecture.py -q -p no:cacheprovider
```

Expected: the new component directory and exports do not exist.

- [ ] **Step 3: Define strict chart types**

Create:

```ts
export type ReportTemplateId = "F3" | "F4" | "F5" | "F6" | "F7" | "F8" | "L12" | "L13" | "L14";

export type ReportVisualChart = {
  chart_id: string;
  template_id: ReportTemplateId;
  title: string;
  subtitle: string;
  insight: string;
  source_label: string;
  data: Array<Record<string, unknown>>;
  meta: {
    displayed_count?: number;
    total_count?: number;
    unit?: string;
    empty_reason?: string;
  };
};
```

- [ ] **Step 4: Build theme and accessible shell**

`chartTheme.ts` exports only AutoVOC variable strings:

```ts
export const reportChartTheme = {
  primary: "var(--theme-primary)",
  secondary: "var(--theme-selected-text)",
  ink: "var(--theme-ink)",
  body: "var(--theme-body)",
  muted: "var(--theme-muted)",
  border: "var(--theme-border)",
  panel: "var(--theme-soft-panel)",
  white: "var(--theme-white)",
} as const;
```

`ReportVisualShell` renders title, subtitle, insight, source, `role="figure"`, an `aria-label`, and a stable empty state when `data.length === 0`.

- [ ] **Step 5: Port F3–F8 SVG structures**

Use the matching card and render blocks from the Lieflat Basics gallery as the starting geometry. Requirements:

- F3 uses one shared numeric scale beginning at zero.
- F4 converts percentages to tick counts without changing the sum.
- F5 uses horizontal length proportional to a single numeric value.
- F6 uses a shared scale for both comparable series.
- F7 computes each segment width from the row total.
- F8 maps X and Y independently and labels every point through focusable `<g tabIndex={0}>`.

Do not include the gallery page layout, demo data, `Math.random`, external fonts, or Mono colors.

- [ ] **Step 6: Add zero-value and long-label tests**

Add static contract assertions for:

```python
assert 'Math.max(1' in source
assert 'textLength' in source or 'truncateSvgLabel' in source
assert 'prefers-reduced-motion' in source
assert 'tabIndex={0}' in source
```

The implementation must use a named `truncateSvgLabel(label, maxChars)` helper rather than reducing font size below the design minimum.

- [ ] **Step 7: Run verification**

```powershell
python -m pytest tests/test_next_frontend_architecture.py -q -p no:cacheprovider
npm run typecheck
```

Expected: both commands pass.

- [ ] **Step 8: Commit**

```powershell
git add frontend/src/components/voc/report-visuals tests/test_next_frontend_architecture.py
git commit -m "feat: add themed basics report charts"
```

---

### Task 3: Narrative SVG Components L12–L14 and Registry

**Files:**
- Create: `frontend/src/components/voc/report-visuals/NarrativeCharts.tsx`
- Create: `frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx`
- Modify: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: `ReportVisualChart`.
- Produces:
  - `L12TypeColonnade`
  - `L13HourglassStream`
  - `L14HundredField`
  - `ReportChartRegistry({ chart }: { chart: ReportVisualChart })`

- [ ] **Step 1: Add failing registry tests**

```python
def test_report_chart_registry_is_closed_and_complete():
    source = Path("frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx").read_text(encoding="utf-8")
    for template_id in ["F3", "F4", "F5", "F6", "F7", "F8", "L12", "L13", "L14"]:
        assert f'{template_id}:' in source
    assert "dangerouslySetInnerHTML" not in source
    assert "eval(" not in source
```

Add an L12 test asserting the implementation renders one path per record and exposes `comment_text` in accessible copy.

- [ ] **Step 2: Run tests and verify RED**

Run the frontend architecture test file. Expected: missing files and exports.

- [ ] **Step 3: Implement L12 Type Colonnade**

Use the Lieflat L12 geometry with these fixed mappings:

```ts
type PkoRecord = {
  comment_id: string;
  target: string;
  dimension: string;
  result_bucket: "advantage" | "disadvantage" | "neutral" | "unclear";
  comment_text: string;
};
```

- Group left labels by `target`.
- Group right circular nodes by `dimension`.
- Render one curved `<path>` per record.
- Assign stroke from the result bucket.
- Wrap each record path in a keyboard-focusable group and expose the original comment through `<title>` plus an on-page detail panel.
- Show `展示 X / 总计 N 条` from `meta`.

- [ ] **Step 4: Implement L13 and L14**

- L13 stages preserve input order and width is proportional to `count / first_count`.
- L14 uses exactly 100 deterministic cells when percentage data is available; assign remainder caused by rounding to an explicit `rounding_remainder` neutral group rather than altering a business category.

- [ ] **Step 5: Implement the closed registry**

```tsx
const REPORT_CHARTS = {
  F3: F3HairlineArea,
  F4: F4TickDonut,
  F5: F5TickRows,
  F6: F6PairedRungs,
  F7: F7StackedRungs,
  F8: F8PlumbScatter,
  L12: L12TypeColonnade,
  L13: L13HourglassStream,
  L14: L14HundredField,
} satisfies Record<ReportTemplateId, React.ComponentType<ChartProps>>;
```

Do not accept HTML, JavaScript, or a component name from the API.

- [ ] **Step 6: Run verification**

```powershell
python -m pytest tests/test_next_frontend_architecture.py -q -p no:cacheprovider
npm run typecheck
```

Expected: both pass.

- [ ] **Step 7: Commit**

```powershell
git add frontend/src/components/voc/report-visuals tests/test_next_frontend_architecture.py
git commit -m "feat: add narrative report charts"
```

---

### Task 4: Department Report Templates and Structured LLM Copy

**Files:**
- Modify: `app/services/report_agent.py`
- Modify: `app/services/system_settings.py`
- Modify: `tests/test_market_report_agent.py`
- Modify: `tests/test_product_report_agent.py`
- Modify: `tests/test_sales_report_agent.py`
- Modify: `frontend/src/types/vocMarket.ts`
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Modify: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: Task 1 chart builders and Task 3 `ReportChartRegistry`.
- Produces: each department payload contains `summary.report_narrative` and `summary.structured_report.charts`.

- [ ] **Step 1: Add backend failing tests**

For each department assert:

```python
assert result["summary"]["report_narrative"] == {
    "headline": "测试标题",
    "executive_summary": "测试摘要",
    "section_insights": {
        "market_rhythm": "节奏判断",
        "market_topics": "话题判断",
        "market_platforms": "平台判断",
        "market_feedback": "反馈判断",
    },
    "data_notes": [],
}
assert [chart["template_id"] for chart in result["summary"]["structured_report"]["charts"]] == ["F3", "F5", "F8", "L14"]
```

Product expected IDs: `["F5", "F6", "F5", "L12", "F7"]`.
Sales expected IDs: `["L13", "F4", "F5", "F6"]`.

- [ ] **Step 2: Run the three test files and verify RED**

```powershell
python -m pytest tests/test_market_report_agent.py tests/test_product_report_agent.py tests/test_sales_report_agent.py -q -p no:cacheprovider
```

Expected: report narrative and structured charts are absent.

- [ ] **Step 3: Version the prompt contracts**

Change department prompt versions to `*_v2`. Each prompt requires only:

```json
{
  "headline": "",
  "executive_summary": "",
  "section_insights": {
    "fixed_section_code": ""
  },
  "data_notes": []
}
```

The prompt must state that chart values and types are system-owned and that missing input cannot be inferred.

- [ ] **Step 4: Normalize narrative fields safely**

Add:

```python
def normalize_report_narrative(
    payload: dict[str, Any],
    section_codes: tuple[str, ...],
    fallback_insights: dict[str, str],
) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    raw_insights = raw.get("section_insights") if isinstance(raw.get("section_insights"), dict) else {}
    return {
        "headline": str(raw.get("headline") or "").strip(),
        "executive_summary": str(raw.get("executive_summary") or "").strip(),
        "section_insights": {
            code: str(raw_insights.get(code) or fallback_insights.get(code) or "").strip()
            for code in section_codes
        },
        "data_notes": normalize_data_notes(raw.get("data_notes")),
    }
```

Attach each section insight to the matching deterministic chart by `chart_id`.

- [ ] **Step 5: Preserve backward compatibility**

`normalize_cached_report_row` must accept:

- v2 rows with `report_narrative` and `structured_report`.
- v1 rows with `report_markdown`; the UI continues to show Markdown without fabricated charts.

Add a test that loads a v1 row and asserts no exception and no invented chart spec.

- [ ] **Step 6: Add three frontend modes**

Replace the current two-mode union with:

```ts
type ReportViewMode = "summary" | "charts" | "evidence";
```

- Summary renders fixed narrative sections.
- Charts maps `structuredReport.charts` through `ReportChartRegistry`.
- Evidence renders data notes and available evidence/calculation notes.
- Legacy Markdown remains a fallback only when structured data is absent.

- [ ] **Step 7: Run focused verification**

```powershell
python -m pytest tests/test_market_report_agent.py tests/test_product_report_agent.py tests/test_sales_report_agent.py tests/test_next_frontend_architecture.py -q -p no:cacheprovider
npm run typecheck
```

Expected: all pass.

- [ ] **Step 8: Commit**

```powershell
git add app/services/report_agent.py app/services/system_settings.py frontend/src/types/vocMarket.ts frontend/src/components/voc/ReportAiSummaryCard.tsx tests
git commit -m "feat: add fixed department report templates"
```

---

### Task 5: Event Comprehensive Report Integration

**Files:**
- Modify: `app/agents/report/builder.py`
- Modify: `tests/test_event_report_agent.py`
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Modify: `frontend/src/components/assets/AssetLibraryPage.tsx` only if the existing report detail path bypasses `StructuredReportView`.

**Interfaces:**
- Consumes: `build_event_report_charts`.
- Produces: event report chart IDs fixed to `["F3", "L14", "F6", "L13"]`.

- [ ] **Step 1: Add event report failing tests**

```python
def test_event_report_uses_four_cross_department_charts():
    payload = build_event_report_payload(
        event_id="event-1",
        market_context=market_context,
        product_context=product_context,
        sales_context=sales_context,
        llm_summary={"executive_summary": ["结论"], "recommendations": [], "sections": []},
    )
    charts = payload["summary"]["structured_report"]["charts"]
    assert [chart["template_id"] for chart in charts] == ["F3", "L14", "F6", "L13"]
```

Add a persistence round-trip test asserting the saved `summary_json.structured_report.charts` is returned unchanged.

- [ ] **Step 2: Run event tests and verify RED**

```powershell
python -m pytest tests/test_event_report_agent.py tests/test_asset_library.py -q -p no:cacheprovider
```

Expected: current metric/bar/trend/table chart types differ from the fixed SVG IDs.

- [ ] **Step 3: Replace only the event chart builder**

Call:

```python
charts = build_event_report_charts(market_context, product_context, sales_context)
```

Keep existing evidence references, calculation notes, template sections, event title, storage fields, and asset detail behavior.

- [ ] **Step 4: Ensure saved reports render through the shared registry**

Verify `StructuredReportView` is the single renderer used by:

- chat report detail
- department AI summary
- report asset detail

Do not add a separate asset-only chart implementation.

- [ ] **Step 5: Run focused verification**

```powershell
python -m pytest tests/test_event_report_agent.py tests/test_asset_library.py tests/test_next_frontend_architecture.py -q -p no:cacheprovider
npm run typecheck
```

Expected: all pass.

- [ ] **Step 6: Commit**

```powershell
git add app/agents/report/builder.py frontend/src/components/voc/ReportAiSummaryCard.tsx frontend/src/components/assets/AssetLibraryPage.tsx tests
git commit -m "feat: unify event report visuals"
```

---

### Task 6: Full Verification and Visual Acceptance

**Files:**
- Modify only files required by failures found in this task.
- Create: `docs/audits/2026-07-24-lieflat-report-visuals-verification.md`

**Interfaces:**
- Consumes: completed implementation.
- Produces: reproducible verification evidence and screenshots.

- [ ] **Step 1: Run all backend tests**

```powershell
python -m pytest -q -p no:cacheprovider
```

Expected: zero failures.

- [ ] **Step 2: Run frontend checks**

```powershell
cd frontend
npm run typecheck
npm run build
```

Expected: both exit 0. If the Codex Windows sandbox produces the known `spawn EPERM`, rerun `npm run build` outside the sandbox and record the exact result; do not call the build successful without an exit code of 0.

- [ ] **Step 3: Run source safety checks**

```powershell
rg -n "echarts|chart\\.js|cdn\\.jsdelivr|dangerouslySetInnerHTML|eval\\(" frontend/src/components/voc/report-visuals
git diff --check
```

Expected: the dependency/security search returns no matches and `git diff --check` exits 0.

- [ ] **Step 4: Start the application with the real backend**

Use the existing local `DATABASE_URL`, start FastAPI on `8000`, and Next.js on `3000`. Do not use mock data.

- [ ] **Step 5: Capture visual acceptance screenshots**

For one real event with complete data, capture:

- market summary mode
- market chart mode
- product chart mode including L12 and F7
- sales chart mode
- event comprehensive report chart mode
- report asset reopening the same saved chart spec

Check at 1280px and 1440px widths.

- [ ] **Step 6: Verify empty states**

Open an event missing at least one relevant dataset, or invoke the relevant builder test fixture. Confirm the fixed chart remains in place with an explicit empty reason and no demo data.

- [ ] **Step 7: Write the verification report**

Record:

- commands and exit codes
- test counts
- screenshots and routes
- actual event ID used
- any known non-blocking limitation
- confirmation that no external chart runtime was loaded

- [ ] **Step 8: Request code review**

Use `superpowers:requesting-code-review` and require no Critical or Important findings before completion.

- [ ] **Step 9: Fix review findings with TDD**

For every accepted finding:

1. Add a failing test or reproducible visual case.
2. Verify RED.
3. Make the smallest fix.
4. Re-run the focused and full verification commands.

- [ ] **Step 10: Commit**

```powershell
git add docs/audits/2026-07-24-lieflat-report-visuals-verification.md <only-files-fixed-in-this-task>
git commit -m "test: verify report visual upgrade"
```

---

## Plan Self-Review

- Spec coverage: all four report types, nine SVG templates, fixed storylines, L12 PKO cap, LLM boundary, history, empty states, theme, accessibility, license, and exclusions have implementation tasks.
- Placeholder scan: every implementation step has concrete files, interfaces, commands, and expected outcomes.
- Type consistency: backend and frontend use snake_case saved JSON fields (`chart_id`, `template_id`, `source_label`, `displayed_count`, `total_count`); `ReportVisualChart` matches the Task 1 payload.
- Scope: the work changes report generation/rendering only; it does not redesign dashboard body layouts, add chart libraries, or modify other agents.
