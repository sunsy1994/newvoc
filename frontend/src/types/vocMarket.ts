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

export type UserProfileDistributionItem = {
  main_label: string;
  user_cnt: number;
};

export type HotPostItem = {
  content_id: string;
  title: string;
  total_engagement: number;
};

export type PostDetailContent = {
  content_id: string;
  event_id: string;
  platform?: string | null;
  source_url?: string | null;
  title: string;
  content_text?: string | null;
  content_type?: string | null;
  media_form?: string | null;
  published_at?: string | null;
  like_cnt: number;
  comment_cnt: number;
  share_cnt: number;
  favorite_cnt: number;
  view_cnt?: number | null;
  engagement_total: number;
  author_id?: string | null;
  author_name?: string | null;
  author_type?: string | null;
  is_kol?: boolean | null;
  author_home_url?: string | null;
  fans_cnt?: number | null;
};

export type PostDetailComment = {
  comment_id: string;
  content_id: string;
  platform?: string | null;
  location?: string | null;
  comment_author_id?: string | null;
  comment_author_name: string;
  parent_comment_id?: string | null;
  parent_comment_author_name?: string | null;
  comment_text: string;
  published_at?: string | null;
  like_cnt: number;
  reply_cnt: number;
  interaction_cnt: number;
};

export type PostDetailSort = "interaction" | "published_at";

export type PostDetailPayload = {
  content: PostDetailContent;
  comments: PostDetailComment[];
  total: number;
  limit: number;
  offset: number;
  sort: PostDetailSort;
};

export type MarketDashboardPayload = {
  event: VocEvent;
  overview_metrics: OverviewMetrics;
  volume_trend: VolumeTrendPoint[];
  channel_distribution: ChannelDistributionItem[];
  kol_type_distribution: KolTypeDistributionItem[];
  user_profile_distribution: UserProfileDistributionItem[];
  hot_posts: HotPostItem[];
};
