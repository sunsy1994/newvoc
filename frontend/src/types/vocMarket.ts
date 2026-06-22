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

export type VolumeRhythmSummary = {
  total_volume: number;
  active_days: number;
  peak_date?: string | null;
  peak_volume: number;
  peak_volume_rate: number;
  rhythm_type: string;
  has_secondary_peak: boolean;
  secondary_peak_count: number;
  content_comment_lag_days?: number | null;
  rule_based_conclusion: string;
};

export type VolumeRhythm = {
  summary: VolumeRhythmSummary;
};

export type ChannelDistributionItem = {
  channel: string;
  content_count: number;
  comment_count: number;
  total_volume: number;
};

export type PlatformEfficiencyItem = {
  platform: string;
  content_count: number;
  comment_count: number;
  total_volume: number;
  volume_rate: number;
  total_engagement: number;
  engagement_per_content: number;
  labeled_comment_count: number;
  vehicle_related_count: number;
  effective_comment_rate: number;
  mid_high_purchase_signal_count: number;
  purchase_signal_rate: number;
};

export type PlatformStorySummary = {
  core_platform: string;
  core_platform_volume: number;
  core_platform_volume_rate: number;
  core_platform_engagement_per_content: number;
  core_platform_effective_comment_rate: number;
  core_platform_purchase_signal_rate: number;
  rule_based_conclusion: string;
};

export type PlatformStory = {
  summary: PlatformStorySummary;
  platform_efficiency: PlatformEfficiencyItem[];
};

export type KolTypeDistributionItem = {
  kol_main_type: string;
  kol_count: number;
  content_count: number;
  total_engagement: number;
};

export type SubjectDistributionItem = {
  label: string;
  count: number;
  rate: number;
};

export type SubjectTopAuthorItem = {
  author_id?: string | null;
  author_name: string;
  subject_type: string;
  is_kol?: boolean | null;
  content_count: number;
  comment_count: number;
  total_engagement: number;
};

export type SubjectStorySummary = {
  total_engagement: number;
  total_content_count: number;
  total_comment_count: number;
  dominant_subject_type: string;
  dominant_subject_engagement: number;
  dominant_subject_engagement_rate: number;
  kol_engagement: number;
  kol_engagement_rate: number;
  top_kol_type: string;
  subject_pattern: string;
  rule_based_conclusion: string;
};

export type SubjectStory = {
  summary: SubjectStorySummary;
  subject_distribution: SubjectDistributionItem[];
  kol_type_distribution: KolTypeDistributionItem[];
  top_authors: SubjectTopAuthorItem[];
};

export type UserProfileDistributionItem = {
  main_label: string;
  user_cnt: number;
};

export type CommentQualityDistributionItem = {
  label: string;
  count: number;
  rate: number;
};

export type CommentQualitySummary = {
  labeled_comment_count: number;
  vehicle_related_count: number;
  vehicle_related_rate: number;
  invalid_comment_count?: number | null;
  positive_rate: number;
  negative_rate: number;
  mid_high_purchase_signal_count: number;
  mid_high_purchase_signal_rate: number;
  top_aspect?: string | null;
  top_intent?: string | null;
};

export type CommentQuality = {
  summary: CommentQualitySummary;
  sentiment_distribution: CommentQualityDistributionItem[];
  intent_distribution: CommentQualityDistributionItem[];
  aspect_distribution: CommentQualityDistributionItem[];
  purchase_signal_distribution: CommentQualityDistributionItem[];
};

export type DiscussionPointComment = {
  comment_id: string;
  content_id: string;
  source_title?: string | null;
  platform?: string | null;
  location?: string | null;
  comment_author_id?: string | null;
  comment_author_name: string;
  comment_text: string;
  published_at?: string | null;
  like_cnt: number;
  reply_cnt: number;
  interaction_cnt: number;
  comment_sentiment?: string | null;
  purchase_signal?: string | null;
};

export type DiscussionPointCommentsPayload = {
  aspect: string;
  comments: DiscussionPointComment[];
  total: number;
  limit: number;
  offset: number;
};

export type RegionalLocationItem = {
  location: string;
  comment_count: number;
  comment_rate: number;
  labeled_comment_count: number;
  vehicle_related_count: number;
  effective_comment_rate: number;
  positive_count: number;
  positive_rate: number;
  negative_count: number;
  negative_rate: number;
  mid_high_purchase_signal_count: number;
  purchase_signal_rate: number;
};

export type RegionalTopContentItem = {
  location: string;
  content_id: string;
  title: string;
  platform?: string | null;
  comment_count: number;
  vehicle_related_count: number;
};

export type RegionalResponseStory = {
  summary: {
    data_scope: "comment_location_only";
    top_location: string;
    top_location_comment_count: number;
    top_location_comment_rate: number;
    top_location_effective_comment_rate: number;
    top_location_positive_rate: number;
    top_location_purchase_signal_rate: number;
    rule_based_conclusion: string;
  };
  locations: RegionalLocationItem[];
  top_contents: RegionalTopContentItem[];
};

export type TopicSpreadContentItem = {
  content_id: string;
  title: string;
  platform?: string | null;
  comment_count: number;
  total_engagement: number;
};

export type TopicSpreadItem = {
  topic: string;
  content_count: number;
  comment_count: number;
  labeled_comment_count: number;
  vehicle_related_count: number;
  effective_comment_rate: number;
  positive_rate: number;
  mid_high_purchase_signal_count: number;
  purchase_signal_rate: number;
  total_engagement: number;
  top_contents: TopicSpreadContentItem[];
};

export type TopicSpreadStory = {
  summary: {
    top_topic: string;
    topic_count: number;
    top_topic_content_count: number;
    top_topic_comment_count: number;
    top_topic_effective_comment_rate: number;
    top_topic_purchase_signal_rate: number;
    rule_based_conclusion: string;
  };
  topics: TopicSpreadItem[];
};

export type HotPostItem = {
  content_id: string;
  title: string;
  total_engagement: number;
  comment_peak_bucket?: string | null;
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

export type PostDetailTimelinePoint = {
  time_bucket: string;
  relative_bucket: string;
  comment_count: number;
  interaction_count: number;
};

export type PostDetailPayload = {
  content: PostDetailContent;
  comments: PostDetailComment[];
  comment_timeline: PostDetailTimelinePoint[];
  total: number;
  limit: number;
  offset: number;
  sort: PostDetailSort;
};

export type MarketReportSummary = {
  event_overview: string;
  scale_summary: string;
  topic_summary: string;
  kol_summary: string;
  audience_summary: string;
  feedback_summary: string;
  market_conclusion: string;
  data_limits: string;
};

export type MarketReportAgentPayload = {
  event_id: string;
  prompt_version: string;
  generated_at?: string | null;
  summary: MarketReportSummary;
  context?: unknown;
  rendered_prompt?: string | null;
};

export type MarketDashboardPayload = {
  event: VocEvent;
  overview_metrics: OverviewMetrics;
  volume_trend: VolumeTrendPoint[];
  volume_rhythm?: VolumeRhythm;
  channel_distribution: ChannelDistributionItem[];
  platform_story?: PlatformStory;
  kol_type_distribution: KolTypeDistributionItem[];
  subject_story?: SubjectStory;
  user_profile_distribution: UserProfileDistributionItem[];
  comment_quality?: CommentQuality;
  regional_response_story?: RegionalResponseStory;
  topic_spread_story?: TopicSpreadStory;
  hot_posts: HotPostItem[];
};

export type ProductFocusAspectItem = {
  aspect: string;
  comment_count: number;
  mention_rate: number;
  positive_count: number;
  positive_rate: number;
  negative_count: number;
  negative_rate: number;
  purchase_signal_count: number;
  purchase_signal_rate: number;
  evidence_comments?: ProductEvidenceComment[];
};

export type ProductEvidenceComment = {
  comment_id?: string | null;
  comment_author_name?: string | null;
  comment_text: string;
  published_at?: string | null;
  interaction_cnt?: number | null;
};

export type ProductFocusStory = {
  summary: {
    top_aspect?: string | null;
    aspect_count: number;
    total_mentions: number;
    top_positive_aspect?: string | null;
    top_negative_aspect?: string | null;
    rule_based_conclusion: string;
  };
  aspects: ProductFocusAspectItem[];
};

export type ProductOpportunityItem = {
  aspect: string;
  category: string;
  comment_count: number;
  mention_rate: number;
  positive_rate: number;
  negative_rate: number;
  purchase_signal_rate: number;
  opportunity_score: number;
  score_key: string;
  reason: string;
  evidence_comments?: ProductEvidenceComment[];
};

export type ProductOpportunityStory = {
  summary: {
    surprise_point?: string | null;
    pain_point?: string | null;
    conversion_point?: string | null;
    rule_based_conclusion: string;
  };
  surprise_points: ProductOpportunityItem[];
  pain_points: ProductOpportunityItem[];
  conversion_points: ProductOpportunityItem[];
};

export type ProductPkoDistributionItem = {
  label: string;
  count: number;
  rate: number;
};

export type ProductPkoDimensionResultRow = {
  dimension: string;
  total_count: number;
  advantage_count: number;
  disadvantage_count: number;
  neutral_count: number;
  unclear_count: number;
  top_target?: string | null;
};

export type ProductPkoEvidenceComment = {
  target: string;
  dimension: string;
  result: string;
  reason?: string | null;
  comment_id?: string | null;
  comment_author_name?: string | null;
  comment_text: string;
  published_at?: string | null;
  interaction_cnt: number;
};

export type ProductPkoStory = {
  summary: {
    pko_comment_count: number;
    top_target?: string | null;
    top_explicit_target?: string | null;
    top_dimension?: string | null;
    advantage_dimension?: string | null;
    disadvantage_dimension?: string | null;
    clear_result_count: number;
    clear_result_rate: number;
    explicit_target_count?: number;
    explicit_target_rate?: number;
    generic_target_count?: number;
    generic_target_rate?: number;
    rule_based_conclusion: string;
  };
  target_distribution: ProductPkoDistributionItem[];
  explicit_target_distribution?: ProductPkoDistributionItem[];
  generic_target_summary?: ProductPkoDistributionItem;
  dimension_distribution: ProductPkoDistributionItem[];
  result_distribution: ProductPkoDistributionItem[];
  dimension_result_matrix?: ProductPkoDimensionResultRow[];
  evidence_comments: ProductPkoEvidenceComment[];
};

export type ProductDashboardPayload = {
  event: VocEvent;
  product_focus_story: ProductFocusStory;
  product_opportunity_story: ProductOpportunityStory;
  product_pko_story: ProductPkoStory;
};

export type SalesDistributionItem = {
  label: string;
  count: number;
  rate: number;
};

export type SalesEvidenceComment = {
  comment_id?: string | null;
  comment_author_name?: string | null;
  platform?: string | null;
  comment_text: string;
  published_at?: string | null;
  interaction_cnt: number;
  is_vehicle_related: string;
  comment_intent: string;
  purchase_signal: string;
};

export type SalesLeadQuality = {
  summary: {
    labeled_comment_count: number;
    vehicle_related_count: number;
    vehicle_related_rate: number;
    sales_intent_comment_count: number;
    sales_intent_rate: number;
    mid_high_purchase_signal_count: number;
    mid_high_purchase_signal_rate: number;
    strong_purchase_signal_count: number;
    strong_purchase_signal_rate: number;
    top_intent?: string | null;
    rule_based_conclusion: string;
  };
  intent_distribution: SalesDistributionItem[];
  purchase_signal_distribution: SalesDistributionItem[];
  sankey: SalesLeadSankeyPayload;
  profile_segments: SalesLeadProfileSegment[];
  evidence_comments: SalesEvidenceComment[];
};

export type SalesLeadSankeyNode = {
  id: string;
  label: string;
  layer: number;
};

export type SalesLeadSankeyLink = {
  source: string;
  target: string;
  value: number;
};

export type SalesLeadSankeyPayload = {
  nodes: SalesLeadSankeyNode[];
  links: SalesLeadSankeyLink[];
};

export type SalesLeadProfileDistributionItem = {
  main_label: string;
  user_count: number;
  rate: number;
};

export type SalesLeadProfileUser = {
  comment_user_id: string;
  comment_author_name: string;
  main_label: string;
  main_dimension?: string | null;
  purchase_signal: string;
  comment_count: number;
  mid_high_purchase_signal_count: number;
  representative_comment: string;
};

export type SalesLeadProfileSegment = {
  segment_id: string;
  label: string;
  summary: {
    user_count: number;
    comment_count: number;
    mid_high_purchase_signal_count: number;
    content_count: number;
  };
  profile_distribution: SalesLeadProfileDistributionItem[];
  users: SalesLeadProfileUser[];
};

export type SalesLeadUserInsightRadarLabel = {
  dimension: string;
  label: string;
  score: number;
  support_count: number;
};

export type SalesLeadUserInsightEvidence = {
  dimension: string;
  label: string;
  score: number;
  comment_id?: string | null;
  comment_text: string;
  evidence_text: string;
  reason: string;
};

export type SalesLeadUserInsightComment = {
  comment_id: string;
  content_id?: string | null;
  content_title?: string | null;
  source_url?: string | null;
  platform?: string | null;
  comment_text: string;
  published_at?: string | null;
  like_cnt: number;
  reply_cnt: number;
  interaction_cnt: number;
  comment_intent?: string | null;
  purchase_signal?: string | null;
  comment_sentiment?: string | null;
};

export type SalesLeadUserInsightProfile = {
  user: {
    comment_user_id: string;
    comment_author_name: string;
    platform?: string | null;
    location?: string | null;
  };
  profile_summary: {
    main_dimension?: string | null;
    main_label?: string | null;
    main_score: number;
    total_comments: number;
    valid_comments: number;
    valid_comment_rate: number;
    profile_batch?: string | null;
    prompt_version?: string | null;
    updated_time?: string | null;
  };
  radar_labels: SalesLeadUserInsightRadarLabel[];
  key_evidence: SalesLeadUserInsightEvidence[];
  comments: SalesLeadUserInsightComment[];
};

export type SalesPlatformEfficiencyItem = {
  platform: string;
  comment_count: number;
  high_intent_comment_count: number;
  strong_signal_comment_count: number;
  mid_signal_comment_count: number;
  low_signal_comment_count: number;
  high_intent_rate: number;
};

export type SalesContentLeadItem = {
  content_id: string;
  title: string;
  platform: string;
  author_name: string;
  source_url?: string | null;
  comment_count: number;
  high_intent_comment_count: number;
  strong_signal_comment_count: number;
  dominant_intent: string;
};

export type SalesLeadSourceEfficiency = {
  summary: {
    comment_count: number;
    high_intent_comment_count: number;
    strong_signal_comment_count: number;
    inquiry_comment_count: number;
    source_platform_count: number;
    top_platform?: string | null;
    top_content?: string | null;
    rule_based_conclusion: string;
  };
  platform_efficiency: SalesPlatformEfficiencyItem[];
  content_leads: SalesContentLeadItem[];
  lead_comments: SalesEvidenceComment[];
};

export type SalesDashboardPayload = {
  event: VocEvent;
  sales_lead_quality: SalesLeadQuality;
  sales_lead_source_efficiency: SalesLeadSourceEfficiency;
};

export type AuthorDetailAuthor = {
  author_id: string;
  platform?: string | null;
  author_name?: string | null;
  author_type?: string | null;
  is_kol?: boolean | null;
  author_home_url?: string | null;
  author_desc?: string | null;
  fans_cnt?: number | null;
};

export type AuthorDetailMetrics = {
  event_count: number;
  content_count: number;
  received_comment_count: number;
  total_engagement: number;
};

export type AuthorKolProfile = {
  kol_main_type?: string | null;
  content_tendency?: string | null;
  car_focus?: string | null;
  remark?: string | null;
  profile_batch?: string | null;
  source_file_name?: string | null;
  updated_time?: string | null;
};

export type AuthorEventItem = {
  event_id: string;
  event_name: string;
  event_status?: string | null;
  brand_name?: string | null;
  model_name?: string | null;
  content_count: number;
  received_comment_count: number;
  total_engagement: number;
  first_published_at?: string | null;
  last_published_at?: string | null;
};

export type AuthorContentItem = {
  content_id: string;
  event_id: string;
  event_name?: string | null;
  platform?: string | null;
  source_url?: string | null;
  title: string;
  content_type?: string | null;
  media_form?: string | null;
  published_at?: string | null;
  like_cnt: number;
  comment_cnt: number;
  share_cnt: number;
  favorite_cnt: number;
  view_cnt?: number | null;
  engagement_total: number;
};

export type AuthorSankeyNode = {
  id: string;
  label: string;
  layer: number;
};

export type AuthorSankeyLink = {
  source: string;
  target: string;
  value: number;
};

export type AuthorSankeyPayload = {
  nodes: AuthorSankeyNode[];
  links: AuthorSankeyLink[];
};

export type AuthorDetailPayload = {
  author: AuthorDetailAuthor;
  metrics: AuthorDetailMetrics;
  kol_profile?: AuthorKolProfile;
  events: AuthorEventItem[];
  contents: AuthorContentItem[];
  comment_quality?: CommentQuality;
  sankey: AuthorSankeyPayload;
};
