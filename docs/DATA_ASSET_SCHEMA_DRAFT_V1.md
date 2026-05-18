# 数据资产底表设计草案 V1

## 1. 目标与范围

本草案用于支撑当前数据资产产品面：
- 事件库
- 内容库
- 评论库
- 作者库
- KOL库
- 关系视图

设计原则：
- 原子事实和加工结果分层存储，不在一张大宽表里混放。
- 内容、评论、账号保留原始可追溯字段。
- 事件、作者、KOL以汇总服务表承接页面展示。
- 标签、画像、价值判断单独建事实表，便于模型迭代和口径切换。

## 2. 分层建议

推荐采用四层：
- `ODS` 原始采集层：平台原始内容、评论、账号快照。
- `DWD` 标准明细层：统一字段口径后的内容、评论、账号、事件、关系明细。
- `DWM/FACT` 标签画像层：标签、阶段识别、评论结构、关系桥接。
- `ADS` 页面服务层：直接服务事件库、作者库、KOL库等页面的汇总结果。

## 3. 表清单总览

### 3.1 原子/标准明细层
- `ods_content_raw`
- `ods_comment_raw`
- `ods_account_raw`
- `dwd_content`
- `dwd_comment`
- `dwd_account`
- `dwd_event`
- `rel_event_content`
- `rel_content_account`

### 3.2 标签/画像/关系层
- `fact_content_tag`
- `fact_comment_tag`
- `fact_account_stage`
- `fact_account_role`
- `fact_content_comment_profile_di`
- `fact_content_relation`

### 3.3 页面汇总层
- `ads_event_asset_overview_di`
- `ads_author_event_summary_di`
- `ads_kol_event_summary_di`
- `ads_content_value_summary_di`

---

## 4. 表设计明细

## 4.1 `ods_content_raw`

用途：落平台原始内容，保留最大可追溯性。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 分区日期，落仓日期 | 计算 |
| `platform` | 平台 | 原始 |
| `content_id` | 平台内容ID | 原始 |
| `source_url` | 原始链接 | 原始 |
| `author_id` | 平台作者ID | 原始 |
| `author_name` | 作者昵称 | 原始 |
| `title` | 标题 | 原始 |
| `content_text` | 正文/描述文本 | 原始 |
| `content_type_raw` | 平台原始内容类型 | 原始 |
| `media_type_raw` | 平台原始媒体形态 | 原始 |
| `publish_time` | 发布时间 | 原始 |
| `like_cnt` | 点赞数 | 原始 |
| `comment_cnt` | 评论数 | 原始 |
| `share_cnt` | 分享数 | 原始 |
| `favorite_cnt` | 收藏数 | 原始 |
| `view_cnt` | 播放/阅读数 | 原始 |
| `raw_json` | 原始JSON载荷 | 原始 |
| `etl_time` | 入仓时间 | 计算 |

主键建议：
- `(platform, content_id, dt)` 物理去重

分区建议：
- `PARTITION BY dt`

---

## 4.2 `ods_comment_raw`

用途：落平台原始评论。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 分区日期，落仓日期 | 计算 |
| `platform` | 平台 | 原始 |
| `comment_id` | 评论ID | 原始 |
| `content_id` | 所属内容ID | 原始 |
| `parent_comment_id` | 父评论ID | 原始 |
| `reply_level` | 楼层/回复层级 | 原始 |
| `comment_author_id` | 评论作者ID | 原始 |
| `comment_author_name` | 评论作者昵称 | 原始 |
| `comment_text` | 评论正文 | 原始 |
| `publish_time` | 评论发布时间 | 原始 |
| `like_cnt` | 点赞数 | 原始 |
| `reply_cnt` | 回复数 | 原始 |
| `source_url` | 评论链接/内容链接 | 原始 |
| `raw_json` | 原始JSON载荷 | 原始 |
| `etl_time` | 入仓时间 | 计算 |

主键建议：
- `(platform, comment_id, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.3 `ods_account_raw`

用途：落平台原始账号快照。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 分区日期 | 计算 |
| `platform` | 平台 | 原始 |
| `account_id` | 平台账号ID | 原始 |
| `nickname` | 昵称 | 原始 |
| `avatar_url` | 头像 | 原始 |
| `fans_cnt` | 粉丝数 | 原始 |
| `follow_cnt` | 关注数 | 原始 |
| `liked_cnt` | 获赞数 | 原始 |
| `account_desc` | 账号简介 | 原始 |
| `account_certification` | 认证信息 | 原始 |
| `raw_json` | 原始JSON载荷 | 原始 |
| `etl_time` | 入仓时间 | 计算 |

主键建议：
- `(platform, account_id, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.4 `dwd_event`

用途：事件主数据，承接业务定义后的事件实体。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `event_id` | 事件ID | 计算 |
| `event_name` | 事件名称 | 计算 |
| `event_desc` | 事件描述 | 计算 |
| `event_type` | 事件类型，如新品上市/质量争议 | 计算 |
| `brand_name` | 品牌 | 半原始 |
| `model_name` | 车型 | 半原始 |
| `keyword_list` | 事件关键词列表 | 计算 |
| `start_time` | 事件开始时间 | 计算 |
| `end_time` | 事件结束时间 | 计算 |
| `event_status` | 进行中/已结束/归档 | 计算 |
| `created_by` | 创建方式/创建人/规则 | 计算 |
| `created_time` | 创建时间 | 计算 |
| `updated_time` | 更新时间 | 计算 |
| `is_deleted` | 逻辑删除标记 | 计算 |

主键建议：
- `event_id`

分区建议：
- 小表，可不分区；如需分区按 `updated_date`

---

## 4.5 `dwd_content`

用途：统一后的内容明细，是内容库和关系视图的核心事实表。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 分区日期，按发布时间或统计日 | 计算 |
| `content_id` | 统一内容ID | 半原始 |
| `platform` | 平台 | 原始 |
| `source_url` | 原始链接 | 原始 |
| `event_id` | 归属事件ID | 计算 |
| `author_id` | 统一作者ID | 半原始 |
| `author_name` | 作者昵称 | 原始 |
| `author_type` | KOL/KOC/普通用户/媒体等 | 计算 |
| `is_kol` | 是否KOL | 计算 |
| `kol_domain` | KOL领域 | 计算 |
| `fans_cnt` | 作者粉丝数快照 | 半原始 |
| `title` | 标题 | 原始 |
| `content_text` | 正文/摘要文本 | 原始 |
| `content_type` | 标准内容类型，如测评/对比/讨论 | 计算 |
| `media_form` | 图文/视频/长文/直播切片 | 计算 |
| `published_at` | 发布时间 | 原始 |
| `like_cnt` | 点赞数 | 原始 |
| `comment_cnt` | 评论数 | 原始 |
| `share_cnt` | 分享数 | 原始 |
| `favorite_cnt` | 收藏数 | 原始 |
| `view_cnt` | 播放/阅读数 | 原始 |
| `engagement_total` | 综合互动量 | 计算 |
| `content_status` | 是否有效/删除/下架 | 计算 |
| `etl_time` | 入仓时间 | 计算 |

主键建议：
- `content_id`
- 唯一键可补 `(platform, source_url)` 或 `(platform, raw_content_id)`

分区建议：
- `PARTITION BY dt`

---

## 4.6 `dwd_comment`

用途：统一后的评论明细，是评论库、评论画像和证据追溯的核心事实表。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 分区日期 | 计算 |
| `comment_id` | 统一评论ID | 半原始 |
| `platform` | 平台 | 原始 |
| `event_id` | 归属事件ID | 计算 |
| `content_id` | 所属内容ID | 原始 |
| `content_author_id` | 内容作者ID | 计算 |
| `content_author_type` | 内容作者类型 | 计算 |
| `from_kol_content` | 是否来自KOL内容下评论 | 计算 |
| `comment_author_id` | 评论作者ID | 原始 |
| `comment_author_name` | 评论作者昵称 | 原始 |
| `parent_comment_id` | 父评论ID | 原始 |
| `reply_level` | 回复层级 | 原始 |
| `comment_text` | 评论正文 | 原始 |
| `published_at` | 评论发布时间 | 原始 |
| `like_cnt` | 点赞数 | 原始 |
| `reply_cnt` | 回复数 | 原始 |
| `interaction_cnt` | 评论互动量 | 计算 |
| `source_url` | 原始链接 | 原始 |
| `etl_time` | 入仓时间 | 计算 |

主键建议：
- `comment_id`

分区建议：
- `PARTITION BY dt`

---

## 4.7 `dwd_account`

用途：统一作者/账号维度，服务作者库、KOL库。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 账号快照日期 | 计算 |
| `account_id` | 统一账号ID | 半原始 |
| `platform` | 平台 | 原始 |
| `platform_account_id` | 平台原始账号ID | 原始 |
| `nickname` | 昵称 | 原始 |
| `avatar_url` | 头像 | 原始 |
| `account_type` | 普通用户/KOC/KOL/媒体/品牌 | 计算 |
| `is_kol` | 是否KOL | 计算 |
| `domain_tag` | 账号领域标签 | 计算 |
| `fans_cnt` | 粉丝数 | 原始 |
| `follow_cnt` | 关注数 | 原始 |
| `liked_cnt` | 累计获赞数 | 原始 |
| `account_desc` | 简介 | 原始 |
| `certification_info` | 认证信息 | 原始 |
| `account_status` | 是否有效 | 计算 |
| `etl_time` | 入仓时间 | 计算 |

主键建议：
- `(account_id, dt)` 快照主键

分区建议：
- `PARTITION BY dt`

---

## 4.8 `rel_event_content`

用途：事件与内容的桥接表，支持一条内容命中多个事件。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 关系生成日期 | 计算 |
| `event_id` | 事件ID | 计算 |
| `content_id` | 内容ID | 原始 |
| `match_type` | 规则命中/模型归因/人工确认 | 计算 |
| `match_score` | 归因得分 | 计算 |
| `is_primary_event` | 是否主事件 | 计算 |
| `created_time` | 关系生成时间 | 计算 |

主键建议：
- `(event_id, content_id)`

分区建议：
- `PARTITION BY dt`

---

## 4.9 `rel_content_account`

用途：内容与账号关系表，保留作者归属。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 分区日期 | 计算 |
| `content_id` | 内容ID | 原始 |
| `account_id` | 账号ID | 计算 |
| `relation_type` | 作者/转发/搬运等 | 计算 |
| `is_primary_author` | 是否主作者 | 计算 |
| `created_time` | 关系生成时间 | 计算 |

主键建议：
- `(content_id, account_id, relation_type)`

分区建议：
- `PARTITION BY dt`

---

## 4.10 `fact_content_tag`

用途：内容标签事实表，承接命题/问题/证据/风险/价值等标签。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 标签生产日期 | 计算 |
| `content_id` | 内容ID | 原始 |
| `event_id` | 事件ID | 计算 |
| `tag_type` | 标签类型，如 proposition/issue/evidence/risk/value/content_role | 计算 |
| `tag_value` | 标签值 | 计算 |
| `tag_score` | 标签分值/概率 | 计算 |
| `is_primary_tag` | 是否主标签 | 计算 |
| `model_version` | 模型版本 | 计算 |
| `tag_source` | 规则/模型/人工 | 计算 |
| `generated_time` | 标签生成时间 | 计算 |

主键建议：
- `(content_id, tag_type, tag_value, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.11 `fact_comment_tag`

用途：评论标签事实表，承接心智、阶段、情绪、命题、问题、证据等标签。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 标签生产日期 | 计算 |
| `comment_id` | 评论ID | 原始 |
| `content_id` | 内容ID | 原始 |
| `event_id` | 事件ID | 计算 |
| `tag_type` | mindset/stage/sentiment/proposition/issue/evidence | 计算 |
| `tag_value` | 标签值 | 计算 |
| `confidence` | 标签置信度 | 计算 |
| `labeling_reason` | 打标原因 | 计算 |
| `model_version` | 模型版本 | 计算 |
| `tag_source` | 规则/模型/人工 | 计算 |
| `generated_time` | 生成时间 | 计算 |

主键建议：
- `(comment_id, tag_type, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.12 `fact_account_stage`

用途：账号阶段识别结果，如车主/试驾/准车主/未知。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 产出日期 | 计算 |
| `account_id` | 账号ID | 计算 |
| `event_id` | 事件ID | 计算 |
| `stage_tag` | 阶段标签 | 计算 |
| `stage_confidence` | 阶段置信度 | 计算 |
| `stage_reason` | 识别依据 | 计算 |
| `sample_content_cnt` | 参与识别的内容数 | 计算 |
| `sample_comment_cnt` | 参与识别的评论数 | 计算 |
| `model_version` | 模型版本 | 计算 |
| `generated_time` | 生成时间 | 计算 |

主键建议：
- `(account_id, event_id, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.13 `fact_account_role`

用途：账号角色标签，如高证据作者、高争议作者、解释型、测评型等。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 产出日期 | 计算 |
| `account_id` | 账号ID | 计算 |
| `event_id` | 事件ID | 计算 |
| `role_tag` | 角色标签 | 计算 |
| `role_score` | 标签得分 | 计算 |
| `role_reason` | 标签依据 | 计算 |
| `generated_time` | 生成时间 | 计算 |

主键建议：
- `(account_id, event_id, role_tag, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.14 `fact_content_comment_profile_di`

用途：内容下评论结构画像，直接支撑内容库里的 `commentProfile`。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 统计日期 | 计算 |
| `content_id` | 内容ID | 原始 |
| `event_id` | 事件ID | 计算 |
| `comment_cnt` | 评论总数 | 计算 |
| `high_confidence_rate` | 高置信评论占比 | 计算 |
| `owner_rate` | 车主评论占比 | 计算 |
| `test_drive_rate` | 试驾评论占比 | 计算 |
| `prospect_rate` | 准车主评论占比 | 计算 |
| `doubt_rate` | 质疑占比 | 计算 |
| `approval_rate` | 认可占比 | 计算 |
| `positive_rate` | 正向占比 | 计算 |
| `negative_rate` | 负向占比 | 计算 |
| `stage_top1` | 阶段Top1 | 计算 |
| `attitude_top1` | 态度Top1 | 计算 |
| `mindset_distribution_json` | 心智分布JSON | 计算 |
| `emotion_distribution_json` | 情绪分布JSON | 计算 |
| `attitude_distribution_json` | 态度分布JSON | 计算 |
| `stage_distribution_json` | 阶段分布JSON | 计算 |

主键建议：
- `(content_id, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.15 `fact_content_relation`

用途：内容与内容的关联推荐，支撑“关联内容”和关系视图扩展。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 产出日期 | 计算 |
| `content_id` | 当前内容ID | 原始 |
| `related_content_id` | 关联内容ID | 原始 |
| `relation_type` | 同事件/同命题/同作者/互证/补充证据 | 计算 |
| `relation_score` | 关联得分 | 计算 |
| `relation_reason` | 关联原因 | 计算 |

主键建议：
- `(content_id, related_content_id, relation_type, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.16 `ads_event_asset_overview_di`

用途：事件库页面服务表，直接支撑事件级摘要。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 统计日期 | 计算 |
| `event_id` | 事件ID | 计算 |
| `platform_list` | 覆盖平台列表 | 计算 |
| `content_cnt` | 内容数 | 计算 |
| `comment_cnt` | 评论数 | 计算 |
| `author_cnt` | 作者数 | 计算 |
| `kol_cnt` | KOL数 | 计算 |
| `heat_score` | 热度 | 计算 |
| `growth_rate` | 增速 | 计算 |
| `risk_level` | 风险等级 | 计算 |
| `topic_top_json` | 主命题Top列表 | 计算 |
| `updated_time` | 最后更新时间 | 计算 |

主键建议：
- `(event_id, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.17 `ads_content_value_summary_di`

用途：内容库页面服务表，承接内容价值判断结果。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 统计日期 | 计算 |
| `content_id` | 内容ID | 原始 |
| `event_id` | 事件ID | 计算 |
| `content_role` | 内容角色，如测评型/提车型/体验型 | 计算 |
| `value_level` | 价值等级 | 计算 |
| `value_flags_json` | 价值标签列表 | 计算 |
| `value_summary` | 价值总结 | 计算 |
| `value_reason_json` | 价值原因列表 | 计算 |
| `risk_summary` | 风险总结 | 计算 |
| `is_core_content` | 是否核心内容 | 计算 |
| `tag_confidence` | 标签总体置信度 | 计算 |
| `representative_comments_json` | 代表评论列表 | 计算 |

主键建议：
- `(content_id, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.18 `ads_author_event_summary_di`

用途：作者库页面服务表。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 统计日期 | 计算 |
| `event_id` | 事件ID | 计算 |
| `author_id` | 作者ID | 计算 |
| `nickname` | 作者昵称快照 | 半原始 |
| `platform` | 平台 | 原始 |
| `author_type` | 作者类型 | 计算 |
| `is_kol` | 是否KOL | 计算 |
| `stage_tag` | 阶段标签 | 计算 |
| `stage_confidence` | 阶段置信度 | 计算 |
| `stage_reason` | 阶段识别依据 | 计算 |
| `posts` | 发文数 | 计算 |
| `total_engagement` | 总互动量 | 计算 |
| `comment_trigger_cnt` | 评论触发量 | 计算 |
| `top_content_types_json` | 内容类型Top | 计算 |
| `proposition_top_json` | 命题Top | 计算 |
| `issue_top_json` | 问题Top | 计算 |
| `evidence_strength` | 证据强度 | 计算 |
| `evidence_type` | 证据类型 | 计算 |
| `reproducible_flag` | 是否可复现 | 计算 |
| `controversy_score` | 争议值 | 计算 |
| `high_value_flag` | 是否高价值 | 计算 |
| `high_controversy_flag` | 是否高争议 | 计算 |
| `high_confidence_flag` | 是否高置信 | 计算 |
| `role_tags_json` | 角色标签列表 | 计算 |
| `ai_summary` | AI摘要 | 计算 |
| `content_timeline_json` | 内容时间线 | 计算 |
| `representative_contents_json` | 代表内容 | 计算 |
| `representative_comments_json` | 代表评论 | 计算 |

主键建议：
- `(event_id, author_id, dt)`

分区建议：
- `PARTITION BY dt`

---

## 4.19 `ads_kol_event_summary_di`

用途：KOL库页面服务表。

| 字段名 | 字段说明 | 原始/计算 |
|------|------|------|
| `dt` | 统计日期 | 计算 |
| `event_id` | 事件ID | 计算 |
| `account_id` | KOL账号ID | 计算 |
| `nickname` | 昵称快照 | 半原始 |
| `avatar_url` | 头像快照 | 半原始 |
| `platform` | 平台 | 原始 |
| `fans_cnt` | 粉丝数 | 原始 |
| `domain_tag` | 领域 | 计算 |
| `author_type` | KOL/KOC/媒体 | 计算 |
| `event_posts` | 事件发文数 | 计算 |
| `total_engagement` | 事件总互动量 | 计算 |
| `total_comments` | 事件总评论量 | 计算 |
| `avg_engagement` | 篇均互动量 | 计算 |
| `high_confidence_ratio` | 高置信评论占比 | 计算 |
| `effective_engagement_rate` | 有效互动率 | 计算 |
| `risk_score` | 风险值 | 计算 |
| `role_tags_json` | 角色标签 | 计算 |
| `mindset_top_json` | 评论者心智Top | 计算 |
| `stage_top_json` | 评论者阶段Top | 计算 |
| `intention_top_json` | 评论者意向Top | 计算 |
| `summary` | KOL总结 | 计算 |
| `representative_comments_json` | 代表评论样本 | 计算 |

主键建议：
- `(event_id, account_id, dt)`

分区建议：
- `PARTITION BY dt`

---

## 5. 页面字段映射建议

### 5.1 事件库
- 主来源：`dwd_event` + `ads_event_asset_overview_di`

### 5.2 内容库
- 主来源：`dwd_content`
- 标签：`fact_content_tag`
- 评论结构：`fact_content_comment_profile_di`
- 价值判断：`ads_content_value_summary_di`

### 5.3 评论库
- 主来源：`dwd_comment`
- 标签：`fact_comment_tag`

### 5.4 作者库
- 主来源：`dwd_account`
- 汇总：`ads_author_event_summary_di`

### 5.5 KOL库
- 主来源：`dwd_account`
- 汇总：`ads_kol_event_summary_di`

### 5.6 关系视图
- 事件关系图：`rel_event_content` + `rel_content_account`
- 内容关联：`fact_content_relation`
- 评论群体结构：`fact_content_comment_profile_di`

## 6. 当前版本的关键口径

### 6.1 建议作为原始事实保留的字段
- 内容标题、正文、链接、发布时间、平台
- 内容互动四元组：点赞、评论、分享、收藏
- 评论正文、评论作者、点赞、回复层级
- 账号昵称、平台、粉丝、认证

### 6.2 明确作为计算层的字段
- 事件热度、增速、风险等级
- 内容价值等级、价值标签、核心内容判断
- 评论心智、阶段、情绪、命题、问题、证据标签
- 作者阶段标签、证据强度、争议值
- KOL有效互动率、高置信评论占比、风险值

## 7. 已确认口径

以下事项已经确认，可作为 V1 固定约束：

1. 一条内容允许归属多个事件。
因此保留 `rel_event_content` 桥接表，多对多建模不变。

2. `author` 和 `comment_author` 统一进入同一个 `account` 维度。
因此 `dwd_account` 作为统一账号池保留不变。

3. `ads` 层不保留日快照。
因此 `ads_*_di` 在实际落地时建议调整为“当前态服务表”或“按重跑覆盖”的宽表，不强制保留历史分区快照。

4. 标签结果需要保留模型版本。
因此 `fact_content_tag`、`fact_comment_tag`、`fact_account_stage` 等表中的 `model_version` 保留不变。

5. `risk_summary` 不入库。
因此建议仅保留结构化风险标签、风险分值、风险等级；如需展示总结文案，在服务层或前端临时生成。

## 8. 建议修订

基于以上确认，V2 建议做以下调整：

- `ads_event_asset_overview_di` 改为 `ads_event_asset_overview`
- `ads_author_event_summary_di` 改为 `ads_author_event_summary`
- `ads_kol_event_summary_di` 改为 `ads_kol_event_summary`
- `ads_content_value_summary_di` 改为 `ads_content_value_summary`
- 以上 `ads` 表默认不按 `dt` 做历史快照，采用覆盖更新
- `ads_content_value_summary_di` 中的 `risk_summary` 字段删除

## 9. 推荐落地顺序

第一阶段：
- `dwd_event`
- `dwd_content`
- `dwd_comment`
- `dwd_account`
- `rel_event_content`

第二阶段：
- `fact_content_tag`
- `fact_comment_tag`
- `fact_account_stage`
- `fact_content_comment_profile_di`

第三阶段：
- `ads_event_asset_overview_di`
- `ads_content_value_summary_di`
- `ads_author_event_summary_di`
- `ads_kol_event_summary_di`

这样可以先把“能查、能筛、能联动”做起来，再补“价值判断、风险判断、画像摘要”。
