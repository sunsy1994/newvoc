from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.report_time import format_shanghai_datetime


@dataclass(frozen=True)
class AssetDefinition:
    key: str
    label: str
    columns: list[dict[str, str]]
    from_sql: str
    search_columns: list[str]
    order_sql: str
    base_where: str = ""


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
        label="作者资产",
        columns=[
            {"key": "platform", "label": "平台"},
            {"key": "author_name", "label": "作者名称"},
            {"key": "author_type", "label": "作者类型"},
            {"key": "fans_cnt", "label": "粉丝数"},
            {"key": "author_home_url", "label": "作者主页"},
            {"key": "author_desc", "label": "作者简介"},
            {"key": "content_cnt", "label": "主贴数"},
            {"key": "received_comment_cnt", "label": "收到评论数"},
            {"key": "total_engagement", "label": "总互动量"},
        ],
        from_sql=(
            "FROM data_asset.dwd_author a "
            "LEFT JOIN ("
            "  SELECT c.author_id, count(DISTINCT c.content_id) AS content_cnt, "
            "         coalesce(sum(c.engagement_total), 0) AS total_engagement "
            "  FROM data_asset.dwd_content c "
            "  GROUP BY c.author_id"
            ") s ON a.author_id = s.author_id "
            "LEFT JOIN ("
            "  SELECT c.author_id, count(DISTINCT cm.comment_id) AS received_comment_cnt "
            "  FROM data_asset.dwd_content c "
            "  LEFT JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id "
            "  GROUP BY c.author_id"
            ") r ON a.author_id = r.author_id"
        ),
        search_columns=["a.platform", "a.author_name", "a.author_type", "a.author_desc"],
        order_sql="total_engagement DESC NULLS LAST, content_cnt DESC NULLS LAST",
        base_where="(a.is_kol = false OR a.is_kol IS NULL)",
    ),
    "kols": AssetDefinition(
        key="kols",
        label="KOL资产",
        columns=[
            {"key": "platform", "label": "平台"},
            {"key": "author_name", "label": "作者名称"},
            {"key": "author_type", "label": "作者类型"},
            {"key": "fans_cnt", "label": "粉丝数"},
            {"key": "author_home_url", "label": "作者主页"},
            {"key": "author_desc", "label": "作者简介"},
            {"key": "content_cnt", "label": "主贴数"},
            {"key": "received_comment_cnt", "label": "收到评论数"},
            {"key": "total_engagement", "label": "总互动量"},
        ],
        from_sql=(
            "FROM data_asset.dwd_author a "
            "LEFT JOIN ("
            "  SELECT c.author_id, count(DISTINCT c.content_id) AS content_cnt, "
            "         coalesce(sum(c.engagement_total), 0) AS total_engagement "
            "  FROM data_asset.dwd_content c "
            "  GROUP BY c.author_id"
            ") s ON a.author_id = s.author_id "
            "LEFT JOIN ("
            "  SELECT c.author_id, count(DISTINCT cm.comment_id) AS received_comment_cnt "
            "  FROM data_asset.dwd_content c "
            "  LEFT JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id "
            "  GROUP BY c.author_id"
            ") r ON a.author_id = r.author_id"
        ),
        search_columns=["a.platform", "a.author_name", "a.author_type", "a.author_desc"],
        order_sql="total_engagement DESC NULLS LAST, content_cnt DESC NULLS LAST",
        base_where="a.is_kol = true",
    ),
    "comment_users": AssetDefinition(
        key="comment_users",
        label="评论用户资产",
        columns=[
            {"key": "platform", "label": "平台"},
            {"key": "comment_author_name", "label": "评论用户昵称"},
            {"key": "location", "label": "位置"},
            {"key": "comment_cnt", "label": "评论数"},
            {"key": "participated_content_cnt", "label": "参与主贴数"},
            {"key": "participated_event_cnt", "label": "参与事件数"},
            {"key": "like_cnt", "label": "获赞数"},
            {"key": "reply_cnt", "label": "回复数"},
            {"key": "latest_comment_at", "label": "最近评论时间"},
        ],
        from_sql=(
            "FROM data_asset.dwd_comment cm "
            "LEFT JOIN data_asset.dwd_content c ON cm.content_id = c.content_id"
        ),
        search_columns=["cm.platform", "cm.comment_author_name", "cm.location"],
        order_sql="comment_cnt DESC NULLS LAST, latest_comment_at DESC NULLS LAST",
    ),
    "reports": AssetDefinition(
        key="reports",
        label="报告资产",
        columns=[
            {"key": "report_type", "label": "报告类型"},
            {"key": "subject_name", "label": "报告对象"},
            {"key": "generated_at", "label": "生成时间"},
            {"key": "report_run_id", "label": "报告编号"},
            {"key": "view_kind", "label": "查看方式"},
        ],
        from_sql="",
        search_columns=["subject_name"],
        order_sql="generated_at DESC NULLS LAST, report_type, report_run_id DESC",
    ),
}


REPORT_ASSET_UNION_SQL = """
SELECT
    'event_report'::text AS report_type,
    coalesce(e.event_name, r.event_id) AS subject_name,
    r.generated_at,
    r.report_run_id,
    'structured'::text AS view_kind
FROM data_asset.event_report_agent_run r
LEFT JOIN data_asset.dwd_event e ON r.event_id = e.event_id
UNION ALL
SELECT
    'competitor_report'::text AS report_type,
    r.brand_name AS subject_name,
    r.generated_at,
    r.report_run_id,
    'html'::text AS view_kind
FROM data_asset.competitor_report_agent_run r
WHERE r.status = 'completed'
"""


SELECT_SQL = {
    "events": "SELECT event_name, event_type, brand_name, model_name, start_time, end_time, event_status, content_cnt, comment_cnt, author_cnt, kol_content_cnt, total_engagement",
    "contents": "SELECT e.event_name, c.platform, c.title, c.content_type, c.media_form, a.author_name, a.is_kol, c.published_at, c.like_cnt, c.comment_cnt, c.share_cnt, c.favorite_cnt, c.engagement_total, c.source_url",
    "comments": "SELECT e.event_name, c.title AS content_title, cm.platform, cm.location, cm.comment_author_name, cm.comment_text, cm.published_at, cm.like_cnt, cm.reply_cnt",
    "authors": "SELECT a.platform, a.author_name, a.author_type, a.fans_cnt, a.author_home_url, a.author_desc, coalesce(s.content_cnt, 0) AS content_cnt, coalesce(r.received_comment_cnt, 0) AS received_comment_cnt, coalesce(s.total_engagement, 0) AS total_engagement",
    "kols": "SELECT a.platform, a.author_name, a.author_type, a.fans_cnt, a.author_home_url, a.author_desc, coalesce(s.content_cnt, 0) AS content_cnt, coalesce(r.received_comment_cnt, 0) AS received_comment_cnt, coalesce(s.total_engagement, 0) AS total_engagement",
    "comment_users": "SELECT cm.platform, cm.comment_author_name, coalesce(nullif(cm.location, ''), '') AS location, count(DISTINCT cm.comment_id) AS comment_cnt, count(DISTINCT cm.content_id) AS participated_content_cnt, count(DISTINCT c.event_id) AS participated_event_cnt, coalesce(sum(cm.like_cnt), 0) AS like_cnt, coalesce(sum(cm.reply_cnt), 0) AS reply_cnt, max(cm.published_at) AS latest_comment_at",
    "reports": "SELECT report_type, subject_name, generated_at, report_run_id, view_kind",
}

GROUP_SQL = {
    "comment_users": "GROUP BY cm.platform, cm.comment_author_name, coalesce(nullif(cm.location, ''), '')",
}


def build_like_pattern(query: str) -> str:
    text = query.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{text}%"


def list_assets(
    asset_key: str,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    database_url: str = DATABASE_URL,
    max_limit: int = 200,
) -> dict[str, Any]:
    if asset_key not in ASSET_DEFINITIONS:
        raise KeyError(asset_key)
    if asset_key == "reports":
        return list_report_assets(q=q, limit=limit, offset=offset, database_url=database_url, max_limit=max_limit)
    definition = ASSET_DEFINITIONS[asset_key]
    limit = max(1, min(limit, max_limit))
    offset = max(0, offset)
    where_clauses = []
    params: list[Any] = []
    if definition.base_where:
        where_clauses.append(definition.base_where)
    if q and q.strip():
        like_pattern = build_like_pattern(q)
        where_parts = [f"coalesce({column}::text, '') ILIKE %s ESCAPE '\\'" for column in definition.search_columns]
        where_clauses.append("(" + " OR ".join(where_parts) + ")")
        params.extend([like_pattern] * len(where_parts))
    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""
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


def list_report_assets(
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    database_url: str = DATABASE_URL,
    max_limit: int = 200,
) -> dict[str, Any]:
    definition = ASSET_DEFINITIONS["reports"]
    limit = max(1, min(limit, max_limit))
    offset = max(0, offset)
    search_sql = ""
    params: list[Any] = []
    if q and q.strip():
        search_sql = " WHERE coalesce(subject_name, '') ILIKE %s ESCAPE '\\'"
        params.append(build_like_pattern(q))
    count_sql = f"WITH report_assets AS ({REPORT_ASSET_UNION_SQL}) SELECT count(*) FROM report_assets{search_sql}"
    data_sql = (
        f"WITH report_assets AS ({REPORT_ASSET_UNION_SQL}) "
        f"SELECT report_type, subject_name, generated_at, report_run_id, view_kind FROM report_assets{search_sql} "
        "ORDER BY generated_at DESC NULLS LAST, report_type, report_run_id DESC LIMIT %s OFFSET %s"
    )
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(count_sql, params)
            total = cur.fetchone()["count"]
            cur.execute(data_sql, [*params, limit, offset])
            rows = [_normalize_report_row(dict(row)) for row in cur.fetchall()]
    return {
        "asset": "reports",
        "label": definition.label,
        "total": int(total),
        "columns": definition.columns,
        "rows": rows,
    }


def get_report_asset(
    report_type: str,
    report_run_id: int,
    database_url: str = DATABASE_URL,
) -> dict[str, Any] | None:
    if report_type not in {"event_report", "competitor_report"}:
        raise KeyError(report_type)
    if report_run_id <= 0:
        raise ValueError("report_run_id must be positive")

    if report_type == "event_report":
        query = """
            SELECT 'event_report'::text AS report_type, r.report_run_id,
                   coalesce(e.event_name, r.event_id) AS subject_name, r.generated_at,
                   'structured'::text AS view_kind, r.summary_json
            FROM data_asset.event_report_agent_run r
            LEFT JOIN data_asset.dwd_event e ON r.event_id = e.event_id
            WHERE r.report_run_id = %s
        """
    else:
        query = """
            SELECT 'competitor_report'::text AS report_type, r.report_run_id,
                   r.brand_name AS subject_name, r.generated_at,
                   'html'::text AS view_kind, r.html
            FROM data_asset.competitor_report_agent_run r
            WHERE r.report_run_id = %s AND r.status = 'completed'
        """

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, [report_run_id])
            row = cur.fetchone()
    if row is None:
        return None

    normalized = _normalize_report_row(dict(row))
    if report_type == "event_report":
        summary = normalized.pop("summary_json", {})
        normalized["structured_report"] = summary.get("structured_report", {}) if isinstance(summary, dict) else {}
    return normalized


def _normalize_report_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_row(row)
    if "generated_at" in row:
        normalized["generated_at"] = format_shanghai_datetime(row["generated_at"])
    return normalized


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    normalized = {}
    for key, value in row.items():
        if value is None:
            normalized[key] = ""
        elif isinstance(value, Decimal):
            normalized[key] = int(value) if value == value.to_integral_value() else float(value)
        elif hasattr(value, "isoformat"):
            normalized[key] = value.isoformat()
        else:
            normalized[key] = value
    return normalized
