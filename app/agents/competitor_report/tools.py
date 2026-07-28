from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.agents.qa.time_slice import date_bounds
from app.config import DATABASE_URL
from app.services.asset_library import normalize_row
from app.services.report_time import format_shanghai_datetime


TOTAL_ENGAGEMENT_SQL = "coalesce(interaction_like_cnt,0)+coalesce(comment_cnt,0)+coalesce(favorite_cnt,0)+coalesce(share_cnt,0)"
SCOPE_SQL = "w.brand_name = %s AND w.published_at >= %s AND w.published_at < %s"
# Keep this order aligned with skill_generator._rank_top_works so the LLM and
# rendered report select the same Top3 from full-scope records.
TOP_WORK_ORDER_SQL = """
total_engagement DESC,
coalesce(w.interaction_like_cnt, 0) DESC,
coalesce(w.comment_cnt, 0) DESC,
w.published_at DESC NULLS LAST,
coalesce(w.work_id::text, '') ASC,
coalesce(w.title, '') ASC,
coalesce(w.author_name, '') ASC
""".strip()


def _rows(cursor: psycopg.Cursor) -> list[dict[str, Any]]:
    return [normalize_row(dict(row)) for row in cursor.fetchall()]


def to_competitor_skill_record(row: dict[str, Any]) -> dict[str, Any]:
    def metric(key: str) -> int:
        return int(row.get(key) or 0)

    def yes_no(key: str) -> str:
        value = row.get(key)
        if isinstance(value, str):
            return "是" if value.strip().lower() in {"1", "true", "t", "yes", "是"} else "否"
        return "是" if value else "否"

    likes = metric("interaction_like_cnt")
    comments = metric("comment_cnt")
    favorites = metric("favorite_cnt")
    shares = metric("share_cnt")
    return {
        "作品ID": str(row.get("work_id") or ""),
        "标题": str(row.get("title") or ""),
        "作者": str(row.get("author_name") or ""),
        "品牌": str(row.get("brand_name") or ""),
        "账号类型": str(row.get("account_type") or ""),
        "是否官方号": yes_no("is_official"),
        "发布时间": format_shanghai_datetime(row.get("published_at")),
        "视频链接": str(row.get("video_url") or ""),
        "封面图路径": str(row.get("cover_url") or ""),
        "互动点赞数": likes,
        "评论数": comments,
        "收藏数": favorites,
        "分享数": shares,
        "总互动量": likes + comments + favorites + shares,
        "是否置顶": yes_no("is_pinned"),
        "话题标签": str(row.get("topic_tags") or ""),
    }


def collect_competitor_report_dataset(
    brand_name: str,
    start_date: str,
    end_date: str,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    start, end = date_bounds(start_date, end_date)
    params = [brand_name, start, end]
    with psycopg.connect(database_url, row_factory=dict_row) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT count(*)::bigint AS work_count,
                       count(DISTINCT author_name)::bigint AS account_count,
                       coalesce(sum({TOTAL_ENGAGEMENT_SQL}), 0)::bigint AS total_engagement,
                       coalesce(avg({TOTAL_ENGAGEMENT_SQL}), 0) AS average_engagement
                FROM data_asset.competitor_work w
                WHERE {SCOPE_SQL}
                """,
                params,
            )
            overview_row = cursor.fetchone()
            overview = normalize_row(dict(overview_row)) if overview_row else {
                "work_count": 0,
                "account_count": 0,
                "total_engagement": 0,
                "average_engagement": 0,
            }

            cursor.execute(
                f"""
                SELECT published_at::date AS publish_date,
                       count(*)::bigint AS work_count,
                       coalesce(sum({TOTAL_ENGAGEMENT_SQL}), 0)::bigint AS total_engagement
                FROM data_asset.competitor_work w
                WHERE {SCOPE_SQL}
                GROUP BY published_at::date
                ORDER BY publish_date ASC
                """,
                params,
            )
            daily_trend = _rows(cursor)

            cursor.execute(
                f"""
                SELECT author_name, account_type, is_official,
                       count(*)::bigint AS work_count,
                       coalesce(sum({TOTAL_ENGAGEMENT_SQL}), 0)::bigint AS total_engagement
                FROM data_asset.competitor_work w
                WHERE {SCOPE_SQL}
                GROUP BY author_name, account_type, is_official
                ORDER BY total_engagement DESC, author_name ASC
                """,
                params,
            )
            account_contribution = _rows(cursor)

            cursor.execute(
                f"""
                WITH scoped_works AS (
                  SELECT topic_tags, {TOTAL_ENGAGEMENT_SQL} AS total_engagement
                  FROM data_asset.competitor_work w
                  WHERE {SCOPE_SQL}
                ), topic_rows AS (
                  SELECT nullif(trim(BOTH ' #' FROM raw_topic), '') AS topic, total_engagement
                  FROM scoped_works
                  CROSS JOIN LATERAL regexp_split_to_table(coalesce(topic_tags, ''), '[,，#[:space:]]+') AS raw_topic
                )
                SELECT topic, count(*)::bigint AS work_count,
                       coalesce(sum(total_engagement), 0)::bigint AS total_engagement
                FROM topic_rows
                WHERE topic IS NOT NULL
                GROUP BY topic
                ORDER BY work_count DESC, total_engagement DESC, topic ASC
                """,
                params,
            )
            topic_distribution = _rows(cursor)

            cursor.execute(
                f"""
                /* full_scope_records */
                SELECT w.work_id AS work_id, w.title, w.author_name, w.brand_name,
                       w.account_type, w.is_official, w.published_at, w.topic_tags, w.video_url, w.cover_url,
                       w.is_pinned,
                       w.interaction_like_cnt, w.comment_cnt, w.favorite_cnt, w.share_cnt,
                       {TOTAL_ENGAGEMENT_SQL} AS total_engagement,
                       i.insight_markdown
                FROM data_asset.competitor_work w
                LEFT JOIN data_asset.competitor_work_insight i ON i.work_id = w.work_id
                WHERE {SCOPE_SQL}
                ORDER BY {TOP_WORK_ORDER_SQL}
                """,
                params,
            )
            records = _rows(cursor)

            cursor.execute(
                f"""
                SELECT w.work_id AS work_id, w.title, w.author_name, w.brand_name,
                       w.account_type, w.is_official, w.published_at, w.topic_tags, w.video_url, w.cover_url,
                       w.is_pinned,
                       w.interaction_like_cnt, w.comment_cnt, w.favorite_cnt, w.share_cnt,
                       {TOTAL_ENGAGEMENT_SQL} AS total_engagement,
                       i.insight_markdown
                FROM data_asset.competitor_work w
                LEFT JOIN data_asset.competitor_work_insight i ON i.work_id = w.work_id
                WHERE {SCOPE_SQL}
                ORDER BY {TOP_WORK_ORDER_SQL}
                LIMIT 3
                """,
                params,
            )
            top_works = _rows(cursor)

    for work in top_works:
        if not str(work.get("insight_markdown") or "").strip():
            work["insight_markdown"] = "无"
    records = [to_competitor_skill_record(work) for work in records]

    work_count = int(overview.get("work_count") or 0)
    data_notes = ["总互动量为互动点赞数、评论数、收藏数与分享数之和。"]
    if work_count < 3:
        data_notes.append(f"筛选范围内仅有 {work_count} 条作品，热门作品按实际数量展示。")
    if any(work["insight_markdown"] == "无" for work in top_works):
        data_notes.append("部分热门作品未维护解读，缺失内容显示“无”。")

    return {
        "brand_name": brand_name,
        "start_date": start_date,
        "end_date": end_date,
        "overview": overview,
        "daily_trend": daily_trend,
        "account_contribution": account_contribution,
        "topic_distribution": topic_distribution,
        "records": records,
        "top_works": top_works,
        "data_notes": data_notes,
    }
