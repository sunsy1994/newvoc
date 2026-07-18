from __future__ import annotations

from typing import Any, TypedDict


class CompetitorReportState(TypedDict, total=False):
    message: str
    event_id: str | None
    history: list[dict[str, Any]]
    brand_name: str
    brand_defaulted: bool
    start_date: str
    end_date: str
    time_defaulted: bool
    scope_notice: list[str]
    dataset: dict[str, Any]
    rendered_prompt: str
    llm_summary: dict[str, Any]
    report_html: str
    report_asset: dict[str, Any]
    result: dict[str, Any]
