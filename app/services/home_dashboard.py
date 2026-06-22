from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.asset_library import normalize_row
from app.services.event_voc_insights import extract_hash_topics

OWN_BRAND_NAME = "一汽大众-大众品牌"
EXCLUDED_PKO_TARGETS = {"其他", "其他对象", "其他维度", "未提及", "未标注", "无", "未知"}


def to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, Decimal):
        return int(value)
    return int(value)


def clamp_days(days: int) -> int:
    return max(1, min(days, 365))


def build_trend(current: int, previous: int) -> dict[str, Any]:
    if previous <= 0 and current > 0:
        return {"value": None, "label": "新出现", "tone": "new"}
    if previous <= 0:
        return {"value": 0, "label": "持平", "tone": "flat"}
    change = round((current - previous) * 100 / previous, 1)
    if change > 0:
        return {"value": change, "label": f"环比 +{change}%", "tone": "up"}
    if change < 0:
        return {"value": change, "label": f"环比 {change}%", "tone": "down"}
    return {"value": change, "label": "持平", "tone": "flat"}


def get_auto_voc_home(days: int = 30, database_url: str = DATABASE_URL) -> dict[str, Any]:
    period_days = clamp_days(days)
    now = datetime.now()
    since = now - timedelta(days=period_days)
    previous_since = since - timedelta(days=period_days)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            overview = fetch_overview(cur, since)
            business_metrics = fetch_business_metrics(cur, since, now, previous_since)
            key_events = fetch_key_events(cur, since)
            topics = fetch_hot_topics(cur, since)
            competitor_updates = fetch_competitor_updates(cur, since)
            signals = fetch_attention_signals(cur, since)
    return {
        "period_days": period_days,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "overview": overview,
        "business_metrics": business_metrics,
        "key_events": key_events,
        "hot_topics": topics,
        "auto_hot_searches": [],
        "competitor_updates": competitor_updates,
        "attention_signals": signals,
        "ai_prompts": [
            "总结近30天VOC重点",
            "哪些事件需要关注？",
            "竞品最近有什么动作？",
            "哪些用户值得销售跟进？",
        ],
    }


def fetch_business_metrics(
    cur: psycopg.Cursor,
    since: datetime,
    until: datetime,
    previous_since: datetime,
) -> list[dict[str, Any]]:
    current_brand_rows = fetch_brand_event_rollups(cur, since, until)
    previous_brand_rows = fetch_brand_event_rollups(cur, previous_since, since)
    current_by_brand = {row["brand_name"]: row for row in current_brand_rows}
    previous_by_brand = {row["brand_name"]: row for row in previous_brand_rows}

    own_current = current_by_brand.get(OWN_BRAND_NAME, {"event_count": 0, "total_volume": 0})
    own_previous = previous_by_brand.get(OWN_BRAND_NAME, {"event_count": 0, "total_volume": 0})

    competitor_candidates = [row for row in current_brand_rows if row["brand_name"] != OWN_BRAND_NAME]
    top_competitor = max(competitor_candidates, key=lambda row: row["total_volume"], default=None)
    competitor_previous_volume = 0
    if top_competitor:
        competitor_previous_volume = to_int(previous_by_brand.get(top_competitor["brand_name"], {}).get("total_volume"))

    pko_current = fetch_top_pko_target(cur, since, until)
    pko_previous_count = fetch_pko_target_count(cur, previous_since, since, pko_current["target"]) if pko_current["target"] else 0

    hot_event = fetch_hottest_event_metric(cur, since, until)
    hot_event_previous_volume = (
        fetch_event_volume(cur, previous_since, since, hot_event["event_id"]) if hot_event.get("event_id") else 0
    )

    return [
        {
            "metric_key": "own_brand",
            "label": "本品事件及声量",
            "title": OWN_BRAND_NAME,
            "primary_text": f"{to_int(own_current.get('event_count'))}/{to_int(own_current.get('total_volume'))}",
            "secondary_text": "事件数 / 总声量",
            "event_count": to_int(own_current.get("event_count")),
            "volume": to_int(own_current.get("total_volume")),
            "brand_name": OWN_BRAND_NAME,
            "trend": build_trend(to_int(own_current.get("total_volume")), to_int(own_previous.get("total_volume"))),
        },
        {
            "metric_key": "competitor_brand",
            "label": "竞品事件及声量",
            "title": top_competitor["brand_name"] if top_competitor else "暂无竞品事件",
            "primary_text": f"{to_int(top_competitor.get('event_count'))}/{to_int(top_competitor.get('total_volume'))}" if top_competitor else "0/0",
            "secondary_text": "声量最高竞品品牌",
            "event_count": to_int(top_competitor.get("event_count")) if top_competitor else 0,
            "volume": to_int(top_competitor.get("total_volume")) if top_competitor else 0,
            "brand_name": top_competitor["brand_name"] if top_competitor else None,
            "trend": build_trend(to_int(top_competitor.get("total_volume")) if top_competitor else 0, competitor_previous_volume),
        },
        {
            "metric_key": "top_pko_target",
            "label": "高频对比对象",
            "title": pko_current["target"] or "暂无明确对比对象",
            "primary_text": f"{to_int(pko_current.get('count'))}次",
            "secondary_text": "已排除其他/未提及",
            "count": to_int(pko_current.get("count")),
            "trend": build_trend(to_int(pko_current.get("count")), pko_previous_count),
        },
        {
            "metric_key": "hottest_event",
            "label": "最热事件",
            "title": hot_event.get("event_name") or "暂无事件",
            "primary_text": f"{to_int(hot_event.get('total_volume'))}",
            "secondary_text": "全品牌最高声量事件",
            "event_id": hot_event.get("event_id"),
            "event_name": hot_event.get("event_name"),
            "volume": to_int(hot_event.get("total_volume")),
            "trend": build_trend(to_int(hot_event.get("total_volume")), hot_event_previous_volume),
        },
    ]


def fetch_brand_event_rollups(cur: psycopg.Cursor, since: datetime, until: datetime) -> list[dict[str, Any]]:
    cur.execute(
        """
        WITH period_content AS (
          SELECT event_id, count(DISTINCT content_id)::bigint AS content_count
          FROM data_asset.dwd_content
          WHERE published_at >= %s AND published_at < %s
          GROUP BY event_id
        ),
        period_comment AS (
          SELECT c.event_id, count(DISTINCT cm.comment_id)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE cm.published_at >= %s AND cm.published_at < %s
          GROUP BY c.event_id
        ),
        period_events AS (
          SELECT e.event_id, coalesce(nullif(e.brand_name, ''), '未知品牌') AS brand_name,
                 coalesce(pc.content_count, 0)::bigint AS content_count,
                 coalesce(pm.comment_count, 0)::bigint AS comment_count
          FROM data_asset.dwd_event e
          LEFT JOIN period_content pc ON e.event_id = pc.event_id
          LEFT JOIN period_comment pm ON e.event_id = pm.event_id
          WHERE coalesce(e.start_time, e.created_time) < %s
            AND coalesce(e.end_time, e.start_time, e.created_time) >= %s
        )
        SELECT brand_name,
               count(DISTINCT event_id)::bigint AS event_count,
               sum(content_count + comment_count)::bigint AS total_volume
        FROM period_events
        GROUP BY brand_name
        ORDER BY total_volume DESC
        """,
        [since, until, since, until, until, since],
    )
    return [{**normalize_row(dict(row)), "event_count": to_int(row.get("event_count")), "total_volume": to_int(row.get("total_volume"))} for row in cur.fetchall()]


def fetch_top_pko_target(cur: psycopg.Cursor, since: datetime, until: datetime) -> dict[str, Any]:
    cur.execute(
        """
        WITH pko_rows AS (
          SELECT coalesce(
                   nullif(cm.comment_label_json #>> '{pko,target}', ''),
                   nullif(cm.comment_label_json ->> 'pko_target', '')
                 ) AS target
          FROM data_asset.dwd_comment cm
          WHERE cm.published_at >= %s AND cm.published_at < %s
            AND cm.comment_label_json IS NOT NULL
            AND coalesce(
                  nullif(cm.comment_label_json #>> '{pko,has_pko}', ''),
                  nullif(cm.comment_label_json ->> 'has_pko', '')
                ) IN ('是', '有', 'true', 'TRUE', '1', 'yes', 'YES')
        )
        SELECT target, count(*)::bigint AS count
        FROM pko_rows
        WHERE target IS NOT NULL
          AND target <> ALL(%s::text[])
        GROUP BY target
        ORDER BY count DESC, target ASC
        LIMIT 1
        """,
        [since, until, list(EXCLUDED_PKO_TARGETS)],
    )
    row = dict(cur.fetchone() or {})
    return {"target": row.get("target"), "count": to_int(row.get("count"))}


def fetch_pko_target_count(cur: psycopg.Cursor, since: datetime, until: datetime, target: str | None) -> int:
    if not target:
        return 0
    cur.execute(
        """
        SELECT count(*)::bigint AS count
        FROM data_asset.dwd_comment cm
        WHERE cm.published_at >= %s AND cm.published_at < %s
          AND cm.comment_label_json IS NOT NULL
          AND coalesce(
                nullif(cm.comment_label_json #>> '{pko,target}', ''),
                nullif(cm.comment_label_json ->> 'pko_target', '')
              ) = %s
          AND coalesce(
                nullif(cm.comment_label_json #>> '{pko,has_pko}', ''),
                nullif(cm.comment_label_json ->> 'has_pko', '')
              ) IN ('是', '有', 'true', 'TRUE', '1', 'yes', 'YES')
        """,
        [since, until, target],
    )
    return to_int((cur.fetchone() or {}).get("count"))


def fetch_hottest_event_metric(cur: psycopg.Cursor, since: datetime, until: datetime) -> dict[str, Any]:
    cur.execute(
        """
        WITH period_content AS (
          SELECT event_id, count(DISTINCT content_id)::bigint AS content_count
          FROM data_asset.dwd_content
          WHERE published_at >= %s AND published_at < %s
          GROUP BY event_id
        ),
        period_comment AS (
          SELECT c.event_id, count(DISTINCT cm.comment_id)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE cm.published_at >= %s AND cm.published_at < %s
          GROUP BY c.event_id
        )
        SELECT e.event_id, e.event_name,
               (coalesce(pc.content_count, 0) + coalesce(pm.comment_count, 0))::bigint AS total_volume
        FROM data_asset.dwd_event e
        LEFT JOIN period_content pc ON e.event_id = pc.event_id
        LEFT JOIN period_comment pm ON e.event_id = pm.event_id
        WHERE coalesce(e.start_time, e.created_time) < %s
          AND coalesce(e.end_time, e.start_time, e.created_time) >= %s
        ORDER BY total_volume DESC, e.start_time DESC NULLS LAST
        LIMIT 1
        """,
        [since, until, since, until, until, since],
    )
    row = dict(cur.fetchone() or {})
    return normalize_row(row) if row else {"event_id": None, "event_name": None, "total_volume": 0}


def fetch_event_volume(cur: psycopg.Cursor, since: datetime, until: datetime, event_id: str) -> int:
    cur.execute(
        """
        SELECT (
          (SELECT count(DISTINCT content_id) FROM data_asset.dwd_content WHERE event_id = %s AND published_at >= %s AND published_at < %s)
          +
          (SELECT count(DISTINCT cm.comment_id)
           FROM data_asset.dwd_comment cm
           JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
           WHERE c.event_id = %s AND cm.published_at >= %s AND cm.published_at < %s)
        )::bigint AS total_volume
        """,
        [event_id, since, until, event_id, since, until],
    )
    return to_int((cur.fetchone() or {}).get("total_volume"))


def fetch_overview(cur: psycopg.Cursor, since: datetime) -> dict[str, int]:
    cur.execute(
        """
        WITH recent_contents AS (
          SELECT content_id, event_id, author_id
          FROM data_asset.dwd_content
          WHERE published_at >= %s
        ),
        recent_comments AS (
          SELECT cm.comment_id, c.event_id, c.author_id
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE cm.published_at >= %s
        ),
        recent_events AS (
          SELECT event_id
          FROM data_asset.dwd_event
          WHERE coalesce(start_time, created_time) >= %s
          UNION
          SELECT event_id
          FROM recent_contents
          WHERE event_id IS NOT NULL
          UNION
          SELECT event_id
          FROM recent_comments
          WHERE event_id IS NOT NULL
        ),
        recent_authors AS (
          SELECT author_id
          FROM recent_contents
          WHERE author_id IS NOT NULL
          UNION
          SELECT author_id
          FROM recent_comments
          WHERE author_id IS NOT NULL
        )
        SELECT
          (SELECT count(DISTINCT event_id) FROM recent_events)::bigint AS event_count,
          (SELECT count(DISTINCT content_id) FROM recent_contents)::bigint AS content_count,
          (SELECT count(DISTINCT comment_id) FROM recent_comments)::bigint AS comment_count,
          (SELECT count(DISTINCT author_id) FROM recent_authors)::bigint AS author_count,
          (SELECT count(*) FROM data_asset.dwd_event)::bigint AS total_event_count,
          (SELECT count(*) FROM data_asset.dwd_content)::bigint AS total_content_count,
          (SELECT count(*) FROM data_asset.dwd_comment)::bigint AS total_comment_count,
          (SELECT count(*) FROM data_asset.dwd_author)::bigint AS total_author_count
        """,
        [since, since, since],
    )
    row = dict(cur.fetchone() or {})
    return {key: to_int(value) for key, value in row.items()}


def fetch_key_events(cur: psycopg.Cursor, since: datetime) -> list[dict[str, Any]]:
    cur.execute(
        """
        WITH recent_content AS (
          SELECT event_id, count(DISTINCT content_id)::bigint AS content_count,
                 coalesce(sum(engagement_total), 0)::bigint AS total_engagement
          FROM data_asset.dwd_content
          WHERE published_at >= %s
          GROUP BY event_id
        ),
        recent_comment AS (
          SELECT c.event_id, count(DISTINCT cm.comment_id)::bigint AS comment_count
          FROM data_asset.dwd_comment cm
          JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
          WHERE cm.published_at >= %s
          GROUP BY c.event_id
        )
        SELECT e.event_id, e.event_name, e.brand_name, e.model_name, e.event_type, e.event_status,
               e.start_time, e.end_time,
               coalesce(rc.content_count, 0)::bigint AS content_count,
               coalesce(rm.comment_count, 0)::bigint AS comment_count,
               coalesce(rc.total_engagement, 0)::bigint AS total_engagement,
               (coalesce(rc.content_count, 0) + coalesce(rm.comment_count, 0))::bigint AS total_volume
        FROM data_asset.dwd_event e
        LEFT JOIN recent_content rc ON e.event_id = rc.event_id
        LEFT JOIN recent_comment rm ON e.event_id = rm.event_id
        WHERE coalesce(e.start_time, e.created_time) >= %s
           OR coalesce(rc.content_count, 0) > 0
           OR coalesce(rm.comment_count, 0) > 0
        ORDER BY total_volume DESC, total_engagement DESC, e.start_time DESC NULLS LAST
        LIMIT 6
        """,
        [since, since, since],
    )
    return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_hot_topics(cur: psycopg.Cursor, since: datetime) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT c.content_id, c.title, c.content_text, c.engagement_total,
               count(cm.comment_id)::bigint AS comment_count
        FROM data_asset.dwd_content c
        LEFT JOIN data_asset.dwd_comment cm ON c.content_id = cm.content_id
        WHERE c.published_at >= %s
        GROUP BY c.content_id, c.title, c.content_text, c.engagement_total
        ORDER BY c.engagement_total DESC NULLS LAST
        LIMIT 500
        """,
        [since],
    )
    topic_map: dict[str, dict[str, Any]] = {}
    topic_contents: dict[str, set[str]] = defaultdict(set)
    for row in cur.fetchall():
        topics = extract_hash_topics(row.get("title"), row.get("content_text"))
        for topic in topics:
            bucket = topic_map.setdefault(
                topic,
                {"topic": topic, "content_count": 0, "comment_count": 0, "total_engagement": 0},
            )
            content_id = str(row.get("content_id") or "")
            if content_id and content_id not in topic_contents[topic]:
                topic_contents[topic].add(content_id)
                bucket["content_count"] += 1
                bucket["comment_count"] += to_int(row.get("comment_count"))
                bucket["total_engagement"] += to_int(row.get("engagement_total"))
    topics = sorted(
        topic_map.values(),
        key=lambda item: (item["comment_count"], item["total_engagement"], item["content_count"]),
        reverse=True,
    )
    return topics[:8]


def fetch_competitor_updates(cur: psycopg.Cursor, since: datetime) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT work_id, title, author_name, brand_name, account_type, is_official,
               coalesce(interaction_like_cnt, 0)::bigint AS interaction_like_cnt,
               coalesce(comment_cnt, 0)::bigint AS comment_cnt,
               coalesce(favorite_cnt, 0)::bigint AS favorite_cnt,
               coalesce(share_cnt, 0)::bigint AS share_cnt,
               published_at, video_url,
               (coalesce(interaction_like_cnt, 0) + coalesce(comment_cnt, 0) + coalesce(favorite_cnt, 0) + coalesce(share_cnt, 0))::bigint AS total_interaction
        FROM data_asset.competitor_work
        WHERE published_at >= %s
        ORDER BY total_interaction DESC, published_at DESC NULLS LAST
        LIMIT 6
        """,
        [since],
    )
    return [normalize_row(dict(row)) for row in cur.fetchall()]


def fetch_attention_signals(cur: psycopg.Cursor, since: datetime) -> list[dict[str, Any]]:
    cur.execute(
        """
        SELECT
          count(*) FILTER (WHERE cm.comment_label_json ->> 'purchase_signal' = %s)::bigint AS strong_purchase_count,
          count(*) FILTER (WHERE cm.comment_label_json ->> 'purchase_signal' IN (%s, %s))::bigint AS mid_high_purchase_count,
          count(*) FILTER (WHERE cm.comment_label_json ->> 'comment_sentiment' = %s)::bigint AS negative_comment_count,
          count(*) FILTER (WHERE cm.comment_label_json IS NOT NULL)::bigint AS labeled_comment_count
        FROM data_asset.dwd_comment cm
        WHERE cm.published_at >= %s
        """,
        ["强", "中", "强", "负向", since],
    )
    row = dict(cur.fetchone() or {})
    strong = to_int(row.get("strong_purchase_count"))
    mid_high = to_int(row.get("mid_high_purchase_count"))
    negative = to_int(row.get("negative_comment_count"))
    labeled = to_int(row.get("labeled_comment_count"))
    return [
        {
            "signal_key": "strong_purchase",
            "label": "强购买信号",
            "value": strong,
            "description": "近30天评论中明确表达强购买意向的用户声音。",
            "tone": "intent",
        },
        {
            "signal_key": "mid_high_purchase",
            "label": "中/强购买信号",
            "value": mid_high,
            "description": "可作为销售线索池继续下钻。",
            "tone": "positive",
        },
        {
            "signal_key": "negative_comments",
            "label": "负向评论",
            "value": negative,
            "description": "建议进入市场/产品看板定位集中讨论点。",
            "tone": "negative",
        },
        {
            "signal_key": "labeled_comments",
            "label": "已打标评论",
            "value": labeled,
            "description": "当前可被AI和规则分析直接使用的评论资产。",
            "tone": "neutral",
        },
    ]
