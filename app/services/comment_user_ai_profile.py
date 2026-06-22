from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx
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
from app.services.profile_library import build_comment_user_id, clean_text, load_comment_user_profile_records
from app.services.system_settings import DEFAULT_PROMPT_SCENE, get_default_prompt_template, get_runtime_ai_config


DEFAULT_PROFILE_BATCH = "ai_profile"
DEFAULT_PROMPT_VERSION = "comment_user_profile_v1"
DEFAULT_PROMPT_FILE = PROJECT_ROOT / "画像提示词.txt"


def render_comment_user_profile_prompt(
    template: str,
    comment_user_id: str,
    comments: list[dict[str, Any]],
) -> str:
    input_section = build_comment_input_section(comment_user_id, comments)
    start_marker = "三、输入格式"
    end_marker = "四、输出格式"
    start_index = template.find(start_marker)
    end_index = template.find(end_marker)
    if start_index == -1 or end_index == -1 or end_index <= start_index:
        return f"{template.rstrip()}\n\n====================\n三、输入数据\n====================\n\n{input_section}\n"

    section_start = template.rfind("====================", 0, start_index)
    if section_start == -1:
        section_start = start_index
    section_end = template.rfind("====================", 0, end_index)
    if section_end == -1 or section_end <= section_start:
        section_end = end_index
    replacement = f"====================\n三、输入数据\n====================\n\n{input_section}\n\n"
    return f"{template[:section_start]}{replacement}{template[section_end:]}"


def build_comment_input_section(comment_user_id: str, comments: list[dict[str, Any]]) -> str:
    lines = [f"用户ID：{comment_user_id}", "", "评论列表："]
    for index, comment in enumerate(comments, start=1):
        comment_id = clean_text(comment.get("comment_id")) or str(index)
        comment_text = clean_text(comment.get("comment_text")) or ""
        lines.append(f"{index}. [comment_id={comment_id}] {comment_text}")
    return "\n".join(lines)


def build_openai_chat_payload(model: str, prompt: str) -> dict[str, Any]:
    return {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"},
        "temperature": 0,
    }


def parse_openai_json_response(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("LLM response missing choices[0].message.content") from exc
    if isinstance(content, dict):
        parsed = content
    else:
        try:
            parsed = json.loads(str(content))
        except json.JSONDecodeError as exc:
            raise ValueError("LLM response content is not valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON must be an object")
    return parsed


def call_openai_compatible_json(
    prompt: str,
    *,
    base_url: str,
    api_key: str,
    model: str,
    timeout_seconds: int = PROFILE_AI_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    if not base_url:
        raise ValueError("PROFILE_AI_BASE_URL is not configured")
    if not api_key:
        raise ValueError("PROFILE_AI_API_KEY is not configured")
    if not model:
        raise ValueError("PROFILE_AI_MODEL is not configured")
    endpoint = base_url.rstrip("/")
    if not endpoint.endswith("/chat/completions"):
        endpoint = f"{endpoint}/chat/completions"
    response = httpx.post(
        endpoint,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=build_openai_chat_payload(model, prompt),
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return parse_openai_json_response(response.json())


def fetch_global_comment_rows(database_url: str = DATABASE_URL) -> list[dict[str, Any]]:
    query = """
        SELECT cm.comment_id, cm.content_id, c.title AS content_title, c.source_url,
               coalesce(cm.platform, c.platform) AS platform,
               cm.location, cm.comment_author_name,
               cm.comment_text, cm.published_at,
               cm.like_cnt, cm.reply_cnt, cm.interaction_cnt
        FROM data_asset.dwd_comment cm
        LEFT JOIN data_asset.dwd_content c ON cm.content_id = c.content_id
        WHERE coalesce(cm.comment_author_name, '') <> ''
        ORDER BY cm.published_at ASC NULLS LAST, cm.comment_id
    """
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return [normalize_row(dict(row)) for row in cur.fetchall()]


def filter_comment_rows_by_user_id(rows: list[dict[str, Any]], comment_user_id: str) -> list[dict[str, Any]]:
    matched_rows = []
    for row in rows:
        row_user_id = build_comment_user_id(row.get("platform"), row.get("comment_author_name"), row.get("location"))
        if row_user_id == comment_user_id:
            enriched = dict(row)
            enriched["comment_user_id"] = row_user_id
            matched_rows.append(enriched)
    return matched_rows


def run_comment_user_ai_profile(
    comment_user_id: str,
    *,
    profile_batch: str = DEFAULT_PROFILE_BATCH,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    prompt_path: Path | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    database_url: str = DATABASE_URL,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    comments = filter_comment_rows_by_user_id(fetch_global_comment_rows(database_url), comment_user_id)
    if not comments:
        raise ValueError("未找到该评论用户的全库评论，无法生成画像。")

    runtime_config = get_runtime_ai_config(database_url) if not (base_url and api_key and model and timeout_seconds) else {}
    resolved_base_url = base_url or runtime_config.get("base_url") or PROFILE_AI_BASE_URL
    resolved_api_key = api_key or runtime_config.get("api_key") or PROFILE_AI_API_KEY
    resolved_model = model or runtime_config.get("model_name") or PROFILE_AI_MODEL
    resolved_timeout_seconds = int(timeout_seconds or runtime_config.get("timeout_seconds") or PROFILE_AI_TIMEOUT_SECONDS)

    if prompt_path is None:
        managed_prompt = get_default_prompt_template(DEFAULT_PROMPT_SCENE, database_url=database_url)
        template = str(managed_prompt["prompt_content"])
        resolved_prompt_version = str(managed_prompt.get("prompt_version") or prompt_version or DEFAULT_PROMPT_VERSION)
        source_file_name = f"system_prompt:{resolved_prompt_version}"
    else:
        template = prompt_path.read_text(encoding="utf-8")
        resolved_prompt_version = prompt_version or DEFAULT_PROMPT_VERSION
        source_file_name = f"ai:{prompt_path.name}"

    prompt = render_comment_user_profile_prompt(template, comment_user_id, comments)
    llm_result = call_openai_compatible_json(
        prompt,
        base_url=resolved_base_url,
        api_key=resolved_api_key,
        model=resolved_model,
        timeout_seconds=resolved_timeout_seconds,
    )

    records = [
        {
            "comment_user_id": comment_user_id,
            "profile_batch": profile_batch or DEFAULT_PROFILE_BATCH,
            "prompt_version": resolved_prompt_version,
            "llm_result_json": llm_result,
            "source_file_name": source_file_name,
        }
    ]
    db_loaded = load_comment_user_profile_records(records, database_url=database_url)
    return {
        "comment_user_id": comment_user_id,
        "comment_count": len(comments),
        "profile_batch": records[0]["profile_batch"],
        "prompt_version": resolved_prompt_version,
        "db_loaded": db_loaded,
        "llm_result": llm_result,
    }
