import json

import pandas as pd

from ._event_asset_utils import (
    NEGATIVE_SENTIMENTS,
    build_topic_top_json,
    normalize_event_status,
    write_refresh_table,
)


def _safe_growth(recent: float, previous: float) -> float:
    if previous <= 0:
        return 100.0 if recent > 0 else 0.0
    return round(((recent - previous) / previous) * 100, 2)


def _min_max_normalize(series: pd.Series) -> pd.Series:
    if series.empty:
        return series
    minimum = float(series.min())
    maximum = float(series.max())
    if maximum <= minimum:
        return pd.Series([0.0] * len(series), index=series.index)
    return ((series - minimum) / (maximum - minimum) * 100).round(2)


def run(engine, params: dict) -> dict:
    event_df = pd.read_sql(
        """
        SELECT event_id, event_name, event_desc, event_type, brand_name, model_name,
               keyword_list, start_time, end_time, event_status, updated_time
        FROM data_asset.dwd_event
        """,
        engine,
    )
    rel_df = pd.read_sql("SELECT event_id, content_id FROM data_asset.rel_event_content", engine)
    content_df = pd.read_sql(
        """
        SELECT content_id, author_id, platform, is_kol, published_at, engagement_total, updated_time
        FROM data_asset.dwd_content
        """,
        engine,
    )
    comment_df = pd.read_sql(
        """
        SELECT comment_id, content_id, published_at, sentiment_tag, opinion_tag, intention_tag, updated_time
        FROM data_asset.dwd_comment
        """,
        engine,
    )

    event_content_df = rel_df.merge(content_df, on="content_id", how="left")
    event_comment_df = rel_df.merge(comment_df, on="content_id", how="left")
    event_content_df["published_at"] = pd.to_datetime(event_content_df["published_at"], errors="coerce")
    event_comment_df["published_at"] = pd.to_datetime(event_comment_df["published_at"], errors="coerce")

    content_summary = (
        event_content_df.groupby("event_id", as_index=False)
        .agg(
            content_cnt=("content_id", "nunique"),
            author_cnt=("author_id", "nunique"),
            total_engagement=("engagement_total", "sum"),
            content_latest_time=("updated_time", "max"),
        )
    )
    kol_summary = (
        event_content_df[event_content_df["is_kol"].fillna(False)]
        .groupby("event_id", as_index=False)["author_id"]
        .nunique()
        .rename(columns={"author_id": "kol_cnt"})
    )

    comment_summary = (
        event_comment_df.groupby("event_id", as_index=False)
        .agg(
            comment_cnt=("comment_id", "nunique"),
            negative_comment_cnt=("sentiment_tag", lambda values: int(values.fillna("").isin(NEGATIVE_SENTIMENTS).sum())),
            labeled_comment_cnt=("sentiment_tag", lambda values: int(values.fillna("").astype(str).str.strip().ne("").sum())),
            comment_latest_time=("updated_time", "max"),
        )
    )
    topic_summary = build_topic_top_json(event_comment_df)

    platform_summary = (
        event_content_df.groupby("event_id")["platform"]
        .apply(lambda values: json.dumps(sorted({value for value in values.dropna() if str(value).strip()}), ensure_ascii=False))
        .reset_index(name="platform_list")
    )

    now = pd.Timestamp.now()
    recent_start = now - pd.Timedelta(days=7)
    previous_start = now - pd.Timedelta(days=14)

    content_heat = event_content_df.assign(
        content_heat=1.0 + event_content_df["engagement_total"].fillna(0) * 0.02,
    )
    comment_heat = event_comment_df.assign(comment_heat=0.2)

    recent_content = (
        content_heat[content_heat["published_at"] >= recent_start]
        .groupby("event_id", as_index=False)["content_heat"]
        .sum()
        .rename(columns={"content_heat": "recent_content_heat"})
    )
    previous_content = (
        content_heat[(content_heat["published_at"] >= previous_start) & (content_heat["published_at"] < recent_start)]
        .groupby("event_id", as_index=False)["content_heat"]
        .sum()
        .rename(columns={"content_heat": "prev_content_heat"})
    )
    recent_comment = (
        comment_heat[comment_heat["published_at"] >= recent_start]
        .groupby("event_id", as_index=False)["comment_heat"]
        .sum()
        .rename(columns={"comment_heat": "recent_comment_heat"})
    )
    previous_comment = (
        comment_heat[(comment_heat["published_at"] >= previous_start) & (comment_heat["published_at"] < recent_start)]
        .groupby("event_id", as_index=False)["comment_heat"]
        .sum()
        .rename(columns={"comment_heat": "prev_comment_heat"})
    )

    result = (
        event_df.merge(content_summary, on="event_id", how="left")
        .merge(kol_summary, on="event_id", how="left")
        .merge(comment_summary, on="event_id", how="left")
        .merge(topic_summary, on="event_id", how="left")
        .merge(platform_summary, on="event_id", how="left")
        .merge(recent_content, on="event_id", how="left")
        .merge(previous_content, on="event_id", how="left")
        .merge(recent_comment, on="event_id", how="left")
        .merge(previous_comment, on="event_id", how="left")
    ).fillna(
        {
            "comment_cnt": 0,
            "negative_comment_cnt": 0,
            "labeled_comment_cnt": 0,
            "topic_top_json": "[]",
            "platform_list": "[]",
            "content_cnt": 0,
            "author_cnt": 0,
            "kol_cnt": 0,
            "recent_content_heat": 0,
            "prev_content_heat": 0,
            "recent_comment_heat": 0,
            "prev_comment_heat": 0,
            "total_engagement": 0,
        }
    )

    result["negative_ratio"] = result.apply(
        lambda row: round(
            float(row["negative_comment_cnt"]) / float(row["labeled_comment_cnt"]),
            4,
        )
        if row["labeled_comment_cnt"] > 0
        else 0,
        axis=1,
    )
    result["risk_level"] = result["negative_ratio"].apply(
        lambda value: "高" if value >= 0.45 else "中" if value >= 0.2 else "低"
    )
    result["recent_heat"] = result["recent_content_heat"] + result["recent_comment_heat"]
    result["prev_heat"] = result["prev_content_heat"] + result["prev_comment_heat"]
    result["growth_rate"] = result.apply(
        lambda row: _safe_growth(float(row["recent_heat"]), float(row["prev_heat"])),
        axis=1,
    )
    result["heat_raw"] = (
        result["content_cnt"].fillna(0) * 1.0
        + result["comment_cnt"].fillna(0) * 0.2
        + result["total_engagement"].fillna(0) * 0.02
    )
    result["heat_score"] = _min_max_normalize(result["heat_raw"]).round(1)
    result["event_status"] = result.apply(
        lambda row: normalize_event_status(row["end_time"], row["event_status"]),
        axis=1,
    )
    result["updated_time"] = result[["updated_time", "content_latest_time", "comment_latest_time"]].max(axis=1)

    result = result[
        [
            "event_id",
            "event_name",
            "event_desc",
            "event_type",
            "brand_name",
            "model_name",
            "keyword_list",
            "start_time",
            "end_time",
            "event_status",
            "platform_list",
            "content_cnt",
            "comment_cnt",
            "author_cnt",
            "kol_cnt",
            "total_engagement",
            "negative_comment_cnt",
            "negative_ratio",
            "heat_score",
            "recent_heat",
            "prev_heat",
            "growth_rate",
            "risk_level",
            "topic_top_json",
            "updated_time",
        ]
    ]

    write_refresh_table(engine, "ads_event_asset_overview", result)
    return {
        "processed_rows": int(len(event_content_df) + len(event_comment_df)),
        "output_rows": int(len(result)),
        "message": "事件资产概览计算完成",
    }
