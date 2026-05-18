import json

import pandas as pd

from .database import engine
from .schemas import KOLAssetItem, KOLAssetListResponse, KOLRepresentativeComment


class KOLAssetError(Exception):
    pass


def _ensure_engine():
    if engine is None:
        raise KOLAssetError("DATABASE_URL not configured")
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


def list_kol_assets(event_id: str | None = None) -> KOLAssetListResponse:
    db_engine = _ensure_engine()
    df = pd.read_sql("SELECT * FROM data_asset.ads_kol_event_summary", db_engine)
    if event_id:
        df = df[df["event_id"] == event_id]
    df = df.sort_values(["total_engagement", "event_posts"], ascending=[False, False], na_position="last")

    items = []
    for _, row in df.iterrows():
        rep_comments = []
        for item in _parse_json_list(row.get("representative_comments_json")):
            if isinstance(item, dict):
                rep_comments.append(
                    KOLRepresentativeComment(
                        type=str(item.get("type", "")),
                        text=str(item.get("text", "")),
                    )
                )
        items.append(
            KOLAssetItem(
                id=str(row["account_id"]),
                nickname=str(row.get("nickname", "") or ""),
                avatar=str(row.get("avatar_url", "") or ""),
                platform=str(row.get("platform", "") or ""),
                fans=int(row.get("fans_cnt", 0) or 0),
                domain=str(row.get("domain_tag", "") or ""),
                author_type=str(row.get("author_type", "") or ""),
                event_id=str(row["event_id"]),
                event_posts=int(row.get("event_posts", 0) or 0),
                total_engagement=int(row.get("total_engagement", 0) or 0),
                total_comments=int(row.get("total_comments", 0) or 0),
                avg_engagement=float(row.get("avg_engagement", 0) or 0),
                high_confidence_ratio=float(row.get("high_confidence_ratio", 0) or 0),
                effective_engagement_rate=float(row.get("effective_engagement_rate", 0) or 0),
                risk_score=float(row.get("risk_score", 0) or 0),
                role_tags=[str(v) for v in _parse_json_list(row.get("role_tags_json"))],
                mindset_top3=[str(v) for v in _parse_json_list(row.get("mindset_top_json"))],
                stage_top3=[str(v) for v in _parse_json_list(row.get("stage_top_json"))],
                intention_top3=[str(v) for v in _parse_json_list(row.get("intention_top_json"))],
                summary=str(row.get("summary", "") or ""),
                representative_comments=rep_comments,
            )
        )
    return KOLAssetListResponse(total=len(items), items=items)
