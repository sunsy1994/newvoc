from __future__ import annotations

import hashlib
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
MARKET_REPORT_PROMPT_VERSION = "market_report_summary_v2"
PRODUCT_REPORT_PROMPT_SCENE = "product_report_summary"
PRODUCT_REPORT_PROMPT_VERSION = "product_report_summary_v3"
SALES_REPORT_PROMPT_SCENE = "sales_report_summary"
SALES_REPORT_PROMPT_VERSION = "sales_report_summary_v2"
DEFAULT_PROMPT_SCENES = {DEFAULT_PROMPT_SCENE, MARKET_REPORT_PROMPT_SCENE, PRODUCT_REPORT_PROMPT_SCENE, SALES_REPORT_PROMPT_SCENE}
LEGACY_REPORT_PROMPT_HASHES = {
    (
        MARKET_REPORT_PROMPT_SCENE,
        "market_report_summary_v1",
    ): "589a3296157164b178e383a14b2842a95ae80827339c6cccd95986eabc3a965e",
    (
        PRODUCT_REPORT_PROMPT_SCENE,
        "product_report_summary_v1",
    ): "dc71fe16d3788156d94a059691af2ae81cfbc92660255c194e2b18fdf12b6dc5",
    (
        PRODUCT_REPORT_PROMPT_SCENE,
        "product_report_summary_v2",
    ): "a0606723cf4598959dd965737804c85714184c2a9dffbcc1812822533c9fdd50",
    (
        SALES_REPORT_PROMPT_SCENE,
        "sales_report_summary_v1",
    ): "4a138e49a9597c3a3f70116a2e40642da818845235e3a65a1e7f3a2645a68031",
}
MARKET_REPORT_PROMPT_CONTENT = """你是汽车行业 VOC 市场分析助手。请只基于给定的市场看板结构化数据生成固定字段的叙事文案。

约束：
1. 所有判断必须来自 market_context_json；输入缺失时不得推断、补齐趋势或编造外部信息。
2. 图表类型和数值由系统固定。不要生成图表、图型、排序、数据点或 structured_report，也不要修改输入数值。
3. 地区信息只代表评论位置响应，不代表用户真实所在地或内容发布地。
4. data_notes 只放真正影响判断的数据说明。
5. 输出必须是 JSON 对象，字段和 section_insights 的键不可增减，不要输出 Markdown。

严格输出：
{
  "headline": "",
  "executive_summary": "",
  "section_insights": {
    "market_rhythm": "",
    "market_topics": "",
    "market_platforms": "",
    "market_feedback": ""
  },
  "data_notes": []
}

市场看板结构化数据：
{{market_context_json}}
"""
PRODUCT_REPORT_PROMPT_CONTENT = """你是汽车行业 VOC 产品分析助手。请只基于给定的产品看板结构化数据生成固定字段的叙事文案。

约束：
1. 所有判断必须来自 product_context_json；输入缺失时不得推断、补齐竞品事实或编造外部信息。
2. 图表类型和数值由系统固定。不要生成图表、图型、排序、数据点或 structured_report，也不要修改输入数值。
3. PKO 只使用 pko 中已有的 target、dimension、result、reason、comment_text 和 comment_id。
4. 只总结机会、风险、转化信号与 PKO 事实，所有输出字段均不得包含产品建议。
5. data_notes 只放真正影响判断的数据说明。
6. storyline 不得复述 section_insights。
7. storyline 的 metric_refs 只能引用输入中提供的指标路径，evidence_refs 只能引用输入中提供的 comment_id。
8. 输出必须是 JSON 对象，字段、章节和 section_insights 的键不可增减，不要输出 Markdown。

严格输出：
{
  "headline": "",
  "executive_summary": "",
  "section_insights": {
    "product_focus": "",
    "product_sentiment": "",
    "product_opportunity": "",
    "product_pko_relationships": "",
    "product_pko_results": ""
  },
  "storyline": {
    "headline": "",
    "lead": "",
    "chapters": [
      {"chapter_id": "focus", "title": "用户在关注什么", "conclusion": "", "body": "", "metric_refs": [], "evidence_refs": []},
      {"chapter_id": "attitude", "title": "用户如何评价", "conclusion": "", "body": "", "metric_refs": [], "evidence_refs": []},
      {"chapter_id": "comparison", "title": "用户在和谁比较", "conclusion": "", "body": "", "metric_refs": [], "evidence_refs": []},
      {"chapter_id": "evidence", "title": "证据如何支撑", "conclusion": "", "body": "", "metric_refs": [], "evidence_refs": []}
    ]
  },
  "data_notes": []
}

产品看板结构化数据：
{{product_context_json}}
"""
SALES_REPORT_PROMPT_CONTENT = """你是汽车行业 VOC 销售线索分析助手。请只基于给定的销售看板结构化数据生成固定字段的叙事文案。

约束：
1. 所有判断必须来自 sales_context_json；输入缺失时不得推断、补齐用户信息或编造外部信息。
2. 图表类型和数值由系统固定。不要生成图表、图型、排序、数据点或 structured_report，也不要修改输入数值。
3. 不输出手机号、微信、真实身份、年龄、性别、收入等系统未提供字段。
4. 不生成营销承诺，只输出线索质量、意图和来源判断。
5. data_notes 只放真正影响判断的数据说明。
6. 输出必须是 JSON 对象，字段和 section_insights 的键不可增减，不要输出 Markdown。

严格输出：
{
  "headline": "",
  "executive_summary": "",
  "section_insights": {
    "sales_funnel": "",
    "sales_signals": "",
    "sales_intents": "",
    "sales_sources": ""
  },
  "data_notes": []
}

销售看板结构化数据：
{{sales_context_json}}
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
    if scene == PRODUCT_REPORT_PROMPT_SCENE:
        return "product report summary prompt", PRODUCT_REPORT_PROMPT_VERSION, PRODUCT_REPORT_PROMPT_CONTENT
    if scene == SALES_REPORT_PROMPT_SCENE:
        return "sales report summary prompt", SALES_REPORT_PROMPT_VERSION, SALES_REPORT_PROMPT_CONTENT
    return "comment user profile prompt", DEFAULT_PROMPT_VERSION, _read_default_prompt_file()


def _prompt_seed_action(row: dict[str, Any] | None) -> str:
    if not row:
        return "seed"
    key = (
        str(row.get("prompt_scene") or ""),
        str(row.get("prompt_version") or ""),
    )
    expected_hash = LEGACY_REPORT_PROMPT_HASHES.get(key)
    content = row.get("prompt_content")
    if not expected_hash or not isinstance(content, str):
        return "keep"
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return "upgrade" if digest == expected_hash else "keep"


def _get_prompt_by_version(
    conn: psycopg.Connection,
    scene: str,
    version: str,
) -> dict[str, Any] | None:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT *
            FROM data_asset.system_prompt_template
            WHERE prompt_scene = %s AND prompt_version = %s
            LIMIT 1
            """,
            (scene, version),
        )
        row = cur.fetchone()
    return normalize_row(dict(row)) if row else None


def _seed_default_prompt_template(conn: psycopg.Connection, scene: str = DEFAULT_PROMPT_SCENE) -> dict[str, Any]:
    prompt_name, prompt_version, prompt_content = _default_prompt_payload(scene)
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            INSERT INTO data_asset.system_prompt_template
              (prompt_name, prompt_scene, prompt_version, prompt_content, is_default, is_enabled)
            VALUES (%s, %s, %s, %s, TRUE, TRUE)
            ON CONFLICT (prompt_scene, prompt_version) DO NOTHING
            RETURNING *
            """,
            (prompt_name, scene, prompt_version, prompt_content),
        )
        row = cur.fetchone()
    if row:
        return normalize_row(dict(row))
    existing = _get_prompt_by_version(conn, scene, prompt_version)
    if existing is None:
        raise RuntimeError(f"Failed to seed default prompt template: {scene}")
    return existing


def _get_enabled_default_prompt(
    conn: psycopg.Connection,
    scene: str,
) -> dict[str, Any] | None:
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
    return normalize_row(dict(row)) if row else None


def _ensure_default_prompt_template(
    conn: psycopg.Connection,
    scene: str,
) -> dict[str, Any] | None:
    row = _get_enabled_default_prompt(conn, scene)
    action = _prompt_seed_action(row)
    if action == "keep":
        return row
    _, target_version, target_content = _default_prompt_payload(scene)
    target = _get_prompt_by_version(conn, scene, target_version)
    if target is not None and target.get("prompt_content") != target_content:
        return row
    if target is not None:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE data_asset.system_prompt_template
                SET is_default = FALSE
                WHERE prompt_scene = %s
                """,
                (scene,),
            )
            cur.execute(
                """
                UPDATE data_asset.system_prompt_template
                SET is_default = TRUE,
                    is_enabled = TRUE,
                    updated_time = CURRENT_TIMESTAMP
                WHERE prompt_scene = %s AND prompt_version = %s
                RETURNING *
                """,
                (scene, target_version),
            )
            activated = cur.fetchone()
        return normalize_row(dict(activated)) if activated else target
    if action == "upgrade":
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE data_asset.system_prompt_template
                SET is_default = FALSE
                WHERE prompt_scene = %s
                """,
                (scene,),
            )
    return _seed_default_prompt_template(conn, scene=scene)


def list_prompt_templates(scene: str | None = None, database_url: str = DATABASE_URL) -> dict[str, list[dict[str, Any]]]:
    init_database(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        scenes_to_seed = [scene] if scene in DEFAULT_PROMPT_SCENES else sorted(DEFAULT_PROMPT_SCENES) if scene is None else []
        for default_scene in scenes_to_seed:
            _ensure_default_prompt_template(conn, default_scene)
        if scenes_to_seed:
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
        row = (
            _ensure_default_prompt_template(conn, scene)
            if scene in DEFAULT_PROMPT_SCENES
            else _get_enabled_default_prompt(conn, scene)
        )
        if row is not None and scene in DEFAULT_PROMPT_SCENES:
            conn.commit()
        if row is None:
            raise ValueError(f"鏈壘鍒板惎鐢ㄧ殑榛樿鎻愮ず璇嶏細{scene}")
        return row


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
