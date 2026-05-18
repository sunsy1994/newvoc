import pandas as pd

from ._event_asset_utils import NEGATIVE_SENTIMENTS, write_refresh_table


def run(engine, params: dict) -> dict:
    rel_df = pd.read_sql("SELECT event_id, content_id FROM data_asset.rel_event_content", engine)
    content_df = pd.read_sql(
        """
        SELECT content_id, published_at, engagement_total
        FROM data_asset.dwd_content
        """,
        engine,
    )
    comment_df = pd.read_sql(
        """
        SELECT content_id, comment_id, published_at, sentiment_tag
        FROM data_asset.dwd_comment
        """,
        engine,
    )

    event_content = rel_df.merge(content_df, on="content_id", how="left")
    event_comment = rel_df.merge(comment_df, on="content_id", how="left")
    event_content["published_at"] = pd.to_datetime(event_content["published_at"], errors="coerce")
    event_comment["published_at"] = pd.to_datetime(event_comment["published_at"], errors="coerce")

    content_daily = (
        event_content.assign(stat_date=pd.to_datetime(event_content["published_at"]).dt.date)
        .groupby(["event_id", "stat_date"], as_index=False)
        .agg(
            content_cnt=("content_id", "nunique"),
            engagement_cnt=("engagement_total", "sum"),
        )
    )
    comment_daily = (
        event_comment.assign(
            stat_date=pd.to_datetime(event_comment["published_at"]).dt.date,
            negative_flag=event_comment["sentiment_tag"].fillna("").isin(NEGATIVE_SENTIMENTS).astype(int),
        )
        .groupby(["event_id", "stat_date"], as_index=False)
        .agg(
            comment_cnt=("comment_id", "nunique"),
            negative_comment_cnt=("negative_flag", "sum"),
        )
    )

    trend = content_daily.merge(comment_daily, on=["event_id", "stat_date"], how="outer").fillna(0)
    trend["heat_score"] = (
        trend["content_cnt"].fillna(0) * 1.0
        + trend["comment_cnt"].fillna(0) * 0.2
        + trend["engagement_cnt"].fillna(0) * 0.02
    ).round(2)
    trend = trend.sort_values(["event_id", "stat_date"]).reset_index(drop=True)

    write_refresh_table(engine, "ads_event_trend_daily", trend)
    return {
        "processed_rows": int(len(event_content) + len(event_comment)),
        "output_rows": int(len(trend)),
        "message": "事件趋势日表计算完成",
    }
