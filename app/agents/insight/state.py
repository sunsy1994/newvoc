from __future__ import annotations

from typing import Any, TypedDict


class InsightAgentState(TypedDict, total=False):
    question: str
    event_id: str | None
    history: list[dict[str, str]]
    scenario: dict[str, Any]
    candidate_events: list[dict[str, Any]]
    similar_events: list[dict[str, Any]]
    gate: dict[str, Any]
    status: str
    clarification_question: str
    draft_simulation: dict[str, Any]
    review_issues: list[str]
    result: dict[str, Any]
    react_rounds: int
MAX_MODEL_ROUNDS = 3
