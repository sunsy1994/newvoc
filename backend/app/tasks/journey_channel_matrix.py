import hashlib
import json

import pandas as pd

from backend.app.journey_rules import NEGATIVE_SENTIMENTS
from ._event_asset_utils import write_refresh_table


MATRIX_COLUMNS = [
    "matrix_id",
    "brand_name",
    "model_name",
    "source_channel",
    "journey_stage",
    "date_from",
    "date_to",
    "touchpoint_cnt",
    "negative_ratio",
    "issue_top_json",
    "intent_top_json",
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


def _build_channel_matrix(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    if not df.empty:
        df = df.copy()
        df["touchpoint_time"] = pd.to_datetime(df["touchpoint_time"], errors="coerce")
        df["negative_flag"] = df["sentiment_tag"].fillna("").isin(NEGATIVE_SENTIMENTS).astype(int)
        for (brand, model, channel, stage), group in df.groupby(
            ["brand_name", "model_name", "source_channel", "journey_stage"],
            dropna=False,
        ):
            date_from = group["touchpoint_time"].min().date()
            date_to = group["touchpoint_time"].max().date()
            touchpoint_cnt = int(group["touchpoint_id"].nunique())
            negative_cnt = int(group["negative_flag"].sum())
            records.append(
                {
                    "matrix_id": f"matrix_{_sha(str(brand) + str(model) + str(channel) + str(stage))}",
                    "brand_name": brand,
                    "model_name": model,
                    "source_channel": channel,
                    "journey_stage": stage,
                    "date_from": date_from,
                    "date_to": date_to,
                    "touchpoint_cnt": touchpoint_cnt,
                    "negative_ratio": round(negative_cnt / touchpoint_cnt, 4) if touchpoint_cnt else 0,
                    "issue_top_json": _top_json(group["issue_tag"]),
                    "intent_top_json": _top_json(group["intent_tag"]),
                    "data_lineage_json": json.dumps(["dwd_customer_touchpoint"], ensure_ascii=False),
                    "updated_time": pd.Timestamp.now(),
                }
            )
    return pd.DataFrame(records, columns=MATRIX_COLUMNS)


def run(engine, params: dict) -> dict:
    df = pd.read_sql("SELECT * FROM data_asset.dwd_customer_touchpoint", engine)
    result = _build_channel_matrix(df)
    write_refresh_table(engine, "ads_journey_channel_matrix", result)
    return {
        "processed_rows": int(len(df)),
        "output_rows": int(len(result)),
        "message": "旅程渠道矩阵汇总完成",
    }
