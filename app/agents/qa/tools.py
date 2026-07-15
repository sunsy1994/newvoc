from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from app.services.event_voc_insights import (
    get_voc_event_market_dashboard,
    get_voc_event_product_dashboard,
    get_voc_event_sales_dashboard,
    list_voc_events,
)
from app.services.report_agent import build_market_report_context, build_product_report_context, build_sales_report_context

from app.agents.qa import time_scope_resolver, time_slice


SHANGHAI_TZ = time_scope_resolver.SHANGHAI_TZ
ALLOWED_TOOLS = {
    "list_events",
    "get_market_story",
    "get_product_story",
    "get_sales_story",
    "get_discussion_evidence",
}


def _date_text(value: Any) -> str:
    return str(value or "")[:10]


def resolve_time_scope(
    question: str,
    *,
    asked_at: datetime | None = None,
    event: dict[str, Any] | None = None,
) -> dict[str, str]:
    return time_scope_resolver.resolve_time_scope(question, asked_at=asked_at, event=event)


def _event_summary(event: dict[str, Any] | None) -> dict[str, Any]:
    source = event or {}
    return {
        "event_id": source.get("event_id"),
        "event_name": source.get("event_name") or "未指定事件",
        "brand_name": source.get("brand_name"),
        "model_name": source.get("model_name"),
        "start_time": source.get("start_time"),
        "end_time": source.get("end_time"),
    }


def resolve_event_context(*, event_id: str | None = None, event_name: str | None = None) -> dict[str, Any] | None:
    if not event_id and not event_name:
        return None
    rows = list_voc_events(q=event_name, limit=100 if event_id else 5).get("events") or []
    if event_id:
        return next((row for row in rows if str(row.get("event_id")) == str(event_id)), None)
    return rows[0] if rows else None


def _event_match_text(value: Any) -> str:
    return re.sub(r"[\s\-_./·]+", "", str(value or "").lower())


def _event_text_candidates(value: Any) -> list[str]:
    text = _event_match_text(value)
    if not text:
        return []
    candidates = [text]
    for suffix in ("上市", "发布", "预热", "亮相", "首发", "活动", "事件"):
        if text.endswith(suffix):
            candidates.append(text[: -len(suffix)])
    return [candidate for candidate in candidates if len(candidate) >= 2]


def infer_event_context_from_question(question: str) -> dict[str, Any] | None:
    normalized_question = _event_match_text(question)
    if not normalized_question:
        return None
    rows = list_voc_events(limit=100).get("events") or []
    for row in rows:
        for key in ("event_name", "model_name", "brand_name"):
            if any(candidate in normalized_question for candidate in _event_text_candidates(row.get(key))):
                return row
    return None


def _envelope(
    tool_name: str,
    *,
    event: dict[str, Any] | None,
    time_scope: dict[str, str],
    data_scope: str,
    facts: dict[str, Any],
    evidence: list[dict[str, Any]] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "tool_name": tool_name,
        "event": _event_summary(event),
        "time_scope": time_scope,
        "data_scope": data_scope,
        "facts": facts,
        "evidence": evidence or [],
        "notes": notes or [],
    }


def _event_in_scope(event: dict[str, Any], time_scope: dict[str, str]) -> bool:
    start = _date_text(event.get("start_time") or event.get("end_time"))
    end = _date_text(event.get("end_time") or event.get("start_time")) or start
    if not start:
        return True
    return start <= time_scope["end_date"] and end >= time_scope["start_date"]


def execute_qa_tool(tool_name: str, arguments: dict[str, Any], time_scope: dict[str, str]) -> dict[str, Any]:
    if tool_name not in ALLOWED_TOOLS:
        raise ValueError(f"不支持的问答工具：{tool_name or '空工具'}。")

    if tool_name == "list_events":
        rows = list_voc_events(q=str(arguments.get("brand") or "").strip() or None, limit=100).get("events") or []
        rows = [row for row in rows if _event_in_scope(row, time_scope)]
        facts = {"event_count": len(rows), "events": rows[:20]}
        return _envelope(tool_name, event=None, time_scope=time_scope, data_scope="事件资产列表", facts=facts)

    event_id = str(arguments.get("event_id") or "").strip()
    if not event_id:
        event_name = str(arguments.get("event_name") or "").strip()
        rows = list_voc_events(q=event_name, limit=5).get("events") or []
        if not rows:
            raise ValueError(f"没有找到名称包含“{event_name}”的事件。")
        event_id = str(rows[0]["event_id"])

    event = {
        "event_id": event_id,
        "event_name": arguments.get("event_name") or "当前事件",
    }
    use_time_slice = time_scope.get("mode") != "event_period"

    if tool_name == "get_market_story":
        if use_time_slice:
            facts = time_slice.get_market_slice(event_id, time_scope["start_date"], time_scope["end_date"])
            return _envelope(
                tool_name,
                event=event,
                time_scope=time_scope,
                data_scope="市场数据（按统计区间切片）",
                facts=facts,
                evidence=facts.get("hot_posts") or [],
            )
        dashboard = get_voc_event_market_dashboard(event_id)
        context = build_market_report_context(dashboard)
        return _envelope(
            tool_name,
            event=dashboard.get("event"),
            time_scope=time_scope,
            data_scope="市场看板结构化数据",
            facts=context,
            evidence=(context.get("evidence") or {}).get("hot_posts") or [],
        )

    if tool_name == "get_product_story":
        if use_time_slice:
            facts = time_slice.get_product_slice(event_id, time_scope["start_date"], time_scope["end_date"])
            aspects = (facts.get("product_focus_story") or {}).get("aspects") or []
            evidence = [comment for aspect_item in aspects for comment in (aspect_item.get("evidence_comments") or [])]
            return _envelope(
                tool_name,
                event=event,
                time_scope=time_scope,
                data_scope="产品数据（按统计区间切片）",
                facts=facts,
                evidence=evidence[:20],
            )
        dashboard = get_voc_event_product_dashboard(event_id)
        context = build_product_report_context(dashboard)
        return _envelope(
            tool_name,
            event=dashboard.get("event"),
            time_scope=time_scope,
            data_scope="产品看板结构化数据",
            facts=context,
            evidence=context.get("evidence_comments") or [],
        )

    if tool_name == "get_sales_story":
        if use_time_slice:
            facts = time_slice.get_sales_slice(event_id, time_scope["start_date"], time_scope["end_date"])
            evidence = (facts.get("sales_lead_source_efficiency") or {}).get("lead_comments") or []
            return _envelope(
                tool_name,
                event=event,
                time_scope=time_scope,
                data_scope="销售数据（按统计区间切片）",
                facts=facts,
                evidence=evidence,
            )
        dashboard = get_voc_event_sales_dashboard(event_id)
        context = build_sales_report_context(dashboard)
        return _envelope(
            tool_name,
            event=dashboard.get("event"),
            time_scope=time_scope,
            data_scope="销售看板结构化数据",
            facts=context,
            evidence=(context.get("lead_source") or {}).get("lead_comments") or [],
        )

    aspect = str(arguments.get("aspect") or "").strip()
    if not aspect:
        raise ValueError("查询评论证据时必须提供产品关注点。")
    payload = time_slice.get_discussion_slice(
        event_id,
        aspect,
        time_scope["start_date"],
        time_scope["end_date"],
    )
    return _envelope(
        tool_name,
        event=event,
        time_scope=time_scope,
        data_scope="产品关注点原始评论（按统计区间切片）",
        facts={"aspect": aspect, "total": payload.get("total", 0)},
        evidence=payload.get("comments") or [],
    )
