# Competitor Report Topic Network Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the competitor report topic bar chart with a Lieflat Big Force topic-account network and remove duplicated topic/dealer sections.

**Architecture:** Add one deterministic Python aggregation helper in the existing report generator to produce bounded topic nodes, account nodes, and edges from the report-period work rows. Render that payload with the existing locally embedded ECharts runtime, adapting `lieflat-chart/templates/big-force.html`; keep LLM output and report storage unchanged.

**Tech Stack:** Python, pandas, generated self-contained HTML, Apache ECharts 5.6.0, pytest.

## Global Constraints

- Topic and account node sizes use cumulative interaction count.
- Edge width uses work count only.
- Include at most 5 topics and 20 accounts.
- Use original topic tags only; do not invent missing relationships.
- Account colors distinguish official, dealer, and other accounts.
- Keep all report assets offline and self-contained; no CDN.
- Historical stored HTML reports are not migrated.
- Do not add LLM responsibility for calculation, filtering, chart selection, or layout.

---

### Task 1: Deterministic topic-account network payload

**Files:**
- Modify: `app/agents/competitor_report/skill_generator.py`
- Test: `tests/test_competitor_report_renderer.py`

**Interfaces:**
- Consumes: prepared work DataFrame columns `作者`, `是否官方号`, `话题标签`, `总互动量`, and `标题`.
- Produces: `build_topic_account_network(brand_df) -> dict` with `topics`, `accounts`, `links`, and `message`.

- [ ] **Step 1: Write failing aggregation tests**

Add tests that call `build_topic_account_network` with real pandas rows and assert:

```python
assert len(result["topics"]) <= 5
assert len(result["accounts"]) <= 20
assert result["topics"][0]["interaction_count"] == 180
assert result["accounts"][0]["account_type"] == "official"
assert result["links"][0]["work_count"] == 2
assert result["links"][0]["interaction_count"] == 180
```

Add an empty-tag test:

```python
assert result["topics"] == []
assert result["accounts"] == []
assert result["links"] == []
assert "暂无" in result["message"]
```

- [ ] **Step 2: Run tests and verify RED**

Run:

```powershell
$env:PYTHONPATH='.'
pytest -q -p no:cacheprovider tests/test_competitor_report_renderer.py -k "topic_account_network"
```

Expected: failure because `build_topic_account_network` does not exist.

- [ ] **Step 3: Implement the minimal aggregation helper**

Implement one function that:

1. Extracts original tags with `extract_tags`.
2. Aggregates `(topic, account)` work count and cumulative interaction count.
3. Selects Top5 topics by cumulative interaction count.
4. Selects Top20 connected accounts by cumulative interaction count.
5. Classifies accounts as `official`, `dealer`, or `other` from existing fields.
6. Returns only nodes and links that survive both filters.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

### Task 2: Big Force rendering and report consolidation

**Files:**
- Modify: `app/agents/competitor_report/skill_generator.py`
- Test: `tests/test_competitor_report_renderer.py`
- Test: `tests/test_task_api.py`

**Interfaces:**
- Consumes: `build_topic_account_network(brand_df)` result serialized into `reportData.topic_network`.
- Produces: ECharts graph mounted at `#topicChart`.

- [ ] **Step 1: Write failing renderer contract tests**

Assert the generated HTML contains:

```python
assert "renderTopicForceGraph" in rendered
assert "FORCE GRAPH · TOPIC ACCOUNT NETWORK" in rendered
assert "type: 'graph'" in rendered
assert "layout: 'force'" in rendered
assert "话题分类分布" not in rendered
assert "重点经销商承接效果</h2>" not in rendered
assert "最强承接账号" in rendered
assert "覆盖话题最多账号" in rendered
assert "低效承接账号" in rendered
assert "cdn.jsdelivr.net" not in rendered
```

Update the API integration contract to require `renderTopicForceGraph` rather than the old topic bar option.

- [ ] **Step 2: Run renderer/API tests and verify RED**

Run:

```powershell
$env:PYTHONPATH='.'
pytest -q -p no:cacheprovider tests/test_competitor_report_renderer.py tests/test_task_api.py -k "competitor_report"
```

Expected: failures because the Big Force renderer and consolidated sections are absent.

- [ ] **Step 3: Implement the fixed Big Force template**

Replace the topic bar option with an ECharts graph adapted from `lieflat-chart/templates/big-force.html`:

- Force layout with roam and draggable nodes.
- Topic nodes use the report brand color and show labels.
- Account nodes use official/dealer/other colors.
- Node sizes use square-root scaling of cumulative interactions.
- Edge widths use work count.
- Hover uses adjacency emphasis and blur.
- Tooltip uses text fields from deterministic payload.
- Empty canvas click restores the option.
- Empty data renders a visible message.

Restructure the topic section to a 36/64 evidence-list/network layout. Remove the topic-category table. Move exactly three deterministic dealer summaries into the Big Threads panel.

- [ ] **Step 4: Run focused tests and verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

### Task 3: Regression, build, and visual verification

**Files:**
- Modify only if a regression is discovered in files already listed above.

**Interfaces:**
- Consumes: complete report generator and frontend asset viewer.
- Produces: verified self-contained competitor report HTML.

- [ ] **Step 1: Run all backend tests**

```powershell
$env:PYTHONPATH='.'
pytest -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 2: Run frontend verification**

```powershell
cd frontend
npm run typecheck
npm run build
```

Expected: TypeScript passes and Next.js production build completes.

- [ ] **Step 3: Generate and inspect a fresh report**

With backend and frontend running, generate a new competitor report and verify:

- No console errors inside the sandboxed report iframe.
- Topic graph has at most 5 topic nodes and 20 account nodes.
- Node hover focuses adjacent nodes and edges.
- Drag, pan, zoom, and empty-area reset work.
- Long labels remain readable through tooltip.
- Big Threads shows exactly three dealer summaries.
- Empty-tag sample shows a clear empty state.

- [ ] **Step 4: Commit implementation**

```powershell
git add app/agents/competitor_report/skill_generator.py tests/test_competitor_report_renderer.py tests/test_task_api.py
git commit -m "feat: add competitor topic propagation network"
```
