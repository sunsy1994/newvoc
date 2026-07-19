from datetime import datetime
from decimal import Decimal
from typing import Any

import app.services.asset_library as asset_library
from app.services.asset_library import ASSET_DEFINITIONS, SELECT_SQL, build_like_pattern, list_assets, normalize_row


class FakeReportCursor:
    def __init__(self, calls: list[tuple[str, Any]], rows: list[dict[str, Any]]) -> None:
        self.calls = calls
        self.rows = rows
        self.result: list[dict[str, Any]] = []

    def __enter__(self) -> "FakeReportCursor":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, query: str, params: Any = None) -> None:
        self.calls.append((query, params))
        if "count(*)" in query:
            self.result = [{"count": len(self.rows)}]
        elif "LIMIT %s OFFSET %s" in query:
            self.result = self.rows
        elif "summary_json" in query and params:
            self.result = [
                {
                    "report_type": "event_report",
                    "report_run_id": params[0],
                    "subject_name": "IDT6 上市事件",
                    "generated_at": datetime(2026, 7, 18, 10, 0),
                    "view_kind": "structured",
                    "summary_json": {"structured_report": {"title": "事件报告", "charts": []}},
                }
            ]
        elif " r.html" in query and params:
            self.result = [
                {
                    "report_type": "competitor_report",
                    "report_run_id": params[0],
                    "subject_name": "比亚迪",
                    "generated_at": datetime(2026, 7, 18, 11, 0),
                    "view_kind": "html",
                    "html": "<!doctype html><html><body>竞品报告</body></html>",
                }
            ]

    def fetchone(self) -> dict[str, Any] | None:
        return self.result[0] if self.result else None

    def fetchall(self) -> list[dict[str, Any]]:
        return self.result


class FakeReportConnection:
    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.rows = rows or []

    def __enter__(self) -> "FakeReportConnection":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def cursor(self, **_kwargs: Any) -> FakeReportCursor:
        return FakeReportCursor(self.calls, self.rows)


def test_asset_definitions_expose_only_business_columns() -> None:
    forbidden = {"event_id", "content_id", "author_id", "comment_id", "event_key", "content_key", "author_key", "ingest_batch_id", "raw_source_key"}

    for definition in ASSET_DEFINITIONS.values():
        keys = {column["key"] for column in definition.columns}
        assert keys
        assert not keys.intersection(forbidden)


def test_event_asset_columns_are_business_facing() -> None:
    labels = [column["label"] for column in ASSET_DEFINITIONS["events"].columns]

    assert labels == [
        "事件名称",
        "事件类型",
        "品牌",
        "车型",
        "开始时间",
        "结束时间",
        "状态",
        "内容数",
        "评论数",
        "作者数",
        "KOL内容数",
        "总互动量",
    ]


def test_author_and_kol_assets_are_separate() -> None:
    assert ASSET_DEFINITIONS["authors"].label == "作者资产"
    assert ASSET_DEFINITIONS["kols"].label == "KOL资产"
    assert "(a.is_kol = false OR a.is_kol IS NULL)" in ASSET_DEFINITIONS["authors"].base_where
    assert "a.is_kol = true" in ASSET_DEFINITIONS["kols"].base_where

    author_columns = {column["key"] for column in ASSET_DEFINITIONS["authors"].columns}
    kol_columns = {column["key"] for column in ASSET_DEFINITIONS["kols"].columns}
    assert "is_kol" not in author_columns
    assert {"content_cnt", "received_comment_cnt", "total_engagement"}.issubset(author_columns)
    assert {"content_cnt", "received_comment_cnt", "total_engagement"}.issubset(kol_columns)


def test_comment_user_asset_is_aggregated_from_comments() -> None:
    definition = ASSET_DEFINITIONS["comment_users"]

    assert definition.label == "评论用户资产"
    assert [column["key"] for column in definition.columns] == [
        "platform",
        "comment_author_name",
        "location",
        "comment_cnt",
        "participated_content_cnt",
        "participated_event_cnt",
        "like_cnt",
        "reply_cnt",
        "latest_comment_at",
    ]


def test_build_like_pattern_escapes_search_text() -> None:
    assert build_like_pattern("  ID_100%  ") == "%ID\\_100\\%%"


def test_normalize_row_converts_decimal_values() -> None:
    assert normalize_row({"total_engagement": Decimal("12"), "rate": Decimal("1.5")}) == {
        "total_engagement": 12,
        "rate": 1.5,
    }


def test_report_assets_union_search_count_and_paginate_without_internal_fields(monkeypatch) -> None:
    rows = [
        {
            "report_type": "competitor_report",
            "subject_name": "比亚迪",
            "generated_at": datetime(2026, 7, 18, 11, 0),
            "report_run_id": 8,
            "view_kind": "html",
        },
        {
            "report_type": "event_report",
            "subject_name": "IDT6 上市事件",
            "generated_at": datetime(2026, 7, 18, 10, 0),
            "report_run_id": 7,
            "view_kind": "structured",
        },
    ]
    connection = FakeReportConnection(rows)
    monkeypatch.setattr(asset_library.psycopg, "connect", lambda *_args, **_kwargs: connection)

    payload = list_assets("reports", q="  比亚迪  ", limit=1, offset=1, database_url="fake-db")

    assert payload["rows"] == [
        {**rows[0], "generated_at": "2026-07-18T11:00:00"},
        {**rows[1], "generated_at": "2026-07-18T10:00:00"},
    ]
    assert all(set(row) == {"report_type", "subject_name", "generated_at", "report_run_id", "view_kind"} for row in payload["rows"])
    count_query, count_params = next(call for call in connection.calls if "count(*)" in call[0])
    data_query, data_params = next(call for call in connection.calls if "LIMIT %s OFFSET %s" in call[0])
    for query in (count_query, data_query):
        assert "UNION ALL" in query
        assert "event_report_agent_run" in query
        assert "competitor_report_agent_run" in query
        assert "subject_name" in query
        assert "rendered_prompt" not in query
        assert "context_json" not in query
    assert count_params == ["%比亚迪%"]
    assert data_params == ["%比亚迪%", 1, 1]
    assert "ORDER BY generated_at DESC NULLS LAST, report_type, report_run_id DESC" in data_query


def test_report_asset_definition_has_no_legacy_prompt_or_context_projection() -> None:
    report_definition = ASSET_DEFINITIONS["reports"]
    report_sql = " ".join([SELECT_SQL["reports"], report_definition.from_sql, *report_definition.search_columns])

    assert "rendered_prompt" not in report_sql
    assert "context_json" not in report_sql
    assert "summary_json" not in report_sql
    assert "prompt_version" not in report_sql


def test_report_asset_detail_returns_only_the_required_event_or_html_view(monkeypatch) -> None:
    connection = FakeReportConnection()
    monkeypatch.setattr(asset_library.psycopg, "connect", lambda *_args, **_kwargs: connection)

    event_report = asset_library.get_report_asset("event_report", 7, database_url="fake-db")
    competitor_report = asset_library.get_report_asset("competitor_report", 8, database_url="fake-db")

    assert event_report == {
        "report_type": "event_report",
        "report_run_id": 7,
        "subject_name": "IDT6 上市事件",
        "generated_at": "2026-07-18T10:00:00",
        "view_kind": "structured",
        "structured_report": {"title": "事件报告", "charts": []},
    }
    assert competitor_report == {
        "report_type": "competitor_report",
        "report_run_id": 8,
        "subject_name": "比亚迪",
        "generated_at": "2026-07-18T11:00:00",
        "view_kind": "html",
        "html": "<!doctype html><html><body>竞品报告</body></html>",
    }
    assert all("rendered_prompt" not in payload and "context" not in payload for payload in (event_report, competitor_report))


def test_report_asset_detail_rejects_unknown_type_and_non_positive_id() -> None:
    for report_type, report_run_id in (("unknown", 1), ("event_report", 0), ("competitor_report", -1)):
        try:
            asset_library.get_report_asset(report_type, report_run_id, database_url="fake-db")
        except (KeyError, ValueError):
            pass
        else:
            raise AssertionError("invalid report reference must be rejected before querying")
