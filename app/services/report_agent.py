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
from app.services.system_settings import get_default_prompt_template, get_runtime_ai_config


MARKET_REPORT_PROMPT_SCENE = "market_report_summary"
PRODUCT_REPORT_PROMPT_SCENE = "product_report_summary"
SALES_REPORT_PROMPT_SCENE = "sales_report_summary"
DEFAULT_MARKET_REPORT_PROMPT_VERSION = "market_report_summary_v1"
DEFAULT_PRODUCT_REPORT_PROMPT_VERSION = "product_report_summary_v1"
DEFAULT_SALES_REPORT_PROMPT_VERSION = "sales_report_summary_v1"
MARKET_REPORT_FIELDS = ["report_markdown", "data_notes"]

DEFAULT_MARKET_REPORT_PROMPT = """你是汽车行业 VOC 市场分析助手。请只基于给定的市场看板结构化数据，生成市场部视角的 Markdown 事件报告。

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

DEFAULT_PRODUCT_REPORT_PROMPT = """你是汽车行业 VOC 产品分析助手。请只基于给定的产品看板结构化数据，生成产品部视角的 Markdown 事件报告。

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

DEFAULT_SALES_REPORT_PROMPT = """你是汽车行业 VOC 销售线索分析助手。请只基于给定的销售看板结构化数据，生成销售部视角的 Markdown 事件报告。

报告目标：
让销售人员快速读懂：这个事件产生了多少可跟进线索，线索质量如何，这些人是什么样的人，来自哪些渠道和内容，哪些用户应优先查看。

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

    for item in pko_story.get("evidence_comments") or []:
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
            "evidence_comments": (pko_story.get("evidence_comments") or [])[:8],
        },
        "evidence_comments": evidence_comments[:12],
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


def normalize_market_report_summary(payload: dict[str, Any]) -> dict[str, Any]:
    raw_notes = payload.get("data_notes") or []
    if isinstance(raw_notes, str):
        data_notes = [raw_notes.strip()] if raw_notes.strip() else []
    elif isinstance(raw_notes, list):
        data_notes = [str(item).strip() for item in raw_notes if str(item).strip()]
    else:
        data_notes = []
    return {"report_markdown": str(payload.get("report_markdown") or "").strip(), "data_notes": data_notes}


def resolve_report_prompt(scene: str, default_prompt: str, default_version: str, database_url: str = DATABASE_URL) -> tuple[str, str]:
    try:
        prompt_row = get_default_prompt_template(scene, database_url=database_url)
    except ValueError:
        return default_prompt, default_version
    return str(prompt_row.get("prompt_content") or default_prompt), str(prompt_row.get("prompt_version") or default_version)


def resolve_market_report_prompt(database_url: str = DATABASE_URL) -> tuple[str, str]:
    return resolve_report_prompt(MARKET_REPORT_PROMPT_SCENE, DEFAULT_MARKET_REPORT_PROMPT, DEFAULT_MARKET_REPORT_PROMPT_VERSION, database_url)


def resolve_product_report_prompt(database_url: str = DATABASE_URL) -> tuple[str, str]:
    return resolve_report_prompt(PRODUCT_REPORT_PROMPT_SCENE, DEFAULT_PRODUCT_REPORT_PROMPT, DEFAULT_PRODUCT_REPORT_PROMPT_VERSION, database_url)


def resolve_sales_report_prompt(database_url: str = DATABASE_URL) -> tuple[str, str]:
    return resolve_report_prompt(SALES_REPORT_PROMPT_SCENE, DEFAULT_SALES_REPORT_PROMPT, DEFAULT_SALES_REPORT_PROMPT_VERSION, database_url)


def ensure_report_agent_table(conn: psycopg.Connection, table_sql: str) -> None:
    with conn.cursor() as cur:
        cur.execute(table_sql)


def normalize_cached_report_row(row: dict[str, Any]) -> dict[str, Any]:
    generated_at = row.get("generated_at")
    generated_at_value = generated_at.isoformat(timespec="seconds") if isinstance(generated_at, datetime) else str(generated_at or "")
    return {
        "event_id": row.get("event_id"),
        "prompt_version": row.get("prompt_version") or "",
        "generated_at": generated_at_value,
        "summary": normalize_market_report_summary(row.get("summary_json") or {}),
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
        "summary": normalize_market_report_summary(llm_result),
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
        "summary": normalize_market_report_summary(llm_result),
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
        "summary": normalize_market_report_summary(llm_result),
        "context": context,
        "rendered_prompt": prompt,
    }
    return save_sales_report_agent_result(result, database_url=database_url)
