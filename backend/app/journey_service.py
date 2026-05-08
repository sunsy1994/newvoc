import json

import pandas as pd
from sqlalchemy import text

from .database import engine
from .schemas import (
    DataLineage,
    JourneyMatrixCell,
    JourneyOverviewResponse,
    JourneyPainpointItem,
    JourneyStageSummaryItem,
    JourneyTouchpointItem,
    JourneyTouchpointListResponse,
)


class JourneyError(Exception):
    pass


def _ensure_engine():
    if engine is None:
        raise JourneyError("DATABASE_URL not configured")
    return engine


def _json_list(value) -> list:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, list) else []
        except json.JSONDecodeError:
            return []
    return []


def _lineage(tables: list[str], formula: str) -> DataLineage:
    return DataLineage(tables=tables, formula=formula)


def _format_time(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return pd.Timestamp(value).strftime("%Y-%m-%d %H:%M:%S")


def _row_to_stage(row: pd.Series) -> JourneyStageSummaryItem:
    return JourneyStageSummaryItem(
        stage=str(row.get("journey_stage", "") or ""),
        touchpoint_count=int(row.get("touchpoint_cnt", 0) or 0),
        channel_count=int(row.get("channel_cnt", 0) or 0),
        negative_ratio=round(float(row.get("negative_ratio", 0) or 0), 4),
        intent_top=_json_list(row.get("intent_top_json")),
        issue_top=_json_list(row.get("issue_top_json")),
        channel_distribution=_json_list(row.get("channel_distribution_json")),
        representative_touchpoints=_json_list(row.get("representative_touchpoints_json")),
        data_lineage=_lineage(
            ["ads_journey_stage_summary"],
            "按 journey_stage 聚合 dwd_customer_touchpoint 的触点数、渠道数、负向占比和标签 TopN。",
        ),
    )


def _row_to_matrix(row: pd.Series) -> JourneyMatrixCell:
    return JourneyMatrixCell(
        source_channel=str(row.get("source_channel", "") or ""),
        journey_stage=str(row.get("journey_stage", "") or ""),
        touchpoint_count=int(row.get("touchpoint_cnt", 0) or 0),
        negative_ratio=round(float(row.get("negative_ratio", 0) or 0), 4),
        issue_top=_json_list(row.get("issue_top_json")),
        intent_top=_json_list(row.get("intent_top_json")),
        data_lineage=_lineage(
            ["ads_journey_channel_matrix"],
            "按 source_channel + journey_stage 聚合 dwd_customer_touchpoint。",
        ),
    )


def _row_to_touchpoint(row: pd.Series) -> JourneyTouchpointItem:
    return JourneyTouchpointItem(
        id=str(row.get("touchpoint_id", "") or ""),
        source_channel=str(row.get("source_channel", "") or ""),
        source_system=str(row.get("source_system", "") or ""),
        user_display_name=str(row.get("user_display_name", "") or ""),
        text=str(row.get("touchpoint_text", "") or ""),
        touchpoint_time=_format_time(row.get("touchpoint_time")),
        brand_name=str(row.get("brand_name", "") or ""),
        model_name=str(row.get("model_name", "") or ""),
        city_name=str(row.get("city_name", "") or ""),
        store_name=str(row.get("store_name", "") or ""),
        journey_stage=str(row.get("journey_stage", "") or ""),
        stage_reason=str(row.get("stage_reason", "") or ""),
        intent_tag=str(row.get("intent_tag", "") or ""),
        issue_tag=str(row.get("issue_tag", "") or ""),
        sentiment_tag=str(row.get("sentiment_tag", "") or ""),
    )


def _row_to_painpoint(row: pd.Series) -> JourneyPainpointItem:
    return JourneyPainpointItem(
        journey_stage=str(row.get("journey_stage", "") or ""),
        issue_tag=str(row.get("issue_tag", "") or ""),
        touchpoint_count=int(row.get("touchpoint_cnt", 0) or 0),
        negative_ratio=round(float(row.get("negative_ratio", 0) or 0), 4),
        source_channels=_json_list(row.get("source_channels_json")),
        sample_texts=_json_list(row.get("sample_texts_json")),
        suggested_owner=str(row.get("suggested_owner", "") or ""),
        suggested_action=str(row.get("suggested_action", "") or ""),
        data_lineage=_lineage(
            ["ads_journey_painpoint_summary", "journey_rules"],
            "按 journey_stage + issue_tag 聚合触点，并基于规则生成负责人和动作建议。",
        ),
    )


def _filter_frame(df: pd.DataFrame, *, brand_name: str | None, model_name: str | None) -> pd.DataFrame:
    if brand_name:
        df = df[df["brand_name"] == brand_name]
    if model_name:
        df = df[df["model_name"] == model_name]
    return df


def get_journey_overview(
    *,
    brand_name: str | None = None,
    model_name: str | None = None,
) -> JourneyOverviewResponse:
    db_engine = _ensure_engine()
    df = pd.read_sql("SELECT * FROM data_asset.ads_journey_stage_summary", db_engine)
    df = _filter_frame(df, brand_name=brand_name, model_name=model_name)
    df = df.sort_values(["touchpoint_cnt", "journey_stage"], ascending=[False, True]) if not df.empty else df
    return JourneyOverviewResponse(
        brand_name=brand_name or "",
        model_name=model_name or "",
        stages=[_row_to_stage(row) for _, row in df.iterrows()],
        data_lineage=_lineage(
            ["ads_journey_stage_summary"],
            "仅展示 ETL 产出的旅程阶段汇总；无数据则返回空数组。",
        ),
    )


def get_journey_matrix(
    *,
    brand_name: str | None = None,
    model_name: str | None = None,
) -> list[JourneyMatrixCell]:
    db_engine = _ensure_engine()
    df = pd.read_sql("SELECT * FROM data_asset.ads_journey_channel_matrix", db_engine)
    df = _filter_frame(df, brand_name=brand_name, model_name=model_name)
    return [_row_to_matrix(row) for _, row in df.iterrows()]


def list_journey_touchpoints(
    *,
    stage: str | None = None,
    channel: str | None = None,
    brand_name: str | None = None,
    model_name: str | None = None,
    page: int = 1,
    page_size: int = 50,
) -> JourneyTouchpointListResponse:
    db_engine = _ensure_engine()
    clauses = []
    params = {}
    if stage:
        clauses.append("journey_stage = :stage")
        params["stage"] = stage
    if channel:
        clauses.append("source_channel = :channel")
        params["channel"] = channel
    if brand_name:
        clauses.append("brand_name = :brand_name")
        params["brand_name"] = brand_name
    if model_name:
        clauses.append("model_name = :model_name")
        params["model_name"] = model_name

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    query = text(
        f"""
        SELECT *
        FROM data_asset.dwd_customer_touchpoint
        {where}
        ORDER BY touchpoint_time DESC
        """
    )
    with db_engine.begin() as conn:
        df = pd.read_sql(query, conn, params=params)

    total = len(df)
    start = max(0, (page - 1) * page_size)
    end = start + page_size
    page_df = df.iloc[start:end]
    return JourneyTouchpointListResponse(
        total=total,
        items=[_row_to_touchpoint(row) for _, row in page_df.iterrows()],
        data_lineage=_lineage(
            ["dwd_customer_touchpoint"],
            "触点证据直接来自统一触点明细表，不做跨渠道用户合并。",
        ),
    )


def list_journey_painpoints(
    *,
    brand_name: str | None = None,
    model_name: str | None = None,
) -> list[JourneyPainpointItem]:
    db_engine = _ensure_engine()
    df = pd.read_sql("SELECT * FROM data_asset.ads_journey_painpoint_summary", db_engine)
    df = _filter_frame(df, brand_name=brand_name, model_name=model_name)
    df = df.sort_values(["negative_ratio", "touchpoint_cnt"], ascending=[False, False]) if not df.empty else df
    return [_row_to_painpoint(row) for _, row in df.iterrows()]
