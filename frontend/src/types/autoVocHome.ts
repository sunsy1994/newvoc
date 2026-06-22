export type AutoVocOverview = {
  event_count: number;
  content_count: number;
  comment_count: number;
  author_count: number;
  total_event_count: number;
  total_content_count: number;
  total_comment_count: number;
  total_author_count: number;
};

export type AutoVocTrend = {
  value: number | null;
  label: string;
  tone: "up" | "down" | "flat" | "new";
};

export type AutoVocBusinessMetric = {
  metric_key: "own_brand" | "competitor_brand" | "top_pko_target" | "hottest_event";
  label: string;
  title: string;
  primary_text: string;
  secondary_text: string;
  event_count?: number;
  volume?: number;
  count?: number;
  brand_name?: string | null;
  event_id?: string | null;
  event_name?: string | null;
  trend: AutoVocTrend;
};

export type AutoVocKeyEvent = {
  event_id: string;
  event_name: string;
  brand_name?: string | null;
  model_name?: string | null;
  event_type?: string | null;
  event_status?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  content_count: number;
  comment_count: number;
  total_engagement: number;
  total_volume: number;
};

export type AutoVocHotTopic = {
  topic: string;
  content_count: number;
  comment_count: number;
  total_engagement: number;
};

export type AutoVocCompetitorUpdate = {
  work_id: string;
  title?: string | null;
  author_name?: string | null;
  brand_name?: string | null;
  account_type?: string | null;
  is_official?: boolean | null;
  interaction_like_cnt: number;
  comment_cnt: number;
  favorite_cnt: number;
  share_cnt: number;
  total_interaction: number;
  published_at?: string | null;
  video_url?: string | null;
};

export type AutoVocAttentionSignal = {
  signal_key: string;
  label: string;
  value: number;
  description: string;
  tone: "intent" | "positive" | "negative" | "neutral";
};

export type AutoVocHomePayload = {
  period_days: number;
  generated_at: string;
  overview: AutoVocOverview;
  business_metrics: AutoVocBusinessMetric[];
  key_events: AutoVocKeyEvent[];
  hot_topics: AutoVocHotTopic[];
  auto_hot_searches: unknown[];
  competitor_updates: AutoVocCompetitorUpdate[];
  attention_signals: AutoVocAttentionSignal[];
  ai_prompts: string[];
};
