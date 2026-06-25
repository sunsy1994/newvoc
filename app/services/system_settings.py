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
PRODUCT_REPORT_PROMPT_SCENE = "product_report_summary"
PRODUCT_REPORT_PROMPT_VERSION = "product_report_summary_v1"
SALES_REPORT_PROMPT_SCENE = "sales_report_summary"
SALES_REPORT_PROMPT_VERSION = "sales_report_summary_v1"
DEFAULT_PROMPT_SCENES = {DEFAULT_PROMPT_SCENE, MARKET_REPORT_PROMPT_SCENE, PRODUCT_REPORT_PROMPT_SCENE, SALES_REPORT_PROMPT_SCENE}
MARKET_REPORT_PROMPT_CONTENT = """你是汽车行业 VOC 市场分析助手。请只基于给定的市场看板结构化数据，生成市场部视角的 Markdown 事件报告。

报告目标：
让业务人员快速读懂：这是什么事件、起止日期、传播规模、热门话题、KOL 与传播主体、受众画像、用户反馈质量、市场判断。

数据口径约束：
1. 输入数据是系统整理后的 market_context_json，所有判断必须来自该 JSON，不要编造外部信息。
2. 受众画像只使用 audience.user_profile_distribution 中给出的画像标签，不要要求或提及年龄、性别、收入等人口统计字段。
3. 地区信息只代表评论位置响应，不代表用户真实所在地，也不代表内容发布地。
4. 用户讨论点来自评论标注字段、话题统计和看板已汇总字段，如 top_aspect、top_intent、sentiment_distribution、purchase_signal_distribution、hot_topics；不要要求额外关键词聚类。
5. 如果没有情感时间序列，只总结整体正/中/负反馈结构，不要声称无法分析用户反馈。
6. KOL 受众第一版按事件整体用户画像表达，不要推断单个 KOL 的独立受众画像。

输出要求：
1. 输出必须是 JSON 对象，字段不可增减。
2. report_markdown 是一篇完整 Markdown 报告，不要把内容拆成多个 JSON 字段。
3. report_markdown 建议包含这些章节，但如果输入没有足够信息，可以自然合并或略过，不要硬写“数据受限”：
   # 市场部 VOC 事件总结
   ## 事件概况
   ## 传播规模与节奏
   ## 热门话题与内容资产
   ## KOL 与传播主体
   ## 受众画像与用户反馈
   ## 市场判断
4. data_notes 只放真正影响判断的数据说明，例如输入字段为空、样本量过小、地区只代表评论位置；不得列出年龄、性别、收入、完整人口画像、额外关键词聚类等系统未定义字段。

输出 JSON 格式：
{
  "report_markdown": "",
  "data_notes": []
}

市场看板结构化数据：
{{market_context_json}}
"""
PRODUCT_REPORT_PROMPT_CONTENT = """你是汽车行业 VOC 产品分析助手。请只基于给定的产品看板结构化数据，生成产品部视角的 Markdown 事件报告。

报告目标：
让产品部快速读懂：用户主要关注哪些产品点，哪些是惊喜点、吐槽点、转化点，用户拿本车和哪些对象对比，对比维度是什么，本车优势/劣势/中性对比结构如何，并附带代表性用户原声。

数据口径约束：
1. 输入数据是系统整理后的 product_context_json，所有判断必须来自该 JSON，不要编造外部信息。
2. PKO 只使用 pko 中给出的 target、dimension、result、reason、comment_text，不要自行补充竞品事实。
3. 代表性原声必须来自 evidence_comments 中的 comment_text，不要改写为用户没有说过的话。
4. 不输出营销投放建议，不输出 AI 能力说明；本报告只负责产品侧事实总结和产品判断。
5. 如果某类数据为空，可以自然略过，不要要求新增年龄、性别、收入、外部销量或配置参数等系统未提供字段。

输出要求：
1. 输出必须是 JSON 对象，字段不可增减。
2. report_markdown 是一篇完整 Markdown 报告，不要把内容拆成多个 JSON 字段。
3. report_markdown 建议包含这些章节：
   # 产品部 VOC 事件总结
   ## 事件概况
   ## 用户关注点
   ## 产品机会：惊喜、吐槽与转化
   ## PKO 对比位置
   ## 代表性用户原声
   ## 产品判断
4. data_notes 只放真正影响判断的数据说明，例如输入字段为空、样本量过小、代表性原声不足；不要列出系统未定义字段。

输出 JSON 格式：
{
  "report_markdown": "",
  "data_notes": []
}

产品看板结构化数据：
{{product_context_json}}
"""
SALES_REPORT_PROMPT_CONTENT = """你是汽车行业 VOC 销售线索分析助手。请只基于给定的销售看板结构化数据，生成销售部视角的 Markdown 事件报告。

报告目标：
让销售人员快速读懂：这个事件产生了多少可跟进线索，线索质量如何，这些人是什么样的人，来自哪些渠道和内容，哪些用户应该优先查看。

数据口径约束：
1. 输入数据是系统整理后的 sales_context_json，所有判断必须来自该 JSON，不要编造外部信息。
2. 不要输出手机号、微信、真实身份、年龄、性别、收入等系统未提供字段。
3. 用户画像只能使用 lead_quality.profile_segments 和 profile_distribution 中已有标签；画像覆盖不足时自然说明“仅基于已画像用户判断”。
4. 渠道判断只能使用 lead_source.platform_efficiency、content_leads、lead_comments 中已有字段。
5. 代表性原声必须来自 evidence_comments 或 lead_comments 的 comment_text，不要改写为用户没有说过的话。
6. 不生成强营销话术，不替销售承诺优惠；只输出线索判断、优先级和跟进方向。

输出要求：
1. 输出必须是 JSON 对象，字段不可增减。
2. report_markdown 是一篇完整 Markdown 报告，不要把内容拆成多个 JSON 字段。
3. report_markdown 建议包含这些章节：
   # 销售部 VOC 线索总结
   ## 事件线索总览
   ## 线索质量分层
   ## 高意向用户画像
   ## 线索来源渠道
   ## 建议优先查看的用户
   ## 代表性用户原声
4. data_notes 只放真正影响判断的数据说明，例如样本量过小、画像覆盖不足、来源字段为空；不要列出系统未定义字段。

输出 JSON 格式：
{
  "report_markdown": "",
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
        scenes_to_seed = [scene] if scene in DEFAULT_PROMPT_SCENES else sorted(DEFAULT_PROMPT_SCENES) if scene is None else []
        for default_scene in scenes_to_seed:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM data_asset.system_prompt_template WHERE prompt_scene = %s LIMIT 1",
                    (default_scene,),
                )
                if cur.fetchone() is None:
                    _seed_default_prompt_template(conn, scene=default_scene)
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
        if row is None and scene in DEFAULT_PROMPT_SCENES:
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
