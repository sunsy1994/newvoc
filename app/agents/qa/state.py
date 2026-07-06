from __future__ import annotations

from typing import Any, TypedDict


class QaAgentState(TypedDict, total=False):
    question: str
    event_id: str | None
    event: dict[str, Any]
    history: list[dict[str, str]]
    asked_at: str
    time_scope: dict[str, str]
    data_scope: str
    round_count: int
    action: str
    arguments: dict[str, Any]
    observations: list[dict[str, Any]]
    draft_answer: str
    answer: str
    sufficient: bool
    needs_clarification: bool
    clarification_question: str
    suggested_questions: list[str]


MAX_REACT_ROUNDS = 3

