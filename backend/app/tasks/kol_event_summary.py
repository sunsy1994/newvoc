import json

import pandas as pd

from ._event_asset_utils import NEGATIVE_SENTIMENTS, write_refresh_table


def _json_list(values) -> str:
    return json.dumps(list(values), ensure_ascii=False)


def _top_values(series: pd.Series, limit: int = 3) -> list[str]:
    cleaned = series.fillna("").astype(str).str.strip()
    cleaned = cleaned[cleaned != ""]
    if cleaned.empty:
        return []
    return cleaned.value_counts().head(limit).index.tolist()


def run(engine, params: dict) -> dict:
    content_df = pd.read_sql(
        """
        select content_id, author_id, author_name, platform, author_type, is_kol,
               fans_cnt, comment_cnt, engagement_total
        from data_asset.dwd_content
        """,
        engine,
    )
    account_df = pd.read_sql(
        """
        select distinct on (account_id)
          account_id, avatar_url, domain_tag, fans_cnt
        from data_asset.dwd_account
        order by account_id, snapshot_date desc
        """,
        engine,
    )
    profile_df = pd.read_sql(
        """
        select content_id, high_confidence_rate, negative_rate
        from data_asset.fact_content_comment_profile_di
        """,
        engine,
    )
    comment_df = pd.read_sql(
        """
        select content_id, comment_text, sentiment_tag, intention_tag, stage_tag, mindset_tag
        from data_asset.dwd_comment
        """,
        engine,
    )
    rel_df = pd.read_sql("select event_id, content_id from data_asset.rel_event_content", engine)

    merged = rel_df.merge(content_df, on="content_id", how="left")
    merged = merged[merged["is_kol"] == True]  # noqa: E712
    merged = merged.merge(account_df, left_on="author_id", right_on="account_id", how="left", suffixes=("", "_account"))
    merged = merged.merge(profile_df, on="content_id", how="left")
    event_comments = rel_df.merge(comment_df, on="content_id", how="left")

    records = []
    for (event_id, author_id), group in merged.groupby(["event_id", "author_id"]):
        comment_scope = event_comments[event_comments["content_id"].isin(group["content_id"].dropna().unique())]
        total_comments = int(group["comment_cnt"].fillna(0).sum())
        total_engagement = float(group["engagement_total"].fillna(0).sum())
        event_posts = int(group["content_id"].nunique())
        fans = int(group["fans_cnt_account"].fillna(group["fans_cnt"]).max() or 0)
        avg_engagement = round(total_engagement / max(event_posts, 1), 2)
        high_conf_ratio = round(group["high_confidence_rate"].fillna(0).mean() / 100, 4)
        effective_engagement_rate = round(min(1.0, total_engagement / max(total_comments * 20, 1)), 4)
        risk_score = round(group["negative_rate"].fillna(0).mean() / 100, 4)

        role_tags = []
        if avg_engagement >= 4000:
            role_tags.append("高互动型")
        if high_conf_ratio >= 0.4:
            role_tags.append("高证据型")
        if risk_score >= 0.45:
            role_tags.append("高争议型")
        if comment_scope["intention_tag"].fillna("").isin(["购买", "试驾"]).mean() >= 0.2:
            role_tags.append("高意向触发型")

        mindset_top = _top_values(comment_scope["mindset_tag"])
        stage_top = _top_values(comment_scope["stage_tag"])
        intention_top = _top_values(comment_scope["intention_tag"])

        rep_rows = comment_scope.assign(
            score=comment_scope["sentiment_tag"].fillna("").isin(NEGATIVE_SENTIMENTS).astype(int)
        ).head(3)
        rep_comments = []
        for _, item in rep_rows.iterrows():
            rep_type = "高点赞"
            if str(item.get("sentiment_tag", "")) in NEGATIVE_SENTIMENTS:
                rep_type = "高争议"
            elif str(item.get("intention_tag", "")) in {"购买", "试驾"}:
                rep_type = "高意向"
            rep_comments.append({"type": rep_type, "text": str(item.get("comment_text", "") or "")})

        summary = "该KOL在本事件中"
        if "高证据型" in role_tags:
            summary += "具备较强证据表达能力，"
        elif "高争议型" in role_tags:
            summary += "争议放大能力较强，"
        else:
            summary += "传播触达稳定，"
        summary += "适合作为重点传播节点观察。"

        records.append(
            {
                "event_id": event_id,
                "account_id": author_id,
                "nickname": str(group["author_name"].dropna().iloc[0]) if group["author_name"].notna().any() else "",
                "avatar_url": str(group["avatar_url"].dropna().iloc[0]) if group["avatar_url"].notna().any() else "",
                "platform": str(group["platform"].dropna().iloc[0]) if group["platform"].notna().any() else "",
                "fans_cnt": fans,
                "domain_tag": str(group["domain_tag"].dropna().iloc[0]) if group["domain_tag"].notna().any() else "",
                "author_type": str(group["author_type"].dropna().iloc[0]) if group["author_type"].notna().any() else "",
                "event_posts": event_posts,
                "total_engagement": int(total_engagement),
                "total_comments": total_comments,
                "avg_engagement": avg_engagement,
                "high_confidence_ratio": high_conf_ratio,
                "effective_engagement_rate": effective_engagement_rate,
                "risk_score": risk_score,
                "role_tags_json": _json_list(role_tags),
                "mindset_top_json": _json_list(mindset_top),
                "stage_top_json": _json_list(stage_top),
                "intention_top_json": _json_list(intention_top),
                "summary": summary,
                "representative_comments_json": json.dumps(rep_comments, ensure_ascii=False),
                "updated_time": pd.Timestamp.now(),
            }
        )

    result = pd.DataFrame(records)
    if result.empty:
        result = pd.DataFrame(
            columns=[
                "event_id", "account_id", "nickname", "avatar_url", "platform", "fans_cnt",
                "domain_tag", "author_type", "event_posts", "total_engagement", "total_comments",
                "avg_engagement", "high_confidence_ratio", "effective_engagement_rate", "risk_score",
                "role_tags_json", "mindset_top_json", "stage_top_json", "intention_top_json",
                "summary", "representative_comments_json", "updated_time",
            ]
        )
    write_refresh_table(engine, "ads_kol_event_summary", result)
    return {"processed_rows": len(merged), "output_rows": len(result), "message": "KOL事件汇总计算完成"}
