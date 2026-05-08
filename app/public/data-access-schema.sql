CREATE SCHEMA IF NOT EXISTS data_asset;

CREATE TABLE IF NOT EXISTS data_asset.dwd_event (
  event_id VARCHAR(64) PRIMARY KEY,
  event_name VARCHAR(255) NOT NULL,
  event_desc TEXT,
  event_type VARCHAR(64) NOT NULL,
  brand_name VARCHAR(128),
  model_name VARCHAR(128),
  keyword_list TEXT,
  start_time TIMESTAMP,
  end_time TIMESTAMP,
  event_status VARCHAR(32) NOT NULL,
  created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS data_asset.dwd_content (
  content_id VARCHAR(64) PRIMARY KEY,
  platform VARCHAR(64) NOT NULL,
  source_url TEXT NOT NULL,
  author_id VARCHAR(64),
  author_name VARCHAR(255) NOT NULL,
  author_type VARCHAR(64),
  is_kol BOOLEAN DEFAULT FALSE,
  kol_domain VARCHAR(128),
  fans_cnt BIGINT DEFAULT 0,
  title TEXT NOT NULL,
  content_text TEXT,
  content_type VARCHAR(64),
  media_form VARCHAR(64),
  published_at TIMESTAMP NOT NULL,
  like_cnt BIGINT DEFAULT 0,
  comment_cnt BIGINT DEFAULT 0,
  share_cnt BIGINT DEFAULT 0,
  favorite_cnt BIGINT DEFAULT 0,
  view_cnt BIGINT DEFAULT 0,
  engagement_total BIGINT GENERATED ALWAYS AS (like_cnt + comment_cnt + share_cnt + favorite_cnt) STORED
);

CREATE TABLE IF NOT EXISTS data_asset.dwd_account (
  account_id VARCHAR(64) NOT NULL,
  snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,
  platform VARCHAR(64) NOT NULL,
  platform_account_id VARCHAR(128),
  nickname VARCHAR(255) NOT NULL,
  avatar_url TEXT,
  account_type VARCHAR(64),
  is_kol BOOLEAN DEFAULT FALSE,
  domain_tag VARCHAR(128),
  fans_cnt BIGINT DEFAULT 0,
  follow_cnt BIGINT DEFAULT 0,
  liked_cnt BIGINT DEFAULT 0,
  account_desc TEXT,
  certification_info TEXT,
  persona_tag VARCHAR(128),
  stage_tag VARCHAR(128),
  profile_tags_json JSONB,
  PRIMARY KEY (account_id, snapshot_date)
);

CREATE TABLE IF NOT EXISTS data_asset.dwd_comment (
  comment_id VARCHAR(64) PRIMARY KEY,
  platform VARCHAR(64),
  content_id VARCHAR(64) NOT NULL REFERENCES data_asset.dwd_content(content_id),
  comment_author_id VARCHAR(64),
  comment_author_name VARCHAR(255) NOT NULL,
  parent_comment_id VARCHAR(64),
  reply_level INTEGER DEFAULT 1,
  comment_text TEXT NOT NULL,
  published_at TIMESTAMP NOT NULL,
  like_cnt BIGINT DEFAULT 0,
  reply_cnt BIGINT DEFAULT 0,
  interaction_cnt BIGINT DEFAULT 0,
  source_url TEXT,
  opinion_tag VARCHAR(128),
  intention_tag VARCHAR(128),
  sentiment_tag VARCHAR(128),
  persona_tag VARCHAR(128),
  stage_tag VARCHAR(128),
  mindset_tag VARCHAR(128)
);

CREATE TABLE IF NOT EXISTS data_asset.calc_task (
  task_id VARCHAR(64) PRIMARY KEY,
  task_name VARCHAR(255) NOT NULL,
  task_group VARCHAR(64) NOT NULL,
  task_desc TEXT,
  script_path TEXT NOT NULL,
  entry_func VARCHAR(64) NOT NULL,
  input_tables_json JSONB NOT NULL,
  output_tables_json JSONB NOT NULL,
  run_mode VARCHAR(32) NOT NULL,
  is_enabled BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS data_asset.calc_task_run (
  run_id VARCHAR(64) PRIMARY KEY,
  task_id VARCHAR(64) NOT NULL REFERENCES data_asset.calc_task(task_id),
  run_status VARCHAR(32) NOT NULL,
  trigger_type VARCHAR(32) NOT NULL,
  started_at TIMESTAMP NOT NULL,
  finished_at TIMESTAMP,
  duration_ms INTEGER,
  processed_rows BIGINT DEFAULT 0,
  output_rows BIGINT DEFAULT 0,
  error_message TEXT,
  log_path TEXT
);
