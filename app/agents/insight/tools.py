from __future__ import annotations

from typing import Any

from app.services.event_voc_insights import (
    get_voc_event_discussion_point_comments,
    get_voc_event_market_dashboard,
    get_voc_event_product_dashboard,
    get_voc_event_sales_dashboard,
    list_voc_events,
)
from app.services.report_agent import (
    build_market_report_context,
    build_product_report_context,
    build_sales_report_context,
)


MIN_RELEVANT_COMMENTS = 10
RELATION_PRIORITY = {"same_model": 0, "same_brand": 1, "cross_brand": 2}
ACTION_TERMS = {
    "配置减少": ("减配", "配置调整", "配置"),
    "配置增加": ("增配", "配置升级", "配置"),
    "价格调整": ("降价", "涨价", "价格", "权益"),
    "新品上市": ("上市", "发布", "首发", "新车"),
}


def _clean_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _relation_type(event: dict[str, Any], scenario: dict[str, Any]) -> str:
    target_model = _clean_text(scenario.get("model_name"))
    target_brand = _clean_text(scenario.get("brand_name"))
    if target_model and _clean_text(event.get("model_name")) == target_model:
        return "same_model"
    if target_brand and _clean_text(event.get("brand_name")) == target_brand:
        return "same_brand"
    return "cross_brand"


def _relevance_score(event: dict[str, Any], scenario: dict[str, Any]) -> int:
    event_text = _clean_text(" ".join(str(event.get(key) or "") for key in ("event_name", "event_type")))
    action_type = str(scenario.get("action_type") or "")
    terms = next((values for key, values in ACTION_TERMS.items() if key in action_type or action_type in key), ())
    aspect_terms = tuple(str(value).strip() for value in scenario.get("affected_aspects") or [] if str(value).strip())
    return sum(term.lower() in event_text for term in (*terms, *aspect_terms))


def list_candidate_events(
    scenario: dict[str, Any],
    *,
    event_id: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    events = list_voc_events(limit=100).get("events") or []
    candidates = []
    for event in events:
        if event_id and str(event.get("event_id") or "") == str(event_id):
            continue
        candidate = dict(event)
        candidate["relation_type"] = _relation_type(event, scenario)
        candidate["relevance_score"] = _relevance_score(event, scenario)
        candidates.append(candidate)
    candidates.sort(key=lambda item: (RELATION_PRIORITY[item["relation_type"]], -int(item["relevance_score"])))
    return candidates[:limit]


def _unique_comments(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    seen = set()
    for item in comments:
        key = str(item.get("comment_id") or item.get("comment_text") or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _comment_matches_aspects(comment: dict[str, Any], aspects: list[str]) -> bool:
    if not aspects:
        return True
    comment_text = _clean_text(comment.get("comment_text"))
    comment_aspect = _clean_text(comment.get("aspect"))
    return any(
        _clean_text(aspect) in comment_text or _clean_text(aspect) == comment_aspect
        for aspect in aspects
        if _clean_text(aspect)
    )


def get_event_reaction_evidence(
    candidate: dict[str, Any],
    scenario: dict[str, Any] | None = None,
) -> dict[str, Any]:
    event_id = str(candidate.get("event_id") or "").strip()
    if not event_id:
        raise ValueError("候选事件缺少 event_id。")
    market = build_market_report_context(get_voc_event_market_dashboard(event_id))
    product = build_product_report_context(get_voc_event_product_dashboard(event_id))
    sales = build_sales_report_context(get_voc_event_sales_dashboard(event_id))
    aspects = [str(value).strip() for value in (scenario or {}).get("affected_aspects") or [] if str(value).strip()]
    relevant_comments = []
    for aspect in aspects:
        relevant_comments.extend(
            get_voc_event_discussion_point_comments(event_id, str(aspect), limit=20).get("comments") or []
        )
    product_comments = [
        item for item in product.get("evidence_comments") or [] if _comment_matches_aspects(item, aspects)
    ]
    sales_comments = [
        item
        for item in (sales.get("lead_source") or {}).get("lead_comments") or []
        if _comment_matches_aspects(item, aspects)
    ]
    evidence_comments = _unique_comments(
        relevant_comments
        + product_comments
        + sales_comments
    )
    event = dict(candidate)
    return {
        "event": event,
        "market": market,
        "product": product,
        "sales": sales,
        "evidence_comments": evidence_comments,
    }


def evaluate_evidence_gate(similar_events: list[dict[str, Any]]) -> dict[str, Any]:
    strong_count = sum(item.get("similarity") == "strong" for item in similar_events)
    medium_count = sum(item.get("similarity") == "medium" for item in similar_events)
    comment_count = sum(len(item.get("evidence_comments") or []) for item in similar_events)
    if not similar_events or comment_count < MIN_RELEVANT_COMMENTS:
        status = "insufficient_data"
    elif strong_count >= 1 or medium_count >= 2:
        status = "completed"
    else:
        status = "partial"
    return {
        "status": status,
        "strong_count": strong_count,
        "medium_count": medium_count,
        "comment_count": comment_count,
    }
