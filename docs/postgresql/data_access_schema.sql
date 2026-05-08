CREATE SCHEMA IF NOT EXISTS data_asset;

CREATE TABLE IF NOT EXISTS data_asset.dwd_event (
  event_id            VARCHAR(64) PRIMARY KEY,
  event_name          VARCHAR(255) NOT NULL,
  event_desc          TEXT,
  event_type          VARCHAR(64) NOT NULL,
  brand_name          VARCHAR(128),
  model_name          VARCHAR(128),
  keyword_list        TEXT,
  start_time          TIMESTAMP,
  end_time            TIMESTAMP,
  event_status        VARCHAR(32) NOT NULL,
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.dwd_account (
  account_id          VARCHAR(64) NOT NULL,
  snapshot_date       DATE NOT NULL DEFAULT CURRENT_DATE,
  platform            VARCHAR(64) NOT NULL,
  platform_account_id VARCHAR(128),
  nickname            VARCHAR(255) NOT NULL,
  avatar_url          TEXT,
  account_type        VARCHAR(64),
  is_kol              BOOLEAN DEFAULT FALSE,
  domain_tag          VARCHAR(128),
  fans_cnt            BIGINT DEFAULT 0,
  follow_cnt          BIGINT DEFAULT 0,
  liked_cnt           BIGINT DEFAULT 0,
  account_desc        TEXT,
  certification_info  TEXT,
  persona_tag         VARCHAR(128),
  stage_tag           VARCHAR(128),
  profile_tags_json   JSONB,
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (account_id, snapshot_date)
);

CREATE TABLE IF NOT EXISTS data_asset.dwd_content (
  content_id          VARCHAR(64) PRIMARY KEY,
  platform            VARCHAR(64) NOT NULL,
  source_url          TEXT NOT NULL,
  author_id           VARCHAR(64),
  author_name         VARCHAR(255) NOT NULL,
  author_type         VARCHAR(64),
  is_kol              BOOLEAN DEFAULT FALSE,
  kol_domain          VARCHAR(128),
  fans_cnt            BIGINT DEFAULT 0,
  title               TEXT NOT NULL,
  content_text        TEXT,
  content_type        VARCHAR(64),
  media_form          VARCHAR(64),
  published_at        TIMESTAMP NOT NULL,
  like_cnt            BIGINT DEFAULT 0,
  comment_cnt         BIGINT DEFAULT 0,
  share_cnt           BIGINT DEFAULT 0,
  favorite_cnt        BIGINT DEFAULT 0,
  view_cnt            BIGINT DEFAULT 0,
  engagement_total    BIGINT GENERATED ALWAYS AS (like_cnt + comment_cnt + share_cnt + favorite_cnt) STORED,
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.rel_event_content (
  event_id            VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  content_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  match_type          VARCHAR(32) DEFAULT 'manual',
  match_score         NUMERIC(8,4) DEFAULT 1,
  is_primary_event    BOOLEAN DEFAULT TRUE,
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (event_id, content_id)
);

CREATE TABLE IF NOT EXISTS data_asset.dwd_comment (
  comment_id          VARCHAR(64) PRIMARY KEY,
  platform            VARCHAR(64),
  content_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  comment_author_id   VARCHAR(64),
  comment_author_name VARCHAR(255) NOT NULL,
  parent_comment_id   VARCHAR(64),
  reply_level         INTEGER DEFAULT 1,
  comment_text        TEXT NOT NULL,
  published_at        TIMESTAMP NOT NULL,
  like_cnt            BIGINT DEFAULT 0,
  reply_cnt           BIGINT DEFAULT 0,
  interaction_cnt     BIGINT DEFAULT 0,
  source_url          TEXT,
  opinion_tag         VARCHAR(128),
  intention_tag       VARCHAR(128),
  sentiment_tag       VARCHAR(128),
  persona_tag         VARCHAR(128),
  stage_tag           VARCHAR(128),
  mindset_tag         VARCHAR(128),
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.fact_content_tag (
  id                  BIGSERIAL PRIMARY KEY,
  content_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  event_id            VARCHAR(64) REFERENCES data_asset.dwd_event(event_id),
  tag_type            VARCHAR(64) NOT NULL,
  tag_value           VARCHAR(255) NOT NULL,
  tag_score           NUMERIC(8,4),
  is_primary_tag      BOOLEAN DEFAULT FALSE,
  model_version       VARCHAR(64),
  tag_source          VARCHAR(32) DEFAULT 'model',
  generated_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.fact_comment_tag (
  id                  BIGSERIAL PRIMARY KEY,
  comment_id          VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_comment(comment_id),
  content_id          VARCHAR(64) REFERENCES data_asset.dwd_content(content_id),
  event_id            VARCHAR(64) REFERENCES data_asset.dwd_event(event_id),
  tag_type            VARCHAR(64) NOT NULL,
  tag_value           VARCHAR(255) NOT NULL,
  confidence          NUMERIC(8,4),
  labeling_reason     TEXT,
  model_version       VARCHAR(64),
  tag_source          VARCHAR(32) DEFAULT 'model',
  generated_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.fact_content_comment_profile_di (
  content_id                VARCHAR(64) PRIMARY KEY REFERENCES data_asset.dwd_content(content_id),
  event_id                  VARCHAR(64) REFERENCES data_asset.dwd_event(event_id),
  comment_cnt               BIGINT DEFAULT 0,
  high_confidence_rate      NUMERIC(8,4) DEFAULT 0,
  owner_rate                NUMERIC(8,4) DEFAULT 0,
  test_drive_rate           NUMERIC(8,4) DEFAULT 0,
  prospect_rate             NUMERIC(8,4) DEFAULT 0,
  doubt_rate                NUMERIC(8,4) DEFAULT 0,
  approval_rate             NUMERIC(8,4) DEFAULT 0,
  positive_rate             NUMERIC(8,4) DEFAULT 0,
  negative_rate             NUMERIC(8,4) DEFAULT 0,
  stage_top1                VARCHAR(64),
  attitude_top1             VARCHAR(64),
  mindset_distribution_json JSONB,
  emotion_distribution_json JSONB,
  attitude_distribution_json JSONB,
  stage_distribution_json   JSONB,
  updated_time              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_event_asset_overview (
  event_id            VARCHAR(64) PRIMARY KEY REFERENCES data_asset.dwd_event(event_id),
  event_name          VARCHAR(255),
  event_desc          TEXT,
  event_type          VARCHAR(64),
  brand_name          VARCHAR(128),
  model_name          VARCHAR(128),
  keyword_list        TEXT,
  start_time          TIMESTAMP,
  end_time            TIMESTAMP,
  event_status        VARCHAR(32),
  platform_list       JSONB,
  content_cnt         BIGINT DEFAULT 0,
  comment_cnt         BIGINT DEFAULT 0,
  author_cnt          BIGINT DEFAULT 0,
  kol_cnt             BIGINT DEFAULT 0,
  total_engagement    BIGINT DEFAULT 0,
  negative_comment_cnt BIGINT DEFAULT 0,
  negative_ratio      NUMERIC(10,4) DEFAULT 0,
  heat_score          NUMERIC(10,2) DEFAULT 0,
  growth_rate         NUMERIC(10,4) DEFAULT 0,
  recent_heat         NUMERIC(10,2) DEFAULT 0,
  prev_heat           NUMERIC(10,2) DEFAULT 0,
  risk_level          VARCHAR(32),
  topic_top_json      JSONB,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_event_trend_daily (
  event_id            VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  stat_date           DATE NOT NULL,
  content_cnt         BIGINT DEFAULT 0,
  comment_cnt         BIGINT DEFAULT 0,
  engagement_cnt      BIGINT DEFAULT 0,
  negative_comment_cnt BIGINT DEFAULT 0,
  heat_score          NUMERIC(10,2) DEFAULT 0,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (event_id, stat_date)
);

CREATE TABLE IF NOT EXISTS data_asset.ads_content_value_summary (
  content_id                VARCHAR(64) PRIMARY KEY REFERENCES data_asset.dwd_content(content_id),
  event_id                  VARCHAR(64) REFERENCES data_asset.dwd_event(event_id),
  content_role              VARCHAR(64),
  value_level               VARCHAR(32),
  value_flags_json          JSONB,
  value_summary             TEXT,
  value_reason_json         JSONB,
  is_core_content           BOOLEAN DEFAULT FALSE,
  tag_confidence            NUMERIC(8,4),
  representative_comments_json JSONB,
  updated_time              TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_author_event_summary (
  event_id                  VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  author_id                 VARCHAR(64) NOT NULL,
  nickname                  VARCHAR(255),
  platform                  VARCHAR(64),
  author_type               VARCHAR(64),
  is_kol                    BOOLEAN DEFAULT FALSE,
  stage_tag                 VARCHAR(64),
  stage_confidence          NUMERIC(8,4),
  stage_reason              TEXT,
  posts                     BIGINT DEFAULT 0,
  total_engagement          BIGINT DEFAULT 0,
  comment_trigger_cnt       BIGINT DEFAULT 0,
  top_content_types_json    JSONB,
  proposition_top_json      JSONB,
  issue_top_json            JSONB,
  evidence_strength         NUMERIC(10,2),
  evidence_type             VARCHAR(64),
  reproducible_flag         BOOLEAN DEFAULT FALSE,
  controversy_score         NUMERIC(10,2),
  high_value_flag           BOOLEAN DEFAULT FALSE,
  high_controversy_flag     BOOLEAN DEFAULT FALSE,
  high_confidence_flag      BOOLEAN DEFAULT FALSE,
  role_tags_json            JSONB,
  ai_summary                TEXT,
  content_timeline_json     JSONB,
  representative_contents_json JSONB,
  representative_comments_json JSONB,
  updated_time              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (event_id, author_id)
);

CREATE TABLE IF NOT EXISTS data_asset.ads_kol_event_summary (
  event_id                  VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_event(event_id),
  account_id                VARCHAR(64) NOT NULL,
  nickname                  VARCHAR(255),
  avatar_url                TEXT,
  platform                  VARCHAR(64),
  fans_cnt                  BIGINT DEFAULT 0,
  domain_tag                VARCHAR(128),
  author_type               VARCHAR(64),
  event_posts               BIGINT DEFAULT 0,
  total_engagement          BIGINT DEFAULT 0,
  total_comments            BIGINT DEFAULT 0,
  avg_engagement            NUMERIC(12,2) DEFAULT 0,
  high_confidence_ratio     NUMERIC(8,4) DEFAULT 0,
  effective_engagement_rate NUMERIC(8,4) DEFAULT 0,
  risk_score                NUMERIC(8,4) DEFAULT 0,
  role_tags_json            JSONB,
  mindset_top_json          JSONB,
  stage_top_json            JSONB,
  intention_top_json        JSONB,
  summary                   TEXT,
  representative_comments_json JSONB,
  updated_time              TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (event_id, account_id)
);

CREATE TABLE IF NOT EXISTS data_asset.dwd_customer_touchpoint (
  touchpoint_id       VARCHAR(64) PRIMARY KEY,
  source_channel      VARCHAR(64) NOT NULL,
  source_system       VARCHAR(128),
  source_record_id    VARCHAR(128),
  channel_user_key    VARCHAR(255),
  user_display_name   VARCHAR(255),
  touchpoint_text     TEXT NOT NULL,
  touchpoint_time     TIMESTAMP NOT NULL,
  brand_name          VARCHAR(128),
  model_name          VARCHAR(128),
  city_name           VARCHAR(128),
  store_id            VARCHAR(128),
  store_name          VARCHAR(255),
  event_id            VARCHAR(64),
  content_id          VARCHAR(64),
  journey_stage       VARCHAR(64) NOT NULL,
  stage_confidence    NUMERIC(8,4) DEFAULT 0,
  stage_reason        TEXT,
  intent_tag          VARCHAR(128),
  issue_tag           VARCHAR(128),
  sentiment_tag       VARCHAR(128),
  mindset_tag         VARCHAR(128),
  business_status     VARCHAR(128),
  rating_score        NUMERIC(8,2),
  created_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_journey_stage_summary (
  summary_id                      VARCHAR(128) PRIMARY KEY,
  brand_name                      VARCHAR(128),
  model_name                      VARCHAR(128),
  journey_stage                   VARCHAR(64) NOT NULL,
  date_from                       DATE,
  date_to                         DATE,
  touchpoint_cnt                  BIGINT DEFAULT 0,
  channel_cnt                     BIGINT DEFAULT 0,
  negative_touchpoint_cnt         BIGINT DEFAULT 0,
  negative_ratio                  NUMERIC(10,4) DEFAULT 0,
  intent_top_json                 JSONB,
  issue_top_json                  JSONB,
  channel_distribution_json       JSONB,
  representative_touchpoints_json JSONB,
  data_lineage_json               JSONB,
  updated_time                    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_journey_channel_matrix (
  matrix_id          VARCHAR(128) PRIMARY KEY,
  brand_name         VARCHAR(128),
  model_name         VARCHAR(128),
  source_channel     VARCHAR(64) NOT NULL,
  journey_stage      VARCHAR(64) NOT NULL,
  date_from          DATE,
  date_to            DATE,
  touchpoint_cnt     BIGINT DEFAULT 0,
  negative_ratio     NUMERIC(10,4) DEFAULT 0,
  issue_top_json     JSONB,
  intent_top_json    JSONB,
  data_lineage_json  JSONB,
  updated_time       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.ads_journey_painpoint_summary (
  painpoint_id         VARCHAR(128) PRIMARY KEY,
  brand_name           VARCHAR(128),
  model_name           VARCHAR(128),
  journey_stage        VARCHAR(64) NOT NULL,
  issue_tag            VARCHAR(128) NOT NULL,
  touchpoint_cnt       BIGINT DEFAULT 0,
  negative_ratio       NUMERIC(10,4) DEFAULT 0,
  source_channels_json JSONB,
  sample_texts_json    JSONB,
  suggested_owner      VARCHAR(64),
  suggested_action     TEXT,
  data_lineage_json    JSONB,
  updated_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_customer_touchpoint_stage ON data_asset.dwd_customer_touchpoint(journey_stage);
CREATE INDEX IF NOT EXISTS idx_customer_touchpoint_channel ON data_asset.dwd_customer_touchpoint(source_channel);
CREATE INDEX IF NOT EXISTS idx_customer_touchpoint_time ON data_asset.dwd_customer_touchpoint(touchpoint_time);

CREATE TABLE IF NOT EXISTS data_asset.import_template (
  template_id          VARCHAR(64) PRIMARY KEY,
  source_key           VARCHAR(64) NOT NULL,
  source_name          VARCHAR(128) NOT NULL,
  file_name            VARCHAR(255) NOT NULL,
  format               VARCHAR(16) NOT NULL,
  description          TEXT,
  required_fields_json JSONB NOT NULL,
  optional_fields_json JSONB,
  download_path        TEXT NOT NULL,
  created_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.import_job (
  job_id               VARCHAR(64) PRIMARY KEY,
  source_key           VARCHAR(64) NOT NULL,
  template_id          VARCHAR(64) NOT NULL REFERENCES data_asset.import_template(template_id),
  file_name            VARCHAR(255) NOT NULL,
  file_format          VARCHAR(16) NOT NULL,
  operator             VARCHAR(128) NOT NULL,
  status               VARCHAR(32) NOT NULL,
  inserted_rows        BIGINT DEFAULT 0,
  rejected_rows        BIGINT DEFAULT 0,
  message              TEXT,
  created_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.calc_task (
  task_id              VARCHAR(64) PRIMARY KEY,
  task_name            VARCHAR(255) NOT NULL,
  task_group           VARCHAR(64) NOT NULL,
  task_desc            TEXT,
  script_path          TEXT NOT NULL,
  entry_func           VARCHAR(64) NOT NULL,
  input_tables_json    JSONB NOT NULL,
  output_tables_json   JSONB NOT NULL,
  run_mode             VARCHAR(32) NOT NULL,
  is_enabled           BOOLEAN DEFAULT TRUE,
  created_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.calc_task_run (
  run_id               VARCHAR(64) PRIMARY KEY,
  task_id              VARCHAR(64) NOT NULL REFERENCES data_asset.calc_task(task_id),
  run_status           VARCHAR(32) NOT NULL,
  trigger_type         VARCHAR(32) NOT NULL,
  started_at           TIMESTAMP NOT NULL,
  finished_at          TIMESTAMP,
  duration_ms          INTEGER,
  processed_rows       BIGINT DEFAULT 0,
  output_rows          BIGINT DEFAULT 0,
  error_message        TEXT,
  log_path             TEXT,
  created_time         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dwd_content_author_id ON data_asset.dwd_content(author_id);
CREATE INDEX IF NOT EXISTS idx_dwd_content_published_at ON data_asset.dwd_content(published_at);
CREATE INDEX IF NOT EXISTS idx_dwd_comment_content_id ON data_asset.dwd_comment(content_id);
CREATE INDEX IF NOT EXISTS idx_fact_content_tag_content_id ON data_asset.fact_content_tag(content_id);
CREATE INDEX IF NOT EXISTS idx_fact_comment_tag_comment_id ON data_asset.fact_comment_tag(comment_id);
