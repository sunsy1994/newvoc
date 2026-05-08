from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DataSourceTemplate(BaseModel):
    id: str
    source_key: str
    source_name: str
    file_name: str
    formats: list[str]
    description: str
    required_fields: list[str]
    optional_fields: list[str]
    target_table: str
    download_path: str
    exists: bool


class ImportJobResponse(BaseModel):
    job_id: str
    accepted: bool
    message: str
    inserted_rows: int = 0
    rejected_rows: int = 0
    warnings: list[str] = Field(default_factory=list)


class ImportJobRecord(BaseModel):
    job_id: str
    source_key: str
    source_name: str
    template_id: str
    template_name: str
    file_name: str
    file_format: str
    operator: str
    status: Literal["queued", "running", "success", "failed"]
    inserted_rows: int = 0
    rejected_rows: int = 0
    message: str = ""
    created_at: datetime
    updated_at: datetime


class OverviewCard(BaseModel):
    id: str
    label: str
    value: str
    hint: str
    tone: Literal["blue", "emerald", "amber", "slate"]


class DataSourceStatus(BaseModel):
    id: str
    name: str
    type: Literal["excel", "csv", "text", "api"]
    owner: str
    status: Literal["ready", "pending", "error"]
    last_sync_at: str
    record_count: int
    template_id: str
    target_table: str


class PostgresInfo(BaseModel):
    schema_name: str
    current_database: str
    tables: list[str]
    key_interfaces: list[str]


class DataAccessOverviewResponse(BaseModel):
    summary: list[OverviewCard]
    sources: list[DataSourceStatus]
    templates: list[DataSourceTemplate]
    jobs: list[ImportJobRecord]
    postgres: PostgresInfo


class EventAssetItem(BaseModel):
    id: str
    name: str
    description: str
    type: str
    brand: str
    model: str
    keywords: list[str]
    start_date: str | None = None
    end_date: str | None = None
    status: str
    platforms: list[str]
    content_count: int
    comment_count: int
    author_count: int
    kol_count: int
    heat: float
    growth: float
    risk_level: str
    updated_at: str | None = None
    topics: list[str]


class EventAssetDetail(EventAssetItem):
    total_engagement: int = 0
    negative_comment_count: int = 0
    negative_ratio: float = 0
    recent_heat: float = 0
    previous_heat: float = 0


class EventAssetListResponse(BaseModel):
    total: int
    items: list[EventAssetItem]


class EventTrendPoint(BaseModel):
    stat_date: str
    content_count: int
    comment_count: int
    engagement_count: int
    negative_comment_count: int
    heat: float


class ContentDistributionPoint(BaseModel):
    label: str
    value: float


class ContentCommentProfileResponse(BaseModel):
    high_confidence_rate: float = 0
    owner_rate: float = 0
    test_drive_rate: float = 0
    prospect_rate: float = 0
    doubt_rate: float = 0
    approval_rate: float = 0
    positive_rate: float = 0
    negative_rate: float = 0
    stage_top: str = ""
    attitude_top: str = ""
    mindset_distribution: list[ContentDistributionPoint] = Field(default_factory=list)
    emotion_distribution: list[ContentDistributionPoint] = Field(default_factory=list)
    attitude_distribution: list[ContentDistributionPoint] = Field(default_factory=list)
    stage_distribution: list[ContentDistributionPoint] = Field(default_factory=list)


class RepresentativeCommentResponse(BaseModel):
    label: str
    text: str


class ContentAssetItem(BaseModel):
    id: str
    event_id: str | None = None
    event_name: str = ""
    title: str
    summary: str = ""
    source_url: str = ""
    platform: str = ""
    content_type: str = ""
    media_form: str = ""
    author_id: str | None = None
    author_name: str = ""
    author_type: str = ""
    is_kol: bool = False
    kol_domain: str | None = None
    fans_count: int = 0
    published_at: str | None = None
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    favorite_count: int = 0
    engagement_total: int = 0
    content_role: str = ""
    value_level: str = ""
    value_flags: list[str] = Field(default_factory=list)
    value_summary: str = ""
    value_reasons: list[str] = Field(default_factory=list)
    tag_confidence: float = 0
    is_core_content: bool = False
    comment_profile: ContentCommentProfileResponse = Field(default_factory=ContentCommentProfileResponse)
    representative_comments: list[RepresentativeCommentResponse] = Field(default_factory=list)


class ContentAssetListResponse(BaseModel):
    total: int
    items: list[ContentAssetItem]


class CommentAssetItem(BaseModel):
    id: str
    event_id: str | None = None
    content_id: str
    content_title: str = ""
    content_author: str = ""
    content_author_type: str = ""
    from_kol_content: bool = False
    text: str
    platform: str = ""
    published_at: str | None = None
    comment_author_id: str | None = None
    comment_author_name: str = ""
    like_count: int = 0
    interaction_count: int = 0
    reply_level: int = 0
    source_url: str = ""
    mindset_tag: str = ""
    stage_tag: str = ""
    proposition_tag: str = ""
    issue_tag: str = ""
    evidence_tag: str = ""
    sentiment_tag: str = ""
    confidence: float = 0
    labeling_reason: str = ""
    similar_comments: list[str] = Field(default_factory=list)


class CommentAssetListResponse(BaseModel):
    total: int
    items: list[CommentAssetItem]


class AuthorTimelineItem(BaseModel):
    title: str
    published_at: str
    content_type: str
    engagement: int
    comments: int
    proposition_tag: str = ""
    issue_tag: str = ""


class AuthorAssetItem(BaseModel):
    id: str
    event_id: str
    nickname: str
    platform: str = ""
    author_type: str = ""
    is_kol: bool = False
    stage_tag: str = ""
    stage_confidence: float = 0
    stage_reason: str = ""
    posts: int = 0
    total_engagement: int = 0
    comment_trigger_count: int = 0
    top_content_types: list[str] = Field(default_factory=list)
    proposition_top: list[str] = Field(default_factory=list)
    issue_top: list[str] = Field(default_factory=list)
    evidence_strength: float = 0
    evidence_type: str = ""
    reproducible: bool = False
    controversy_score: float = 0
    high_value: bool = False
    high_controversy: bool = False
    high_confidence: bool = False
    role_tags: list[str] = Field(default_factory=list)
    ai_summary: str = ""
    content_timeline: list[AuthorTimelineItem] = Field(default_factory=list)
    representative_contents: list[str] = Field(default_factory=list)
    representative_comments: list[str] = Field(default_factory=list)


class AuthorAssetListResponse(BaseModel):
    total: int
    items: list[AuthorAssetItem]


class KOLRepresentativeComment(BaseModel):
    type: str
    text: str


class KOLAssetItem(BaseModel):
    id: str
    nickname: str
    avatar: str = ""
    platform: str = ""
    fans: int = 0
    domain: str = ""
    author_type: str = ""
    event_id: str
    event_posts: int = 0
    total_engagement: int = 0
    total_comments: int = 0
    avg_engagement: float = 0
    high_confidence_ratio: float = 0
    effective_engagement_rate: float = 0
    risk_score: float = 0
    role_tags: list[str] = Field(default_factory=list)
    mindset_top3: list[str] = Field(default_factory=list)
    stage_top3: list[str] = Field(default_factory=list)
    intention_top3: list[str] = Field(default_factory=list)
    summary: str = ""
    representative_comments: list[KOLRepresentativeComment] = Field(default_factory=list)


class KOLAssetListResponse(BaseModel):
    total: int
    items: list[KOLAssetItem]


class DataLineage(BaseModel):
    tables: list[str] = Field(default_factory=list)
    formula: str = ""


class JourneyStageSummaryItem(BaseModel):
    stage: str
    touchpoint_count: int = 0
    channel_count: int = 0
    negative_ratio: float = 0
    intent_top: list[dict] = Field(default_factory=list)
    issue_top: list[dict] = Field(default_factory=list)
    channel_distribution: list[dict] = Field(default_factory=list)
    representative_touchpoints: list[dict] = Field(default_factory=list)
    data_lineage: DataLineage = Field(default_factory=DataLineage)


class JourneyOverviewResponse(BaseModel):
    brand_name: str = ""
    model_name: str = ""
    stages: list[JourneyStageSummaryItem] = Field(default_factory=list)
    data_lineage: DataLineage = Field(default_factory=DataLineage)


class JourneyMatrixCell(BaseModel):
    source_channel: str
    journey_stage: str
    touchpoint_count: int = 0
    negative_ratio: float = 0
    issue_top: list[dict] = Field(default_factory=list)
    intent_top: list[dict] = Field(default_factory=list)
    data_lineage: DataLineage = Field(default_factory=DataLineage)


class JourneyTouchpointItem(BaseModel):
    id: str
    source_channel: str
    source_system: str = ""
    user_display_name: str = ""
    text: str
    touchpoint_time: str = ""
    brand_name: str = ""
    model_name: str = ""
    city_name: str = ""
    store_name: str = ""
    journey_stage: str
    stage_reason: str = ""
    intent_tag: str = ""
    issue_tag: str = ""
    sentiment_tag: str = ""


class JourneyTouchpointListResponse(BaseModel):
    total: int
    items: list[JourneyTouchpointItem] = Field(default_factory=list)
    data_lineage: DataLineage = Field(default_factory=DataLineage)


class JourneyPainpointItem(BaseModel):
    journey_stage: str
    issue_tag: str
    touchpoint_count: int
    negative_ratio: float
    source_channels: list[dict] = Field(default_factory=list)
    sample_texts: list[dict] = Field(default_factory=list)
    suggested_owner: str = ""
    suggested_action: str = ""
    data_lineage: DataLineage = Field(default_factory=DataLineage)
