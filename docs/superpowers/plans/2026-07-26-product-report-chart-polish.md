# Product Report Chart Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the product AI report with a wider modal, above-chart narrative, an L6 multi-product-point PKO cluster field, and an L15 positive/neutral/negative tick tally using only existing report data.

**Architecture:** Extend the existing deterministic report chart contract with two closed template IDs, while retaining the raw aspect and PKO evidence rows already stored in report JSON. Add focused SVG components behind the existing registry, then make the shared report shell and department chart grid apply the approved layout without changing market, sales, event, or legacy cached reports.

**Tech Stack:** Python 3, FastAPI service layer, pytest, Next.js 14, React, TypeScript, Tailwind CSS, hand-written accessible SVG.

## Global Constraints

- Modify only the department AI report modal and the two product report charts described in the approved spec.
- `product-sentiment` changes from F6 to L15; `product-pko-evidence` changes from L12 to L6.
- Market sentiment, sales reports, event reports, and the other three product charts remain unchanged.
- L6 uses existing `pko.evidence_comments`; L15 uses existing `product_focus.aspects`.
- LLM output may populate bounded chart insight text only; it must not control template IDs, data, counts, percentages, colors, or positions.
- Do not add ECharts, Chart.js, CDN scripts, `dangerouslySetInnerHTML`, `eval`, random sampling, or demo data.
- Historical saved F6 and L12 reports must remain renderable.
- Use system theme colors and pure SVG.

---

## File Structure

- `app/services/report_visuals.py`: closed template list, L6/L15 data normalization, renderability, metadata, and new product chart IDs.
- `app/services/report_agent.py`: fixed product department chart contract used for prompt/cache validation.
- `frontend/src/components/voc/report-visuals/types.ts`: closed TypeScript template union.
- `frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx`: closed template-to-component registry.
- `frontend/src/components/voc/report-visuals/NarrativeCharts.tsx`: L6 cluster-field SVG and its pure mapping/layout helpers.
- `frontend/src/components/voc/report-visuals/SmallDataCharts.tsx`: L15 tick-tally SVG and its pure normalization/allocation helpers.
- `frontend/src/components/voc/report-visuals/ReportVisualShell.tsx`: shared title/subtitle/insight/source order.
- `frontend/src/components/voc/ReportAiSummaryCard.tsx`: modal size and L6 full-width grid span.
- `tests/test_report_visuals.py`: backend contract and deterministic data tests.
- `tests/test_product_report_agent.py`: product report/cache integration tests.
- `tests/test_next_frontend_architecture.py`: executable TypeScript/SSR and layout-contract tests.

---

### Task 1: Add L6 and L15 Backend Contracts

**Files:**
- Modify: `app/services/report_visuals.py`
- Modify: `app/services/report_agent.py`
- Test: `tests/test_report_visuals.py`
- Test: `tests/test_product_report_agent.py`

**Interfaces:**
- Consumes: existing product context fields `product_focus.aspects` and `pko.evidence_comments`.
- Produces: `normalize_chart_data("L6" | "L15", rows)`, fixed product chart sequence with L15 and L6, and unchanged raw evidence rows in saved chart data.

- [ ] **Step 1: Write failing closed-contract tests**

Add tests asserting the fixed product contract changes only the two approved templates:

```python
def test_product_report_uses_l15_and_l6_without_changing_other_charts():
    charts = build_product_report_charts(PRODUCT_CONTEXT)
    assert [(chart["chart_id"], chart["template_id"]) for chart in charts] == [
        ("product-focus", "F5"),
        ("product-sentiment", "L15"),
        ("product-opportunity", "F5"),
        ("product-pko-evidence", "L6"),
        ("product-pko-matrix", "F7"),
    ]
```

Add assertions that `REPORT_TEMPLATE_IDS` includes L6/L15 and still includes F6/L12 for historical caches.

Add two cache round-trip fixtures using the same current product prompt version:

```python
def test_product_cache_accepts_new_and_legacy_visual_contracts():
    assert normalize_cached_report_summary(NEW_L15_L6_PAYLOAD, PRODUCT_REPORT_PROMPT_VERSION)["structured_report"]["charts"] == NEW_L15_L6_PAYLOAD["structured_report"]["charts"]
    assert normalize_cached_report_summary(LEGACY_F6_L12_PAYLOAD, PRODUCT_REPORT_PROMPT_VERSION)["structured_report"]["charts"] == LEGACY_F6_L12_PAYLOAD["structured_report"]["charts"]
```

Also assert a mixed or partially upgraded sequence falls back to its valid
Markdown rather than being treated as a structured report.

- [ ] **Step 2: Write failing L6 normalization tests**

Use complete and malformed evidence rows:

```python
def test_l6_keeps_only_real_dimension_target_evidence_rows():
    rows = [
        {"comment_id": "c1", "comment_text": "外观比竞品更协调", "dimension": "外观", "target": "竞品A", "result_bucket": "advantage"},
        {"comment_id": "c2", "comment_text": "空间对比", "dimension": "", "target": "竞品B", "result_bucket": "neutral"},
        {"comment_id": "c3", "comment_text": "缺少车系", "dimension": "空间", "target": None, "result_bucket": "neutral"},
    ]
    normalized = normalize_chart_data("L6", rows)
    assert normalized == [rows[0]]
```

Assert row order and raw `comment_id`, `comment_text`, `dimension`, `target`, and `result_bucket` are preserved.

- [ ] **Step 3: Write failing L15 normalization tests**

Cover valid, missing, non-finite, and over-100 historical rates:

```python
def test_l15_requires_named_aspect_and_two_finite_rates():
    rows = [
        {"aspect": "外观", "positive_rate": 70, "negative_rate": 20},
        {"aspect": "空间", "positive_rate": 55, "negative_rate": None},
        {"aspect": "", "positive_rate": 40, "negative_rate": 30},
    ]
    assert normalize_chart_data("L15", rows) == [rows[0]]
```

Add a test for a deterministic helper:

```python
assert normalize_sentiment_rates(70, 20) == {
    "positive_rate": 70.0,
    "neutral_rate": 10.0,
    "negative_rate": 20.0,
}
assert normalize_sentiment_rates(80, 40) == {
    "positive_rate": pytest.approx(66.6667, rel=1e-4),
    "neutral_rate": 0.0,
    "negative_rate": pytest.approx(33.3333, rel=1e-4),
}
```

- [ ] **Step 4: Run the new tests and verify RED**

Run:

```powershell
python -m pytest tests/test_report_visuals.py tests/test_product_report_agent.py -q -p no:cacheprovider
```

Expected: failures because L6/L15 are absent and product charts still use F6/L12.

- [ ] **Step 5: Implement minimal backend validation and chart mapping**

In `report_visuals.py`:

```python
REPORT_TEMPLATE_IDS = {"F3", "F4", "F5", "F6", "F7", "F8", "L6", "L12", "L13", "L14", "L15"}

def normalize_sentiment_rates(positive: Any, negative: Any) -> dict[str, float] | None:
    if not _finite_non_negative(positive) or not _finite_non_negative(negative):
        return None
    positive_value = min(float(positive), 100.0)
    negative_value = min(float(negative), 100.0)
    selected_total = positive_value + negative_value
    if selected_total > 100.0:
        scale = 100.0 / selected_total
        positive_value *= scale
        negative_value *= scale
    return {
        "positive_rate": positive_value,
        "neutral_rate": max(0.0, 100.0 - positive_value - negative_value),
        "negative_rate": negative_value,
    }
```

Add `_valid_l6_row` requiring non-empty string `comment_id`, `comment_text`, `dimension`, and `target`. Add `_valid_l15_row` requiring a non-empty aspect label and a successful rate normalization. Extend `normalize_chart_data` and renderability for both IDs.

Change only these two `chart_data` tuples:

```python
("product-sentiment", "L15", "产品点正负反馈", "一格代表固定百分点 · 正向 / 中性 / 负向", "product_focus.aspects", aspects),
("product-pko-evidence", "L6", "用户反馈构成", "中心为产品点 · 气泡面积代表真实对比次数", "pko.evidence_comments", evidence),
```

Rename the current tuple to `LEGACY_PRODUCT_REPORT_CHART_CONTRACT`, define the new
`PRODUCT_REPORT_CHART_CONTRACT`, and register both against the existing product
prompt version:

```python
REPORT_CACHE_CONTRACTS = (
    ...,
    (
        DEFAULT_PRODUCT_REPORT_PROMPT_VERSION,
        PRODUCT_REPORT_SECTION_CODES,
        PRODUCT_REPORT_CHART_CONTRACT,
    ),
    (
        DEFAULT_PRODUCT_REPORT_PROMPT_VERSION,
        PRODUCT_REPORT_SECTION_CODES,
        LEGACY_PRODUCT_REPORT_CHART_CONTRACT,
    ),
    ...,
)
```

Change `_cached_report_contract` from `next(...)` to all contracts matching the
saved `prompt_version`; validate each candidate by its exact chart ID/template
sequence. This is required because the prompt version does not change in this
visual-only release. A complete historical F6/L12 product cache must restore
unchanged, while a new L15/L6 cache must also restore unchanged.

Give L6 the same strict evidence metadata contract already used by L12:
`displayed_count`, `total_count`, and `unit`; include `empty_reason` only when
data is empty. The existing pre-cap `evidence_total_count` remains the L6
`total_count`, while `displayed_count` equals the number of retained raw rows.

- [ ] **Step 6: Run focused backend tests and verify GREEN**

Run:

```powershell
python -m pytest tests/test_report_visuals.py tests/test_product_report_agent.py tests/test_market_report_agent.py tests/test_sales_report_agent.py tests/test_event_report_agent.py -q -p no:cacheprovider
```

Expected: all pass; event fixed sequence remains F3/L14/F6/L13.

- [ ] **Step 7: Commit Task 1**

```powershell
git add app/services/report_visuals.py app/services/report_agent.py tests/test_report_visuals.py tests/test_product_report_agent.py
git commit -m "feat: add product report l6 l15 contracts"
```

---

### Task 2: Implement L6 Cluster Field and L15 Tick Tally

**Files:**
- Create: `frontend/src/components/voc/report-visuals/SmallDataCharts.tsx`
- Modify: `frontend/src/components/voc/report-visuals/NarrativeCharts.tsx`
- Modify: `frontend/src/components/voc/report-visuals/types.ts`
- Modify: `frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: L6 raw evidence rows and L15 aspect/rate rows from Task 1.
- Produces: `L6ClusterField`, `L15BallotTally`, `mapL6Clusters`, `bubbleRadius`, `normalizeL15Rows`, and `allocateSentimentTicks`.

- [ ] **Step 1: Write failing executable TypeScript tests for L6**

Add an SSR/probe test compiling the real component module and asserting:

```typescript
const clusters = mapL6Clusters([
  { comment_id: "c1", comment_text: "a", dimension: "外观", target: "竞品B", result_bucket: "advantage" },
  { comment_id: "c2", comment_text: "b", dimension: "外观", target: "竞品A", result_bucket: "neutral" },
  { comment_id: "c3", comment_text: "c", dimension: "外观", target: "竞品B", result_bucket: "advantage" },
  { comment_id: "c4", comment_text: "d", dimension: "空间", target: "竞品A", result_bucket: "disadvantage" },
]);

assert.deepEqual(clusters.map(({ dimension, totalCount }) => ({ dimension, totalCount })), [
  { dimension: "外观", totalCount: 3 },
  { dimension: "空间", totalCount: 1 },
]);
assert.equal(clusters[0].targets[0].target, "竞品B");
assert.equal(clusters[0].targets[0].count, 2);
assert.ok(bubbleRadius(4, 4) > bubbleRadius(1, 4));
assert.ok(Math.abs((bubbleRadius(4, 4) ** 2) / (bubbleRadius(1, 4) ** 2) - 4) < 1.0);
```

Also SSR-render L6 and assert labels, counts, `role`, focusability, and hidden evidence text are present.

- [ ] **Step 2: Write failing executable TypeScript tests for L15**

Assert deterministic 20-tick allocation:

```typescript
const allocation = allocateSentimentTicks(
  { positiveRate: 62.5, neutralRate: 12.5, negativeRate: 25 },
  20,
);
assert.deepEqual(allocation, { positive: 12, neutral: 3, negative: 5 });
assert.equal(allocation.positive + allocation.neutral + allocation.negative, 20);
```

SSR-render multiple aspects and assert each row contains the exact percentages and exactly 20 visual tick elements.

- [ ] **Step 3: Run frontend tests and verify RED**

Run:

```powershell
python -m pytest tests/test_next_frontend_architecture.py -q -p no:cacheprovider -k "l6 or l15 or report_visual_registry"
```

Expected: failures because the two components, helpers, and registry entries do not exist.

- [ ] **Step 4: Implement L6 pure mapping and geometry**

In `NarrativeCharts.tsx`, define:

```typescript
export type L6Cluster = {
  dimension: string;
  totalCount: number;
  targets: Array<{
    target: string;
    count: number;
    records: PkoRecord[];
  }>;
};

export function bubbleRadius(count: number, maxCount: number): number {
  const safeMax = Math.max(1, maxCount);
  return 12 + Math.sqrt(Math.max(0, count) / safeMax) * 18;
}
```

`mapL6Clusters` must group by dimension and target, sort dimensions and targets by descending counts with locale string tie-breaks, and retain records. Render product-point centers separately from target bubbles. Use deterministic cluster centers derived from index, not random coordinates.

Add keyboard-focusable target groups:

```tsx
<g
  role="button"
  tabIndex={0}
  aria-label={`${cluster.dimension}与${target.target}对比${target.count}次`}
  onFocus={() => setActiveTarget(key)}
  onMouseEnter={() => setActiveTarget(key)}
>
```

Use a visually hidden list for all raw records so the saved evidence remains accessible.

- [ ] **Step 5: Implement L15 pure normalization and allocation**

Create `SmallDataCharts.tsx`:

```typescript
export function allocateSentimentTicks(
  rates: { positiveRate: number; neutralRate: number; negativeRate: number },
  tickCount = 20,
): { positive: number; neutral: number; negative: number } {
  const entries = [
    ["positive", rates.positiveRate],
    ["neutral", rates.neutralRate],
    ["negative", rates.negativeRate],
  ] as const;
  const exact = entries.map(([key, value]) => ({ key, exact: (value / 100) * tickCount }));
  const base = exact.map((item) => ({ ...item, count: Math.floor(item.exact) }));
  let remaining = tickCount - base.reduce((sum, item) => sum + item.count, 0);
  base
    .sort((a, b) => (b.exact - b.count) - (a.exact - a.count))
    .forEach((item) => {
      if (remaining > 0) {
        item.count += 1;
        remaining -= 1;
      }
    });
  return Object.fromEntries(base.map(({ key, count }) => [key, count])) as {
    positive: number;
    neutral: number;
    negative: number;
  };
}
```

Render one labeled row per valid aspect, three themed tick states, exact percentage text, a legend, accessible SVG labels, and the shared explicit empty state.

- [ ] **Step 6: Register the templates without removing legacy entries**

Extend `ReportTemplateId` with `"L6" | "L15"` and add:

```typescript
const REPORT_CHART_REGISTRY = {
  ...existingRegistry,
  L6: L6ClusterField,
  L15: L15BallotTally,
} satisfies Record<ReportTemplateId, ComponentType<ReportChartProps>>;
```

Keep F6 and L12 entries intact for saved historical reports.

- [ ] **Step 7: Run frontend verification**

Run:

```powershell
python -m pytest tests/test_next_frontend_architecture.py -q -p no:cacheprovider
cd frontend
npm run typecheck
```

Expected: all pass.

- [ ] **Step 8: Commit Task 2**

```powershell
git add frontend/src/components/voc/report-visuals/NarrativeCharts.tsx frontend/src/components/voc/report-visuals/SmallDataCharts.tsx frontend/src/components/voc/report-visuals/types.ts frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx tests/test_next_frontend_architecture.py
git commit -m "feat: render product report cluster and tick charts"
```

---

### Task 3: Apply the Wider Modal and Above-Chart Narrative

**Files:**
- Modify: `frontend/src/components/voc/report-visuals/ReportVisualShell.tsx`
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: registered L6/L15 report charts.
- Produces: shared visual order `title → subtitle → insight → chart → source`, wider modal, and L6 full-width placement.

- [ ] **Step 1: Write failing layout-contract tests**

Assert source order in `ReportVisualShell`:

```python
source = Path("frontend/src/components/voc/report-visuals/ReportVisualShell.tsx").read_text(encoding="utf-8")
assert source.index("{chart.subtitle}") < source.index("{chart.insight}")
assert source.index("{chart.insight}") < source.index("{children}")
assert source.index("{children}") < source.index("数据来源：{chart.source_label}")
```

Assert the modal includes `w-[94vw]`, `max-w-[1480px]`, `max-h-[92vh]`, and an inner height based on `92vh`.

Assert chart cards receive a full-width grid class only when `chart.template_id === "L6"`.

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
python -m pytest tests/test_next_frontend_architecture.py -q -p no:cacheprovider -k "report_visual_shell or report_modal or l6_full_width"
```

Expected: failures for old 5xl/88vh dimensions, below-chart insight, and no L6 span.

- [ ] **Step 3: Move insight into the chart header**

Update `ReportVisualShell`:

```tsx
<header>
  <h3>{chart.title}</h3>
  <p>{chart.subtitle}</p>
  {hasData && chart.insight ? (
    <p className="mt-3 text-sm leading-6" style={{ color: reportChartTheme.body }}>
      {chart.insight}
    </p>
  ) : null}
</header>
```

Remove the old below-chart insight paragraph. Keep the source line below the chart. Do not show an LLM insight when the chart is in its empty state.

- [ ] **Step 4: Enlarge the modal and span L6**

Change the modal surface and scroller:

```tsx
<div className="max-h-[92vh] w-[94vw] max-w-[1480px] overflow-hidden ...">
...
<div className="max-h-[calc(92vh-92px)] overflow-auto p-5 md:p-6">
```

Wrap each chart:

```tsx
<div className={chart.template_id === "L6" ? "xl:col-span-2" : undefined}>
  <ReportChartRegistry chart={chart} />
</div>
```

Keep the grid single-column below the `xl` breakpoint.

- [ ] **Step 5: Run focused frontend verification**

Run:

```powershell
python -m pytest tests/test_next_frontend_architecture.py -q -p no:cacheprovider
cd frontend
npm run typecheck
```

Expected: all pass.

- [ ] **Step 6: Commit Task 3**

```powershell
git add frontend/src/components/voc/report-visuals/ReportVisualShell.tsx frontend/src/components/voc/ReportAiSummaryCard.tsx tests/test_next_frontend_architecture.py
git commit -m "style: widen ai report chart layout"
```

---

### Task 4: Full Regression and Visual Verification

**Files:**
- Modify only files required by accepted failures.
- Modify: `docs/audits/2026-07-24-lieflat-report-visuals-verification.md`

**Interfaces:**
- Consumes: completed L6/L15 and modal implementation.
- Produces: reproducible verification evidence.

- [ ] **Step 1: Run the complete backend test suite**

```powershell
python -m pytest -q -p no:cacheprovider
```

Expected: zero failures.

- [ ] **Step 2: Run frontend type and production checks**

```powershell
cd frontend
npm run typecheck
npm run build
```

Expected: both exit 0 and all Next.js pages build.

- [ ] **Step 3: Run source safety checks**

```powershell
rg -n "echarts|chart\\.js|cdn\\.jsdelivr|dangerouslySetInnerHTML|eval\\(|Math\\.random" frontend/src/components/voc/report-visuals
git diff --check
```

Expected: no unsafe runtime or random-layout matches; diff check exits 0.

- [ ] **Step 4: Verify real product report behavior**

Start the existing real backend and frontend from this worktree. Open a real product report containing PKO evidence and verify:

- modal width at 1280px and 1440px;
- title, subtitle, and AI insight above each SVG;
- multiple product-point clusters;
- target bubble size ordering matches comparison counts;
- L15 row percentages and tick allocation;
- keyboard focus on L6 target bubbles;
- empty L6/L15 fixtures show explicit empty states with no demo data.

If Windows prevents controlled browser launch, record the exact process error and use executable SSR plus production build evidence without claiming visual acceptance.

- [ ] **Step 5: Update the verification record**

Append commands, exit codes, test counts, actual route/event if available, screenshot status, and confirmation that no external chart runtime is loaded to:

`docs/audits/2026-07-24-lieflat-report-visuals-verification.md`

- [ ] **Step 6: Request independent code review**

Review from the commit before Task 1 through the Task 4 verification commit. Require:

- Spec PASS;
- Quality APPROVED;
- no Critical or Important findings.

For every accepted finding, add a failing regression test, verify RED, apply the smallest fix, and rerun focused plus full verification.

- [ ] **Step 7: Commit verification evidence**

```powershell
git add docs/audits/2026-07-24-lieflat-report-visuals-verification.md
git commit -m "test: verify product report chart polish"
```

---

## Plan Self-Review

- Spec coverage: modal size, information order, L6 multi-cluster semantics, square-root area encoding, L15 three-part 100% ticks, empty states, legacy compatibility, accessibility, LLM boundary, safety scan, and visual verification are each assigned to a task.
- Placeholder scan: no TBD, TODO, deferred implementation, or unspecified test step remains.
- Type consistency: backend and frontend add the same `L6` and `L15` IDs; L6 consumes existing evidence rows and L15 consumes existing aspect rows; legacy F6/L12 remain registered.
- Scope: no market, sales, event, prompt, database, or unrelated dashboard redesign is included.
