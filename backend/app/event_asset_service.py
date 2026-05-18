import json
from datetime import timedelta

import pandas as pd
from sqlalchemy import text

from .database import engine
from .schemas import EventAssetDetail, EventAssetItem, EventAssetListResponse, EventTrendPoint


class EventAssetError(Exception):
    pass


SORT_FIELD_MAP = {
    "updatedAt": "updated_time",
    "updated_at": "updated_time",
    "contentCount": "content_cnt",
    "content_count": "content_cnt",
    "commentCount": "comment_cnt",
    "comment_count": "comment_cnt",
    "authorCount": "author_cnt",
    "author_count": "author_cnt",
    "heat": "heat_score",
    "growth": "growth_rate",
}


def _ensure_engine():
    if engine is None:
        raise EventAssetError("DATABASE_URL not configured")
    return engine


def _load_json_list(value) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    if isinstance(value, str):
        text_value = value.strip()
        if not text_value:
            return []
        if text_value.startswith("["):
            try:
                parsed = json.loads(text_value)
                return [str(item) for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass
        return [item.strip() for item in text_value.replace("，", "|").replace(",", "|").split("|") if item.strip()]
    return [str(value)]


def _format_dt(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    ts = pd.Timestamp(value)
    return ts.strftime("%Y-%m-%d")


def _format_dt_full(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    ts = pd.Timestamp(value)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def _row_to_item(row: pd.Series) -> EventAssetItem:
    return EventAssetItem(
        id=str(row.get("event_id", "")),
        name=str(row.get("event_name", "")),
        description=str(row.get("event_desc", "") or ""),
        type=str(row.get("event_type", "") or ""),
        brand=str(row.get("brand_name", "") or ""),
        model=str(row.get("model_name", "") or ""),
        keywords=_load_json_list(row.get("keyword_list")),
        start_date=_format_dt(row.get("start_time")),
        end_date=_format_dt(row.get("end_time")),
        status=str(row.get("event_status", "") or ""),
        platforms=_load_json_list(row.get("platform_list")),
        content_count=int(row.get("content_cnt", 0) or 0),
        comment_count=int(row.get("comment_cnt", 0) or 0),
        author_count=int(row.get("author_cnt", 0) or 0),
        kol_count=int(row.get("kol_cnt", 0) or 0),
        heat=round(float(row.get("heat_score", 0) or 0), 1),
        growth=round(float(row.get("growth_rate", 0) or 0), 1),
        risk_level=str(row.get("risk_level", "") or "低"),
        updated_at=_format_dt_full(row.get("updated_time")),
        topics=_load_json_list(row.get("topic_top_json")),
    )


def _row_to_detail(row: pd.Series) -> EventAssetDetail:
    item = _row_to_item(row)
    return EventAssetDetail(
        **item.model_dump(),
        total_engagement=int(row.get("total_engagement", 0) or 0),
        negative_comment_count=int(row.get("negative_comment_cnt", 0) or 0),
        negative_ratio=round(float(row.get("negative_ratio", 0) or 0), 4),
        recent_heat=round(float(row.get("recent_heat", 0) or 0), 2),
        previous_heat=round(float(row.get("prev_heat", 0) or 0), 2),
    )


def _read_overview() -> pd.DataFrame:
    db_engine = _ensure_engine()
    query = """
        SELECT *
        FROM data_asset.ads_event_asset_overview
    """
    return pd.read_sql(query, db_engine)


def list_event_assets(
    *,
    keyword: str | None = None,
    event_type: str | None = None,
    event_status: str | None = None,
    brand_name: str | None = None,
    platform: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = "updatedAt",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 50,
) -> EventAssetListResponse:
    overview = _read_overview()
    if overview.empty:
        return EventAssetListResponse(total=0, items=[])

    if keyword:
        q = keyword.strip().lower()
        keyword_series = (
            overview["event_name"].fillna("").str.lower()
            + " "
            + overview["brand_name"].fillna("").str.lower()
            + " "
            + overview["model_name"].fillna("").str.lower()
            + " "
            + overview["keyword_list"].fillna("").astype(str).str.lower()
        )
        overview = overview[keyword_series.str.contains(q, na=False)]

    if event_type:
        overview = overview[overview["event_type"] == event_type]
    if event_status:
        overview = overview[overview["event_status"] == event_status]
    if brand_name:
        overview = overview[overview["brand_name"] == brand_name]
    if platform:
        overview = overview[
            overview["platform_list"].apply(lambda value: platform in _load_json_list(value))
        ]

    if date_from:
        overview = overview[pd.to_datetime(overview["updated_time"]) >= pd.Timestamp(date_from)]
    if date_to:
        overview = overview[pd.to_datetime(overview["updated_time"]) <= pd.Timestamp(date_to) + timedelta(days=1)]

    sort_field = SORT_FIELD_MAP.get(sort_by, "updated_time")
    ascending = sort_order.lower() == "asc"
    overview = overview.sort_values(sort_field, ascending=ascending, na_position="last")

    total = len(overview)
    start = max(0, (page - 1) * page_size)
    end = start + page_size
    page_df = overview.iloc[start:end]

    return EventAssetListResponse(
        total=total,
        items=[_row_to_item(row) for _, row in page_df.iterrows()],
    )


def get_event_asset_detail(event_id: str) -> EventAssetDetail:
    overview = _read_overview()
    if overview.empty:
        raise EventAssetError(f"Event not found: {event_id}")
    matched = overview[overview["event_id"] == event_id]
    if matched.empty:
        raise EventAssetError(f"Event not found: {event_id}")
    return _row_to_detail(matched.iloc[0])


def get_event_asset_trend(event_id: str) -> list[EventTrendPoint]:
    db_engine = _ensure_engine()
    query = text(
        """
        SELECT stat_date, content_cnt, comment_cnt, engagement_cnt, negative_comment_cnt, heat_score
        FROM data_asset.ads_event_trend_daily
        WHERE event_id = :event_id
        ORDER BY stat_date ASC
        """
    )
    with db_engine.begin() as conn:
        trend = pd.read_sql(query, conn, params={"event_id": event_id})

    return [
        EventTrendPoint(
            stat_date=_format_dt(row["stat_date"]) or "",
            content_count=int(row.get("content_cnt", 0) or 0),
            comment_count=int(row.get("comment_cnt", 0) or 0),
            engagement_count=int(row.get("engagement_cnt", 0) or 0),
            negative_comment_count=int(row.get("negative_comment_cnt", 0) or 0),
            heat=round(float(row.get("heat_score", 0) or 0), 2),
        )
        for _, row in trend.iterrows()
    ]
