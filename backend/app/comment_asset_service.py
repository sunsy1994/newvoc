import pandas as pd

from .database import engine
from .schemas import CommentAssetItem, CommentAssetListResponse


class CommentAssetError(Exception):
    pass


def _ensure_engine():
    if engine is None:
        raise CommentAssetError("DATABASE_URL not configured")
    return engine


def _confidence(like_count: int, reply_count: int) -> float:
    score = min(1.0, 0.6 + (like_count + reply_count * 2) / 1000)
    return round(score, 2)


def list_comment_assets(event_id: str | None = None) -> CommentAssetListResponse:
    db_engine = _ensure_engine()
    query = """
        SELECT
          cm.comment_id, rel.event_id, cm.content_id, c.title as content_title, c.author_name as content_author,
          c.author_type as content_author_type, c.is_kol as from_kol_content, cm.comment_text, cm.platform,
          cm.published_at, cm.comment_author_id, cm.comment_author_name, cm.like_cnt, cm.reply_cnt,
          cm.interaction_cnt, cm.reply_level, cm.source_url, cm.mindset_tag, cm.stage_tag,
          cm.intention_tag, cm.opinion_tag, cm.persona_tag, cm.sentiment_tag
        FROM data_asset.dwd_comment cm
        LEFT JOIN data_asset.dwd_content c ON c.content_id = cm.content_id
        LEFT JOIN data_asset.rel_event_content rel ON rel.content_id = cm.content_id
    """
    df = pd.read_sql(query, db_engine)
    if event_id:
        df = df[df["event_id"] == event_id]
    df = df.sort_values(["interaction_cnt", "published_at"], ascending=[False, False], na_position="last")

    items = []
    for _, row in df.iterrows():
        same_scope = df[
            (df["content_id"] == row["content_id"])
            & (df["comment_id"] != row["comment_id"])
            & (df["mindset_tag"].fillna("") == str(row.get("mindset_tag", "") or ""))
        ]["comment_text"].dropna().astype(str).head(2).tolist()
        labeling_reason = "标签来自导入评论字段"
        if row.get("mindset_tag"):
            labeling_reason += f"，心智标签为“{row['mindset_tag']}”"
        if row.get("stage_tag"):
            labeling_reason += f"，阶段标签为“{row['stage_tag']}”"

        items.append(
            CommentAssetItem(
                id=str(row["comment_id"]),
                event_id=row.get("event_id"),
                content_id=str(row["content_id"]),
                content_title=str(row.get("content_title", "") or ""),
                content_author=str(row.get("content_author", "") or ""),
                content_author_type=str(row.get("content_author_type", "") or ""),
                from_kol_content=bool(row.get("from_kol_content", False)),
                text=str(row.get("comment_text", "") or ""),
                platform=str(row.get("platform", "") or ""),
                published_at=pd.Timestamp(row["published_at"]).strftime("%Y-%m-%d %H:%M:%S") if pd.notna(row.get("published_at")) else None,
                comment_author_id=row.get("comment_author_id"),
                comment_author_name=str(row.get("comment_author_name", "") or ""),
                like_count=int(row.get("like_cnt", 0) or 0),
                interaction_count=int(row.get("interaction_cnt", 0) or 0),
                reply_level=int(row.get("reply_level", 0) or 0),
                source_url=str(row.get("source_url", "") or ""),
                mindset_tag=str(row.get("mindset_tag", "") or ""),
                stage_tag=str(row.get("stage_tag", "") or ""),
                proposition_tag=str(row.get("intention_tag", "") or ""),
                issue_tag=str(row.get("opinion_tag", "") or ""),
                evidence_tag=str(row.get("persona_tag", "") or ""),
                sentiment_tag=str(row.get("sentiment_tag", "") or ""),
                confidence=_confidence(int(row.get("like_cnt", 0) or 0), int(row.get("reply_cnt", 0) or 0)),
                labeling_reason=labeling_reason,
                similar_comments=same_scope,
            )
        )
    return CommentAssetListResponse(total=len(items), items=items)
