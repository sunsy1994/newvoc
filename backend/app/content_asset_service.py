import json

import pandas as pd

from .database import engine
from .schemas import (
    ContentAssetItem,
    ContentAssetListResponse,
    ContentCommentProfileResponse,
    ContentDistributionPoint,
    RepresentativeCommentResponse,
)


class ContentAssetError(Exception):
    pass


def _ensure_engine():
    if engine is None:
        raise ContentAssetError("DATABASE_URL not configured")
    return engine


def _parse_json_list(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _parse_distribution(value) -> list[ContentDistributionPoint]:
    items = _parse_json_list(value)
    result: list[ContentDistributionPoint] = []
    for item in items:
        if isinstance(item, dict):
            result.append(
                ContentDistributionPoint(
                    label=str(item.get("label", "")),
                    value=float(item.get("value", 0) or 0),
                )
            )
    return result


def _parse_comments(value) -> list[RepresentativeCommentResponse]:
    items = _parse_json_list(value)
    result: list[RepresentativeCommentResponse] = []
    for item in items:
        if isinstance(item, dict):
            result.append(
                RepresentativeCommentResponse(
                    label=str(item.get("label", "")),
                    text=str(item.get("text", "")),
                )
            )
    return result


def _row_to_item(row: pd.Series) -> ContentAssetItem:
    return ContentAssetItem(
        id=str(row.get("content_id", "")),
        event_id=row.get("event_id"),
        event_name=str(row.get("event_name", "") or ""),
        title=str(row.get("title", "") or ""),
        summary=str(row.get("content_text", "") or ""),
        source_url=str(row.get("source_url", "") or ""),
        platform=str(row.get("platform", "") or ""),
        content_type=str(row.get("content_type", "") or ""),
        media_form=str(row.get("media_form", "") or ""),
        author_id=row.get("author_id"),
        author_name=str(row.get("author_name", "") or ""),
        author_type=str(row.get("author_type", "") or ""),
        is_kol=bool(row.get("is_kol", False)),
        kol_domain=row.get("kol_domain"),
        fans_count=int(row.get("fans_cnt", 0) or 0),
        published_at=pd.Timestamp(row.get("published_at")).strftime("%Y-%m-%d %H:%M:%S") if pd.notna(row.get("published_at")) else None,
        like_count=int(row.get("like_cnt", 0) or 0),
        comment_count=int(row.get("comment_cnt", 0) or 0),
        share_count=int(row.get("share_cnt", 0) or 0),
        favorite_count=int(row.get("favorite_cnt", 0) or 0),
        engagement_total=int(row.get("engagement_total", 0) or 0),
        content_role=str(row.get("content_role", "") or ""),
        value_level=str(row.get("value_level", "") or ""),
        value_flags=[str(item) for item in _parse_json_list(row.get("value_flags_json"))],
        value_summary=str(row.get("value_summary", "") or ""),
        value_reasons=[str(item) for item in _parse_json_list(row.get("value_reason_json"))],
        tag_confidence=round(float(row.get("tag_confidence", 0) or 0), 4),
        is_core_content=bool(row.get("is_core_content", False)),
        comment_profile=ContentCommentProfileResponse(
            high_confidence_rate=float(row.get("high_confidence_rate", 0) or 0),
            owner_rate=float(row.get("owner_rate", 0) or 0),
            test_drive_rate=float(row.get("test_drive_rate", 0) or 0),
            prospect_rate=float(row.get("prospect_rate", 0) or 0),
            doubt_rate=float(row.get("doubt_rate", 0) or 0),
            approval_rate=float(row.get("approval_rate", 0) or 0),
            positive_rate=float(row.get("positive_rate", 0) or 0),
            negative_rate=float(row.get("negative_rate", 0) or 0),
            stage_top=str(row.get("stage_top1", "") or ""),
            attitude_top=str(row.get("attitude_top1", "") or ""),
            mindset_distribution=_parse_distribution(row.get("mindset_distribution_json")),
            emotion_distribution=_parse_distribution(row.get("emotion_distribution_json")),
            attitude_distribution=_parse_distribution(row.get("attitude_distribution_json")),
            stage_distribution=_parse_distribution(row.get("stage_distribution_json")),
        ),
        representative_comments=_parse_comments(row.get("representative_comments_json")),
    )


def list_content_assets(event_id: str | None = None) -> ContentAssetListResponse:
    db_engine = _ensure_engine()
    query = """
        SELECT
          c.content_id, rel.event_id, e.event_name, c.title, c.content_text, c.source_url,
          c.platform, c.content_type, c.media_form, c.author_id, c.author_name, c.author_type,
          c.is_kol, c.kol_domain, c.fans_cnt, c.published_at, c.like_cnt, c.comment_cnt,
          c.share_cnt, c.favorite_cnt, c.engagement_total,
          v.content_role, v.value_level, v.value_flags_json, v.value_summary, v.value_reason_json,
          v.tag_confidence, v.is_core_content, v.representative_comments_json,
          p.high_confidence_rate, p.owner_rate, p.test_drive_rate, p.prospect_rate,
          p.doubt_rate, p.approval_rate, p.positive_rate, p.negative_rate,
          p.stage_top1, p.attitude_top1, p.mindset_distribution_json, p.emotion_distribution_json,
          p.attitude_distribution_json, p.stage_distribution_json
        FROM data_asset.dwd_content c
        LEFT JOIN data_asset.rel_event_content rel ON rel.content_id = c.content_id
        LEFT JOIN data_asset.dwd_event e ON e.event_id = rel.event_id
        LEFT JOIN data_asset.ads_content_value_summary v ON v.content_id = c.content_id
        LEFT JOIN data_asset.fact_content_comment_profile_di p ON p.content_id = c.content_id
    """
    df = pd.read_sql(query, db_engine)
    if event_id:
        df = df[df["event_id"] == event_id]
    df = df.sort_values(["engagement_total", "published_at"], ascending=[False, False], na_position="last")
    return ContentAssetListResponse(total=len(df), items=[_row_to_item(row) for _, row in df.iterrows()])
