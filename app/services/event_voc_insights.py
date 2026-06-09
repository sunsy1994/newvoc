from __future__ import annotations

from collections import Counter, defaultdict
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
        kol_type_distribution = fetch_event_kol_type_distribution(conn, event_id)
        profile_rows = fetch_latest_comment_user_profiles(conn, event_id)
        hot_posts = fetch_event_hot_posts(conn, event_id)
    return {
        "event": overview,
        "overview_metrics": build_market_overview_metrics(overview, kol_type_distribution),
        "volume_trend": trend,
        "channel_distribution": channel_distribution,
        "kol_type_distribution": kol_type_distribution,
        "user_profile_distribution": summarize_user_profiles(profile_rows),
        "hot_posts": hot_posts,
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
            return {"content": {}, "comments": [], "total": 0, "limit": limit, "offset": offset, "sort": sort}
        comments, total = fetch_event_content_comments(conn, content_id, sort=sort, limit=limit, offset=offset)
    return {
        "content": content,
        "comments": comments,
        "total": total,
        "limit": limit,
        "offset": offset,
        "sort": sort,
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
        SELECT content_id, title, coalesce(engagement_total, 0)::bigint AS total_engagement
        FROM data_asset.dwd_content
        WHERE event_id = %s
        ORDER BY engagement_total DESC NULLS LAST, published_at DESC NULLS LAST
        LIMIT %s
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query, [event_id, limit])
        return [normalize_row(dict(row)) for row in cur.fetchall()]


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
