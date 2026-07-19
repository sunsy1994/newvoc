from __future__ import annotations

from datetime import date
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import DATABASE_URL
from app.services.report_time import format_shanghai_datetime, to_shanghai_datetime


def normalize_competitor_report_row(row: dict[str, Any]) -> dict[str, Any]:
    generated_at = row.get("generated_at")
    generated_at_value = format_shanghai_datetime(generated_at)

    def normalize_date(value: Any) -> str:
        return value.isoformat() if isinstance(value, date) else str(value or "")

    return {
        "report_run_id": row.get("report_run_id"),
        "brand_name": row.get("brand_name") or "",
        "start_date": normalize_date(row.get("start_date")),
        "end_date": normalize_date(row.get("end_date")),
        "generated_at": generated_at_value,
        "status": row.get("status") or "completed",
        "error_message": row.get("error_message") or "",
        "prompt_version": row.get("prompt_version") or "",
        "html": row.get("html") or "",
        "summary": row.get("summary_json") or {},
        "context": row.get("context_json") or {},
        "rendered_prompt": row.get("rendered_prompt") or "",
    }


def save_competitor_report_agent_result(
    result: dict[str, Any],
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    with psycopg.connect(database_url) as connection:
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO data_asset.competitor_report_agent_run
                    (brand_name, start_date, end_date, generated_at, status, error_message,
                     prompt_version, html, summary_json, context_json, rendered_prompt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING report_run_id, brand_name, start_date, end_date, generated_at,
                          status, error_message, prompt_version, html, summary_json,
                          context_json, rendered_prompt
                """,
                (
                    result["brand_name"],
                    result["start_date"],
                    result["end_date"],
                    to_shanghai_datetime(result["generated_at"]),
                    result.get("status") or "completed",
                    result.get("error_message"),
                    result["prompt_version"],
                    result.get("html") or "",
                    Jsonb(result.get("summary") or {}),
                    Jsonb(result.get("context") or {}),
                    result.get("rendered_prompt") or "",
                ),
            )
            row = cursor.fetchone()
        connection.commit()
    if row is None:
        raise RuntimeError("竞品报告保存失败。")
    return normalize_competitor_report_row(dict(row))
