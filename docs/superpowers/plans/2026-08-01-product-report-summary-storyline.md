# Product Report Summary Storyline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the product report's duplicated insight-card summary with a validated four-chapter business storyline while preserving chart insights, real data references, and historical report compatibility.

**Architecture:** Extend only the product report narrative with a normalized `storyline` contract. The backend validates fixed chapter IDs and filters metric/evidence references against allowlists derived from the existing product context; a reusable frontend storyline component resolves display values from structured chart data and renders the shared single-theme visual system. Market and sales reports keep their current content and can adopt the shared component after separate storyline designs.

**Tech Stack:** Python 3, FastAPI service layer, pytest, TypeScript, React 18, Next.js 14, Tailwind CSS, native system CSS variables.

## Global Constraints

- This implementation changes only the product report summary; market and sales behavior must remain unchanged.
- The summary tells a two-minute business story and must not repeat the five chart insights in order.
- The Agent may organize text but may not calculate display numbers or invent metric paths, targets, or comments.
- The four product chapter IDs are exactly `focus`, `attitude`, `comparison`, and `evidence`, in that order.
- Product recommendations are forbidden; opportunity, surprise, and risk are factual labels only.
- All displayed metrics and evidence must resolve from the existing structured report data.
- Historical reports without `storyline` must continue rendering the legacy summary.
- Styling must follow `docs/superpowers/specs/report-summary-visual-system.md`: one theme hue, white content surfaces, system tokens, no per-chapter color palette.
- Do not add a chart library or new backend metric.

---

### Task 1: Add and validate the product storyline backend contract

**Files:**
- Modify: `app/services/report_agent.py`
- Test: `tests/test_product_report_agent.py`

**Interfaces:**
- Produces: `normalize_product_storyline(value: Any, context: dict[str, Any]) -> dict[str, Any] | None`
- Produces: `PRODUCT_STORY_CHAPTER_IDS = ("focus", "attitude", "comparison", "evidence")`
- Consumes: existing product context keys `product_focus`, `product_opportunity`, and `pko`

- [ ] **Step 1: Write failing normalization tests**

Add tests proving that chapter order is fixed, text is bounded, unknown metric paths are removed, missing comment IDs are removed, and an incomplete chapter set returns `None`:

```python
def test_product_storyline_keeps_only_fixed_real_references() -> None:
    from app.services.report_agent import normalize_product_storyline

    context = build_product_report_context(sample_product_dashboard())
    raw = {
        "headline": "用户讨论由外观吸引，价格比较形成主要分歧",
        "lead": "讨论先集中到外观，随后进入价格与竞品比较。",
        "chapters": [
            {"chapter_id": "focus", "title": "用户在关注什么", "conclusion": "外观最受关注", "body": "讨论集中在外观。", "metric_refs": ["product_focus.aspects", "unknown.path"], "evidence_refs": []},
            {"chapter_id": "attitude", "title": "用户如何评价", "conclusion": "外观正向", "body": "价格负向更集中。", "metric_refs": ["product_opportunity.summary"], "evidence_refs": []},
            {"chapter_id": "comparison", "title": "用户在和谁比较", "conclusion": "主要比较 ID.4", "body": "价格是主要维度。", "metric_refs": ["pko.summary"], "evidence_refs": ["pko_001", "missing"]},
            {"chapter_id": "evidence", "title": "证据如何支撑", "conclusion": "原话支持上述判断", "body": "证据来自真实评论。", "metric_refs": [], "evidence_refs": ["pko_001"]},
        ],
    }

    storyline = normalize_product_storyline(raw, context)
    assert [item["chapter_id"] for item in storyline["chapters"]] == ["focus", "attitude", "comparison", "evidence"]
    assert storyline["chapters"][0]["metric_refs"] == ["product_focus.aspects"]
    assert storyline["chapters"][2]["evidence_refs"] == ["pko_001"]
```

- [ ] **Step 2: Run tests and verify RED**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_product_report_agent.py -k storyline`

Expected: FAIL because `normalize_product_storyline` does not exist.

- [ ] **Step 3: Implement minimal strict normalization**

Add fixed bounds and allowlists without a generic path interpreter:

```python
PRODUCT_STORY_CHAPTER_IDS = ("focus", "attitude", "comparison", "evidence")
PRODUCT_STORY_METRIC_REFS = {
    "product_focus.summary",
    "product_focus.aspects",
    "product_opportunity.summary",
    "product_opportunity.surprise_points",
    "product_opportunity.pain_points",
    "product_opportunity.conversion_points",
    "pko.summary",
    "pko.dimension_result_matrix",
}

def normalize_product_storyline(value: Any, context: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(value, dict) or not isinstance(value.get("chapters"), list):
        return None
    raw_chapters = {item.get("chapter_id"): item for item in value["chapters"] if isinstance(item, dict)}
    evidence_ids = {
        str(item.get("comment_id"))
        for item in (context.get("pko") or {}).get("evidence_comments", [])
        if isinstance(item, dict) and item.get("comment_id")
    }
    chapters = []
    for chapter_id in PRODUCT_STORY_CHAPTER_IDS:
        item = raw_chapters.get(chapter_id)
        if not isinstance(item, dict):
            return None
        chapters.append({
            "chapter_id": chapter_id,
            "title": _bounded_text(item.get("title"), 60),
            "conclusion": _bounded_text(item.get("conclusion"), 240),
            "body": _bounded_text(item.get("body"), 900),
            "metric_refs": [ref for ref in item.get("metric_refs", []) if ref in PRODUCT_STORY_METRIC_REFS][:4],
            "evidence_refs": [ref for ref in item.get("evidence_refs", []) if ref in evidence_ids][:2],
        })
    if any(not item["title"] or not item["conclusion"] for item in chapters):
        return None
    return {"headline": _bounded_text(value.get("headline"), 160), "lead": _bounded_text(value.get("lead"), 600), "chapters": chapters}
```

- [ ] **Step 4: Run backend storyline tests and verify GREEN**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_product_report_agent.py -k storyline`

Expected: PASS.

- [ ] **Step 5: Commit the contract**

```powershell
git add app/services/report_agent.py tests/test_product_report_agent.py
git commit -m "feat: validate product report storyline"
```

### Task 2: Generate storyline content without breaking chart insights or cached reports

**Files:**
- Modify: `app/services/system_settings.py`
- Modify: `app/services/report_agent.py`
- Test: `tests/test_product_report_agent.py`
- Test: `tests/test_report_prompt_api.py`

**Interfaces:**
- Consumes: `normalize_product_storyline(...)` from Task 1
- Produces: product `report_narrative.storyline` only when the validated contract is complete
- Preserves: existing `section_insights` as chart-mode copy

- [ ] **Step 1: Write failing generation and compatibility tests**

Add tests asserting:

```python
assert "storyline" in result["summary"]["report_narrative"]
assert result["summary"]["report_narrative"]["section_insights"]["product_focus"] == "关注判断"
assert normalize_cached_report_summary(old_v2_payload, "product_report_summary_v2")["structured_report"]
assert "storyline" in resolve_product_report_prompt_for_test()[0]
```

Also assert that market and sales default prompts do not require `storyline`.

- [ ] **Step 2: Run focused tests and verify RED**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_product_report_agent.py tests/test_report_prompt_api.py -k "storyline or product_prompt"`

Expected: FAIL because the prompt and report summary omit `storyline`.

- [ ] **Step 3: Extend only the product prompt contract**

Bump `PRODUCT_REPORT_PROMPT_VERSION` to `product_report_summary_v3` and include the exact fixed JSON shape:

```json
"storyline": {
  "headline": "",
  "lead": "",
  "chapters": [
    {"chapter_id": "focus", "title": "用户在关注什么", "conclusion": "", "body": "", "metric_refs": [], "evidence_refs": []},
    {"chapter_id": "attitude", "title": "用户如何评价", "conclusion": "", "body": "", "metric_refs": [], "evidence_refs": []},
    {"chapter_id": "comparison", "title": "用户在和谁比较", "conclusion": "", "body": "", "metric_refs": [], "evidence_refs": []},
    {"chapter_id": "evidence", "title": "证据如何支撑", "conclusion": "", "body": "", "metric_refs": [], "evidence_refs": []}
  ]
}
```

The prompt must explicitly state: do not repeat `section_insights`, do not write recommendations, and reference only supplied metric paths/comment IDs.

- [ ] **Step 4: Attach normalized storyline to the product summary**

Keep `normalize_report_narrative` shared and add the product-only attachment in the product report path:

```python
summary = build_report_summary(...)
storyline = normalize_product_storyline(payload.get("storyline"), context)
if storyline:
    summary["report_narrative"]["storyline"] = storyline
```

Register both v2 and v3 product cache contracts so old stored reports remain readable. Do not synthesize a storyline for old reports.

- [ ] **Step 5: Run product, prompt, market, and sales tests**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_product_report_agent.py tests/test_report_prompt_api.py tests/test_market_report_agent.py tests/test_sales_report_agent.py`

Expected: PASS.

- [ ] **Step 6: Commit Agent changes**

```powershell
git add app/services/system_settings.py app/services/report_agent.py tests/test_product_report_agent.py tests/test_report_prompt_api.py
git commit -m "feat: generate product report storyline"
```

### Task 3: Add typed frontend storyline parsing and real-data resolvers

**Files:**
- Modify: `frontend/src/types/vocMarket.ts`
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Create: `frontend/src/components/voc/report-summary/productStorylineData.ts`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Produces: `ReportStoryline`, `ReportStoryChapter`, and optional `ReportNarrative.storyline`
- Produces: `buildProductStorylineView(storyline, charts)` returning validated metric chips and evidence records
- Consumes: P1–P4/L6 structured report charts already built by the backend

- [ ] **Step 1: Write failing parser and resolver tests**

Use the existing Node/TypeScript SSR probe pattern to assert:

```ts
const view = buildProductStorylineView(storyline, charts);
assert.deepEqual(view.chapters.map((item) => item.chapterId), ["focus", "attitude", "comparison", "evidence"]);
assert.equal(view.chapters[0].metrics[0].value, "40%");
assert.equal(view.chapters[2].evidence[0].commentId, "pko_001");
assert.equal(buildProductStorylineView(invalidStoryline, charts), null);
```

- [ ] **Step 2: Run the frontend architecture test and verify RED**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_next_frontend_architecture.py -k product_storyline`

Expected: FAIL because the types and resolver module do not exist.

- [ ] **Step 3: Add explicit types and a small resolver**

Define:

```ts
export type ReportStoryChapter = {
  chapter_id: "focus" | "attitude" | "comparison" | "evidence";
  title: string;
  conclusion: string;
  body: string;
  metric_refs: string[];
  evidence_refs: string[];
};

export type ReportStoryline = {
  headline: string;
  lead: string;
  chapters: ReportStoryChapter[];
};
```

Implement direct reference mappings in `productStorylineData.ts`; do not implement arbitrary dot-path execution. Resolve only the allowlisted refs and derive metric chips from the already normalized P1–P4 rows. Resolve evidence only from the L6 chart by `comment_id`.

- [ ] **Step 4: Accept storyline without making it mandatory**

Update `isReportNarrative` so valid storylines are retained, invalid storylines are ignored, and the base narrative contract still accepts historical reports without the field.

- [ ] **Step 5: Run focused tests and typecheck**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_next_frontend_architecture.py -k "product_storyline or report_card"`

Run: `npm run typecheck` from `frontend/`

Expected: PASS for both.

- [ ] **Step 6: Commit typed data flow**

```powershell
git add frontend/src/types/vocMarket.ts frontend/src/components/voc/ReportAiSummaryCard.tsx frontend/src/components/voc/report-summary/productStorylineData.ts tests/test_next_frontend_architecture.py
git commit -m "feat: resolve product storyline data"
```

### Task 4: Render the reusable single-theme storyline summary

**Files:**
- Create: `frontend/src/components/voc/report-summary/ReportSummaryStoryline.tsx`
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: view model from `buildProductStorylineView(...)`
- Produces: `ReportSummaryStoryline` shared visual component with no department-specific data access
- Falls back: existing insight cards when no valid storyline view exists

- [ ] **Step 1: Write failing SSR and source-boundary tests**

Assert the rendered output contains one conclusion hero and four ordered chapters, uses only system theme tokens, and omits chart template IDs:

```python
assert 'data-report-storyline-hero' in markup
assert markup.index('data-story-chapter="focus"') < markup.index('data-story-chapter="evidence"')
assert "P1" not in markup and "P2" not in markup
assert "var(--theme-primary)" in source
assert "rgba(" not in source
assert "bg-rose-" not in source and "bg-emerald-" not in source
```

Also render a legacy product narrative without `storyline` and assert the old summary insight cards remain present.

- [ ] **Step 2: Run SSR tests and verify RED**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_next_frontend_architecture.py -k "storyline_summary or legacy_product_summary"`

Expected: FAIL because `ReportSummaryStoryline.tsx` does not exist.

- [ ] **Step 3: Implement the shared visual component**

Build the component with:

- a single hero using `from-[var(--theme-selected-bg)] to-[var(--theme-white)]`;
- one theme-color glow using CSS system variables only;
- metric chips using `theme-selected-bg`, `theme-primary`, and `theme-ink`;
- a vertical line and `01`–`04` markers using `theme-primary` opacity;
- white chapter surfaces with `theme-border`;
- evidence cards using `theme-soft-panel`;
- responsive `lg:grid-cols-[minmax(0,1fr)_280px]`, collapsing to one column below `lg`.

The component accepts prepared text/metrics/evidence only; it must not inspect report charts or product fields.

- [ ] **Step 4: Wire product storyline with legacy fallback**

In summary mode:

```tsx
const storylineView = reportNarrative.storyline
  ? buildProductStorylineView(reportNarrative.storyline, structuredReport.charts)
  : null;

return storylineView
  ? <ReportSummaryStoryline storyline={storylineView} />
  : <LegacyDepartmentSummary reportNarrative={reportNarrative} charts={structuredReport.charts} />;
```

Apply this only when the structured charts match the P1/P2/P3/L6/P4 product contract. Market and sales continue through the legacy branch.

- [ ] **Step 5: Run SSR tests, typecheck, and production build**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider tests/test_next_frontend_architecture.py -k "storyline or report_card"`

Run: `npm run typecheck` from `frontend/`

Run: `npm run build` from `frontend/`

Expected: all commands PASS.

- [ ] **Step 6: Commit the visual summary**

```powershell
git add frontend/src/components/voc/report-summary/ReportSummaryStoryline.tsx frontend/src/components/voc/ReportAiSummaryCard.tsx tests/test_next_frontend_architecture.py
git commit -m "feat: render product report storyline summary"
```

### Task 5: Run full regression and record verification

**Files:**
- Create: `docs/audits/2026-08-01-product-report-summary-storyline-verification.md`

**Interfaces:**
- Consumes: completed backend and frontend implementation
- Produces: reproducible verification record

- [ ] **Step 1: Run the complete backend/frontend test suite**

Run: `$env:PYTHONPATH='.'; pytest -q -p no:cacheprovider`

Run: `npm run typecheck` from `frontend/`

Run: `npm run build` from `frontend/`

Expected: all tests pass, typecheck exits 0, and Next.js reports `Compiled successfully`.

- [ ] **Step 2: Verify repository boundaries**

Run: `git diff --check`

Run: `git status --short`

Expected: no whitespace errors; unrelated untracked Excel, skill, sample, and audit files remain unstaged.

- [ ] **Step 3: Record exact evidence**

Create the verification document with the branch name, commit IDs, exact commands, pass counts, build result, and explicit statements that market/sales behavior and historical product fallback were tested.

- [ ] **Step 4: Commit verification**

```powershell
git add docs/audits/2026-08-01-product-report-summary-storyline-verification.md
git commit -m "docs: verify product report storyline"
```
