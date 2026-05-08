import hashlib

import pandas as pd
from sqlalchemy import text

from backend.app.journey_rules import infer_journey_stage
from ._event_asset_utils import write_refresh_table


TOUCHPOINT_COLUMNS = [
    "touchpoint_id",
    "source_channel",
    "source_system",
    "source_record_id",
    "channel_user_key",
    "user_display_name",
    "touchpoint_text",
    "touchpoint_time",
    "brand_name",
    "model_name",
    "city_name",
    "store_id",
    "store_name",
    "event_id",
    "content_id",
    "journey_stage",
    "stage_confidence",
    "stage_reason",
    "intent_tag",
    "issue_tag",
    "sentiment_tag",
    "mindset_tag",
    "business_status",
    "rating_score",
    "updated_time",
]


def _sha(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _text(row) -> str:
    return str(row.get("comment_text", "") or "")


def _build_public_touchpoints(comment_df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in comment_df.iterrows():
        inferred = infer_journey_stage(
            source_channel="public_social",
            text=_text(row),
            business_status=str(row.get("stage_tag", "") or ""),
            rating_score=None,
        )
        records.append(
            {
                "touchpoint_id": f"tp_public_{_sha(str(row.get('comment_id', '')))}",
                "source_channel": "public_social",
                "source_system": str(row.get("platform", "") or "public_social"),
                "source_record_id": str(row.get("comment_id", "") or ""),
                "channel_user_key": str(row.get("comment_author_id", "") or row.get("comment_author_name", "") or ""),
                "user_display_name": str(row.get("comment_author_name", "") or ""),
                "touchpoint_text": _text(row),
                "touchpoint_time": row.get("published_at"),
                "brand_name": row.get("brand_name"),
                "model_name": row.get("model_name"),
                "city_name": None,
                "store_id": None,
                "store_name": None,
                "event_id": row.get("event_id"),
                "content_id": row.get("content_id"),
                "journey_stage": inferred["stage"],
                "stage_confidence": inferred["confidence"],
                "stage_reason": inferred["reason"],
                "intent_tag": row.get("intention_tag"),
                "issue_tag": row.get("opinion_tag"),
                "sentiment_tag": row.get("sentiment_tag"),
                "mindset_tag": row.get("mindset_tag"),
                "business_status": row.get("stage_tag"),
                "rating_score": None,
                "updated_time": pd.Timestamp.now(),
            }
        )
    return pd.DataFrame(records, columns=TOUCHPOINT_COLUMNS)


def run(engine, params: dict) -> dict:
    comment_df = pd.read_sql(
        """
        SELECT
          cm.comment_id, cm.platform, cm.content_id, cm.comment_author_id, cm.comment_author_name,
          cm.comment_text, cm.published_at, cm.opinion_tag, cm.intention_tag,
          cm.sentiment_tag, cm.mindset_tag, cm.stage_tag,
          rel.event_id, ev.brand_name, ev.model_name
        FROM data_asset.dwd_comment cm
        LEFT JOIN data_asset.rel_event_content rel ON rel.content_id = cm.content_id
        LEFT JOIN data_asset.dwd_event ev ON ev.event_id = rel.event_id
        """,
        engine,
    )
    existing_df = pd.read_sql(
        """
        SELECT *
        FROM data_asset.dwd_customer_touchpoint
        WHERE source_channel <> 'public_social'
        """,
        engine,
    )

    public_df = _build_public_touchpoints(comment_df)
    result = pd.concat([existing_df, public_df], ignore_index=True, sort=False)
    result = result.drop_duplicates(subset=["touchpoint_id"], keep="last")

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM data_asset.dwd_customer_touchpoint"))
    write_refresh_table(engine, "dwd_customer_touchpoint", result)
    return {
        "processed_rows": int(len(comment_df) + len(existing_df)),
        "output_rows": int(len(result)),
        "message": "用户旅程触点标准化完成",
    }
