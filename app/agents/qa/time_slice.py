from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.asset_library import normalize_row
from app.services.event_voc_insights import (
    build_product_focus_story,
    build_product_opportunity_story,
    build_sales_lead_quality_story,
    build_sales_lead_source_efficiency,
)


def date_bounds(start_date: str, end_date: str) -> tuple[datetime, datetime]:
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("日期必须使用 YYYY-MM-DD 格式。") from exc
    if start > end:
        raise ValueError("开始日期不能晚于结束日期。")
    return start, end + timedelta(days=1)


def _fetch_all(query: str, params: list[object], database_url: str = DATABASE_URL) -> list[dict[str, Any]]:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            return [normalize_row(dict(row)) for row in cur.fetchall()]


def get_market_slice(
    event_id: str,
    start_date: str,
    end_date: str,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    start, end = date_bounds(start_date, end_date)
    summary_rows = _fetch_all(
        """
        WITH content_stats AS (
          SELECT count(*)::bigint AS content_count,
                 coalesce(sum(c.engagement_total), 0)::bigint AS total_engagement
          FROM data_asset.dwd_content c
          WHERE c.event_id = %s AND c.published_at >= %s AND c.published_at < %s
        ), comment_stats AS (
          SELECT count(*)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s AND cm.published_at >= %s AND cm.published_at < %s
        )
        SELECT content_count, total_engagement, comment_count FROM content_stats, comment_stats
        """,
        [event_id, start, end, event_id, start, end],
        database_url,
    )
    trend = _fetch_all(
        """
        WITH content_daily AS (
          SELECT date_trunc('day', c.published_at)::date AS day, count(*)::bigint AS content_count
          FROM data_asset.dwd_content c
          WHERE c.event_id = %s AND c.published_at >= %s AND c.published_at < %s
          GROUP BY 1
        ), comment_daily AS (
          SELECT date_trunc('day', cm.published_at)::date AS day, count(*)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s AND cm.published_at >= %s AND cm.published_at < %s
          GROUP BY 1
        )
        SELECT coalesce(cd.day, md.day) AS day,
               coalesce(cd.content_count, 0)::bigint AS content_count,
               coalesce(md.comment_count, 0)::bigint AS comment_count
        FROM content_daily cd FULL JOIN comment_daily md ON cd.day = md.day
        ORDER BY 1
        """,
        [event_id, start, end, event_id, start, end],
        database_url,
    )
    platforms = _fetch_all(
        """
        WITH scoped_content AS (
          SELECT * FROM data_asset.dwd_content
          WHERE event_id = %s AND published_at >= %s AND published_at < %s
        )
        SELECT coalesce(nullif(c.platform, ''), '未标注平台') AS platform,
               count(DISTINCT c.content_id)::bigint AS content_count,
               count(DISTINCT cm.comment_id)::bigint AS comment_count
        FROM scoped_content c
        LEFT JOIN data_asset.dwd_comment cm ON cm.content_id = c.content_id
          AND cm.published_at >= %s AND cm.published_at < %s
        GROUP BY 1 ORDER BY content_count DESC, comment_count DESC, platform
        """,
        [event_id, start, end, start, end],
        database_url,
    )
    hot_posts = _fetch_all(
        """
        SELECT c.content_id, c.title, c.platform, c.source_url, c.published_at,
               coalesce(c.engagement_total, 0)::bigint AS total_engagement
        FROM data_asset.dwd_content c
        WHERE c.event_id = %s AND c.published_at >= %s AND c.published_at < %s
        ORDER BY c.engagement_total DESC NULLS LAST, c.published_at DESC NULLS LAST
        LIMIT 10
        """,
        [event_id, start, end],
        database_url,
    )
    return {
        "summary": summary_rows[0] if summary_rows else {"content_count": 0, "comment_count": 0, "total_engagement": 0},
        "volume_trend": trend,
        "platform_distribution": platforms,
        "hot_posts": hot_posts,
    }


def get_product_slice(
    event_id: str,
    start_date: str,
    end_date: str,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    start, end = date_bounds(start_date, end_date)
    rows = _fetch_all(
        """
        WITH aspect_rows AS (
          SELECT aspect, cm.comment_label_json ->> 'comment_sentiment' AS sentiment,
                 cm.comment_label_json ->> 'purchase_signal' AS purchase_signal,
                 cm.comment_id, cm.comment_author_name, cm.comment_text, cm.published_at, cm.interaction_cnt
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          CROSS JOIN LATERAL jsonb_array_elements_text(
            CASE WHEN jsonb_typeof(cm.comment_label_json -> 'mentioned_aspect') = 'array'
              THEN cm.comment_label_json -> 'mentioned_aspect'
              WHEN cm.comment_label_json ? 'mentioned_aspect'
              THEN jsonb_build_array(cm.comment_label_json ->> 'mentioned_aspect')
              ELSE '[]'::jsonb END
          ) AS aspect
          WHERE c.event_id = %s AND cm.published_at >= %s AND cm.published_at < %s
            AND cm.comment_label_json IS NOT NULL AND coalesce(aspect, '') <> ''
        ), ranked AS (
          SELECT *, row_number() OVER (
            PARTITION BY aspect ORDER BY interaction_cnt DESC NULLS LAST, published_at DESC NULLS LAST, comment_id
          ) AS rn FROM aspect_rows
        )
        SELECT aspect, count(*)::bigint AS comment_count,
               count(*) FILTER (WHERE sentiment = '正向')::bigint AS positive_count,
               count(*) FILTER (WHERE sentiment = '负向')::bigint AS negative_count,
               count(*) FILTER (WHERE purchase_signal IN ('中', '强'))::bigint AS purchase_signal_count,
               coalesce(jsonb_agg(jsonb_build_object(
                 'comment_id', comment_id, 'comment_author_name', comment_author_name,
                 'comment_text', comment_text, 'published_at', published_at,
                 'interaction_cnt', interaction_cnt
               ) ORDER BY interaction_cnt DESC NULLS LAST, published_at DESC NULLS LAST) FILTER (WHERE rn <= 8), '[]'::jsonb) AS evidence_comments
        FROM ranked GROUP BY aspect
        ORDER BY comment_count DESC, positive_count DESC, negative_count DESC, aspect LIMIT 20
        """,
        [event_id, start, end],
        database_url,
    )
    focus = build_product_focus_story(rows)
    return {
        "product_focus_story": focus,
        "product_opportunity_story": build_product_opportunity_story(focus.get("aspects") or []),
    }


def get_sales_slice(
    event_id: str,
    start_date: str,
    end_date: str,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    start, end = date_bounds(start_date, end_date)
    rows = _fetch_all(
        """
        SELECT coalesce(nullif(cm.comment_label_json ->> 'is_vehicle_related', ''), '未标注') AS is_vehicle_related,
               coalesce(nullif(cm.comment_label_json ->> 'comment_intent', ''), '未标注') AS comment_intent,
               coalesce(nullif(cm.comment_label_json ->> 'purchase_signal', ''), '未标注') AS purchase_signal,
               coalesce(nullif(c.platform, ''), coalesce(nullif(cm.platform, ''), '未标注平台')) AS platform,
               c.content_id, coalesce(nullif(c.title, ''), '未命名内容') AS title, c.source_url,
               coalesce(nullif(a.author_name, ''), '未标注作者') AS author_name,
               cm.comment_id, cm.location, cm.comment_author_name, cm.comment_text,
               cm.published_at, cm.interaction_cnt
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        LEFT JOIN data_asset.dwd_author a ON c.author_id = a.author_id
        WHERE c.event_id = %s AND cm.published_at >= %s AND cm.published_at < %s
          AND cm.comment_label_json IS NOT NULL
        ORDER BY cm.interaction_cnt DESC NULLS LAST, cm.published_at DESC NULLS LAST, cm.comment_id
        LIMIT 3000
        """,
        [event_id, start, end],
        database_url,
    )
    return {
        "sales_lead_quality": build_sales_lead_quality_story(rows),
        "sales_lead_source_efficiency": build_sales_lead_source_efficiency(rows),
    }


def get_discussion_slice(
    event_id: str,
    aspect: str,
    start_date: str,
    end_date: str,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    start, end = date_bounds(start_date, end_date)
    rows = _fetch_all(
        """
        SELECT cm.comment_id, cm.comment_author_name, cm.comment_text, cm.published_at, cm.interaction_cnt,
               count(*) OVER ()::bigint AS total
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        CROSS JOIN LATERAL jsonb_array_elements_text(
          CASE WHEN jsonb_typeof(cm.comment_label_json -> 'mentioned_aspect') = 'array'
            THEN cm.comment_label_json -> 'mentioned_aspect'
            WHEN cm.comment_label_json ? 'mentioned_aspect'
            THEN jsonb_build_array(cm.comment_label_json ->> 'mentioned_aspect')
            ELSE '[]'::jsonb END
        ) AS mentioned_aspect
        WHERE c.event_id = %s AND cm.published_at >= %s AND cm.published_at < %s
          AND mentioned_aspect = %s
        ORDER BY cm.interaction_cnt DESC NULLS LAST, cm.published_at DESC NULLS LAST, cm.comment_id
        LIMIT 20
        """,
        [event_id, start, end, aspect],
        database_url,
    )
    total = int(rows[0].get("total") or 0) if rows else 0
    for row in rows:
        row.pop("total", None)
    return {"total": total, "comments": rows}
