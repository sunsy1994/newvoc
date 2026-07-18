from __future__ import annotations

from datetime import date, datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import DATABASE_URL


COMPETITOR_REPORT_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS data_asset;
CREATE TABLE IF NOT EXISTS data_asset.competitor_report_agent_run (
    report_run_id BIGSERIAL PRIMARY KEY,
    brand_name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    prompt_version TEXT NOT NULL,
    html TEXT NOT NULL,
    summary_json JSONB NOT NULL,
    context_json JSONB NOT NULL,
    rendered_prompt TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_competitor_report_agent_run_scope_time
    ON data_asset.competitor_report_agent_run
    (brand_name, start_date, end_date, generated_at DESC, report_run_id DESC);
"""


def ensure_competitor_report_table(connection: psycopg.Connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(COMPETITOR_REPORT_TABLE_SQL)


def normalize_competitor_report_row(row: dict[str, Any]) -> dict[str, Any]:
    generated_at = row.get("generated_at")
    if isinstance(generated_at, datetime):
        generated_at_value = generated_at.isoformat(timespec="seconds")
    else:
        generated_at_value = str(generated_at or "")

    def normalize_date(value: Any) -> str:
        return value.isoformat() if isinstance(value, date) else str(value or "")

    return {
        "report_run_id": row.get("report_run_id"),
        "brand_name": row.get("brand_name") or "",
        "start_date": normalize_date(row.get("start_date")),
        "end_date": normalize_date(row.get("end_date")),
        "generated_at": generated_at_value,
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
        ensure_competitor_report_table(connection)
        with connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                """
                INSERT INTO data_asset.competitor_report_agent_run
                    (brand_name, start_date, end_date, generated_at, prompt_version, html,
                     summary_json, context_json, rendered_prompt)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING report_run_id, brand_name, start_date, end_date, generated_at,
                          prompt_version, html, summary_json, context_json, rendered_prompt
                """,
                (
                    result["brand_name"],
                    result["start_date"],
                    result["end_date"],
                    result["generated_at"],
                    result["prompt_version"],
                    result["html"],
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
