from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.asset_library import normalize_row
from app.services.db_loader import init_database


VALID_EMOJI_TYPES = {"emoji", "image"}


def list_emoji_mappings(enabled_only: bool = False, database_url: str = DATABASE_URL) -> dict[str, list[dict[str, Any]]]:
    init_database(database_url)
    query = """
        SELECT emoji_id,
               emoji_code,
               emoji_type,
               emoji_value,
               display_name,
               is_enabled,
               created_time,
               updated_time
        FROM data_asset.system_emoji_mapping
        WHERE (%s::boolean = FALSE OR is_enabled = TRUE)
        ORDER BY is_enabled DESC, emoji_code
    """
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (enabled_only,))
            rows = [normalize_row(dict(row)) for row in cur.fetchall()]
    return {"emojis": rows}


def save_emoji_mapping(payload: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    init_database(database_url)
    emoji_code = str(payload.get("emoji_code") or "").strip()
    emoji_type = str(payload.get("emoji_type") or "emoji").strip()
    emoji_value = str(payload.get("emoji_value") or "").strip()
    display_name = str(payload.get("display_name") or "").strip()
    is_enabled = bool(payload.get("is_enabled", True))

    if not emoji_code:
        raise ValueError("emoji_code 不能为空")
    if not emoji_code.startswith("[") or not emoji_code.endswith("]"):
        raise ValueError("emoji_code 必须使用 [表情名] 格式")
    if emoji_type not in VALID_EMOJI_TYPES:
        raise ValueError("emoji_type 只能是 emoji 或 image")
    if not emoji_value:
        raise ValueError("emoji_value 不能为空")
    if emoji_type == "image" and not (emoji_value.startswith("http://") or emoji_value.startswith("https://") or emoji_value.startswith("/")):
        raise ValueError("image 类型的 emoji_value 必须是 http(s) URL 或以 / 开头的静态路径")

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO data_asset.system_emoji_mapping
                  (emoji_code, emoji_type, emoji_value, display_name, is_enabled)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (emoji_code) DO UPDATE
                SET emoji_type = EXCLUDED.emoji_type,
                    emoji_value = EXCLUDED.emoji_value,
                    display_name = EXCLUDED.display_name,
                    is_enabled = EXCLUDED.is_enabled,
                    updated_time = CURRENT_TIMESTAMP
                RETURNING emoji_id,
                          emoji_code,
                          emoji_type,
                          emoji_value,
                          display_name,
                          is_enabled,
                          created_time,
                          updated_time
                """,
                (emoji_code, emoji_type, emoji_value, display_name or emoji_code.strip("[]"), is_enabled),
            )
            row = cur.fetchone()
        conn.commit()
    return normalize_row(dict(row))
