from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from app.agents.data_question.state import DataQuestionState, METRIC_CATALOG
from app.services.event_voc_insights import get_voc_event_market_dashboard, list_voc_events
from app.services.home_dashboard import get_auto_voc_home


def public_event(event: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_name": event.get("event_name") or "未命名事件",
        "brand_name": event.get("brand_name") or "未知品牌",
        "start_time": event.get("start_time"),
        "end_time": event.get("end_time"),
        "total_volume": event.get("total_volume", 0),
    }


def resolve_event(event_name: str) -> dict[str, Any]:
    rows = list_voc_events(q=event_name, limit=5).get("events") or []
    if not rows:
        raise ValueError(f"没有找到名称包含“{event_name}”的事件。")
    return rows[0]


def execute_list_events(arguments: dict[str, Any]) -> dict[str, Any]:
    days = int(arguments.get("days") or 30)
    brand = str(arguments.get("brand") or "").strip().lower()
    rows = get_auto_voc_home(days=days).get("key_events") or []
    if brand:
        rows = [row for row in rows if brand in str(row.get("brand_name") or "").lower()]
    events = [public_event(row) for row in rows[:10]]
    return {"range_days": days, "event_count": len(events), "events": events}


def execute_resolve_event(arguments: dict[str, Any]) -> dict[str, Any]:
    return public_event(resolve_event(str(arguments["event_name"])))


def execute_event_metric(state: DataQuestionState) -> dict[str, Any]:
    arguments = state["arguments"]
    event_id = state.get("event_id")
    if not event_id:
        event_id = str(resolve_event(str(arguments["event_name"]))["event_id"])
    dashboard = get_voc_event_market_dashboard(str(event_id))
    event = dashboard.get("event") or {}
    metric_key = str(arguments["metric"])
    metric = METRIC_CATALOG[metric_key]
    value = (dashboard.get("overview_metrics") or {}).get(metric["field"], 0)
    return {"event_name": event.get("event_name") or "当前事件", "metric": metric["label"], "value": value, "unit": metric["unit"]}


def parse_datetime(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if value:
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).replace(tzinfo=None)
        except ValueError:
            return None
    return None


def execute_rank_events(arguments: dict[str, Any]) -> dict[str, Any]:
    days = int(arguments.get("days") or 30)
    metric_key = str(arguments["metric"])
    rows = list_voc_events(limit=50).get("events") or []
    cutoff = datetime.now() - timedelta(days=days)
    rows = [row for row in rows if not parse_datetime(row.get("start_time")) or parse_datetime(row.get("start_time")) >= cutoff]
    ranked = []
    for row in rows:
        if metric_key == "kol_count":
            value = (get_voc_event_market_dashboard(str(row["event_id"])).get("overview_metrics") or {}).get("kol_count", 0)
        elif metric_key == "total_volume":
            value = int(row.get("content_cnt") or 0) + int(row.get("comment_cnt") or 0)
        else:
            field = {"content_count": "content_cnt", "comment_count": "comment_cnt", "total_engagement": "total_engagement"}[metric_key]
            value = row.get(field) or 0
        ranked.append({"event_name": row.get("event_name") or "未命名事件", "brand_name": row.get("brand_name") or "未知品牌", "value": value})
    ranked.sort(key=lambda item: item["value"], reverse=True)
    metric = METRIC_CATALOG[metric_key]
    return {"range_days": days, "metric": metric["label"], "unit": metric["unit"], "ranking": ranked[:10]}


def execute_tool(state: DataQuestionState) -> dict[str, Any]:
    action = state["action"]
    if action == "list_events":
        return execute_list_events(state["arguments"])
    if action == "resolve_event":
        return execute_resolve_event(state["arguments"])
    if action == "get_event_metric":
        return execute_event_metric(state)
    return execute_rank_events(state["arguments"])
