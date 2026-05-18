import json

import pandas as pd

from .database import engine
from .schemas import AuthorAssetItem, AuthorAssetListResponse, AuthorTimelineItem


class AuthorAssetError(Exception):
    pass


def _ensure_engine():
    if engine is None:
        raise AuthorAssetError("DATABASE_URL not configured")
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


def list_author_assets(event_id: str | None = None, include_kol: bool = True) -> AuthorAssetListResponse:
    db_engine = _ensure_engine()
    query = "SELECT * FROM data_asset.ads_author_event_summary"
    df = pd.read_sql(query, db_engine)
    if event_id:
        df = df[df["event_id"] == event_id]
    if not include_kol:
        df = df[df["is_kol"] != True]  # noqa: E712
    df = df.sort_values(["posts", "total_engagement"], ascending=[False, False], na_position="last")

    items = []
    for _, row in df.iterrows():
        timeline = []
        for item in _parse_json_list(row.get("content_timeline_json")):
            if isinstance(item, dict):
                timeline.append(
                    AuthorTimelineItem(
                        title=str(item.get("title", "")),
                        published_at=str(item.get("publishedAt", "")),
                        content_type=str(item.get("contentType", "")),
                        engagement=int(item.get("engagement", 0) or 0),
                        comments=int(item.get("comments", 0) or 0),
                        proposition_tag=str(item.get("propositionTag", "")),
                        issue_tag=str(item.get("issueTag", "")),
                    )
                )
        items.append(
            AuthorAssetItem(
                id=str(row["author_id"]),
                event_id=str(row["event_id"]),
                nickname=str(row.get("nickname", "") or ""),
                platform=str(row.get("platform", "") or ""),
                author_type=str(row.get("author_type", "") or ""),
                is_kol=bool(row.get("is_kol", False)),
                stage_tag=str(row.get("stage_tag", "") or ""),
                stage_confidence=float(row.get("stage_confidence", 0) or 0),
                stage_reason=str(row.get("stage_reason", "") or ""),
                posts=int(row.get("posts", 0) or 0),
                total_engagement=int(row.get("total_engagement", 0) or 0),
                comment_trigger_count=int(row.get("comment_trigger_cnt", 0) or 0),
                top_content_types=[str(v) for v in _parse_json_list(row.get("top_content_types_json"))],
                proposition_top=[str(v) for v in _parse_json_list(row.get("proposition_top_json"))],
                issue_top=[str(v) for v in _parse_json_list(row.get("issue_top_json"))],
                evidence_strength=float(row.get("evidence_strength", 0) or 0),
                evidence_type=str(row.get("evidence_type", "") or ""),
                reproducible=bool(row.get("reproducible_flag", False)),
                controversy_score=float(row.get("controversy_score", 0) or 0),
                high_value=bool(row.get("high_value_flag", False)),
                high_controversy=bool(row.get("high_controversy_flag", False)),
                high_confidence=bool(row.get("high_confidence_flag", False)),
                role_tags=[str(v) for v in _parse_json_list(row.get("role_tags_json"))],
                ai_summary=str(row.get("ai_summary", "") or ""),
                content_timeline=timeline,
                representative_contents=[str(v) for v in _parse_json_list(row.get("representative_contents_json"))],
                representative_comments=[str(v) for v in _parse_json_list(row.get("representative_comments_json"))],
            )
        )
    return AuthorAssetListResponse(total=len(items), items=items)
