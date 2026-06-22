from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.asset_library import normalize_row
from app.services.db_loader import init_database


FLOW_TEMPLATE = [
    {
        "id": "select_users",
        "title": "选择用户范围",
        "desc": "从评论用户资产中选择需要画像的用户，第一版默认使用全库评论用户。",
        "input_tables": ["data_asset.dwd_comment"],
        "output_tables": ["comment_user_id"],
        "rules": ["按平台、昵称、位置生成系统内评论用户ID", "销售看板可对单个用户触发画像"],
        "function_name": "select_comment_users",
        "metric_keys": ["comment_user_count"],
    },
    {
        "id": "extract_comments",
        "title": "抽取全量评论",
        "desc": "抽取该用户在全库所有事件、所有帖子下的评论，保证画像不是单条评论判断。",
        "input_tables": ["data_asset.dwd_comment", "data_asset.dwd_content"],
        "output_tables": ["user_comment_rows"],
        "rules": ["按系统评论用户ID匹配", "保留评论正文、发布时间、来源平台和帖子链接"],
        "function_name": "fetch_global_comment_rows",
        "metric_keys": ["comment_count"],
    },
    {
        "id": "render_prompt",
        "title": "拼接提示词",
        "desc": "读取系统管理中的默认提示词，把用户ID和评论列表拼接为 LLM 输入。",
        "input_tables": ["data_asset.system_prompt_template", "user_comment_rows"],
        "output_tables": ["rendered_prompt"],
        "rules": ["默认场景 comment_user_profile", "提示词版本写入画像结果用于追溯"],
        "function_name": "render_comment_user_profile_prompt",
        "metric_keys": ["enabled_prompt_count"],
    },
    {
        "id": "call_llm",
        "title": "调用 LLM",
        "desc": "读取系统管理中的 AI 参数，按 OpenAI 兼容格式调用模型并要求返回 JSON。",
        "input_tables": ["data_asset.system_ai_config", "rendered_prompt"],
        "output_tables": ["llm_result_json"],
        "rules": ["response_format 使用 json_object", "API Key 不在前端明文展示"],
        "function_name": "call_openai_compatible_json",
        "metric_keys": ["ai_config_count"],
    },
    {
        "id": "normalize_json",
        "title": "JSON 规范化解析",
        "desc": "将 LLM 原始 JSON 解析为用户主标签、标签得分和证据明细。",
        "input_tables": ["llm_result_json"],
        "output_tables": ["profile_records", "label_score_records"],
        "rules": ["保留原始 JSON", "按 Python 规则计算主标签与标签得分"],
        "function_name": "load_comment_user_profile_records",
        "metric_keys": ["raw_profile_count"],
    },
    {
        "id": "write_profile_tables",
        "title": "写入画像表",
        "desc": "把原始结果、汇总画像和标签得分分别写入三张画像表。",
        "input_tables": ["profile_records", "label_score_records"],
        "output_tables": [
            "data_asset.user_profile_comment_raw",
            "data_asset.user_profile_comment_result",
            "data_asset.user_profile_comment_label_score",
        ],
        "rules": ["按 comment_user_id + profile_batch upsert", "标签得分按维度和标签展开"],
        "function_name": "load_comment_user_profile_records",
        "metric_keys": ["profiled_user_count", "label_score_count"],
    },
    {
        "id": "validate_result",
        "title": "结果校验",
        "desc": "检查画像是否入库、是否有主标签和标签分数，供销售看板继续消费。",
        "input_tables": ["data_asset.user_profile_comment_result", "data_asset.user_profile_comment_label_score"],
        "output_tables": ["sales_dashboard_user_profile"],
        "rules": ["销售看板读取用户画像", "用户详情抽屉展示雷达图、证据和情绪曲线"],
        "function_name": "get_voc_event_comment_user_insight_profile",
        "metric_keys": ["profiled_user_count", "label_score_count"],
    },
]


def _fetch_ai_flow_summary(database_url: str) -> dict[str, int]:
    query = """
        WITH comment_users AS (
          SELECT DISTINCT
                 coalesce(platform, '') || '|' ||
                 coalesce(comment_author_name, '') || '|' ||
                 coalesce(location, '') AS comment_user_key
          FROM data_asset.dwd_comment
          WHERE coalesce(comment_author_name, '') <> ''
        )
        SELECT
          (SELECT count(*) FROM comment_users) AS comment_user_count,
          (SELECT count(*) FROM data_asset.dwd_comment) AS comment_count,
          (SELECT count(*) FROM data_asset.system_prompt_template WHERE prompt_scene = 'comment_user_profile' AND is_enabled = TRUE) AS enabled_prompt_count,
          (SELECT count(*) FROM data_asset.system_ai_config WHERE is_default = TRUE AND is_enabled = TRUE) AS ai_config_count,
          (SELECT count(*) FROM data_asset.user_profile_comment_raw) AS raw_profile_count,
          (SELECT count(*) FROM data_asset.user_profile_comment_result) AS profiled_user_count,
          (SELECT count(*) FROM data_asset.user_profile_comment_label_score) AS label_score_count
    """
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            row = normalize_row(dict(cur.fetchone()))
    return {key: int(value or 0) for key, value in row.items()}


def _node_status(node: dict[str, Any], summary: dict[str, int]) -> str:
    if node["id"] == "render_prompt" and summary.get("enabled_prompt_count", 0) <= 0:
        return "blocked"
    if node["id"] == "call_llm" and summary.get("ai_config_count", 0) <= 0:
        return "blocked"
    if node["id"] in {"normalize_json", "write_profile_tables", "validate_result"} and summary.get("raw_profile_count", 0) <= 0:
        return "waiting"
    return "ready"


def build_comment_user_ai_flow(database_url: str = DATABASE_URL) -> dict[str, Any]:
    init_database(database_url)
    summary = _fetch_ai_flow_summary(database_url)
    nodes = []
    for index, node in enumerate(FLOW_TEMPLATE, start=1):
        metrics = {key: summary.get(key, 0) for key in node["metric_keys"]}
        nodes.append(
            {
                **node,
                "order": index,
                "metrics": metrics,
                "status": _node_status(node, summary),
            }
        )
    return {"nodes": nodes, "summary": summary}
