# Competitor Report Skill Parity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the simplified competitor-report renderer with a project-local, importable version of the final `weekly-voc-report` McKinsey generator and correctly resolve “某月最后一周”.

**Architecture:** A deterministic scope resolver selects the exact database window. PostgreSQL rows are mapped to the final skill’s canonical Chinese-column record schema, then a single importable generator produces the complete McKinsey HTML for both records and Excel inputs. ECharts is embedded from a project-owned Apache-2.0 vendor asset so stored reports remain self-contained.

**Tech Stack:** Python 3.11, pandas, psycopg 3, LangGraph, FastAPI, HTML/CSS/JavaScript, Apache ECharts 5, pytest.

## Global Constraints

- The visual and structural source of truth is `E:\openclaw实战bak\新skill\scripts\generate_brand_reports.py --style mckinsey`.
- Runtime code must not depend on the `E:\` absolute path.
- Database records and Excel input must call the same `build_html` implementation.
- LLM output may supply prose only; dates, filters, rankings, metrics, chart data, topic classification and HTML are deterministic.
- Total engagement equals likes + comments + favorites + shares.
- Missing video insight content renders `无`; it must never be invented.
- “2026年5月最后一周” resolves to `2026-05-25` through `2026-05-31`.
- Existing event reports, department reports and report assets must remain compatible.
- Public CDN availability must not determine whether report charts render.

---

### Task 1: Deterministic Last-Week-of-Month Scope

**Files:**
- Modify: `app/agents/qa/time_scope_resolver.py`
- Modify: `app/agents/competitor_report/scope.py`
- Test: `tests/test_qa_agent.py`
- Test: `tests/test_competitor_report_agent.py`

**Interfaces:**
- Consumes: `resolve_time_scope(question: str, asked_at: datetime | None, event: dict | None)`.
- Produces: a `mode="named_month_last_week"` scope with ISO `start_date`, `end_date`, label and `anchor_date`.

- [ ] **Step 1: Add failing resolver tests**

```python
def test_resolve_time_scope_supports_named_month_last_week():
    asked_at = datetime(2026, 7, 28, 12, tzinfo=SHANGHAI_TZ)
    assert resolve_time_scope("生成2026年5月最后一周的竞品动态报告", asked_at=asked_at) == {
        "mode": "named_month_last_week",
        "start_date": "2026-05-25",
        "end_date": "2026-05-31",
        "label": "2026-05-25 至 2026-05-31（用户指定2026年5月最后一周）",
        "source": "user_month_last_week_phrase",
        "anchor_date": "2026-07-28",
    }
    assert resolve_time_scope("生成5月最后一周的竞品动态报告", asked_at=asked_at)["start_date"] == "2026-05-25"
    assert resolve_time_scope("生成5月报告", asked_at=asked_at)["start_date"] == "2026-05-01"
```

- [ ] **Step 2: Verify RED**

Run:

```powershell
python -m pytest tests/test_qa_agent.py -q -p no:cacheprovider
```

Expected: the last-week assertions fail because the resolver returns the full named month.

- [ ] **Step 3: Implement the specific parser before named-month parsing**

Add a pattern accepting Arabic years/months and `最后一周|最后一星期`. Compute the month’s final day, move backward to Monday, and clip the range to that month. Invoke this parser before `_named_month_scope`.

- [ ] **Step 4: Add competitor scope validation coverage**

```python
def test_competitor_scope_keeps_supported_last_week_candidate():
    scope = extract_competitor_report_scope(
        "生成5月最后一周的竞品动态报告",
        history=[],
        known_brands=["上汽大众"],
        llm_json=lambda _: {
            "brand_name": None,
            "start_date": "2026-05-25",
            "end_date": "2026-05-31",
        },
        today=date(2026, 7, 28),
    )
    assert (scope["start_date"], scope["end_date"], scope["time_defaulted"]) == (
        "2026-05-25", "2026-05-31", False
    )
```

- [ ] **Step 5: Verify GREEN and commit**

Run:

```powershell
python -m pytest tests/test_qa_agent.py tests/test_competitor_report_agent.py -q -p no:cacheprovider
git add app/agents/qa/time_scope_resolver.py app/agents/competitor_report/scope.py tests/test_qa_agent.py tests/test_competitor_report_agent.py
git commit -m "fix: resolve monthly final week scopes"
```

Expected: all selected tests pass.

---

### Task 2: Project-Local Final Skill Generator

**Files:**
- Create: `app/agents/competitor_report/skill_generator.py`
- Create: `app/agents/competitor_report/assets/echarts.min.js`
- Create: `docs/licenses/apache-echarts-5.md`
- Delete: `app/agents/competitor_report/templates/long_report.html`
- Modify: `app/agents/competitor_report/renderer.py`
- Test: `tests/test_competitor_report_renderer.py`

**Interfaces:**
- Produces: `build_html(brand: str, works_df: pandas.DataFrame, top_df: pandas.DataFrame, comments_df: pandas.DataFrame, hot_topics: list[dict], output_name: str, *, style_key: str = "mckinsey", video_insights: dict | None = None) -> str`.
- Produces: `generate_html_from_records(records: list[dict], *, brand_name: str, output_name: str, video_insights_by_work_id: dict[str, str]) -> str`.
- Retains: `render_competitor_report_html(dataset: dict, summary: dict) -> str` as the Agent-facing compatibility entry.

- [ ] **Step 1: Add failing parity tests**

Tests must assert that generated HTML contains:

```python
required_fragments = [
    "McKinsey Consulting",
    "Top3 热门作品",
    'id="authorChart"',
    'id="trendChart"',
    'id="topicChart"',
    'id="sankeyChart"',
    "账号互动贡献",
    "重点经销商承接效果",
    "官方发起 → 经销商承接 桑基图",
]
for fragment in required_fragments:
    assert fragment in rendered
assert "cdn.jsdelivr.net" not in rendered
assert "echarts.init" in rendered
```

Add a records-versus-Excel fixture that verifies equal KPI values, Top3 work IDs and serialized chart datasets.

- [ ] **Step 2: Verify RED**

Run:

```powershell
python -m pytest tests/test_competitor_report_renderer.py -q -p no:cacheprovider
```

Expected: missing McKinsey structure, chart containers and parity entry point.

- [ ] **Step 3: Port the final skill generator**

Copy the topic taxonomy, metric parsing, ranking, summaries, McKinsey CSS, report JSON and ECharts options from the final skill. Remove CLI-only orchestration from the importable module. Preserve the same visible module order and copy.

- [ ] **Step 4: Vendor ECharts**

Store the minified Apache ECharts 5 browser build at `app/agents/competitor_report/assets/echarts.min.js`, record version/source/license in `docs/licenses/apache-echarts-5.md`, and inline the asset before the report initialization script. Do not read `node_modules` or the network at report-generation time.

- [ ] **Step 5: Adapt the compatibility renderer**

`render_competitor_report_html` must convert the existing deterministic dataset to canonical records and call `generate_html_from_records`. Remove placeholder substitution and the simplified template.

- [ ] **Step 6: Verify GREEN and commit**

Run:

```powershell
python -m pytest tests/test_competitor_report_renderer.py tests/test_competitor_report_agent.py -q -p no:cacheprovider
git add app/agents/competitor_report/skill_generator.py app/agents/competitor_report/assets/echarts.min.js docs/licenses/apache-echarts-5.md app/agents/competitor_report/renderer.py tests/test_competitor_report_renderer.py
git rm app/agents/competitor_report/templates/long_report.html
git commit -m "feat: render competitor reports with final skill"
```

Expected: all selected tests pass and no report references a public CDN.

---

### Task 3: Database-to-Skill Data Contract

**Files:**
- Modify: `app/agents/competitor_report/tools.py`
- Modify: `app/agents/competitor_report/graph.py`
- Modify: `app/agents/competitor_report/renderer.py`
- Test: `tests/test_competitor_report_agent.py`
- Test: `tests/test_competitor_report_final_fixes.py`

**Interfaces:**
- Consumes: grounded PostgreSQL works and `insight_markdown`.
- Produces: canonical records with the skill’s Chinese field names and a deterministic rendering dataset.

- [ ] **Step 1: Add failing contract tests**

Assert one database row maps as follows:

```python
assert record == {
    "作品ID": "w-1",
    "标题": "样例标题",
    "作者": "样例账号",
    "品牌": "上汽大众",
    "账号类型": "官方",
    "是否官方号": "是",
    "发布时间": "2026-05-26T10:00:00+08:00",
    "视频链接": "https://example.test/w-1",
    "互动点赞数": 10,
    "评论数": 2,
    "收藏数": 3,
    "分享数": 4,
    "总互动量": 19,
    "是否置顶": "否",
    "话题标签": "#上市",
}
```

Also assert total engagement ignores an inconsistent precomputed value and uses `10 + 2 + 3 + 4`.

- [ ] **Step 2: Verify RED**

Run:

```powershell
python -m pytest tests/test_competitor_report_agent.py tests/test_competitor_report_final_fixes.py -q -p no:cacheprovider
```

Expected: canonical skill records are absent.

- [ ] **Step 3: Implement the adapter and graph handoff**

Add one focused adapter function. The graph must pass the deterministic records, Top3 insight Markdown and validated prose summary into the single skill generator. It must not construct or ask the LLM to construct HTML.

- [ ] **Step 4: Verify no-data and error status**

Tests must prove:

- zero rows returns `status="no_data"` and no completed HTML;
- renderer exception returns a failed status with no completed asset;
- optional insight gaps render `无`;
- report scope in the response equals the stored scope.

- [ ] **Step 5: Verify GREEN and commit**

Run:

```powershell
python -m pytest tests/test_competitor_report_agent.py tests/test_competitor_report_final_fixes.py tests/test_task_api.py -q -p no:cacheprovider
git add app/agents/competitor_report/tools.py app/agents/competitor_report/graph.py app/agents/competitor_report/renderer.py tests/test_competitor_report_agent.py tests/test_competitor_report_final_fixes.py
git commit -m "feat: feed grounded records to competitor skill"
```

Expected: all selected tests pass.

---

### Task 4: Full Integration and Visual Verification

**Files:**
- Modify: `tests/test_asset_library.py`
- Modify: `tests/test_next_frontend_architecture.py`
- Create: `docs/audits/2026-07-28-competitor-report-skill-parity-verification.md`

**Interfaces:**
- Verifies the existing AI report entry, chat report link and report asset HTML viewer.

- [ ] **Step 1: Add integration assertions**

Tests must prove:

- an AI report request for `生成5月最后一周的竞品动态报告` returns and stores `2026-05-25` through `2026-05-31`;
- the chat payload links to the created competitor report asset;
- the asset API returns `view_kind="html"` with the McKinsey structure;
- event report assets remain unchanged.

- [ ] **Step 2: Run focused integration tests**

Run:

```powershell
python -m pytest tests/test_task_api.py tests/test_asset_library.py tests/test_next_frontend_architecture.py -q -p no:cacheprovider
```

Expected: all tests pass.

- [ ] **Step 3: Run full automated verification**

Run:

```powershell
python -m pytest -q -p no:cacheprovider
cd frontend
npm run typecheck
npm run build
```

Expected: zero failures and a successful 30-page Next.js production build.

- [ ] **Step 4: Perform browser comparison**

Generate the same 2026-05-25 through 2026-05-31 report through the AI entry, open its report asset, and compare it at the same desktop viewport with the final skill’s McKinsey sample. Record:

- scope text;
- all required sections;
- Top3 layout;
- chart rendering;
- Sankey rendering;
- missing-data states;
- browser console errors.

- [ ] **Step 5: Record evidence and commit**

Write exact commands, counts, screenshots or screenshot limitations, and remaining gaps to the audit file.

```powershell
git add tests/test_asset_library.py tests/test_next_frontend_architecture.py docs/audits/2026-07-28-competitor-report-skill-parity-verification.md
git commit -m "test: verify competitor report skill parity"
```

