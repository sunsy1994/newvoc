-- AutoVOC 数据资产 Schema v1
-- 范围：第一阶段「VOC看事件」最小可落地数据链路。
-- 核心理解：
-- 1. 使用者上传 ODS 原始数据，不需要维护复杂系统ID。
-- 2. 导入/标准化 ETL 负责字段清洗、ID生成、自然键去重、upsert、拆表和关系生成。
-- 3. DWD/REL 是系统产出的标准明细和关系层。
-- 4. ADS 是聚合 ETL 产出的页面指标层。
-- 5. 第一版不包含用户旅程、竞品、标签事实、订单/成交/复购等后续能力。

CREATE SCHEMA IF NOT EXISTS data_asset;

COMMENT ON SCHEMA data_asset IS 'AutoVOC 数据资产 schema，第一版聚焦 VOC 看事件。';

-- =========================================================
-- ODS：原始上传层
-- 说明：这些表保留使用者上传的原始数据形态。字段尽量贴近Excel。
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.ods_event_upload (
  ods_row_id       BIGSERIAL PRIMARY KEY,
  ingest_batch_id  VARCHAR(64) NOT NULL,
  source_file_name VARCHAR(255),
  raw_row_no       INTEGER,
  raw_event_id     VARCHAR(64),
  event_name       VARCHAR(255) NOT NULL,
  event_type       VARCHAR(64) NOT NULL,
  brand_name       VARCHAR(128),
  model_name       VARCHAR(128),
  start_time       TIMESTAMP,
  end_time         TIMESTAMP,
  event_status     VARCHAR(32) NOT NULL,
  keyword_list     TEXT,
  event_desc       TEXT,
  raw_payload_json JSONB,
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.ods_event_upload IS 'ODS事件上传表。保留使用者上传的事件原始数据，供标准化ETL生成 dwd_event。';
COMMENT ON COLUMN data_asset.ods_event_upload.ods_row_id IS 'ODS行ID。系统生成，仅用于追溯原始上传行。';
COMMENT ON COLUMN data_asset.ods_event_upload.ingest_batch_id IS '导入批次ID。系统生成，标识这行数据来自哪一次上传。';
COMMENT ON COLUMN data_asset.ods_event_upload.source_file_name IS '来源文件名。系统记录，便于追溯。';
COMMENT ON COLUMN data_asset.ods_event_upload.raw_row_no IS '原始文件行号。系统记录，便于定位错误行。';
COMMENT ON COLUMN data_asset.ods_event_upload.raw_event_id IS '原始事件ID。使用者建议上传；内容上传可用同一ID归属事件。为空时标准化ETL会按事件名称等自然字段生成系统 event_id。';
COMMENT ON COLUMN data_asset.ods_event_upload.event_name IS '事件名称。使用者上传，必填。';
COMMENT ON COLUMN data_asset.ods_event_upload.event_type IS '事件类型。使用者上传，必填；第一版枚举：新品上市、品牌传播、价格权益、产品质量、服务体验、事故舆情、竞品对比、用户口碑、其他。';
COMMENT ON COLUMN data_asset.ods_event_upload.brand_name IS '品牌名称。使用者上传，可为空。';
COMMENT ON COLUMN data_asset.ods_event_upload.model_name IS '车型名称。使用者上传，可为空。';
COMMENT ON COLUMN data_asset.ods_event_upload.start_time IS '事件开始时间。使用者上传，可为空但建议填写。';
COMMENT ON COLUMN data_asset.ods_event_upload.end_time IS '事件结束时间。使用者上传，可为空。';
COMMENT ON COLUMN data_asset.ods_event_upload.event_status IS '事件状态。使用者上传，必填；第一版枚举：进行中、已结束、归档。';
COMMENT ON COLUMN data_asset.ods_event_upload.keyword_list IS '事件关键词。使用者上传，可为空，多个关键词可用竖线、逗号或顿号分隔。';
COMMENT ON COLUMN data_asset.ods_event_upload.event_desc IS '事件描述。使用者上传，可为空。';
COMMENT ON COLUMN data_asset.ods_event_upload.raw_payload_json IS '原始行JSON。系统可选记录，用于保留上传文件中的完整原始字段。';
COMMENT ON COLUMN data_asset.ods_event_upload.created_time IS 'ODS入库时间。系统生成。';

CREATE TABLE IF NOT EXISTS data_asset.ods_content_upload (
  ods_row_id       BIGSERIAL PRIMARY KEY,
  ingest_batch_id  VARCHAR(64) NOT NULL,
  source_file_name VARCHAR(255),
  raw_row_no       INTEGER,
  raw_content_id   VARCHAR(64),
  raw_event_id     VARCHAR(64),
  event_id         VARCHAR(64),
  platform         VARCHAR(64) NOT NULL,
  source_url       TEXT NOT NULL,
  title            TEXT NOT NULL,
  content_text     TEXT,
  content_type     VARCHAR(64),
  media_form       VARCHAR(64),
  published_at     TIMESTAMP NOT NULL,
  like_cnt         BIGINT,
  comment_cnt      BIGINT,
  share_cnt        BIGINT,
  favorite_cnt     BIGINT,
  view_cnt         BIGINT,
  raw_author_id    VARCHAR(64),
  author_name      VARCHAR(255) NOT NULL,
  author_home_url  TEXT,
  author_type      VARCHAR(64),
  is_kol           BOOLEAN,
  fans_cnt         BIGINT,
  author_desc      TEXT,
  raw_payload_json JSONB,
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.ods_content_upload IS 'ODS内容上传表。使用者上传帖子/视频/文章时可以同时带作者信息；标准化ETL会拆成 dwd_content、dwd_author 和关系表。';
COMMENT ON COLUMN data_asset.ods_content_upload.ods_row_id IS 'ODS行ID。系统生成，仅用于追溯原始上传行。';
COMMENT ON COLUMN data_asset.ods_content_upload.ingest_batch_id IS '导入批次ID。系统生成，标识这行数据来自哪一次上传。';
COMMENT ON COLUMN data_asset.ods_content_upload.source_file_name IS '来源文件名。系统记录，便于追溯。';
COMMENT ON COLUMN data_asset.ods_content_upload.raw_row_no IS '原始文件行号。系统记录，便于定位错误行。';
COMMENT ON COLUMN data_asset.ods_content_upload.raw_content_id IS '原始内容ID。使用者可传；为空时标准化ETL会基于 platform + source_url 生成系统 content_id。';
COMMENT ON COLUMN data_asset.ods_content_upload.raw_event_id IS '原始事件ID。使用者上传，建议必填；填写事件上传模板中的 raw_event_id，用于把内容归属到事件。';
COMMENT ON COLUMN data_asset.ods_content_upload.event_id IS '标准事件ID。系统可选写入或高级使用者填写；普通上传建议填写 raw_event_id，不要求知道系统 event_id。';
COMMENT ON COLUMN data_asset.ods_content_upload.platform IS '平台。使用者上传，必填，如抖音、快手、小红书、微博、B站、懂车帝等。';
COMMENT ON COLUMN data_asset.ods_content_upload.source_url IS '原始链接。使用者上传，必填；标准化ETL优先用 platform + source_url 做内容去重。';
COMMENT ON COLUMN data_asset.ods_content_upload.title IS '内容标题。使用者上传，必填；如果原平台无标题，可用正文前若干字生成。';
COMMENT ON COLUMN data_asset.ods_content_upload.content_text IS '内容正文。使用者上传，可为空。';
COMMENT ON COLUMN data_asset.ods_content_upload.content_type IS '内容类型。使用者上传，可为空；第一版枚举：官方内容、媒体内容、达人内容、用户内容、经销商内容。';
COMMENT ON COLUMN data_asset.ods_content_upload.media_form IS '媒介形态。使用者上传，可为空；第一版枚举：视频、图文、直播、其他。';
COMMENT ON COLUMN data_asset.ods_content_upload.published_at IS '发布时间。使用者上传，必填。';
COMMENT ON COLUMN data_asset.ods_content_upload.like_cnt IS '点赞数。使用者上传，可为空；标准化ETL为空时置0。';
COMMENT ON COLUMN data_asset.ods_content_upload.comment_cnt IS '平台显示评论数。使用者上传，可为空；标准化ETL为空时置0。';
COMMENT ON COLUMN data_asset.ods_content_upload.share_cnt IS '分享/转发数。使用者上传，可为空；标准化ETL为空时置0。';
COMMENT ON COLUMN data_asset.ods_content_upload.favorite_cnt IS '收藏数。使用者上传，可为空；标准化ETL为空时置0。';
COMMENT ON COLUMN data_asset.ods_content_upload.view_cnt IS '播放/阅读/浏览数。使用者上传，可为空；不同平台口径可能不同。';
COMMENT ON COLUMN data_asset.ods_content_upload.raw_author_id IS '原始作者ID。使用者可传；为空时标准化ETL会基于 platform + author_home_url 或 platform + author_name 生成系统 author_id。';
COMMENT ON COLUMN data_asset.ods_content_upload.author_name IS '作者名称。使用者上传，必填。';
COMMENT ON COLUMN data_asset.ods_content_upload.author_home_url IS '作者主页链接。使用者上传，可为空；有主页链接时优先用于作者去重。';
COMMENT ON COLUMN data_asset.ods_content_upload.author_type IS '作者类型。使用者上传，可为空；第一版枚举：官方号、媒体号、达人、经销商、普通用户、其他。';
COMMENT ON COLUMN data_asset.ods_content_upload.is_kol IS '是否KOL。使用者可传；这是作者资产属性，不属于帖子本身。';
COMMENT ON COLUMN data_asset.ods_content_upload.fans_cnt IS '作者粉丝数。使用者可传；作为作者粉丝快照进入 dwd_author。';
COMMENT ON COLUMN data_asset.ods_content_upload.author_desc IS '作者简介。使用者上传，可为空。';
COMMENT ON COLUMN data_asset.ods_content_upload.raw_payload_json IS '原始行JSON。系统可选记录，用于保留上传文件中的完整原始字段。';
COMMENT ON COLUMN data_asset.ods_content_upload.created_time IS 'ODS入库时间。系统生成。';

CREATE TABLE IF NOT EXISTS data_asset.ods_comment_upload (
  ods_row_id          BIGSERIAL PRIMARY KEY,
  ingest_batch_id     VARCHAR(64) NOT NULL,
  source_file_name    VARCHAR(255),
  raw_row_no          INTEGER,
  raw_comment_id      VARCHAR(64),
  content_id          VARCHAR(64),
  content_source_url  TEXT,
  platform            VARCHAR(64),
  location            VARCHAR(128),
  comment_author_id   VARCHAR(64),
  comment_author_name VARCHAR(255) NOT NULL,
  parent_comment_id   VARCHAR(64),
  comment_text        TEXT NOT NULL,
  published_at        TIMESTAMP NOT NULL,
  like_cnt            BIGINT,
  reply_cnt           BIGINT,
  comment_label_json  JSONB,
  raw_payload_json    JSONB,
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE data_asset.ods_comment_upload
  ADD COLUMN IF NOT EXISTS comment_label_json JSONB;

COMMENT ON TABLE data_asset.ods_comment_upload IS 'ODS评论上传表。保留使用者上传的评论原始数据，供标准化ETL生成 dwd_comment。';
COMMENT ON COLUMN data_asset.ods_comment_upload.ods_row_id IS 'ODS行ID。系统生成，仅用于追溯原始上传行。';
COMMENT ON COLUMN data_asset.ods_comment_upload.ingest_batch_id IS '导入批次ID。系统生成，标识这行数据来自哪一次上传。';
COMMENT ON COLUMN data_asset.ods_comment_upload.source_file_name IS '来源文件名。系统记录，便于追溯。';
COMMENT ON COLUMN data_asset.ods_comment_upload.raw_row_no IS '原始文件行号。系统记录，便于定位错误行。';
COMMENT ON COLUMN data_asset.ods_comment_upload.raw_comment_id IS '原始评论ID。使用者可传；为空时标准化ETL会基于 content_id + 作者昵称 + 正文 + 时间 生成系统 comment_id。';
COMMENT ON COLUMN data_asset.ods_comment_upload.content_id IS '所属内容ID。使用者可传；可填写系统 content_id 或内容上传表中的 raw_content_id。为空时标准化ETL优先用 content_source_url 匹配内容。';
COMMENT ON COLUMN data_asset.ods_comment_upload.content_source_url IS '所属内容原始链接。使用者上传，可为空但建议填写；标准化ETL可用 platform + content_source_url 匹配 dwd_content。';
COMMENT ON COLUMN data_asset.ods_comment_upload.platform IS '评论所在平台。使用者上传，可为空；为空时标准化ETL可从内容表继承。';
COMMENT ON COLUMN data_asset.ods_comment_upload.location IS '位置。使用者上传，可为空；表示平台显示的位置、IP属地或城市文本，不代表真实地址。';
COMMENT ON COLUMN data_asset.ods_comment_upload.comment_author_id IS '评论作者ID。使用者上传，可为空；第一版不用于跨平台识别用户。';
COMMENT ON COLUMN data_asset.ods_comment_upload.comment_author_name IS '评论作者昵称。使用者上传，必填。';
COMMENT ON COLUMN data_asset.ods_comment_upload.parent_comment_id IS '父评论ID。使用者上传，可为空。';
COMMENT ON COLUMN data_asset.ods_comment_upload.comment_text IS '评论正文。使用者上传，必填。';
COMMENT ON COLUMN data_asset.ods_comment_upload.published_at IS '评论发布时间。使用者上传，必填。';
COMMENT ON COLUMN data_asset.ods_comment_upload.like_cnt IS '评论点赞数。使用者上传，可为空；标准化ETL为空时置0。';
COMMENT ON COLUMN data_asset.ods_comment_upload.reply_cnt IS '评论回复数。使用者上传，可为空；标准化ETL为空时置0。';
COMMENT ON COLUMN data_asset.ods_comment_upload.comment_label_json IS '评论打标结果JSON。使用者线下打标后上传，可为空；用于后续计算有效互动率、情感、意图、关注点和购买信号。';
COMMENT ON COLUMN data_asset.ods_comment_upload.raw_payload_json IS '原始行JSON。系统可选记录，用于保留上传文件中的完整原始字段。';
COMMENT ON COLUMN data_asset.ods_comment_upload.created_time IS 'ODS入库时间。系统生成。';

-- =========================================================
-- DWD：标准明细层
-- 说明：这些表由标准化ETL从ODS生成，字段规范、ID稳定、可去重更新。
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.dwd_event (
  event_id        VARCHAR(64) PRIMARY KEY,
  event_key       VARCHAR(128) NOT NULL UNIQUE,
  event_name      VARCHAR(255) NOT NULL,
  event_type      VARCHAR(64) NOT NULL,
  brand_name      VARCHAR(128),
  model_name      VARCHAR(128),
  start_time      TIMESTAMP,
  end_time        TIMESTAMP,
  event_status    VARCHAR(32) NOT NULL,
  keyword_list    TEXT,
  event_desc      TEXT,
  ingest_batch_id VARCHAR(64),
  raw_source_key  VARCHAR(64) DEFAULT 'event_upload',
  created_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.dwd_event IS '事件标准明细表。由 ods_event_upload 标准化生成，一个事件是一条 VOC 分析主线的锚点。';
COMMENT ON COLUMN data_asset.dwd_event.event_id IS '事件ID。标准化ETL生成或沿用上传的 raw_event_id，主键，稳定不重复。';
COMMENT ON COLUMN data_asset.dwd_event.event_key IS '事件自然键。标准化ETL生成，用于去重和upsert；优先使用 raw_event_id，否则对事件名称+品牌+车型+开始时间做标准化后生成哈希。';
COMMENT ON COLUMN data_asset.dwd_event.event_name IS '事件名称。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_event.event_type IS '事件类型。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_event.brand_name IS '品牌名称。来自ODS，可为空。';
COMMENT ON COLUMN data_asset.dwd_event.model_name IS '车型名称。来自ODS，可为空。';
COMMENT ON COLUMN data_asset.dwd_event.start_time IS '事件开始时间。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_event.end_time IS '事件结束时间。来自ODS，可为空。';
COMMENT ON COLUMN data_asset.dwd_event.event_status IS '事件状态。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_event.keyword_list IS '事件关键词。来自ODS，ETL可做分隔符标准化。';
COMMENT ON COLUMN data_asset.dwd_event.event_desc IS '事件描述。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_event.ingest_batch_id IS '最近一次写入该记录的导入批次ID。标准化ETL写入。';
COMMENT ON COLUMN data_asset.dwd_event.raw_source_key IS '原始来源类型。标准化ETL写入，第一版默认为 event_upload。';
COMMENT ON COLUMN data_asset.dwd_event.created_time IS '标准记录首次创建时间。系统生成。';
COMMENT ON COLUMN data_asset.dwd_event.updated_time IS '标准记录最近更新时间。标准化ETL upsert 时更新。';

CREATE TABLE IF NOT EXISTS data_asset.dwd_author (
  author_id       VARCHAR(64) PRIMARY KEY,
  author_key      VARCHAR(128) NOT NULL UNIQUE,
  platform        VARCHAR(64) NOT NULL,
  author_name     VARCHAR(255) NOT NULL,
  author_home_url TEXT,
  author_type     VARCHAR(64),
  is_kol          BOOLEAN DEFAULT FALSE,
  fans_cnt        BIGINT DEFAULT 0,
  author_desc     TEXT,
  ingest_batch_id VARCHAR(64),
  raw_source_key  VARCHAR(64) DEFAULT 'content_upload',
  created_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.dwd_author IS '作者标准明细表。由 ods_content_upload 中的作者字段标准化生成，存储媒体号、达人号、经销商号等账号资产。';
COMMENT ON COLUMN data_asset.dwd_author.author_id IS '作者ID。标准化ETL生成或沿用上传的 raw_author_id，主键，稳定不重复。';
COMMENT ON COLUMN data_asset.dwd_author.author_key IS '作者自然键。标准化ETL生成，用于去重和upsert；优先对 platform+author_home_url 生成哈希，其次对 platform+author_name 生成哈希。';
COMMENT ON COLUMN data_asset.dwd_author.platform IS '作者所在平台。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_author.author_name IS '作者名称。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_author.author_home_url IS '作者主页链接。来自ODS，可为空。';
COMMENT ON COLUMN data_asset.dwd_author.author_type IS '作者类型。来自ODS，可为空；第一版枚举：官方号、媒体号、达人、经销商、普通用户、其他。';
COMMENT ON COLUMN data_asset.dwd_author.is_kol IS '是否KOL。来自ODS或作者资产维护；这是作者属性，不属于帖子本身。';
COMMENT ON COLUMN data_asset.dwd_author.fans_cnt IS '作者粉丝数。来自ODS或作者资产维护；upsert 时更新为最新快照。';
COMMENT ON COLUMN data_asset.dwd_author.author_desc IS '作者简介。来自ODS，可为空。';
COMMENT ON COLUMN data_asset.dwd_author.ingest_batch_id IS '最近一次写入该记录的导入批次ID。标准化ETL写入。';
COMMENT ON COLUMN data_asset.dwd_author.raw_source_key IS '原始来源类型。标准化ETL写入，第一版默认为 content_upload。';
COMMENT ON COLUMN data_asset.dwd_author.created_time IS '标准记录首次创建时间。系统生成。';
COMMENT ON COLUMN data_asset.dwd_author.updated_time IS '标准记录最近更新时间。标准化ETL upsert 时更新。';

CREATE TABLE IF NOT EXISTS data_asset.dwd_content (
  content_id       VARCHAR(64) PRIMARY KEY,
  content_key      VARCHAR(128) NOT NULL UNIQUE,
  event_id         VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  author_id        VARCHAR(64) REFERENCES data_asset.dwd_author(author_id),
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
  ingest_batch_id  VARCHAR(64),
  raw_source_key   VARCHAR(64) DEFAULT 'content_upload',
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.dwd_content IS '内容标准明细表。由 ods_content_upload 标准化生成，只描述帖子/视频/文章本身；作者资产通过 author_id 关联 dwd_author。';
COMMENT ON COLUMN data_asset.dwd_content.content_id IS '内容ID。标准化ETL生成或沿用上传的 raw_content_id，主键，稳定不重复。';
COMMENT ON COLUMN data_asset.dwd_content.content_key IS '内容自然键。标准化ETL生成，用于去重和upsert；第一版对 platform + source_url 做标准化后生成哈希。';
COMMENT ON COLUMN data_asset.dwd_content.event_id IS '所属事件ID。标准化ETL根据 ODS 的 raw_event_id 或 event_id 匹配生成，关联 dwd_event.event_id。';
COMMENT ON COLUMN data_asset.dwd_content.author_id IS '作者ID。标准化ETL根据ODS作者字段生成并关联 dwd_author.author_id；可为空但建议生成。';
COMMENT ON COLUMN data_asset.dwd_content.platform IS '平台。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_content.source_url IS '原始链接。来自ODS，是内容去重的核心自然字段。';
COMMENT ON COLUMN data_asset.dwd_content.title IS '内容标题。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_content.content_text IS '内容正文。来自ODS，可为空。';
COMMENT ON COLUMN data_asset.dwd_content.content_type IS '内容类型。来自ODS，可为空；第一版枚举：官方内容、媒体内容、达人内容、用户内容、经销商内容。';
COMMENT ON COLUMN data_asset.dwd_content.media_form IS '媒介形态。来自ODS，可为空；第一版枚举：视频、图文、直播、其他。';
COMMENT ON COLUMN data_asset.dwd_content.published_at IS '发布时间。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_content.like_cnt IS '点赞数。来自ODS，upsert 时可更新为最新值。';
COMMENT ON COLUMN data_asset.dwd_content.comment_cnt IS '平台显示评论数。来自ODS，upsert 时可更新为最新值；不等同于导入评论明细数。';
COMMENT ON COLUMN data_asset.dwd_content.share_cnt IS '分享/转发数。来自ODS，upsert 时可更新为最新值。';
COMMENT ON COLUMN data_asset.dwd_content.favorite_cnt IS '收藏数。来自ODS，upsert 时可更新为最新值。';
COMMENT ON COLUMN data_asset.dwd_content.view_cnt IS '播放/阅读/浏览数。来自ODS，upsert 时可更新为最新值。';
COMMENT ON COLUMN data_asset.dwd_content.engagement_total IS '综合互动量。系统生成，公式：点赞数 + 评论数 + 分享数 + 收藏数。';
COMMENT ON COLUMN data_asset.dwd_content.ingest_batch_id IS '最近一次写入该记录的导入批次ID。标准化ETL写入。';
COMMENT ON COLUMN data_asset.dwd_content.raw_source_key IS '原始来源类型。标准化ETL写入，第一版默认为 content_upload。';
COMMENT ON COLUMN data_asset.dwd_content.created_time IS '标准记录首次创建时间。系统生成。';
COMMENT ON COLUMN data_asset.dwd_content.updated_time IS '标准记录最近更新时间。标准化ETL upsert 时更新。';

CREATE TABLE IF NOT EXISTS data_asset.dwd_comment (
  comment_id          VARCHAR(64) PRIMARY KEY,
  comment_key         VARCHAR(128) NOT NULL UNIQUE,
  content_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  platform            VARCHAR(64),
  location            VARCHAR(128),
  comment_author_id   VARCHAR(64),
  comment_author_name VARCHAR(255) NOT NULL,
  parent_comment_id   VARCHAR(64),
  comment_text        TEXT NOT NULL,
  published_at        TIMESTAMP NOT NULL,
  like_cnt            BIGINT DEFAULT 0,
  reply_cnt           BIGINT DEFAULT 0,
  interaction_cnt     BIGINT GENERATED ALWAYS AS (like_cnt + reply_cnt) STORED,
  comment_label_json  JSONB,
  ingest_batch_id     VARCHAR(64),
  raw_source_key      VARCHAR(64) DEFAULT 'comment_upload',
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE data_asset.dwd_comment
  ADD COLUMN IF NOT EXISTS comment_label_json JSONB;

COMMENT ON TABLE data_asset.dwd_comment IS '评论标准明细表。由 ods_comment_upload 标准化生成，存储公网评论原文，是 VOC 看事件的用户声音来源。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_id IS '评论ID。标准化ETL生成或沿用上传的 raw_comment_id，主键，稳定不重复。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_key IS '评论自然键。标准化ETL生成，用于去重和upsert；第一版对 content_id + 评论作者昵称 + 评论正文 + 发布时间 做标准化后生成哈希。';
COMMENT ON COLUMN data_asset.dwd_comment.content_id IS '所属内容ID。来自ODS或标准化ETL匹配结果，关联 dwd_content.content_id。';
COMMENT ON COLUMN data_asset.dwd_comment.platform IS '评论所在平台。来自ODS；为空时标准化ETL可从内容表继承。';
COMMENT ON COLUMN data_asset.dwd_comment.location IS '位置。来自ODS，表示平台显示的位置、IP属地或城市文本，用于事件评论位置分布统计，不代表真实地址。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_author_id IS '评论作者ID。来自ODS，可为空；第一版不用于跨平台识别用户。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_author_name IS '评论作者昵称。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_comment.parent_comment_id IS '父评论ID。来自ODS，可为空。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_text IS '评论正文。来自ODS，VOC 分析的核心原文。';
COMMENT ON COLUMN data_asset.dwd_comment.published_at IS '评论发布时间。来自ODS。';
COMMENT ON COLUMN data_asset.dwd_comment.like_cnt IS '评论点赞数。来自ODS，upsert 时可更新为最新值。';
COMMENT ON COLUMN data_asset.dwd_comment.reply_cnt IS '评论回复数。来自ODS，upsert 时可更新为最新值。';
COMMENT ON COLUMN data_asset.dwd_comment.interaction_cnt IS '评论互动量。系统生成，公式：评论点赞数 + 评论回复数。';
COMMENT ON COLUMN data_asset.dwd_comment.comment_label_json IS '评论打标结果JSON。来自ODS，用于沉淀评论级标签，字段建议包含 is_vehicle_related、comment_sentiment、comment_intent、mentioned_aspect、purchase_signal、comment_label_reason。';
COMMENT ON COLUMN data_asset.dwd_comment.ingest_batch_id IS '最近一次写入该记录的导入批次ID。标准化ETL写入。';
COMMENT ON COLUMN data_asset.dwd_comment.raw_source_key IS '原始来源类型。标准化ETL写入，第一版默认为 comment_upload。';
COMMENT ON COLUMN data_asset.dwd_comment.created_time IS '标准记录首次创建时间。系统生成。';
COMMENT ON COLUMN data_asset.dwd_comment.updated_time IS '标准记录最近更新时间。标准化ETL upsert 时更新。';

-- =========================================================
-- REL：关系层
-- 说明：这些表由标准化ETL根据DWD表自动生成。
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

COMMENT ON TABLE data_asset.rel_event_content IS '事件-内容关系表。由标准化ETL根据 dwd_content.event_id 自动生成，表示哪些内容属于哪个事件。';
COMMENT ON COLUMN data_asset.rel_event_content.event_id IS '事件ID，关联 dwd_event.event_id。';
COMMENT ON COLUMN data_asset.rel_event_content.content_id IS '内容ID，关联 dwd_content.content_id。';
COMMENT ON COLUMN data_asset.rel_event_content.match_type IS '匹配方式。第一版固定为 manual，表示使用者上传内容时已明确 raw_event_id 或 event_id。';
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

COMMENT ON TABLE data_asset.rel_author_content IS '作者-内容关系表。由标准化ETL根据 dwd_content.author_id 自动生成，表示哪个作者发布了哪条内容。';
COMMENT ON COLUMN data_asset.rel_author_content.author_id IS '作者ID，关联 dwd_author.author_id。';
COMMENT ON COLUMN data_asset.rel_author_content.content_id IS '内容ID，关联 dwd_content.content_id。';
COMMENT ON COLUMN data_asset.rel_author_content.platform IS '平台。来自 dwd_content.platform，用于辅助查询。';
COMMENT ON COLUMN data_asset.rel_author_content.published_at IS '内容发布时间。来自 dwd_content.published_at，便于按作者追踪内容时间线。';
COMMENT ON COLUMN data_asset.rel_author_content.created_time IS '关系创建时间。系统生成。';

-- =========================================================
-- ADS：应用汇总层
-- 说明：这些表由聚合ETL生成，前端页面只读ADS，不直接拼DWD。
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

COMMENT ON TABLE data_asset.ads_event_overview IS '事件总览ADS表。由聚合ETL从DWD/REL聚合生成，供VOC看事件页面使用。';
COMMENT ON COLUMN data_asset.ads_event_overview.event_id IS '事件ID。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.event_name IS '事件名称。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.event_type IS '事件类型。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.brand_name IS '品牌名称。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.model_name IS '车型名称。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.start_time IS '事件开始时间。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.end_time IS '事件结束时间。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.event_status IS '事件状态。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_overview.platform_list IS '平台列表。聚合ETL生成，事件相关内容覆盖的平台去重列表。';
COMMENT ON COLUMN data_asset.ads_event_overview.content_cnt IS '内容数。聚合ETL生成，公式：count(distinct content_id)。';
COMMENT ON COLUMN data_asset.ads_event_overview.comment_cnt IS '评论明细数。聚合ETL生成，公式：count(distinct comment_id)。';
COMMENT ON COLUMN data_asset.ads_event_overview.author_cnt IS '作者数。聚合ETL生成，公式：基于 rel_author_content count(distinct author_id)。';
COMMENT ON COLUMN data_asset.ads_event_overview.kol_content_cnt IS 'KOL内容数。聚合ETL生成，公式：内容关联作者中 dwd_author.is_kol=true 的内容数。';
COMMENT ON COLUMN data_asset.ads_event_overview.total_engagement IS '总互动量。聚合ETL生成，公式：sum(dwd_content.engagement_total)。';
COMMENT ON COLUMN data_asset.ads_event_overview.top_platform_json IS '平台分布TopN。聚合ETL生成，JSON数组，元素包含 label 和 value。';
COMMENT ON COLUMN data_asset.ads_event_overview.top_author_json IS '作者分布TopN。聚合ETL生成，JSON数组，元素包含 label 和 value。';
COMMENT ON COLUMN data_asset.ads_event_overview.data_lineage_json IS '数据血缘。聚合ETL生成，记录来源表和公式说明。';
COMMENT ON COLUMN data_asset.ads_event_overview.updated_time IS 'ADS更新时间。聚合ETL生成。';

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

COMMENT ON TABLE data_asset.ads_event_trend_daily IS '事件日趋势ADS表。按事件和日期聚合内容数、评论数、互动量。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.event_id IS '事件ID。来自 dwd_event。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.stat_date IS '统计日期。聚合ETL生成，取内容发布时间或评论发布时间的日期。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.content_cnt IS '当日内容数。聚合ETL生成，公式：当日发布内容数。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.comment_cnt IS '当日评论数。聚合ETL生成，公式：当日发布评论数。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.engagement_cnt IS '当日互动量。聚合ETL生成，公式：当日内容互动量 + 可用的评论互动量。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.data_lineage_json IS '数据血缘。聚合ETL生成，记录来源表和公式说明。';
COMMENT ON COLUMN data_asset.ads_event_trend_daily.updated_time IS 'ADS更新时间。聚合ETL生成。';

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

COMMENT ON TABLE data_asset.ads_event_content_rank IS '事件内容排行ADS表。用于展示事件下高互动内容、KOL内容、评论量高的内容。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.rank_id IS '排行记录ID。聚合ETL生成，通常由 event_id + rank_type + content_id 生成。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.event_id IS '事件ID。来自 dwd_content.event_id。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.content_id IS '内容ID。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.rank_type IS '排行类型。聚合ETL生成，如 engagement、comment、kol_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.rank_no IS '排名序号。聚合ETL生成，从1开始。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.platform IS '平台。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.title IS '内容标题。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.author_name IS '作者名称。聚合ETL通过 dwd_content.author_id 关联 dwd_author 生成。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.is_kol IS '是否KOL内容。聚合ETL通过 dwd_content.author_id 关联 dwd_author.is_kol 生成。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.published_at IS '发布时间。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.engagement_total IS '综合互动量。来自 dwd_content.engagement_total。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.comment_cnt IS '平台显示评论数。来自 dwd_content.comment_cnt。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.source_url IS '原始链接。来自 dwd_content。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.data_lineage_json IS '数据血缘。聚合ETL生成，记录来源表和公式说明。';
COMMENT ON COLUMN data_asset.ads_event_content_rank.updated_time IS 'ADS更新时间。聚合ETL生成。';

CREATE TABLE IF NOT EXISTS data_asset.ads_event_location_distribution (
  event_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  location          VARCHAR(128) NOT NULL,
  comment_cnt       BIGINT DEFAULT 0,
  data_lineage_json JSONB,
  updated_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (event_id, location)
);

COMMENT ON TABLE data_asset.ads_event_location_distribution IS '事件评论位置分布ADS表。按事件和评论位置统计评论明细数量。';
COMMENT ON COLUMN data_asset.ads_event_location_distribution.event_id IS '事件ID。聚合ETL通过 dwd_comment.content_id 关联 dwd_content.event_id 得到。';
COMMENT ON COLUMN data_asset.ads_event_location_distribution.location IS '位置。来自 dwd_comment.location，表示平台显示的位置、IP属地或城市文本。';
COMMENT ON COLUMN data_asset.ads_event_location_distribution.comment_cnt IS '评论明细数。聚合ETL生成，公式：按 event_id + location 统计 count(distinct comment_id)。';
COMMENT ON COLUMN data_asset.ads_event_location_distribution.data_lineage_json IS '数据血缘。聚合ETL生成，记录来源表和公式说明。';
COMMENT ON COLUMN data_asset.ads_event_location_distribution.updated_time IS 'ADS更新时间。聚合ETL生成。';

CREATE TABLE IF NOT EXISTS data_asset.rejected_content (
  batch_id     VARCHAR(64) NOT NULL,
  row_no       INTEGER NOT NULL,
  reason       TEXT,
  payload_json JSONB,
  created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (batch_id, row_no)
);

COMMENT ON TABLE data_asset.rejected_content IS '内容拒绝行表。记录标准化ETL未能进入 dwd_content 的原始行和原因。';
COMMENT ON COLUMN data_asset.rejected_content.batch_id IS '导入批次ID。来自工作台任务批次。';
COMMENT ON COLUMN data_asset.rejected_content.row_no IS '拒绝行序号。系统生成，从1开始。';
COMMENT ON COLUMN data_asset.rejected_content.reason IS '拒绝原因。标准化ETL生成。';
COMMENT ON COLUMN data_asset.rejected_content.payload_json IS '拒绝行原始数据JSON。系统生成，用于排错。';
COMMENT ON COLUMN data_asset.rejected_content.created_time IS '记录创建时间。系统生成。';

CREATE TABLE IF NOT EXISTS data_asset.rejected_comment (
  batch_id     VARCHAR(64) NOT NULL,
  row_no       INTEGER NOT NULL,
  reason       TEXT,
  payload_json JSONB,
  created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (batch_id, row_no)
);

COMMENT ON TABLE data_asset.rejected_comment IS '评论拒绝行表。记录标准化ETL未能进入 dwd_comment 的原始行和原因。';
COMMENT ON COLUMN data_asset.rejected_comment.batch_id IS '导入批次ID。来自工作台任务批次。';
COMMENT ON COLUMN data_asset.rejected_comment.row_no IS '拒绝行序号。系统生成，从1开始。';
COMMENT ON COLUMN data_asset.rejected_comment.reason IS '拒绝原因。标准化ETL生成。';
COMMENT ON COLUMN data_asset.rejected_comment.payload_json IS '拒绝行原始数据JSON。系统生成，用于排错。';
COMMENT ON COLUMN data_asset.rejected_comment.created_time IS '记录创建时间。系统生成。';

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
COMMENT ON COLUMN data_asset.import_template.source_key IS '数据源类型编码。系统维护，如 event_upload、content_upload、comment_upload。';
COMMENT ON COLUMN data_asset.import_template.source_name IS '数据源名称。系统维护，如事件上传、内容上传、评论上传。';
COMMENT ON COLUMN data_asset.import_template.file_name IS '模板文件名。系统维护。';
COMMENT ON COLUMN data_asset.import_template.file_format IS '模板文件格式。系统维护，如 xlsx、csv。';
COMMENT ON COLUMN data_asset.import_template.target_table IS '目标ODS表。系统维护，如 ods_event_upload、ods_content_upload、ods_comment_upload。';
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

COMMENT ON TABLE data_asset.import_job IS '导入任务记录表。记录每次上传文件进入ODS的校验和入库结果。';
COMMENT ON COLUMN data_asset.import_job.job_id IS '导入任务ID。系统生成，主键；也可作为 ODS 的 ingest_batch_id 使用。';
COMMENT ON COLUMN data_asset.import_job.source_key IS '数据源类型编码。来自导入请求，如 event_upload、content_upload、comment_upload。';
COMMENT ON COLUMN data_asset.import_job.template_id IS '使用的模板ID。来自 import_template。';
COMMENT ON COLUMN data_asset.import_job.file_name IS '上传文件名。系统记录。';
COMMENT ON COLUMN data_asset.import_job.file_format IS '上传文件格式。系统记录，如 xlsx、csv。';
COMMENT ON COLUMN data_asset.import_job.operator IS '操作人。上传时填写或系统记录。';
COMMENT ON COLUMN data_asset.import_job.status IS '导入状态。系统生成，如 running、success、failed。';
COMMENT ON COLUMN data_asset.import_job.inserted_rows IS '成功写入ODS的行数。系统生成。';
COMMENT ON COLUMN data_asset.import_job.rejected_rows IS '拒绝写入ODS的行数。系统生成。';
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

COMMENT ON TABLE data_asset.calc_task IS '计算任务元数据表。记录标准化ETL和聚合ETL作业定义。';
COMMENT ON COLUMN data_asset.calc_task.task_id IS '计算任务ID。系统维护，主键。';
COMMENT ON COLUMN data_asset.calc_task.task_name IS '计算任务名称。系统维护，用于页面展示。';
COMMENT ON COLUMN data_asset.calc_task.task_group IS '任务分组。系统维护，如 标准化ETL、VOC看事件。';
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

COMMENT ON TABLE data_asset.calc_task_run IS '计算任务运行记录表。记录每次标准化ETL或聚合ETL执行结果。';
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

CREATE INDEX IF NOT EXISTS idx_ods_event_upload_batch ON data_asset.ods_event_upload(ingest_batch_id);
CREATE INDEX IF NOT EXISTS idx_ods_content_upload_batch ON data_asset.ods_content_upload(ingest_batch_id);
CREATE INDEX IF NOT EXISTS idx_ods_comment_upload_batch ON data_asset.ods_comment_upload(ingest_batch_id);

CREATE INDEX IF NOT EXISTS idx_dwd_content_event_id ON data_asset.dwd_content(event_id);
CREATE INDEX IF NOT EXISTS idx_dwd_content_author_id ON data_asset.dwd_content(author_id);
CREATE INDEX IF NOT EXISTS idx_dwd_content_published_at ON data_asset.dwd_content(published_at);
CREATE INDEX IF NOT EXISTS idx_dwd_author_platform_name ON data_asset.dwd_author(platform, author_name);
CREATE INDEX IF NOT EXISTS idx_dwd_comment_content_id ON data_asset.dwd_comment(content_id);
CREATE INDEX IF NOT EXISTS idx_dwd_comment_location ON data_asset.dwd_comment(location);
CREATE INDEX IF NOT EXISTS idx_dwd_comment_published_at ON data_asset.dwd_comment(published_at);

CREATE INDEX IF NOT EXISTS idx_rel_event_content_content_id ON data_asset.rel_event_content(content_id);
CREATE INDEX IF NOT EXISTS idx_rel_author_content_content_id ON data_asset.rel_author_content(content_id);
CREATE INDEX IF NOT EXISTS idx_ads_event_content_rank_event_type ON data_asset.ads_event_content_rank(event_id, rank_type);

-- =========================================================
-- COMPETITOR：竞品动态
-- 说明：承接每周抖音竞品账号采集形成的账号表、作品底表和后续周报归档。
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.competitor_account (
  account_id       VARCHAR(128) PRIMARY KEY,
  account_key      VARCHAR(128) NOT NULL UNIQUE,
  account_name     VARCHAR(255) NOT NULL,
  account_home_url TEXT,
  account_type     VARCHAR(64),
  is_official      BOOLEAN DEFAULT FALSE,
  brand_name       VARCHAR(128),
  is_enabled       BOOLEAN DEFAULT TRUE,
  remark           TEXT,
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.competitor_account IS '竞品账号表。来自用户维护的抖音竞品账号作者表，用于管理竞品官方号、经销商号等账号资产。';
COMMENT ON COLUMN data_asset.competitor_account.account_id IS '竞品账号ID。系统根据账号主页URL或账号名称生成，主键。';
COMMENT ON COLUMN data_asset.competitor_account.account_key IS '竞品账号自然键。用于去重和 upsert。';
COMMENT ON COLUMN data_asset.competitor_account.account_name IS '账号名称。来自作者表。';
COMMENT ON COLUMN data_asset.competitor_account.account_home_url IS '账号主页URL。来自作者表，优先用于账号去重。';
COMMENT ON COLUMN data_asset.competitor_account.account_type IS '账号类型。来自作者表，如官方、经销商等。';
COMMENT ON COLUMN data_asset.competitor_account.is_official IS '是否官方号。来自作者表。';
COMMENT ON COLUMN data_asset.competitor_account.brand_name IS '品牌。来自作者表。';
COMMENT ON COLUMN data_asset.competitor_account.is_enabled IS '是否启用采集。来自作者表。';
COMMENT ON COLUMN data_asset.competitor_account.remark IS '备注。来自作者表。';

CREATE TABLE IF NOT EXISTS data_asset.competitor_work (
  work_id              VARCHAR(128) PRIMARY KEY,
  work_key             VARCHAR(128) NOT NULL UNIQUE,
  title                TEXT,
  author_name          VARCHAR(255),
  brand_name           VARCHAR(128),
  account_type         VARCHAR(64),
  is_official          BOOLEAN DEFAULT FALSE,
  home_like_cnt        BIGINT DEFAULT 0,
  interaction_like_cnt BIGINT DEFAULT 0,
  comment_cnt          BIGINT DEFAULT 0,
  favorite_cnt         BIGINT DEFAULT 0,
  share_cnt            BIGINT DEFAULT 0,
  published_at         TIMESTAMP,
  is_pinned            BOOLEAN DEFAULT FALSE,
  video_url            TEXT,
  cover_url            TEXT,
  topic_tags           TEXT,
  source_file          TEXT,
  first_seen_at        TIMESTAMP,
  last_seen_at         TIMESTAMP,
  run_id               VARCHAR(64),
  created_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE data_asset.competitor_work IS '竞品作品底表。来自每周抖音竞品内容采集沉淀的大作品底表，用于按发布时间筛选竞品动态。';
COMMENT ON COLUMN data_asset.competitor_work.work_id IS '作品ID。优先来自抖音作品ID，主键。';
COMMENT ON COLUMN data_asset.competitor_work.work_key IS '作品自然键。用于去重和 upsert。';
COMMENT ON COLUMN data_asset.competitor_work.title IS '作品标题或正文摘要。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.author_name IS '作者账号名称。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.brand_name IS '品牌。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.account_type IS '账号类型。来自作品底表，如官方、经销商等。';
COMMENT ON COLUMN data_asset.competitor_work.is_official IS '是否官方号。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.home_like_cnt IS '首页点赞数。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.interaction_like_cnt IS '互动点赞数。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.comment_cnt IS '评论数。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.favorite_cnt IS '收藏数。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.share_cnt IS '分享数。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.published_at IS '发布时间。用于按一周、一个月或自定义日期范围筛选竞品动态。';
COMMENT ON COLUMN data_asset.competitor_work.is_pinned IS '是否置顶。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.video_url IS '视频链接。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.cover_url IS '封面图URL。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.topic_tags IS '话题标签。来自作品底表。';
COMMENT ON COLUMN data_asset.competitor_work.source_file IS '来源文件。来自采集脚本生成的中间文件名。';
COMMENT ON COLUMN data_asset.competitor_work.first_seen_at IS '首次发现时间。表示系统第一次采集到该作品的时间。';
COMMENT ON COLUMN data_asset.competitor_work.last_seen_at IS '最近更新时间。表示系统最近一次更新该作品互动数据的时间。';
COMMENT ON COLUMN data_asset.competitor_work.run_id IS '采集运行ID。来自采集脚本。';

CREATE INDEX IF NOT EXISTS idx_competitor_account_brand_type ON data_asset.competitor_account(brand_name, account_type);
CREATE INDEX IF NOT EXISTS idx_competitor_work_brand_type ON data_asset.competitor_work(brand_name, account_type);
CREATE INDEX IF NOT EXISTS idx_competitor_work_author ON data_asset.competitor_work(author_name);
CREATE INDEX IF NOT EXISTS idx_competitor_work_published_at ON data_asset.competitor_work(published_at);

-- =========================================================
-- PROFILE：用户画像维护
-- 说明：承接线下AI/Excel打标结果。底表存事实，画像表存判断。
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.user_profile_kol (
  kol_profile_id   BIGSERIAL PRIMARY KEY,
  author_id        VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_author(author_id),
  kol_main_type    VARCHAR(64),
  content_tendency VARCHAR(64),
  car_focus        VARCHAR(64),
  remark           TEXT,
  profile_batch    VARCHAR(128) NOT NULL DEFAULT 'default',
  source_file_name VARCHAR(255),
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (author_id, profile_batch)
);

COMMENT ON TABLE data_asset.user_profile_kol IS 'KOL画像表。存储线下根据KOL近7日发帖文本打标后的画像结果，一条记录表示某个KOL在某个画像批次下的结果。';
COMMENT ON COLUMN data_asset.user_profile_kol.kol_profile_id IS 'KOL画像记录ID。系统生成。';
COMMENT ON COLUMN data_asset.user_profile_kol.author_id IS '系统内作者ID。关联 dwd_author.author_id，上传画像时用于精准匹配KOL。';
COMMENT ON COLUMN data_asset.user_profile_kol.kol_main_type IS 'KOL主类型。枚举：车型实测测评KOL/新车资讯爆料KOL/用车养车科普KOL/二手车KOL/导购优惠探店KOL/自驾出行生活KOL/行业宏观评论KOL/商单广告博主/综合杂谈类KOL。';
COMMENT ON COLUMN data_asset.user_profile_kol.content_tendency IS '内容倾向。枚举：偏客观实测/偏种草营销/偏吐槽负面。';
COMMENT ON COLUMN data_asset.user_profile_kol.car_focus IS '车型关注。枚举：燃油车专注/新能源专注/全品类通吃。';
COMMENT ON COLUMN data_asset.user_profile_kol.remark IS '简要判定依据。建议一句话说明近7日内容占比。';
COMMENT ON COLUMN data_asset.user_profile_kol.profile_batch IS '画像批次或提示词版本。用于对比不同prompt版本的打标效果。';
COMMENT ON COLUMN data_asset.user_profile_kol.source_file_name IS '上传画像结果文件名。';

CREATE INDEX IF NOT EXISTS idx_user_profile_kol_batch ON data_asset.user_profile_kol(profile_batch);
CREATE INDEX IF NOT EXISTS idx_user_profile_kol_author ON data_asset.user_profile_kol(author_id);

CREATE TABLE IF NOT EXISTS data_asset.user_profile_comment_raw (
  raw_profile_id   BIGSERIAL PRIMARY KEY,
  comment_user_id  VARCHAR(128) NOT NULL,
  profile_batch    VARCHAR(128) NOT NULL DEFAULT 'default',
  prompt_version   VARCHAR(128),
  llm_result_json  JSONB NOT NULL,
  source_file_name VARCHAR(255),
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (comment_user_id, profile_batch)
);

COMMENT ON TABLE data_asset.user_profile_comment_raw IS '评论用户画像LLM原始结果表。存储线下对某个评论用户全量评论打标后的原始JSON，便于回看提示词输出。';
COMMENT ON COLUMN data_asset.user_profile_comment_raw.raw_profile_id IS '评论用户画像原始记录ID。系统生成。';
COMMENT ON COLUMN data_asset.user_profile_comment_raw.comment_user_id IS '系统内评论用户ID。由平台、评论昵称、位置生成，来自评论样本导出文件。';
COMMENT ON COLUMN data_asset.user_profile_comment_raw.profile_batch IS '画像批次。用于区分不同时间、不同提示词或不同实验版本的打标结果。';
COMMENT ON COLUMN data_asset.user_profile_comment_raw.prompt_version IS '提示词版本。使用者上传，便于比较不同提示词效果。';
COMMENT ON COLUMN data_asset.user_profile_comment_raw.llm_result_json IS 'LLM输出原始JSON。包含评论级证据、维度、标签、原因和分数。';
COMMENT ON COLUMN data_asset.user_profile_comment_raw.source_file_name IS '上传画像结果文件名。';

CREATE TABLE IF NOT EXISTS data_asset.user_profile_comment_result (
  comment_user_profile_id BIGSERIAL PRIMARY KEY,
  comment_user_id         VARCHAR(128) NOT NULL,
  platform                VARCHAR(64),
  comment_author_name     VARCHAR(255),
  location                VARCHAR(128),
  total_comments          BIGINT DEFAULT 0,
  valid_comments          BIGINT DEFAULT 0,
  main_dimension          VARCHAR(128),
  main_label              VARCHAR(255),
  main_score              NUMERIC(8,2),
  label_scores_json       JSONB,
  profile_batch           VARCHAR(128) NOT NULL DEFAULT 'default',
  prompt_version          VARCHAR(128),
  source_raw_profile_id   BIGINT REFERENCES data_asset.user_profile_comment_raw(raw_profile_id),
  source_file_name        VARCHAR(255),
  created_time            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (comment_user_id, profile_batch)
);

COMMENT ON TABLE data_asset.user_profile_comment_result IS '评论用户画像汇总表。由LLM原始结果经过Python规则汇总生成，一条记录表示某个评论用户在某个批次下的主标签和总体画像。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.comment_user_id IS '系统内评论用户ID。用于上传回灌时精准匹配评论用户。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.platform IS '平台。来自该评论用户在评论明细中的平台。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.comment_author_name IS '评论用户昵称。来自 dwd_comment.comment_author_name。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.location IS '位置。来自 dwd_comment.location，可为空。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.total_comments IS '参与画像计算的评论总数。来自LLM结果。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.valid_comments IS '有效评论数。来自LLM结果，表示可用于画像判断的评论数量。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.main_dimension IS '主标签所属维度。由Python汇总规则选取得分最高标签得到。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.main_label IS '主标签。由Python汇总规则选取得分最高标签得到。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.main_score IS '主标签分数。由Python汇总规则计算。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.label_scores_json IS '全部标签得分和证据JSON。保留每个标签的得分、置信、证据示例和原因。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.profile_batch IS '画像批次。用于对比不同提示词或不同时间的画像结果。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.prompt_version IS '提示词版本。来自上传文件。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.source_raw_profile_id IS '来源LLM原始结果ID，关联 user_profile_comment_raw.raw_profile_id。';
COMMENT ON COLUMN data_asset.user_profile_comment_result.source_file_name IS '上传画像结果文件名。';

CREATE TABLE IF NOT EXISTS data_asset.user_profile_comment_label_score (
  comment_user_id        VARCHAR(128) NOT NULL,
  profile_batch          VARCHAR(128) NOT NULL,
  dimension              VARCHAR(128) NOT NULL,
  label                  VARCHAR(255) NOT NULL,
  final_score            NUMERIC(8,2),
  feature_level          VARCHAR(64),
  confidence_level       VARCHAR(64),
  support_count          BIGINT DEFAULT 0,
  evidence_examples_json JSONB,
  evidence_details_json  JSONB,
  updated_time           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (comment_user_id, profile_batch, dimension, label)
);

COMMENT ON TABLE data_asset.user_profile_comment_label_score IS '评论用户画像标签明细表。展开保存每个用户每个标签的得分、置信度和证据，支撑解释原因。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.comment_user_id IS '系统内评论用户ID。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.profile_batch IS '画像批次。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.dimension IS '标签维度。来自LLM证据JSON。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.label IS '标签名称。来自LLM证据JSON。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.final_score IS '最终得分。由Python汇总规则计算。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.feature_level IS '特征强度等级。由Python汇总规则根据得分生成。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.confidence_level IS '置信等级。由Python汇总规则根据得分和支持评论数生成。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.support_count IS '支持该标签的评论证据数量。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.evidence_examples_json IS '证据示例JSON。用于页面或导出展示简要原因。';
COMMENT ON COLUMN data_asset.user_profile_comment_label_score.evidence_details_json IS '证据明细JSON。用于追溯每条评论、证据文本、原因和权重。';

CREATE INDEX IF NOT EXISTS idx_user_profile_comment_raw_batch ON data_asset.user_profile_comment_raw(profile_batch);
CREATE INDEX IF NOT EXISTS idx_user_profile_comment_result_batch ON data_asset.user_profile_comment_result(profile_batch);
CREATE INDEX IF NOT EXISTS idx_user_profile_comment_result_label ON data_asset.user_profile_comment_result(main_label);

-- =========================================================
-- SYSTEM：系统参数与提示词维护
-- 说明：用于把 AI 服务参数、提示词模板从代码文件迁移到可维护的数据表。
-- =========================================================

CREATE TABLE IF NOT EXISTS data_asset.system_ai_config (
  ai_config_id     BIGSERIAL PRIMARY KEY,
  config_name      VARCHAR(128) NOT NULL DEFAULT 'default',
  base_url         TEXT NOT NULL,
  api_key          TEXT,
  model_name       VARCHAR(128) NOT NULL,
  timeout_seconds  INTEGER NOT NULL DEFAULT 60,
  is_enabled       BOOLEAN NOT NULL DEFAULT TRUE,
  is_default       BOOLEAN NOT NULL DEFAULT TRUE,
  created_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (config_name)
);

COMMENT ON TABLE data_asset.system_ai_config IS '系统AI参数配置表。维护 OpenAI 兼容接口的 base_url、api_key、model 和超时时间，供用户画像AI打标流程读取。';
COMMENT ON COLUMN data_asset.system_ai_config.ai_config_id IS 'AI参数配置记录ID。系统生成。';
COMMENT ON COLUMN data_asset.system_ai_config.config_name IS '配置名称。第一版默认使用 default，后续可扩展多套模型配置。';
COMMENT ON COLUMN data_asset.system_ai_config.base_url IS 'OpenAI兼容接口地址。可以填写到 /v1 或 /v1/chat/completions，系统会自动补齐。';
COMMENT ON COLUMN data_asset.system_ai_config.api_key IS 'AI接口密钥。仅后端运行时读取，前端接口不返回明文。';
COMMENT ON COLUMN data_asset.system_ai_config.model_name IS '模型名称。用于 chat completions 请求的 model 字段。';
COMMENT ON COLUMN data_asset.system_ai_config.timeout_seconds IS 'AI请求超时时间，单位秒。';
COMMENT ON COLUMN data_asset.system_ai_config.is_enabled IS '是否启用该配置。关闭后不允许发起AI画像打标。';
COMMENT ON COLUMN data_asset.system_ai_config.is_default IS '是否默认配置。第一版只使用默认配置。';

CREATE TABLE IF NOT EXISTS data_asset.system_prompt_template (
  prompt_id       BIGSERIAL PRIMARY KEY,
  prompt_name     VARCHAR(128) NOT NULL,
  prompt_scene    VARCHAR(64) NOT NULL,
  prompt_version  VARCHAR(128) NOT NULL,
  prompt_content  TEXT NOT NULL,
  is_default      BOOLEAN NOT NULL DEFAULT FALSE,
  is_enabled      BOOLEAN NOT NULL DEFAULT TRUE,
  created_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (prompt_scene, prompt_version)
);

COMMENT ON TABLE data_asset.system_prompt_template IS '系统提示词模板表。维护不同业务场景、不同版本的提示词正文，供AI流程运行时读取。';
COMMENT ON COLUMN data_asset.system_prompt_template.prompt_id IS '提示词模板ID。系统生成。';
COMMENT ON COLUMN data_asset.system_prompt_template.prompt_name IS '提示词名称。面向使用者展示，例如评论用户画像提示词。';
COMMENT ON COLUMN data_asset.system_prompt_template.prompt_scene IS '提示词场景。第一版使用 comment_user_profile，表示评论用户画像AI打标。';
COMMENT ON COLUMN data_asset.system_prompt_template.prompt_version IS '提示词版本。用于区分不同prompt实验版本，并写入画像结果表追溯。';
COMMENT ON COLUMN data_asset.system_prompt_template.prompt_content IS '提示词正文。系统会把用户ID和评论列表拼接到该模板中。';
COMMENT ON COLUMN data_asset.system_prompt_template.is_default IS '是否默认提示词。同一场景下默认只应有一个默认版本。';
COMMENT ON COLUMN data_asset.system_prompt_template.is_enabled IS '是否启用该提示词。关闭后不作为运行候选。';

CREATE INDEX IF NOT EXISTS idx_system_ai_config_default ON data_asset.system_ai_config(is_default, is_enabled);
CREATE INDEX IF NOT EXISTS idx_system_prompt_template_scene ON data_asset.system_prompt_template(prompt_scene, is_default, is_enabled);

CREATE TABLE IF NOT EXISTS data_asset.system_emoji_mapping (
  emoji_id      BIGSERIAL PRIMARY KEY,
  emoji_code    VARCHAR(128) NOT NULL,
  emoji_type    VARCHAR(32) NOT NULL DEFAULT 'emoji',
  emoji_value   TEXT NOT NULL,
  display_name  VARCHAR(128),
  is_enabled    BOOLEAN NOT NULL DEFAULT TRUE,
  created_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (emoji_code)
);

COMMENT ON TABLE data_asset.system_emoji_mapping IS '系统表情包映射表。用于把评论原文中的[666]、[捂脸]等平台表情文本，在前端展示时替换为emoji字符或图片。';
COMMENT ON COLUMN data_asset.system_emoji_mapping.emoji_code IS '原始表情文本，例如[666]、[捂脸]。原文不改，只在展示层匹配替换。';
COMMENT ON COLUMN data_asset.system_emoji_mapping.emoji_type IS '表情类型。emoji表示字符表情，image表示图片地址。';
COMMENT ON COLUMN data_asset.system_emoji_mapping.emoji_value IS '替换后的展示值。emoji类型填写字符，image类型填写图片URL或静态资源路径。';
COMMENT ON COLUMN data_asset.system_emoji_mapping.display_name IS '表情展示名称，后台维护和搜索使用。';
COMMENT ON COLUMN data_asset.system_emoji_mapping.is_enabled IS '是否启用。关闭后前端不替换该表情。';

CREATE INDEX IF NOT EXISTS idx_system_emoji_mapping_enabled ON data_asset.system_emoji_mapping(is_enabled, emoji_code);
