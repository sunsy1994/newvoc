from __future__ import annotations

from datetime import datetime

import pytest


def test_date_bounds_cover_the_inclusive_end_day() -> None:
    from app.agents.qa.time_slice import date_bounds

    start, end = date_bounds("2026-05-01", "2026-05-10")

    assert start == datetime(2026, 5, 1)
    assert end == datetime(2026, 5, 11)


@pytest.mark.parametrize(
    ("start_date", "end_date"),
    [("2026/05/01", "2026-05-10"), ("2026-05-11", "2026-05-10")],
)
def test_date_bounds_reject_invalid_or_reversed_ranges(start_date: str, end_date: str) -> None:
    from app.agents.qa.time_slice import date_bounds

    with pytest.raises(ValueError, match="日期"):
        date_bounds(start_date, end_date)


def test_all_time_slice_queries_bind_event_and_half_open_date_bounds(monkeypatch) -> None:
    from app.agents.qa import time_slice

    calls: list[tuple[str, list[object]]] = []

    def fake_fetch_all(query: str, params: list[object], database_url: str) -> list[dict]:
        calls.append((query, params))
        return []

    monkeypatch.setattr(time_slice, "_fetch_all", fake_fetch_all)

    time_slice.get_market_slice("event_001", "2026-05-01", "2026-05-10")
    time_slice.get_product_slice("event_001", "2026-05-01", "2026-05-10")
    time_slice.get_sales_slice("event_001", "2026-05-01", "2026-05-10")
    time_slice.get_discussion_slice("event_001", "外观", "2026-05-01", "2026-05-10")

    assert calls
    for query, params in calls:
        assert "%s" in query
        assert params[0] == "event_001"
        assert datetime(2026, 5, 1) in params
        assert datetime(2026, 5, 11) in params
    assert any("外观" in params for _, params in calls)

