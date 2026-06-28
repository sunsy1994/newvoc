from __future__ import annotations

from typing import Any, TypedDict


class DataQuestionState(TypedDict, total=False):
    question: str
    event_id: str | None
    history: list[dict[str, str]]
    action: str
    arguments: dict[str, Any]
    needs_clarification: bool
    clarification_question: str
    tool_result: dict[str, Any]
    status: str
    answer: str
    suggested_questions: list[str]


METRIC_CATALOG: dict[str, dict[str, str]] = {
    "total_volume": {"label": "总声量", "field": "total_volume", "unit": "条"},
    "content_count": {"label": "帖子数", "field": "content_count", "unit": "篇"},
    "comment_count": {"label": "评论数", "field": "comment_count", "unit": "条"},
    "kol_count": {"label": "KOL数", "field": "kol_count", "unit": "位"},
    "total_engagement": {"label": "总互动量", "field": "total_engagement", "unit": "次"},
}

ALLOWED_ACTIONS = {"list_events", "resolve_event", "get_event_metric", "rank_events"}

SUGGESTIONS_BY_ACTION = {
    "list_events": ["哪个事件声量最高？", "哪个事件评论最多？", "哪个事件的KOL最多？"],
    "resolve_event": ["这个事件的声量是多少？", "这个事件有多少评论？"],
    "get_event_metric": ["近期有哪些事件？", "哪个事件声量最高？"],
    "rank_events": ["近期有哪些事件？", "哪个事件互动量最高？"],
}
