import json

import pandas as pd

from ._event_asset_utils import NEGATIVE_SENTIMENTS, write_refresh_table


def _json_list(items: list[str]) -> str:
    return json.dumps(items, ensure_ascii=False)


def _value_level(score: int) -> str:
    if score >= 4:
        return "高"
    if score >= 2:
        return "中"
    return "低"


def _content_role(content_type: str, media_form: str, engagement_total: float) -> str:
    if content_type in {"测评", "对比"}:
        return "证据型"
    if content_type == "提车作业":
        return "体验型"
    if media_form in {"视频", "直播切片"} and engagement_total >= 3000:
        return "传播型"
    return "信息型"


def run(engine, params: dict) -> dict:
    rel_df = pd.read_sql("select event_id, content_id from data_asset.rel_event_content", engine)
    content_df = pd.read_sql(
        """
        select
          content_id, platform, source_url, author_id, author_name, author_type,
          is_kol, kol_domain, fans_cnt, title, content_text, content_type, media_form,
          published_at, like_cnt, comment_cnt, share_cnt, favorite_cnt, view_cnt, engagement_total
        from data_asset.dwd_content
        """,
        engine,
    )
    profile_df = pd.read_sql(
        """
        select
          content_id, event_id, comment_cnt, high_confidence_rate, owner_rate, test_drive_rate,
          prospect_rate, doubt_rate, approval_rate, positive_rate, negative_rate,
          stage_top1, attitude_top1
        from data_asset.fact_content_comment_profile_di
        """,
        engine,
    )
    comment_df = pd.read_sql(
        """
        select content_id, comment_id, comment_text, like_cnt, reply_cnt, sentiment_tag
        from data_asset.dwd_comment
        """,
        engine,
    )

    event_map = (
        rel_df.dropna(subset=["event_id", "content_id"])
        .drop_duplicates(subset=["content_id"])
        .rename(columns={"event_id": "mapped_event_id"})
    )

    merged = (
        content_df.merge(event_map, on="content_id", how="left")
        .merge(profile_df, on="content_id", how="left", suffixes=("", "_profile"))
    )
    merged["event_id"] = merged["event_id"].fillna(merged["mapped_event_id"])

    grouped_comments = {}
    for content_id, group in comment_df.groupby("content_id"):
        sorted_group = group.assign(
            comment_score=group["like_cnt"].fillna(0) + group["reply_cnt"].fillna(0) * 2
        ).sort_values(["comment_score", "like_cnt"], ascending=False)
        grouped_comments[content_id] = sorted_group.head(3)

    if merged.empty:
        result = pd.DataFrame(
            columns=[
                "content_id",
                "event_id",
                "content_role",
                "value_level",
                "value_flags_json",
                "value_summary",
                "value_reason_json",
                "is_core_content",
                "tag_confidence",
                "representative_comments_json",
                "updated_time",
            ]
        )
        write_refresh_table(engine, "ads_content_value_summary", result)
        return {"processed_rows": 0, "output_rows": 0, "message": "无内容数据可计算"}

    event_quantile = (
        merged.groupby("event_id")["engagement_total"]
        .quantile(0.8)
        .to_dict()
    )

    records = []
    for _, row in merged.iterrows():
        flags: list[str] = []
        reasons: list[str] = []

        engagement_total = float(row.get("engagement_total", 0) or 0)
        comment_cnt = int(row.get("comment_cnt_profile", row.get("comment_cnt", 0)) or 0)
        negative_rate = float(row.get("negative_rate", 0) or 0)
        high_confidence_rate = float(row.get("high_confidence_rate", 0) or 0)
        owner_rate = float(row.get("owner_rate", 0) or 0)
        prospect_rate = float(row.get("prospect_rate", 0) or 0)

        if engagement_total >= 5000:
            flags.append("高互动")
            reasons.append("综合互动量高，具备传播放大价值")
        if high_confidence_rate >= 60 or owner_rate >= 30:
            flags.append("高证据")
            reasons.append("评论中高置信或车主样本占比高，具备证据价值")
        if negative_rate >= 35 or float(row.get("doubt_rate", 0) or 0) >= 35:
            flags.append("高争议")
            reasons.append("负向或质疑评论占比较高，具备争议识别价值")
        if prospect_rate >= 25 or float(row.get("approval_rate", 0) or 0) >= 45:
            flags.append("高意向")
            reasons.append("准车主或认可评论占比高，具备转化参考价值")

        threshold = event_quantile.get(row.get("event_id"), None)
        is_core_content = bool(threshold is not None and engagement_total >= threshold and engagement_total > 0)
        if is_core_content:
            flags.append("核心内容")
            reasons.append("在所属事件中处于高互动分位，属于核心承载内容")

        score = len(flags)
        value_level = _value_level(score)
        content_role = _content_role(
            str(row.get("content_type", "") or ""),
            str(row.get("media_form", "") or ""),
            engagement_total,
        )
        tag_confidence = round(min(1.0, max(high_confidence_rate / 100, 0.5 if score >= 2 else 0.3)), 4)

        rep_comments = []
        top_comments = grouped_comments.get(row["content_id"])
        if top_comments is not None:
            for _, comment in top_comments.iterrows():
                label = "代表评论"
                if str(comment.get("sentiment_tag", "")) in NEGATIVE_SENTIMENTS:
                    label = "负向代表评论"
                rep_comments.append(
                    {
                        "label": label,
                        "text": str(comment.get("comment_text", "") or ""),
                    }
                )

        if value_level == "高":
            value_summary = "该内容同时承担传播与判断价值，适合作为内容库重点样本。"
        elif value_level == "中":
            value_summary = "该内容具备一定参考价值，适合作为事件理解的辅助样本。"
        else:
            value_summary = "该内容更适合作为补充信息，不建议作为核心判断依据。"

        records.append(
            {
                "content_id": row["content_id"],
                "event_id": row.get("event_id"),
                "content_role": content_role,
                "value_level": value_level,
                "value_flags_json": _json_list(flags),
                "value_summary": value_summary,
                "value_reason_json": json.dumps(reasons, ensure_ascii=False),
                "is_core_content": is_core_content,
                "tag_confidence": tag_confidence,
                "representative_comments_json": json.dumps(rep_comments, ensure_ascii=False),
                "updated_time": pd.Timestamp.now(),
            }
        )

    result = pd.DataFrame(records)
    write_refresh_table(engine, "ads_content_value_summary", result)
    return {
        "processed_rows": int(len(merged)),
        "output_rows": int(len(result)),
        "message": "内容价值汇总计算完成",
    }
