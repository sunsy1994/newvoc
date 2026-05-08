import hashlib
import json

import pandas as pd

from backend.app.journey_rules import NEGATIVE_SENTIMENTS, suggest_owner_and_action
from ._event_asset_utils import write_refresh_table


PAINPOINT_COLUMNS = [
    "painpoint_id",
    "brand_name",
    "model_name",
    "journey_stage",
    "issue_tag",
    "touchpoint_cnt",
    "negative_ratio",
    "source_channels_json",
    "sample_texts_json",
    "suggested_owner",
    "suggested_action",
    "data_lineage_json",
    "updated_time",
]


def _sha(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]


def _top_json(series: pd.Series, limit: int = 5) -> str:
    cleaned = series.fillna("").astype(str).str.strip()
    cleaned = cleaned[cleaned != ""]
    if cleaned.empty:
        return "[]"
    rows = cleaned.value_counts().head(limit).reset_index()
    rows.columns = ["label", "value"]
    return json.dumps(rows.to_dict(orient="records"), ensure_ascii=False)


def _sample_json(group: pd.DataFrame, limit: int = 3) -> str:
    rows = group.sort_values("touchpoint_time", ascending=False).head(limit)
    return json.dumps(
        [
            {
                "touchpointId": str(row["touchpoint_id"]),
                "channel": str(row["source_channel"]),
                "text": str(row["touchpoint_text"]),
                "time": str(row["touchpoint_time"]),
            }
            for _, row in rows.iterrows()
        ],
        ensure_ascii=False,
    )


def _build_painpoint_summary(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    if not df.empty:
        df = df.copy()
        df["touchpoint_time"] = pd.to_datetime(df["touchpoint_time"], errors="coerce")
        df["issue_tag"] = df["issue_tag"].fillna("未标注问题").replace("", "未标注问题")
        df["negative_flag"] = df["sentiment_tag"].fillna("").isin(NEGATIVE_SENTIMENTS).astype(int)
        for (brand, model, stage, issue), group in df.groupby(
            ["brand_name", "model_name", "journey_stage", "issue_tag"],
            dropna=False,
        ):
            touchpoint_cnt = int(group["touchpoint_id"].nunique())
            negative_cnt = int(group["negative_flag"].sum())
            suggestion = suggest_owner_and_action(
                journey_stage=str(stage),
                issue_tag=str(issue),
                sentiment_tag="负向" if negative_cnt else "",
            )
            records.append(
                {
                    "painpoint_id": f"pain_{_sha(str(brand) + str(model) + str(stage) + str(issue))}",
                    "brand_name": brand,
                    "model_name": model,
                    "journey_stage": stage,
                    "issue_tag": issue,
                    "touchpoint_cnt": touchpoint_cnt,
                    "negative_ratio": round(negative_cnt / touchpoint_cnt, 4) if touchpoint_cnt else 0,
                    "source_channels_json": _top_json(group["source_channel"]),
                    "sample_texts_json": _sample_json(group),
                    "suggested_owner": suggestion["owner"],
                    "suggested_action": suggestion["action"],
                    "data_lineage_json": json.dumps(["dwd_customer_touchpoint", "journey_rules"], ensure_ascii=False),
                    "updated_time": pd.Timestamp.now(),
                }
            )
    return pd.DataFrame(records, columns=PAINPOINT_COLUMNS)


def run(engine, params: dict) -> dict:
    df = pd.read_sql("SELECT * FROM data_asset.dwd_customer_touchpoint", engine)
    result = _build_painpoint_summary(df)
    write_refresh_table(engine, "ads_journey_painpoint_summary", result)
    return {
        "processed_rows": int(len(df)),
        "output_rows": int(len(result)),
        "message": "旅程痛点汇总完成",
    }
