# AutoVOC 数据资产总蓝图 v1

日期：2026-05-08

## 1. 重新出发的原则

当前系统已经验证出一个关键教训：不能先做页面，再反推底表。页面会不断诱导我们增加看起来有用、但来源不清的卡片和指标，最后导致数据资产、ETL、API、UI 都混在一起。

后续 AutoVOC 按以下顺序建设：

1. 先定义用户故事。
2. 再定义数据主干。
3. 再定义 ETL 职责。
4. 再定义指标白名单。
5. 最后才设计页面。

允许抛弃当前不清晰的代码和页面，但保留已经沉淀出的业务认知：

- VOC 看事件需要围绕事件锚点组织内容、评论、作者/KOL、业务部门视角。
- VOC 看用户不能假设跨渠道身份打通，只能做渠道级触点旅程。
- VOC 看竞品应作为独立故事线，不和前两条底表混在一起。
- 没有真实来源的指标不展示。

## 2. 顶层用户故事

### 2.1 VOC 看事件

用户故事：

作为 VOC 分析师，我希望以一个事件为锚点，查看该事件相关内容、评论、KOL/KOC、用户反馈和部门视角，从而判断事件传播表现、产品反馈、销售机会、服务风险，以及可复用的内容和人群资产。

核心问题：

- 这个事件在什么平台、什么内容形态里传播？
- 用户在评论里讨论了哪些车相关问题？
- 哪些作者/KOL 带来了有效车相关讨论？
- 市场、产品、销售、服务、公关分别能拿走什么结论？
- 哪些内容、评论、作者可以沉淀为后续精准营销资产？

不做的事：

- 不声称知道真实成交。
- 不声称知道真实用户身份。
- 不展示没有底表支持的风险等级、目标匹配度、问题集中度等概念。

### 2.2 VOC 看用户

用户故事：

作为 VOC 分析师，我希望把公网评论、400、企业微信、DCC、大众点评等渠道里的用户声音统一成渠道级触点，按旅程阶段观察用户痛点，从而知道不同阶段用户在问什么、卡在哪里、应该由哪个部门处理。

核心问题：

- 不同渠道天然对应哪些旅程阶段？
- 每个阶段的高频问题、意图、情绪是什么？
- 哪些触点原文能作为证据？
- 哪些问题应该交给销售、门店、服务、客户运营处理？

不做的事：

- 不跨渠道合并用户。
- 不画单个用户完整路径。
- 不计算真实转化率、成交率、复购率，除非未来有订单或客户主数据。

### 2.3 VOC 看竞品

用户故事：

作为 VOC 分析师，我希望自动跟踪核心竞品账号、官方发文、经销商发文和传播动态，从而知道竞品最近在讲什么、推什么、哪些内容值得我方响应。

核心问题：

- 竞品官方最近发布了什么？
- 经销商在推什么卖点和权益？
- 竞品传播节奏、内容主题、车型动作有什么变化？

不做的事：

- 不和我方用户旅程强行打通。
- 不把竞品账号当作我方 KOL 资产。

## 3. 数据分层规范

### 3.1 ODS：原始接入层

用途：

保留来源数据原貌，尽量少加工，用于追溯和重新清洗。

第一版可以不强制建独立 ODS 表。如果使用 Excel/CSV 上传，则上传文件和导入任务记录承担 ODS 作用。

需要记录：

- 文件名
- 来源渠道
- 导入模板
- 操作人
- 导入时间
- 成功/失败状态
- 错误信息

### 3.2 DWD：标准明细层

用途：

承接业务上稳定存在的实体和明细。DWD 表应尽量接近事实，不放复杂推导指标。

第一版核心 DWD 表：

| 表名 | 业务对象 | 说明 |
|---|---|---|
| `dwd_event` | 事件 | 一个可追踪的 VOC 锚点 |
| `dwd_content` | 内容 | 帖子、视频、文章、官方发文等 |
| `dwd_comment` | 评论 | 公网评论和用户公开表达 |
| `dwd_account` | 账号 | 作者、KOL、KOC、官方号、经销商号 |
| `dwd_customer_touchpoint` | 用户触点 | 400、企微、DCC、大众点评、公网评论等统一触点 |

### 3.3 REL：关系层

用途：

表达实体之间的关系，不承载复杂指标。

第一版核心 REL 表：

| 表名 | 关系 | 说明 |
|---|---|---|
| `rel_event_content` | 事件-内容 | 一条内容属于哪个事件 |
| `rel_content_comment` | 内容-评论 | 可选；如果评论表已有 `content_id`，第一版不单独建 |
| `rel_account_content` | 账号-内容 | 可选；如果内容表已有 `author_id`，第一版不单独建 |

第一版建议只保留 `rel_event_content`，避免关系表膨胀。

### 3.4 FACT：标签事实层

用途：

承载模型、人工、规则产生的标签事实。标签不是原始字段，应和 DWD 明细解耦。

第一版核心 FACT 表：

| 表名 | 粒度 | 说明 |
|---|---|---|
| `fact_comment_tag` | 评论-标签 | 评论的问题、意图、情绪、阶段、心智等 |
| `fact_content_tag` | 内容-标签 | 内容主题、卖点、内容角色等 |
| `fact_account_tag` | 账号-标签 | 可选；账号领域、风格、人群倾向等 |
| `fact_touchpoint_tag` | 触点-标签 | 可选；如果触点和评论分离后需要统一标签 |

第一版建议：

- 先保留 `fact_comment_tag` 和 `fact_content_tag`。
- 不急着建 `fact_account_tag` 和 `fact_touchpoint_tag`。
- 如果触点标签字段较少，可暂时放在 `dwd_customer_touchpoint`，后续再拆。

### 3.5 ADS：应用汇总层

用途：

只服务页面和 API。ADS 表可以包含计算指标、TopN JSON、代表样本、数据血缘说明。

ADS 不应反向影响底表定义。

第一版 ADS 按故事线拆分：

| 故事线 | ADS 表 | 用途 |
|---|---|---|
| VOC 看事件 | `ads_event_overview` | 事件总览 |
| VOC 看事件 | `ads_event_department_summary` | 部门视角汇总 |
| VOC 看事件 | `ads_event_kol_summary` | KOL/KOC 表现 |
| VOC 看用户 | `ads_journey_stage_summary` | 旅程阶段汇总 |
| VOC 看用户 | `ads_journey_channel_matrix` | 渠道-阶段矩阵 |
| VOC 看用户 | `ads_journey_painpoint_summary` | 阶段痛点和动作建议 |
| VOC 看竞品 | `ads_competitor_activity_summary` | 竞品动态汇总 |

## 4. 第一版核心底表字段

### 4.1 `dwd_event`

必需字段：

- `event_id`
- `event_name`
- `event_type`
- `brand_name`
- `model_name`
- `start_time`
- `event_status`

可选字段：

- `event_desc`
- `end_time`
- `keyword_list`

不建议放入：

- 热度
- 风险等级
- 部门结论
- AI 摘要

这些应由 ADS 或报告层生成。

### 4.2 `dwd_content`

必需字段：

- `content_id`
- `platform`
- `source_url`
- `author_name`
- `title`
- `published_at`

可选字段：

- `author_id`
- `content_text`
- `content_type`
- `media_form`
- `like_cnt`
- `comment_cnt`
- `share_cnt`
- `favorite_cnt`
- `view_cnt`
- `is_kol`
- `fans_cnt`

计算字段：

- `engagement_total = like_cnt + comment_cnt + share_cnt + favorite_cnt`

注意：

`engagement_total` 是基础计算字段，可以放在 DWD 作为生成列；但复杂价值判断不放在 DWD。

### 4.3 `dwd_comment`

必需字段：

- `comment_id`
- `content_id`
- `comment_author_name`
- `comment_text`
- `published_at`

可选字段：

- `platform`
- `comment_author_id`
- `parent_comment_id`
- `reply_level`
- `like_cnt`
- `reply_cnt`
- `source_url`

不建议放入：

- `opinion_tag`
- `intention_tag`
- `sentiment_tag`
- `persona_tag`
- `stage_tag`
- `mindset_tag`

这些本质上是标签事实，更适合进入 `fact_comment_tag`。如果当前代码已有这些字段，后续可以兼容保留，但新规范中应逐步迁移到 FACT。

### 4.4 `dwd_account`

必需字段：

- `account_id`
- `platform`
- `nickname`

可选字段：

- `platform_account_id`
- `avatar_url`
- `account_type`
- `is_kol`
- `fans_cnt`
- `follow_cnt`
- `liked_cnt`
- `account_desc`
- `certification_info`

不建议放入：

- 用户画像
- 阶段标签
- KOL 价值等级

这些进入标签事实或 ADS。

### 4.5 `dwd_customer_touchpoint`

必需字段：

- `touchpoint_id`
- `source_channel`
- `touchpoint_text`
- `touchpoint_time`

强烈建议字段：

- `source_system`
- `source_record_id`
- `user_display_name`
- `brand_name`
- `model_name`

可选字段：

- `channel_user_key`
- `city_name`
- `store_id`
- `store_name`
- `event_id`
- `content_id`
- `business_status`
- `rating_score`

阶段字段：

- `journey_stage`
- `stage_confidence`
- `stage_reason`

阶段字段可以由 ETL 写入，但必须标明来源：

- 来自业务状态
- 来自文本规则
- 来自渠道默认
- 来自人工标注

不允许：

- 用昵称跨渠道合并用户。
- 用手机号、企微ID等敏感字段进入展示层。
- 在没有订单表的情况下计算成交率、复购率。

## 5. ETL 职责边界

### 5.1 导入 ETL

负责：

- 校验模板必填字段
- 字段名标准化
- 生成缺失主键
- 写入 DWD 表
- 记录导入任务

不负责：

- 生成复杂业务结论
- 生成页面卡片文案
- 推断无法验证的用户身份

### 5.2 标签 ETL

负责：

- 评论问题标签
- 意图标签
- 情绪标签
- 阶段标签
- 心智标签
- 内容主题标签
- 内容角色标签

标签来源必须记录：

- `tag_source`: manual / rule / model
- `model_version`
- `confidence`
- `labeling_reason`

### 5.3 聚合 ETL

负责：

- 按事件聚合内容数、评论数、作者数、KOL数
- 按内容聚合评论结构
- 按作者/KOL聚合内容和评论表现
- 按旅程阶段聚合触点数、问题、意图、情绪
- 生成 TopN、代表样本、数据血缘

不负责：

- 写入原始底表
- 修改标签结果
- 生成无来源指标

## 6. 指标白名单

### 6.1 第一版允许展示的指标

| 指标 | 来源 | 公式 | 适用故事线 |
|---|---|---|---|
| 内容数 | DWD/REL | `count(distinct content_id)` | VOC看事件 |
| 评论数 | DWD/REL | `count(distinct comment_id)` | VOC看事件 |
| 作者数 | DWD/REL | `count(distinct author_id)` | VOC看事件 |
| KOL数 | DWD | `count(distinct author_id where is_kol=true)` | VOC看事件 |
| 总互动量 | DWD | `sum(like_cnt + comment_cnt + share_cnt + favorite_cnt)` | VOC看事件 |
| 负向评论数 | FACT/DWD兼容 | `count(comment where sentiment=负向)` | VOC看事件 |
| 负向占比 | FACT/DWD兼容 | `负向评论数 / 有情绪标签评论数` | VOC看事件 |
| 有效互动率 | FACT/DWD兼容 | `有效评论数 / 评论总数`，有效评论指探讨车相关内容 | VOC看事件/KOL |
| 阶段触点数 | DWD touchpoint | `count(distinct touchpoint_id)` | VOC看用户 |
| 渠道覆盖数 | DWD touchpoint | `count(distinct source_channel)` | VOC看用户 |
| 阶段负向占比 | DWD/FACT | `负向触点数 / 有情绪标签触点数` | VOC看用户 |
| 问题TopN | FACT/DWD兼容 | `group by issue_tag count` | 两条故事线 |
| 意图TopN | FACT/DWD兼容 | `group by intent_tag count` | 两条故事线 |
| 代表样本 | DWD | 最新或高互动原文样本 | 两条故事线 |

### 6.2 第一版暂不展示的指标

| 指标 | 原因 |
|---|---|
| 真实成交率 | 缺少订单/CRM闭环 |
| 真实转化率 | 缺少用户跨渠道身份和漏斗事件 |
| 复购率 | 缺少客户主数据和历史订单 |
| 目标人群匹配度 | 缺少目标人群定义和用户画像标准 |
| 风险等级 | 容易误导，需明确规则和业务阈值 |
| 高置信率 | 需要标签置信度标准化 |
| 问题集中度 | 暂无明确业务动作，先不展示 |
| KOL带单能力 | 缺少投放和成交归因 |
| 单用户旅程路径 | 不能跨渠道识别同一用户 |

## 7. 顶层 UI 应该如何重做

第一版 UI 不再从卡片开始，而从导航结构开始。

推荐顶层导航：

1. 工作台
2. VOC 看事件
3. VOC 看用户
4. VOC 看竞品
5. 数据资产
6. 数据接入
7. 数据计算

### 7.1 数据资产页优先级最高

在继续做故事线页面前，应该先做一个“数据资产总览页”，它回答：

- 当前有哪些底表？
- 每张表是什么粒度？
- 每张表有哪些核心字段？
- 哪些字段是原始导入？
- 哪些字段是 ETL 生成？
- 哪些 ADS 指标可以展示？
- 哪些指标暂不展示？

### 7.2 故事线页面必须引用指标白名单

每个页面卡片必须能回答：

- 数据来自哪张表？
- 是否经过 ETL？
- 公式是什么？
- 没有数据时是否隐藏或空状态？

不能回答这些问题的卡片，不进入第一版页面。

## 8. 当前代码处理策略

当前代码可以作为试验产物保留，但不再作为产品主线继续堆功能。

建议处理方式：

1. 保留当前分支提交，作为探索记录。
2. 新建一次“数据资产规范化”计划。
3. 从 schema 文档开始重写。
4. 先不删旧页面，等新数据资产总览跑通后，再决定哪些页面保留、哪些重做。

不建议马上硬删所有代码，因为当前代码里仍有可复用部分：

- 导入模板机制
- 计算任务机制
- FastAPI 基础结构
- 部分 ETL 写表工具
- 前端导航和资产页骨架

但后续开发必须以本蓝图为准，不再让页面先行。

## 9. 下一步建议

下一步只做一件事：

重写 `docs/postgresql/data_access_schema.sql` 的规范版本，先不实现页面。

目标是产出一份清晰的 schema：

- 表按 ODS / DWD / REL / FACT / ADS 分区排列。
- 每张表写清楚粒度。
- 每个字段区分：原始导入、系统生成、ETL生成。
- 删除或标记不成熟字段。
- 保留兼容字段时注明“过渡字段”。

这一步完成后，再做 ETL 和页面。
