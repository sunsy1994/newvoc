from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from app.config import DATABASE_URL
from app.services.comment_user_ai_profile import call_openai_compatible_json
from app.services.event_voc_insights import get_voc_event_market_dashboard, get_voc_event_product_dashboard, get_voc_event_sales_dashboard
from app.services.report_visuals import (
    build_market_report_charts,
    build_product_report_charts,
    build_sales_report_charts,
    has_renderable_data,
    normalize_report_chart_data,
)
from app.services.system_settings import (
    MARKET_REPORT_PROMPT_CONTENT,
    MARKET_REPORT_PROMPT_VERSION,
    PRODUCT_REPORT_PROMPT_CONTENT,
    PRODUCT_REPORT_PROMPT_VERSION,
    SALES_REPORT_PROMPT_CONTENT,
    SALES_REPORT_PROMPT_VERSION,
    get_default_prompt_template,
    get_runtime_ai_config,
)


MARKET_REPORT_PROMPT_SCENE = "market_report_summary"
PRODUCT_REPORT_PROMPT_SCENE = "product_report_summary"
SALES_REPORT_PROMPT_SCENE = "sales_report_summary"
DEFAULT_MARKET_REPORT_PROMPT_VERSION = MARKET_REPORT_PROMPT_VERSION
DEFAULT_PRODUCT_REPORT_PROMPT_VERSION = PRODUCT_REPORT_PROMPT_VERSION
DEFAULT_SALES_REPORT_PROMPT_VERSION = SALES_REPORT_PROMPT_VERSION
DEFAULT_MARKET_REPORT_PROMPT = MARKET_REPORT_PROMPT_CONTENT
DEFAULT_PRODUCT_REPORT_PROMPT = PRODUCT_REPORT_PROMPT_CONTENT
DEFAULT_SALES_REPORT_PROMPT = SALES_REPORT_PROMPT_CONTENT
MARKET_REPORT_SECTION_CODES = ("market_rhythm", "market_topics", "market_platforms", "market_feedback")
PRODUCT_REPORT_SECTION_CODES = (
    "product_focus",
    "product_sentiment",
    "product_opportunity",
    "product_pko_relationships",
    "product_pko_results",
)
SALES_REPORT_SECTION_CODES = ("sales_funnel", "sales_signals", "sales_intents", "sales_sources")
MARKET_REPORT_CHART_SECTIONS = {
    "market-volume-trend": "market_rhythm",
    "market-hot-topics": "market_topics",
    "market-platform-efficiency": "market_platforms",
    "market-feedback-sentiment": "market_feedback",
}
PRODUCT_REPORT_CHART_SECTIONS = {
    "product-focus": "product_focus",
    "product-sentiment": "product_sentiment",
    "product-opportunity": "product_opportunity",
    "product-pko-evidence": "product_pko_relationships",
    "product-pko-matrix": "product_pko_results",
}
SALES_REPORT_CHART_SECTIONS = {
    "sales-lead-funnel": "sales_funnel",
    "sales-purchase-signals": "sales_signals",
    "sales-intents": "sales_intents",
    "sales-source-efficiency": "sales_sources",
}
MAX_REPORT_HEADLINE_LENGTH = 120
MAX_REPORT_EXECUTIVE_SUMMARY_LENGTH = 1200
MAX_REPORT_SECTION_INSIGHT_LENGTH = 600
MAX_REPORT_DATA_NOTE_LENGTH = 300
MAX_REPORT_DATA_NOTES = 10
EMPTY_REPORT_HEADLINE = "暂无可用报告数据"
EMPTY_REPORT_EXECUTIVE_SUMMARY = "当前数据不足，无法生成可靠报告结论。"
REPORT_PROMPT_CONTRACT_MARKER = "[AUTO_VOC_FIXED_NARRATIVE_V2_CONTRACT]"
MARKET_REPORT_CHART_CONTRACT = (
    ("market-volume-trend", "F3", "传播规模与节奏", "按日声量变化", "volume_trend"),
    ("market-hot-topics", "F5", "热门话题结构", "按讨论量展示", "hot_topics.topics"),
    ("market-platform-efficiency", "F8", "平台传播效率", "规模与反馈效率", "platform.platform_efficiency"),
    ("market-feedback-sentiment", "L14", "用户反馈构成", "情感分布", "feedback_quality.sentiment_distribution"),
)
PRODUCT_REPORT_CHART_CONTRACT = (
    ("product-focus", "F5", "产品关注点", "按提及占比展示", "product_focus.aspects"),
    ("product-sentiment", "F6", "产品点正负反馈", "正向与负向反馈率", "product_focus.aspects"),
    ("product-opportunity", "F5", "机会、风险与转化", "系统计算的机会分", "product_opportunity"),
    ("product-pko-evidence", "L12", "PKO 车系与对比维度", "每条线对应一条真实评论", "pko.evidence_comments"),
    ("product-pko-matrix", "F7", "PKO 维度结果明细", "优势、劣势与中性结果", "pko.dimension_result_matrix"),
)
SALES_REPORT_CHART_CONTRACT = (
    ("sales-lead-funnel", "L13", "线索转化漏斗", "固定转化阶段", "lead_quality.summary"),
    ("sales-purchase-signals", "F4", "购买信号结构", "强、中、弱及未标注信号", "lead_quality.purchase_signal_distribution"),
    ("sales-intents", "F5", "用户意图分布", "评论数与占比", "lead_quality.intent_distribution"),
    ("sales-source-efficiency", "F6", "渠道线索效率", "总反馈量与销售线索量", "lead_source.platform_efficiency"),
)
REPORT_CACHE_CONTRACTS = (
    (
        DEFAULT_MARKET_REPORT_PROMPT_VERSION,
        MARKET_REPORT_SECTION_CODES,
        MARKET_REPORT_CHART_CONTRACT,
    ),
    (
        DEFAULT_PRODUCT_REPORT_PROMPT_VERSION,
        PRODUCT_REPORT_SECTION_CODES,
        PRODUCT_REPORT_CHART_CONTRACT,
    ),
    (
        DEFAULT_SALES_REPORT_PROMPT_VERSION,
        SALES_REPORT_SECTION_CODES,
        SALES_REPORT_CHART_CONTRACT,
    ),
)

MARKET_REPORT_CACHE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS data_asset;
CREATE TABLE IF NOT EXISTS data_asset.market_report_agent_run (
    report_run_id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary_json JSONB NOT NULL,
    context_json JSONB NOT NULL,
    rendered_prompt TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_market_report_agent_run_event_time
    ON data_asset.market_report_agent_run (event_id, generated_at DESC, report_run_id DESC);
"""

PRODUCT_REPORT_CACHE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS data_asset;
CREATE TABLE IF NOT EXISTS data_asset.product_report_agent_run (
    report_run_id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary_json JSONB NOT NULL,
    context_json JSONB NOT NULL,
    rendered_prompt TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_product_report_agent_run_event_time
    ON data_asset.product_report_agent_run (event_id, generated_at DESC, report_run_id DESC);
"""

SALES_REPORT_CACHE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS data_asset;
CREATE TABLE IF NOT EXISTS data_asset.sales_report_agent_run (
    report_run_id BIGSERIAL PRIMARY KEY,
    event_id TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    summary_json JSONB NOT NULL,
    context_json JSONB NOT NULL,
    rendered_prompt TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sales_report_agent_run_event_time
    ON data_asset.sales_report_agent_run (event_id, generated_at DESC, report_run_id DESC);
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
            ["event_id", "event_name", "brand_name", "model_name", "event_type", "event_status", "start_time", "end_time"],
        ),
        "scale": pick_keys(metrics, ["total_volume", "content_count", "comment_count", "kol_count", "kol_content_count", "total_engagement"]),
        "volume_trend": [
            pick_keys(item, ["date", "content_count", "comment_count", "total_volume"])
            for item in (dashboard.get("volume_trend") or [])[:30]
        ],
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
        "audience": {"user_profile_distribution": dashboard.get("user_profile_distribution") or []},
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
        "evidence": {"hot_posts": (dashboard.get("hot_posts") or [])[:5]},
    }


def build_product_report_context(dashboard: dict[str, Any]) -> dict[str, Any]:
    event = dashboard.get("event") or {}
    focus_story = dashboard.get("product_focus_story") or {}
    opportunity_story = dashboard.get("product_opportunity_story") or {}
    pko_story = dashboard.get("product_pko_story") or {}
    evidence_comments = []
    pko_evidence = [
        item
        for item in (pko_story.get("evidence_comments") or [])
        if isinstance(item, dict)
        and str(item.get("comment_id") or "").strip()
        and str(item.get("comment_text") or "").strip()
    ][:50]

    for item in pko_evidence:
        evidence_comments.append(item)
    for aspect in focus_story.get("aspects") or []:
        for comment in aspect.get("evidence_comments") or []:
            evidence_comments.append({"aspect": aspect.get("aspect"), **comment})

    return {
        "event_overview": pick_keys(
            event,
            ["event_id", "event_name", "brand_name", "model_name", "event_type", "event_status", "start_time", "end_time"],
        ),
        "product_focus": {
            "summary": focus_story.get("summary") or {},
            "aspects": (focus_story.get("aspects") or [])[:10],
        },
        "product_opportunity": {
            "summary": opportunity_story.get("summary") or {},
            "surprise_points": (opportunity_story.get("surprise_points") or [])[:5],
            "pain_points": (opportunity_story.get("pain_points") or [])[:5],
            "conversion_points": (opportunity_story.get("conversion_points") or [])[:5],
        },
        "pko": {
            "summary": pko_story.get("summary") or {},
            "explicit_target_distribution": (pko_story.get("explicit_target_distribution") or [])[:8],
            "target_distribution": (pko_story.get("target_distribution") or [])[:8],
            "dimension_distribution": (pko_story.get("dimension_distribution") or [])[:8],
            "result_distribution": pko_story.get("result_distribution") or [],
            "dimension_result_matrix": (pko_story.get("dimension_result_matrix") or [])[:8],
            "evidence_comments": pko_evidence,
        },
        "evidence_comments": evidence_comments[:50],
    }


def build_sales_report_context(dashboard: dict[str, Any]) -> dict[str, Any]:
    event = dashboard.get("event") or {}
    lead_quality = dashboard.get("sales_lead_quality") or {}
    lead_source = dashboard.get("sales_lead_source_efficiency") or {}
    recommended_users = []

    for segment in lead_quality.get("profile_segments") or []:
        for user in segment.get("users") or []:
            recommended_users.append(
                {
                    "segment_id": segment.get("segment_id"),
                    "segment_label": segment.get("label"),
                    "comment_user_id": user.get("comment_user_id"),
                    "nickname": user.get("nickname"),
                    "platform": user.get("platform"),
                    "purchase_signal": user.get("purchase_signal"),
                    "profile_status": user.get("profile_status"),
                    "representative_comment": user.get("representative_comment"),
                }
            )

    return {
        "event_overview": pick_keys(
            event,
            ["event_id", "event_name", "brand_name", "model_name", "event_type", "event_status", "start_time", "end_time"],
        ),
        "lead_quality": {
            "summary": lead_quality.get("summary") or {},
            "intent_distribution": lead_quality.get("intent_distribution") or [],
            "purchase_signal_distribution": lead_quality.get("purchase_signal_distribution") or [],
            "profile_segments": (lead_quality.get("profile_segments") or [])[:8],
            "evidence_comments": (lead_quality.get("evidence_comments") or [])[:8],
        },
        "lead_source": {
            "summary": lead_source.get("summary") or {},
            "platform_efficiency": (lead_source.get("platform_efficiency") or [])[:8],
            "content_leads": (lead_source.get("content_leads") or [])[:8],
            "lead_comments": (lead_source.get("lead_comments") or [])[:10],
        },
        "recommended_follow_up_users": recommended_users[:10],
    }


def render_report_prompt(template: str, context: dict[str, Any], placeholder: str, fallback_prompt: str, context_title: str) -> str:
    context_json = json.dumps(context, ensure_ascii=False, indent=2, default=str)
    base_prompt = template or fallback_prompt
    if placeholder in base_prompt:
        rendered = base_prompt.replace(placeholder, context_json)
    else:
        rendered = f"{base_prompt.rstrip()}\n\n{context_title}：\n{context_json}\n"
    if "只使用给定信息" not in rendered and "只基于给定" not in rendered:
        rendered = f"请只使用给定信息，不要编造数据。\n{rendered}"
    return rendered


def render_market_report_prompt(template: str, market_context: dict[str, Any]) -> str:
    return render_report_prompt(template, market_context, "{{market_context_json}}", DEFAULT_MARKET_REPORT_PROMPT, "市场看板结构化数据")


def render_product_report_prompt(template: str, product_context: dict[str, Any]) -> str:
    return render_report_prompt(template, product_context, "{{product_context_json}}", DEFAULT_PRODUCT_REPORT_PROMPT, "产品看板结构化数据")


def render_sales_report_prompt(template: str, sales_context: dict[str, Any]) -> str:
    rendered = render_report_prompt(template, sales_context, "{{sales_context_json}}", DEFAULT_SALES_REPORT_PROMPT, "销售看板结构化数据")
    if "只使用给定信息" not in rendered:
        rendered = f"请只使用给定信息，不要编造数据。\n{rendered}"
    return rendered


def _bounded_text(value: Any, max_length: int) -> str:
    return value.strip()[:max_length] if isinstance(value, str) else ""


def normalize_data_notes(value: Any) -> list[str]:
    raw_notes = [value] if isinstance(value, str) else value if isinstance(value, list) else []
    notes = [
        note
        for item in raw_notes
        if (note := _bounded_text(item, MAX_REPORT_DATA_NOTE_LENGTH))
    ]
    return notes[:MAX_REPORT_DATA_NOTES]


def normalize_report_narrative(
    payload: dict[str, Any],
    section_codes: tuple[str, ...],
    fallback_insights: dict[str, str],
) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    raw_insights = raw.get("section_insights") if isinstance(raw.get("section_insights"), dict) else {}
    return {
        "headline": _bounded_text(raw.get("headline"), MAX_REPORT_HEADLINE_LENGTH),
        "executive_summary": _bounded_text(
            raw.get("executive_summary"),
            MAX_REPORT_EXECUTIVE_SUMMARY_LENGTH,
        ),
        "section_insights": {
            code: _bounded_text(
                raw_insights.get(code),
                MAX_REPORT_SECTION_INSIGHT_LENGTH,
            )
            or _bounded_text(
                fallback_insights.get(code),
                MAX_REPORT_SECTION_INSIGHT_LENGTH,
            )
            for code in section_codes
        },
        "data_notes": normalize_data_notes(raw.get("data_notes")),
    }


def normalize_market_report_summary(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    return {
        "report_markdown": _bounded_text(raw.get("report_markdown"), 200_000),
        "data_notes": normalize_data_notes(raw.get("data_notes")),
    }


def _rule_based_conclusion(section: Any) -> str:
    return (
        _bounded_text(
            section.get("rule_based_conclusion"),
            MAX_REPORT_SECTION_INSIGHT_LENGTH,
        )
        if isinstance(section, dict)
        else ""
    )


def _market_fallback_insights(context: dict[str, Any]) -> dict[str, str]:
    hot_topics = context.get("hot_topics") or {}
    platform = context.get("platform") or {}
    feedback = context.get("feedback_quality") or {}
    return {
        "market_rhythm": _rule_based_conclusion(context.get("rhythm")),
        "market_topics": _rule_based_conclusion(hot_topics.get("summary")),
        "market_platforms": _rule_based_conclusion(platform.get("summary")),
        "market_feedback": _rule_based_conclusion(feedback.get("summary")),
    }


def _product_fallback_insights(context: dict[str, Any]) -> dict[str, str]:
    focus = context.get("product_focus") or {}
    opportunity = context.get("product_opportunity") or {}
    pko = context.get("pko") or {}
    focus_conclusion = _rule_based_conclusion(focus.get("summary"))
    pko_conclusion = _rule_based_conclusion(pko.get("summary"))
    return {
        "product_focus": focus_conclusion,
        "product_sentiment": focus_conclusion,
        "product_opportunity": _rule_based_conclusion(opportunity.get("summary")),
        "product_pko_relationships": pko_conclusion,
        "product_pko_results": pko_conclusion,
    }


def _sales_fallback_insights(context: dict[str, Any]) -> dict[str, str]:
    lead_quality = context.get("lead_quality") or {}
    lead_source = context.get("lead_source") or {}
    quality_conclusion = _rule_based_conclusion(lead_quality.get("summary"))
    return {
        "sales_funnel": quality_conclusion,
        "sales_signals": quality_conclusion,
        "sales_intents": quality_conclusion,
        "sales_sources": _rule_based_conclusion(lead_source.get("summary")),
    }


def build_report_summary(
    payload: dict[str, Any],
    charts: list[dict[str, Any]],
    section_codes: tuple[str, ...],
    fallback_insights: dict[str, str],
    chart_sections: dict[str, str],
) -> dict[str, Any]:
    narrative = normalize_report_narrative(payload, section_codes, fallback_insights)
    normalized_charts = []
    for chart in charts:
        item = dict(chart)
        section_code = chart_sections.get(str(item.get("chart_id") or ""))
        chart_has_data = has_renderable_data(item)
        insight = (
            narrative["section_insights"].get(section_code or "", "")
            if chart_has_data
            else fallback_insights.get(section_code or "", "")
        )
        item["insight"] = _bounded_text(insight, MAX_REPORT_SECTION_INSIGHT_LENGTH)
        if section_code and not chart_has_data:
            narrative["section_insights"][section_code] = item["insight"]
        normalized_charts.append(item)
    if not any(has_renderable_data(chart) for chart in normalized_charts):
        narrative["headline"] = EMPTY_REPORT_HEADLINE
        narrative["executive_summary"] = EMPTY_REPORT_EXECUTIVE_SUMMARY
        narrative["section_insights"] = {
            code: _bounded_text(
                fallback_insights.get(code),
                MAX_REPORT_SECTION_INSIGHT_LENGTH,
            )
            for code in section_codes
        }
    return {
        "report_narrative": narrative,
        "structured_report": {"charts": normalized_charts},
    }


def ensure_report_prompt_contract(
    prompt_content: str,
    section_codes: tuple[str, ...],
) -> str:
    contract = {
        "headline": "",
        "executive_summary": "",
        "section_insights": {code: "" for code in section_codes},
        "data_notes": [],
    }
    suffix = (
        f"{REPORT_PROMPT_CONTRACT_MARKER}\n"
        "保留以上业务要求，但最终只输出下面固定结构的 JSON 对象；"
        "不得输出 report_markdown、structured_report 或图表数据。"
        "图表类型和数值由系统固定，输入缺失时不得推断。\n"
        f"{json.dumps(contract, ensure_ascii=False, indent=2)}"
    )
    if prompt_content.rstrip().endswith(suffix):
        return prompt_content
    return f"{prompt_content.rstrip()}\n\n{suffix}"


def resolve_report_prompt(
    scene: str,
    default_prompt: str,
    default_version: str,
    section_codes: tuple[str, ...],
    database_url: str = DATABASE_URL,
) -> tuple[str, str]:
    try:
        prompt_row = get_default_prompt_template(scene, database_url=database_url)
    except ValueError:
        return default_prompt, default_version
    prompt_content = _bounded_text(prompt_row.get("prompt_content"), 200_000)
    prompt_version = _bounded_text(prompt_row.get("prompt_version"), 200) or default_version
    if not prompt_content:
        return default_prompt, default_version
    if prompt_content == default_prompt.strip():
        return prompt_content, prompt_version
    return ensure_report_prompt_contract(prompt_content, section_codes), prompt_version


def resolve_market_report_prompt(database_url: str = DATABASE_URL) -> tuple[str, str]:
    return resolve_report_prompt(
        MARKET_REPORT_PROMPT_SCENE,
        DEFAULT_MARKET_REPORT_PROMPT,
        DEFAULT_MARKET_REPORT_PROMPT_VERSION,
        MARKET_REPORT_SECTION_CODES,
        database_url,
    )


def resolve_product_report_prompt(database_url: str = DATABASE_URL) -> tuple[str, str]:
    return resolve_report_prompt(
        PRODUCT_REPORT_PROMPT_SCENE,
        DEFAULT_PRODUCT_REPORT_PROMPT,
        DEFAULT_PRODUCT_REPORT_PROMPT_VERSION,
        PRODUCT_REPORT_SECTION_CODES,
        database_url,
    )


def resolve_sales_report_prompt(database_url: str = DATABASE_URL) -> tuple[str, str]:
    return resolve_report_prompt(
        SALES_REPORT_PROMPT_SCENE,
        DEFAULT_SALES_REPORT_PROMPT,
        DEFAULT_SALES_REPORT_PROMPT_VERSION,
        SALES_REPORT_SECTION_CODES,
        database_url,
    )


def ensure_report_agent_table(conn: psycopg.Connection, table_sql: str) -> None:
    with conn.cursor() as cur:
        cur.execute(table_sql)


def _valid_cached_chart(
    chart: Any,
    expected_chart_id: str,
    expected_template_id: str,
    expected_title: str,
    expected_subtitle: str,
    expected_source_label: str,
) -> bool:
    if not isinstance(chart, dict):
        return False
    if (
        chart.get("chart_id") != expected_chart_id
        or chart.get("template_id") != expected_template_id
        or chart.get("title") != expected_title
        or chart.get("subtitle") != expected_subtitle
        or chart.get("source_label") != expected_source_label
    ):
        return False
    if not all(
        isinstance(chart.get(field), str)
        for field in ("title", "subtitle", "insight", "source_label")
    ):
        return False
    data = chart.get("data")
    meta = chart.get("meta")
    if not (
        isinstance(data, list)
        and all(isinstance(row, dict) for row in data)
        and isinstance(meta, dict)
    ):
        return False
    if normalize_report_chart_data(expected_template_id, data) != data:
        return False
    if has_renderable_data(chart):
        return True
    return (
        data == []
        and isinstance(meta.get("empty_reason"), str)
        and bool(meta["empty_reason"].strip())
    )


def _cached_report_contract(
    prompt_version: str,
    narrative: Any,
    charts: Any,
) -> tuple[str, ...] | None:
    if not isinstance(narrative, dict) or not isinstance(charts, list):
        return None
    known_contract = next(
        (
            contract
            for contract in REPORT_CACHE_CONTRACTS
            if prompt_version == contract[0]
        ),
        None,
    )
    candidates = (known_contract,) if known_contract else REPORT_CACHE_CONTRACTS
    for _, section_codes, chart_contract in candidates:
        if known_contract or [
            (chart.get("chart_id"), chart.get("template_id"))
            for chart in charts
            if isinstance(chart, dict)
        ] == [(expected[0], expected[1]) for expected in chart_contract]:
            if len(charts) != len(chart_contract) or not all(
                _valid_cached_chart(chart, *expected)
                for chart, expected in zip(charts, chart_contract)
            ):
                continue
            raw_insights = narrative.get("section_insights")
            if not (
                isinstance(narrative.get("headline"), str)
                and isinstance(narrative.get("executive_summary"), str)
                and isinstance(raw_insights, dict)
                and set(raw_insights) == set(section_codes)
                and all(isinstance(raw_insights.get(code), str) for code in section_codes)
                and isinstance(narrative.get("data_notes"), list)
                and all(isinstance(note, str) for note in narrative["data_notes"])
            ):
                continue
            return section_codes
    return None


def normalize_cached_report_summary(
    payload: Any,
    prompt_version: str = "",
) -> dict[str, Any]:
    raw = payload if isinstance(payload, dict) else {}
    raw_narrative = raw.get("report_narrative")
    raw_structured_report = raw.get("structured_report")
    raw_charts = raw_structured_report.get("charts") if isinstance(raw_structured_report, dict) else None
    section_codes = _cached_report_contract(prompt_version, raw_narrative, raw_charts)
    if not section_codes:
        return normalize_market_report_summary(raw)

    summary: dict[str, Any] = {}
    summary["report_narrative"] = normalize_report_narrative(raw_narrative, section_codes, {})
    structured_report = dict(raw_structured_report)
    structured_report["charts"] = []
    for chart in raw_charts:
        item = dict(chart)
        item["insight"] = _bounded_text(
            item.get("insight"),
            MAX_REPORT_SECTION_INSIGHT_LENGTH,
        )
        structured_report["charts"].append(item)
    summary["structured_report"] = structured_report

    if "report_markdown" in raw:
        summary["report_markdown"] = _bounded_text(raw.get("report_markdown"), 200_000)
    if "data_notes" in raw:
        summary["data_notes"] = normalize_data_notes(raw.get("data_notes"))
    return summary


def normalize_cached_report_row(row: dict[str, Any]) -> dict[str, Any]:
    generated_at = row.get("generated_at")
    generated_at_value = generated_at.isoformat(timespec="seconds") if isinstance(generated_at, datetime) else str(generated_at or "")
    prompt_version = _bounded_text(row.get("prompt_version"), 200)
    return {
        "event_id": row.get("event_id"),
        "prompt_version": prompt_version,
        "generated_at": generated_at_value,
        "summary": normalize_cached_report_summary(
            row.get("summary_json"),
            prompt_version,
        ),
        "context": row.get("context_json") or {},
        "rendered_prompt": row.get("rendered_prompt") or "",
    }


def save_report_agent_result(result: dict[str, Any], table_name: str, table_sql: str, database_url: str = DATABASE_URL) -> dict[str, Any]:
    with psycopg.connect(database_url) as conn:
        ensure_report_agent_table(conn, table_sql)
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                INSERT INTO data_asset.{table_name}
                    (event_id, prompt_version, generated_at, summary_json, context_json, rendered_prompt)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING event_id, prompt_version, generated_at, summary_json, context_json, rendered_prompt
                """,
                (
                    result["event_id"],
                    result["prompt_version"],
                    result.get("generated_at"),
                    Jsonb(result.get("summary") or {}),
                    Jsonb(result.get("context") or {}),
                    result.get("rendered_prompt") or "",
                ),
            )
            row = cur.fetchone()
        conn.commit()
    return normalize_cached_report_row(dict(row))


def get_latest_report_agent_result(event_id: str, table_name: str, table_sql: str, database_url: str = DATABASE_URL) -> dict[str, Any] | None:
    with psycopg.connect(database_url) as conn:
        ensure_report_agent_table(conn, table_sql)
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(
                f"""
                SELECT event_id, prompt_version, generated_at, summary_json, context_json, rendered_prompt
                FROM data_asset.{table_name}
                WHERE event_id = %s
                ORDER BY generated_at DESC, report_run_id DESC
                LIMIT 1
                """,
                (event_id,),
            )
            row = cur.fetchone()
    return normalize_cached_report_row(dict(row)) if row else None


def save_market_report_agent_result(result: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    return save_report_agent_result(result, "market_report_agent_run", MARKET_REPORT_CACHE_TABLE_SQL, database_url)


def get_latest_market_report_agent_result(event_id: str, database_url: str = DATABASE_URL) -> dict[str, Any] | None:
    return get_latest_report_agent_result(event_id, "market_report_agent_run", MARKET_REPORT_CACHE_TABLE_SQL, database_url)


def save_product_report_agent_result(result: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    return save_report_agent_result(result, "product_report_agent_run", PRODUCT_REPORT_CACHE_TABLE_SQL, database_url)


def get_latest_product_report_agent_result(event_id: str, database_url: str = DATABASE_URL) -> dict[str, Any] | None:
    return get_latest_report_agent_result(event_id, "product_report_agent_run", PRODUCT_REPORT_CACHE_TABLE_SQL, database_url)


def save_sales_report_agent_result(result: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    return save_report_agent_result(result, "sales_report_agent_run", SALES_REPORT_CACHE_TABLE_SQL, database_url)


def get_latest_sales_report_agent_result(event_id: str, database_url: str = DATABASE_URL) -> dict[str, Any] | None:
    return get_latest_report_agent_result(event_id, "sales_report_agent_run", SALES_REPORT_CACHE_TABLE_SQL, database_url)


def resolve_runtime_config(
    database_url: str,
    base_url: str | None,
    api_key: str | None,
    model: str | None,
    timeout_seconds: int | None,
) -> tuple[str, str, str, int]:
    runtime_config = get_runtime_ai_config(database_url) if not (base_url and api_key and model and timeout_seconds) else {}
    return (
        base_url or runtime_config.get("base_url") or "",
        api_key or runtime_config.get("api_key") or "",
        model or runtime_config.get("model_name") or "",
        int(timeout_seconds or runtime_config.get("timeout_seconds") or 60),
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
    resolved_base_url, resolved_api_key, resolved_model, resolved_timeout = resolve_runtime_config(
        database_url, base_url, api_key, model, timeout_seconds
    )
    llm_result = call_openai_compatible_json(
        prompt,
        base_url=resolved_base_url,
        api_key=resolved_api_key,
        model=resolved_model,
        timeout_seconds=resolved_timeout,
    )
    result = {
        "event_id": event_id,
        "prompt_version": prompt_version,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": build_report_summary(
            llm_result,
            build_market_report_charts(context),
            MARKET_REPORT_SECTION_CODES,
            _market_fallback_insights(context),
            MARKET_REPORT_CHART_SECTIONS,
        ),
        "context": context,
        "rendered_prompt": prompt,
    }
    return save_market_report_agent_result(result, database_url=database_url)


def run_product_report_agent(
    event_id: str,
    *,
    database_url: str = DATABASE_URL,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    dashboard = get_voc_event_product_dashboard(event_id, database_url=database_url)
    if not dashboard.get("event"):
        raise ValueError("未找到事件数据，无法生成产品部 AI 摘要。")

    context = build_product_report_context(dashboard)
    prompt_template, prompt_version = resolve_product_report_prompt(database_url)
    prompt = render_product_report_prompt(prompt_template, context)
    resolved_base_url, resolved_api_key, resolved_model, resolved_timeout = resolve_runtime_config(
        database_url, base_url, api_key, model, timeout_seconds
    )
    llm_result = call_openai_compatible_json(
        prompt,
        base_url=resolved_base_url,
        api_key=resolved_api_key,
        model=resolved_model,
        timeout_seconds=resolved_timeout,
    )
    result = {
        "event_id": event_id,
        "prompt_version": prompt_version,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": build_report_summary(
            llm_result,
            build_product_report_charts(context),
            PRODUCT_REPORT_SECTION_CODES,
            _product_fallback_insights(context),
            PRODUCT_REPORT_CHART_SECTIONS,
        ),
        "context": context,
        "rendered_prompt": prompt,
    }
    return save_product_report_agent_result(result, database_url=database_url)


def run_sales_report_agent(
    event_id: str,
    *,
    database_url: str = DATABASE_URL,
    base_url: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    dashboard = get_voc_event_sales_dashboard(event_id, database_url=database_url)
    if not dashboard.get("event"):
        raise ValueError("No sales dashboard event data found.")

    context = build_sales_report_context(dashboard)
    prompt_template, prompt_version = resolve_sales_report_prompt(database_url)
    prompt = render_sales_report_prompt(prompt_template, context)
    resolved_base_url, resolved_api_key, resolved_model, resolved_timeout = resolve_runtime_config(
        database_url, base_url, api_key, model, timeout_seconds
    )
    llm_result = call_openai_compatible_json(
        prompt,
        base_url=resolved_base_url,
        api_key=resolved_api_key,
        model=resolved_model,
        timeout_seconds=resolved_timeout,
    )
    result = {
        "event_id": event_id,
        "prompt_version": prompt_version,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": build_report_summary(
            llm_result,
            build_sales_report_charts(context),
            SALES_REPORT_SECTION_CODES,
            _sales_fallback_insights(context),
            SALES_REPORT_CHART_SECTIONS,
        ),
        "context": context,
        "rendered_prompt": prompt,
    }
    return save_sales_report_agent_result(result, database_url=database_url)
