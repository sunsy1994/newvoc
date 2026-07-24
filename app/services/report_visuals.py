from __future__ import annotations

from typing import Any


PKO_RESULT_BUCKETS = {
    "优势": "advantage",
    "本车优势": "advantage",
    "劣势": "disadvantage",
    "本车劣势": "disadvantage",
    "中性": "neutral",
}


def _chart(
    chart_id: str,
    template_id: str,
    title: str,
    subtitle: str,
    source_label: str,
    data: list[dict[str, Any]],
    *,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "chart_id": chart_id,
        "template_id": template_id,
        "title": title,
        "subtitle": subtitle,
        "insight": "",
        "source_label": source_label,
        "data": data,
        "meta": meta or {},
    }


def _rows(value: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _meta(data: list[dict[str, Any]]) -> dict[str, Any]:
    return {} if data else {"empty_reason": "暂无可用数据"}


def _sort_pko_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: str(row.get("comment_id") or ""))
    ordered.sort(key=lambda row: str(row.get("published_at") or ""), reverse=True)
    ordered.sort(key=lambda row: int(row.get("interaction_cnt") or 0), reverse=True)
    return ordered


def _pko_evidence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for row in _sort_pko_rows(rows)[:50]:
        item = dict(row)
        item["target"] = item.get("target") or "其他对象"
        item["dimension"] = item.get("dimension") or "未明确维度"
        item["result"] = PKO_RESULT_BUCKETS.get(str(item.get("result") or ""), "unclear")
        normalized.append(item)
    return normalized


def build_market_report_charts(context: dict[str, Any]) -> list[dict[str, Any]]:
    hot_topics = context.get("hot_topics") or {}
    platform = context.get("platform") or {}
    feedback_quality = context.get("feedback_quality") or {}
    chart_data = [
        ("market-volume-trend", "F3", "传播规模与节奏", "按日声量变化", "volume_trend", _rows(context.get("volume_trend"))),
        ("market-hot-topics", "F5", "热门话题结构", "按讨论量展示", "hot_topics.topics", _rows(hot_topics.get("topics"))),
        ("market-platform-efficiency", "F8", "平台传播效率", "规模与反馈效率", "platform.platform_efficiency", _rows(platform.get("platform_efficiency"))),
        ("market-feedback-sentiment", "L14", "用户反馈构成", "情感分布", "feedback_quality.sentiment_distribution", _rows(feedback_quality.get("sentiment_distribution"))),
    ]
    return [_chart(*item, meta=_meta(item[-1])) for item in chart_data]


def build_product_report_charts(context: dict[str, Any]) -> list[dict[str, Any]]:
    focus = context.get("product_focus") or {}
    opportunity = context.get("product_opportunity") or {}
    pko = context.get("pko") or {}
    aspects = _rows(focus.get("aspects"))
    opportunity_rows = [
        {**row, "point_type": point_type}
        for point_type, rows in (
            ("surprise", opportunity.get("surprise_points")),
            ("pain", opportunity.get("pain_points")),
            ("conversion", opportunity.get("conversion_points")),
        )
        for row in _rows(rows)
    ]
    evidence_rows = _rows(pko.get("evidence_comments"))
    evidence = _pko_evidence(evidence_rows)
    evidence_meta = {"displayed_count": len(evidence), "total_count": len(evidence_rows), "unit": "条对比评论"}
    if not evidence:
        evidence_meta["empty_reason"] = "暂无可用数据"
    chart_data = [
        ("product-focus", "F5", "产品关注点", "按提及占比展示", "product_focus.aspects", aspects),
        ("product-sentiment", "F6", "产品点正负反馈", "正向与负向反馈率", "product_focus.aspects", aspects),
        ("product-opportunity", "F5", "机会、风险与转化", "系统计算的机会分", "product_opportunity", opportunity_rows),
        ("product-pko-evidence", "L12", "PKO 车系与对比维度", "每条线对应一条真实评论", "pko.evidence_comments", evidence),
        ("product-pko-matrix", "F7", "PKO 维度结果明细", "优势、劣势与中性结果", "pko.dimension_result_matrix", _rows(pko.get("dimension_result_matrix"))),
    ]
    charts = [_chart(*item, meta=_meta(item[-1])) for item in chart_data]
    charts[3]["meta"] = evidence_meta
    return charts


def build_sales_report_charts(context: dict[str, Any]) -> list[dict[str, Any]]:
    lead_quality = context.get("lead_quality") or {}
    lead_source = context.get("lead_source") or {}
    summary = lead_quality.get("summary") or {}
    funnel = [
        {"stage": label, "count": summary.get(key)}
        for label, key in (
            ("已打标评论", "labeled_comment_count"),
            ("车相关评论", "vehicle_related_count"),
            ("销售相关意图", "sales_intent_comment_count"),
            ("中/强购买信号", "mid_high_signal_count"),
        )
        if summary.get(key) is not None
    ]
    chart_data = [
        ("sales-lead-funnel", "L13", "线索转化漏斗", "固定转化阶段", "lead_quality.summary", funnel),
        ("sales-purchase-signals", "F4", "购买信号结构", "强、中、弱及未标注信号", "lead_quality.purchase_signal_distribution", _rows(lead_quality.get("purchase_signal_distribution"))),
        ("sales-intents", "F5", "用户意图分布", "评论数与占比", "lead_quality.intent_distribution", _rows(lead_quality.get("intent_distribution"))),
        ("sales-source-efficiency", "F6", "渠道线索效率", "总反馈量与销售线索量", "lead_source.platform_efficiency", _rows(lead_source.get("platform_efficiency"))),
    ]
    return [_chart(*item, meta=_meta(item[-1])) for item in chart_data]


def build_event_report_charts(
    market: dict[str, Any], product: dict[str, Any], sales: dict[str, Any]
) -> list[dict[str, Any]]:
    market_charts = build_market_report_charts(market)
    product_charts = build_product_report_charts(product)
    sales_charts = build_sales_report_charts(sales)
    return [market_charts[0], market_charts[3], product_charts[1], sales_charts[0]]
