# VOC看事件：BI图表与AI摘要指标血缘

## 1. 巡检结论

本次巡检范围：

- 市场部 VOC BI：`app/src/components/voc/market`
- 产品部 VOC BI：`app/src/components/voc/product`
- 通用部门故事线与图表：`app/src/components/data`
- 通用 AI 助手摘要文案：`app/src/components/AIAssistant.tsx`

已清理口径：

| 旧口径 | 处理方式 | 当前替代 |
| --- | --- | --- |
| 高置信/高致信 | 不作为首期 BI 或 AI 摘要指标 | 车相关原声、证据强度 |
| 问题集中度 | 不作为指标 | 问题标签Top、证据强度、扩散速度 |
| 风险等级 | 不作为等级判断 | 争议信号、负向信号、关键节点 |
| NPS估算 | 不展示 | 正负反馈占比、推荐/劝退表达需另补标签 |
| 投放ROI/预算效率 | 不展示 | 平台有效讨论、KOL有效互动 |
| 价格接受度 | 不展示 | 价格感知 |
| 破圈指数 | 不作为核心判断 | 平台声量结构、有效互动率 |

保留说明：

- “预算压力”保留为用户原声，属于价格感知表达，不是投放预算或 ROI 指标。
- “证据强度”保留，它不是高置信样本数，而是对评论证据类型的加权判断。
- “误伤率”保留为内容引发误解/争议的比例，需要评论标签支撑。

## 2. 原始表字段

这些字段应直接来自原始表或标准化明细表，不在 BI 层重新发明。

| 数据域 | 字段 | 来源层 | 用途 |
| --- | --- | --- | --- |
| 事件 | `event_id` | 原始/标准化 | 事件锚点 |
| 事件 | `event_name` | 原始/标准化 | 页面标题、筛选 |
| 事件 | `event_type` | 原始/标准化 | 判断营销事件/产品舆情事件 |
| 事件 | `event_start_at`、`event_end_at` | 原始/标准化 | 时间窗口 |
| 内容 | `content_id` | 原始/标准化 | 内容去重、内容库 |
| 内容 | `platform` | 原始/标准化 | 平台结构 |
| 内容 | `source_url` | 原始/标准化 | 溯源跳转 |
| 内容 | `title`、`content_text` | 原始/标准化 | AI 摘要、标签抽取 |
| 内容 | `published_at` | 原始/标准化 | 声量趋势、扩散速度 |
| 内容 | `author_id` | 原始/标准化 | 作者/KOL 关联 |
| 内容 | `like_cnt`、`comment_cnt`、`share_cnt`、`favorite_cnt`、`view_cnt` | 原始/标准化 | 互动指标 |
| 评论 | `comment_id` | 原始/标准化 | 评论去重 |
| 评论 | `content_id` | 原始/标准化 | 评论归属内容 |
| 评论 | `comment_text` | 原始/标准化 | 原声、标签抽取 |
| 评论 | `comment_author_id` | 原始/标准化 | 用户画像、阶段聚合 |
| 评论 | `created_at` | 原始/标准化 | 评论趋势、扩散速度 |
| 评论 | `like_cnt`、`reply_cnt` | 原始/标准化 | 评论影响力 |
| 作者 | `account_id`、`account_name` | 原始/标准化 | 作者库、KOL库 |
| 作者 | `fans_cnt` | 原始/标准化 | KOL基础影响力 |

## 3. 标注/加工字段

这些不是原始表天然给出的字段，需要清洗、规则或模型标注后落表。它们是现阶段 BI 能否落地的关键。

| 字段 | 粒度 | 生成方式 | 支撑指标 |
| --- | --- | --- | --- |
| `sentiment_tag` | 评论/内容 | 情感标注：正向、中性、负向、强负向 | 负面率、正负反馈 |
| `attitude_tag` | 评论 | 态度标注：认可、质疑、观望、反对、求证、咨询 | 质疑率、购买决策障碍 |
| `stage_tag` | 评论者/作者 | 阶段标注：知晓、兴趣了解、对比、试驾/到店、报价、下订、车主/售后、未知 | 目标人群匹配度、阶段分布 |
| `intent_tag` | 评论 | 意向标注：问价格、问配置、想试驾、等优惠、已购买等 | 购买决策障碍 |
| `mindset_tag` | 评论者/评论 | 心智标注：价格敏感、技术参数、家庭出行、竞品对比等 | 目标人群匹配度、KOL受众画像 |
| `proposition_tag` | 内容/评论 | 命题标注：价格价值、智能科技、空间实用等 | 主命题Top、用户记忆点 |
| `issue_tag` | 内容/评论 | 问题标注：价格贵、配置纠结、车机卡顿、售后等待等 | 问题标签Top、价格感知 |
| `evidence_tag` | 评论/内容 | 证据标注：亲历、试驾、截图、视频、参数对比、转述、无证据 | 证据强度 |
| `is_vehicle_related_comment` | 评论 | 是否探讨与车相关 | 有效互动率 |
| `author_type`、`is_kol` | 作者 | 账号类型识别：KOL/KOC/媒体/品牌/普通用户 | 来源结构、KOL有效性 |

## 4. 计算指标列表

### 4.1 市场部

| 指标 | 原始/计算 | 公式 | 需要字段 |
| --- | --- | --- | --- |
| 总声量 | 计算 | `内容数 + 评论数`，也可按页面拆成内容声量/评论声量 | `content_id`、`comment_id` |
| 声量趋势 | 计算 | 按日/小时统计 `内容数 + 评论数` | `published_at`、`created_at` |
| 增速 | 计算 | `(当前窗口声量 - 上一窗口声量) / 上一窗口声量` | 时间窗口声量 |
| 总互动量 | 计算 | `like_cnt + comment_cnt + share_cnt + favorite_cnt`，`view_cnt`单列不混入互动 | 内容互动字段 |
| 平台结构 | 计算 | `某平台声量 / 全部声量` | `platform`、声量 |
| 来源结构 | 计算 | `某作者类型内容数 / 全部内容数` | `author_type`、`content_id` |
| 主命题Top | 计算 | 按 `proposition_tag` 统计评论或内容数量并排序 | `proposition_tag` |
| 用户记忆点 | 计算 | `命题/短语出现次数 / 车相关评论数`，展示Top表达与代表原声 | `comment_text`、`proposition_tag`、`is_vehicle_related_comment` |
| 有效互动率 | 计算 | `车相关有效评论数 / 评论总数` | `is_vehicle_related_comment`、`comment_id` |
| 平台有效讨论率 | 计算 | `某平台车相关评论数 / 某平台评论总数` | `platform`、`is_vehicle_related_comment` |
| KOL贡献度 | 计算 | `KOL内容互动量 / 全部内容互动量` | `is_kol`、互动字段 |
| KOL有效互动率 | 计算 | `KOL内容下车相关评论数 / KOL内容下评论总数` | `is_kol`、`is_vehicle_related_comment` |
| 目标人群匹配度 | 计算 | `命中目标心智/阶段的车相关评论者数 / 车相关评论者数` | `mindset_tag`、`stage_tag`、目标人群配置 |
| 误伤率 | 计算 | `由内容表达引发的误解/争议/负向评论数 / 评论总数` | `attitude_tag`、`sentiment_tag`、`issue_tag` |

### 4.2 产品部

| 指标 | 原始/计算 | 公式 | 需要字段 |
| --- | --- | --- | --- |
| 产品正向反馈Top | 计算 | `sentiment_tag=正向` 的评论中按 `proposition_tag/issue_tag` 排序 | `sentiment_tag`、`proposition_tag`、`issue_tag` |
| 产品负向反馈Top | 计算 | `sentiment_tag in (负向,强负向)` 的评论中按 `issue_tag` 排序 | `sentiment_tag`、`issue_tag` |
| 负面率 | 计算 | `负向/强负向评论数 / 评论总数` | `sentiment_tag` |
| 质疑率 | 计算 | `attitude_tag=质疑或求证的评论数 / 评论总数` | `attitude_tag` |
| 问题标签Top | 计算 | 按 `issue_tag` 统计问题评论数并排序 | `issue_tag` |
| 配置纠结点Top | 计算 | `issue_tag`命中配置类 + `attitude_tag in (质疑,观望,求证)` 的评论排序 | `issue_tag`、`attitude_tag` |
| 证据强度 | 计算 | `avg(evidence_weight) / 3`，亲历/视频/截图=3，试驾/参数对比=2，转述=1，无证据=0 | `evidence_tag` |
| 车主/试驾原声 | 计算 | 筛选 `stage_tag in (试驾/到店,车主/售后)` 且车相关评论，按点赞或证据强度排序 | `stage_tag`、`is_vehicle_related_comment`、`like_cnt`、`evidence_tag` |

### 4.3 销售部

| 指标 | 原始/计算 | 公式 | 需要字段 |
| --- | --- | --- | --- |
| 价格感知占比 | 计算 | `价格相关评论数 / 车相关评论数` | `issue_tag=价格类`、`is_vehicle_related_comment` |
| 贵/值/等优惠分布 | 计算 | 价格相关评论中按 `attitude_tag/issue_tag` 分组 | `attitude_tag`、`issue_tag` |
| 竞品价格对比 | 计算 | 命中竞品实体且价格相关评论数 / 价格相关评论数 | 竞品实体、`issue_tag` |
| 购买决策障碍Top | 计算 | `intent_tag in (等优惠,等口碑,配置纠结,竞品对比)` 的评论排序 | `intent_tag`、`issue_tag` |
| 试驾/咨询表达占比 | 计算 | `intent_tag in (想试驾,问价格,问配置) 的评论数 / 车相关评论数` | `intent_tag` |

### 4.4 售后部

| 指标 | 原始/计算 | 公式 | 需要字段 |
| --- | --- | --- | --- |
| 售后服务问题Top | 计算 | 服务类 `issue_tag` 评论数排序 | `issue_tag` |
| 服务负向占比 | 计算 | 服务类负向评论数 / 服务类评论总数 | `issue_tag`、`sentiment_tag` |
| 质量问题售后承接信号 | 计算 | 质量/功能类问题中带售后、维修、解决诉求的评论数 | `issue_tag`、`intent_tag`、`comment_text` |
| 车主售后原声 | 计算 | `stage_tag=车主/售后` 且服务类评论，按点赞/回复排序 | `stage_tag`、`issue_tag`、评论互动字段 |

### 4.5 公关部

| 指标 | 原始/计算 | 公式 | 需要字段 |
| --- | --- | --- | --- |
| 舆情负面率 | 计算 | `负向/强负向评论数 / 评论总数` | `sentiment_tag` |
| 负面话题Top | 计算 | 负向评论中按 `issue_tag/proposition_tag` 排序 | `sentiment_tag`、`issue_tag` |
| 扩散速度 | 计算 | `(当前窗口问题声量 - 上一窗口问题声量) / 上一窗口问题声量` | `issue_tag`、时间字段 |
| 疑似起源内容 | 计算 | 同一 `issue_tag` 下最早且互动/评论较高的内容 | `issue_tag`、`published_at`、互动字段 |
| 关键节点 | 计算 | `互动量标准分 * 0.4 + 评论量标准分 * 0.3 + 负向占比标准分 * 0.3` 排序 | 内容互动、评论量、`sentiment_tag` |
| KOL立场分布 | 计算 | KOL内容和评论区按正/中/负/质疑分组 | `is_kol`、`sentiment_tag`、`attitude_tag` |

## 5. AI摘要输入口径

AI 摘要不直接创造新指标，只读取 BI 已计算的结果和代表原声。

| 摘要模块 | 输入 | 禁止输出 |
| --- | --- | --- |
| 事件进展 | 声量趋势、平台结构、关键节点、增速 | 未接入销量/线索时不说成交、到店、ROI |
| 关键指标 | 主命题Top、有效互动率、KOL有效互动、负面率、问题标签Top | 不说 NPS、高置信、问题集中度 |
| 预警/建议 | 误伤率、负向信号、价格感知、证据强度、代表原声 | 不输出风险等级，不直接给产品技术方案 |

## 6. 当前仍需补标注的数据

为保证现有 BI 能真实落地，下一轮数据清洗优先补这些字段：

1. `is_vehicle_related_comment`：有效互动率的核心字段。
2. `issue_tag`：问题Top、价格感知、售后问题都依赖它。
3. `proposition_tag`：市场部主命题、用户记忆点依赖它。
4. `attitude_tag`：质疑率、误伤率、购买决策障碍依赖它。
5. `stage_tag` 和 `mindset_tag`：目标人群匹配度、KOL受众画像依赖它。
6. `evidence_tag`：产品部证据强度和原声排序依赖它。
