from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import (
    DATABASE_URL,
    PROFILE_AI_API_KEY,
    PROFILE_AI_BASE_URL,
    PROFILE_AI_MODEL,
    PROFILE_AI_TIMEOUT_SECONDS,
    PROJECT_ROOT,
)
from app.services.asset_library import normalize_row
from app.services.db_loader import init_database


DEFAULT_AI_CONFIG_NAME = "default"
DEFAULT_PROMPT_SCENE = "comment_user_profile"
DEFAULT_PROMPT_VERSION = "comment_user_profile_v1"
MARKET_REPORT_PROMPT_SCENE = "market_report_summary"
MARKET_REPORT_PROMPT_VERSION = "market_report_summary_v1"
MARKET_REPORT_PROMPT_CONTENT = """浣犳槸姹借溅琛屼笟 VOC 甯傚満鍒嗘瀽鍔╂墜銆傝鍙熀浜庣粰瀹氱殑甯傚満鐪嬫澘缁撴瀯鍖栨暟鎹紝鐢熸垚甯傚満閮ㄨ瑙掔殑浜嬩欢鎬荤粨銆?
璇锋寜涓氬姟浜哄憳闃呰椤哄簭缁勭粐锛氳繖鏄粈涔堜簨浠躲€佽捣姝㈡棩鏈熴€佸０閲忚妯°€佺儹闂ㄨ瘽棰樸€並OL 涓庝綔鑰呫€佸彈浼楃敾鍍忋€佺敤鎴峰弽棣堣川閲忋€佸競鍦洪儴缁撹銆?
瑕佹眰锛?1. 鍙娇鐢ㄧ粰瀹氫俊鎭紝涓嶇紪閫犳暟鎹紝涓嶅紩鍏ヨ緭鍏ュ鐨勪俊鎭€?2. 涓嶈閫愰」澶嶈堪鍥捐〃锛岃鍑濈粌浼犳挱鍒ゆ柇銆?3. 濡傛灉鏌愮被鏁版嵁涓嶈冻锛岃鍦?data_limits 璇存槑銆?4. 杈撳嚭蹇呴』鏄?JSON 瀵硅薄锛屽瓧娈典笉鍙鍑忥細
{
  "event_overview": "",
  "scale_summary": "",
  "topic_summary": "",
  "kol_summary": "",
  "audience_summary": "",
  "feedback_summary": "",
  "market_conclusion": "",
  "data_limits": ""
}

甯傚満鐪嬫澘缁撴瀯鍖栨暟鎹細
{{market_context_json}}
"""
DEFAULT_PROMPT_FILE = PROJECT_ROOT / "鐢诲儚鎻愮ず璇?txt"


def mask_api_key(api_key: str | None) -> str:
    if not api_key:
        return ""
    if len(api_key) <= 8:
        return "****"
    return f"{api_key[:3]}****{api_key[-4:]}"


def _public_ai_config(row: dict[str, Any]) -> dict[str, Any]:
    api_key = str(row.get("api_key") or "")
    return {
        "ai_config_id": row.get("ai_config_id"),
        "config_name": row.get("config_name") or DEFAULT_AI_CONFIG_NAME,
        "base_url": row.get("base_url") or "",
        "model_name": row.get("model_name") or "",
        "timeout_seconds": int(row.get("timeout_seconds") or PROFILE_AI_TIMEOUT_SECONDS),
        "is_enabled": bool(row.get("is_enabled")),
        "is_default": bool(row.get("is_default")),
        "api_key_configured": bool(api_key),
        "api_key_masked": mask_api_key(api_key),
        "created_time": row.get("created_time"),
        "updated_time": row.get("updated_time"),
    }


def _seed_default_ai_config(conn: psycopg.Connection) -> dict[str, Any]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO data_asset.system_ai_config
              (config_name, base_url, api_key, model_name, timeout_seconds, is_enabled, is_default)
            VALUES (%s, %s, %s, %s, %s, TRUE, TRUE)
            ON CONFLICT (config_name) DO UPDATE
            SET updated_time = CURRENT_TIMESTAMP
            RETURNING *
            """,
            (
                DEFAULT_AI_CONFIG_NAME,
                PROFILE_AI_BASE_URL,
                PROFILE_AI_API_KEY,
                PROFILE_AI_MODEL,
                PROFILE_AI_TIMEOUT_SECONDS,
            ),
        )
        return normalize_row(dict(cur.fetchone()))


def get_default_ai_config(database_url: str = DATABASE_URL) -> dict[str, Any]:
    init_database(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM data_asset.system_ai_config
                WHERE is_default = TRUE
                ORDER BY ai_config_id
                LIMIT 1
                """
            )
            row = cur.fetchone()
        if row is None:
            row = _seed_default_ai_config(conn)
            conn.commit()
        return _public_ai_config(normalize_row(dict(row)))


def get_runtime_ai_config(database_url: str = DATABASE_URL) -> dict[str, Any]:
    init_database(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM data_asset.system_ai_config
                WHERE is_default = TRUE
                ORDER BY ai_config_id
                LIMIT 1
                """
            )
            row = cur.fetchone()
        if row is None:
            row = _seed_default_ai_config(conn)
            conn.commit()
        config = normalize_row(dict(row))
        if not config.get("is_enabled"):
            raise ValueError("AI 参数配置已停用，请先在系统管理中启用。")
        return {
            "base_url": config.get("base_url") or "",
            "api_key": config.get("api_key") or "",
            "model_name": config.get("model_name") or "",
            "timeout_seconds": int(config.get("timeout_seconds") or PROFILE_AI_TIMEOUT_SECONDS),
            "is_enabled": bool(config.get("is_enabled")),
        }


def save_default_ai_config(payload: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    init_database(database_url)
    base_url = str(payload.get("base_url") or "").strip()
    model_name = str(payload.get("model_name") or "").strip()
    if not base_url:
        raise ValueError("base_url 涓嶈兘涓虹┖")
    if not model_name:
        raise ValueError("model_name 涓嶈兘涓虹┖")
    timeout_seconds = int(payload.get("timeout_seconds") or PROFILE_AI_TIMEOUT_SECONDS)
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds 蹇呴』澶т簬 0")
    api_key = payload.get("api_key")

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT api_key
                FROM data_asset.system_ai_config
                WHERE config_name = %s
                """,
                (DEFAULT_AI_CONFIG_NAME,),
            )
            existing = cur.fetchone()
            next_api_key = str(api_key).strip() if api_key is not None and str(api_key).strip() else (existing or {}).get("api_key")
            cur.execute(
                """
                INSERT INTO data_asset.system_ai_config
                  (config_name, base_url, api_key, model_name, timeout_seconds, is_enabled, is_default)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE)
                ON CONFLICT (config_name) DO UPDATE
                SET base_url = EXCLUDED.base_url,
                    api_key = EXCLUDED.api_key,
                    model_name = EXCLUDED.model_name,
                    timeout_seconds = EXCLUDED.timeout_seconds,
                    is_enabled = EXCLUDED.is_enabled,
                    is_default = TRUE,
                    updated_time = CURRENT_TIMESTAMP
                RETURNING *
                """,
                (
                    DEFAULT_AI_CONFIG_NAME,
                    base_url,
                    next_api_key,
                    model_name,
                    timeout_seconds,
                    bool(payload.get("is_enabled", True)),
                ),
            )
            row = cur.fetchone()
        conn.commit()
        return _public_ai_config(normalize_row(dict(row)))


def _read_default_prompt_file() -> str:
    if DEFAULT_PROMPT_FILE.exists():
        return DEFAULT_PROMPT_FILE.read_text(encoding="utf-8")
    return "鐢ㄦ埛ID锛歿{user_id}}\n\n璇勮鍒楄〃锛歕n1. {{comment_1}}\n"


def _default_prompt_payload(scene: str) -> tuple[str, str, str]:
    if scene == MARKET_REPORT_PROMPT_SCENE:
        return "market report summary prompt", MARKET_REPORT_PROMPT_VERSION, MARKET_REPORT_PROMPT_CONTENT
    return "comment user profile prompt", DEFAULT_PROMPT_VERSION, _read_default_prompt_file()


def _seed_default_prompt_template(conn: psycopg.Connection, scene: str = DEFAULT_PROMPT_SCENE) -> dict[str, Any]:
    prompt_name, prompt_version, prompt_content = _default_prompt_payload(scene)
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO data_asset.system_prompt_template
              (prompt_name, prompt_scene, prompt_version, prompt_content, is_default, is_enabled)
            VALUES (%s, %s, %s, %s, TRUE, TRUE)
            ON CONFLICT (prompt_scene, prompt_version) DO UPDATE
            SET updated_time = CURRENT_TIMESTAMP
            RETURNING *
            """,
            (prompt_name, scene, prompt_version, prompt_content),
        )
        return normalize_row(dict(cur.fetchone()))


def list_prompt_templates(scene: str | None = None, database_url: str = DATABASE_URL) -> dict[str, list[dict[str, Any]]]:
    init_database(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        if scene in {DEFAULT_PROMPT_SCENE, MARKET_REPORT_PROMPT_SCENE}:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM data_asset.system_prompt_template WHERE prompt_scene = %s LIMIT 1",
                    (scene,),
                )
                if cur.fetchone() is None:
                    _seed_default_prompt_template(conn, scene=scene)
                    conn.commit()

        query = """
            SELECT *
            FROM data_asset.system_prompt_template
            WHERE (%s::text IS NULL OR prompt_scene = %s)
            ORDER BY prompt_scene, is_default DESC, updated_time DESC, prompt_id DESC
        """
        with conn.cursor() as cur:
            cur.execute(query, (scene, scene))
            prompts = [normalize_row(dict(row)) for row in cur.fetchall()]
        return {"prompts": prompts}


def get_default_prompt_template(scene: str = DEFAULT_PROMPT_SCENE, database_url: str = DATABASE_URL) -> dict[str, Any]:
    init_database(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT *
                FROM data_asset.system_prompt_template
                WHERE prompt_scene = %s AND is_default = TRUE AND is_enabled = TRUE
                ORDER BY updated_time DESC, prompt_id DESC
                LIMIT 1
                """,
                (scene,),
            )
            row = cur.fetchone()
        if row is None and scene in {DEFAULT_PROMPT_SCENE, MARKET_REPORT_PROMPT_SCENE}:
            row = _seed_default_prompt_template(conn, scene=scene)
            conn.commit()
        if row is None:
            raise ValueError(f"鏈壘鍒板惎鐢ㄧ殑榛樿鎻愮ず璇嶏細{scene}")
        return normalize_row(dict(row))


def save_prompt_template(payload: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    init_database(database_url)
    prompt_name = str(payload.get("prompt_name") or "").strip()
    prompt_scene = str(payload.get("prompt_scene") or "").strip()
    prompt_version = str(payload.get("prompt_version") or "").strip()
    prompt_content = str(payload.get("prompt_content") or "").strip()
    if not prompt_name:
        raise ValueError("prompt_name 涓嶈兘涓虹┖")
    if not prompt_scene:
        raise ValueError("prompt_scene 涓嶈兘涓虹┖")
    if not prompt_version:
        raise ValueError("prompt_version 涓嶈兘涓虹┖")
    if not prompt_content:
        raise ValueError("prompt_content 涓嶈兘涓虹┖")

    is_default = bool(payload.get("is_default", False))
    is_enabled = bool(payload.get("is_enabled", True))
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            if is_default:
                cur.execute(
                    "UPDATE data_asset.system_prompt_template SET is_default = FALSE WHERE prompt_scene = %s",
                    (prompt_scene,),
                )
            cur.execute(
                """
                INSERT INTO data_asset.system_prompt_template
                  (prompt_name, prompt_scene, prompt_version, prompt_content, is_default, is_enabled)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (prompt_scene, prompt_version) DO UPDATE
                SET prompt_name = EXCLUDED.prompt_name,
                    prompt_content = EXCLUDED.prompt_content,
                    is_default = EXCLUDED.is_default,
                    is_enabled = EXCLUDED.is_enabled,
                    updated_time = CURRENT_TIMESTAMP
                RETURNING *
                """,
                (prompt_name, prompt_scene, prompt_version, prompt_content, is_default, is_enabled),
            )
            row = cur.fetchone()
        conn.commit()
        return normalize_row(dict(row))

