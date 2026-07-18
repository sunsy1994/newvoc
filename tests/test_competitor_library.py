import app.services.competitor_library as competitor_library
from app.services.competitor_library import (
    ACCOUNT_COLUMNS,
    WORK_COLUMNS,
    build_work_filters,
)


class FakeInsightCursor:
    def __init__(self, store: dict[str, dict[str, object]], calls: list[tuple[str, object]]) -> None:
        self.store = store
        self.calls = calls
        self.row: dict[str, object] | None = None

    def __enter__(self) -> "FakeInsightCursor":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def execute(self, query: str, params: object = None) -> None:
        self.calls.append((query, params))
        if "SELECT work_id FROM data_asset.competitor_work" in query:
            work_id = params[0]
            self.row = {"work_id": work_id} if work_id == "work_001" else None
        elif "INSERT INTO data_asset.competitor_work_insight" in query:
            work_id, insight_markdown, updated_by = params
            self.store[work_id] = {
                "work_id": work_id,
                "insight_markdown": insight_markdown,
                "updated_by": updated_by,
                "updated_at": "2026-07-18T00:00:00",
            }
            self.row = self.store[work_id]
        elif "LEFT JOIN data_asset.competitor_work_insight" in query:
            self.row = self.store.get(params[0])

    def fetchone(self) -> dict[str, object] | None:
        return self.row


class FakeInsightConnection:
    def __init__(self) -> None:
        self.store: dict[str, dict[str, object]] = {}
        self.calls: list[tuple[str, object]] = []
        self.committed = False

    def __enter__(self) -> "FakeInsightConnection":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def cursor(self) -> FakeInsightCursor:
        return FakeInsightCursor(self.store, self.calls)

    def commit(self) -> None:
        self.committed = True


def test_competitor_column_definitions_are_business_facing() -> None:
    account_keys = [column["key"] for column in ACCOUNT_COLUMNS]
    work_keys = [column["key"] for column in WORK_COLUMNS]

    assert account_keys == [
        "account_name",
        "brand_name",
        "account_type",
        "is_official",
        "is_enabled",
        "account_home_url",
        "remark",
    ]
    assert "work_id" in work_keys
    assert "published_at" in work_keys
    assert "video_url" in work_keys


def test_build_work_filters_supports_published_date_range_and_query() -> None:
    where_sql, params = build_work_filters(
        q="途观",
        brand_name="上汽大众",
        account_type="经销商",
        start_date="2026-05-01",
        end_date="2026-05-31",
    )

    assert "w.published_at >= %s" in where_sql
    assert "w.published_at < (%s::date + INTERVAL '1 day')" in where_sql
    assert "w.brand_name = %s" in where_sql
    assert "w.account_type = %s" in where_sql
    assert params == ["上汽大众", "经销商", "2026-05-01", "2026-05-31", "%途观%", "%途观%", "%途观%"]


def test_competitor_work_insight_round_trip(monkeypatch) -> None:
    connection = FakeInsightConnection()
    monkeypatch.setattr(competitor_library.psycopg, "connect", lambda *_args, **_kwargs: connection)

    saved = competitor_library.save_competitor_work_insight("work_001", "## 视频介绍\n外观展示", "tester", "test-db")

    assert saved["work_id"] == "work_001"
    assert saved["insight_markdown"].startswith("## 视频介绍")
    assert competitor_library.get_competitor_work_insight("work_001", "test-db")["updated_by"] == "tester"

    cleared = competitor_library.save_competitor_work_insight("work_001", "   ", "tester", "test-db")

    assert cleared["insight_markdown"] == ""
    assert connection.committed is True
    assert all("%s" in query for query, _params in connection.calls if query.lstrip().startswith(("SELECT", "INSERT")))


def test_competitor_work_insight_rejects_missing_work(monkeypatch) -> None:
    connection = FakeInsightConnection()
    monkeypatch.setattr(competitor_library.psycopg, "connect", lambda *_args, **_kwargs: connection)

    try:
        competitor_library.save_competitor_work_insight("missing", "内容", database_url="test-db")
    except ValueError as exc:
        assert str(exc) == "Competitor work not found"
    else:
        raise AssertionError("missing work must be rejected")


def test_competitor_work_columns_include_insight_status() -> None:
    work_keys = [column["key"] for column in WORK_COLUMNS]

    assert "has_insight" in work_keys
    assert "insight_updated_at" in work_keys
