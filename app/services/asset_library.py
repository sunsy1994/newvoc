from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL


@dataclass(frozen=True)
class AssetDefinition:
    key: str
    label: str
    columns: list[dict[str, str]]
    from_sql: str
    search_columns: list[str]
    order_sql: str


ASSET_DEFINITIONS: dict[str, AssetDefinition] = {
    "events": AssetDefinition(
        key="events",
        label="事件资产",
        columns=[
            {"key": "event_name", "label": "事件名称"},
            {"key": "event_type", "label": "事件类型"},
            {"key": "brand_name", "label": "品牌"},
            {"key": "model_name", "label": "车型"},
            {"key": "start_time", "label": "开始时间"},
            {"key": "end_time", "label": "结束时间"},
            {"key": "event_status", "label": "状态"},
            {"key": "content_cnt", "label": "内容数"},
            {"key": "comment_cnt", "label": "评论数"},
            {"key": "author_cnt", "label": "作者数"},
            {"key": "kol_content_cnt", "label": "KOL内容数"},
            {"key": "total_engagement", "label": "总互动量"},
        ],
        from_sql="FROM data_asset.ads_event_overview e",
        search_columns=["e.event_name", "e.event_type", "e.brand_name", "e.model_name"],
        order_sql="e.start_time DESC NULLS LAST, e.event_name ASC",
    ),
    "contents": AssetDefinition(
        key="contents",
        label="内容资产",
        columns=[
            {"key": "event_name", "label": "所属事件"},
            {"key": "platform", "label": "平台"},
            {"key": "title", "label": "标题"},
            {"key": "content_type", "label": "内容类型"},
            {"key": "media_form", "label": "媒介形态"},
            {"key": "author_name", "label": "作者名称"},
            {"key": "is_kol", "label": "是否KOL"},
            {"key": "published_at", "label": "发布时间"},
            {"key": "like_cnt", "label": "点赞数"},
            {"key": "comment_cnt", "label": "评论数"},
            {"key": "share_cnt", "label": "分享数"},
            {"key": "favorite_cnt", "label": "收藏数"},
            {"key": "engagement_total", "label": "总互动量"},
            {"key": "source_url", "label": "原始链接"},
        ],
        from_sql=(
            "FROM data_asset.dwd_content c "
            "LEFT JOIN data_asset.dwd_event e ON c.event_id = e.event_id "
            "LEFT JOIN data_asset.dwd_author a ON c.author_id = a.author_id"
        ),
        search_columns=["e.event_name", "c.platform", "c.title", "a.author_name", "c.content_type", "c.media_form"],
        order_sql="c.published_at DESC NULLS LAST, c.engagement_total DESC",
    ),
    "comments": AssetDefinition(
        key="comments",
        label="评论资产",
        columns=[
            {"key": "event_name", "label": "所属事件"},
            {"key": "content_title", "label": "所属内容标题"},
            {"key": "platform", "label": "平台"},
            {"key": "location", "label": "位置"},
            {"key": "comment_author_name", "label": "评论作者昵称"},
            {"key": "comment_text", "label": "评论正文"},
            {"key": "published_at", "label": "评论时间"},
            {"key": "like_cnt", "label": "点赞数"},
            {"key": "reply_cnt", "label": "回复数"},
        ],
        from_sql=(
            "FROM data_asset.dwd_comment cm "
            "LEFT JOIN data_asset.dwd_content c ON cm.content_id = c.content_id "
            "LEFT JOIN data_asset.dwd_event e ON c.event_id = e.event_id"
        ),
        search_columns=["e.event_name", "c.title", "cm.platform", "cm.location", "cm.comment_author_name", "cm.comment_text"],
        order_sql="cm.published_at DESC NULLS LAST",
    ),
    "authors": AssetDefinition(
        key="authors",
        label="作者KOL资产",
        columns=[
            {"key": "platform", "label": "平台"},
            {"key": "author_name", "label": "作者名称"},
            {"key": "author_type", "label": "作者类型"},
            {"key": "is_kol", "label": "是否KOL"},
            {"key": "fans_cnt", "label": "粉丝数"},
            {"key": "author_home_url", "label": "作者主页"},
            {"key": "author_desc", "label": "作者简介"},
            {"key": "content_cnt", "label": "内容数"},
            {"key": "total_engagement", "label": "总互动量"},
        ],
        from_sql=(
            "FROM data_asset.dwd_author a "
            "LEFT JOIN data_asset.dwd_content c ON a.author_id = c.author_id"
        ),
        search_columns=["a.platform", "a.author_name", "a.author_type", "a.author_desc"],
        order_sql="total_engagement DESC NULLS LAST, content_cnt DESC NULLS LAST",
    ),
}


SELECT_SQL = {
    "events": "SELECT event_name, event_type, brand_name, model_name, start_time, end_time, event_status, content_cnt, comment_cnt, author_cnt, kol_content_cnt, total_engagement",
    "contents": "SELECT e.event_name, c.platform, c.title, c.content_type, c.media_form, a.author_name, a.is_kol, c.published_at, c.like_cnt, c.comment_cnt, c.share_cnt, c.favorite_cnt, c.engagement_total, c.source_url",
    "comments": "SELECT e.event_name, c.title AS content_title, cm.platform, cm.location, cm.comment_author_name, cm.comment_text, cm.published_at, cm.like_cnt, cm.reply_cnt",
    "authors": "SELECT a.platform, a.author_name, a.author_type, a.is_kol, a.fans_cnt, a.author_home_url, a.author_desc, count(DISTINCT c.content_id) AS content_cnt, coalesce(sum(c.engagement_total), 0) AS total_engagement",
}

GROUP_SQL = {
    "authors": "GROUP BY a.platform, a.author_name, a.author_type, a.is_kol, a.fans_cnt, a.author_home_url, a.author_desc",
}


def build_like_pattern(query: str) -> str:
    text = query.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{text}%"


def list_assets(asset_key: str, q: str | None = None, limit: int = 50, offset: int = 0, database_url: str = DATABASE_URL) -> dict[str, Any]:
    if asset_key not in ASSET_DEFINITIONS:
        raise KeyError(asset_key)
    definition = ASSET_DEFINITIONS[asset_key]
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    where_sql = ""
    params: list[Any] = []
    if q and q.strip():
        like_pattern = build_like_pattern(q)
        where_parts = [f"coalesce({column}::text, '') ILIKE %s ESCAPE '\\'" for column in definition.search_columns]
        where_sql = " WHERE " + " OR ".join(where_parts)
        params.extend([like_pattern] * len(where_parts))
    group_sql = f" {GROUP_SQL[asset_key]}" if asset_key in GROUP_SQL else ""
    count_sql = f"SELECT count(*) FROM (SELECT 1 {definition.from_sql}{where_sql}{group_sql}) asset_count"
    data_sql = (
        f"{SELECT_SQL[asset_key]} {definition.from_sql}{where_sql}{group_sql} "
        f"ORDER BY {definition.order_sql} LIMIT %s OFFSET %s"
    )
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(count_sql, params)
            total = cur.fetchone()["count"]
            cur.execute(data_sql, [*params, limit, offset])
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return {
        "asset": asset_key,
        "label": definition.label,
        "total": int(total),
        "columns": definition.columns,
        "rows": rows,
    }


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in row.items():
        if value is None:
            normalized[key] = ""
        elif hasattr(value, "isoformat"):
            normalized[key] = value.isoformat()
        else:
            normalized[key] = value
    return normalized
