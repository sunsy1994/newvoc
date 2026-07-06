from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from app.services.event_voc_insights import (
    get_voc_event_discussion_point_comments,
    get_voc_event_market_dashboard,
    get_voc_event_product_dashboard,
    get_voc_event_sales_dashboard,
    list_voc_events,
)
from app.services.report_agent import build_market_report_context, build_product_report_context, build_sales_report_context


SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
EXPLICIT_RANGE_PATTERN = re.compile(
    r"(?P<start>\d{4}-\d{2}-\d{2})\s*(?:到|至|~|—|–)\s*(?P<end>\d{4}-\d{2}-\d{2})"
)
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
    anchor = asked_at or datetime.now(SHANGHAI_TZ)
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=SHANGHAI_TZ)
    else:
        anchor = anchor.astimezone(SHANGHAI_TZ)

    explicit = EXPLICIT_RANGE_PATTERN.search(question)
    if explicit:
        start_date = explicit.group("start")
        end_date = explicit.group("end")
        return {
            "mode": "explicit",
            "start_date": start_date,
            "end_date": end_date,
            "label": f"{start_date} 至 {end_date}（用户指定）",
        }

    if event:
        start_date = _date_text(event.get("start_time") or event.get("end_time"))
        end_date = _date_text(event.get("end_time") or event.get("start_time"))
        if start_date and end_date:
            return {
                "mode": "event_period",
                "start_date": start_date,
                "end_date": end_date,
                "label": f"{start_date} 至 {end_date}（事件完整周期）",
            }

    end = anchor.date()
    start = end - timedelta(days=29)
    start_date = start.isoformat()
    end_date = end.isoformat()
    return {
        "mode": "default_30_days",
        "start_date": start_date,
        "end_date": end_date,
        "label": f"{start_date} 至 {end_date}（提问时点近30天）",
    }


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

    if tool_name == "get_market_story":
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
    payload = get_voc_event_discussion_point_comments(event_id, aspect, limit=20, offset=0)
    return _envelope(
        tool_name,
        event={"event_id": event_id, "event_name": arguments.get("event_name") or "当前事件"},
        time_scope=time_scope,
        data_scope="产品关注点原始评论",
        facts={"aspect": aspect, "total": payload.get("total", 0)},
        evidence=payload.get("comments") or [],
    )
