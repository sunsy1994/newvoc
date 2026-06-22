from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from app.config import DATABASE_URL
from app.services.comment_user_ai_profile import call_openai_compatible_json
from app.services.event_voc_insights import get_voc_event_market_dashboard
from app.services.system_settings import get_default_prompt_template, get_runtime_ai_config


MARKET_REPORT_PROMPT_SCENE = "market_report_summary"
DEFAULT_MARKET_REPORT_PROMPT_VERSION = "market_report_summary_v1"
MARKET_REPORT_FIELDS = [
    "event_overview",
    "scale_summary",
    "topic_summary",
    "kol_summary",
    "audience_summary",
    "feedback_summary",
    "market_conclusion",
    "data_limits",
]

DEFAULT_MARKET_REPORT_PROMPT = """你是汽车行业 VOC 市场分析助手。请只基于给定的市场看板结构化数据，生成市场部视角的事件总结。

请按业务人员阅读顺序组织：这是什么事件、起止日期、声量规模、热门话题、KOL 与作者、受众画像、用户反馈质量、市场部结论。

要求：
1. 只使用给定信息，不编造数据，不引入输入外的信息。
2. 不要逐项复述图表，要凝练传播判断。
3. 如果某类数据不足，请在 data_limits 说明。
4. 输出必须是 JSON 对象，字段不可增减：
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

市场看板结构化数据：
{{market_context_json}}
"""


def pick_keys(payload: dict[str, Any] | None, keys: list[str]) -> dict[str, Any]:
    source = payload or {}
    return {key: source.get(key) for key in keys}


def build_market_report_context(dashboard: dict[str, Any]) -> dict[str, Any]:
    event = dashboard.get("event") or {}
    metrics = dashboard.get("overview_metrics") or {}
    rhythm_summary = (dashboard.get("volume_rhythm") or {}).get("summary") or {}
    subject_story = dashboard.get("subject_story") or {}
    platform_story = dashboard.get("platform_story") or {}
    comment_quality = dashboard.get("comment_quality") or {}
    regional_story = dashboard.get("regional_response_story") or {}
    topic_story = dashboard.get("topic_spread_story") or {}

    return {
        "event_overview": pick_keys(
            event,
            [
                "event_id",
                "event_name",
                "brand_name",
                "model_name",
                "event_type",
                "event_status",
                "start_time",
                "end_time",
            ],
        ),
        "scale": pick_keys(
            metrics,
            ["total_volume", "content_count", "comment_count", "kol_count", "kol_content_count", "total_engagement"],
        ),
        "rhythm": pick_keys(
            rhythm_summary,
            [
                "rhythm_type",
                "total_volume",
                "active_days",
                "peak_date",
                "peak_volume",
                "peak_volume_rate",
                "has_secondary_peak",
                "secondary_peak_count",
                "rule_based_conclusion",
            ],
        ),
        "hot_topics": {
            "summary": pick_keys(
                topic_story.get("summary"),
                [
                    "top_topic",
                    "topic_count",
                    "top_topic_content_count",
                    "top_topic_comment_count",
                    "top_topic_effective_comment_rate",
                    "top_topic_purchase_signal_rate",
                    "rule_based_conclusion",
                ],
            ),
            "topics": (topic_story.get("topics") or [])[:10],
        },
        "kol_and_authors": {
            "summary": pick_keys(
                subject_story.get("summary"),
                [
                    "subject_pattern",
                    "dominant_subject_type",
                    "dominant_subject_engagement_rate",
                    "kol_engagement_rate",
                    "top_kol_type",
                    "rule_based_conclusion",
                ],
            ),
            "top_authors": (subject_story.get("top_authors") or [])[:5],
            "kol_type_distribution": dashboard.get("kol_type_distribution") or [],
        },
        "audience": {
            "user_profile_distribution": dashboard.get("user_profile_distribution") or [],
        },
        "feedback_quality": {
            "summary": pick_keys(
                comment_quality.get("summary"),
                [
                    "labeled_comment_count",
                    "vehicle_related_count",
                    "vehicle_related_rate",
                    "top_aspect",
                    "top_intent",
                    "positive_rate",
                    "negative_rate",
                    "mid_high_purchase_signal_count",
                    "mid_high_purchase_signal_rate",
                    "rule_based_conclusion",
                ],
            ),
            "sentiment_distribution": comment_quality.get("sentiment_distribution") or [],
            "purchase_signal_distribution": comment_quality.get("purchase_signal_distribution") or [],
        },
        "platform": {
            "summary": pick_keys(
                platform_story.get("summary"),
                [
                    "core_platform",
                    "core_platform_volume_rate",
                    "core_platform_effective_comment_rate",
                    "core_platform_purchase_signal_rate",
                    "core_platform_engagement_per_content",
                    "rule_based_conclusion",
                ],
            ),
            "platform_efficiency": (platform_story.get("platform_efficiency") or [])[:5],
        },
        "regional_response": pick_keys(
            regional_story.get("summary"),
            ["top_location", "top_location_comment_rate", "top_location_effective_comment_rate", "data_scope", "rule_based_conclusion"],
        ),
        "evidence": {
            "hot_posts": (dashboard.get("hot_posts") or [])[:5],
        },
    }


def render_market_report_prompt(template: str, market_context: dict[str, Any]) -> str:
    context_json = json.dumps(market_context, ensure_ascii=False, indent=2, default=str)
    base_prompt = template or DEFAULT_MARKET_REPORT_PROMPT
    if "{{market_context_json}}" in base_prompt:
        rendered = base_prompt.replace("{{market_context_json}}", context_json)
    else:
        rendered = f"{base_prompt.rstrip()}\n\n市场看板结构化数据：\n{context_json}\n"
    if "只使用给定信息" not in rendered:
        rendered = f"请只使用给定信息，不要编造数据。\n{rendered}"
    return rendered


def normalize_market_report_summary(payload: dict[str, Any]) -> dict[str, str]:
    return {field: str(payload.get(field) or "").strip() for field in MARKET_REPORT_FIELDS}


def resolve_market_report_prompt(database_url: str = DATABASE_URL) -> tuple[str, str]:
    try:
        prompt_row = get_default_prompt_template(MARKET_REPORT_PROMPT_SCENE, database_url=database_url)
    except ValueError:
        return DEFAULT_MARKET_REPORT_PROMPT, DEFAULT_MARKET_REPORT_PROMPT_VERSION
    return str(prompt_row.get("prompt_content") or DEFAULT_MARKET_REPORT_PROMPT), str(
        prompt_row.get("prompt_version") or DEFAULT_MARKET_REPORT_PROMPT_VERSION
    )


def run_market_report_agent(
    event_id: str,
    *,
    database_url: str = DATABASE_URL,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    dashboard = get_voc_event_market_dashboard(event_id, database_url=database_url)
    if not dashboard.get("event"):
        raise ValueError("未找到事件数据，无法生成市场部 AI 摘要。")

    context = build_market_report_context(dashboard)
    prompt_template, prompt_version = resolve_market_report_prompt(database_url)
    prompt = render_market_report_prompt(prompt_template, context)

    runtime_config = get_runtime_ai_config(database_url) if not (base_url and api_key and model and timeout_seconds) else {}
    resolved_base_url = base_url or runtime_config.get("base_url") or ""
    resolved_api_key = api_key or runtime_config.get("api_key") or ""
    resolved_model = model or runtime_config.get("model_name") or ""
    resolved_timeout = int(timeout_seconds or runtime_config.get("timeout_seconds") or 60)

    llm_result = call_openai_compatible_json(
        prompt,
        base_url=resolved_base_url,
        api_key=resolved_api_key,
        model=resolved_model,
        timeout_seconds=resolved_timeout,
    )
    return {
        "event_id": event_id,
        "prompt_version": prompt_version,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": normalize_market_report_summary(llm_result),
        "context": context,
        "rendered_prompt": prompt,
    }
