# 竞品动态报告 Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 AutoVOC 中交付可线上使用的竞品动态报告：按对话中的品牌和时间查询竞品库，确定性选取 Top3，融合逐作品维护的 Markdown 解读，生成固定长 HTML 并进入报告资产。

**Architecture:** 为竞品报告建立独立 LangGraph，不改变事件报告 Graph。数据库服务负责作品解读 CRUD、时间过滤、指标计算和 Top3；LLM 只解析范围并生成有证据的短结论；固定 renderer 生成 HTML，统一报告资产查询同时呈现事件报告和竞品报告。

**Tech Stack:** FastAPI、Pydantic、PostgreSQL/psycopg、LangGraph、现有 OpenAI-compatible JSON 调用、Next.js/React/TypeScript、pytest、npm typecheck。

## Global Constraints

- AI 报告仅提供“事件报告”和“竞品动态报告”，不做二者之间的语义猜测路由。
- 未指定品牌时明确提示并默认“上汽大众”；未指定时间时默认近一个月，并展示实际起止日期。
- `总互动量 = 互动点赞数 + 评论数 + 收藏数 + 分享数`，Top3 必须由确定性代码在品牌和时间过滤后计算。
- 一条作品维护一份 Markdown；没有解读或某个解读字段时显示“无”，不得编造。
- 只交付在线长 HTML；不实现 Deck、PDF、上传、批量解析或多品牌综合报告。
- 不依赖运行时外部目录 `E:\openclaw实战bak\新skill`，只将已确认规则与在线模板迁入工程。
- 保持现有事件报告行为不变；只修改与本功能直接相关的文件。

---

### Task 1: 作品解读存储与 CRUD API

**Files:**
- Modify: `app/services/competitor_library.py`
- Modify: `app/routers/tasks.py`
- Modify: `frontend/src/types/competitors.ts`
- Test: `tests/test_competitor_library.py`
- Test: `tests/test_task_api.py`

**Interfaces:**
- Produces: `get_competitor_work_insight(work_id, database_url=DATABASE_URL) -> dict[str, Any]`
- Produces: `save_competitor_work_insight(work_id, insight_markdown, updated_by=None, database_url=DATABASE_URL) -> dict[str, Any]`
- Produces: `DELETE /api/competitors/works/{work_id}/insight` and GET/PUT on the same resource.
- Produces: works list rows containing `has_insight: bool` and `insight_updated_at`.

- [ ] **Step 1: Write failing service tests**

Add tests that use the existing database test fixture and assert save, update, fetch and clear behavior:

```python
def test_competitor_work_insight_round_trip(database_url):
    saved = save_competitor_work_insight("work_001", "## 视频介绍\n外观展示", "tester", database_url)
    assert saved["work_id"] == "work_001"
    assert saved["insight_markdown"].startswith("## 视频介绍")
    assert get_competitor_work_insight("work_001", database_url)["updated_by"] == "tester"

    cleared = save_competitor_work_insight("work_001", "", "tester", database_url)
    assert cleared["insight_markdown"] == ""
```

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_competitor_library.py -q`

Expected: FAIL because the insight functions do not exist.

- [ ] **Step 3: Implement the minimal storage API**

Add an idempotent table initializer and parameterized CRUD functions in `competitor_library.py`:

```python
COMPETITOR_WORK_INSIGHT_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS data_asset;
CREATE TABLE IF NOT EXISTS data_asset.competitor_work_insight (
    work_id TEXT PRIMARY KEY REFERENCES data_asset.competitor_work(work_id),
    insight_markdown TEXT NOT NULL DEFAULT '',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);
"""
```

Use `INSERT ... ON CONFLICT (work_id) DO UPDATE`, reject nonexistent `work_id`, and treat blank content as a stored empty value. Extend the works query with a `LEFT JOIN` and return `has_insight = length(trim(coalesce(i.insight_markdown, ''))) > 0`.

- [ ] **Step 4: Add route tests and endpoints**

Test GET/PUT/DELETE, a missing work returning 404, and PUT whitespace returning an empty value. Add a Pydantic body:

```python
class CompetitorWorkInsightSaveRequest(BaseModel):
    insight_markdown: str = ""
    updated_by: str | None = None
```

Expose `/api/competitors/works/{work_id}/insight` without adding upload endpoints.

- [ ] **Step 5: Run focused tests**

Run: `pytest tests/test_competitor_library.py tests/test_task_api.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add app/services/competitor_library.py app/routers/tasks.py frontend/src/types/competitors.ts tests/test_competitor_library.py tests/test_task_api.py
git commit -m "feat: add competitor work insight maintenance api"
```

### Task 2: 竞品作品库解读编辑弹窗

**Files:**
- Modify: `frontend/src/components/competitors/CompetitorLibraryPage.tsx`
- Modify: `frontend/src/types/competitors.ts`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: Task 1 GET/PUT/DELETE insight endpoints and `has_insight` list field.
- Produces: works-only “维护解读” action and Markdown editor modal.

- [ ] **Step 1: Write a failing frontend architecture test**

Assert the component contains the insight endpoint, “维护解读”, “已维护”, “未维护”, a textarea, save and clear controls, and that these controls are guarded by `config.mode === "works"`.

- [ ] **Step 2: Run the test and verify failure**

Run: `pytest tests/test_next_frontend_architecture.py -q`

Expected: FAIL because the maintenance UI is absent.

- [ ] **Step 3: Implement the minimal editor**

In `CompetitorLibraryPage.tsx`, add state for the selected work, Markdown text, loading and saving. Add an operation column only in works mode. Opening the modal fetches the current value; saving PUTs JSON; clearing DELETEs or saves an empty string, closes only on explicit close, and refreshes the current page after success.

The modal must show title, author, brand and publish time above a plain `<textarea>`. Do not add upload, Markdown preview, version history or a new component abstraction.

- [ ] **Step 4: Verify UI and types**

Run: `pytest tests/test_next_frontend_architecture.py -q`

Run: `npm run typecheck` in `frontend`

Expected: both PASS.

- [ ] **Step 5: Commit**

```powershell
git add frontend/src/components/competitors/CompetitorLibraryPage.tsx frontend/src/types/competitors.ts tests/test_next_frontend_architecture.py
git commit -m "feat: maintain video insights in competitor library"
```

### Task 3: 时间品牌解析与确定性报告数据集

**Files:**
- Create: `app/agents/competitor_report/__init__.py`
- Create: `app/agents/competitor_report/state.py`
- Create: `app/agents/competitor_report/scope.py`
- Create: `app/agents/competitor_report/tools.py`
- Test: `tests/test_competitor_report_agent.py`

**Interfaces:**
- Produces: `resolve_competitor_report_scope(message, today=None) -> dict[str, str | bool]`.
- Produces: `collect_competitor_report_dataset(brand_name, start_date, end_date, database_url=DATABASE_URL) -> dict[str, Any]`.
- Dataset includes `overview`, `daily_trend`, `account_contribution`, `topic_distribution`, `top_works` and `data_notes`.

- [ ] **Step 1: Write failing scope tests**

Cover explicit dates, “上个月”, “最近两周”, missing time, specified brand and missing brand. The default assertion must be:

```python
scope = resolve_competitor_report_scope("生成一份竞品动态报告", today=date(2026, 7, 18))
assert scope == {
    "brand_name": "上汽大众",
    "brand_defaulted": True,
    "start_date": "2026-06-19",
    "end_date": "2026-07-18",
    "time_defaulted": True,
}
```

Reuse the existing deterministic date resolver where its semantics match; do not duplicate a second natural-language date parser.

- [ ] **Step 2: Write failing dataset tests**

Seed works inside and outside the range and assert filtering occurs before ranking. Assert interaction totals and Top3 ordering, fewer than three rows returning TopN, and insight matching strictly by `work_id`.

- [ ] **Step 3: Run tests and verify failure**

Run: `pytest tests/test_competitor_report_agent.py -q`

Expected: FAIL because the package does not exist.

- [ ] **Step 4: Implement scope and dataset functions**

Use SQL aggregation for counts and daily/account summaries, but calculate every work’s `total_engagement` with the same expression:

```sql
coalesce(interaction_like_cnt, 0)
+ coalesce(comment_cnt, 0)
+ coalesce(favorite_cnt, 0)
+ coalesce(share_cnt, 0)
```

Order Top3 by `total_engagement DESC, published_at DESC, work_id ASC`. Include raw title, author, brand, account type, official flag, publish time, topic tags, URL and all four interaction components. Normalize missing insight content to the literal display value `无` only in the renderer-facing dataset.

- [ ] **Step 5: Run focused tests**

Run: `pytest tests/test_competitor_report_agent.py -q`

Expected: PASS.

- [ ] **Step 6: Commit**

```powershell
git add app/agents/competitor_report tests/test_competitor_report_agent.py
git commit -m "feat: collect grounded competitor report data"
```

### Task 4: 固定 HTML renderer 与竞品报告 LangGraph

**Files:**
- Create: `app/agents/competitor_report/prompts.py`
- Create: `app/agents/competitor_report/renderer.py`
- Create: `app/agents/competitor_report/storage.py`
- Create: `app/agents/competitor_report/graph.py`
- Create: `app/agents/competitor_report/templates/long_report.html`
- Modify: `app/agents/competitor_report/__init__.py`
- Test: `tests/test_competitor_report_agent.py`

**Interfaces:**
- Consumes: Task 3 scope and dataset functions.
- Produces: `run_competitor_report_agent(message, event_id=None, history=None) -> dict[str, Any]`.
- Produces result fields: `status`, `answer`, `report_type`, `brand_name`, `time_scope`, `scope_notice`, `summary`, `report_asset`.

- [ ] **Step 1: Write failing renderer and graph tests**

Mock the LLM JSON response. Assert the HTML contains brand, concrete dates, overview values and Top3 titles; escapes source text; displays `无` for missing insight; contains no Skill path, Tool name or database field name. Assert zero rows raises a business `ValueError` and does not save an asset.

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_competitor_report_agent.py -q`

Expected: FAIL because graph, storage and renderer are absent.

- [ ] **Step 3: Implement the prompt contract**

Require JSON with only evidence-grounded prose:

```json
{
  "executive_summary": ["3至5条有数字或案例支撑的结论"],
  "top_work_findings": [{"work_id": "作品ID", "why_it_matters": "基于输入证据的判断"}],
  "account_summary": "账号贡献结论",
  "rhythm_summary": "发布与互动节奏结论",
  "dealer_summary": "经销商表现；证据不足时明确不足"
}
```

Prompt 明确禁止补齐缺失的视频描述、评论情绪、典型评论和作者回复。

- [ ] **Step 4: Implement renderer and storage**

将新版 Skill 的长报告视觉规则迁成项目内固定 Jinja-free 模板或小型 Python renderer，优先复用现有 HTML 转义工具，不引入新模板依赖。建立 `data_asset.competitor_report_agent_run`，保存品牌、起止日期、生成时间、prompt version、HTML、summary JSON、context JSON 和 rendered prompt。

- [ ] **Step 5: Implement the graph**

Use nodes `resolve_scope → collect_data → summarize → render_report → save_report`. LLM failure must propagate as failure; do not save a completed report. Return an answer that always states final brand and concrete date range, including default notices when applicable.

- [ ] **Step 6: Verify graph tests**

Run: `pytest tests/test_competitor_report_agent.py -q`

Expected: PASS.

- [ ] **Step 7: Commit**

```powershell
git add app/agents/competitor_report tests/test_competitor_report_agent.py
git commit -m "feat: generate fixed competitor html reports"
```

### Task 5: 明确报告类型入口与统一 Agent API

**Files:**
- Modify: `app/agents/core/dispatcher.py`
- Modify: `app/routers/tasks.py`
- Modify: `frontend/src/components/home/AutoVocHomePage.tsx`
- Modify: `frontend/src/types/vocMarket.ts`
- Test: `tests/test_agent_dispatcher.py`
- Test: `tests/test_task_api.py`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: `run_event_report_agent` and Task 4 `run_competitor_report_agent`.
- Produces explicit capabilities `report` (existing event report) and `competitor_report`; no semantic router.
- Produces a clickable competitor report card using `report_asset.report_run_id`.

- [ ] **Step 1: Write failing dispatcher and API tests**

Assert `AGENT_RUNNERS["report"]` remains the event runner, `AGENT_RUNNERS["competitor_report"]` is the new runner, and `/api/agents/run` accepts the new literal. Assert competitor report dispatch does not require or forward an event ID.

- [ ] **Step 2: Run backend tests and verify failure**

Run: `pytest tests/test_agent_dispatcher.py tests/test_task_api.py -q`

Expected: FAIL because the capability is not registered.

- [ ] **Step 3: Register the explicit capability**

Extend `AgentCapability` and `AGENT_RUNNERS`. Keep `report` untouched. Update dispatcher invocation so both runner signatures remain compatible without adding semantic classification.

- [ ] **Step 4: Write failing frontend tests**

Assert the report skill displays exactly two explicit choices, “事件报告”和“竞品动态报告”; selecting competitor report sends `capability: "competitor_report"`; report mode still has no recommendation questions; successful response renders a “查看竞品报告” action.

- [ ] **Step 5: Implement the report subtype switch**

Inside the existing report workspace, add a compact two-option selector. Do not create a fifth top-level AI capability. For event report retain existing event context; for competitor report send no `event_id`. Show the returned brand/time notice in the assistant response and open the HTML through the report asset viewer.

- [ ] **Step 6: Verify frontend and API**

Run: `pytest tests/test_agent_dispatcher.py tests/test_task_api.py tests/test_next_frontend_architecture.py -q`

Run: `npm run typecheck` in `frontend`

Expected: all PASS.

- [ ] **Step 7: Commit**

```powershell
git add app/agents/core/dispatcher.py app/routers/tasks.py frontend/src/components/home/AutoVocHomePage.tsx frontend/src/types/vocMarket.ts tests/test_agent_dispatcher.py tests/test_task_api.py tests/test_next_frontend_architecture.py
git commit -m "feat: add explicit competitor report entry"
```

### Task 6: 报告资产统一列表与 HTML 查看

**Files:**
- Modify: `app/services/asset_library.py`
- Modify: `app/routers/tasks.py`
- Modify: `frontend/src/components/assets/AssetLibraryPage.tsx`
- Modify: `frontend/src/types/assets.ts`
- Test: `tests/test_asset_library.py`
- Test: `tests/test_task_api.py`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: existing event report table and Task 4 competitor report table.
- Produces report asset rows with common fields: `report_type`, `subject_name`, `generated_at`, `report_run_id`, `view_kind`.
- Produces `GET /api/assets/reports/{report_type}/{report_run_id}` for a single report view payload.

- [ ] **Step 1: Write failing asset list tests**

Seed one event report and one competitor report. Assert the unified list contains both, is ordered by generation time, labels the subjects correctly, searches by event/brand, paginates across the union, and never exposes rendered prompts in the list.

- [ ] **Step 2: Run tests and verify failure**

Run: `pytest tests/test_asset_library.py tests/test_task_api.py -q`

Expected: FAIL because report assets currently query only event reports.

- [ ] **Step 3: Implement the unified report query**

Replace the report-only event query with a `UNION ALL` subquery mapping event and competitor reports to the common fields. Keep all other asset definitions unchanged. The detail endpoint returns structured JSON for event reports and sanitized stored HTML for competitor reports.

- [ ] **Step 4: Write failing viewer tests and implement the viewer**

Assert event reports still open `StructuredReportView`; competitor reports open the stored HTML in an isolated iframe using `srcDoc` with sandbox restrictions and no script permission. Do not inject stored HTML directly through `dangerouslySetInnerHTML` into the parent application.

- [ ] **Step 5: Run verification**

Run: `pytest tests/test_asset_library.py tests/test_task_api.py tests/test_next_frontend_architecture.py -q`

Run: `npm run typecheck` in `frontend`

Expected: all PASS.

- [ ] **Step 6: Commit**

```powershell
git add app/services/asset_library.py app/routers/tasks.py frontend/src/components/assets/AssetLibraryPage.tsx frontend/src/types/assets.ts tests/test_asset_library.py tests/test_task_api.py tests/test_next_frontend_architecture.py
git commit -m "feat: include competitor reports in report assets"
```

### Task 7: 数据血缘、回归验证与浏览器验收

**Files:**
- Modify: `app/services/data_lineage.py`
- Test: `tests/test_data_lineage.py`
- Test: `tests/test_competitor_report_agent.py`

**Interfaces:**
- Consumes: completed competitor report flow.
- Produces lineage nodes for raw competitor facts, derived total engagement, Top3 rule, maintained insight source and competitor report output.

- [ ] **Step 1: Write failing lineage tests**

Assert the lineage graph distinguishes raw work fields, derived engagement, rule-based Top3, manually maintained Markdown and LLM summary, with edges into the competitor report output.

- [ ] **Step 2: Implement only the required lineage nodes and edges**

Add nodes matching existing `data_lineage.py` conventions. Classify video insight as maintained source data, total engagement as `derived_metric`, Top3 as `rule_judgement`, and report prose as `llm_summary`.

- [ ] **Step 3: Run backend regression**

Run: `pytest tests/test_competitor_library.py tests/test_competitor_report_agent.py tests/test_agent_dispatcher.py tests/test_asset_library.py tests/test_data_lineage.py tests/test_task_api.py -q`

Expected: PASS.

- [ ] **Step 4: Run frontend regression**

Run: `pytest tests/test_next_frontend_architecture.py -q`

Run: `npm run typecheck` in `frontend`

Expected: PASS.

- [ ] **Step 5: Perform browser acceptance**

Verify this exact path against local frontend/backend:

1. Open competitor works and maintain Markdown for three known works.
2. Generate “上个月的竞品动态报告” without a brand and confirm the assistant announces default 上汽大众.
3. Confirm the displayed concrete range is last month and Top3 matches the filtered works.
4. Confirm maintained Top3 content appears and missing fields show “无”.
5. Open the report from the assistant card and from 报告资产.
6. Generate an existing event report and confirm its flow and viewer are unchanged.
7. Confirm no Deck, PDF or upload controls exist.

- [ ] **Step 6: Commit**

```powershell
git add app/services/data_lineage.py tests/test_data_lineage.py tests/test_competitor_report_agent.py
git commit -m "feat: trace competitor report lineage"
```

## Self-review result

- Spec coverage: all ten acceptance criteria map to Tasks 1–7.
- Scope control: Deck、PDF、上传、批量解析和多品牌综合报告均未进入任务。
- Type consistency: `work_id` is the sole insight join key; `competitor_report` is the explicit capability and report type throughout.
- Security: database queries are parameterized; report HTML is escaped during rendering and isolated in a sandboxed iframe when viewed.
- Regression boundary: existing `report` capability and event report tables/viewer remain supported.
