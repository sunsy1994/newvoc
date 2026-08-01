# Market Report Storyline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将市场部 AI 报告升级为固定的事件传播复盘故事线，并以传播态势、话题驱动、传播主体、渠道效率四张专属图表替换旧版图表组合。

**Architecture:** 保持现有“LLM 生成文案、后端固定图表契约、前端确定性渲染”的边界。市场报告升级独立 Prompt 版本和缓存契约；新增市场故事线标准化与前端解析器，复用产品部已经落地的故事线外壳与主题色，不改变产品、销售和历史报告。

**Tech Stack:** Python 3、pytest、FastAPI 服务层、Next.js/React、TypeScript、内联 SVG、现有 CSS 主题变量。

## Global Constraints

- 只使用 `build_market_report_context()` 已提供的数据，不新增数据库字段或业务接口。
- LLM 不生成图表、数据点、排序、建议或外部事实。
- 新市场报告使用四章：`rhythm`、`topics`、`subjects`、`channels`。
- 新市场图表使用固定模板：`M1`、`M2`、`M3`、`M4`。
- 历史市场报告按原缓存契约继续读取，不在读取时迁移。
- 删除新市场报告中的“用户反馈构成”，不修改产品部和销售部报告。
- 所有图表只使用现有主题变量，不引入图表依赖。

## File Map

- Modify `app/services/system_settings.py`: 市场 Prompt v2 与故事线输出契约。
- Modify `app/services/report_agent.py`: 市场章节、图表、故事线标准化、Prompt 注入和缓存兼容。
- Modify `app/services/report_visuals.py`: 四张市场专属图表的数据契约。
- Modify `tests/test_market_report_agent.py`: 后端市场 v2 行为和历史兼容测试。
- Modify `tests/test_report_prompt_api.py`: 自定义市场 Prompt 的固定故事线约束测试。
- Create `frontend/src/components/voc/report-summary/marketStorylineData.ts`: 市场故事线校验、指标解析和复制文本。
- Modify `frontend/src/components/voc/report-summary/productStorylineData.ts`: 导出共享故事线视图类型；不改变产品解析行为。
- Modify `frontend/src/components/voc/report-summary/ReportSummaryStoryline.tsx`: 接收共享故事线视图和可选摘要类型文案。
- Create `frontend/src/components/voc/report-visuals/MarketCharts.tsx`: `M1`–`M4` 的确定性 SVG 图表。
- Modify `frontend/src/components/voc/report-visuals/types.ts`: 注册市场模板 ID。
- Modify `frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx`: 映射市场图表组件。
- Modify `frontend/src/components/voc/ReportAiSummaryCard.tsx`: 识别市场 v2、渲染市场故事线并生成复制文本。
- Modify `tests/test_next_frontend_architecture.py`: 前端契约、渲染和降级测试。

---

### Task 1: 固定市场报告 v2 后端契约

**Files:**
- Modify: `app/services/system_settings.py`
- Modify: `app/services/report_agent.py`
- Modify: `app/services/report_visuals.py`
- Test: `tests/test_market_report_agent.py`
- Test: `tests/test_report_prompt_api.py`

**Interfaces:**
- Consumes: `build_market_report_context(dashboard: dict[str, Any]) -> dict[str, Any]`
- Produces: `normalize_market_storyline(value: Any, context: dict[str, Any]) -> dict[str, Any] | None`
- Produces: 图表契约 `M1/M2/M3/M4`，供前端注册表消费。

- [ ] **Step 1: 写市场故事线与图表契约失败测试**

在 `tests/test_market_report_agent.py` 增加断言：

```python
def test_market_v2_uses_propagation_review_contract() -> None:
    from app.services.report_agent import MARKET_REPORT_CHART_CONTRACT, MARKET_REPORT_SECTION_CODES

    assert MARKET_REPORT_SECTION_CODES == (
        "market_rhythm", "market_topics", "market_subjects", "market_channels"
    )
    assert [(item[0], item[1]) for item in MARKET_REPORT_CHART_CONTRACT] == [
        ("market-volume-rhythm", "M1"),
        ("market-topic-drivers", "M2"),
        ("market-subject-contribution", "M3"),
        ("market-channel-efficiency", "M4"),
    ]
    assert all(item[0] != "market-feedback-sentiment" for item in MARKET_REPORT_CHART_CONTRACT)
```

增加 `normalize_market_storyline()` 测试，合法引用只允许：

```python
{
    "scale", "rhythm", "volume_trend", "hot_topics.summary",
    "hot_topics.topics", "kol_and_authors.summary",
    "kol_and_authors.top_authors", "kol_and_authors.kol_type_distribution",
    "platform.summary", "platform.platform_efficiency",
}
```

并验证章节严格按 `rhythm/topics/subjects/channels` 排列，未知指标引用被过滤，空标题或缺章返回 `None`。

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest tests/test_market_report_agent.py -q`

Expected: FAIL，显示旧章节 `market_platforms/market_feedback`、旧模板 `F3/F5/F8/L14`，且 `normalize_market_storyline` 尚不存在。

- [ ] **Step 3: 实现最小后端契约**

在 `app/services/report_agent.py` 定义：

```python
MARKET_STORY_CHAPTER_IDS = ("rhythm", "topics", "subjects", "channels")
MARKET_STORY_METRIC_REFS = {
    "scale", "rhythm", "volume_trend", "hot_topics.summary", "hot_topics.topics",
    "kol_and_authors.summary", "kol_and_authors.top_authors",
    "kol_and_authors.kol_type_distribution", "platform.summary",
    "platform.platform_efficiency",
}
```

`normalize_market_storyline()` 复用产品故事线的文本上限：headline 160、lead 600、title 60、conclusion 240、body 900、每章最多 4 个 `metric_refs`；市场章节不接受评论证据，所以 `evidence_refs` 统一输出空数组。

将新图表契约固定为：

```python
MARKET_REPORT_CHART_CONTRACT = (
    ("market-volume-rhythm", "M1", "传播结果与节奏", "内容与评论的每日构成", "volume_trend"),
    ("market-topic-drivers", "M2", "话题驱动", "讨论规模、内容量与累计互动", "hot_topics.topics"),
    ("market-subject-contribution", "M3", "传播主体", "作者互动贡献与内容量", "kol_and_authors.top_authors"),
    ("market-channel-efficiency", "M4", "渠道效率", "传播规模与单内容互动效率", "platform.platform_efficiency"),
)
```

在 `build_market_report_charts()` 中按以上字段传递原始行；只做现有 `_rows()` 和 `_meta()` 标准化，不在 LLM 层计算数据。

- [ ] **Step 4: 升级 Prompt 并保持自定义 Prompt 受约束**

将 `MARKET_REPORT_PROMPT_VERSION` 提升为 `market_report_summary_v2`，固定输出 `storyline`：

```json
{
  "headline": "",
  "lead": "",
  "chapters": [
    {"chapter_id":"rhythm","title":"传播结果与节奏","conclusion":"","body":"","metric_refs":[],"evidence_refs":[]},
    {"chapter_id":"topics","title":"话题驱动","conclusion":"","body":"","metric_refs":[],"evidence_refs":[]},
    {"chapter_id":"subjects","title":"传播主体","conclusion":"","body":"","metric_refs":[],"evidence_refs":[]},
    {"chapter_id":"channels","title":"渠道效率","conclusion":"","body":"","metric_refs":[],"evidence_refs":[]}
  ]
}
```

把 `ensure_report_prompt_contract()` 的产品布尔开关收窄为可选 storyline contract 参数，使市场和产品分别注入自己的固定章节，销售保持不注入。更新 `tests/test_report_prompt_api.py`，验证市场自定义 Prompt 必须包含 storyline，销售仍不包含。

- [ ] **Step 5: 连接运行结果与缓存兼容**

在市场 agent 成功路径中仅当四张图至少一张可渲染时附加标准化 storyline。把旧市场 v1 契约加入 `REPORT_CACHE_CONTRACTS`，新生成使用 v2；历史 `market-feedback-sentiment/L14` 报告继续可读。

- [ ] **Step 6: 运行后端测试**

Run: `pytest tests/test_market_report_agent.py tests/test_report_prompt_api.py tests/test_event_report_agent.py -q`

Expected: PASS；事件综合报告仍使用其既有图表合同，不因市场独立报告升级而改变。

- [ ] **Step 7: 提交**

```bash
git add app/services/system_settings.py app/services/report_agent.py app/services/report_visuals.py tests/test_market_report_agent.py tests/test_report_prompt_api.py
git commit -m "feat: add market report review storyline"
```

---

### Task 2: 实现四张市场专属图表

**Files:**
- Create: `frontend/src/components/voc/report-visuals/MarketCharts.tsx`
- Modify: `frontend/src/components/voc/report-visuals/types.ts`
- Modify: `frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: `ReportVisualChart` 的 `M1/M2/M3/M4` 数据。
- Produces: `M1VolumeRhythm`、`M2TopicDrivers`、`M3SubjectContribution`、`M4ChannelEfficiency` React 组件。

- [ ] **Step 1: 写注册与可访问性失败测试**

在前端架构 probe 中构造四张市场图，服务端渲染后断言：

```python
assert probe["marketTemplateIds"] == ["M1", "M2", "M3", "M4"]
assert 'aria-label="传播结果与节奏图"' in probe["marketChartsMarkup"]
assert 'aria-label="话题驱动图"' in probe["marketChartsMarkup"]
assert 'aria-label="传播主体图"' in probe["marketChartsMarkup"]
assert 'aria-label="渠道效率图"' in probe["marketChartsMarkup"]
assert "用户反馈构成" not in probe["marketChartsMarkup"]
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest tests/test_next_frontend_architecture.py -q`

Expected: FAIL，`M1`–`M4` 尚未注册。

- [ ] **Step 3: 注册模板 ID 和图表组件**

在 `types.ts` 将 `M1 | M2 | M3 | M4` 加入 `ReportTemplateId`。在 `ReportChartRegistry.tsx` 注册四个组件，不改变现有模板。

- [ ] **Step 4: 实现 M1 传播态势柱状图**

在 `MarketCharts.tsx` 将日期行按输入顺序展示；每个日期把 `content_count` 和 `comment_count` 映射为同柱上下两段，使用同一主题色的深浅透明度。最大 `total_volume` 日期添加峰值标记。只有一个日期时仍显示一根构成柱和数值标签。

- [ ] **Step 5: 实现 M2 话题驱动排名图**

最多渲染 10 个话题，按 `comment_count` 降序、`total_engagement` 降序、原始索引升序确定顺序。条形长度表达评论量；右侧文字固定显示内容量和累计互动量。所有值为零时显示现有空状态样式。

- [ ] **Step 6: 实现 M3 传播主体棒棒糖图**

最多渲染 5 位作者，线长表达 `total_engagement`，端点直径按 `content_count` 在 8–18px 之间线性映射。作者类型存在时显示为次级标签；不使用随机位置和动画布局。

- [ ] **Step 7: 实现 M4 渠道效率散点图**

横轴使用 `total_volume`，纵轴使用 `engagement_per_content`。坐标归一化到固定 SVG viewBox，平台名称直接标注。只有一个平台时放在图心并显示两个指标；不使用虚假比较轴。

- [ ] **Step 8: 运行测试与类型检查**

Run: `pytest tests/test_next_frontend_architecture.py -q`

Expected: PASS。

Run: `npm run typecheck`

Workdir: `frontend`

Expected: exit code 0。

- [ ] **Step 9: 提交**

```bash
git add frontend/src/components/voc/report-visuals/MarketCharts.tsx frontend/src/components/voc/report-visuals/types.ts frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx tests/test_next_frontend_architecture.py
git commit -m "feat: add market report visual models"
```

---

### Task 3: 将市场摘要接入共享故事线外壳

**Files:**
- Create: `frontend/src/components/voc/report-summary/marketStorylineData.ts`
- Modify: `frontend/src/components/voc/report-summary/productStorylineData.ts`
- Modify: `frontend/src/components/voc/report-summary/ReportSummaryStoryline.tsx`
- Modify: `frontend/src/types/vocMarket.ts`
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Consumes: 后端 `report_narrative.storyline` 和 `M1`–`M4` 图表。
- Produces: `buildMarketStorylineView()`、`formatMarketStorylineCopyText()`。

- [ ] **Step 1: 写市场摘要失败测试**

构造完整市场 v2 payload，断言摘要模式输出一个 hero 和四章：

```python
assert probe["marketStorylineChapterIds"] == ["rhythm", "topics", "subjects", "channels"]
assert probe["marketStorylineMarkup"].count("data-report-storyline-hero") == 1
assert probe["marketStorylineMarkup"].count("data-story-chapter=") == 4
assert "传播结果与节奏" in probe["marketStorylineCopyText"]
assert "market-volume-rhythm" not in probe["marketStorylineCopyText"]
```

再构造缺章、空 headline、全部指标引用无法解析三个 payload，断言均回退到旧摘要，而不是渲染空故事线。

- [ ] **Step 2: 运行测试并确认失败**

Run: `pytest tests/test_next_frontend_architecture.py -q`

Expected: FAIL，当前只识别产品故事线章节。

- [ ] **Step 3: 提取共享视图类型**

将 `ProductStorylineView` 的展示结构改名并导出为 `ReportStorylineView`，保留 `export type ProductStorylineView = ReportStorylineView` 兼容现有产品代码。`ReportSummaryStoryline` 接收共享类型，并新增可选 `summaryLabel`，产品默认“事件综合摘要”，市场传入“事件传播复盘”。

- [ ] **Step 4: 实现市场故事线解析器**

`marketStorylineData.ts` 严格校验 `rhythm/topics/subjects/channels` 顺序。指标解析规则固定为：

- `scale`: 总声量、内容量、评论量、累计互动；
- `rhythm`: 峰值日期、峰值声量、峰值贡献率、二次峰值；
- `hot_topics.*`: 头部话题、话题评论量、内容量和互动量；
- `kol_and_authors.*`: 头部作者、累计互动、内容量和主体类型；
- `platform.*`: 核心平台、平台声量、单内容互动量。

Hero 最多显示总声量、峰值贡献率、核心平台三项确定性指标。章节最多展示三项去重指标，市场 evidence 始终为空。

- [ ] **Step 5: 接入市场 v2 展示与复制**

在 `ReportAiSummaryCard.tsx` 增加市场 v2 合同识别。只有图表精确匹配 `M1/M2/M3/M4` 时调用 `buildMarketStorylineView()`；产品路径保持原逻辑，历史市场报告继续使用旧摘要和旧图表。

- [ ] **Step 6: 运行前端契约测试**

Run: `pytest tests/test_next_frontend_architecture.py -q`

Expected: PASS，产品故事线既有断言仍通过。

Run: `npm run typecheck`

Workdir: `frontend`

Expected: exit code 0。

- [ ] **Step 7: 提交**

```bash
git add frontend/src/components/voc/report-summary/marketStorylineData.ts frontend/src/components/voc/report-summary/productStorylineData.ts frontend/src/components/voc/report-summary/ReportSummaryStoryline.tsx frontend/src/types/vocMarket.ts frontend/src/components/voc/ReportAiSummaryCard.tsx tests/test_next_frontend_architecture.py
git commit -m "feat: render market report storyline"
```

---

### Task 4: 全量验证与真实页面验收

**Files:**
- Modify only if a defect is reproduced in files already listed above.

**Interfaces:**
- Consumes: Tasks 1–3 的完整市场报告 v2。
- Produces: 可生成、可查看、可复制且不破坏历史报告的市场传播复盘。

- [ ] **Step 1: 运行后端全量测试**

Run: `pytest -q`

Expected: 全部通过，无新增失败。

- [ ] **Step 2: 运行前端类型与生产构建**

Run: `npm run typecheck`

Workdir: `frontend`

Expected: exit code 0。

Run: `npm run build`

Workdir: `frontend`

Expected: exit code 0。

- [ ] **Step 3: 浏览器验证真实市场事件**

在 `/voc/events/market` 选择一个具备趋势、话题、作者和平台数据的事件并生成新报告，验证：

1. 摘要默认展示“事件传播复盘”和四章故事线；
2. 图表模式中说明文字位于图表上方；
3. 四张图依次为传播态势、话题驱动、传播主体、渠道效率；
4. 页面不存在“用户反馈构成”；
5. 单独切换摘要/图表模式不丢失内容；
6. 窄屏下标签不遮挡，弹窗无需横向滚动；
7. 打开一个历史市场报告仍能正常展示旧结构。

- [ ] **Step 4: 检查改动边界**

Run: `git diff --check`

Expected: 无空白错误。

Run: `git status --short`

Expected: 只出现本计划文件与实现文件；用户原有未跟踪文件保持未修改、未暂存。

- [ ] **Step 5: 最终提交**

仅当浏览器验收导致必要修复时提交：

```bash
git add app/services/system_settings.py app/services/report_agent.py app/services/report_visuals.py frontend/src/components/voc/report-summary/marketStorylineData.ts frontend/src/components/voc/report-summary/productStorylineData.ts frontend/src/components/voc/report-summary/ReportSummaryStoryline.tsx frontend/src/components/voc/report-visuals/MarketCharts.tsx frontend/src/components/voc/report-visuals/types.ts frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx frontend/src/components/voc/ReportAiSummaryCard.tsx frontend/src/types/vocMarket.ts tests/test_market_report_agent.py tests/test_report_prompt_api.py tests/test_next_frontend_architecture.py
git commit -m "fix: polish market report review experience"
```
