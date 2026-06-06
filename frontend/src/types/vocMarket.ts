export type VocEvent = {
  event_id: string;
  event_name: string;
  brand_name?: string | null;
  model_name?: string | null;
  event_type?: string | null;
  event_status?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  content_cnt?: number | null;
  comment_cnt?: number | null;
  kol_content_cnt?: number | null;
  total_engagement?: number | null;
};

export type OverviewMetrics = {
  total_volume: number;
  content_count: number;
  comment_count: number;
  kol_count: number;
  kol_content_count: number;
  total_engagement: number;
};

export type VolumeTrendPoint = {
  date: string;
  content_count: number;
  comment_count: number;
  total_volume: number;
};

export type ChannelDistributionItem = {
  channel: string;
  content_count: number;
  comment_count: number;
  total_volume: number;
};

export type KolTypeDistributionItem = {
  kol_main_type: string;
  kol_count: number;
  content_count: number;
  total_engagement: number;
};

export type HotPostItem = {
  content_id: string;
  title: string;
  total_engagement: number;
};

export type MarketDashboardPayload = {
  event: VocEvent;
  overview_metrics: OverviewMetrics;
  volume_trend: VolumeTrendPoint[];
  channel_distribution: ChannelDistributionItem[];
  kol_type_distribution: KolTypeDistributionItem[];
  hot_posts: HotPostItem[];
};
