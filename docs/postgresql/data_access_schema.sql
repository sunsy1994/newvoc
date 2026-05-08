-- AutoVOC 数据资产 Schema v1
-- 范围：仅覆盖第一阶段「VOC看事件」最小可落地数据链路。
-- 原则：
-- 1. 你上传原始事实数据：事件、内容、作者、评论。
-- 2. 系统生成关系表：事件-内容关系、作者-内容关系。
-- 3. ETL 生成 ADS 汇总表：事件总览、事件趋势、内容排行。
-- 4. 第一版不包含用户旅程、竞品、标签事实、订单/成交/复购等后续能力。

CREATE SCHEMA IF NOT EXISTS data_asset;

COMMENT ON SCHEMA data_asset IS 'AutoVOC 数据资产 schema，第一版聚焦 VOC 看事件。';

-- =========================================================
-- DWD：标准明细层
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.dwd_event (
  event_id        VARCHAR(64) PRIMARY KEY,
  event_name      VARCHAR(255) NOT NULL,
  event_type      VARCHAR(64) NOT NULL,
  brand_name      VARCHAR(128),
  model_name      VARCHAR(128),
  start_time      TIMESTAMP,
  end_time        TIMESTAMP,
  event_status    VARCHAR(32) NOT NULL,
  keyword_list    TEXT,
  event_desc      TEXT,
  created_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.dwd_event IS '事件标准明细表。一个事件是一条 VOC 分析主线的锚点。';
COMMENT ON COLUMN data_asset.dwd_event.event_id IS '事件ID。你上传，主键，要求稳定且不重复。示例：EVT-2026-001。';
COMMENT ON COLUMN data_asset.dwd_event.event_name IS '事件名称。你上传，用于页面展示和分析定位。';
COMMENT ON COLUMN data_asset.dwd_event.event_type IS '事件类型。你上传，如新品上市、品牌传播、质量争议、服务体验等。';
COMMENT ON COLUMN data_asset.dwd_event.brand_name IS '品牌名称。你上传，可为空。';
COMMENT ON COLUMN data_asset.dwd_event.model_name IS '车型名称。你上传，可为空。';
COMMENT ON COLUMN data_asset.dwd_event.start_time IS '事件开始时间。你上传，用于圈定事件周期。';
COMMENT ON COLUMN data_asset.dwd_event.end_time IS '事件结束时间。你上传，可为空；为空表示事件仍在观察。';
COMMENT ON COLUMN data_asset.dwd_event.event_status IS '事件状态。你上传，如进行中、已结束、归档。';
COMMENT ON COLUMN data_asset.dwd_event.keyword_list IS '事件关键词。你上传，多个关键词可用竖线或逗号分隔；第一版不强制用于自动匹配。';
COMMENT ON COLUMN data_asset.dwd_event.event_desc IS '事件描述。你上传，可为空，用于补充背景。';
COMMENT ON COLUMN data_asset.dwd_event.created_time IS '记录创建时间。系统生成。';
COMMENT ON COLUMN data_asset.dwd_event.updated_time IS '记录更新时间。系统生成或导入时更新。';

CREATE TABLE IF NOT EXISTS data_asset.dwd_content (
  content_id       VARCHAR(64) PRIMARY KEY,
  event_id         VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  platform         VARCHAR(64) NOT NULL,
  source_url       TEXT NOT NULL,
  title            TEXT NOT NULL,
  content_text     TEXT,
  content_type     VARCHAR(64),
  media_form       VARCHAR(64),
  published_at     TIMESTAMP NOT NULL,
  like_cnt         BIGINT DEFAULT 0,
  comment_cnt      BIGINT DEFAULT 0,
  share_cnt        BIGINT DEFAULT 0,
  favorite_cnt     BIGINT DEFAULT 0,
  view_cnt         BIGINT DEFAULT 0,
  engagement_total BIGINT GENERATED ALWAYS AS (like_cnt + comment_cnt + share_cnt + favorite_cnt) STORED,
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.dwd_content IS '内容标准明细表。存储帖子、视频、文章、官方发文等事件相关内容。';
COMMENT ON COLUMN data_asset.dwd_content.content_id IS '内容ID。你上传，主键，要求稳定且不重复。';
COMMENT ON COLUMN data_asset.dwd_content.event_id IS '所属事件ID。你上传，关联 dwd_event.event_id；第一版由你人工确认内容属于哪个事件。';
COMMENT ON COLUMN data_asset.dwd_content.platform IS '平台。你上传，如抖音、快手、小红书、微博、B站、懂车帝等。';
COMMENT ON COLUMN data_asset.dwd_content.source_url IS '原始链接。你上传，用于追溯内容来源。';
COMMENT ON COLUMN data_asset.dwd_content.title IS '内容标题。你上传；如果原平台无标题，可用正文前若干字生成。';
COMMENT ON COLUMN data_asset.dwd_content.content_text IS '内容正文。你上传，可为空；用于后续标签、摘要、主题分析。';
COMMENT ON COLUMN data_asset.dwd_content.content_type IS '内容类型。你上传，可为空；第一版枚举：官方内容、媒体内容、达人内容、用户内容、经销商内容。';
COMMENT ON COLUMN data_asset.dwd_content.media_form IS '媒介形态。你上传，可为空；第一版枚举：视频、图文、直播、其他。';
COMMENT ON COLUMN data_asset.dwd_content.published_at IS '发布时间。你上传，用于趋势分析。';
COMMENT ON COLUMN data_asset.dwd_content.like_cnt IS '点赞数。你上传，可为空时默认0。';
COMMENT ON COLUMN data_asset.dwd_content.comment_cnt IS '平台显示评论数。你上传，可为空时默认0；不等同于导入评论明细数。';
COMMENT ON COLUMN data_asset.dwd_content.share_cnt IS '分享/转发数。你上传，可为空时默认0。';
COMMENT ON COLUMN data_asset.dwd_content.favorite_cnt IS '收藏数。你上传，可为空时默认0。';
COMMENT ON COLUMN data_asset.dwd_content.view_cnt IS '播放/阅读/浏览数。你上传，可为空时默认0；不同平台口径可能不同。';
COMMENT ON COLUMN data_asset.dwd_content.engagement_total IS '综合互动量。系统生成，公式：点赞数 + 评论数 + 分享数 + 收藏数。';
COMMENT ON COLUMN data_asset.dwd_content.created_time IS '记录创建时间。系统生成。';
COMMENT ON COLUMN data_asset.dwd_content.updated_time IS '记录更新时间。系统生成或导入时更新。';

CREATE TABLE IF NOT EXISTS data_asset.dwd_author (
  author_id       VARCHAR(64) PRIMARY KEY,
  platform        VARCHAR(64) NOT NULL,
  author_name     VARCHAR(255) NOT NULL,
  author_home_url TEXT,
  author_type     VARCHAR(64),
  is_kol          BOOLEAN DEFAULT FALSE,
  fans_cnt        BIGINT DEFAULT 0,
  author_desc     TEXT,
  created_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.dwd_author IS '作者标准明细表。存储内容作者、媒体号、达人号、经销商号等账号资产。';
COMMENT ON COLUMN data_asset.dwd_author.author_id IS '作者ID。你上传，主键，要求在系统内稳定不重复；如果没有平台作者ID，可用平台+作者名生成。';
COMMENT ON COLUMN data_asset.dwd_author.platform IS '作者所在平台。你上传，如抖音、快手、小红书、微博、B站、懂车帝等。';
COMMENT ON COLUMN data_asset.dwd_author.author_name IS '作者名称。你上传，如账号昵称、媒体名、官方号名称。';
COMMENT ON COLUMN data_asset.dwd_author.author_home_url IS '作者主页链接。你上传，可为空，用于追溯账号来源。';
COMMENT ON COLUMN data_asset.dwd_author.author_type IS '作者类型。你上传，可为空；第一版枚举：官方号、媒体号、达人、经销商、普通用户、其他。';
COMMENT ON COLUMN data_asset.dwd_author.is_kol IS '是否KOL。你单独维护，可为空时默认 false；这是作者资产属性，不属于帖子本身。';
COMMENT ON COLUMN data_asset.dwd_author.fans_cnt IS '作者粉丝数。你单独维护，可为空时默认0；表示作者最新或采集时粉丝快照。';
COMMENT ON COLUMN data_asset.dwd_author.author_desc IS '作者简介。你上传，可为空。';
COMMENT ON COLUMN data_asset.dwd_author.created_time IS '记录创建时间。系统生成。';
COMMENT ON COLUMN data_asset.dwd_author.updated_time IS '记录更新时间。系统生成或导入时更新。';

CREATE TABLE IF NOT EXISTS data_asset.dwd_comment (
  comment_id          VARCHAR(64) PRIMARY KEY,
  content_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  platform            VARCHAR(64),
  comment_author_id   VARCHAR(64),
  comment_author_name VARCHAR(255) NOT NULL,
  parent_comment_id   VARCHAR(64),
  reply_level         INTEGER DEFAULT 1,
  comment_text        TEXT NOT NULL,
  published_at        TIMESTAMP NOT NULL,
  like_cnt            BIGINT DEFAULT 0,
  reply_cnt           BIGINT DEFAULT 0,
  interaction_cnt     BIGINT GENERATED ALWAYS AS (like_cnt + reply_cnt) STORED,
  source_url          TEXT,
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.dwd_comment IS '评论标准明细表。存储公网评论原文，是 VOC 看事件的用户声音来源。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_id IS '评论ID。你上传，主键，要求稳定且不重复。';
COMMENT ON COLUMN data_asset.dwd_comment.content_id IS '所属内容ID。你上传，关联 dwd_content.content_id。';
COMMENT ON COLUMN data_asset.dwd_comment.platform IS '评论所在平台。你上传，可为空；为空时可从内容表继承。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_author_id IS '评论作者ID。你上传，可为空；第一版不用于跨平台识别用户。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_author_name IS '评论作者昵称。你上传。';
COMMENT ON COLUMN data_asset.dwd_comment.parent_comment_id IS '父评论ID。你上传，可为空；用于识别回复关系。';
COMMENT ON COLUMN data_asset.dwd_comment.reply_level IS '回复层级。你上传，可为空时默认1；1表示主评论，2及以上表示回复。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_text IS '评论正文。你上传，VOC 分析的核心原文。';
COMMENT ON COLUMN data_asset.dwd_comment.published_at IS '评论发布时间。你上传，用于评论趋势。';
COMMENT ON COLUMN data_asset.dwd_comment.like_cnt IS '评论点赞数。你上传，可为空时默认0。';
COMMENT ON COLUMN data_asset.dwd_comment.reply_cnt IS '评论回复数。你上传，可为空时默认0。';
COMMENT ON COLUMN data_asset.dwd_comment.interaction_cnt IS '评论互动量。系统生成，公式：评论点赞数 + 评论回复数。';
COMMENT ON COLUMN data_asset.dwd_comment.source_url IS '评论原始链接。你上传，可为空，用于追溯。';
COMMENT ON COLUMN data_asset.dwd_comment.created_time IS '记录创建时间。系统生成。';
COMMENT ON COLUMN data_asset.dwd_comment.updated_time IS '记录更新时间。系统生成或导入时更新。';

-- =========================================================
-- REL：关系层
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.rel_event_content (
  event_id         VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  content_id       VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  match_type       VARCHAR(32) DEFAULT 'manual',
  match_score      NUMERIC(8,4) DEFAULT 1,
  is_primary_event BOOLEAN DEFAULT TRUE,
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (event_id, content_id)
);

COMMENT ON TABLE data_asset.rel_event_content IS '事件-内容关系表。第一版由内容表 event_id 自动生成，表示哪些内容属于哪个事件。';
COMMENT ON COLUMN data_asset.rel_event_content.event_id IS '事件ID，关联 dwd_event.event_id。';
COMMENT ON COLUMN data_asset.rel_event_content.content_id IS '内容ID，关联 dwd_content.content_id。';
COMMENT ON COLUMN data_asset.rel_event_content.match_type IS '匹配方式。第一版固定为 manual，表示你上传内容时已明确 event_id。';
COMMENT ON COLUMN data_asset.rel_event_content.match_score IS '匹配置信度。第一版人工指定关系默认为1。';
COMMENT ON COLUMN data_asset.rel_event_content.is_primary_event IS '是否为内容主事件。第一版默认 true。';
COMMENT ON COLUMN data_asset.rel_event_content.created_time IS '关系创建时间。系统生成。';

CREATE TABLE IF NOT EXISTS data_asset.rel_author_content (
  author_id    VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_author(author_id),
  content_id   VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  platform     VARCHAR(64),
  published_at TIMESTAMP,
  created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (author_id, content_id)
);

COMMENT ON TABLE data_asset.rel_author_content IS '作者-内容关系表。表示哪个作者发布了哪条内容，第一版由内容上传模板中的作者字段自动生成。';
COMMENT ON COLUMN data_asset.rel_author_content.author_id IS '作者ID，关联 dwd_author.author_id。';
COMMENT ON COLUMN data_asset.rel_author_content.content_id IS '内容ID，关联 dwd_content.content_id。';
COMMENT ON COLUMN data_asset.rel_author_content.platform IS '平台。来自内容或作者数据，用于辅助查询。';
COMMENT ON COLUMN data_asset.rel_author_content.published_at IS '内容发布时间。来自 dwd_content.published_at，便于按作者追踪内容时间线。';
COMMENT ON COLUMN data_asset.rel_author_content.created_time IS '关系创建时间。系统生成。';

-- =========================================================
-- ADS：应用汇总层
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.ads_event_overview (
  event_id          VARCHAR(64) PRIMARY KEY REFERENCES data_asset.dwd_event(event_id),
  event_name        VARCHAR(255),
  event_type        VARCHAR(64),
  brand_name        VARCHAR(128),
  model_name        VARCHAR(128),
  start_time        TIMESTAMP,
  end_time          TIMESTAMP,
  event_status      VARCHAR(32),
  platform_list     JSONB,
  content_cnt       BIGINT DEFAULT 0,
  comment_cnt       BIGINT DEFAULT 0,
  author_cnt        BIGINT DEFAULT 0,
  kol_content_cnt   BIGINT DEFAULT 0,
  total_engagement  BIGINT DEFAULT 0,
  top_platform_json JSONB,
  top_author_json   JSONB,
  data_lineage_json JSONB,
  updated_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.ads_event_overview IS '事件总览 ADS 表。由 ETL 从事件、内容、评论、关系表聚合生成，供 VOC 看事件页面使用。';
COMMENT ON COLUMN data_asset.ads_event_overview.event_id IS '事件ID。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.event_name IS '事件名称。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.event_type IS '事件类型。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.brand_name IS '品牌名称。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.model_name IS '车型名称。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.start_time IS '事件开始时间。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.end_time IS '事件结束时间。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.event_status IS '事件状态。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.platform_list IS '平台列表。ETL生成，事件相关内容覆盖的平台去重列表。';
COMMENT ON COLUMN data_asset.ads_event_overview.content_cnt IS '内容数。ETL生成，公式：count(distinct content_id)。';
COMMENT ON COLUMN data_asset.ads_event_overview.comment_cnt IS '评论明细数。ETL生成，公式：count(distinct comment_id)。';
COMMENT ON COLUMN data_asset.ads_event_overview.author_cnt IS '作者数。ETL生成，公式：基于 rel_author_content count(distinct author_id)。';
COMMENT ON COLUMN data_asset.ads_event_overview.kol_content_cnt IS 'KOL内容数。ETL生成，公式：内容关联作者中 dwd_author.is_kol=true 的内容数。';
COMMENT ON COLUMN data_asset.ads_event_overview.total_engagement IS '总互动量。ETL生成，公式：sum(dwd_content.engagement_total)。';
COMMENT ON COLUMN data_asset.ads_event_overview.top_platform_json IS '平台分布TopN。ETL生成，JSON数组，元素包含 label 和 value。';
COMMENT ON COLUMN data_asset.ads_event_overview.top_author_json IS '作者分布TopN。ETL生成，JSON数组，元素包含 label 和 value。';
COMMENT ON COLUMN data_asset.ads_event_overview.data_lineage_json IS '数据血缘。ETL生成，记录来源表和公式说明。';
COMMENT ON COLUMN data_asset.ads_event_overview.updated_time IS 'ADS更新时间。ETL生成。';

CREATE TABLE IF NOT EXISTS data_asset.ads_event_trend_daily (
  event_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  stat_date         DATE NOT NULL,
  content_cnt       BIGINT DEFAULT 0,
  comment_cnt       BIGINT DEFAULT 0,
  engagement_cnt    BIGINT DEFAULT 0,
  data_lineage_json JSONB,
  updated_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (event_id, stat_date)
);

COMMENT ON TABLE data_asset.ads_event_trend_daily IS '事件日趋势 ADS 表。按事件和日期聚合内容数、评论数、互动量。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.event_id IS '事件ID。来自 rel_event_content 或 dwd_content.event_id。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.stat_date IS '统计日期。ETL生成，取内容发布时间或评论发布时间的日期。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.content_cnt IS '当日内容数。ETL生成，公式：当日发布内容数。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.comment_cnt IS '当日评论数。ETL生成，公式：当日发布评论数。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.engagement_cnt IS '当日互动量。ETL生成，公式：当日内容互动量 + 可用的评论互动量。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.data_lineage_json IS '数据血缘。ETL生成，记录来源表和公式说明。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.updated_time IS 'ADS更新时间。ETL生成。';

CREATE TABLE IF NOT EXISTS data_asset.ads_event_content_rank (
  rank_id           VARCHAR(128) PRIMARY KEY,
  event_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  content_id        VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  rank_type         VARCHAR(64) NOT NULL,
  rank_no           INTEGER NOT NULL,
  platform          VARCHAR(64),
  title             TEXT,
  author_name       VARCHAR(255),
  is_kol            BOOLEAN DEFAULT FALSE,
  published_at      TIMESTAMP,
  engagement_total  BIGINT DEFAULT 0,
  comment_cnt       BIGINT DEFAULT 0,
  source_url        TEXT,
  data_lineage_json JSONB,
  updated_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.ads_event_content_rank IS '事件内容排行 ADS 表。用于展示事件下高互动内容、KOL内容、评论量高的内容。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.rank_id IS '排行记录ID。ETL生成，通常由 event_id + rank_type + content_id 生成。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.event_id IS '事件ID。来自 dwd_content.event_id。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.content_id IS '内容ID。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.rank_type IS '排行类型。ETL生成，如 engagement、comment、kol_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.rank_no IS '排名序号。ETL生成，从1开始。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.platform IS '平台。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.title IS '内容标题。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.author_name IS '作者名称。ETL通过 rel_author_content 关联 dwd_author 生成。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.is_kol IS '是否KOL内容。ETL通过 rel_author_content 关联 dwd_author.is_kol 生成。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.published_at IS '发布时间。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.engagement_total IS '综合互动量。来自 dwd_content.engagement_total。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.comment_cnt IS '平台显示评论数。来自 dwd_content.comment_cnt。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.source_url IS '原始链接。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.data_lineage_json IS '数据血缘。ETL生成，记录来源表和公式说明。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.updated_time IS 'ADS更新时间。ETL生成。';

-- =========================================================
-- META：导入和计算任务元数据
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.import_template (
  template_id          VARCHAR(64) PRIMARY KEY,
  source_key           VARCHAR(64) NOT NULL,
  source_name          VARCHAR(128) NOT NULL,
  file_name            VARCHAR(255) NOT NULL,
  file_format          VARCHAR(16) NOT NULL,
  target_table         VARCHAR(128) NOT NULL,
  description          TEXT,
  required_fields_json JSONB NOT NULL,
  optional_fields_json JSONB,
  download_path        TEXT NOT NULL,
  created_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.import_template IS '导入模板元数据表。记录每类上传模板的字段要求。';
COMMENT ON COLUMN data_asset.import_template.template_id IS '模板ID。系统维护，主键。';
COMMENT ON COLUMN data_asset.import_template.source_key IS '数据源类型编码。系统维护，如 event、content、author、comment。';
COMMENT ON COLUMN data_asset.import_template.source_name IS '数据源名称。系统维护，如事件数据、内容数据、作者数据、评论数据。';
COMMENT ON COLUMN data_asset.import_template.file_name IS '模板文件名。系统维护。';
COMMENT ON COLUMN data_asset.import_template.file_format IS '模板文件格式。系统维护，如 xlsx、csv。';
COMMENT ON COLUMN data_asset.import_template.target_table IS '目标落库表。系统维护，如 dwd_event、dwd_content、dwd_author、dwd_comment。';
COMMENT ON COLUMN data_asset.import_template.description IS '模板说明。系统维护。';
COMMENT ON COLUMN data_asset.import_template.required_fields_json IS '必填字段列表。系统维护，JSON数组。';
COMMENT ON COLUMN data_asset.import_template.optional_fields_json IS '可选字段列表。系统维护，JSON数组。';
COMMENT ON COLUMN data_asset.import_template.download_path IS '模板下载路径。系统维护。';
COMMENT ON COLUMN data_asset.import_template.created_time IS '模板记录创建时间。系统生成。';

CREATE TABLE IF NOT EXISTS data_asset.import_job (
  job_id        VARCHAR(64) PRIMARY KEY,
  source_key    VARCHAR(64) NOT NULL,
  template_id   VARCHAR(64) NOT NULL REFERENCES data_asset.import_template(template_id),
  file_name     VARCHAR(255) NOT NULL,
  file_format   VARCHAR(16) NOT NULL,
  operator      VARCHAR(128) NOT NULL,
  status        VARCHAR(32) NOT NULL,
  inserted_rows BIGINT DEFAULT 0,
  rejected_rows BIGINT DEFAULT 0,
  message       TEXT,
  created_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.import_job IS '导入任务记录表。记录每次上传文件的校验和入库结果。';
COMMENT ON COLUMN data_asset.import_job.job_id IS '导入任务ID。系统生成，主键。';
COMMENT ON COLUMN data_asset.import_job.source_key IS '数据源类型编码。来自导入请求，如 event、content、comment。';
COMMENT ON COLUMN data_asset.import_job.template_id IS '使用的模板ID。来自 import_template。';
COMMENT ON COLUMN data_asset.import_job.file_name IS '上传文件名。系统记录。';
COMMENT ON COLUMN data_asset.import_job.file_format IS '上传文件格式。系统记录，如 xlsx、csv。';
COMMENT ON COLUMN data_asset.import_job.operator IS '操作人。上传时填写或系统记录。';
COMMENT ON COLUMN data_asset.import_job.status IS '导入状态。系统生成，如 running、success、failed。';
COMMENT ON COLUMN data_asset.import_job.inserted_rows IS '成功入库行数。系统生成。';
COMMENT ON COLUMN data_asset.import_job.rejected_rows IS '拒绝入库行数。系统生成。';
COMMENT ON COLUMN data_asset.import_job.message IS '导入结果说明或错误信息。系统生成。';
COMMENT ON COLUMN data_asset.import_job.created_time IS '任务创建时间。系统生成。';
COMMENT ON COLUMN data_asset.import_job.updated_time IS '任务更新时间。系统生成。';

CREATE TABLE IF NOT EXISTS data_asset.calc_task (
  task_id            VARCHAR(64) PRIMARY KEY,
  task_name          VARCHAR(255) NOT NULL,
  task_group         VARCHAR(64) NOT NULL,
  task_desc          TEXT,
  script_path        TEXT NOT NULL,
  module_path        TEXT,
  entry_func         VARCHAR(64) NOT NULL,
  input_tables_json  JSONB NOT NULL,
  output_tables_json JSONB NOT NULL,
  run_mode           VARCHAR(32) NOT NULL,
  is_enabled         BOOLEAN DEFAULT TRUE,
  created_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.calc_task IS '计算任务元数据表。记录 ETL 作业定义。';
COMMENT ON COLUMN data_asset.calc_task.task_id IS '计算任务ID。系统维护，主键。';
COMMENT ON COLUMN data_asset.calc_task.task_name IS '计算任务名称。系统维护，用于页面展示。';
COMMENT ON COLUMN data_asset.calc_task.task_group IS '任务分组。系统维护，如 VOC看事件。';
COMMENT ON COLUMN data_asset.calc_task.task_desc IS '任务说明。系统维护。';
COMMENT ON COLUMN data_asset.calc_task.script_path IS '任务脚本路径。系统维护。';
COMMENT ON COLUMN data_asset.calc_task.module_path IS '任务模块路径。系统维护，用于 Python 动态加载。';
COMMENT ON COLUMN data_asset.calc_task.entry_func IS '任务入口函数。系统维护，通常为 run。';
COMMENT ON COLUMN data_asset.calc_task.input_tables_json IS '输入表列表。系统维护，JSON数组。';
COMMENT ON COLUMN data_asset.calc_task.output_tables_json IS '输出表列表。系统维护，JSON数组。';
COMMENT ON COLUMN data_asset.calc_task.run_mode IS '运行方式。系统维护，如 manual、schedule。';
COMMENT ON COLUMN data_asset.calc_task.is_enabled IS '是否启用。系统维护。';
COMMENT ON COLUMN data_asset.calc_task.created_time IS '任务定义创建时间。系统生成。';
COMMENT ON COLUMN data_asset.calc_task.updated_time IS '任务定义更新时间。系统生成。';

CREATE TABLE IF NOT EXISTS data_asset.calc_task_run (
  run_id         VARCHAR(64) PRIMARY KEY,
  task_id        VARCHAR(64) NOT NULL REFERENCES data_asset.calc_task(task_id),
  run_status     VARCHAR(32) NOT NULL,
  trigger_type   VARCHAR(32) NOT NULL,
  started_at     TIMESTAMP NOT NULL,
  finished_at    TIMESTAMP,
  duration_ms    INTEGER,
  processed_rows BIGINT DEFAULT 0,
  output_rows    BIGINT DEFAULT 0,
  error_message  TEXT,
  log_path       TEXT,
  created_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.calc_task_run IS '计算任务运行记录表。记录每次 ETL 执行结果。';
COMMENT ON COLUMN data_asset.calc_task_run.run_id IS '运行ID。系统生成，主键。';
COMMENT ON COLUMN data_asset.calc_task_run.task_id IS '计算任务ID。关联 calc_task.task_id。';
COMMENT ON COLUMN data_asset.calc_task_run.run_status IS '运行状态。系统生成，如 running、success、failed。';
COMMENT ON COLUMN data_asset.calc_task_run.trigger_type IS '触发方式。系统生成，如 manual、schedule。';
COMMENT ON COLUMN data_asset.calc_task_run.started_at IS '开始时间。系统生成。';
COMMENT ON COLUMN data_asset.calc_task_run.finished_at IS '结束时间。系统生成。';
COMMENT ON COLUMN data_asset.calc_task_run.duration_ms IS '运行耗时，单位毫秒。系统生成。';
COMMENT ON COLUMN data_asset.calc_task_run.processed_rows IS '处理输入行数。ETL返回。';
COMMENT ON COLUMN data_asset.calc_task_run.output_rows IS '输出结果行数。ETL返回。';
COMMENT ON COLUMN data_asset.calc_task_run.error_message IS '错误信息。失败时系统记录。';
COMMENT ON COLUMN data_asset.calc_task_run.log_path IS '日志路径。系统记录，可为空。';
COMMENT ON COLUMN data_asset.calc_task_run.created_time IS '运行记录创建时间。系统生成。';

-- =========================================================
-- Indexes
-- =========================================================

CREATE INDEX IF NOT EXISTS idx_dwd_content_event_id ON data_asset.dwd_content(event_id);
CREATE INDEX IF NOT EXISTS idx_dwd_content_published_at ON data_asset.dwd_content(published_at);
CREATE INDEX IF NOT EXISTS idx_dwd_author_platform_name ON data_asset.dwd_author(platform, author_name);
CREATE INDEX IF NOT EXISTS idx_dwd_comment_content_id ON data_asset.dwd_comment(content_id);
CREATE INDEX IF NOT EXISTS idx_dwd_comment_published_at ON data_asset.dwd_comment(published_at);
CREATE INDEX IF NOT EXISTS idx_rel_event_content_content_id ON data_asset.rel_event_content(content_id);
CREATE INDEX IF NOT EXISTS idx_rel_author_content_content_id ON data_asset.rel_author_content(content_id);
CREATE INDEX IF NOT EXISTS idx_ads_event_content_rank_event_type ON data_asset.ads_event_content_rank(event_id, rank_type);
