# Sales Report Storyline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将销售部 AI 报告升级为固定的线索复盘故事线，并使用线索漏斗、需求结构、内容来源和承接对象四张专属图表。

**Architecture:** 保持 LLM 只生成叙事、后端固定数据合同、前端确定性渲染的边界。新增销售故事线标准化和 `S1–S4` 图表合同，复用共享故事线与图表外壳，并把旧销售合同作为只读缓存兼容项。

**Tech Stack:** Python 3、pytest、React、Next.js、TypeScript、内联 SVG、现有主题变量。

## Global Constraints

- 只消费 `build_sales_report_context()` 已有字段，不新增数据库字段。
- 四章固定为 `output`、`needs`、`sources`、`follow_up`。
- 四张图固定为 `S1`、`S2`、`S3`、`S4`。
- LLM 不生成图表、排序、个人信息、成交判断或营销承诺。
- 未画像用户显示“未画像用户”，不得推断。
- 历史销售报告保持可读；产品、市场和事件综合报告不改变。
- 所有新图必须使用 `ReportVisualShell`，显示标题、上方解读、来源和空状态。

---

### Task 1: 固定销售报告 v3 后端合同

**Files:**
- Modify: `app/services/system_settings.py`
- Modify: `app/services/report_agent.py`
- Modify: `app/services/report_visuals.py`
- Test: `tests/test_sales_report_agent.py`
- Test: `tests/test_report_prompt_api.py`
- Test: `tests/test_report_visuals.py`

**Interfaces:**
- Produces: `normalize_sales_storyline(value: Any, context: dict[str, Any]) -> dict[str, Any] | None`
- Produces: `S1/S2/S3/S4` 图表数据合同。

- [ ] **Step 1: 写失败测试**

断言新章节为 `sales_output/sales_needs/sales_sources/sales_follow_up`，图表为：

```python
[
    ("sales-lead-output", "S1"),
    ("sales-user-needs", "S2"),
    ("sales-content-sources", "S3"),
    ("sales-follow-up-pool", "S4"),
]
```

测试 `normalize_sales_storyline()` 严格接受 `output/needs/sources/follow_up` 四章，只保留销售上下文允许的 `metric_refs` 和真实用户/评论引用。

- [ ] **Step 2: 验证测试因旧合同失败**

Run: `$env:PYTHONPATH='.'; pytest tests/test_sales_report_agent.py tests/test_report_prompt_api.py tests/test_report_visuals.py -q`

Expected: FAIL，显示旧 `L13/F4/F5/F6` 合同且销售 storyline 不存在。

- [ ] **Step 3: 实现新合同和 Prompt**

将销售默认 Prompt 版本提升为 `sales_report_summary_v3`，固定四章 storyline。允许指标路径：

```python
{
    "lead_quality.summary",
    "lead_quality.intent_distribution",
    "lead_quality.purchase_signal_distribution",
    "lead_quality.profile_segments",
    "lead_source.summary",
    "lead_source.platform_efficiency",
    "lead_source.content_leads",
    "lead_source.lead_comments",
    "recommended_follow_up_users",
}
```

销售证据引用只接受上下文中真实 `comment_user_id`；标准化后每章最多 4 个指标引用、2 个证据引用。

- [ ] **Step 4: 构建四张图数据**

- `S1`: 固定四阶段漏斗，附强信号汇总元数据。
- `S2`: 意图分布作为主数据，购买信号分布放入 `meta.signal_distribution`。
- `S3`: 优先使用 `content_leads`；为空时使用 `platform_efficiency` 并在 `meta.level` 标记 `platform`。
- `S4`: 对 `recommended_follow_up_users` 按用户去重，强信号优先于中信号，仅保留强/中梯队。

- [ ] **Step 5: 保持历史缓存兼容并接入运行结果**

旧 `sales_report_summary_v2 + L13/F4/F5/F6` 加入缓存候选；新运行只有存在可渲染图时附加标准化 storyline。

- [ ] **Step 6: 运行后端测试**

Run: `$env:PYTHONPATH='.'; pytest tests/test_sales_report_agent.py tests/test_report_prompt_api.py tests/test_report_visuals.py tests/test_event_report_agent.py -q`

Expected: PASS，事件综合报告仍使用原销售漏斗。

- [ ] **Step 7: 提交**

```powershell
git add app/services/system_settings.py app/services/report_agent.py app/services/report_visuals.py tests/test_sales_report_agent.py tests/test_report_prompt_api.py tests/test_report_visuals.py
git commit -m "feat: add sales lead review storyline"
```

---

### Task 2: 实现四张销售专属图

**Files:**
- Create: `frontend/src/components/voc/report-visuals/SalesCharts.tsx`
- Modify: `frontend/src/components/voc/report-visuals/types.ts`
- Modify: `frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Produces: `S1LeadOutputFunnel`、`S2UserNeeds`、`S3ContentSources`、`S4FollowUpPool`。

- [ ] **Step 1: 写注册、外壳和可访问性失败测试**

断言 `S1–S4` 均注册，四个组件分别提供“线索产出图、用户需求图、内容线索来源图、承接对象图” aria-label，并且源码中四个主组件均使用 `ReportVisualShell`。

- [ ] **Step 2: 运行失败测试**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py -k sales_report_visual -q`

Expected: FAIL，新模板与组件不存在。

- [ ] **Step 3: 实现 S1 线索漏斗**

用传统横向递减条表达四阶段，显示数量和相对上一级转化率；强购买信号显示为底部辅助指标，不形成第五阶段。

- [ ] **Step 4: 实现 S2 用户需求**

横向排名最多 8 项；机会意图使用主题色，`无效/玩梗` 使用同色低透明度。卡片下方用连续分段条展示强、中、弱、无信号。

- [ ] **Step 5: 实现 S3 内容线索来源**

每行用浅色总长度展示中/强意向，深色内部段展示强信号，右侧显示总评论；附平台和作者标签。平台降级数据必须显示“平台级数据”，不得伪装成内容。

- [ ] **Step 6: 实现 S4 承接对象**

强、中信号两列；每列展示数量和最多 5 个用户卡片。卡片仅显示昵称、平台、画像状态、代表评论；没有明细时仅显示汇总数量。

- [ ] **Step 7: 验证并提交**

Run: `npm run typecheck`

Workdir: `frontend`

Expected: exit code 0。

```powershell
git add frontend/src/components/voc/report-visuals/SalesCharts.tsx frontend/src/components/voc/report-visuals/types.ts frontend/src/components/voc/report-visuals/ReportChartRegistry.tsx tests/test_next_frontend_architecture.py
git commit -m "feat: add sales report visual models"
```

---

### Task 3: 接入销售摘要故事线

**Files:**
- Create: `frontend/src/components/voc/report-summary/salesStorylineData.ts`
- Modify: `frontend/src/types/vocMarket.ts`
- Modify: `frontend/src/components/voc/ReportAiSummaryCard.tsx`
- Test: `tests/test_next_frontend_architecture.py`

**Interfaces:**
- Produces: `isSalesStoryline()`、`buildSalesStorylineView()`、`formatSalesStorylineCopyText()`。

- [ ] **Step 1: 写前端归一化失败测试**

测试销售 storyline 经过 `resolveDepartmentReportPresentation()` 后仍存在；缺章、空标题或全部指标无法解析时回退旧摘要。断言市场和产品 storyline 仍被保留。

- [ ] **Step 2: 验证测试失败**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py -k sales_storyline -q`

Expected: FAIL，前端尚未识别销售四章。

- [ ] **Step 3: 实现销售解析器**

Hero 固定提取中/强信号数、强信号数和线索最高内容；四章从 `S1–S4` 确定性解析最多三项指标。用户证据按真实 `comment_user_id` 解析，无法匹配的引用丢弃。

- [ ] **Step 4: 接入统一报告卡**

在 `DEPARTMENT_REPORT_CONTRACTS` 增加新销售合同并保留旧合同。归一化使用产品、市场、销售三个校验器的 OR 逻辑；摘要标签为“销售线索复盘”，复制文本使用销售格式化器。

- [ ] **Step 5: 验证并提交**

Run: `$env:PYTHONPATH='.'; pytest tests/test_next_frontend_architecture.py -q`

Expected: PASS。

Run: `npm run typecheck`

Workdir: `frontend`

Expected: exit code 0。

```powershell
git add frontend/src/components/voc/report-summary/salesStorylineData.ts frontend/src/types/vocMarket.ts frontend/src/components/voc/ReportAiSummaryCard.tsx tests/test_next_frontend_architecture.py
git commit -m "feat: render sales report storyline"
```

---

### Task 4: 全量验证和真实页面验收

**Files:**
- Modify only files listed above if a reproduced defect requires correction.

- [ ] **Step 1: 后端全量验证**

Run: `$env:PYTHONPATH='.'; pytest -q`

Expected: 全部通过。

- [ ] **Step 2: 前端验证**

Run: `npm run typecheck`

Workdir: `frontend`

Expected: exit code 0。

Run: `npm run build`

Workdir: `frontend`

Expected: exit code 0。

- [ ] **Step 3: 浏览器验收**

在销售看板生成新报告并确认：

1. 默认显示“销售线索复盘”顶部结论和四章摘要；
2. 图表模式四张图的标题、上方解读和来源均存在；
3. 内容线索贡献替代旧平台效率图；
4. 强/中用户不重复，未画像用户不被推断；
5. 历史销售报告仍能打开；
6. 产品和市场最新报告摘要不回退。

- [ ] **Step 4: 边界检查**

Run: `git diff --check`

Expected: 无空白错误，用户原有未跟踪文件未被暂存或修改。
