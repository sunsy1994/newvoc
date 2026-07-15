from __future__ import annotations

from typing import Any, TypedDict


class EventReportState(TypedDict, total=False):
    message: str
    event_id: str | None
    history: list[dict[str, str]]
    market_context: dict[str, Any]
    product_context: dict[str, Any]
    sales_context: dict[str, Any]
    rendered_prompt: str
    llm_summary: dict[str, Any]
    result: dict[str, Any]
