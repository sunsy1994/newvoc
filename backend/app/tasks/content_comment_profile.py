import pandas as pd
import json

from ._event_asset_utils import NEGATIVE_SENTIMENTS, write_refresh_table


def run(engine, params: dict) -> dict:
    comment_df = pd.read_sql(
        """
        select
          content_id,
          comment_id,
          like_cnt,
          reply_cnt,
          opinion_tag,
          sentiment_tag,
          persona_tag,
          stage_tag,
          mindset_tag
        from data_asset.dwd_comment
        """,
        engine,
    )
    rel_df = pd.read_sql("select event_id, content_id from data_asset.rel_event_content", engine)
    if comment_df.empty:
        result = pd.DataFrame(
            columns=[
                "content_id",
                "comment_cnt",
                "event_id",
                "high_confidence_rate",
                "owner_rate",
                "test_drive_rate",
                "prospect_rate",
                "doubt_rate",
                "approval_rate",
                "positive_rate",
                "negative_rate",
                "stage_top1",
                "attitude_top1",
                "mindset_distribution_json",
                "emotion_distribution_json",
                "attitude_distribution_json",
                "stage_distribution_json",
                "updated_time",
            ]
        )
        write_refresh_table(engine, "fact_content_comment_profile_di", result)
        return {"processed_rows": 0, "output_rows": 0, "message": "无评论数据可计算"}

    def rate(series: pd.Series, value: str) -> float:
        return round(float((series.fillna("") == value).mean() * 100), 2)

    def distribution(series: pd.Series) -> str:
        cleaned = series.fillna("未知")
        dist = (
            cleaned.value_counts(normalize=True)
            .mul(100)
            .round(2)
            .reset_index()
        )
        dist.columns = ["label", "value"]
        return json.dumps(dist.to_dict(orient="records"), ensure_ascii=False)

    event_map = (
        rel_df.dropna(subset=["event_id", "content_id"])
        .drop_duplicates(subset=["content_id"])
        .set_index("content_id")["event_id"]
        .to_dict()
    )

    records = []
    for content_id, group in comment_df.groupby("content_id"):
        stage_mode = group["stage_tag"].fillna("未知").mode()
        opinion_mode = group["opinion_tag"].fillna("未知").mode()
        high_confidence_rate = round(
            float(((group["like_cnt"].fillna(0) + group["reply_cnt"].fillna(0)) >= 5).mean() * 100),
            2,
        )
        records.append(
            {
                "content_id": content_id,
                "event_id": event_map.get(content_id),
                "comment_cnt": int(group["comment_id"].count()),
                "high_confidence_rate": high_confidence_rate,
                "owner_rate": rate(group["stage_tag"], "车主"),
                "test_drive_rate": rate(group["stage_tag"], "试驾"),
                "prospect_rate": rate(group["stage_tag"], "准车主"),
                "doubt_rate": rate(group["opinion_tag"], "质疑"),
                "approval_rate": rate(group["opinion_tag"], "认可"),
                "positive_rate": rate(group["sentiment_tag"], "积极"),
                "negative_rate": round(
                    float(group["sentiment_tag"].fillna("").isin(NEGATIVE_SENTIMENTS).mean() * 100),
                    2,
                ),
                "stage_top1": None if stage_mode.empty else stage_mode.iloc[0],
                "attitude_top1": None if opinion_mode.empty else opinion_mode.iloc[0],
                "mindset_distribution_json": distribution(group["mindset_tag"]),
                "emotion_distribution_json": distribution(group["sentiment_tag"]),
                "attitude_distribution_json": distribution(group["opinion_tag"]),
                "stage_distribution_json": distribution(group["stage_tag"]),
                "updated_time": pd.Timestamp.now(),
            }
        )
    result = pd.DataFrame(records)
    write_refresh_table(engine, "fact_content_comment_profile_di", result)
    return {"processed_rows": len(comment_df), "output_rows": len(result), "message": "内容评论结构计算完成"}
