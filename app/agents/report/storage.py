from __future__ import annotations

from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import DATABASE_URL


EVENT_REPORT_CACHE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS data_asset;
CREATE TABLE IF NOT EXISTS data_asset.event_report_agent_run (
    report_run_id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary_json JSONB NOT NULL,
    context_json JSONB NOT NULL,
    rendered_prompt TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_event_report_agent_run_event_time
    ON data_asset.event_report_agent_run (event_id, generated_at DESC, report_run_id DESC);
"""


def ensure_event_report_table(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(EVENT_REPORT_CACHE_TABLE_SQL)


def normalize_event_report_row(row: dict[str, Any]) -> dict[str, Any]:
    generated_at = row.get("generated_at")
    generated_at_value = generated_at.isoformat(timespec="seconds") if isinstance(generated_at, datetime) else str(generated_at or "")
    return {
        "event_id": row.get("event_id"),
        "prompt_version": row.get("prompt_version") or "",
        "generated_at": generated_at_value,
        "summary": row.get("summary_json") or {},
        "context": row.get("context_json") or {},
        "rendered_prompt": row.get("rendered_prompt") or "",
    }


def save_event_report_agent_result(result: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    with psycopg.connect(database_url) as conn:
        ensure_event_report_table(conn)
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                """
                INSERT INTO data_asset.event_report_agent_run
                    (event_id, prompt_version, generated_at, summary_json, context_json, rendered_prompt)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING event_id, prompt_version, generated_at, summary_json, context_json, rendered_prompt
                """,
                (
                    result["event_id"],
                    result.get("prompt_version") or "event_report_agent_v1",
                    result.get("generated_at"),
                    Jsonb(result.get("summary") or {}),
                    Jsonb(result.get("context") or {}),
                    result.get("rendered_prompt") or "",
                ),
            )
            row = cur.fetchone()
        conn.commit()
    normalized = normalize_event_report_row(dict(row))
    return {**result, **normalized}
