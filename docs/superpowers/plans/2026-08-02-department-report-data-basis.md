# Department Report Data Basis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the three department reports' developer-oriented evidence tab with fixed, business-readable data source and metric logic cards.

**Architecture:** Keep all explanatory copy in one frontend-only department registry and render it through one shared view component. `ReportAiSummaryCard` identifies the department using its existing `departmentName`, supplies the fixed configuration to `DepartmentReportView`, and keeps Prompt/JSON only in a collapsed technical-details block.

**Tech Stack:** Next.js 14, React, TypeScript, Tailwind CSS, pytest source-contract tests, TypeScript compiler.

## Global Constraints

- Do not add or modify backend report fields, database tables, APIs, prompts, or report caches.
- Do not let the LLM generate data-basis copy.
- Use only the current event name and report generation time as dynamic presentation metadata; fixed explanatory copy must not infer missing values.
- Preserve summary mode, chart mode, chart contracts, legacy Markdown reports, and existing report generation behavior.
- Keep Prompt and structured input available only in collapsed technical details.

---

### Task 1: Fixed department data-basis registry

**Files:**
- Create: `frontend/src/components/voc/report-data-basis/reportDataBasis.ts`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Produces: `DepartmentDataBasisKey`, `DataBasisProcessType`, `DataBasisSection`, `resolveDepartmentDataBasis(departmentName: string): DataBasisSection[]`.
- Consumes: no report payload and no backend types.

- [ ] **Step 1: Write the failing registry contract test**

Add a test that reads the registry source and asserts all three departments, twelve chapter IDs, four process types, and the absence of Prompt/JSON copy:

```python
def test_department_data_basis_registry_covers_three_storylines() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    source = (root / "frontend/src/components/voc/report-data-basis/reportDataBasis.ts").read_text(encoding="utf-8")
    for department in ("市场部", "产品部", "销售部"):
        assert f'"{department}"' in source
    for chapter_id in (
        "rhythm", "topics", "subjects", "channels",
        "focus", "attitude", "comparison", "evidence",
        "output", "needs", "sources", "follow_up",
    ):
        assert f'chapterId: "{chapter_id}"' in source
    for process_type in ("direct", "rule", "llm_label", "llm_summary"):
        assert f'"{process_type}"' in source
    assert "完整 Prompt" not in source
    assert "结构化 JSON" not in source
```

- [ ] **Step 2: Run the test and verify RED**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py::test_department_data_basis_registry_covers_three_storylines -q`

Expected: FAIL because `reportDataBasis.ts` does not exist.

- [ ] **Step 3: Implement the fixed registry**

Create the types and an immutable record:

```ts
export type DataBasisProcessType = "direct" | "rule" | "llm_label" | "llm_summary";

export type DataBasisSection = {
  chapterId: string;
  title: string;
  dataItems: string[];
  sources: string[];
  processingSteps: Array<{ type: DataBasisProcessType; description: string }>;
  metricDefinitions: string[];
  supports: string;
  availabilityNote: string;
};

export function resolveDepartmentDataBasis(departmentName: string): DataBasisSection[] {
  return DEPARTMENT_DATA_BASIS[departmentName] ?? [];
}
```

Define `DEPARTMENT_DATA_BASIS` as `Record<string, DataBasisSection[]>` with these exact ordered chapter/title pairs:

- 市场部：`rhythm / 传播结果与节奏`、`topics / 话题驱动`、`subjects / 传播主体`、`channels / 渠道效率`。
- 产品部：`focus / 用户关注`、`attitude / 评价态度`、`comparison / 竞品比较`、`evidence / 证据支撑`。
- 销售部：`output / 线索产出`、`needs / 用户需求`、`sources / 线索来源`、`follow_up / 承接对象`。

For each object, use the complete “使用数据、数据来源、处理方式、支撑内容” sentences from `docs/superpowers/specs/2026-08-02-department-report-data-basis-design.md`. Split each processing sentence into its stated `direct`, `rule`, `llm_label`, or `llm_summary` steps. Add the fixed availability note “本章节说明系统标准口径；本次没有相应数据时，报告不会补造结论。” and express each stated calculation rule as `metricDefinitions`. Do not introduce backend field paths or table names.

- [ ] **Step 4: Run the registry test and TypeScript check**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py::test_department_data_basis_registry_covers_three_storylines -q`

Expected: PASS.

Run: `npm run typecheck` from `frontend`.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/voc/report-data-basis/reportDataBasis.ts tests/test_next_frontend_architecture.py
git commit -m "feat: define department report data basis"
```

### Task 2: Shared business data-basis view

**Files:**
- Create: `frontend/src/components/voc/report-data-basis/ReportDataBasisView.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: `departmentName: string`, `eventName?: string`, `generatedAt?: string`, and `resolveDepartmentDataBasis` from Task 1.
- Produces: `ReportDataBasisView`, a presentational component with scope summary and four fixed chapter cards.

- [ ] **Step 1: Write the failing renderer contract test**

```python
def test_report_data_basis_view_uses_business_sections_and_process_labels() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    source = (root / "frontend/src/components/voc/report-data-basis/ReportDataBasisView.tsx").read_text(encoding="utf-8")
    assert "resolveDepartmentDataBasis" in source
    for label in ("使用数据", "数据来源", "处理过程", "指标口径", "支撑内容", "数据完整性"):
        assert label in source
    for label in ("直接统计", "规则计算", "LLM 标签", "LLM 总结"):
        assert label in source
    assert 'eventName || "未记录"' in source
    assert 'generatedAt || "未记录"' in source
```

- [ ] **Step 2: Run the renderer test and verify RED**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py::test_report_data_basis_view_uses_business_sections_and_process_labels -q`

Expected: FAIL because the component does not exist.

- [ ] **Step 3: Implement the shared view**

Implement one scope header and a responsive two-column card grid. Use a single theme color plus neutral surfaces. Map process types through this fixed label record:

```ts
const PROCESS_LABELS = {
  direct: "直接统计",
  rule: "规则计算",
  llm_label: "LLM 标签",
  llm_summary: "LLM 总结",
} as const;
```

Render all six business fields per section and show `eventName || "未记录"` and `generatedAt || "未记录"` in the scope header. If a department is unknown, render the existing neutral empty-state style with “当前报告未配置业务数据依据”。

- [ ] **Step 4: Run renderer test and TypeScript check**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py::test_report_data_basis_view_uses_business_sections_and_process_labels -q`

Expected: PASS.

Run: `npm run typecheck` from `frontend`.

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/voc/report-data-basis/ReportDataBasisView.tsx tests/test_next_frontend_architecture.py
git commit -m "feat: render business report data basis"
```

### Task 3: Integrate all three reports and preserve technical details

**Files:**
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: `ReportDataBasisView` from Task 2 and the existing `departmentName`, `eventName`, and `payload.generated_at` values.
- Produces: three-mode report UI where evidence mode always shows the business data-basis view for structured department reports.

- [ ] **Step 1: Write the failing integration test**

```python
def test_department_report_evidence_mode_uses_fixed_data_basis_and_collapses_technical_details() -> None:
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    source = (root / "frontend/src/components/voc/ReportAiSummaryCard.tsx").read_text(encoding="utf-8")
    assert 'import { ReportDataBasisView } from "@/components/voc/report-data-basis/ReportDataBasisView"' in source
    assert "departmentName={departmentName}" in source
    assert "generatedAt={payload?.generated_at}" in source
    assert "<ReportDataBasisView" in source
    assert 'title="技术详情"' in source
    assert "当前报告没有额外的数据说明、证据引用或计算备注。" not in source
```

- [ ] **Step 2: Run the integration test and verify RED**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py::test_department_report_evidence_mode_uses_fixed_data_basis_and_collapses_technical_details -q`

Expected: FAIL because the existing evidence view still renders optional narrative evidence and separate Prompt/JSON blocks.

- [ ] **Step 3: Integrate the new view**

Extend `DepartmentReportView` props with `departmentName` and `generatedAt`. Replace the existing `hasEvidence` conditional evidence block with:

```tsx
{reportViewMode === "evidence" ? (
  <ReportDataBasisView
    departmentName={departmentName}
    eventName={eventName}
    generatedAt={generatedAt}
  />
) : null}
```

Pass `departmentName={departmentName}` and `generatedAt={payload?.generated_at}` at the existing call site. Change the evidence-mode subtitle to “查看本报告使用的数据、来源、处理方式与指标口径。”

Replace the two sibling Prompt/JSON details blocks with one outer `DetailsBlock title="技术详情"`; inside it, keep two clearly titled subsections containing the existing `rendered_prompt` and `context` values. Do not expose these blocks inside `ReportDataBasisView`.

Remove imports or local variables made dead by deleting the old evidence renderer.

- [ ] **Step 4: Run targeted and full verification**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py -q`

Expected: PASS.

Run: `npm run typecheck` from `frontend`.

Expected: PASS.

Run: `npm run build` from `frontend`.

Expected: Next.js production build succeeds.

Run: `$env:PYTHONPATH='.'; pytest -q`

Expected: all tests pass.

Run: `git diff --check`

Expected: exit code 0.

- [ ] **Step 5: Verify the three real pages**

For `/voc/events/market`, `/voc/events/product`, and `/voc/events/sales`:

1. Open AI 总结.
2. Select 数据依据.
3. Confirm four department-specific cards appear in storyline order.
4. Confirm all six business fields are present.
5. Confirm Prompt and JSON appear only after expanding 技术详情.
6. Confirm 摘要模式 and 图表模式 are unchanged.

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/voc/ReportAiSummaryCard.tsx frontend/src/components/voc/report-data-basis/ReportDataBasisView.tsx frontend/src/components/voc/report-data-basis/reportDataBasis.ts tests/test_next_frontend_architecture.py
git commit -m "feat: upgrade department report data basis"
```
