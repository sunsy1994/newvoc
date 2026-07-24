from __future__ import annotations

from datetime import datetime
from typing import Any

from app.services.report_visuals import build_event_report_charts, has_renderable_data


MAX_CHART_INSIGHT_LENGTH = 160


def _get(source: dict[str, Any], path: str, default: Any = None) -> Any:
    current: Any = source
    for part in path.split("."):
        if not isinstance(current, dict):
            return default
        current = current.get(part)
    return current if current is not None else default


def _list(source: dict[str, Any], path: str) -> list[dict[str, Any]]:
    value = _get(source, path, [])
    return value if isinstance(value, list) else []


def _event_overview(market_context: dict[str, Any], product_context: dict[str, Any], sales_context: dict[str, Any]) -> dict[str, Any]:
    return (
        _get(market_context, "event_overview", {})
        or _get(product_context, "event_overview", {})
        or _get(sales_context, "event_overview", {})
        or {}
    )


def _evidence_table(market_context: dict[str, Any], product_context: dict[str, Any], sales_context: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for item in _list(market_context, "evidence.hot_posts")[:3]:
        rows.append({"source": "市场热门内容", "text": item.get("title"), "metric": item.get("total_engagement"), "source_path": "market.evidence.hot_posts"})
    for item in _list(product_context, "evidence_comments")[:3]:
        rows.append({"source": f"产品原声/{item.get('aspect') or ''}", "text": item.get("comment_text"), "metric": item.get("interaction_cnt"), "source_path": "product.evidence_comments"})
    for item in _list(sales_context, "lead_source.lead_comments")[:3]:
        rows.append({"source": "销售线索评论", "text": item.get("comment_text"), "metric": item.get("purchase_signal"), "source_path": "sales.lead_source.lead_comments"})
    return {
        "chart_id": "evidence_reference_table",
        "chart_type": "table",
        "title": "关键证据引用",
        "columns": ["source", "text", "metric"],
        "data": [row for row in rows if row.get("text")],
    }


def _evidence_references(charts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references = []
    for row in next((chart.get("data", []) for chart in charts if chart.get("chart_id") == "evidence_reference_table"), []):
        references.append(
            {
                "source": row.get("source"),
                "quote": row.get("text"),
                "metric": row.get("metric"),
                "source_path": row.get("source_path"),
            }
        )
    return references


def _calculation_notes() -> list[dict[str, str]]:
    return [
        {"metric": "总声量", "method": "total_volume = content_count + comment_count，来自市场看板 overview_metrics。"},
        {"metric": "产品关注点声量", "method": "按已标注评论中的 aspect 分组计数，来自产品看板 product_focus.aspects。"},
        {"metric": "中高购买信号", "method": "购买信号为中/强的评论计数或占比，来自销售看板 lead_quality.summary。"},
        {"metric": "证据引用", "method": "仅引用工具返回的热门内容、产品原声和销售线索评论，不改写为用户未表达的内容。"},
    ]


def _first_text(items: list[Any], fallback: str) -> str:
    for item in items:
        text = str(item or "").strip()
        if text:
            return text
    return fallback


def _template_card(title: str, body: str, bullets: list[str], badge: str = "") -> dict[str, Any]:
    return {
        "title": title,
        "badge": badge,
        "body": body,
        "bullets": [item for item in bullets if item][:4],
    }


def _bounded_text(value: Any, limit: int = MAX_CHART_INSIGHT_LENGTH) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


def _event_chart_insights(llm_summary: dict[str, Any]) -> dict[str, str]:
    sections = llm_summary.get("sections")
    if not isinstance(sections, list):
        return {}
    by_view: dict[str, str] = {}
    candidates: list[tuple[str, str]] = []
    for section in sections[:3]:
        if not isinstance(section, dict):
            candidates.append(("", ""))
            continue
        summary = _bounded_text(section.get("summary"))
        if not summary:
            candidates.append(("", ""))
            continue
        title = section.get("title") if isinstance(section.get("title"), str) else ""
        if "市场" in title or "传播" in title:
            view = "market"
        elif "产品" in title:
            view = "product"
        elif "销售" in title or "线索" in title:
            view = "sales"
        else:
            view = ""
        candidates.append((view, summary))
        if view:
            by_view.setdefault(view, summary)
    for index, view in enumerate(("market", "product", "sales")):
        if view not in by_view and index < len(candidates):
            summary = candidates[index][1]
            if summary:
                by_view[view] = summary
    return by_view


def _apply_event_chart_insights(
    charts: list[dict[str, Any]],
    llm_summary: dict[str, Any],
) -> None:
    insights = _event_chart_insights(llm_summary)
    chart_views = ("market", "market", "product", "sales")
    for chart, view in zip(charts, chart_views):
        chart["insight"] = insights.get(view, "") if has_renderable_data(chart) else ""


def _template_sections(
    *,
    structured_report: dict[str, Any],
    market_context: dict[str, Any],
    product_context: dict[str, Any],
    sales_context: dict[str, Any],
) -> list[dict[str, Any]]:
    scale = _get(market_context, "scale", {})
    feedback = _get(market_context, "feedback_quality.summary", {})
    focus = _get(product_context, "product_focus.summary", {})
    lead = _get(sales_context, "lead_quality.summary", {})
    opportunity = _list(product_context, "product_opportunity.conversion_points")
    pains = _list(product_context, "product_opportunity.pain_points")
    surprises = _list(product_context, "product_opportunity.surprise_points")
    lead_source = _get(sales_context, "lead_source.summary", {})
    evidence = structured_report.get("evidence_references") or []
    calculations = structured_report.get("calculation_notes") or []
    executive_summary = structured_report.get("executive_summary") or []
    top_aspect = focus.get("top_aspect") or feedback.get("top_aspect") or "核心关注点"
    pain_aspect = (pains[0] or {}).get("aspect") if pains else "风险点"
    opportunity_aspect = (opportunity[0] or {}).get("aspect") if opportunity else top_aspect
    surprise_aspect = (surprises[0] or {}).get("aspect") if surprises else top_aspect

    return [
        {
            "code": "01",
            "title": "事件总判断",
            "subtitle": "先给业务判断，再看市场、产品、销售证据",
            "tone": "red",
            "cards": [
                _template_card(
                    "事件判断",
                    _first_text(executive_summary, f"{top_aspect}是当前事件最值得优先关注的信号。"),
                    [
                        f"总声量 {scale.get('total_volume', 0)}，内容 {scale.get('content_count', 0)}，评论 {scale.get('comment_count', 0)}。",
                        f"正向率 {feedback.get('positive_rate', 0)}%，负向率 {feedback.get('negative_rate', 0)}%。",
                    ],
                    "结论",
                ),
                _template_card(
                    "判断依据",
                    f"当前判断主要由市场声量、产品关注点和销售购买信号共同支撑。",
                    [f"产品关注点数量 {focus.get('aspect_count', 0)}。", f"中高购买信号 {lead.get('mid_high_purchase_signal_count', 0)} 条。"],
                    "依据",
                ),
            ],
        },
        {
            "code": "02",
            "title": "市场传播判断",
            "subtitle": "判断事件有没有传播规模和有效讨论",
            "tone": "green",
            "cards": [
                _template_card(
                    "声量规模",
                    f"事件总声量为 {scale.get('total_volume', 0)}，其中内容 {scale.get('content_count', 0)}，评论 {scale.get('comment_count', 0)}。",
                    [f"正向率 {feedback.get('positive_rate', 0)}%。", f"负向率 {feedback.get('negative_rate', 0)}%。"],
                    "市场",
                ),
                _template_card(
                    "讨论质量",
                    f"市场反馈中最显性的关注点是“{top_aspect}”。",
                    [f"中高购买信号率 {feedback.get('mid_high_purchase_signal_rate', 0)}%。", "声量与情绪共同用于判断传播是否有效。"],
                    "质量",
                ),
            ],
        },
        {
            "code": "03",
            "title": "产品机会与风险",
            "subtitle": "只呈现机会点、风险点、惊喜点和判断口径",
            "tone": "brown",
            "cards": [
                _template_card(
                    "机会点",
                    (opportunity[0] or {}).get("reason") or f"{opportunity_aspect}具备相对更强的转化机会。",
                    [f"产品点：{opportunity_aspect}", f"机会分：{(opportunity[0] or {}).get('opportunity_score', '-')}"],
                    "机会",
                ),
                _template_card(
                    "风险点",
                    (pains[0] or {}).get("reason") or "当前负向反馈需要持续跟踪。",
                    [f"产品点：{pain_aspect}", f"风险分：{(pains[0] or {}).get('opportunity_score', '-')}"],
                    "风险",
                ),
                _template_card(
                    "惊喜点",
                    (surprises[0] or {}).get("reason") or f"{surprise_aspect}具备相对更强的正向惊喜。",
                    [f"产品点：{surprise_aspect}", f"惊喜分：{(surprises[0] or {}).get('opportunity_score', '-')}"],
                    "惊喜",
                ),
                _template_card(
                    "判断口径",
                    "惊喜点、风险点、机会点均由提及率与对应业务率相乘得到，用来避免只看单一声量。",
                    ["惊喜点 = 提及率 × 正向率。", "风险点 = 提及率 × 负向率。", "机会点 = 提及率 × 中/强购买信号率。"],
                    "口径",
                ),
            ],
        },
        {
            "code": "04",
            "title": "销售转化判断",
            "subtitle": "判断当前讨论是否形成可承接的销售信号",
            "tone": "blue",
            "cards": [
                _template_card(
                    "购买信号",
                    f"当前中高购买信号为 {lead.get('mid_high_purchase_signal_count', 0)} 条，核心意图是 {lead.get('top_intent') or '暂未识别'}。",
                    [f"中高购买信号率 {lead.get('mid_high_purchase_signal_rate', 0)}%。", f"主要来源：{lead_source.get('top_platform') or '-'}。"],
                    "销售",
                ),
                _template_card(
                    "承接判断",
                    "销售视角只判断是否存在可承接信号，不在报告中给出执行建议。",
                    ["强/中购买信号用于识别转化窗口。", "平台来源用于判断线索集中位置。"],
                    "判断",
                ),
            ],
        },
        {
            "code": "05",
            "title": "证据与计算口径",
            "subtitle": "只展示业务可理解的证据来源和指标口径",
            "tone": "green",
            "cards": [
                _template_card(
                    "代表证据",
                    (evidence[0] or {}).get("quote") or "暂无可引用证据。",
                    [f"证据来源：{(evidence[0] or {}).get('source') or '-'}", "仅引用当前事件内的内容和评论。"],
                    "证据",
                ),
                _template_card(
                    "计算口径",
                    (calculations[0] or {}).get("method") or "暂无计算说明。",
                    [f"指标：{(calculations[0] or {}).get('metric') or '-'}", "不展示底层接口字段路径，只保留业务口径。"],
                    "口径",
                ),
            ],
        },
    ]


def _markdown(structured_report: dict[str, Any]) -> str:
    summary_items = "\n".join(f"- {item}" for item in structured_report.get("executive_summary") or [])
    recommendations = "\n".join(f"- {item}" for item in structured_report.get("recommendations") or [])
    evidence = "\n".join(f"- {item.get('source')}：{item.get('quote')}" for item in structured_report.get("evidence_references") or [])
    calculations = "\n".join(f"- {item.get('metric')}：{item.get('method')}" for item in structured_report.get("calculation_notes") or [])
    return f"""# {structured_report.get('title')}

## 执行摘要
{summary_items or "- 当前数据不足以生成执行摘要。"}

## 关键建议
{recommendations or "- 建议结合市场、产品、销售看板继续复核。"}

## 证据引用
{evidence or "- 暂无可引用证据。"}

## 数据计算方式
{calculations}
"""


def build_event_report_payload(
    *,
    event_id: str,
    market_context: dict[str, Any],
    product_context: dict[str, Any],
    sales_context: dict[str, Any],
    llm_summary: dict[str, Any],
    prompt_version: str = "event_report_agent_v1",
    rendered_prompt: str = "",
) -> dict[str, Any]:
    event = _event_overview(market_context, product_context, sales_context)
    title = f"{event.get('event_name') or event_id}事件综合报告"
    charts = build_event_report_charts(market_context, product_context, sales_context)
    _apply_event_chart_insights(charts, llm_summary)
    evidence_chart = _evidence_table(market_context, product_context, sales_context)
    structured_report = {
        "title": title,
        "event": event,
        "executive_summary": [str(item) for item in (llm_summary.get("executive_summary") or [])][:5],
        "recommendations": [str(item) for item in (llm_summary.get("recommendations") or [])][:5],
        "sections": llm_summary.get("sections") if isinstance(llm_summary.get("sections"), list) else [],
        "charts": charts,
        "evidence_references": _evidence_references([evidence_chart]),
        "calculation_notes": _calculation_notes(),
    }
    structured_report["template_sections"] = _template_sections(
        structured_report=structured_report,
        market_context=market_context,
        product_context=product_context,
        sales_context=sales_context,
    )
    return {
        "status": "generated",
        "message": f"已生成《{title}》。",
        "answer": f"已生成《{title}》。你可以在事件报告入口查看图文报告，报告包含固定图表、证据引用和数据计算方式。",
        "suggested_questions": [],
        "requires_clarification": False,
        "event_id": event_id,
        "prompt_version": prompt_version,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "report_markdown": _markdown(structured_report),
            "data_notes": ["本报告仅基于当前事件市场、产品、销售看板与评论证据生成。"],
            "structured_report": structured_report,
        },
        "context": {
            "market": market_context,
            "product": product_context,
            "sales": sales_context,
        },
        "rendered_prompt": rendered_prompt,
    }
