from __future__ import annotations

from typing import Any, TypedDict


class CompetitorReportState(TypedDict, total=False):
    message: str
    brand_name: str
    brand_defaulted: bool
    start_date: str
    end_date: str
    time_defaulted: bool
    dataset: dict[str, Any]
