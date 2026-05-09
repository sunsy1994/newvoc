# VOC看事件：上传模板、ETL规则与指标支撑设计

## 1. 目标

这份文档用于把「VOC看事件」从底层数据反推到用户可使用的数据准备方式。

我们当前的共识是：

- 使用者上传的是 ODS 原始数据，不直接维护复杂的 DWD/REL/ADS 表。
- 标准化 ETL 负责清洗字段、生成系统 ID、去重、更新、拆分作者资产、生成关系。
- 聚合 ETL 负责从 DWD/REL 生成 ADS 指标表，页面和报告只读 ADS。
- 第一阶段只做「VOC看事件」，不做「VOC看用户」、竞品、成交、到店、复购等链路。

对应 schema 文件：

- `docs/postgresql/data_access_schema.sql`

## 2. 数据链路总览

```text
用户上传 Excel/CSV
  -> ODS 原始上传层
     - ods_event_upload
     - ods_content_upload
     - ods_comment_upload
  -> 标准化 ETL
     - 字段校验
     - 枚举清洗
     - ID生成
     - 自然键去重
     - upsert更新
     - 作者拆分
     - 关系生成
  -> DWD/REL 标准明细与关系层
     - dwd_event
     - dwd_content
     - dwd_author
     - dwd_comment
     - rel_event_content
     - rel_author_content
  -> 聚合 ETL
     - ads_event_overview
     - ads_event_trend_daily
     - ads_event_content_rank
  -> VOC看事件页面 / 报告 / AI摘要
```

## 2.1 推荐上传顺序

推荐顺序：

1. 先上传事件表。
2. 再上传内容表。
3. 最后上传评论表。

原因是内容需要归属到某个事件，评论需要归属到某条内容。

但这里的“顺序”不应该增加使用者负担：

- 事件表里建议填写 `raw_event_id`，这是你自己维护的事件编号，例如 `EVT-2026-001`。
- 内容表里填写同一个 `raw_event_id`，系统就能把内容归到事件下，不要求你知道系统生成的 `event_id`。
- 评论表里优先填写 `content_source_url`，系统用内容原始链接匹配帖子，不要求你知道系统生成的 `content_id`。

如果未来做成一个上传向导，页面可以表现成三步：

- 第一步：创建/选择事件。
- 第二步：上传事件内容。
- 第三步：上传评论明细。

## 3. 上传模板一：事件上传

目标表：`ods_event_upload`

使用场景：先定义一个事件锚点，例如“某车型上市发布会”“某价格权益调整”“某质量争议事件”。

| 中文名 | 字段名 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- |
| 原始事件ID | `raw_event_id` | 建议必填 | `EVT-2026-001` | 你自己维护的事件ID。建议填写，因为后续内容上传可以直接用它归属事件；不传时 ETL 根据事件名称等字段生成系统 `event_id`。 |
| 事件名称 | `event_name` | 必填 | `A车型上市传播` | 页面和报告里的事件标题。 |
| 事件类型 | `event_type` | 必填 | `新品上市` | 枚举：新品上市、品牌传播、价格权益、产品质量、服务体验、事故舆情、竞品对比、用户口碑、其他。 |
| 品牌名称 | `brand_name` | 选填 | `某品牌` | 用于筛选和展示。 |
| 车型名称 | `model_name` | 选填 | `A车型` | 用于筛选和展示。 |
| 事件开始时间 | `start_time` | 建议填 | `2026-05-01 00:00:00` | 用于事件周期和趋势。 |
| 事件结束时间 | `end_time` | 选填 | `2026-05-08 23:59:59` | 未结束可为空。 |
| 事件状态 | `event_status` | 必填 | `进行中` | 枚举：进行中、已结束、归档。 |
| 事件关键词 | `keyword_list` | 选填 | `A车型,上市,权益` | 多个关键词可用逗号、顿号、竖线分隔。 |
| 事件描述 | `event_desc` | 选填 | `上市传播阶段重点观察用户对价格和配置的反馈` | 用于人工理解事件背景。 |

系统字段：

- `ods_row_id`、`ingest_batch_id`、`source_file_name`、`raw_row_no`、`raw_payload_json`、`created_time` 由系统记录或生成，上传模板里不要求用户填写。

## 4. 上传模板二：内容上传

目标表：`ods_content_upload`

使用场景：上传事件相关的帖子、视频、文章、官方内容、媒体内容、达人内容、经销商内容等。内容表允许同时带作者字段，ETL 会自动拆成内容资产和作者资产。

| 中文名 | 字段名 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- |
| 原始内容ID | `raw_content_id` | 选填 | `douyin_123` | 有平台内容ID就传；不传时 ETL 基于 `platform + source_url` 生成系统 `content_id`。 |
| 原始事件ID | `raw_event_id` | 建议必填 | `EVT-2026-001` | 填事件上传模板里的 `raw_event_id`。这样使用者不需要知道系统生成的 `event_id`。 |
| 标准事件ID | `event_id` | 选填 | `EVT-2026-001` | 高级字段。系统已返回标准 `event_id` 时可填；普通上传不用填。 |
| 平台 | `platform` | 必填 | `抖音` | 如抖音、快手、小红书、微博、B站、懂车帝、汽车之家等。 |
| 原始链接 | `source_url` | 必填 | `https://...` | 内容去重的核心字段。每条内容尽量提供稳定链接。 |
| 内容标题 | `title` | 必填 | `A车型上市，价格到底香不香？` | 原平台无标题时，可用正文前若干字生成。 |
| 内容正文 | `content_text` | 选填 | `这次上市主要看点是...` | 用于后续摘要、标注、搜索。 |
| 内容类型 | `content_type` | 选填 | `达人内容` | 枚举：官方内容、媒体内容、达人内容、用户内容、经销商内容。 |
| 媒介形态 | `media_form` | 选填 | `视频` | 枚举：视频、图文、直播、其他。 |
| 发布时间 | `published_at` | 必填 | `2026-05-01 20:30:00` | 用于趋势和传播节点。 |
| 点赞数 | `like_cnt` | 选填 | `1200` | 空值 ETL 置 0。 |
| 评论数 | `comment_cnt` | 选填 | `318` | 平台显示评论数，空值 ETL 置 0。 |
| 分享数 | `share_cnt` | 选填 | `88` | 空值 ETL 置 0。 |
| 收藏数 | `favorite_cnt` | 选填 | `56` | 空值 ETL 置 0。 |
| 播放/阅读数 | `view_cnt` | 选填 | `50213` | 不混入互动量，仅作为曝光/阅读参考。 |
| 原始作者ID | `raw_author_id` | 选填 | `author_001` | 有平台作者ID就传；不传时 ETL 基于主页或昵称生成系统 `author_id`。 |
| 作者名称 | `author_name` | 必填 | `车圈老张` | 作者资产的基础字段。 |
| 作者主页链接 | `author_home_url` | 选填 | `https://.../user/...` | 作者去重优先使用该字段。 |
| 作者类型 | `author_type` | 选填 | `达人` | 枚举：官方号、媒体号、达人、经销商、普通用户、其他。 |
| 是否KOL | `is_kol` | 选填 | `true` | 作者属性，不属于帖子本身。不会放在内容表里做帖子字段。 |
| 作者粉丝数 | `fans_cnt` | 选填 | `120000` | 作为作者粉丝数快照，upsert 时更新。 |
| 作者简介 | `author_desc` | 选填 | `汽车测评博主` | 用于作者资产沉淀。 |

系统字段：

- `ods_row_id`、`ingest_batch_id`、`source_file_name`、`raw_row_no`、`raw_payload_json`、`created_time` 由系统记录或生成。

## 5. 上传模板三：评论上传

目标表：`ods_comment_upload`

使用场景：上传某条内容下的评论明细。第一版不做跨平台用户识别，只把评论作为事件原声和指标计算材料。

| 中文名 | 字段名 | 必填 | 示例 | 说明 |
| --- | --- | --- | --- | --- |
| 原始评论ID | `raw_comment_id` | 选填 | `comment_001` | 有平台评论ID就传；不传时 ETL 基于内容、昵称、正文、时间生成系统 `comment_id`。 |
| 所属内容ID | `content_id` | 选填 | `CONTENT-001` | 可填写系统 `content_id`，也可填写内容上传模板里的 `raw_content_id`。不知道ID时可以不填。 |
| 所属内容原始链接 | `content_source_url` | 建议填 | `https://.../post/...` | 推荐填写内容原始链接，ETL 可用 `platform + content_source_url` 匹配内容。 |
| 平台 | `platform` | 选填 | `抖音` | 为空时 ETL 可从内容表继承。 |
| 评论作者ID | `comment_author_id` | 选填 | `user_001` | 第一版不用于跨平台用户识别。 |
| 评论作者昵称 | `comment_author_name` | 必填 | `喜欢旅行的小王` | 用于评论展示和评论去重。 |
| 父评论ID | `parent_comment_id` | 选填 | `comment_parent_001` | 用于回复关系，第一版可以不重点使用。 |
| 回复层级 | `reply_level` | 选填 | `1` | 空值 ETL 置 1；1 表示主评论。 |
| 评论正文 | `comment_text` | 必填 | `这个价格如果有置换补贴就很香` | VOC 分析核心原文。 |
| 评论发布时间 | `published_at` | 必填 | `2026-05-01 21:10:00` | 用于评论趋势和扩散节点。 |
| 评论点赞数 | `like_cnt` | 选填 | `23` | 空值 ETL 置 0。 |
| 评论回复数 | `reply_cnt` | 选填 | `4` | 空值 ETL 置 0。 |
| 评论原始链接 | `source_url` | 选填 | `https://...` | 有则保留，便于溯源。 |

系统字段：

- `ods_row_id`、`ingest_batch_id`、`source_file_name`、`raw_row_no`、`raw_payload_json`、`created_time` 由系统记录或生成。

## 6. 标准化 ETL 规则

### 6.1 导入批次

每次上传生成一个 `import_job.job_id`，该 ID 可作为 ODS 表的 `ingest_batch_id`。

导入任务需要记录：

- 上传文件名
- 上传人
- 上传模板
- 成功写入 ODS 行数
- 拒绝写入 ODS 行数
- 错误信息

### 6.2 字段校验

导入 ODS 前先做轻校验：

- 必填字段为空：拒绝该行。
- 时间字段无法解析：拒绝该行。
- 数字字段无法转为数字：拒绝该行或置空后进入错误提示，第一版建议拒绝。
- 枚举不在允许范围：允许入 ODS，但标准化 ETL 标记为 `其他` 或拒绝进入 DWD。第一版建议进入 ODS、DWD 标准化为 `其他`。
- 原始链接为空：内容表拒绝该行，因为 `source_url` 是内容去重核心字段。

### 6.3 ID 生成规则

事件：

- 如果 `raw_event_id` 不为空：`event_id = raw_event_id`。
- 如果 `raw_event_id` 为空：用事件名称、品牌、车型、开始时间标准化后生成哈希 ID。
- `event_key` 用于 upsert 去重，优先 raw_event_id，否则使用自然字段哈希。

内容归属事件：

- 第一推荐：内容上传时填写事件模板里的 `raw_event_id`，ETL 用它匹配 `dwd_event.event_id` 或 `dwd_event.event_key`。
- 如果内容上传时直接填写了标准 `event_id`，ETL 直接匹配 `dwd_event.event_id`。
- 如果两个字段都为空，内容无法稳定归属事件，第一版不进入 `dwd_content`，保留在 ODS 并提示补充事件ID。

内容：

- 如果 `raw_content_id` 不为空：`content_id = raw_content_id`。
- 如果 `raw_content_id` 为空：用 `platform + source_url` 标准化后生成哈希 ID。
- `content_key` 固定由 `platform + source_url` 标准化后生成。

作者：

- 如果 `raw_author_id` 不为空：`author_id = raw_author_id`。
- 如果有 `author_home_url`：用 `platform + author_home_url` 标准化后生成作者哈希 ID。
- 如果没有主页链接：用 `platform + author_name` 标准化后生成作者哈希 ID。
- `author_key` 同样按上述优先级生成，用于作者去重。

评论：

- 如果 `raw_comment_id` 不为空：`comment_id = raw_comment_id`。
- 如果 `raw_comment_id` 为空：用 `content_id + comment_author_name + comment_text + published_at` 标准化后生成哈希 ID。
- `comment_key` 用同一组自然字段生成，用于评论去重。

评论归属内容：

- 如果上传了系统 `content_id`：直接关联 `dwd_content.content_id`。
- 如果上传了内容原始 `raw_content_id`：先匹配内容上传时生成的标准内容。
- 如果没有内容ID但上传了 `content_source_url`：用 `platform + content_source_url` 匹配 `dwd_content.content_key`。
- 如果以上都匹配不到：评论留在 ODS，进入错误提示或待人工补充，不进入 `dwd_comment`。

### 6.4 upsert 更新规则

事件：

- 命中相同 `event_key` 时更新事件名称、类型、品牌、车型、状态、关键词、描述和更新时间。
- `created_time` 保持首次创建时间。

内容：

- 命中相同 `content_key` 时更新标题、正文、内容类型、媒介形态、发布时间和互动字段。
- 点赞、评论、分享、收藏、播放/阅读数以最新上传为准。

作者：

- 命中相同 `author_key` 时更新作者名称、主页、类型、是否KOL、粉丝数、简介。
- 粉丝数作为最新快照，不做历史曲线。

评论：

- 命中相同 `comment_key` 时更新点赞数、回复数、平台、原始链接。
- 评论正文原则上不改；如果原始文本变化，以最新上传为准。

### 6.5 作者拆分与关系生成

内容上传时带作者字段，但标准化后需要拆成：

- `dwd_content`：只保留内容本身和 `author_id`。
- `dwd_author`：沉淀作者资产。
- `rel_author_content`：记录哪个作者发布了哪条内容。

事件关系：

- 第一版内容上传时明确给 `raw_event_id` 或标准 `event_id`。
- 标准化 ETL 匹配到标准事件后，根据 `dwd_content.event_id` 自动生成 `rel_event_content`。
- `match_type = manual`。
- `match_score = 1`。
- `is_primary_event = true`。

## 7. 聚合 ETL 与 ADS 指标

### 7.1 事件总览

目标表：`ads_event_overview`

| 指标 | 字段 | 公式 | 当前是否可做 |
| --- | --- | --- | --- |
| 内容数 | `content_cnt` | `count(distinct dwd_content.content_id)` | 可做 |
| 评论明细数 | `comment_cnt` | `count(distinct dwd_comment.comment_id)` | 可做 |
| 作者数 | `author_cnt` | `count(distinct rel_author_content.author_id)` | 可做 |
| KOL内容数 | `kol_content_cnt` | 作者 `is_kol=true` 的内容数 | 可做 |
| 总互动量 | `total_engagement` | `sum(like_cnt + comment_cnt + share_cnt + favorite_cnt)` | 可做 |
| 平台列表 | `platform_list` | 事件内容覆盖平台去重 | 可做 |
| 平台Top | `top_platform_json` | 按内容数、评论数或互动量聚合平台TopN | 可做 |
| 作者Top | `top_author_json` | 按内容数或互动量聚合作者TopN | 可做 |

注意：

- `view_cnt` 不进入总互动量，只作为曝光/阅读参考。
- `comment_cnt` 在内容表里是平台显示评论数，`ads_event_overview.comment_cnt` 是导入评论明细数，两者口径不同。

### 7.2 日趋势

目标表：`ads_event_trend_daily`

| 指标 | 字段 | 公式 | 当前是否可做 |
| --- | --- | --- | --- |
| 当日内容数 | `content_cnt` | 按 `dwd_content.published_at::date` 统计内容数 | 可做 |
| 当日评论数 | `comment_cnt` | 按 `dwd_comment.published_at::date` 统计评论数 | 可做 |
| 当日互动量 | `engagement_cnt` | 当日内容互动量 + 当日评论互动量 | 可做 |

注意：

- 如果某天只有评论没有新内容，该天也需要出现在趋势表中。
- 趋势只代表已上传数据的时间分布，不代表全网真实声量。

### 7.3 内容排行

目标表：`ads_event_content_rank`

首期建议只保留三类排行：

| 排行类型 | `rank_type` | 排序规则 | 当前是否可做 |
| --- | --- | --- | --- |
| 高互动内容 | `engagement` | `engagement_total desc` | 可做 |
| 高评论内容 | `comment` | `comment_cnt desc` | 可做 |
| KOL内容 | `kol_content` | `is_kol=true` 且 `engagement_total desc` | 可做 |

暂不做：

- 负面内容排行：需要评论情感标签。
- 问题内容排行：需要 `issue_tag`。
- 有效互动内容排行：需要 `is_vehicle_related_comment`。

## 8. 当前 schema 能支撑的首批页面/报告指标

首批可以直接做：

| 模块 | 指标 | 数据来源 | 说明 |
| --- | --- | --- | --- |
| 事件概览 | 内容数 | `ads_event_overview.content_cnt` | 已上传事件内容规模。 |
| 事件概览 | 评论明细数 | `ads_event_overview.comment_cnt` | 已上传评论规模。 |
| 事件概览 | 作者数 | `ads_event_overview.author_cnt` | 事件下参与发文作者数量。 |
| 事件概览 | KOL内容数 | `ads_event_overview.kol_content_cnt` | 依赖作者 `is_kol`。 |
| 事件概览 | 总互动量 | `ads_event_overview.total_engagement` | 点赞+评论+分享+收藏。 |
| 平台分析 | 平台结构 | `ads_event_overview.top_platform_json` | 平台内容/互动分布。 |
| 作者分析 | 作者Top | `ads_event_overview.top_author_json` | 高内容量或高互动作者。 |
| 趋势分析 | 内容/评论日趋势 | `ads_event_trend_daily` | 按日期展示上传数据分布。 |
| 内容排行 | 高互动内容 | `ads_event_content_rank` | 可回跳原始链接。 |
| 内容排行 | KOL内容排行 | `ads_event_content_rank` | 基于作者是否KOL。 |

## 9. 需要补标注后才能做的指标

这些指标不是不能做，而是需要后续增加评论/内容标签表或标签字段。第一版页面不要硬展示。

| 指标 | 缺少的数据 | 建议后续补充 |
| --- | --- | --- |
| 有效互动率 | `is_vehicle_related_comment` | 评论级是否车相关。 |
| 平台有效讨论率 | `is_vehicle_related_comment` + `platform` | 评论归属平台和车相关标签。 |
| KOL有效互动率 | KOL内容下评论是否车相关 | 评论级车相关标签。 |
| 负面率 | `sentiment_tag` | 评论情感标签。 |
| 产品正负反馈Top | `sentiment_tag`、`issue_tag`、`proposition_tag` | 评论/内容标签。 |
| 价格感知 | 价格类 `issue_tag`、`attitude_tag` | 问题和态度标签。 |
| 购买决策障碍 | `intent_tag`、`issue_tag` | 意向和问题标签。 |
| 证据强度 | `evidence_tag` | 证据类型标签。 |
| 目标人群匹配度 | `stage_tag`、`mindset_tag` | 阶段和心智标签。 |
| 误伤/争议信号 | `sentiment_tag`、`attitude_tag`、`issue_tag` | 评论标签。 |

## 10. 第一版不要展示的内容

为了避免产品虚胖，以下内容当前不展示：

- 投放 ROI：缺少投放成本、曝光、线索和转化。
- 真实到店/下订/成交：当前未接入 DCC、CRM、订单。
- NPS：缺少标准推荐题。
- 服务满意度：缺少工单、门店、服务评价闭环。
- 传播链路图：缺少转发、引用、跨平台转载关系。
- 自动谣言识别：缺少事实库和人工真伪标注。
- KOL信任度指数：缺少信任/广告质疑标签。

## 11. 下一步落地顺序

建议按这个顺序做：

1. 固化三张上传模板说明，先让使用者知道怎么准备数据。
2. 写 ETL 标准化脚本：ODS -> DWD/REL，先跑事件，再跑内容，最后跑评论。
3. 写聚合 ETL 脚本：DWD/REL -> ADS。
4. 用一小批真实事件数据跑通链路。
5. 页面只展示 ADS 已经能支撑的指标。
6. 另起一轮设计标签表，再扩展有效互动率、负面率、问题Top、价格感知等 VOC 深层指标。

## 12. 当前本地试跑方式

已提供一个本地 ETL 脚本，用于先不依赖数据库地验证三张上传表是否能跑通 ODS -> DWD/REL -> ADS。

脚本位置：

- `backend/scripts/event_voc_ods_etl.py`

模板输出位置：

- `app/public/data-import-templates/event-voc/event_upload_template.xlsx`
- `app/public/data-import-templates/event-voc/content_upload_template.xlsx`
- `app/public/data-import-templates/event-voc/comment_upload_template.xlsx`

同时也生成同名 `.csv` 模板。

生成模板：

```bash
python backend/scripts/event_voc_ods_etl.py generate-templates
```

生成并试跑样例：

```bash
python backend/scripts/event_voc_ods_etl.py run-sample
```

样例输入输出位置：

- 输入：`runs/event_voc_etl_sample/input`
- 输出：`runs/event_voc_etl_sample/output`

用真实数据试跑时，建议把三张上传文件放入一个目录，文件名使用：

- `event_upload.xlsx` 或 `event_upload.csv`
- `content_upload.xlsx` 或 `content_upload.csv`
- `comment_upload.xlsx` 或 `comment_upload.csv`

然后执行：

```bash
python backend/scripts/event_voc_ods_etl.py run --input-dir <你的输入目录> --output-dir <你的输出目录>
```

当前脚本输出：

- ODS：`ods_event_upload.csv`、`ods_content_upload.csv`、`ods_comment_upload.csv`
- DWD：`dwd_event.csv`、`dwd_content.csv`、`dwd_author.csv`、`dwd_comment.csv`
- REL：`rel_event_content.csv`、`rel_author_content.csv`
- ADS：`ads_event_overview.csv`、`ads_event_trend_daily.csv`、`ads_event_content_rank.csv`
- 汇总：`event_voc_etl_result.xlsx`、`etl_summary.json`
- 拒绝记录：`rejected_content.csv`、`rejected_comment.csv`

## 13. 自查结论

- 本文档只覆盖「VOC看事件」，没有引入用户旅程和竞品故事线。
- 上传模板只反推当前 `data_access_schema.sql` 已存在的 ODS 字段；为了解决系统ID对使用者不友好，内容上传已补充 `raw_event_id`，评论上传已补充 `content_source_url`。
- 当前可展示指标只依赖 DWD/REL/ADS 现有字段。
- 需要标签支撑的指标已单独列出，不进入第一版页面核心展示。
