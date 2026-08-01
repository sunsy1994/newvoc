from __future__ import annotations

import math
from typing import Any


REPORT_TEMPLATE_IDS = {"F3", "F4", "F5", "F6", "F7", "F8", "L6", "L12", "L13", "L14", "L15", "P1", "P2", "P3", "P4", "M1", "M2", "M3", "M4", "S1", "S2", "S3", "S4"}
MAX_SAFE_INTEGER = 9_007_199_254_740_991
SALES_FUNNEL_STAGES = ("已打标评论", "车相关评论", "销售相关意图", "中/强购买信号")
RESULT_BUCKETS = {"advantage", "disadvantage", "neutral", "unclear"}
LABEL_KEYS = ("label", "name", "date", "platform", "category", "dimension")
VALUE_KEYS = ("value", "count", "total", "percentage", "percent", "rate", "total_volume")


def _text(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _number(value: Any, *, clamp_negative: bool = True) -> float | None:
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or (not clamp_negative and number < 0):
        return None
    return max(0.0, number) if clamp_negative else number


def _finite_non_negative(value: Any) -> bool:
    return _number(value, clamp_negative=False) is not None


def normalize_sentiment_rates(positive: Any, negative: Any) -> dict[str, float] | None:
    if not _finite_non_negative(positive) or not _finite_non_negative(negative):
        return None
    positive_value = min(float(positive), 100.0)
    negative_value = min(float(negative), 100.0)
    selected_total = positive_value + negative_value
    if selected_total > 100.0:
        scale = 100.0 / selected_total
        positive_value = round(positive_value * scale, 2)
        negative_value = round(100.0 - positive_value, 2)
        neutral_value = 0.0
    else:
        positive_value = round(positive_value, 2)
        negative_value = round(negative_value, 2)
        neutral_value = round(max(0.0, 100.0 - positive_value - negative_value), 2)
    return {
        "positive_rate": positive_value,
        "neutral_rate": neutral_value,
        "negative_rate": negative_value,
    }


def _first_text(row: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    return next((_text(row.get(key)) for key in keys if _text(row.get(key))), None)


def _first_number(row: dict[str, Any], keys: tuple[str, ...]) -> float | None:
    for key in keys:
        number = _number(row.get(key))
        if number is not None:
            return number
    return None


def _valid_f5_row(row: dict[str, Any]) -> bool:
    if _text(row.get("topic")):
        return _number(row.get("comment_count")) is not None
    if _text(row.get("aspect")):
        return (
            _number(row.get("opportunity_score")) is not None
            or _number(row.get("mention_rate")) is not None
        )
    return bool(
        _text(row.get("label"))
        and (_number(row.get("count")) is not None or _number(row.get("rate")) is not None)
    )


def _valid_f6_row(row: dict[str, Any]) -> bool:
    if _text(row.get("aspect")):
        return (
            _number(row.get("positive_rate")) is not None
            and _number(row.get("negative_rate")) is not None
        )
    return bool(
        _text(row.get("platform"))
        and _number(row.get("comment_count")) is not None
        and _number(row.get("high_intent_comment_count")) is not None
    )


def _valid_f7_row(row: dict[str, Any]) -> bool:
    return bool(
        _text(row.get("dimension"))
        and any(
            _number(row.get(key)) is not None
            for key in (
                "advantage_count",
                "disadvantage_count",
                "neutral_count",
                "unclear_count",
            )
        )
    )


def _valid_f8_row(row: dict[str, Any]) -> bool:
    return bool(
        _text(row.get("platform"))
        and _number(row.get("total_volume")) is not None
        and _number(row.get("engagement_per_content")) is not None
    )


def _valid_l12_row(row: dict[str, Any]) -> bool:
    result = _text(row.get("result_bucket")) or _text(row.get("result"))
    return bool(
        _text(row.get("comment_id"))
        and _text(row.get("target"))
        and _text(row.get("dimension"))
        and result in RESULT_BUCKETS
        and _text(row.get("comment_text"))
    )


def _valid_l6_row(row: dict[str, Any]) -> bool:
    return bool(
        _text(row.get("comment_id"))
        and _text(row.get("comment_text"))
        and _text(row.get("dimension"))
        and not _text(row.get("dimension")).startswith("未标注")
        and _text(row.get("target"))
        and not _text(row.get("target")).startswith("未标注")
    )


def _result_bucket(value: Any) -> str:
    normalized = _text(value)
    if normalized in {"advantage", "本车优势", "优势"}:
        return "advantage"
    if normalized in {"disadvantage", "本车劣势", "劣势"}:
        return "disadvantage"
    if normalized in {"neutral", "中性对比", "中性"}:
        return "neutral"
    return "unclear"


def normalize_report_chart_data(template_id: str, value: Any) -> list[dict[str, Any]]:
    rows = _rows(value)
    if template_id == "S1":
        if len(rows) != len(SALES_FUNNEL_STAGES):
            return []
        counts = [_number(row.get("count"), clamp_negative=False) for row in rows]
        return rows if all(count is not None for count in counts) and all(right <= left for left, right in zip(counts, counts[1:])) else []
    if template_id == "S2":
        return [row for row in rows if _text(row.get("row_type")) in {"intent", "signal"} and _text(row.get("label")) and _number(row.get("count")) is not None]
    if template_id == "S3":
        return [row for row in rows if _text(row.get("source_level")) in {"content", "platform"} and (_text(row.get("title")) or _text(row.get("platform"))) and _number(row.get("high_intent_comment_count")) is not None][:8]
    if template_id == "S4":
        return [row for row in rows if _text(row.get("comment_user_id")) and _text(row.get("purchase_signal")) in {"强", "中", "strong", "medium"}][:10]
    if template_id == "M1":
        return [
            row for row in rows
            if _text(row.get("date"))
            and _number(row.get("content_count")) is not None
            and _number(row.get("comment_count")) is not None
        ]
    if template_id == "M2":
        return [
            row for row in rows
            if _text(row.get("topic")) and _number(row.get("comment_count")) is not None
        ][:10]
    if template_id == "M3":
        return [
            row for row in rows
            if _text(row.get("author_name"))
            and _number(row.get("total_engagement")) is not None
            and _number(row.get("content_count")) is not None
        ][:5]
    if template_id == "M4":
        return [row for row in rows if _valid_f8_row(row)]
    if template_id == "F3":
        return [
            row
            for row in rows
            if _first_text(row, LABEL_KEYS) and _first_number(row, VALUE_KEYS) is not None
        ]
    if template_id == "F4":
        normalized = [
            row
            for row in rows
            if _first_text(row, LABEL_KEYS) and _first_number(row, VALUE_KEYS) is not None
        ]
        return normalized if sum(_first_number(row, VALUE_KEYS) or 0 for row in normalized) > 0 else []
    if template_id in {"F5", "P1", "P3"}:
        return [row for row in rows if _valid_f5_row(row)]
    if template_id == "F6":
        return [row for row in rows if _valid_f6_row(row)]
    if template_id in {"F7", "P4"}:
        return [row for row in rows if _valid_f7_row(row)]
    if template_id == "F8":
        return [row for row in rows if _valid_f8_row(row)]
    if template_id == "L12":
        return [row for row in rows if _valid_l12_row(row)]
    if template_id == "L6":
        return [
            {
                **row,
                "result_bucket": _result_bucket(
                    row.get("result_bucket")
                    if _text(row.get("result_bucket"))
                    else row.get("result")
                ),
            }
            for row in rows
            if _valid_l6_row(row)
        ]
    if template_id == "L13":
        if len(rows) != len(SALES_FUNNEL_STAGES):
            return []
        labels = tuple(_text(row.get("stage")) for row in rows)
        counts = [_number(row.get("count"), clamp_negative=False) for row in rows]
        if labels != SALES_FUNNEL_STAGES or any(count is None for count in counts):
            return []
        numeric_counts = [count for count in counts if count is not None]
        if not numeric_counts or numeric_counts[0] <= 0:
            return []
        return rows if all(right <= left for left, right in zip(numeric_counts, numeric_counts[1:])) else []
    if template_id == "L14":
        percentages = []
        for row in rows:
            percentage = next(
                (
                    number
                    for key in ("percentage", "percent", "rate")
                    if (number := _number(row.get(key), clamp_negative=False)) is not None
                ),
                None,
            )
            if not _text(row.get("label")) or percentage is None:
                continue
            percentages.append((row, percentage))
        total = sum(percentage for _, percentage in percentages)
        if not percentages or abs(total - 100) > 1.01:
            return []
        return [row for row, _ in percentages]
    if template_id in {"L15", "P2"}:
        normalized_rows = []
        for row in rows:
            rates = normalize_sentiment_rates(
                row.get("positive_rate"),
                row.get("negative_rate"),
            )
            if _text(row.get("aspect")) and rates:
                normalized_rows.append({**row, **rates})
        return normalized_rows
    return []


def has_renderable_data(chart: Any) -> bool:
    if not isinstance(chart, dict):
        return False
    template_id = chart.get("template_id")
    return bool(
        isinstance(template_id, str)
        and template_id in REPORT_TEMPLATE_IDS
        and normalize_report_chart_data(template_id, chart.get("data"))
    )


def normalize_report_chart_meta(
    template_id: str,
    data: list[dict[str, Any]],
    value: Any,
) -> dict[str, Any] | None:
    if template_id not in REPORT_TEMPLATE_IDS:
        return None
    if not isinstance(value, dict):
        return None
    meta = dict(value)
    if template_id in {"L6", "L12"}:
        expected_keys = {"displayed_count", "total_count", "unit"}
        if not data:
            expected_keys.add("empty_reason")
        if set(meta) != expected_keys:
            return None
        displayed_count = meta.get("displayed_count")
        total_count = meta.get("total_count")
        if not (
            isinstance(displayed_count, int)
            and not isinstance(displayed_count, bool)
            and displayed_count == len(data)
            and displayed_count <= 50
            and isinstance(total_count, int)
            and not isinstance(total_count, bool)
            and total_count >= displayed_count
            and total_count <= MAX_SAFE_INTEGER
            and meta.get("unit") == "条对比评论"
        ):
            return None
        if not data and (
            total_count != 0 or meta.get("empty_reason") != "暂无可用数据"
        ):
            return None
        return meta
    if data:
        return meta if not meta else None
    return (
        meta
        if meta == {"empty_reason": "暂无可用数据"}
        else None
    )


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
    normalized_data = normalize_report_chart_data(template_id, data)
    chart_meta = dict(meta or {})
    if not normalized_data:
        chart_meta.setdefault("empty_reason", "暂无可用数据")
    return {
        "chart_id": chart_id,
        "template_id": template_id,
        "title": title,
        "subtitle": subtitle,
        "insight": "",
        "source_label": source_label,
        "data": normalized_data,
        "meta": chart_meta,
    }


def _rows(value: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in value if isinstance(row, dict)] if isinstance(value, list) else []


def _meta(data: list[dict[str, Any]]) -> dict[str, Any]:
    return {} if data else {"empty_reason": "暂无可用数据"}


def _sort_pko_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: str(row.get("comment_id") or ""))
    ordered.sort(key=lambda row: str(row.get("published_at") or ""), reverse=True)
    ordered.sort(
        key=lambda row: _number(row.get("interaction_cnt"), clamp_negative=False) or 0,
        reverse=True,
    )
    return ordered


def build_market_report_charts(context: dict[str, Any]) -> list[dict[str, Any]]:
    hot_topics = context.get("hot_topics") or {}
    platform = context.get("platform") or {}
    subjects = context.get("kol_and_authors") or {}
    chart_data = [
        ("market-volume-rhythm", "M1", "传播结果与节奏", "内容与评论的每日构成", "volume_trend", _rows(context.get("volume_trend"))),
        ("market-topic-drivers", "M2", "话题驱动", "讨论规模、内容量与累计互动", "hot_topics.topics", _rows(hot_topics.get("topics"))),
        ("market-subject-contribution", "M3", "传播主体", "作者互动贡献与内容量", "kol_and_authors.top_authors", _rows(subjects.get("top_authors"))),
        ("market-channel-efficiency", "M4", "渠道效率", "传播规模与单内容互动效率", "platform.platform_efficiency", _rows(platform.get("platform_efficiency"))),
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
    evidence_rows = normalize_report_chart_data(
        "L6", _sort_pko_rows(_rows(pko.get("evidence_comments")))
    )
    evidence = evidence_rows[:50]
    raw_total_count = pko.get("evidence_total_count")
    total_count = (
        raw_total_count
        if isinstance(raw_total_count, int)
        and not isinstance(raw_total_count, bool)
        and len(evidence_rows) <= raw_total_count <= MAX_SAFE_INTEGER
        else len(evidence_rows)
    )
    evidence_meta = {"displayed_count": len(evidence), "total_count": total_count, "unit": "条对比评论"}
    if not evidence:
        evidence_meta["empty_reason"] = "暂无可用数据"
    chart_data = [
        ("product-focus", "P1", "产品关注点", "提及占比与反馈质量", "product_focus.aspects", aspects),
        ("product-sentiment", "P2", "产品点正负反馈", "正向 / 中性 / 负向连续构成", "product_focus.aspects", aspects),
        ("product-opportunity", "P3", "机会、风险与惊喜", "基于系统机会分归类", "product_opportunity", opportunity_rows),
        ("product-pko-evidence", "L6", "用户反馈构成", "中心为产品点 · 气泡面积代表真实对比次数", "pko.evidence_comments", evidence),
        ("product-pko-matrix", "P4", "PKO 维度结果明细", "各产品维度的对比结果构成", "pko.dimension_result_matrix", _rows(pko.get("dimension_result_matrix"))),
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
            ("中/强购买信号", "mid_high_purchase_signal_count"),
        )
        if summary.get(key) is not None
    ]
    source_efficiency = [
        {
            **row,
            "comment_count": row.get("comment_count", row.get("total_comment_count")),
        }
        for row in _rows(lead_source.get("platform_efficiency"))
    ]
    needs = [
        {**row, "row_type": "intent"}
        for row in _rows(lead_quality.get("intent_distribution"))
    ] + [
        {**row, "row_type": "signal"}
        for row in _rows(lead_quality.get("purchase_signal_distribution"))
    ]
    content_sources = [
        {**row, "source_level": "content"}
        for row in _rows(lead_source.get("content_leads"))
    ]
    if not content_sources:
        content_sources = [{**row, "source_level": "platform"} for row in source_efficiency]
    follow_up = []
    seen_users = set()
    signal_rank = {"强": 0, "strong": 0, "中": 1, "medium": 1}
    for row in sorted(
        _rows(context.get("recommended_follow_up_users")),
        key=lambda item: signal_rank.get(str(item.get("purchase_signal") or ""), 9),
    ):
        user_id = str(row.get("comment_user_id") or "")
        if not user_id or user_id in seen_users or str(row.get("purchase_signal") or "") not in signal_rank:
            continue
        seen_users.add(user_id)
        follow_up.append(row)
    chart_data = [
        ("sales-lead-output", "S1", "线索产出", "从已打标评论到中/强购买信号", "lead_quality.summary", funnel),
        ("sales-user-needs", "S2", "用户需求", "意图结构与购买信号", "lead_quality.intent_distribution", needs),
        ("sales-content-sources", "S3", "线索来源", "带来中高意向的内容", "lead_source.content_leads", content_sources),
        ("sales-follow-up-pool", "S4", "承接对象", "强、中购买信号用户梯队", "recommended_follow_up_users", follow_up),
    ]
    return [_chart(*item, meta=_meta(item[-1])) for item in chart_data]


def build_event_report_charts(
    market: dict[str, Any], product: dict[str, Any], sales: dict[str, Any]
) -> list[dict[str, Any]]:
    feedback = market.get("feedback_quality") or {}
    event_market_trend = _chart(
        "market-volume-trend", "F3", "传播规模与节奏", "按日声量变化",
        "volume_trend", _rows(market.get("volume_trend")),
        meta=_meta(_rows(market.get("volume_trend"))),
    )
    event_market_feedback = _chart(
        "market-feedback-sentiment", "L14", "用户反馈构成", "情感分布",
        "feedback_quality.sentiment_distribution",
        _rows(feedback.get("sentiment_distribution")),
        meta=_meta(_rows(feedback.get("sentiment_distribution"))),
    )
    product_focus = product.get("product_focus") or {}
    event_product_sentiment = _chart(
        "product-sentiment",
        "F6",
        "产品点正负反馈",
        "正向与负向反馈率",
        "product_focus.aspects",
        _rows(product_focus.get("aspects")),
        meta=_meta(_rows(product_focus.get("aspects"))),
    )
    sales_summary = (sales.get("lead_quality") or {}).get("summary") or {}
    event_sales_funnel = _chart(
        "sales-lead-funnel", "L13", "线索转化漏斗", "固定转化阶段",
        "lead_quality.summary",
        [
            {"stage": label, "count": sales_summary.get(key)}
            for label, key in (
                ("已打标评论", "labeled_comment_count"),
                ("车相关评论", "vehicle_related_count"),
                ("销售相关意图", "sales_intent_comment_count"),
                ("中/强购买信号", "mid_high_purchase_signal_count"),
            )
            if sales_summary.get(key) is not None
        ],
    )
    return [event_market_trend, event_market_feedback, event_product_sentiment, event_sales_funnel]
