# VOC看事件：ETL与BI数据支撑审计

## 1. 审计结论

当前后端与ETL已经能支撑“事件级基础BI”和“资产库明细追溯”，但还不能支撑之前市场部/产品部大屏中的大部分精细卡片。

已支撑：

- 事件规模：内容数、评论数、作者数、KOL数。
- 互动：点赞、评论、分享、收藏合计互动量。
- 趋势：按日内容数、评论数、互动量、负向评论数、热度分。
- 平台：事件覆盖平台列表。
- 话题/问题粗聚合：基于评论 `opinion_tag`、`intention_tag` 的Top标签。
- 负向舆情：基于 `sentiment_tag` 的负向评论数和负向占比。
- 内容/评论/作者/KOL资产库：可从 `/api/assets/*` 追溯到底层样本。

暂不支撑：

- 有效互动率：缺少 `is_vehicle_related_comment`。
- 目标人群匹配度：缺少目标人群配置，以及稳定的心智/阶段目标规则。
- 产品证据强度：当前导入模板没有独立 `evidence_tag`，后端用 `persona_tag` 临时代替，不应作为正式证据指标展示。
- 产品影响面、处置路径、OTA/服务/改款分流：缺少内部产品/售后处理字段。
- 销售成交、报价、到店、DCC线索：未接入CRM/DCC/订单。
- 售后门店差异、解决速度、重复进店：缺少门店ID和工单闭环。
- 公关完整传播链路：缺少转发、引用、跨平台关联。
- AI摘要：没有基于真实聚合结果的后端生成接口，不能再展示前端静态摘要。

## 2. 底表支撑范围

| 表 | 当前字段能力 | 可支撑展示 |
| --- | --- | --- |
| `dwd_event` | 事件ID、名称、类型、品牌、车型、时间、状态 | 事件筛选、事件标题、时间范围 |
| `dwd_content` | 平台、作者、内容、发布时间、互动量、内容类型、KOL标识 | 内容数、作者数、平台、互动量、来源结构 |
| `rel_event_content` | 事件与内容关系 | 事件维度聚合 |
| `dwd_comment` | 评论文本、时间、点赞回复、情绪、观点、意图、阶段、心智 | 评论数、情绪、问题Top、命题Top、阶段Top |
| `dwd_account` | 账号、粉丝、账号类型、领域、阶段 | 作者/KOL基础画像 |
| `fact_content_tag` | 内容标签通用表 | 目前ETL未充分用于VOC BI |
| `fact_comment_tag` | 评论标签通用表 | 目前ETL未充分用于VOC BI |

## 3. ETL产物支撑范围

| ETL作业 | 输出表 | 已产出指标 | 注意点 |
| --- | --- | --- | --- |
| `event_asset_overview.py` | `ads_event_asset_overview` | 内容数、评论数、作者数、KOL数、总互动、负向占比、热度、增速、平台列表、话题Top | 仍产出 `risk_level`，前端不再展示 |
| `event_trend_daily.py` | `ads_event_trend_daily` | 日内容数、日评论数、日互动量、日负向评论数、日热度 | 可用于趋势图 |
| `content_comment_profile.py` | `fact_content_comment_profile_di` | 评论结构、阶段分布、态度分布、情绪分布 | `high_confidence_rate` 是互动代理，不是我们现在定义的证据字段 |
| `content_value_summary.py` | `ads_content_value_summary` | 内容角色、价值等级、代表评论 | 价值判断仍依赖高置信代理，需要后续改成车相关/证据标签 |
| `author_event_summary.py` | `ads_author_event_summary` | 作者发文、互动、阶段、争议、代表内容/评论 | 仍有 `high_confidence_flag`，前端不作为首期BI指标 |
| `kol_event_summary.py` | `ads_kol_event_summary` | KOL发文、互动、评论、心智Top、阶段Top、意图Top | `effective_engagement_rate` 当前公式不是车相关评论率，不能展示为有效互动率 |

## 4. 前端展示调整

本次已将 `VOC 看事件` 页面从静态样例大屏改为真实数据面板：

- 不再渲染 `MarketDashboard`、`ProductDashboard`、`DepartmentCharts` 的静态样例图表。
- 不再渲染静态 `AIReportModal` 摘要。
- 新增 `EventDataBackedPanel`，只读取真实 `/api/assets/events`、`/trend`、`/comments`、`/contents`、`/kols`。
- 后端不可用或没有事件时，页面显示“未展示样例数据”，不再fallback到mock。
- 每个部门只展示当前底表/ETL能支撑的指标，并列出“暂不展示”的缺口字段。

## 5. 当前可展示指标

| 部门 | 可展示 | 数据来源 |
| --- | --- | --- |
| 市场部 | 内容数、评论数、作者数、KOL数、互动量、热度、增速、平台、命题/意图Top、来源结构 | `ads_event_asset_overview`、`ads_event_trend_daily`、`dwd_content`、`dwd_comment` |
| 产品部 | 负向占比、问题标签Top、情绪分布、负向评论数 | `dwd_comment.sentiment_tag/opinion_tag` |
| 销售部 | 价格相关评论数量、阶段Top | `dwd_comment.opinion_tag/comment_text/stage_tag` |
| 售后部 | 服务相关评论数量、服务/问题标签Top | `dwd_comment.opinion_tag/comment_text` |
| 公关部 | 负向评论数、负向占比、负向问题Top、日趋势 | `dwd_comment.sentiment_tag/opinion_tag`、`ads_event_trend_daily` |

## 6. 当前不要展示的指标

| 指标/卡片 | 不展示原因 | 需要补什么 |
| --- | --- | --- |
| 有效互动率 | 现有ETL没有车相关评论判定 | `is_vehicle_related_comment` |
| KOL有效互动率 | 当前KOL表公式是互动量代理，不是车相关评论/评论总数 | 基于评论标签重算 |
| 目标人群匹配度 | 没有目标人群配置 | 目标人群规则表、心智/阶段匹配规则 |
| 产品证据强度 | 没有独立证据标签 | `evidence_tag` |
| 产品影响面四象限 | 没有购买影响/使用影响标注 | `purchase_impact_tag`、`usage_impact_tag` 或人工规则 |
| 处置路径 | 没有内部处理方案字段 | OTA/售后/硬件/公关分流字段 |
| 销售转化 | 没有DCC/CRM/订单 | 外部业务系统 |
| 售后效率 | 没有工单和门店闭环 | 工单ID、门店ID、解决时间 |
| AI摘要 | 没有真实聚合结果生成接口 | 后端摘要接口，输入必须来自已支撑指标 |

## 7. 下一步最小补字段

为了把之前设计的部门BI逐步恢复，而不是重新变成样例，建议按这个顺序补：

1. 评论表补 `is_vehicle_related_comment`。
2. 评论表或标签表补 `evidence_tag`。
3. 用 `fact_comment_tag` 正式承接 `issue_tag`、`proposition_tag`、`attitude_tag`，减少 `opinion_tag/intention_tag` 的语义混用。
4. KOL汇总重算 `effective_engagement_rate = KOL内容下车相关评论数 / KOL内容下评论总数`。
5. 建立一张目标人群配置表，用于目标人群匹配度。
6. AI摘要接口只允许读取已支撑指标，不允许自由生成未落地结论。
