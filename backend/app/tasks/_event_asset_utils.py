import json

import pandas as pd
from sqlalchemy import inspect, text


NEGATIVE_SENTIMENTS = {"负向", "强负面", "负面", "消极"}


def normalize_event_status(end_time, raw_status) -> str:
    if raw_status:
        text_value = str(raw_status).strip()
        if text_value:
            return text_value
    if pd.notna(end_time) and pd.Timestamp(end_time) < pd.Timestamp.now():
        return "已结束"
    return "进行中"


def build_topic_top_json(comment_df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for column in ("opinion_tag", "intention_tag"):
        if column not in comment_df.columns:
            continue
        part = comment_df[["event_id", column]].rename(columns={column: "tag_value"})
        part["tag_value"] = part["tag_value"].fillna("").astype(str).str.strip()
        part = part[part["tag_value"] != ""]
        if not part.empty:
            frames.append(part)

    if not frames:
        return pd.DataFrame(columns=["event_id", "topic_top_json"])

    merged = pd.concat(frames, ignore_index=True)
    grouped = (
        merged.groupby(["event_id", "tag_value"], as_index=False)
        .size()
        .sort_values(["event_id", "size", "tag_value"], ascending=[True, False, True])
    )
    top = (
        grouped.groupby("event_id")
        .head(3)
        .groupby("event_id")["tag_value"]
        .apply(lambda values: json.dumps(list(values), ensure_ascii=False))
        .reset_index(name="topic_top_json")
    )
    return top


def write_refresh_table(engine, table_name: str, dataframe: pd.DataFrame) -> None:
    inspector = inspect(engine)
    table_exists = inspector.has_table(table_name, schema="data_asset")
    with engine.begin() as conn:
        if table_exists:
            conn.execute(text(f"DELETE FROM data_asset.{table_name}"))
        dataframe.to_sql(
            table_name,
            conn,
            schema="data_asset",
            if_exists="append",
            index=False,
            method="multi",
        )
