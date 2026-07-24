from __future__ import annotations

from collections import Counter, defaultdict
from datetime import date, datetime
import re
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.asset_library import build_like_pattern, normalize_row
from app.services.profile_library import build_comment_user_id


def list_voc_events(
    q: str | None = None,
    limit: int = 20,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    limit = max(1, min(limit, 100))
    clauses = []
    params: list[Any] = []
    if q and q.strip():
        like_pattern = build_like_pattern(q)
        clauses.append(
            "(coalesce(event_name, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(brand_name, '') ILIKE %s ESCAPE '\\' OR "
            "coalesce(model_name, '') ILIKE %s ESCAPE '\\')"
        )
        params.extend([like_pattern, like_pattern, like_pattern])
    where_sql = " WHERE " + " AND ".join(clauses) if clauses else ""
    query = (
        "SELECT event_id, event_name, event_type, brand_name, model_name, start_time, end_time, event_status, "
        "content_cnt, comment_cnt, author_cnt, kol_content_cnt, total_engagement, top_platform_json "
        "FROM data_asset.ads_event_overview "
        f"{where_sql} "
        "ORDER BY start_time DESC NULLS LAST, total_engagement DESC NULLS LAST LIMIT %s"
    )
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, [*params, limit])
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return {"events": rows}


def get_voc_event_detail(event_id: str, database_url: str = DATABASE_URL) -> dict[str, Any]:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        overview = fetch_event_overview(conn, event_id)
        top_contents = fetch_event_top_contents(conn, event_id)
        kol_voice = fetch_event_kol_voice(conn, event_id)
        profile_rows = fetch_latest_comment_user_profiles(conn, event_id)
    user_profiles = summarize_user_profiles(profile_rows)
    kol_user_matrix = summarize_kol_user_matrix(kol_voice, profile_rows)
    return {
        "event_id": event_id,
        "overview": overview,
        "top_contents": top_contents,
        "kol_voice": kol_voice,
        "user_profiles": user_profiles,
        "kol_user_matrix": kol_user_matrix,
        "asset_counts": {
            "events": 1 if overview else 0,
            "contents": overview.get("content_cnt", 0) if overview else 0,
            "comments": overview.get("comment_cnt", 0) if overview else 0,
            "kols": len(kol_voice),
            "comment_user_profiles": sum(item["user_cnt"] for item in user_profiles),
        },
    }


def get_voc_event_market_dashboard(event_id: str, database_url: str = DATABASE_URL) -> dict[str, Any]:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        overview = fetch_event_overview(conn, event_id)
        trend = fetch_event_volume_trend(conn, event_id)
        channel_distribution = fetch_event_channel_distribution(conn, event_id)
        platform_story = fetch_event_platform_story(conn, event_id)
        kol_type_distribution = fetch_event_kol_type_distribution(conn, event_id)
        subject_story = fetch_event_subject_story(conn, event_id, kol_type_distribution)
        profile_rows = fetch_latest_comment_user_profiles(conn, event_id)
        hot_posts = fetch_event_hot_posts(conn, event_id)
        comment_quality = fetch_event_comment_quality(conn, event_id)
        regional_response_story = fetch_event_regional_response_story(conn, event_id)
        topic_spread_story = fetch_event_topic_spread_story(conn, event_id)
    return {
        "event": overview,
        "overview_metrics": build_market_overview_metrics(overview, kol_type_distribution),
        "volume_trend": trend,
        "volume_rhythm": build_volume_rhythm_story(trend),
        "channel_distribution": channel_distribution,
        "platform_story": platform_story,
        "kol_type_distribution": kol_type_distribution,
        "subject_story": subject_story,
        "user_profile_distribution": summarize_user_profiles(profile_rows),
        "comment_quality": comment_quality,
        "regional_response_story": regional_response_story,
        "topic_spread_story": topic_spread_story,
        "hot_posts": hot_posts,
    }


def get_voc_event_product_dashboard(event_id: str, database_url: str = DATABASE_URL) -> dict[str, Any]:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        overview = fetch_event_overview(conn, event_id)
        product_focus_story = fetch_event_product_focus_story(conn, event_id)
        product_pko_story = fetch_event_product_pko_story(conn, event_id)
    return {
        "event": overview,
        "product_focus_story": product_focus_story,
        "product_opportunity_story": build_product_opportunity_story(product_focus_story.get("aspects", [])),
        "product_pko_story": product_pko_story,
    }


def get_voc_event_sales_dashboard(event_id: str, database_url: str = DATABASE_URL) -> dict[str, Any]:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        overview = fetch_event_overview(conn, event_id)
        sales_lead_quality = fetch_event_sales_lead_quality(conn, event_id)
        sales_lead_source_efficiency = fetch_event_sales_lead_source_efficiency(conn, event_id)
    return {
        "event": overview,
        "sales_lead_quality": sales_lead_quality,
        "sales_lead_source_efficiency": sales_lead_source_efficiency,
    }


def get_voc_event_comment_user_insight_profile(
    event_id: str,
    comment_user_id: str,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        profile = fetch_comment_user_profile(conn, comment_user_id)
        label_scores = fetch_comment_user_label_scores(conn, comment_user_id, profile.get("profile_batch"))
        comments = fetch_event_comment_user_comments(conn, event_id, comment_user_id)
    return build_comment_user_insight_profile(profile, label_scores, comments)


def get_voc_author_detail(author_id: str, database_url: str = DATABASE_URL) -> dict[str, Any]:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        author_payload = fetch_author_base(conn, author_id)
        author = author_payload["author"]
        if not author:
            return {"author": {}}
        metrics = fetch_author_metrics(conn, author_id)
        events = fetch_author_events(conn, author_id)
        contents = fetch_author_contents(conn, author_id)
        comment_quality = fetch_author_comment_quality(conn, author_id)
        sankey_rows = fetch_author_sankey_rows(conn, author_id)
        profile_map = fetch_latest_profile_label_map(conn, sorted({row["comment_user_id"] for row in sankey_rows}))
        sankey = build_author_profile_sankey(author_id, author.get("author_name") or "未知作者", sankey_rows, profile_map)
    return {
        "author": author,
        "metrics": metrics,
        "kol_profile": author_payload["kol_profile"],
        "events": events,
        "contents": contents,
        "comment_quality": comment_quality,
        "sankey": sankey,
    }


def get_voc_event_content_detail(
    event_id: str,
    content_id: str,
    sort: str = "interaction",
    limit: int = 10,
    offset: int = 0,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    sort = sort if sort in {"interaction", "published_at"} else "interaction"
    limit = max(1, min(limit, 100))
    offset = max(0, offset)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        content = fetch_event_content(conn, event_id, content_id)
        if not content:
            return {"content": {}, "comments": [], "comment_timeline": [], "total": 0, "limit": limit, "offset": offset, "sort": sort}
        comments, total = fetch_event_content_comments(conn, content_id, sort=sort, limit=limit, offset=offset)
        comment_timeline = fetch_event_content_comment_timeline(conn, content_id, content.get("published_at"))
    return {
        "content": content,
        "comments": comments,
        "comment_timeline": comment_timeline,
        "total": total,
        "limit": limit,
        "offset": offset,
        "sort": sort,
    }


def get_voc_event_discussion_point_comments(
    event_id: str,
    aspect: str,
    limit: int = 20,
    offset: int = 0,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    safe_limit = max(1, min(int(limit or 20), 100))
    safe_offset = max(0, int(offset or 0))
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        comments, total = fetch_event_discussion_point_comments(conn, event_id, aspect, limit=safe_limit, offset=safe_offset)
    return {
        "aspect": aspect,
        "comments": comments,
        "total": total,
        "limit": safe_limit,
        "offset": safe_offset,
    }


def build_market_overview_metrics(
    overview: dict[str, Any],
    kol_type_distribution: list[dict[str, Any]],
) -> dict[str, Any]:
    content_count = int(overview.get("content_cnt") or 0)
    comment_count = int(overview.get("comment_cnt") or 0)
    return {
        "total_volume": content_count + comment_count,
        "content_count": content_count,
        "comment_count": comment_count,
        "kol_count": sum(int(row.get("kol_count") or 0) for row in kol_type_distribution),
        "kol_content_count": int(overview.get("kol_content_cnt") or 0),
        "total_engagement": int(overview.get("total_engagement") or 0),
    }


def build_volume_rhythm_story(trend: list[dict[str, Any]]) -> dict[str, Any]:
    active_points = [point for point in trend if int(point.get("total_volume") or 0) > 0]
    if not active_points:
        return {
            "summary": {
                "total_volume": 0,
                "active_days": 0,
                "peak_date": None,
                "peak_volume": 0,
                "peak_volume_rate": 0,
                "rhythm_type": "鏆傛棤鏁版嵁",
                "has_secondary_peak": False,
                "secondary_peak_count": 0,
                "content_comment_lag_days": None,
                "rule_based_conclusion": "缺少发布时间趋势数据，暂时无法判断传播规模与节奏。",
            }
        }

    total_volume = sum(int(point.get("total_volume") or 0) for point in active_points)
    peak = max(active_points, key=lambda point: int(point.get("total_volume") or 0))
    peak_volume = int(peak.get("total_volume") or 0)
    peak_rate = round(peak_volume * 100 / total_volume, 1) if total_volume else 0
    peak_date = str(peak.get("date") or "")

    secondary_peaks = [
        point
        for point in active_points
        if point is not peak
        and int(point.get("total_volume") or 0) >= peak_volume * 0.5
        and abs(days_between(str(point.get("date") or ""), peak_date) or 0) > 1
    ]
    active_days = len(active_points)
    if secondary_peaks:
        rhythm_type = "二次传播"
    elif peak_rate >= 50:
        rhythm_type = "集中爆发"
    elif active_days >= 5 and peak_rate <= 40:
        rhythm_type = "持续发酵"
    else:
        rhythm_type = "平稳扩散"

    content_peak = max(active_points, key=lambda point: int(point.get("content_count") or 0))
    comment_peak = max(active_points, key=lambda point: int(point.get("comment_count") or 0))
    lag_days = days_between(str(comment_peak.get("date") or ""), str(content_peak.get("date") or ""))
    lag_text = build_lag_text(lag_days)
    secondary_text = "观察到二次传播峰值。" if secondary_peaks else "未观察到明显二次传播。"
    conclusion = (
        f"本事件累计声量 {total_volume:,}，传播节奏呈现「{rhythm_type}」；"
        f"峰值出现在 {peak_date}，当日贡献 {peak_rate}% 声量。{lag_text}{secondary_text}"
    )

    return {
        "summary": {
            "total_volume": total_volume,
            "active_days": active_days,
            "peak_date": peak_date,
            "peak_volume": peak_volume,
            "peak_volume_rate": peak_rate,
            "rhythm_type": rhythm_type,
            "has_secondary_peak": bool(secondary_peaks),
            "secondary_peak_count": len(secondary_peaks),
            "content_comment_lag_days": lag_days,
            "rule_based_conclusion": conclusion,
        }
    }


def parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value[:10])
    except (TypeError, ValueError):
        return None


def days_between(later: str, earlier: str) -> int | None:
    later_date = parse_date(later)
    earlier_date = parse_date(earlier)
    if not later_date or not earlier_date:
        return None
    return (later_date - earlier_date).days


def build_lag_text(lag_days: int | None) -> str:
    if lag_days is None:
        return ""
    if lag_days > 0:
        return f"评论峰值滞后主贴峰值 {lag_days} 天，说明内容发布后进入用户讨论。"
    if lag_days < 0:
        return f"评论峰值早于主贴峰值 {abs(lag_days)} 天，说明用户讨论先于内容集中发布。"
    return "主贴峰值与评论峰值同日出现，说明内容发布和用户讨论同步爆发。"


def fetch_event_overview(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    query = """
        SELECT event_id, event_name, event_type, brand_name, model_name, start_time, end_time, event_status,
               content_cnt, comment_cnt, author_cnt, kol_content_cnt, total_engagement,
               top_platform_json, top_author_json, updated_time
        FROM data_asset.ads_event_overview
        WHERE event_id = %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        row = cur.fetchone()
    return normalize_row(dict(row)) if row else {}


def fetch_event_volume_trend(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    query = """
        WITH content_daily AS (
          SELECT date_trunc('day', published_at)::date AS day, count(*)::bigint AS content_count
          FROM data_asset.dwd_content
          WHERE event_id = %s AND published_at IS NOT NULL
          GROUP BY 1
        ),
        comment_daily AS (
          SELECT date_trunc('day', cm.published_at)::date AS day, count(*)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s AND cm.published_at IS NOT NULL
          GROUP BY 1
        ),
        days AS (
          SELECT day FROM content_daily
          UNION
          SELECT day FROM comment_daily
        )
        SELECT day::text AS date,
               coalesce(content_count, 0) AS content_count,
               coalesce(comment_count, 0) AS comment_count,
               coalesce(content_count, 0) + coalesce(comment_count, 0) AS total_volume
        FROM days
        LEFT JOIN content_daily USING (day)
        LEFT JOIN comment_daily USING (day)
        ORDER BY day
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, event_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_event_channel_distribution(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    query = """
        WITH content_channel AS (
          SELECT coalesce(nullif(platform, ''), '未知渠道') AS channel, count(*)::bigint AS content_count
          FROM data_asset.dwd_content
          WHERE event_id = %s
          GROUP BY 1
        ),
        comment_channel AS (
          SELECT coalesce(nullif(c.platform, ''), nullif(cm.platform, ''), '未知渠道') AS channel,
                 count(*)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s
          GROUP BY 1
        ),
        channels AS (
          SELECT channel FROM content_channel
          UNION
          SELECT channel FROM comment_channel
        )
        SELECT channel,
               coalesce(content_count, 0) AS content_count,
               coalesce(comment_count, 0) AS comment_count,
               coalesce(content_count, 0) + coalesce(comment_count, 0) AS total_volume
        FROM channels
        LEFT JOIN content_channel USING (channel)
        LEFT JOIN comment_channel USING (channel)
        ORDER BY total_volume DESC, channel
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, event_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_event_kol_type_distribution(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    query = """
        WITH latest_kol_profile AS (
          SELECT DISTINCT ON (author_id)
                 author_id, kol_main_type, updated_time
          FROM data_asset.user_profile_kol
          ORDER BY author_id, updated_time DESC NULLS LAST
        )
        SELECT coalesce(nullif(p.kol_main_type, ''), '尚未维护KOL画像') AS kol_main_type,
               count(DISTINCT a.author_id)::bigint AS kol_count,
               count(DISTINCT c.content_id)::bigint AS content_count,
               coalesce(sum(c.engagement_total), 0)::bigint AS total_engagement
        FROM data_asset.dwd_content c
        JOIN data_asset.dwd_author a ON c.author_id = a.author_id
        LEFT JOIN latest_kol_profile p ON a.author_id = p.author_id
        WHERE c.event_id = %s AND a.is_kol = true
        GROUP BY 1
        ORDER BY kol_count DESC, content_count DESC, total_engagement DESC
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_event_hot_posts(conn: psycopg.Connection, event_id: str, limit: int = 10) -> list[dict[str, Any]]:
    query = """
        SELECT content_id, title, published_at, coalesce(engagement_total, 0)::bigint AS total_engagement
        FROM data_asset.dwd_content
        WHERE event_id = %s
        ORDER BY engagement_total DESC NULLS LAST, published_at DESC NULLS LAST
        LIMIT %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, limit])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    for row in rows:
        timeline = fetch_event_content_comment_timeline(conn, row.get("content_id"), row.get("published_at"))
        row["comment_peak_bucket"] = describe_comment_peak_bucket(timeline)
        row.pop("published_at", None)
    return rows


def fetch_event_comment_quality(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    summary_query = """
        WITH labeled AS (
          SELECT cm.comment_label_json AS label_json
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s
            AND cm.comment_label_json IS NOT NULL
        )
        SELECT
          count(*)::bigint AS labeled_comment_count,
          count(*) FILTER (WHERE label_json ->> 'is_vehicle_related' = '是')::bigint AS vehicle_related_count,
          round(100.0 * count(*) FILTER (WHERE label_json ->> 'is_vehicle_related' = '是') / nullif(count(*), 0), 1) AS vehicle_related_rate,
          round(100.0 * count(*) FILTER (WHERE label_json ->> 'comment_sentiment' = '正向') / nullif(count(*), 0), 1) AS positive_rate,
          round(100.0 * count(*) FILTER (WHERE label_json ->> 'comment_sentiment' = '负向') / nullif(count(*), 0), 1) AS negative_rate,
          count(*) FILTER (WHERE label_json ->> 'purchase_signal' IN ('中', '强'))::bigint AS mid_high_purchase_signal_count,
          round(100.0 * count(*) FILTER (WHERE label_json ->> 'purchase_signal' IN ('中', '强')) / nullif(count(*), 0), 1) AS mid_high_purchase_signal_rate
        FROM labeled
    """
    sentiment_query = """
        SELECT coalesce(nullif(comment_label_json ->> 'comment_sentiment', ''), '未标注') AS label,
               count(*)::bigint AS count
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE c.event_id = %s AND cm.comment_label_json IS NOT NULL
        GROUP BY 1
        ORDER BY count DESC, label
    """
    intent_query = """
        SELECT coalesce(nullif(comment_label_json ->> 'comment_intent', ''), '未标注') AS label,
               count(*)::bigint AS count
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE c.event_id = %s AND cm.comment_label_json IS NOT NULL
        GROUP BY 1
        ORDER BY count DESC, label
    """
    purchase_query = """
        SELECT coalesce(nullif(comment_label_json ->> 'purchase_signal', ''), '未标注') AS label,
               count(*)::bigint AS count
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE c.event_id = %s AND cm.comment_label_json IS NOT NULL
        GROUP BY 1
        ORDER BY
          CASE coalesce(nullif(comment_label_json ->> 'purchase_signal', ''), '未标注')
            WHEN '强' THEN 1
            WHEN '中' THEN 2
            WHEN '弱' THEN 3
            WHEN '无' THEN 4
            ELSE 5
          END,
          count DESC
    """
    aspect_query = """
        SELECT aspect AS label, count(*)::bigint AS count
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        CROSS JOIN LATERAL jsonb_array_elements_text(
          CASE
            WHEN jsonb_typeof(cm.comment_label_json -> 'mentioned_aspect') = 'array'
              THEN cm.comment_label_json -> 'mentioned_aspect'
            WHEN cm.comment_label_json ? 'mentioned_aspect'
              THEN jsonb_build_array(cm.comment_label_json ->> 'mentioned_aspect')
            ELSE '[]'::jsonb
          END
        ) AS aspect
        WHERE c.event_id = %s AND cm.comment_label_json IS NOT NULL
        GROUP BY aspect
        ORDER BY count DESC, aspect
        LIMIT 20
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(summary_query, [event_id])
        summary = normalize_row(dict(cur.fetchone() or {}))
        cur.execute(sentiment_query, [event_id])
        sentiment_distribution = build_rate_distribution([normalize_row(dict(row)) for row in cur.fetchall()])
        cur.execute(intent_query, [event_id])
        intent_distribution = build_rate_distribution([normalize_row(dict(row)) for row in cur.fetchall()])
        cur.execute(aspect_query, [event_id])
        aspect_distribution = build_rate_distribution([normalize_row(dict(row)) for row in cur.fetchall()])
        cur.execute(purchase_query, [event_id])
        purchase_signal_distribution = build_rate_distribution([normalize_row(dict(row)) for row in cur.fetchall()])

    summary.setdefault("labeled_comment_count", 0)
    summary.setdefault("vehicle_related_count", 0)
    summary.setdefault("vehicle_related_rate", 0)
    summary.setdefault("positive_rate", 0)
    summary.setdefault("negative_rate", 0)
    summary.setdefault("mid_high_purchase_signal_count", 0)
    summary.setdefault("mid_high_purchase_signal_rate", 0)
    summary["top_aspect"] = aspect_distribution[0]["label"] if aspect_distribution else None
    summary["top_intent"] = intent_distribution[0]["label"] if intent_distribution else None
    return {
        "summary": summary,
        "sentiment_distribution": sentiment_distribution,
        "intent_distribution": intent_distribution,
        "aspect_distribution": aspect_distribution,
        "purchase_signal_distribution": purchase_signal_distribution,
    }


def fetch_event_discussion_point_comments(
    conn: psycopg.Connection,
    event_id: str,
    aspect: str,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    query = """
        WITH matched_comments AS (
          SELECT cm.comment_id,
                 cm.content_id,
                 c.title AS source_title,
                 cm.platform,
                 cm.location,
                 cm.comment_author_id,
                 cm.comment_author_name,
                 cm.comment_text,
                 cm.published_at,
                 coalesce(cm.like_cnt, 0)::bigint AS like_cnt,
                 coalesce(cm.reply_cnt, 0)::bigint AS reply_cnt,
                 coalesce(cm.interaction_cnt, 0)::bigint AS interaction_cnt,
                 coalesce(nullif(cm.comment_label_json ->> 'comment_sentiment', ''), '') AS comment_sentiment,
                 coalesce(nullif(cm.comment_label_json ->> 'purchase_signal', ''), '') AS purchase_signal
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          CROSS JOIN LATERAL jsonb_array_elements_text(
            CASE
              WHEN jsonb_typeof(cm.comment_label_json -> 'mentioned_aspect') = 'array'
                THEN cm.comment_label_json -> 'mentioned_aspect'
              WHEN cm.comment_label_json ? 'mentioned_aspect'
                THEN jsonb_build_array(cm.comment_label_json ->> 'mentioned_aspect')
              ELSE '[]'::jsonb
            END
          ) AS matched_aspect
          WHERE c.event_id = %s
            AND cm.comment_label_json IS NOT NULL
            AND matched_aspect = %s
        )
        SELECT *, count(*) OVER()::bigint AS total_count
        FROM matched_comments
        ORDER BY interaction_cnt DESC NULLS LAST, published_at DESC NULLS LAST, comment_id
        LIMIT %s OFFSET %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, aspect, limit, offset])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    total = int(rows[0].get("total_count") or 0) if rows else 0
    for row in rows:
        row.pop("total_count", None)
    return rows, total


def fetch_event_regional_response_story(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    location_query = """
        SELECT coalesce(nullif(trim(cm.location), ''), '未知地区') AS location,
               count(*)::bigint AS comment_count,
               count(*) FILTER (WHERE cm.comment_label_json IS NOT NULL)::bigint AS labeled_comment_count,
               count(*) FILTER (WHERE cm.comment_label_json ->> 'is_vehicle_related' = '是')::bigint AS vehicle_related_count,
               count(*) FILTER (WHERE cm.comment_label_json ->> 'comment_sentiment' = '正向')::bigint AS positive_count,
               count(*) FILTER (WHERE cm.comment_label_json ->> 'comment_sentiment' = '负向')::bigint AS negative_count,
               count(*) FILTER (WHERE cm.comment_label_json ->> 'purchase_signal' IN ('中', '强'))::bigint AS mid_high_purchase_signal_count
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE c.event_id = %s
        GROUP BY 1
        ORDER BY comment_count DESC, location
        LIMIT 20
    """
    top_content_query = """
        WITH base AS (
          SELECT coalesce(nullif(trim(cm.location), ''), '未知地区') AS location,
                 c.content_id,
                 c.title,
                 c.platform,
                 count(*)::bigint AS comment_count,
                 count(*) FILTER (WHERE cm.comment_label_json ->> 'is_vehicle_related' = '是')::bigint AS vehicle_related_count,
                 row_number() OVER (
                   PARTITION BY coalesce(nullif(trim(cm.location), ''), '未知地区')
                   ORDER BY count(*) DESC, c.engagement_total DESC NULLS LAST, c.published_at DESC NULLS LAST
                 ) AS row_no
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s
          GROUP BY 1, c.content_id, c.title, c.platform, c.engagement_total, c.published_at
        )
        SELECT location, content_id, title, platform, comment_count, vehicle_related_count
        FROM base
        WHERE row_no <= 2
        ORDER BY location, comment_count DESC
        LIMIT 16
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(location_query, [event_id])
        location_rows = [normalize_row(dict(row)) for row in cur.fetchall()]
        cur.execute(top_content_query, [event_id])
        top_contents = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_regional_response_story(location_rows, top_contents)


def build_regional_response_story(
    location_rows: list[dict[str, Any]],
    top_contents: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    total_comments = sum(int(row.get("comment_count") or 0) for row in location_rows)
    if not location_rows or total_comments == 0:
        return {
            "summary": {
                "data_scope": "comment_location_only",
                "top_location": "鏆傛棤鏁版嵁",
                "top_location_comment_count": 0,
                "top_location_comment_rate": 0,
                "top_location_effective_comment_rate": 0,
                "top_location_positive_rate": 0,
                "top_location_purchase_signal_rate": 0,
                "rule_based_conclusion": "暂无评论位置数据。地区响应只基于评论位置统计，不代表主贴发布地区。",
            },
            "locations": [],
            "top_contents": [],
        }

    locations = []
    for row in location_rows:
        comment_count = int(row.get("comment_count") or 0)
        labeled_count = int(row.get("labeled_comment_count") or 0)
        vehicle_related = int(row.get("vehicle_related_count") or 0)
        positive_count = int(row.get("positive_count") or 0)
        negative_count = int(row.get("negative_count") or 0)
        purchase_signal = int(row.get("mid_high_purchase_signal_count") or 0)
        locations.append(
            {
                "location": row.get("location") or "未知地区",
                "comment_count": comment_count,
                "comment_rate": round(comment_count * 100 / total_comments, 1) if total_comments else 0,
                "labeled_comment_count": labeled_count,
                "vehicle_related_count": vehicle_related,
                "effective_comment_rate": round(vehicle_related * 100 / labeled_count, 1) if labeled_count else 0,
                "positive_count": positive_count,
                "positive_rate": round(positive_count * 100 / labeled_count, 1) if labeled_count else 0,
                "negative_count": negative_count,
                "negative_rate": round(negative_count * 100 / labeled_count, 1) if labeled_count else 0,
                "mid_high_purchase_signal_count": purchase_signal,
                "purchase_signal_rate": round(purchase_signal * 100 / labeled_count, 1) if labeled_count else 0,
            }
        )

    top_location = locations[0]
    conclusion = (
        f"评论响应最集中在「{top_location['location']}」，贡献 {top_location['comment_rate']}% 评论；"
        f"该地区有效评论率 {top_location['effective_comment_rate']}%，"
        f"正向率 {top_location['positive_rate']}%，中/强购买信号 {top_location['purchase_signal_rate']}%。"
        "地区统计基于评论用户位置，不代表内容发布地。"
    )
    return {
        "summary": {
            "data_scope": "comment_location_only",
            "top_location": top_location["location"],
            "top_location_comment_count": top_location["comment_count"],
            "top_location_comment_rate": top_location["comment_rate"],
            "top_location_effective_comment_rate": top_location["effective_comment_rate"],
            "top_location_positive_rate": top_location["positive_rate"],
            "top_location_purchase_signal_rate": top_location["purchase_signal_rate"],
            "rule_based_conclusion": conclusion,
        },
        "locations": locations,
        "top_contents": top_contents or [],
    }


TOPIC_PATTERN = re.compile(r"#([^#\s,锛屻€傦紱;锛?銆?\\]+)")


def extract_hash_topics(*values: Any) -> list[str]:
    topics: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value is None:
            continue
        text = str(value)
        for raw_topic in TOPIC_PATTERN.findall(text):
            topic = raw_topic.strip().strip("#").strip()
            if not topic or topic in seen:
                continue
            seen.add(topic)
            topics.append(topic)
    return topics


def fetch_event_topic_spread_story(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    query = """
        SELECT c.content_id,
               c.title,
               c.content_text,
               c.platform,
               coalesce(c.engagement_total, 0)::bigint AS total_engagement,
               count(cm.comment_id)::bigint AS comment_count,
               count(cm.comment_id) FILTER (WHERE cm.comment_label_json IS NOT NULL)::bigint AS labeled_comment_count,
               count(cm.comment_id) FILTER (WHERE cm.comment_label_json ->> 'is_vehicle_related' = '是')::bigint AS vehicle_related_count,
               count(cm.comment_id) FILTER (WHERE cm.comment_label_json ->> 'comment_sentiment' = '正向')::bigint AS positive_count,
               count(cm.comment_id) FILTER (WHERE cm.comment_label_json ->> 'purchase_signal' IN ('中', '强'))::bigint AS mid_high_purchase_signal_count
        FROM data_asset.dwd_content c
        LEFT JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id
        WHERE c.event_id = %s
        GROUP BY c.content_id, c.title, c.content_text, c.platform, c.engagement_total
        ORDER BY c.engagement_total DESC NULLS LAST, c.published_at DESC NULLS LAST
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_topic_spread_story(rows)


def build_topic_spread_story(content_rows: list[dict[str, Any]]) -> dict[str, Any]:
    topic_map: dict[str, dict[str, Any]] = {}
    for row in content_rows:
        topics = extract_hash_topics(row.get("title"), row.get("content_text"))
        if not topics:
            continue
        for topic in topics:
            bucket = topic_map.setdefault(
                topic,
                {
                    "topic": topic,
                    "content_ids": set(),
                    "content_count": 0,
                    "comment_count": 0,
                    "labeled_comment_count": 0,
                    "vehicle_related_count": 0,
                    "positive_count": 0,
                    "mid_high_purchase_signal_count": 0,
                    "total_engagement": 0,
                    "top_contents": [],
                },
            )
            bucket["content_ids"].add(row.get("content_id"))
            bucket["content_count"] = len(bucket["content_ids"])
            bucket["comment_count"] += int(row.get("comment_count") or 0)
            bucket["labeled_comment_count"] += int(row.get("labeled_comment_count") or 0)
            bucket["vehicle_related_count"] += int(row.get("vehicle_related_count") or 0)
            bucket["positive_count"] += int(row.get("positive_count") or 0)
            bucket["mid_high_purchase_signal_count"] += int(row.get("mid_high_purchase_signal_count") or 0)
            bucket["total_engagement"] += int(row.get("total_engagement") or 0)
            bucket["top_contents"].append(
                {
                    "content_id": row.get("content_id"),
                    "title": row.get("title") or "未命名内容",
                    "platform": row.get("platform") or "未知平台",
                    "comment_count": int(row.get("comment_count") or 0),
                    "total_engagement": int(row.get("total_engagement") or 0),
                }
            )

    topics = []
    for bucket in topic_map.values():
        labeled_count = int(bucket["labeled_comment_count"] or 0)
        topic_item = {
            "topic": bucket["topic"],
            "content_count": int(bucket["content_count"] or 0),
            "comment_count": int(bucket["comment_count"] or 0),
            "labeled_comment_count": labeled_count,
            "vehicle_related_count": int(bucket["vehicle_related_count"] or 0),
            "effective_comment_rate": round(int(bucket["vehicle_related_count"] or 0) * 100 / labeled_count, 1) if labeled_count else 0,
            "positive_rate": round(int(bucket["positive_count"] or 0) * 100 / labeled_count, 1) if labeled_count else 0,
            "mid_high_purchase_signal_count": int(bucket["mid_high_purchase_signal_count"] or 0),
            "purchase_signal_rate": round(int(bucket["mid_high_purchase_signal_count"] or 0) * 100 / labeled_count, 1) if labeled_count else 0,
            "total_engagement": int(bucket["total_engagement"] or 0),
            "top_contents": sorted(
                bucket["top_contents"],
                key=lambda item: (int(item.get("total_engagement") or 0), int(item.get("comment_count") or 0)),
                reverse=True,
            ),
        }
        topics.append(topic_item)

    topics.sort(key=lambda item: (item["comment_count"], item["total_engagement"], item["content_count"]), reverse=True)
    if not topics:
        return {
            "summary": {
                "top_topic": "鏆傛棤璇濋",
                "topic_count": 0,
                "top_topic_content_count": 0,
                "top_topic_comment_count": 0,
                "top_topic_effective_comment_rate": 0,
                "top_topic_purchase_signal_rate": 0,
                "rule_based_conclusion": "暂未从主贴标题或正文中解析到 #话题。补充带 # 的话题文本后，这里会展示话题传播效率。",
            },
            "topics": [],
        }

    top_topic = topics[0]
    conclusion = (
        f"话题「{top_topic['topic']}」传播效率最高，覆盖 {top_topic['content_count']} 条主贴。"
        f"带来 {top_topic['comment_count']} 条评论；有效评论率 {top_topic['effective_comment_rate']}%，"
        f"中/强购买信号 {top_topic['purchase_signal_rate']}%。"
    )
    return {
        "summary": {
            "top_topic": top_topic["topic"],
            "topic_count": len(topics),
            "top_topic_content_count": top_topic["content_count"],
            "top_topic_comment_count": top_topic["comment_count"],
            "top_topic_effective_comment_rate": top_topic["effective_comment_rate"],
            "top_topic_purchase_signal_rate": top_topic["purchase_signal_rate"],
            "rule_based_conclusion": conclusion,
        },
        "topics": topics[:12],
    }


def fetch_event_product_focus_story(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    query = """
        WITH aspect_rows AS (
          SELECT aspect AS aspect,
                 cm.comment_label_json ->> 'comment_sentiment' AS sentiment,
                 cm.comment_label_json ->> 'purchase_signal' AS purchase_signal
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          CROSS JOIN LATERAL jsonb_array_elements_text(
            CASE
              WHEN jsonb_typeof(cm.comment_label_json -> 'mentioned_aspect') = 'array'
                THEN cm.comment_label_json -> 'mentioned_aspect'
              WHEN cm.comment_label_json ? 'mentioned_aspect'
                THEN jsonb_build_array(cm.comment_label_json ->> 'mentioned_aspect')
              ELSE '[]'::jsonb
            END
          ) AS aspect
          WHERE c.event_id = %s
            AND cm.comment_label_json IS NOT NULL
            AND coalesce(aspect, '') <> ''
        )
        SELECT aspect,
               count(*)::bigint AS comment_count,
               count(*) FILTER (WHERE sentiment = '正向')::bigint AS positive_count,
               count(*) FILTER (WHERE sentiment = '负向')::bigint AS negative_count,
               count(*) FILTER (WHERE purchase_signal IN ('中', '强'))::bigint AS purchase_signal_count
        FROM aspect_rows
        GROUP BY aspect
        ORDER BY comment_count DESC, positive_count DESC, negative_count DESC, aspect
        LIMIT 20
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_product_focus_story(rows)


def build_product_focus_story(rows: list[dict[str, Any]]) -> dict[str, Any]:
    aspects = []
    total_mentions = sum(int(row.get("comment_count") or 0) for row in rows)
    for row in rows:
        comment_count = int(row.get("comment_count") or 0)
        positive_count = int(row.get("positive_count") or 0)
        negative_count = int(row.get("negative_count") or 0)
        purchase_signal_count = int(row.get("purchase_signal_count") or 0)
        aspects.append(
            {
                "aspect": row.get("aspect") or "未标注产品点",
                "comment_count": comment_count,
                "mention_rate": round(comment_count * 100 / total_mentions, 1) if total_mentions else 0,
                "positive_count": positive_count,
                "positive_rate": round(positive_count * 100 / comment_count, 1) if comment_count else 0,
                "negative_count": negative_count,
                "negative_rate": round(negative_count * 100 / comment_count, 1) if comment_count else 0,
                "purchase_signal_count": purchase_signal_count,
                "purchase_signal_rate": round(purchase_signal_count * 100 / comment_count, 1) if comment_count else 0,
            }
        )
    top_aspect = aspects[0] if aspects else None
    positive_aspect = max(aspects, key=lambda item: (item["positive_count"], item["comment_count"]), default=None)
    negative_aspect = max(aspects, key=lambda item: (item["negative_count"], item["comment_count"]), default=None)
    if top_aspect:
        conclusion = (
            f"用户讨论车本身时，最集中的产品点是「{top_aspect['aspect']}」，"
            f"贡献 {top_aspect['mention_rate']}% 产品点提及；"
            f"其中正向最高的是「{positive_aspect['aspect']}」，负向压力最高的是「{negative_aspect['aspect']}」。"
        )
    else:
        conclusion = "暂未从 comment_label_json 中解析到产品关注点。补入 mentioned_aspect 后，这里会展示用户讨论了哪些产品点。"
    return {
        "summary": {
            "top_aspect": top_aspect["aspect"] if top_aspect else None,
            "aspect_count": len(aspects),
            "total_mentions": total_mentions,
            "top_positive_aspect": positive_aspect["aspect"] if positive_aspect else None,
            "top_negative_aspect": negative_aspect["aspect"] if negative_aspect else None,
            "rule_based_conclusion": conclusion,
        },
        "aspects": aspects,
    }


def build_product_opportunity_story(aspects: list[dict[str, Any]]) -> dict[str, Any]:
    def build_items(score_key: str, rate_key: str, category: str) -> list[dict[str, Any]]:
        items = []
        for aspect in aspects:
            mention_rate = float(aspect.get("mention_rate") or 0)
            rate = float(aspect.get(rate_key) or 0)
            score = round(mention_rate * rate / 100, 1)
            if score <= 0:
                continue
            items.append(
                {
                    "aspect": aspect.get("aspect") or "未标注产品点",
                    "category": category,
                    "comment_count": int(aspect.get("comment_count") or 0),
                    "mention_rate": mention_rate,
                    "positive_rate": float(aspect.get("positive_rate") or 0),
                    "negative_rate": float(aspect.get("negative_rate") or 0),
                    "purchase_signal_rate": float(aspect.get("purchase_signal_rate") or 0),
                    "opportunity_score": score,
                    "score_key": score_key,
                    "reason": f"提及率 {mention_rate:.1f}% × {category}率 {rate:.1f}%",
                }
            )
        return sorted(items, key=lambda item: (item["opportunity_score"], item["comment_count"]), reverse=True)[:5]

    surprise_points = build_items("surprise_score", "positive_rate", "惊喜")
    pain_points = build_items("pain_score", "negative_rate", "风险")
    conversion_points = build_items("conversion_score", "purchase_signal_rate", "转化")

    surprise_point = surprise_points[0]["aspect"] if surprise_points else None
    pain_point = pain_points[0]["aspect"] if pain_points else None
    conversion_point = conversion_points[0]["aspect"] if conversion_points else None

    if surprise_point or pain_point or conversion_point:
        conclusion = (
            f"产品机会优先级显示：惊喜点集中在「{surprise_point or '暂无'}」，"
            f"吐槽压力集中在「{pain_point or '暂无'}」，"
            f"转化信号集中在「{conversion_point or '暂无'}」。"
        )
    else:
        conclusion = "暂未形成稳定的产品机会优先级。补充评论标签后，可识别惊喜点、吐槽点和转化点。"

    return {
        "summary": {
            "surprise_point": surprise_point,
            "pain_point": pain_point,
            "conversion_point": conversion_point,
            "rule_based_conclusion": conclusion,
        },
        "surprise_points": surprise_points,
        "pain_points": pain_points,
        "conversion_points": conversion_points,
    }


def fetch_event_product_focus_story(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    query = """
        WITH aspect_rows AS (
          SELECT aspect AS aspect,
                 cm.comment_label_json ->> 'comment_sentiment' AS sentiment,
                 cm.comment_label_json ->> 'purchase_signal' AS purchase_signal,
                 cm.comment_id,
                 cm.comment_author_name,
                 cm.comment_text,
                 cm.published_at,
                 cm.interaction_cnt
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          CROSS JOIN LATERAL jsonb_array_elements_text(
            CASE
              WHEN jsonb_typeof(cm.comment_label_json -> 'mentioned_aspect') = 'array'
                THEN cm.comment_label_json -> 'mentioned_aspect'
              WHEN cm.comment_label_json ? 'mentioned_aspect'
                THEN jsonb_build_array(cm.comment_label_json ->> 'mentioned_aspect')
              ELSE '[]'::jsonb
            END
          ) AS aspect
          WHERE c.event_id = %s
            AND cm.comment_label_json IS NOT NULL
            AND coalesce(aspect, '') <> ''
        ),
        aspect_stats AS (
          SELECT aspect,
                 count(*)::bigint AS comment_count,
                 count(*) FILTER (WHERE sentiment = '正向')::bigint AS positive_count,
                 count(*) FILTER (WHERE sentiment = '负向')::bigint AS negative_count,
                 count(*) FILTER (WHERE purchase_signal IN ('中', '强'))::bigint AS purchase_signal_count
          FROM aspect_rows
          GROUP BY aspect
        ),
        ranked_comments AS (
          SELECT aspect, comment_id, comment_author_name, comment_text, published_at, interaction_cnt,
                 row_number() OVER (
                   PARTITION BY aspect
                   ORDER BY interaction_cnt DESC NULLS LAST, published_at DESC NULLS LAST, comment_id
                 ) AS rn
          FROM aspect_rows
        ),
        comment_evidence AS (
          SELECT aspect,
                 jsonb_agg(
                   jsonb_build_object(
                     'comment_id', comment_id,
                     'comment_author_name', comment_author_name,
                     'comment_text', comment_text,
                     'published_at', published_at,
                     'interaction_cnt', interaction_cnt
                   )
                   ORDER BY interaction_cnt DESC NULLS LAST, published_at DESC NULLS LAST, comment_id
                 ) AS evidence_comments
          FROM ranked_comments
          WHERE rn <= 8
          GROUP BY aspect
        )
        SELECT s.aspect,
               s.comment_count,
               s.positive_count,
               s.negative_count,
               s.purchase_signal_count,
               coalesce(e.evidence_comments, '[]'::jsonb) AS evidence_comments
        FROM aspect_stats s
        LEFT JOIN comment_evidence e ON s.aspect = e.aspect
        ORDER BY s.comment_count DESC, s.positive_count DESC, s.negative_count DESC, s.aspect
        LIMIT 20
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_product_focus_story(rows)


def build_product_focus_story(rows: list[dict[str, Any]]) -> dict[str, Any]:
    aspects = []
    total_mentions = sum(int(row.get("comment_count") or 0) for row in rows)
    for row in rows:
        comment_count = int(row.get("comment_count") or 0)
        positive_count = int(row.get("positive_count") or 0)
        negative_count = int(row.get("negative_count") or 0)
        purchase_signal_count = int(row.get("purchase_signal_count") or 0)
        aspects.append(
            {
                "aspect": row.get("aspect") or "未标注产品点",
                "comment_count": comment_count,
                "mention_rate": round(comment_count * 100 / total_mentions, 1) if total_mentions else 0,
                "positive_count": positive_count,
                "positive_rate": round(positive_count * 100 / comment_count, 1) if comment_count else 0,
                "negative_count": negative_count,
                "negative_rate": round(negative_count * 100 / comment_count, 1) if comment_count else 0,
                "purchase_signal_count": purchase_signal_count,
                "purchase_signal_rate": round(purchase_signal_count * 100 / comment_count, 1) if comment_count else 0,
                "evidence_comments": row.get("evidence_comments") or [],
            }
        )
    top_aspect = aspects[0] if aspects else None
    positive_aspect = max(aspects, key=lambda item: (item["positive_count"], item["comment_count"]), default=None)
    negative_aspect = max(aspects, key=lambda item: (item["negative_count"], item["comment_count"]), default=None)
    if top_aspect:
        conclusion = (
            f"用户讨论车本身时，最集中的产品点是「{top_aspect['aspect']}」，"
            f"贡献 {top_aspect['mention_rate']}% 产品点提及；"
            f"其中正向最高的是「{positive_aspect['aspect']}」，负向压力最高的是「{negative_aspect['aspect']}」。"
        )
    else:
        conclusion = "暂未从 comment_label_json 中解析到产品关注点。补入 mentioned_aspect 后，这里会展示用户讨论了哪些产品点。"
    return {
        "summary": {
            "top_aspect": top_aspect["aspect"] if top_aspect else None,
            "aspect_count": len(aspects),
            "total_mentions": total_mentions,
            "top_positive_aspect": positive_aspect["aspect"] if positive_aspect else None,
            "top_negative_aspect": negative_aspect["aspect"] if negative_aspect else None,
            "rule_based_conclusion": conclusion,
        },
        "aspects": aspects,
    }


def build_product_opportunity_story(aspects: list[dict[str, Any]]) -> dict[str, Any]:
    def build_items(score_key: str, rate_key: str, category: str) -> list[dict[str, Any]]:
        items = []
        for aspect in aspects:
            mention_rate = float(aspect.get("mention_rate") or 0)
            rate = float(aspect.get(rate_key) or 0)
            score = round(mention_rate * rate / 100, 1)
            if score <= 0:
                continue
            items.append(
                {
                    "aspect": aspect.get("aspect") or "未标注产品点",
                    "category": category,
                    "comment_count": int(aspect.get("comment_count") or 0),
                    "mention_rate": mention_rate,
                    "positive_rate": float(aspect.get("positive_rate") or 0),
                    "negative_rate": float(aspect.get("negative_rate") or 0),
                    "purchase_signal_rate": float(aspect.get("purchase_signal_rate") or 0),
                    "opportunity_score": score,
                    "score_key": score_key,
                    "reason": f"提及率 {mention_rate:.1f}% × {category}率 {rate:.1f}%",
                    "evidence_comments": aspect.get("evidence_comments") or [],
                }
            )
        return sorted(items, key=lambda item: (item["opportunity_score"], item["comment_count"]), reverse=True)[:5]

    surprise_points = build_items("surprise_score", "positive_rate", "惊喜")
    pain_points = build_items("pain_score", "negative_rate", "风险")
    conversion_points = build_items("conversion_score", "purchase_signal_rate", "转化")

    surprise_point = surprise_points[0]["aspect"] if surprise_points else None
    pain_point = pain_points[0]["aspect"] if pain_points else None
    conversion_point = conversion_points[0]["aspect"] if conversion_points else None

    if surprise_point or pain_point or conversion_point:
        conclusion = (
            f"产品机会优先级显示：惊喜点集中在「{surprise_point or '暂无'}」，"
            f"吐槽压力集中在「{pain_point or '暂无'}」，"
            f"转化信号集中在「{conversion_point or '暂无'}」。"
        )
    else:
        conclusion = "暂未形成稳定的产品机会优先级。补充评论标签后，可识别惊喜点、吐槽点和转化点。"

    return {
        "summary": {
            "surprise_point": surprise_point,
            "pain_point": pain_point,
            "conversion_point": conversion_point,
            "rule_based_conclusion": conclusion,
        },
        "surprise_points": surprise_points,
        "pain_points": pain_points,
        "conversion_points": conversion_points,
    }


def fetch_event_product_pko_story(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    query = """
        WITH extracted AS (
          SELECT
            coalesce(
              nullif(cm.comment_label_json #>> '{pko,target}', ''),
              nullif(cm.comment_label_json ->> 'pko_target', '')
            ) AS target,
            coalesce(
              nullif(cm.comment_label_json #>> '{pko,dimension}', ''),
              nullif(cm.comment_label_json ->> 'pko_dimension', '')
            ) AS dimension,
            coalesce(
              nullif(cm.comment_label_json #>> '{pko,result}', ''),
              nullif(cm.comment_label_json ->> 'pko_result', '')
            ) AS result,
            coalesce(
              nullif(cm.comment_label_json #>> '{pko,reason}', ''),
              nullif(cm.comment_label_json ->> 'pko_reason', '')
            ) AS reason,
            coalesce(
              nullif(cm.comment_label_json #>> '{pko,has_pko}', ''),
              nullif(cm.comment_label_json ->> 'has_pko', '')
            ) AS has_pko,
            cm.comment_id,
            cm.comment_author_name,
            cm.comment_text,
            cm.published_at,
            cm.interaction_cnt
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s
            AND cm.comment_label_json IS NOT NULL
        )
        SELECT target, dimension, result, reason, comment_id, comment_author_name, comment_text, published_at, interaction_cnt
        FROM extracted
        WHERE (
            coalesce(has_pko, '') IN ('是', '有', 'true', 'TRUE', '1', 'yes', 'YES')
            OR coalesce(target, '') <> ''
            OR coalesce(dimension, '') <> ''
            OR coalesce(result, '') <> ''
          )
        ORDER BY interaction_cnt DESC NULLS LAST, published_at DESC NULLS LAST, comment_id
        LIMIT 500
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_product_pko_story(rows)


def build_product_pko_story(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def clean_label(value: Any, fallback: str) -> str:
        text = str(value or "").strip()
        return text if text else fallback

    normalized = []
    for row in rows:
        normalized.append(
            {
                "target": clean_label(row.get("target"), "未标注对比对象"),
                "dimension": clean_label(row.get("dimension"), "未标注维度"),
                "result": clean_label(row.get("result"), "无明确判断"),
                "reason": str(row.get("reason") or "").strip(),
                "comment_id": row.get("comment_id"),
                "comment_author_name": row.get("comment_author_name"),
                "comment_text": row.get("comment_text") or "",
                "published_at": row.get("published_at"),
                "interaction_cnt": int(row.get("interaction_cnt") or 0),
            }
        )

    def distribution(key: str) -> list[dict[str, Any]]:
        counter = Counter(item[key] for item in normalized)
        interaction_counter = Counter()
        for item in normalized:
            interaction_counter[item[key]] += int(item.get("interaction_cnt") or 0)
        total = sum(counter.values())
        return [
            {"label": label, "count": count, "rate": round(count * 100 / total, 1) if total else 0}
            for label, count in sorted(counter.items(), key=lambda item: (-item[1], -interaction_counter[item[0]], item[0]))
        ]

    target_distribution = distribution("target")
    dimension_distribution = distribution("dimension")
    result_distribution = distribution("result")
    pko_comment_count = len(normalized)
    def is_generic_target(target: str) -> bool:
        return target == "其他"

    def is_unknown_target(target: str) -> bool:
        return target.startswith("未标注") or any(token in target for token in ("鏈", "鐢", "诲", "儚", "涓", "寮", "姝", "璐"))

    generic_target_rows = [item for item in normalized if is_generic_target(item["target"])]
    explicit_target_rows = [item for item in normalized if not is_generic_target(item["target"]) and not is_unknown_target(item["target"])]

    def distribution_for_rows(items: list[dict[str, Any]], key: str, denominator: int | None = None) -> list[dict[str, Any]]:
        counter = Counter(item[key] for item in items)
        interaction_counter = Counter()
        for item in items:
            interaction_counter[item[key]] += int(item.get("interaction_cnt") or 0)
        total = denominator if denominator is not None else sum(counter.values())
        return [
            {"label": label, "count": count, "rate": round(count * 100 / total, 1) if total else 0}
            for label, count in sorted(counter.items(), key=lambda item: (-item[1], -interaction_counter[item[0]], item[0]))
        ]

    def result_bucket(value: str) -> str:
        if value == "本车优势":
            return "advantage"
        if value == "本车劣势":
            return "disadvantage"
        if value == "中性对比":
            return "neutral"
        return "unclear"

    explicit_target_distribution = distribution_for_rows(explicit_target_rows, "target", pko_comment_count)
    dimension_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in normalized:
        dimension_groups[item["dimension"]].append(item)
    dimension_result_matrix = []
    for dimension, dimension_rows in sorted(dimension_groups.items(), key=lambda item: (-len(item[1]), item[0])):
        dimension_explicit_rows = [
            item
            for item in dimension_rows
            if not is_generic_target(item["target"]) and not is_unknown_target(item["target"])
        ]
        target_source = dimension_explicit_rows or dimension_rows
        top_target_for_dimension = distribution_for_rows(target_source, "target")[0]["label"] if target_source else None
        dimension_result_matrix.append(
            {
                "dimension": dimension,
                "total_count": len(dimension_rows),
                "advantage_count": sum(1 for item in dimension_rows if result_bucket(item["result"]) == "advantage"),
                "disadvantage_count": sum(1 for item in dimension_rows if result_bucket(item["result"]) == "disadvantage"),
                "neutral_count": sum(1 for item in dimension_rows if result_bucket(item["result"]) == "neutral"),
                "unclear_count": sum(1 for item in dimension_rows if result_bucket(item["result"]) == "unclear"),
                "top_target": top_target_for_dimension,
            }
        )
    top_explicit_target = explicit_target_distribution[0]["label"] if explicit_target_distribution else None
    renderable_evidence = [
        item
        for item in normalized
        if str(item.get("comment_id") or "").strip()
        and str(item.get("comment_text") or "").strip()
    ]
    legacy_text_evidence = [
        item
        for item in normalized
        if not str(item.get("comment_id") or "").strip()
        and str(item.get("comment_text") or "").strip()
    ]

    def ordered_evidence(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ordered = sorted(
            items,
            key=lambda item: (
                str(item.get("comment_id") or ""),
                str(item.get("comment_text") or ""),
            ),
        )
        ordered.sort(
            key=lambda item: str(item.get("published_at") or ""),
            reverse=True,
        )

        def interaction_count(item: dict[str, Any]) -> int:
            try:
                return int(item.get("interaction_cnt") or 0)
            except (TypeError, ValueError):
                return 0

        ordered.sort(key=interaction_count, reverse=True)
        return ordered

    evidence_comments = [
        *ordered_evidence(renderable_evidence),
        *ordered_evidence(legacy_text_evidence),
    ][:50]
    advantage_rows = [item for item in normalized if result_bucket(item["result"]) == "advantage"]
    disadvantage_rows = [item for item in normalized if result_bucket(item["result"]) == "disadvantage"]
    advantage_dimension = distribution_from_rows(advantage_rows, "dimension")[0]["label"] if advantage_rows else None
    disadvantage_dimension = distribution_from_rows(disadvantage_rows, "dimension")[0]["label"] if disadvantage_rows else None
    clear_result_count = len(advantage_rows) + len(disadvantage_rows)
    pko_comment_count = len(normalized)
    top_target = target_distribution[0]["label"] if target_distribution else None
    top_dimension = dimension_distribution[0]["label"] if dimension_distribution else None

    if pko_comment_count:
        explicit_clause = f"明确对比对象以「{top_explicit_target}」为主，" if top_explicit_target else "明确竞品对象不足，"
        conclusion = (
            f"PKO 对比评论共 {pko_comment_count} 条，{explicit_clause}"
            f"泛化对比 {len(generic_target_rows)} 条；"
            f"对比维度集中在「{top_dimension}」，优势集中在「{advantage_dimension or '暂无'}」，劣势集中在「{disadvantage_dimension or '暂无'}」。"
        )
    else:
        conclusion = "暂未解析到 PKO 对比评论。补入 comment_label_json.pko 后，这里会展示竞品对比位置。"
    return {
        "summary": {
            "pko_comment_count": pko_comment_count,
            "top_target": top_target,
            "top_explicit_target": top_explicit_target,
            "top_dimension": top_dimension,
            "advantage_dimension": advantage_dimension,
            "disadvantage_dimension": disadvantage_dimension,
            "clear_result_count": clear_result_count,
            "clear_result_rate": round(clear_result_count * 100 / pko_comment_count, 1) if pko_comment_count else 0,
            "explicit_target_count": len(explicit_target_rows),
            "explicit_target_rate": round(len(explicit_target_rows) * 100 / pko_comment_count, 1) if pko_comment_count else 0,
            "generic_target_count": len(generic_target_rows),
            "generic_target_rate": round(len(generic_target_rows) * 100 / pko_comment_count, 1) if pko_comment_count else 0,
            "rule_based_conclusion": conclusion,
        },
        "target_distribution": target_distribution,
        "explicit_target_distribution": explicit_target_distribution,
        "generic_target_summary": {
            "label": "其他对象",
            "count": len(generic_target_rows),
            "rate": round(len(generic_target_rows) * 100 / pko_comment_count, 1) if pko_comment_count else 0,
        },
        "dimension_distribution": dimension_distribution,
        "result_distribution": result_distribution,
        "dimension_result_matrix": dimension_result_matrix[:6],
        "evidence_comments": evidence_comments[:50],
    }


def distribution_from_rows(rows: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    counter = Counter(item[key] for item in rows)
    total = sum(counter.values())
    return [
        {"label": label, "count": count, "rate": round(count * 100 / total, 1) if total else 0}
        for label, count in sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    ]


def fetch_event_sales_lead_quality(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    query = """
        SELECT
          coalesce(nullif(cm.comment_label_json ->> 'is_vehicle_related', ''), '未标注') AS is_vehicle_related,
          coalesce(nullif(cm.comment_label_json ->> 'comment_intent', ''), '未标注') AS comment_intent,
          coalesce(nullif(cm.comment_label_json ->> 'purchase_signal', ''), '未标注') AS purchase_signal,
          cm.comment_id,
          cm.content_id,
          cm.platform,
          cm.location,
          cm.comment_author_name,
          cm.comment_text,
          cm.published_at,
          cm.interaction_cnt
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE c.event_id = %s
          AND cm.comment_label_json IS NOT NULL
        ORDER BY cm.interaction_cnt DESC NULLS LAST, cm.published_at DESC NULLS LAST, cm.comment_id
        LIMIT 2000
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    for row in rows:
        row["comment_user_id"] = build_comment_user_id(row.get("platform"), row.get("comment_author_name"), row.get("location"))
    profile_map = fetch_latest_comment_user_profile_map(conn, sorted({row["comment_user_id"] for row in rows}))
    for row in rows:
        profile = profile_map.get(row["comment_user_id"], {})
        row["main_label"] = profile.get("main_label") or "未画像用户"
        row["main_dimension"] = profile.get("main_dimension")
    return build_sales_lead_quality_story(rows)


def build_sales_lead_quality_story(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sales_intents = {"购买意向", "询价", "报价", "价格敏感", "到店", "试驾", "下订"}
    intent_order = {
        "询价": 1,
        "报价": 2,
        "价格敏感": 3,
        "到店": 4,
        "试驾": 5,
        "下订": 6,
        "对比": 7,
        "观望": 8,
        "购买意向": 9,
        "吐槽": 10,
        "闲聊": 11,
        "未标注": 99,
    }
    purchase_order = {"强": 1, "中": 2, "弱": 3, "无": 4, "未标注": 99}

    normalized = [
        {
            "is_vehicle_related": str(row.get("is_vehicle_related") or "未标注").strip() or "未标注",
            "comment_intent": str(row.get("comment_intent") or "未标注").strip() or "未标注",
            "purchase_signal": str(row.get("purchase_signal") or "未标注").strip() or "未标注",
            "comment_id": row.get("comment_id"),
            "comment_user_id": row.get("comment_user_id") or build_comment_user_id(row.get("platform"), row.get("comment_author_name"), row.get("location")),
            "main_label": row.get("main_label") or "未画像用户",
            "main_dimension": row.get("main_dimension"),
            "content_id": row.get("content_id"),
            "comment_author_name": row.get("comment_author_name"),
            "comment_text": row.get("comment_text") or "",
            "published_at": row.get("published_at"),
            "interaction_cnt": int(row.get("interaction_cnt") or 0),
        }
        for row in rows
    ]

    def distribution(key: str, order_map: dict[str, int] | None = None) -> list[dict[str, Any]]:
        counter = Counter(item[key] for item in normalized)
        total = sum(counter.values())
        return [
            {"label": label, "count": count, "rate": round(count * 100 / total, 1) if total else 0}
            for label, count in sorted(counter.items(), key=lambda item: (-item[1], order_map.get(item[0], 50) if order_map else item[0], item[0]))
        ]

    labeled_comment_count = len(normalized)
    vehicle_related_count = sum(1 for row in normalized if row["is_vehicle_related"] == "是")
    mid_high_rows = [row for row in normalized if row["purchase_signal"] in {"中", "强"}]
    strong_rows = [row for row in normalized if row["purchase_signal"] == "强"]
    sales_intent_rows = [
        row
        for row in normalized
        if row["is_vehicle_related"] == "是"
        and (row["comment_intent"] in sales_intents or row["purchase_signal"] in {"中", "强"})
    ]
    non_sales_intent_count = max(vehicle_related_count - len(sales_intent_rows), 0)
    intent_distribution = distribution("comment_intent", intent_order)
    purchase_signal_distribution = distribution("purchase_signal", purchase_order)
    evidence_comments = sorted(mid_high_rows, key=lambda row: (-row["interaction_cnt"], row.get("published_at") or "", row.get("comment_id") or ""))[:6]
    top_intent = intent_distribution[0]["label"] if intent_distribution else None

    if labeled_comment_count:
        conclusion = (
            f"本事件已打标评论 {labeled_comment_count} 条，"
            f"车相关评论率 {round(vehicle_related_count * 100 / labeled_comment_count, 1)}%，"
            f"中/强购买信号占 {round(len(mid_high_rows) * 100 / labeled_comment_count, 1)}%，"
            f"主要用户意图为「{top_intent}」。"
        )
    else:
        conclusion = "暂未解析到销售意向标签。补入 comment_label_json.purchase_signal 和 comment_intent 后，这里会展示线索意向质量。"

    return {
        "summary": {
            "labeled_comment_count": labeled_comment_count,
            "vehicle_related_count": vehicle_related_count,
            "vehicle_related_rate": round(vehicle_related_count * 100 / labeled_comment_count, 1) if labeled_comment_count else 0,
            "sales_intent_comment_count": len(sales_intent_rows),
            "sales_intent_rate": round(len(sales_intent_rows) * 100 / labeled_comment_count, 1) if labeled_comment_count else 0,
            "mid_high_purchase_signal_count": len(mid_high_rows),
            "mid_high_purchase_signal_rate": round(len(mid_high_rows) * 100 / labeled_comment_count, 1) if labeled_comment_count else 0,
            "strong_purchase_signal_count": len(strong_rows),
            "strong_purchase_signal_rate": round(len(strong_rows) * 100 / labeled_comment_count, 1) if labeled_comment_count else 0,
            "top_intent": top_intent,
            "rule_based_conclusion": conclusion,
        },
        "intent_distribution": intent_distribution,
        "purchase_signal_distribution": purchase_signal_distribution,
        "sankey": build_sales_lead_sankey(
            labeled_comment_count=labeled_comment_count,
            vehicle_related_count=vehicle_related_count,
            sales_intent_rows=sales_intent_rows,
            non_sales_intent_count=non_sales_intent_count,
        ),
        "profile_segments": build_sales_lead_profile_segments(
            normalized=normalized,
            sales_intent_rows=sales_intent_rows,
        ),
        "evidence_comments": evidence_comments,
    }


def build_sales_lead_profile_segments(
    normalized: list[dict[str, Any]],
    sales_intent_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sales_intent_ids = {id(row) for row in sales_intent_rows}

    def is_sales_intent(row: dict[str, Any]) -> bool:
        return id(row) in sales_intent_ids

    segment_definitions: list[tuple[str, str, list[dict[str, Any]]]] = [
        ("all", "全部已打标评论", normalized),
        ("vehicle_related", "车相关", [row for row in normalized if row["is_vehicle_related"] == "是"]),
        ("not_vehicle_related", "非车相关", [row for row in normalized if row["is_vehicle_related"] != "是"]),
        ("sales_intent", "销售相关意图", sales_intent_rows),
        (
            "non_sales_intent",
            "非销售相关意图",
            [row for row in normalized if row["is_vehicle_related"] == "是" and not is_sales_intent(row)],
        ),
        ("signal_strong", "强购买信号", [row for row in sales_intent_rows if row["purchase_signal"] == "强"]),
        ("signal_mid", "中购买信号", [row for row in sales_intent_rows if row["purchase_signal"] == "中"]),
        ("signal_weak", "弱购买信号", [row for row in sales_intent_rows if row["purchase_signal"] == "弱"]),
        ("signal_none", "无购买信号", [row for row in sales_intent_rows if row["purchase_signal"] == "无"]),
        (
            "signal_unknown",
            "未标注购买信号",
            [row for row in sales_intent_rows if row["purchase_signal"] not in {"强", "中", "弱", "无"}],
        ),
    ]
    link_segments = [
        ("all->vehicle_related", "全部已打标评论 -> 车相关", [row for row in normalized if row["is_vehicle_related"] == "是"]),
        ("all->not_vehicle_related", "全部已打标评论 -> 非车相关", [row for row in normalized if row["is_vehicle_related"] != "是"]),
        ("vehicle_related->sales_intent", "车相关 -> 销售相关意图", sales_intent_rows),
        (
            "vehicle_related->non_sales_intent",
            "车相关 -> 非销售相关意图",
            [row for row in normalized if row["is_vehicle_related"] == "是" and not is_sales_intent(row)],
        ),
        ("sales_intent->signal_strong", "销售相关意图 -> 强购买信号", [row for row in sales_intent_rows if row["purchase_signal"] == "强"]),
        ("sales_intent->signal_mid", "销售相关意图 -> 中购买信号", [row for row in sales_intent_rows if row["purchase_signal"] == "中"]),
        ("sales_intent->signal_weak", "销售相关意图 -> 弱购买信号", [row for row in sales_intent_rows if row["purchase_signal"] == "弱"]),
        ("sales_intent->signal_none", "销售相关意图 -> 无购买信号", [row for row in sales_intent_rows if row["purchase_signal"] == "无"]),
    ]
    return [build_sales_profile_segment(segment_id, label, rows) for segment_id, label, rows in segment_definitions + link_segments]


def dominant_purchase_signal(rows: list[dict[str, Any]]) -> str:
    signal_priority = ["强", "中", "弱", "无"]
    signals = [str(row.get("purchase_signal") or "").strip() for row in rows]
    for signal in signal_priority:
        if signal in signals:
            return signal
    return signals[0] if signals and signals[0] else "未标注"


def build_sales_profile_segment(segment_id: str, label: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    user_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        user_groups[str(row.get("comment_user_id") or "unknown_user")].append(row)
    label_counter = Counter()
    users = []
    for comment_user_id, user_rows in user_groups.items():
        ordered_rows = sorted(user_rows, key=lambda row: (-int(row.get("interaction_cnt") or 0), row.get("published_at") or ""))
        first = ordered_rows[0]
        main_label = first.get("main_label") or "未画像用户"
        purchase_signal = dominant_purchase_signal(user_rows)
        label_counter[main_label] += 1
        users.append(
            {
                "comment_user_id": comment_user_id,
                "comment_author_name": first.get("comment_author_name") or "未命名用户",
                "main_label": main_label,
                "main_dimension": first.get("main_dimension"),
                "purchase_signal": purchase_signal,
                "comment_count": len(user_rows),
                "mid_high_purchase_signal_count": sum(1 for row in user_rows if row.get("purchase_signal") in {"中", "强"}),
                "representative_comment": first.get("comment_text") or "",
            }
        )
    user_count = len(user_groups)
    profile_distribution = [
        {"main_label": label_name, "user_count": count, "rate": round(count * 100 / user_count, 1) if user_count else 0}
        for label_name, count in sorted(label_counter.items(), key=lambda item: (-item[1], item[0]))
    ]
    users.sort(key=lambda item: (-item["mid_high_purchase_signal_count"], -item["comment_count"], item["comment_author_name"]))
    return {
        "segment_id": segment_id,
        "label": label,
        "summary": {
            "user_count": user_count,
            "comment_count": len(rows),
            "mid_high_purchase_signal_count": sum(1 for row in rows if row.get("purchase_signal") in {"中", "强"}),
            "content_count": len({row.get("content_id") for row in rows if row.get("content_id")}),
        },
        "profile_distribution": profile_distribution,
        "users": users[:50],
    }


def build_sales_lead_sankey(
    labeled_comment_count: int,
    vehicle_related_count: int,
    sales_intent_rows: list[dict[str, Any]],
    non_sales_intent_count: int,
) -> dict[str, Any]:
    signal_counter = Counter(row["purchase_signal"] for row in sales_intent_rows)
    nodes = [
        {"id": "all", "label": "全部已打标评论", "layer": 0},
        {"id": "vehicle_related", "label": "车相关", "layer": 1},
        {"id": "not_vehicle_related", "label": "非车相关", "layer": 1},
        {"id": "sales_intent", "label": "销售相关意图", "layer": 2},
        {"id": "non_sales_intent", "label": "非销售相关意图", "layer": 2},
        {"id": "signal_strong", "label": "强购买信号", "layer": 3},
        {"id": "signal_mid", "label": "中购买信号", "layer": 3},
        {"id": "signal_weak", "label": "弱购买信号", "layer": 3},
        {"id": "signal_none", "label": "无购买信号", "layer": 3},
        {"id": "signal_unknown", "label": "未标注购买信号", "layer": 3},
    ]
    signal_map = {
        "强": "signal_strong",
        "中": "signal_mid",
        "弱": "signal_weak",
        "无": "signal_none",
    }
    links = [
        {"source": "all", "target": "vehicle_related", "value": vehicle_related_count},
        {"source": "all", "target": "not_vehicle_related", "value": max(labeled_comment_count - vehicle_related_count, 0)},
        {"source": "vehicle_related", "target": "sales_intent", "value": len(sales_intent_rows)},
        {"source": "vehicle_related", "target": "non_sales_intent", "value": non_sales_intent_count},
    ]
    for signal, count in signal_counter.items():
        links.append({"source": "sales_intent", "target": signal_map.get(signal, "signal_unknown"), "value": count})
    return {
        "nodes": nodes,
        "links": [link for link in links if int(link["value"] or 0) > 0],
    }

def ensure_json_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []


def build_comment_user_insight_profile(
    profile: dict[str, Any],
    label_scores: list[dict[str, Any]],
    comments: list[dict[str, Any]],
) -> dict[str, Any]:
    first_comment = comments[0] if comments else {}
    user = {
        "comment_user_id": profile.get("comment_user_id") or first_comment.get("comment_user_id") or "",
        "comment_author_name": profile.get("comment_author_name") or first_comment.get("comment_author_name") or "",
        "platform": profile.get("platform") or first_comment.get("platform") or "",
        "location": profile.get("location") or first_comment.get("location") or "",
    }
    total_comments = int(profile.get("total_comments") or len(comments))
    valid_comments = int(profile.get("valid_comments") or 0)
    profile_summary = {
        "main_dimension": profile.get("main_dimension") or "",
        "main_label": profile.get("main_label") or "",
        "main_score": float(profile.get("main_score") or 0),
        "total_comments": total_comments,
        "valid_comments": valid_comments,
        "valid_comment_rate": round(valid_comments * 100 / total_comments, 1) if total_comments else 0,
        "profile_batch": profile.get("profile_batch") or "",
        "prompt_version": profile.get("prompt_version") or "",
        "updated_time": profile.get("updated_time") or "",
    }
    ordered_scores = sorted(label_scores, key=lambda item: float(item.get("final_score") or 0), reverse=True)
    radar_labels = [
        {
            "dimension": row.get("dimension") or "",
            "label": row.get("label") or "",
            "score": float(row.get("final_score") or 0),
            "support_count": int(row.get("support_count") or 0),
        }
        for row in ordered_scores[:8]
    ]

    key_evidence = []
    for row in ordered_scores:
        for evidence in ensure_json_list(row.get("evidence_details_json")):
            key_evidence.append(
                {
                    "dimension": row.get("dimension") or evidence.get("dimension") or "",
                    "label": row.get("label") or evidence.get("label") or "",
                    "score": float(row.get("final_score") or 0),
                    "comment_id": evidence.get("comment_id") or "",
                    "comment_text": evidence.get("comment_text") or "",
                    "evidence_text": evidence.get("evidence_text") or "",
                    "reason": evidence.get("reason") or "",
                }
            )
    if not key_evidence:
        for row in ordered_scores:
            for evidence in ensure_json_list(row.get("evidence_examples_json")):
                key_evidence.append(
                    {
                        "dimension": row.get("dimension") or "",
                        "label": row.get("label") or "",
                        "score": float(row.get("final_score") or 0),
                        "comment_id": evidence.get("comment_id") or "",
                        "comment_text": evidence.get("comment_text") or "",
                        "evidence_text": evidence.get("evidence_text") or "",
                        "reason": evidence.get("reason") or "",
                    }
                )

    normalized_comments = sorted(
        [
            {
                "comment_id": row.get("comment_id") or "",
                "content_id": row.get("content_id") or "",
                "content_title": row.get("content_title") or "",
                "source_url": row.get("source_url") or "",
                "platform": row.get("platform") or "",
                "comment_text": row.get("comment_text") or "",
                "published_at": row.get("published_at") or "",
                "like_cnt": int(row.get("like_cnt") or 0),
                "reply_cnt": int(row.get("reply_cnt") or 0),
                "interaction_cnt": int(row.get("interaction_cnt") or 0),
                "comment_intent": row.get("comment_intent") or "",
                "purchase_signal": row.get("purchase_signal") or "",
                "comment_sentiment": row.get("comment_sentiment") or "",
            }
            for row in comments
        ],
        key=lambda item: (item["published_at"], item["comment_id"]),
        reverse=True,
    )
    return {
        "user": user,
        "profile_summary": profile_summary,
        "radar_labels": radar_labels,
        "key_evidence": key_evidence[:8],
        "comments": normalized_comments,
    }


def fetch_comment_user_profile(conn: psycopg.Connection, comment_user_id: str) -> dict[str, Any]:
    query = """
        SELECT DISTINCT ON (comment_user_id)
               comment_user_id, platform, comment_author_name, location,
               main_dimension, main_label, main_score, total_comments, valid_comments,
               profile_batch, prompt_version, updated_time
        FROM data_asset.user_profile_comment_result
        WHERE comment_user_id = %s
        ORDER BY comment_user_id, updated_time DESC NULLS LAST, comment_user_profile_id DESC
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [comment_user_id])
        row = cur.fetchone()
    return normalize_row(dict(row)) if row else {"comment_user_id": comment_user_id}


def fetch_comment_user_label_scores(
    conn: psycopg.Connection,
    comment_user_id: str,
    profile_batch: str | None,
) -> list[dict[str, Any]]:
    params: list[Any] = [comment_user_id]
    batch_clause = ""
    if profile_batch:
        batch_clause = "AND profile_batch = %s"
        params.append(profile_batch)
    query = f"""
        SELECT dimension, label, final_score, feature_level, confidence_level, support_count,
               evidence_examples_json, evidence_details_json, profile_batch, updated_time
        FROM data_asset.user_profile_comment_label_score
        WHERE comment_user_id = %s
          {batch_clause}
        ORDER BY final_score DESC NULLS LAST, support_count DESC NULLS LAST, label
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, params)
        return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_event_comment_user_comments(
    conn: psycopg.Connection,
    event_id: str,
    comment_user_id: str,
) -> list[dict[str, Any]]:
    query = """
        SELECT cm.comment_id, cm.content_id, c.title AS content_title, c.source_url,
               coalesce(cm.platform, c.platform) AS platform,
               cm.location, cm.comment_author_name,
               cm.comment_text, cm.published_at,
               cm.like_cnt, cm.reply_cnt, cm.interaction_cnt,
               coalesce(nullif(cm.comment_label_json ->> 'comment_intent', ''), '') AS comment_intent,
               coalesce(nullif(cm.comment_label_json ->> 'purchase_signal', ''), '') AS purchase_signal,
               coalesce(nullif(cm.comment_label_json ->> 'comment_sentiment', ''), '') AS comment_sentiment
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE c.event_id = %s
          AND coalesce(cm.comment_author_name, '') <> ''
        ORDER BY cm.published_at DESC NULLS LAST, cm.interaction_cnt DESC NULLS LAST, cm.comment_id
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    matched_rows = []
    for row in rows:
        row["comment_user_id"] = build_comment_user_id(row.get("platform"), row.get("comment_author_name"), row.get("location"))
        if row["comment_user_id"] == comment_user_id:
            matched_rows.append(row)
    return matched_rows


def fetch_event_sales_lead_source_efficiency(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    query = """
        SELECT
          coalesce(nullif(c.platform, ''), coalesce(nullif(cm.platform, ''), '未标注平台')) AS platform,
          c.content_id,
          coalesce(nullif(c.title, ''), '未命名内容') AS title,
          c.source_url,
          coalesce(nullif(a.author_name, ''), '未标注作者') AS author_name,
          coalesce(nullif(cm.comment_label_json ->> 'comment_intent', ''), '未标注') AS comment_intent,
          coalesce(nullif(cm.comment_label_json ->> 'purchase_signal', ''), '未标注') AS purchase_signal,
          cm.comment_id,
          cm.comment_author_name,
          cm.comment_text,
          cm.published_at,
          cm.interaction_cnt
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        LEFT JOIN data_asset.dwd_author a ON c.author_id = a.author_id
        WHERE c.event_id = %s
          AND cm.comment_label_json IS NOT NULL
        ORDER BY cm.interaction_cnt DESC NULLS LAST, cm.published_at DESC NULLS LAST, cm.comment_id
        LIMIT 3000
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_sales_lead_source_efficiency(rows)


def build_sales_lead_source_efficiency(rows: list[dict[str, Any]]) -> dict[str, Any]:
    high_signals = {"中", "强"}
    inquiry_intents = {"询价", "报价", "价格敏感", "到店", "试驾"}
    normalized = [
        {
            "platform": str(row.get("platform") or "未标注平台").strip() or "未标注平台",
            "content_id": row.get("content_id") or "",
            "title": row.get("title") or "未命名内容",
            "source_url": row.get("source_url"),
            "author_name": row.get("author_name") or "未标注作者",
            "comment_intent": str(row.get("comment_intent") or "未标注").strip() or "未标注",
            "purchase_signal": str(row.get("purchase_signal") or "未标注").strip() or "未标注",
            "comment_id": row.get("comment_id"),
            "comment_author_name": row.get("comment_author_name"),
            "comment_text": row.get("comment_text") or "",
            "published_at": row.get("published_at"),
            "interaction_cnt": int(row.get("interaction_cnt") or 0),
        }
        for row in rows
    ]
    high_rows = [row for row in normalized if row["purchase_signal"] in high_signals]
    strong_rows = [row for row in normalized if row["purchase_signal"] == "强"]
    inquiry_rows = [row for row in normalized if row["comment_intent"] in inquiry_intents]

    platform_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    content_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in normalized:
        platform_groups[row["platform"]].append(row)
        if row["content_id"]:
            content_groups[str(row["content_id"])].append(row)

    platform_efficiency = []
    for platform, group_rows in platform_groups.items():
        platform_high_rows = [row for row in group_rows if row["purchase_signal"] in high_signals]
        platform_strong_rows = [row for row in group_rows if row["purchase_signal"] == "强"]
        platform_mid_rows = [row for row in group_rows if row["purchase_signal"] == "中"]
        platform_low_rows = [row for row in group_rows if row["purchase_signal"] == "弱"]
        platform_efficiency.append(
            {
                "platform": platform,
                "comment_count": len(group_rows),
                "high_intent_comment_count": len(platform_high_rows),
                "strong_signal_comment_count": len(platform_strong_rows),
                "mid_signal_comment_count": len(platform_mid_rows),
                "low_signal_comment_count": len(platform_low_rows),
                "high_intent_rate": round(len(platform_high_rows) * 100 / len(group_rows), 1) if group_rows else 0,
            }
        )
    platform_efficiency.sort(key=lambda item: (-item["high_intent_comment_count"], -item["high_intent_rate"], item["platform"]))

    content_leads = []
    for content_id, group_rows in content_groups.items():
        content_high_rows = [row for row in group_rows if row["purchase_signal"] in high_signals]
        if not content_high_rows:
            continue
        first = group_rows[0]
        intent_counter = Counter(row["comment_intent"] for row in content_high_rows)
        dominant_intent = sorted(intent_counter.items(), key=lambda item: (-item[1], item[0]))[0][0]
        content_leads.append(
            {
                "content_id": content_id,
                "title": first["title"],
                "platform": first["platform"],
                "author_name": first["author_name"],
                "source_url": first["source_url"],
                "comment_count": len(group_rows),
                "high_intent_comment_count": len(content_high_rows),
                "strong_signal_comment_count": sum(1 for row in content_high_rows if row["purchase_signal"] == "强"),
                "dominant_intent": dominant_intent,
            }
        )
    content_leads.sort(key=lambda item: (-item["high_intent_comment_count"], -item["strong_signal_comment_count"], item["title"]))

    follow_up_rows = [row for row in normalized if row["purchase_signal"] in {"强", "中", "弱"}]
    lead_comments = sorted(follow_up_rows, key=lambda row: (-row["interaction_cnt"], row.get("published_at") or "", row.get("comment_id") or ""))[:20]
    source_platform_count = len({row["platform"] for row in high_rows})
    top_platform = platform_efficiency[0]["platform"] if platform_efficiency else None
    top_content = content_leads[0]["title"] if content_leads else None
    if normalized:
        conclusion = (
            f"本事件识别到中/强购买信号 {len(high_rows)} 条，其中强购买信号 {len(strong_rows)} 条；"
            f"主要线索来源平台为「{top_platform or '暂无'}」，高意向内容集中在「{top_content or '暂无'}」。"
        )
    else:
        conclusion = "暂未识别到销售线索来源数据。补入 comment_label_json.purchase_signal 和 comment_intent 后，这里会展示平台与内容的线索效率。"

    return {
        "summary": {
            "comment_count": len(normalized),
            "high_intent_comment_count": len(high_rows),
            "strong_signal_comment_count": len(strong_rows),
            "inquiry_comment_count": len(inquiry_rows),
            "source_platform_count": source_platform_count,
            "top_platform": top_platform,
            "top_content": top_content,
            "rule_based_conclusion": conclusion,
        },
        "platform_efficiency": platform_efficiency[:10],
        "content_leads": content_leads[:10],
        "lead_comments": lead_comments,
    }


def fetch_author_base(conn: psycopg.Connection, author_id: str) -> dict[str, Any]:
    query = """
        WITH latest_kol_profile AS (
          SELECT DISTINCT ON (author_id)
                 author_id, kol_main_type, content_tendency, car_focus, remark,
                 profile_batch, source_file_name, updated_time
          FROM data_asset.user_profile_kol
          WHERE author_id = %s
          ORDER BY author_id, updated_time DESC NULLS LAST, kol_profile_id DESC
        )
        SELECT a.author_id, a.platform, a.author_name, a.author_type, a.is_kol,
               a.author_home_url, a.author_desc, a.fans_cnt,
               p.kol_main_type, p.content_tendency, p.car_focus, p.remark,
               p.profile_batch, p.source_file_name, p.updated_time AS kol_profile_updated_time
        FROM data_asset.dwd_author a
        LEFT JOIN latest_kol_profile p ON a.author_id = p.author_id
        WHERE a.author_id = %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [author_id, author_id])
        row = normalize_row(dict(cur.fetchone() or {}))
    if not row:
        return {"author": {}, "kol_profile": {}}
    kol_profile = {
        "kol_main_type": row.pop("kol_main_type", None),
        "content_tendency": row.pop("content_tendency", None),
        "car_focus": row.pop("car_focus", None),
        "remark": row.pop("remark", None),
        "profile_batch": row.pop("profile_batch", None),
        "source_file_name": row.pop("source_file_name", None),
        "updated_time": row.pop("kol_profile_updated_time", None),
    }
    if not any(kol_profile.values()):
        kol_profile = {}
    return {"author": row, "kol_profile": kol_profile}


def fetch_author_metrics(conn: psycopg.Connection, author_id: str) -> dict[str, Any]:
    query = """
        WITH contents AS (
          SELECT content_id, event_id, engagement_total
          FROM data_asset.dwd_content
          WHERE author_id = %s
        )
        SELECT
          (SELECT count(DISTINCT event_id)::bigint FROM contents) AS event_count,
          (SELECT count(DISTINCT content_id)::bigint FROM contents) AS content_count,
          (SELECT count(DISTINCT cm.comment_id)::bigint FROM data_asset.dwd_comment cm JOIN contents c ON cm.content_id = c.content_id) AS received_comment_count,
          (SELECT coalesce(sum(engagement_total), 0)::bigint FROM contents) AS total_engagement
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [author_id])
        return normalize_row(dict(cur.fetchone() or {}))


def fetch_author_events(conn: psycopg.Connection, author_id: str) -> list[dict[str, Any]]:
    query = """
        WITH content_stats AS (
          SELECT c.event_id,
                 count(DISTINCT c.content_id)::bigint AS content_count,
                 coalesce(sum(c.engagement_total), 0)::bigint AS total_engagement,
                 min(c.published_at) AS first_published_at,
                 max(c.published_at) AS last_published_at
          FROM data_asset.dwd_content c
          WHERE c.author_id = %s
          GROUP BY c.event_id
        ),
        comment_stats AS (
          SELECT c.event_id, count(DISTINCT cm.comment_id)::bigint AS received_comment_count
          FROM data_asset.dwd_content c
          LEFT JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id
          WHERE c.author_id = %s
          GROUP BY c.event_id
        )
        SELECT e.event_id, e.event_name, e.event_status, e.brand_name, e.model_name,
               cs.content_count, coalesce(cms.received_comment_count, 0)::bigint AS received_comment_count,
               cs.total_engagement, cs.first_published_at, cs.last_published_at
        FROM content_stats cs
        JOIN data_asset.dwd_event e ON cs.event_id = e.event_id
        LEFT JOIN comment_stats cms ON cs.event_id = cms.event_id
        ORDER BY cs.total_engagement DESC, received_comment_count DESC, cs.last_published_at DESC NULLS LAST
        LIMIT 20
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [author_id, author_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_author_contents(conn: psycopg.Connection, author_id: str, limit: int = 50) -> list[dict[str, Any]]:
    query = """
        SELECT c.content_id, c.event_id, e.event_name, c.platform, c.source_url, c.title,
               c.content_type, c.media_form, c.published_at,
               c.like_cnt, c.comment_cnt, c.share_cnt, c.favorite_cnt, c.view_cnt,
               c.engagement_total
        FROM data_asset.dwd_content c
        LEFT JOIN data_asset.dwd_event e ON c.event_id = e.event_id
        WHERE c.author_id = %s
        ORDER BY c.engagement_total DESC NULLS LAST, c.published_at DESC NULLS LAST
        LIMIT %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [author_id, limit])
        return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_author_comment_quality(conn: psycopg.Connection, author_id: str) -> dict[str, Any]:
    base_where = "c.author_id = %s AND cm.comment_label_json IS NOT NULL"
    summary_query = f"""
        SELECT
          count(*)::bigint AS labeled_comment_count,
          count(*) FILTER (WHERE cm.comment_label_json ->> 'is_vehicle_related' = '是')::bigint AS vehicle_related_count,
          round(100.0 * count(*) FILTER (WHERE cm.comment_label_json ->> 'is_vehicle_related' = '是') / nullif(count(*), 0), 1) AS vehicle_related_rate,
          round(100.0 * count(*) FILTER (WHERE cm.comment_label_json ->> 'comment_sentiment' = '正向') / nullif(count(*), 0), 1) AS positive_rate,
          round(100.0 * count(*) FILTER (WHERE cm.comment_label_json ->> 'comment_sentiment' = '负向') / nullif(count(*), 0), 1) AS negative_rate,
          count(*) FILTER (WHERE cm.comment_label_json ->> 'purchase_signal' IN ('中', '强'))::bigint AS mid_high_purchase_signal_count,
          round(100.0 * count(*) FILTER (WHERE cm.comment_label_json ->> 'purchase_signal' IN ('中', '强')) / nullif(count(*), 0), 1) AS mid_high_purchase_signal_rate
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE {base_where}
    """
    distribution_query = """
        SELECT coalesce(nullif(cm.comment_label_json ->> {field}, ''), '未标注') AS label,
               count(*)::bigint AS count
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE {base_where}
        GROUP BY 1
        ORDER BY count DESC, label
    """
    aspect_query = f"""
        SELECT aspect AS label, count(*)::bigint AS count
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        CROSS JOIN LATERAL jsonb_array_elements_text(
          CASE
            WHEN jsonb_typeof(cm.comment_label_json -> 'mentioned_aspect') = 'array'
              THEN cm.comment_label_json -> 'mentioned_aspect'
            WHEN cm.comment_label_json ? 'mentioned_aspect'
              THEN jsonb_build_array(cm.comment_label_json ->> 'mentioned_aspect')
            ELSE '[]'::jsonb
          END
        ) AS aspect
        WHERE {base_where}
        GROUP BY aspect
        ORDER BY count DESC, aspect
        LIMIT 20
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(summary_query, [author_id])
        summary = normalize_row(dict(cur.fetchone() or {}))
        cur.execute(distribution_query.format(field="'comment_sentiment'", base_where=base_where), [author_id])
        sentiment_distribution = build_rate_distribution([normalize_row(dict(row)) for row in cur.fetchall()])
        cur.execute(distribution_query.format(field="'comment_intent'", base_where=base_where), [author_id])
        intent_distribution = build_rate_distribution([normalize_row(dict(row)) for row in cur.fetchall()])
        cur.execute(aspect_query, [author_id])
        aspect_distribution = build_rate_distribution([normalize_row(dict(row)) for row in cur.fetchall()])
        cur.execute(distribution_query.format(field="'purchase_signal'", base_where=base_where), [author_id])
        purchase_signal_distribution = build_rate_distribution([normalize_row(dict(row)) for row in cur.fetchall()])
    labeled_count = int(summary.get("labeled_comment_count") or 0)
    valid_count = int(summary.get("vehicle_related_count") or 0)
    summary.setdefault("vehicle_related_rate", 0)
    summary.setdefault("positive_rate", 0)
    summary.setdefault("negative_rate", 0)
    summary.setdefault("mid_high_purchase_signal_count", 0)
    summary.setdefault("mid_high_purchase_signal_rate", 0)
    summary["invalid_comment_count"] = max(labeled_count - valid_count, 0)
    summary["top_aspect"] = aspect_distribution[0]["label"] if aspect_distribution else None
    summary["top_intent"] = intent_distribution[0]["label"] if intent_distribution else None
    return {
        "summary": summary,
        "sentiment_distribution": sentiment_distribution,
        "intent_distribution": intent_distribution,
        "aspect_distribution": aspect_distribution,
        "purchase_signal_distribution": purchase_signal_distribution,
    }


def fetch_author_sankey_rows(conn: psycopg.Connection, author_id: str) -> list[dict[str, Any]]:
    query = """
        SELECT e.event_id, e.event_name,
               coalesce(nullif(cm.platform, ''), nullif(c.platform, '')) AS platform,
               cm.comment_author_name,
               cm.location,
               count(DISTINCT cm.comment_id)::bigint AS comment_count
        FROM data_asset.dwd_content c
        JOIN data_asset.dwd_event e ON c.event_id = e.event_id
        JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id
        WHERE c.author_id = %s
          AND coalesce(cm.comment_author_name, '') <> ''
        GROUP BY e.event_id, e.event_name, coalesce(nullif(cm.platform, ''), nullif(c.platform, '')), cm.comment_author_name, cm.location
        ORDER BY comment_count DESC, e.event_name
        LIMIT 500
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [author_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    for row in rows:
        row["comment_user_id"] = build_comment_user_id(row.get("platform"), row.get("comment_author_name"), row.get("location"))
    return rows


def fetch_latest_profile_label_map(conn: psycopg.Connection, comment_user_ids: list[str]) -> dict[str, str]:
    if not comment_user_ids:
        return {}
    query = """
        SELECT DISTINCT ON (comment_user_id)
               comment_user_id,
               coalesce(nullif(main_label, ''), '未画像用户') AS main_label
        FROM data_asset.user_profile_comment_result
        WHERE comment_user_id = ANY(%s)
        ORDER BY comment_user_id, updated_time DESC NULLS LAST, comment_user_profile_id DESC
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [comment_user_ids])
        return {row["comment_user_id"]: row["main_label"] for row in cur.fetchall()}


def fetch_latest_comment_user_profile_map(conn: psycopg.Connection, comment_user_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not comment_user_ids:
        return {}
    query = """
        SELECT DISTINCT ON (comment_user_id)
               comment_user_id,
               coalesce(nullif(main_label, ''), '未画像用户') AS main_label,
               main_dimension,
               main_score,
               profile_batch,
               updated_time
        FROM data_asset.user_profile_comment_result
        WHERE comment_user_id = ANY(%s)
        ORDER BY comment_user_id, updated_time DESC NULLS LAST, comment_user_profile_id DESC
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [comment_user_ids])
        return {row["comment_user_id"]: normalize_row(dict(row)) for row in cur.fetchall()}


def build_author_profile_sankey(
    author_id: str,
    author_name: str,
    rows: list[dict[str, Any]],
    profile_map: dict[str, str],
) -> dict[str, Any]:
    author_node_id = f"author:{author_id}"
    event_totals: Counter[str] = Counter()
    event_names: dict[str, str] = {}
    profile_totals: Counter[tuple[str, str]] = Counter()
    for row in rows:
        event_id = str(row.get("event_id") or "unknown")
        event_name = str(row.get("event_name") or "未知事件")
        comment_user_id = str(row.get("comment_user_id") or "")
        profile_label = profile_map.get(comment_user_id) or "未画像用户"
        value = int(row.get("comment_count") or 0)
        if value <= 0:
            continue
        event_names[event_id] = event_name
        event_totals[event_id] += value
        profile_totals[(event_id, profile_label)] += value

    top_event_ids = [event_id for event_id, _ in event_totals.most_common(8)]
    top_profile_pairs = {pair for pair, _ in profile_totals.most_common(12)}
    compact_profile_totals: Counter[tuple[str, str]] = Counter()
    for pair, value in profile_totals.items():
        if pair[0] not in top_event_ids:
            continue
        compact_profile_totals[pair if pair in top_profile_pairs else (pair[0], "其他画像")] += value

    nodes = [{"id": author_node_id, "label": author_name, "layer": 0}]
    links = []
    for event_id in top_event_ids:
        event_node_id = f"event:{event_id}"
        nodes.append({"id": event_node_id, "label": event_names.get(event_id, "未知事件"), "layer": 1})
        links.append({"source": author_node_id, "target": event_node_id, "value": event_totals[event_id]})

    profile_labels = []
    for (event_id, profile_label), value in compact_profile_totals.items():
        if profile_label not in profile_labels:
            profile_labels.append(profile_label)
        links.append({"source": f"event:{event_id}", "target": f"profile:{profile_label}", "value": value})

    nodes.extend({"id": f"profile:{label}", "label": label, "layer": 2} for label in profile_labels)
    return {"nodes": nodes, "links": links}


def build_rate_distribution(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    total = sum(int(row.get("count") or 0) for row in rows)
    distribution = []
    for row in rows:
        count = int(row.get("count") or 0)
        distribution.append(
            {
                "label": row.get("label") or "未标注",
                "count": count,
                "rate": round(count * 100 / total, 1) if total else 0,
            }
        )
    return distribution


def fetch_event_subject_story(
    conn: psycopg.Connection,
    event_id: str,
    kol_type_distribution: list[dict[str, Any]],
) -> dict[str, Any]:
    subject_query = """
        WITH content_base AS (
          SELECT c.content_id,
                 CASE
                   WHEN coalesce(a.is_kol, false) THEN 'KOL'
                   ELSE coalesce(nullif(a.author_type, ''), '未维护作者类型')
                 END AS subject_type,
                 coalesce(c.engagement_total, 0)::bigint AS engagement_total
          FROM data_asset.dwd_content c
          LEFT JOIN data_asset.dwd_author a ON c.author_id = a.author_id
          WHERE c.event_id = %s
        ),
        comment_base AS (
          SELECT c.content_id, count(cm.comment_id)::bigint AS comment_count
          FROM data_asset.dwd_content c
          LEFT JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id
          WHERE c.event_id = %s
          GROUP BY c.content_id
        )
        SELECT cb.subject_type,
               count(DISTINCT cb.content_id)::bigint AS content_count,
               coalesce(sum(comment_base.comment_count), 0)::bigint AS comment_count,
               coalesce(sum(cb.engagement_total), 0)::bigint AS total_engagement
        FROM content_base cb
        LEFT JOIN comment_base ON cb.content_id = comment_base.content_id
        GROUP BY cb.subject_type
        ORDER BY total_engagement DESC, comment_count DESC, content_count DESC, subject_type
    """
    top_author_query = """
        WITH author_base AS (
          SELECT a.author_id,
                 coalesce(nullif(a.author_name, ''), '未知作者') AS author_name,
                 CASE
                   WHEN coalesce(a.is_kol, false) THEN 'KOL'
                   ELSE coalesce(nullif(a.author_type, ''), '未维护作者类型')
                 END AS subject_type,
                 coalesce(a.is_kol, false) AS is_kol,
                 count(DISTINCT c.content_id)::bigint AS content_count,
                 count(DISTINCT cm.comment_id)::bigint AS comment_count,
                 coalesce(sum(DISTINCT c.engagement_total), 0)::bigint AS total_engagement
          FROM data_asset.dwd_content c
          LEFT JOIN data_asset.dwd_author a ON c.author_id = a.author_id
          LEFT JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id
          WHERE c.event_id = %s
          GROUP BY a.author_id, a.author_name, a.author_type, a.is_kol
        )
        SELECT author_id, author_name, subject_type, is_kol, content_count, comment_count, total_engagement
        FROM author_base
        ORDER BY total_engagement DESC, comment_count DESC, content_count DESC, author_name
        LIMIT 8
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(subject_query, [event_id, event_id])
        subject_rows = [normalize_row(dict(row)) for row in cur.fetchall()]
        cur.execute(top_author_query, [event_id])
        top_authors = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_subject_story(subject_rows, kol_type_distribution, top_authors)


def build_subject_story(
    subject_rows: list[dict[str, Any]],
    kol_type_rows: list[dict[str, Any]],
    top_authors: list[dict[str, Any]],
) -> dict[str, Any]:
    subject_distribution = build_rate_distribution(
        [{"label": row.get("subject_type") or "未维护作者类型", "count": int(row.get("total_engagement") or 0)} for row in subject_rows]
    )
    total_engagement = sum(int(row.get("total_engagement") or 0) for row in subject_rows)
    total_content = sum(int(row.get("content_count") or 0) for row in subject_rows)
    total_comments = sum(int(row.get("comment_count") or 0) for row in subject_rows)
    dominant = subject_distribution[0] if subject_distribution else {"label": "暂无数据", "count": 0, "rate": 0}
    top_kol_row = max(kol_type_rows, key=lambda row: int(row.get("total_engagement") or 0), default={})
    top_kol_type = top_kol_row.get("kol_main_type") or "暂无KOL画像"
    kol_engagement = sum(int(row.get("total_engagement") or 0) for row in subject_rows if row.get("subject_type") == "KOL")
    kol_engagement_rate = round(kol_engagement * 100 / total_engagement, 1) if total_engagement else 0

    if dominant["label"] == "KOL" and dominant["rate"] >= 50:
        pattern = "KOL带动"
        conclusion = (
            f"本事件传播主要由KOL带动，KOL贡献 {kol_engagement_rate}% 总互动；"
            f"其中「{top_kol_type}」贡献最高，可优先作为后续投放与复盘对象。"
        )
    elif dominant["label"] not in {"暂无数据", "KOL"}:
        pattern = f"{dominant['label']}带动"
        conclusion = (
            f"本事件传播主要由「{dominant['label']}」带动，贡献 {dominant['rate']}% 总互动；"
            "可结合热门作者与评论质量判断是否具备自然扩散价值。"
        )
    else:
        pattern = "主体分散"
        conclusion = "本事件传播主体暂未形成单一主导来源，可结合平台与热门内容继续观察。"

    return {
        "summary": {
            "total_engagement": total_engagement,
            "total_content_count": total_content,
            "total_comment_count": total_comments,
            "dominant_subject_type": dominant["label"],
            "dominant_subject_engagement": dominant["count"],
            "dominant_subject_engagement_rate": dominant["rate"],
            "kol_engagement": kol_engagement,
            "kol_engagement_rate": kol_engagement_rate,
            "top_kol_type": top_kol_type,
            "subject_pattern": pattern,
            "rule_based_conclusion": conclusion,
        },
        "subject_distribution": subject_distribution,
        "kol_type_distribution": kol_type_rows,
        "top_authors": top_authors,
    }


def fetch_event_platform_story(conn: psycopg.Connection, event_id: str) -> dict[str, Any]:
    query = """
        WITH content_platform AS (
          SELECT coalesce(nullif(platform, ''), '未知平台') AS platform,
                 count(DISTINCT content_id)::bigint AS content_count,
                 coalesce(sum(engagement_total), 0)::bigint AS total_engagement
          FROM data_asset.dwd_content
          WHERE event_id = %s
          GROUP BY 1
        ),
        comment_platform AS (
          SELECT coalesce(nullif(c.platform, ''), nullif(cm.platform, ''), '未知平台') AS platform,
                 count(DISTINCT cm.comment_id)::bigint AS comment_count,
                 count(DISTINCT cm.comment_id) FILTER (WHERE cm.comment_label_json IS NOT NULL)::bigint AS labeled_comment_count,
                 count(DISTINCT cm.comment_id) FILTER (WHERE cm.comment_label_json ->> 'is_vehicle_related' = '是')::bigint AS vehicle_related_count,
                 count(DISTINCT cm.comment_id) FILTER (WHERE cm.comment_label_json ->> 'purchase_signal' IN ('中', '强'))::bigint AS mid_high_purchase_signal_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE c.event_id = %s
          GROUP BY 1
        ),
        platforms AS (
          SELECT platform FROM content_platform
          UNION
          SELECT platform FROM comment_platform
        )
        SELECT p.platform,
               coalesce(cp.content_count, 0)::bigint AS content_count,
               coalesce(cm.comment_count, 0)::bigint AS comment_count,
               coalesce(cp.content_count, 0) + coalesce(cm.comment_count, 0)::bigint AS total_volume,
               coalesce(cp.total_engagement, 0)::bigint AS total_engagement,
               coalesce(cm.labeled_comment_count, 0)::bigint AS labeled_comment_count,
               coalesce(cm.vehicle_related_count, 0)::bigint AS vehicle_related_count,
               coalesce(cm.mid_high_purchase_signal_count, 0)::bigint AS mid_high_purchase_signal_count
        FROM platforms p
        LEFT JOIN content_platform cp USING (platform)
        LEFT JOIN comment_platform cm USING (platform)
        ORDER BY total_volume DESC, total_engagement DESC, p.platform
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, event_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_platform_story(rows)


def build_platform_story(platform_rows: list[dict[str, Any]]) -> dict[str, Any]:
    total_volume = sum(int(row.get("total_volume") or 0) for row in platform_rows)
    if not platform_rows or total_volume == 0:
        return {
            "summary": {
                "core_platform": "暂无数据",
                "core_platform_volume": 0,
                "core_platform_volume_rate": 0,
                "core_platform_engagement_per_content": 0,
                "core_platform_effective_comment_rate": 0,
                "core_platform_purchase_signal_rate": 0,
                "rule_based_conclusion": "暂无平台分布数据，暂时无法判断渠道选择。",
            },
            "platform_efficiency": [],
        }

    enriched_rows = []
    for row in platform_rows:
        content_count = int(row.get("content_count") or 0)
        total_engagement = int(row.get("total_engagement") or 0)
        total_volume_row = int(row.get("total_volume") or 0)
        labeled_count = int(row.get("labeled_comment_count") or 0)
        vehicle_related = int(row.get("vehicle_related_count") or 0)
        purchase_signal = int(row.get("mid_high_purchase_signal_count") or 0)
        enriched_rows.append(
            {
                "platform": row.get("platform") or "未知平台",
                "content_count": content_count,
                "comment_count": int(row.get("comment_count") or 0),
                "total_volume": total_volume_row,
                "volume_rate": round(total_volume_row * 100 / total_volume, 1) if total_volume else 0,
                "total_engagement": total_engagement,
                "engagement_per_content": round(total_engagement / content_count, 1) if content_count else 0,
                "labeled_comment_count": labeled_count,
                "vehicle_related_count": vehicle_related,
                "effective_comment_rate": round(vehicle_related * 100 / labeled_count, 1) if labeled_count else 0,
                "mid_high_purchase_signal_count": purchase_signal,
                "purchase_signal_rate": round(purchase_signal * 100 / labeled_count, 1) if labeled_count else 0,
            }
        )
    enriched_rows.sort(
        key=lambda item: (
            item["purchase_signal_rate"],
            item["effective_comment_rate"],
            item["volume_rate"],
            item["total_engagement"],
        ),
        reverse=True,
    )
    core_platform = max(enriched_rows, key=lambda item: (item["total_volume"], item["total_engagement"]))
    conclusion = (
        f"本事件主要在「{core_platform['platform']}」形成传播，贡献 {core_platform['volume_rate']}% 声量；"
        f"该平台有效评论率 {core_platform['effective_comment_rate']}%，中/强购买信号占 {core_platform['purchase_signal_rate']}%，"
        "可作为渠道放大优先级判断依据。"
    )
    return {
        "summary": {
            "core_platform": core_platform["platform"],
            "core_platform_volume": core_platform["total_volume"],
            "core_platform_volume_rate": core_platform["volume_rate"],
            "core_platform_engagement_per_content": core_platform["engagement_per_content"],
            "core_platform_effective_comment_rate": core_platform["effective_comment_rate"],
            "core_platform_purchase_signal_rate": core_platform["purchase_signal_rate"],
            "rule_based_conclusion": conclusion,
        },
        "platform_efficiency": enriched_rows,
    }
def fetch_event_content(conn: psycopg.Connection, event_id: str, content_id: str) -> dict[str, Any]:
    query = """
        SELECT c.content_id, c.event_id, c.platform, c.source_url, c.title, c.content_text,
               c.content_type, c.media_form, c.published_at,
               c.like_cnt, c.comment_cnt, c.share_cnt, c.favorite_cnt, c.view_cnt, c.engagement_total,
               a.author_id, a.author_name, a.author_type, coalesce(a.is_kol, false) AS is_kol,
               a.author_home_url, a.fans_cnt
        FROM data_asset.dwd_content c
        LEFT JOIN data_asset.dwd_author a ON c.author_id = a.author_id
        WHERE c.event_id = %s AND c.content_id = %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, content_id])
        row = cur.fetchone()
    return normalize_row(dict(row)) if row else {}


def fetch_event_content_comments(
    conn: psycopg.Connection,
    content_id: str,
    sort: str,
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], int]:
    order_sql = (
        "cm.published_at DESC NULLS LAST, cm.interaction_cnt DESC NULLS LAST, cm.comment_id"
        if sort == "published_at"
        else "cm.interaction_cnt DESC NULLS LAST, cm.published_at DESC NULLS LAST, cm.comment_id"
    )
    root_filter = "(cm.parent_comment_id IS NULL OR cm.parent_comment_id = '')"
    count_query = f"SELECT count(*)::bigint AS total FROM data_asset.dwd_comment cm WHERE cm.content_id = %s AND {root_filter}"
    data_query = f"""
        WITH root_page AS (
          SELECT cm.comment_id, cm.content_id, cm.platform, cm.location,
                 cm.comment_author_id, cm.comment_author_name, cm.parent_comment_id,
                 NULL::varchar AS parent_comment_author_name,
                 cm.comment_text, cm.published_at,
                 cm.like_cnt, cm.reply_cnt, cm.interaction_cnt,
                 row_number() OVER (ORDER BY {order_sql}) AS thread_order,
                 0 AS reply_order
          FROM data_asset.dwd_comment cm
          WHERE cm.content_id = %s AND {root_filter}
          ORDER BY {order_sql}
          LIMIT %s OFFSET %s
        ),
        reply_rows AS (
          SELECT child.comment_id, child.content_id, child.platform, child.location,
                 child.comment_author_id, child.comment_author_name, child.parent_comment_id,
                 root.comment_author_name AS parent_comment_author_name,
                 child.comment_text, child.published_at,
                 child.like_cnt, child.reply_cnt, child.interaction_cnt,
                 root.thread_order,
                 row_number() OVER (
                   PARTITION BY root.comment_id
                   ORDER BY child.published_at ASC NULLS LAST, child.interaction_cnt DESC NULLS LAST, child.comment_id
                 ) AS reply_order
          FROM root_page root
          JOIN data_asset.dwd_comment child
            ON child.content_id = root.content_id
           AND (
             child.parent_comment_id = root.comment_id
             OR (
               child.parent_comment_id ILIKE '%%e+%%'
               AND root.comment_id LIKE regexp_replace(split_part(lower(child.parent_comment_id), 'e', 1), '\\.', '', 'g') || '%%'
             )
           )
        )
        SELECT comment_id, content_id, platform, location,
               comment_author_id, comment_author_name, parent_comment_id,
               parent_comment_author_name, comment_text, published_at,
               like_cnt, reply_cnt, interaction_cnt
        FROM (
          SELECT * FROM root_page
          UNION ALL
          SELECT * FROM reply_rows
        ) threaded
        ORDER BY thread_order, reply_order
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(count_query, [content_id])
        total = int(cur.fetchone()["total"])
        cur.execute(data_query, [content_id, limit, offset])
        comments = [normalize_row(dict(row)) for row in cur.fetchall()]
    return comments, total


def fetch_event_content_comment_timeline(conn: psycopg.Connection, content_id: str, content_published_at: Any) -> list[dict[str, Any]]:
    query = """
        SELECT published_at, interaction_cnt
        FROM data_asset.dwd_comment
        WHERE content_id = %s AND published_at IS NOT NULL
        ORDER BY published_at
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [content_id])
        rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return build_content_comment_timeline(rows, content_published_at)


LIFECYCLE_BUCKETS: tuple[tuple[str, float, float | None], ...] = (
    ("0-3h", 0, 3),
    ("3-6h", 3, 6),
    ("6-9h", 6, 9),
    ("9-12h", 9, 12),
    ("12-24h", 12, 24),
    ("24-48h", 24, 48),
    ("48h+", 48, None),
)


def parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value).replace("Z", "").replace("T", " "))
    except ValueError:
        return None


def lifecycle_bucket_for(hours_after_publish: float) -> str | None:
    if hours_after_publish < 0:
        return None
    for label, start_hour, end_hour in LIFECYCLE_BUCKETS:
        if hours_after_publish >= start_hour and (end_hour is None or hours_after_publish < end_hour):
            return label
    return "48h+"


def build_content_comment_timeline(rows: list[dict[str, Any]], content_published_at: Any) -> list[dict[str, Any]]:
    publish_dt = parse_datetime(content_published_at)
    buckets: dict[str, dict[str, int | str]] = {
        label: {"time_bucket": label, "relative_bucket": label, "comment_count": 0, "interaction_count": 0}
        for label, _, _ in LIFECYCLE_BUCKETS
    }
    if not publish_dt:
        return []
    for row in rows:
        comment_dt = parse_datetime(row.get("published_at"))
        if not comment_dt:
            continue
        hours_after_publish = (comment_dt - publish_dt).total_seconds() / 3600
        bucket_key = lifecycle_bucket_for(hours_after_publish)
        if not bucket_key:
            continue
        bucket = buckets[bucket_key]
        bucket["comment_count"] = int(bucket["comment_count"]) + 1
        bucket["interaction_count"] = int(bucket["interaction_count"]) + int(row.get("interaction_cnt") or 0)
    return list(buckets.values())


def describe_comment_peak_bucket(timeline: list[dict[str, Any]]) -> str | None:
    bucket_order = {label: index for index, (label, _, _) in enumerate(LIFECYCLE_BUCKETS)}
    non_empty_points = [point for point in timeline if int(point.get("comment_count") or 0) > 0]
    if not non_empty_points:
        return None
    peak = max(
        non_empty_points,
        key=lambda point: (
            int(point.get("comment_count") or 0),
            int(point.get("interaction_count") or 0),
            -bucket_order.get(str(point.get("relative_bucket") or point.get("time_bucket") or ""), 999),
        ),
    )
    return str(peak.get("relative_bucket") or peak.get("time_bucket") or "")


def fetch_event_top_contents(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    query = """
        SELECT c.content_id, c.platform, c.title, c.content_type, c.media_form,
               a.author_name, coalesce(a.is_kol, false) AS is_kol,
               c.published_at, c.engagement_total, c.comment_cnt, c.source_url
        FROM data_asset.dwd_content c
        LEFT JOIN data_asset.dwd_author a ON c.author_id = a.author_id
        WHERE c.event_id = %s
        ORDER BY c.engagement_total DESC NULLS LAST, c.comment_cnt DESC NULLS LAST
        LIMIT 30
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_event_kol_voice(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    query = """
        WITH latest_kol_profile AS (
          SELECT DISTINCT ON (author_id)
                 author_id, kol_main_type, content_tendency, car_focus, remark, profile_batch, updated_time
          FROM data_asset.user_profile_kol
          ORDER BY author_id, updated_time DESC NULLS LAST
        )
        SELECT a.author_id, a.platform, a.author_name, a.author_type, a.fans_cnt, a.author_home_url,
               p.kol_main_type, p.content_tendency, p.car_focus, p.remark,
               count(DISTINCT c.content_id) AS content_cnt,
               count(DISTINCT cm.comment_id) AS comment_cnt,
               coalesce(sum(DISTINCT c.engagement_total), 0) AS total_engagement
        FROM data_asset.dwd_content c
        JOIN data_asset.dwd_author a ON c.author_id = a.author_id
        LEFT JOIN latest_kol_profile p ON a.author_id = p.author_id
        LEFT JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id
        WHERE c.event_id = %s AND a.is_kol = true
        GROUP BY a.author_id, a.platform, a.author_name, a.author_type, a.fans_cnt, a.author_home_url,
                 p.kol_main_type, p.content_tendency, p.car_focus, p.remark
        ORDER BY total_engagement DESC NULLS LAST, comment_cnt DESC NULLS LAST
        LIMIT 30
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id])
        return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_latest_comment_user_profiles(conn: psycopg.Connection, event_id: str) -> list[dict[str, Any]]:
    comment_query = """
        SELECT coalesce(cm.platform, c.platform) AS platform,
               cm.comment_author_name,
               cm.location,
               c.author_id AS content_author_id
        FROM data_asset.dwd_comment cm
        JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE c.event_id = %s AND coalesce(cm.comment_author_name, '') <> ''
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(comment_query, [event_id])
        comment_rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    user_to_kols: dict[str, set[str]] = defaultdict(set)
    for row in comment_rows:
        comment_user_id = build_comment_user_id(row.get("platform"), row.get("comment_author_name"), row.get("location"))
        if row.get("content_author_id"):
            user_to_kols[comment_user_id].add(row["content_author_id"])
    if not user_to_kols:
        return []
    profile_query = """
        SELECT DISTINCT ON (comment_user_id)
               comment_user_id, platform, comment_author_name, location,
               main_dimension, main_label, main_score, total_comments, valid_comments,
               profile_batch, prompt_version, updated_time
        FROM data_asset.user_profile_comment_result
        WHERE comment_user_id = ANY(%s)
        ORDER BY comment_user_id, updated_time DESC NULLS LAST
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(profile_query, [list(user_to_kols.keys())])
        profiles = [normalize_row(dict(row)) for row in cur.fetchall()]
    for profile in profiles:
        profile["kol_author_ids"] = sorted(user_to_kols.get(profile["comment_user_id"], set()))
    return profiles


def summarize_user_profiles(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter = Counter(row.get("main_label") or "未打主标签" for row in profile_rows)
    return [
        {"main_label": label, "user_cnt": count}
        for label, count in counter.most_common(20)
    ]


def summarize_kol_user_matrix(
    kol_voice: list[dict[str, Any]],
    profile_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    kol_names = {row["author_id"]: row.get("author_name", "") for row in kol_voice}
    matrix: dict[tuple[str, str], int] = defaultdict(int)
    for profile in profile_rows:
        label = profile.get("main_label") or "未打主标签"
        for author_id in profile.get("kol_author_ids", []):
            if author_id in kol_names:
                matrix[(author_id, label)] += 1
    rows = [
        {
            "author_id": author_id,
            "author_name": kol_names.get(author_id, ""),
            "main_label": label,
            "user_cnt": count,
        }
        for (author_id, label), count in matrix.items()
    ]
    rows.sort(key=lambda item: (item["author_name"], -item["user_cnt"], item["main_label"]))
    return rows[:50]
