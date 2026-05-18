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
               content_type, published_at, engagement_total, comment_cnt, title
        from data_asset.dwd_content
        """,
        engine,
    )
    account_df = pd.read_sql(
        """
        select distinct on (account_id)
          account_id as author_id, avatar_url, account_type, domain_tag, persona_tag, stage_tag
        from data_asset.dwd_account
        order by account_id, snapshot_date desc
        """,
        engine,
    )
    rel_df = pd.read_sql("select event_id, content_id from data_asset.rel_event_content", engine)
    profile_df = pd.read_sql(
        """
        select content_id, high_confidence_rate, owner_rate, test_drive_rate, prospect_rate,
               doubt_rate, approval_rate, positive_rate, negative_rate,
               stage_top1, attitude_top1
        from data_asset.fact_content_comment_profile_di
        """,
        engine,
    )
    value_df = pd.read_sql(
        """
        select content_id, value_level, value_flags_json, content_role
        from data_asset.ads_content_value_summary
        """,
        engine,
    )
    comment_df = pd.read_sql(
        """
        select content_id, comment_text, opinion_tag, intention_tag, sentiment_tag
        from data_asset.dwd_comment
        """,
        engine,
    )

    merged = (
        rel_df.merge(content_df, on="content_id", how="left")
        .merge(account_df, on="author_id", how="left")
        .merge(profile_df, on="content_id", how="left")
        .merge(value_df, on="content_id", how="left")
    )
    merged["total_engagement_proxy"] = merged["engagement_total"].fillna(0)
    event_comments = rel_df.merge(comment_df, on="content_id", how="left")

    records = []
    for (event_id, author_id), group in merged.groupby(["event_id", "author_id"]):
        author_comments = event_comments[event_comments["content_id"].isin(group["content_id"].dropna().unique())]
        top_content_types = _top_values(group["content_type"])
        proposition_top = _top_values(author_comments["intention_tag"])
        issue_top = _top_values(author_comments["opinion_tag"])

        stage_from_account = str(group["stage_tag"].dropna().iloc[0]) if group["stage_tag"].notna().any() else ""
        owner_rate = float(group["owner_rate"].fillna(0).mean())
        test_drive_rate = float(group["test_drive_rate"].fillna(0).mean())
        prospect_rate = float(group["prospect_rate"].fillna(0).mean())
        if stage_from_account:
            stage_tag = stage_from_account
            stage_confidence = 0.9
            stage_reason = "账号表已提供用户阶段标签，优先采用导入值。"
        else:
            stage_candidates = {
                "车主": owner_rate,
                "试驾": test_drive_rate,
                "准车主": prospect_rate,
            }
            stage_tag = max(stage_candidates, key=stage_candidates.get) if stage_candidates else "未知"
            stage_confidence = round(max(stage_candidates.values(), default=0) / 100, 4)
            stage_reason = "根据作者内容下评论的用户阶段分布推断作者阶段。"

        evidence_strength = round(
            min(100.0, group["high_confidence_rate"].fillna(0).mean() * 0.6 + owner_rate * 0.4),
            2,
        )
        controversy_score = round(
            min(100.0, group["negative_rate"].fillna(0).mean() * 0.6 + group["doubt_rate"].fillna(0).mean() * 0.4),
            2,
        )
        evidence_type = "亲历" if stage_tag == "车主" else "试驾" if stage_tag == "试驾" else "视频" if "视频" in top_content_types else "转述"
        reproducible_flag = bool(stage_tag in {"车主", "试驾"} or evidence_strength >= 75)

        flags = set()
        for raw in group["value_flags_json"].dropna():
            try:
                for item in json.loads(raw):
                    flags.add(str(item))
            except Exception:
                continue
        role_tags = []
        if evidence_strength >= 80:
            role_tags.append("高证据作者")
        if group["total_engagement_proxy"].sum() >= 8000:
            role_tags.append("高互动作者")
        if controversy_score >= 40:
            role_tags.append("高争议作者")
        if stage_confidence >= 0.85:
            role_tags.append("高置信作者")
        if stage_tag == "车主":
            role_tags.append("真实车主样本")
        if not role_tags and group["persona_tag"].notna().any():
            role_tags.append(str(group["persona_tag"].dropna().iloc[0]))

        timeline_rows = (
            group.sort_values("published_at", ascending=False)
            .head(5)[["title", "published_at", "content_type", "engagement_total", "comment_cnt"]]
        )
        timeline = [
            {
                "title": str(item["title"] or ""),
                "publishedAt": pd.Timestamp(item["published_at"]).strftime("%Y-%m-%d %H:%M:%S") if pd.notna(item["published_at"]) else "",
                "contentType": str(item["content_type"] or ""),
                "engagement": int(item["engagement_total"] or 0),
                "comments": int(item["comment_cnt"] or 0),
                "propositionTag": proposition_top[0] if proposition_top else "",
                "issueTag": issue_top[0] if issue_top else "",
            }
            for _, item in timeline_rows.iterrows()
        ]

        rep_contents = group.sort_values("engagement_total", ascending=False)["title"].dropna().astype(str).head(3).tolist()
        rep_comments = author_comments.sort_values(
            by="sentiment_tag",
            key=lambda s: s.fillna("").isin(NEGATIVE_SENTIMENTS).astype(int),
            ascending=False,
        )["comment_text"].dropna().astype(str).head(3).tolist()

        ai_summary = "该作者在本事件中"
        if evidence_strength >= 80:
            ai_summary += "证据强度高，"
        elif controversy_score >= 40:
            ai_summary += "争议带动明显，"
        else:
            ai_summary += "具备稳定发声能力，"
        ai_summary += "适合作为事件分析的重点主体样本。"

        records.append(
            {
                "event_id": event_id,
                "author_id": author_id,
                "nickname": str(group["author_name"].dropna().iloc[0]) if group["author_name"].notna().any() else "",
                "platform": str(group["platform"].dropna().iloc[0]) if group["platform"].notna().any() else "",
                "author_type": str(group["author_type"].dropna().iloc[0]) if group["author_type"].notna().any() else "",
                "is_kol": bool(group["is_kol"].fillna(False).max()),
                "stage_tag": stage_tag,
                "stage_confidence": stage_confidence,
                "stage_reason": stage_reason,
                "posts": int(group["content_id"].nunique()),
                "total_engagement": int(group["total_engagement_proxy"].sum()),
                "comment_trigger_cnt": int(group["comment_cnt"].fillna(0).sum()),
                "top_content_types_json": _json_list(top_content_types),
                "proposition_top_json": _json_list(proposition_top),
                "issue_top_json": _json_list(issue_top),
                "evidence_strength": evidence_strength,
                "evidence_type": evidence_type,
                "reproducible_flag": reproducible_flag,
                "controversy_score": controversy_score,
                "high_value_flag": "核心内容" in flags or "高证据" in flags,
                "high_controversy_flag": controversy_score >= 40,
                "high_confidence_flag": stage_confidence >= 0.85,
                "role_tags_json": _json_list(role_tags),
                "ai_summary": ai_summary,
                "content_timeline_json": json.dumps(timeline, ensure_ascii=False),
                "representative_contents_json": _json_list(rep_contents),
                "representative_comments_json": _json_list(rep_comments),
                "updated_time": pd.Timestamp.now(),
            }
        )

    result = pd.DataFrame(records)
    if result.empty:
        result = pd.DataFrame(
            columns=[
                "event_id", "author_id", "nickname", "platform", "author_type", "is_kol", "stage_tag",
                "stage_confidence", "stage_reason", "posts", "total_engagement", "comment_trigger_cnt",
                "top_content_types_json", "proposition_top_json", "issue_top_json", "evidence_strength",
                "evidence_type", "reproducible_flag", "controversy_score", "high_value_flag",
                "high_controversy_flag", "high_confidence_flag", "role_tags_json", "ai_summary",
                "content_timeline_json", "representative_contents_json", "representative_comments_json", "updated_time",
            ]
        )
    write_refresh_table(engine, "ads_author_event_summary", result)
    return {"processed_rows": len(merged), "output_rows": len(result), "message": "作者事件汇总计算完成"}
