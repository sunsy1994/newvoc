# AutoVOC AI 报告 SVG 可视化升级设计

## 1. 目标

在不改变现有业务接口口径的前提下，为以下四类 AI 报告建立固定故事线和固定 SVG 图表模板：

- 事件综合报告
- 市场部 AI 总结
- 产品部 AI 总结
- 销售部 AI 总结

报告中的数值与图表数据由确定性代码从现有接口数据构建；LLM 只生成固定位置的标题、摘要和图表解读，不选择图型、不计算图表数据、不输出任意 HTML 或 JavaScript。

本次工作在独立分支 `codex/lieflat-ai-report-visuals` 中完成，方便随时回滚到当前稳定版本。

## 2. 设计原则

### 2.1 固定故事线

每类报告的章节、图表数量、图型和数据映射均由代码固定。报告生成时只替换事件数据和 LLM 文案。

### 2.2 数据与文案分离

```text
现有业务接口
├─ 确定性 chart builder：计算并组装 chart_spec
├─ 固定 report template：决定章节和图表位置
└─ LLM：生成 headline、summary、chart_insight
```

LLM 不能覆盖 chart builder 生成的数值。图表缺少数据时展示明确空状态，不生成演示数据或推测数据。

### 2.3 纯 SVG 第一版

第一版只采用 Lieflat Charts 的 Lupi Editorial 与 Lupi Basics SVG 模板，不引入 ECharts、Chart.js、CDN 或在线字体。

采用的图型：

- F3 Hairline Area
- F4 Tick Donut
- F5 Tick Rows
- F6 Paired Rungs
- F7 Stacked Rungs
- F8 Plumb Scatter
- L12 Type Colonnade
- L13 Hourglass Stream
- L14 Hundred Field

### 2.4 AutoVOC 主题换肤

保留 Lieflat 模板的数据编码、几何关系、比例和逐记录表达，视觉颜色改为 AutoVOC 主题变量：

- 主数据：`--theme-primary`
- 次要数据：`--theme-selected-text` 或主题辅助色
- 正向：现有成功/机会色
- 负向：现有风险色
- 中性：`--theme-muted`
- 网格与导轨：`--theme-border`
- 正文与数值：`--theme-ink`、`--theme-body`
- 背景：`--theme-white`、`--theme-soft-panel`

不复制 Lieflat 的纸灰黑白页面风格，不新增一套独立主题。

## 3. 报告交互结构

三个部门 AI 总结统一提供三个视图：

1. **摘要模式**：固定章节卡片，优先阅读 LLM 结论。
2. **图表模式**：四张固定 SVG 图，每张图上方展示对应的 LLM 解读。
3. **数据依据**：代表性证据、计算口径和数据说明。

事件综合报告沿用现有模式切换能力，并统一使用同一套报告外壳、图表组件与数据依据组件。

历史报告必须保存完整的结构化文案与 chart_spec，使报告再次打开时不重新调用 LLM，且能还原生成时的数据。

## 4. 市场部固定故事线

业务问题：事件如何传播、由谁推动、用户如何反馈？

### 4.1 传播规模与节奏

- 图型：F3 Hairline Area
- 数据源：`volume_trend`
- 固定主值：`total_volume`
- 辅助信息：日期、内容数、评论数、峰值日期
- 结论：起势、峰值、持续时间和衰减形态

### 4.2 热门议题结构

- 图型：F5 Tick Rows
- 数据源：`topic_spread_story.topics`
- 固定排序：接口返回顺序；缺少明确排序时按总讨论量降序
- 结论：讨论最集中的话题及头部集中度

### 4.3 平台传播效率

- 图型：F8 Plumb Scatter
- 数据源：`platform_story.platform_efficiency`
- X/Y 只使用现有同一接口提供的平台规模和反馈效率字段
- 每个点：一个平台
- 结论：区分高规模、高效率和规模效率不匹配的平台

若接口没有足够的二维指标，则图表显示空状态，不临时改成其他图型。

### 4.4 用户反馈构成

- 图型：L14 Hundred Field
- 数据源：`comment_quality.sentiment_distribution`
- 一个点代表一个百分点
- 分类：正向、中性、负向及接口中真实存在的其他类别
- 结论：整体反馈结构和主要情感方向

## 5. 产品部固定故事线

业务问题：用户关注什么、喜欢什么、担心什么、如何比较？

### 5.1 产品关注点

- 图型：F5 Tick Rows
- 数据源：`product_focus_story.aspects`
- 数值：`mention_rate`
- 结论：用户讨论最集中的产品点

### 5.2 产品点正负反馈

- 图型：F6 Paired Rungs
- 数据源：`product_focus_story.aspects`
- 两系列：`positive_rate` 与 `negative_rate`
- 结论：各产品点的惊喜与风险压力

### 5.3 机会、风险与转化

- 图型：三组紧凑 F5 Tick Rows
- 数据源：
  - `product_opportunity_story.surprise_points`
  - `product_opportunity_story.pain_points`
  - `product_opportunity_story.conversion_points`
- 数值：系统已计算的 `opportunity_score`
- 口径展示：`mention_rate × 对应信号率`
- 结论：只展示惊喜点、风险点和转化点，不生成产品建议

### 5.4 PKO 车系与对比维度关系

- 主图：L12 Type Colonnade
- 左侧：明确或泛化的对比车系 `target`
- 右侧：对比维度 `dimension`
- 每条线：一条真实 PKO 评论记录
- 线条颜色：优势、劣势、中性/不明确
- Hover：展示该记录的用户原声、对比对象、维度和结果
- 记录上限：50 条
- 超过 50 条时：按互动量降序、发布时间降序、稳定 ID 排序确定性截取
- 明确标注：`展示 X / 总计 N 条`
- 泛化对象统一归入“其他对象”，不伪造成具体车系

### 5.5 PKO 维度结果明细

- 明细图：F7 Stacked Rungs
- 数据源：`dimension_result_matrix`
- 堆叠系列：优势、劣势、中性；不明确单独弱化展示
- 结论：各对比维度中的本车竞争位置

PKO 阅读顺序固定为：

```text
用户拿我和谁比
→ 主要在哪些维度比较
→ 每个维度的优势/劣势结果
→ 代表性用户原声
```

## 6. 销售部固定故事线

业务问题：线索有多少、质量如何、来自哪里、谁值得优先查看？

### 6.1 线索转化漏斗

- 图型：L13 Hourglass Stream
- 数据源：`sales_lead_quality.summary`
- 固定阶段：
  - 已打标评论
  - 车相关评论
  - 销售相关意图
  - 中/强购买信号
- 每一阶段必须是上一阶段的子集

### 6.2 购买信号结构

- 图型：F4 Tick Donut
- 数据源：`purchase_signal_distribution`
- 分类：强、中、弱、无及真实存在的未标注

### 6.3 用户意图分布

- 图型：F5 Tick Rows
- 数据源：`intent_distribution`
- 数值：评论数与占比

### 6.4 渠道线索效率

- 图型：F6 Paired Rungs
- 数据源：`sales_lead_source_efficiency.platform_efficiency`
- 两系列只使用接口中同口径的总反馈量与销售线索量
- 结论：区分讨论规模与线索产出

## 7. 事件综合报告固定故事线

综合报告不重复展示三个部门的全部图表，只保留四张跨部门核心图：

1. F3：传播节奏
2. L14：用户情感构成
3. F6：产品关注点正负反馈
4. L13：销售线索漏斗

固定阅读顺序：

```text
发生了什么
→ 传播如何演进
→ 用户如何评价
→ 产品机会与风险在哪里
→ 是否形成销售线索
→ 证据引用与计算口径
```

## 8. 数据契约

### 8.1 图表规格

所有图表共享基础字段：

```ts
type ReportChartSpec = {
  chartId: string;
  templateId: "F3" | "F4" | "F5" | "F6" | "F7" | "F8" | "L12" | "L13" | "L14";
  title: string;
  subtitle: string;
  insight: string;
  sourceLabel: string;
  data: unknown[];
  meta?: {
    displayedCount?: number;
    totalCount?: number;
    unit?: string;
    emptyReason?: string;
  };
};
```

不同 SVG 组件拥有各自更严格的内部数据类型。前端注册表按 `templateId` 渲染固定组件，不接受任意组件名或脚本。

### 8.2 LLM 输出

每类部门报告使用固定结构字段，而不是只有自由 Markdown：

```json
{
  "headline": "",
  "executive_summary": "",
  "section_insights": {
    "section_code": ""
  },
  "data_notes": []
}
```

后端校验字段类型和长度。缺失文案使用确定性规则结论回退，不影响图表生成。

### 8.3 空数据

- 图表位置保持不变。
- 显示该图表对应的明确空状态。
- 不用其他图型替换。
- 不生成演示数据。
- LLM 文案不得声称缺失数据中存在趋势或结论。

## 9. 前端组件边界

建议新增：

```text
frontend/src/components/voc/report-visuals/
├─ ReportVisualShell.tsx
├─ ReportChartRegistry.tsx
├─ F3HairlineArea.tsx
├─ F4TickDonut.tsx
├─ F5TickRows.tsx
├─ F6PairedRungs.tsx
├─ F7StackedRungs.tsx
├─ F8PlumbScatter.tsx
├─ L12TypeColonnade.tsx
├─ L13HourglassStream.tsx
├─ L14HundredField.tsx
├─ chartTheme.ts
└─ types.ts
```

每个组件只负责一种数据编码。公共外壳负责标题、副标题、来源、空状态和响应式尺寸。

## 10. 动效与可访问性

- SVG 入场动画只在首次进入视口时播放。
- 支持 `prefers-reduced-motion`，关闭动画后直接显示最终状态。
- 图表必须有可读标题、文字摘要和表格式无障碍描述。
- Hover 信息同时支持键盘焦点。
- 不因动画改变数值比例或排序。

## 11. 测试与验收

### 11.1 后端

- 每个报告类型生成固定 templateId 顺序。
- chart builder 只使用现有接口字段。
- PKO 截取结果确定且不超过 50 条。
- LLM 返回错误或缺字段时，图表仍可生成。
- 空数据不产生虚构值。
- 历史报告保存并恢复同一 chart_spec。

### 11.2 前端

- 九类 SVG 组件能够处理正常、零值、空数组和长中文标签。
- 三个部门报告均有摘要、图表、数据依据模式。
- 综合报告只展示四张固定核心图。
- L12 每条线对应一条真实记录，Hover/键盘可读。
- 主题色来自 AutoVOC CSS 变量。
- 不加载 ECharts、Chart.js 或外部 CDN。

### 11.3 视觉验收

- 桌面端报告弹窗无横向溢出。
- 1280px 与 1440px 下图表标签不重叠。
- 系统明暗层级统一，不出现 Lieflat 原始纸灰黑白孤岛。
- 图表能在 10–30 秒内支持对应故事段落，不成为纯装饰。

## 12. 许可证与来源

本项目为个人非商业项目，允许在 PolyForm Noncommercial License 1.0.0 范围内学习和修改 Lieflat Charts 模板。

实现时：

- 只抽取本设计实际使用的 SVG 模板代码。
- 在仓库中保留 Lieflat Charts 来源与许可证说明。
- 不引入当前未使用的 Chart.js、ECharts 或 Inter 字体。
- 若项目未来转为企业或商业用途，必须在继续使用模板前重新确认商业授权。

## 13. 本次不做

- 不让 LLM动态选图。
- 不引入全部 48 个模板。
- 不引入 ECharts、Chart.js、网络图、Bar Race 或实时流图。
- 不修改三个业务看板主体布局。
- 不新增接口中不存在的数据字段。
- 不把报告导出为 PDF/PPT。
- 不改变现有问答、问数或洞察 Agent 的能力。
