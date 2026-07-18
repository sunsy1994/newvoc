from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pytest

import app.agents.competitor_report.tools as competitor_tools
from app.agents.competitor_report.scope import resolve_competitor_report_scope
from app.agents.competitor_report.tools import collect_competitor_report_dataset


def test_scope_defaults_brand_and_last_30_days() -> None:
    scope = resolve_competitor_report_scope("生成一份竞品动态报告", today=date(2026, 7, 18))

    assert scope == {
        "brand_name": "上汽大众",
        "brand_defaulted": True,
        "start_date": "2026-06-19",
        "end_date": "2026-07-18",
        "time_defaulted": True,
    }


def test_scope_resolves_explicit_dates_and_brand() -> None:
    scope = resolve_competitor_report_scope(
        "生成比亚迪品牌2026-05-01至2026-05-31的竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["比亚迪"],
    )

    assert scope == {
        "brand_name": "比亚迪",
        "brand_defaulted": False,
        "start_date": "2026-05-01",
        "end_date": "2026-05-31",
        "time_defaulted": False,
    }


def test_scope_resolves_last_month() -> None:
    scope = resolve_competitor_report_scope("品牌为一汽大众，上个月的竞品动态报告", today=date(2026, 7, 18))

    assert scope["brand_name"] == "一汽大众"
    assert scope["brand_defaulted"] is False
    assert scope["start_date"] == "2026-06-01"
    assert scope["end_date"] == "2026-06-30"
    assert scope["time_defaulted"] is False


def test_scope_resolves_recent_two_weeks_with_default_brand() -> None:
    scope = resolve_competitor_report_scope("最近两周的竞品动态报告", today=date(2026, 7, 18))

    assert scope == {
        "brand_name": "上汽大众",
        "brand_defaulted": True,
        "start_date": "2026-07-05",
        "end_date": "2026-07-18",
        "time_defaulted": False,
    }


def test_scope_defaults_only_time_when_brand_is_specified() -> None:
    scope = resolve_competitor_report_scope("生成一份品牌为比亚迪的竞品动态报告", today=date(2026, 7, 18))

    assert scope["brand_name"] == "比亚迪"
    assert scope["brand_defaulted"] is False
    assert scope["start_date"] == "2026-06-19"
    assert scope["end_date"] == "2026-07-18"
    assert scope["time_defaulted"] is True


def test_scope_does_not_treat_report_modifier_as_brand() -> None:
    scope = resolve_competitor_report_scope("请生成一份详细的竞品动态报告", today=date(2026, 7, 18))

    assert scope["brand_name"] == "上汽大众"
    assert scope["brand_defaulted"] is True


def test_scope_does_not_treat_generic_request_as_brand() -> None:
    scope = resolve_competitor_report_scope("我想看一份竞品动态报告", today=date(2026, 7, 18))

    assert scope["brand_name"] == "上汽大众"
    assert scope["brand_defaulted"] is True


def test_scope_defaults_brand_for_plain_report_requests() -> None:
    for message in (
        "帮我做一份竞品动态报告",
        "请输出一份竞品动态报告",
        "生成一份专业的竞品动态报告",
        "生成一份完整竞品动态报告",
        "帮我写一份竞品动态报告",
        "请撰写一份竞品动态报告",
    ):
        scope = resolve_competitor_report_scope(
            message,
            today=date(2026, 7, 18),
            known_brands=["比亚迪", "极氪"],
        )

        assert scope["brand_name"] == "上汽大众", message
        assert scope["brand_defaulted"] is True, message


def test_scope_stops_labeled_brand_at_explicit_date_boundary() -> None:
    scope = resolve_competitor_report_scope(
        "品牌为比亚迪2026-05-01至2026-05-31的竞品动态报告",
        today=date(2026, 7, 18),
    )

    assert scope["brand_name"] == "比亚迪"
    assert scope["brand_defaulted"] is False
    assert scope["start_date"] == "2026-05-01"
    assert scope["end_date"] == "2026-05-31"


def test_scope_stops_labeled_brand_before_report_suffix() -> None:
    scope = resolve_competitor_report_scope(
        "生成一份品牌为极氪的竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["比亚迪"],
    )

    assert scope["brand_name"] == "极氪"
    assert scope["brand_defaulted"] is False


def test_scope_resolves_possessive_brand_before_report() -> None:
    scope = resolve_competitor_report_scope(
        "生成一份比亚迪的竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["比亚迪"],
    )

    assert scope["brand_name"] == "比亚迪"
    assert scope["brand_defaulted"] is False


def test_scope_defaults_ambiguous_bare_brand_report() -> None:
    scope = resolve_competitor_report_scope(
        "极氪竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["极氪"],
    )

    assert scope["brand_name"] == "上汽大众"
    assert scope["brand_defaulted"] is True


def test_scope_resolves_known_brand_suffix() -> None:
    scope = resolve_competitor_report_scope(
        "我想看比亚迪品牌的竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["比亚迪"],
    )

    assert scope["brand_name"] == "比亚迪"
    assert scope["brand_defaulted"] is False


def test_scope_resolves_two_character_known_brand_possessive() -> None:
    scope = resolve_competitor_report_scope(
        "帮我看看极氪的竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["比亚迪", "极氪"],
    )

    assert scope["brand_name"] == "极氪"
    assert scope["brand_defaulted"] is False


def test_scope_prefers_longest_known_brand() -> None:
    scope = resolve_competitor_report_scope(
        "请输出一份上汽大众品牌的竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["大众", "上汽大众"],
    )

    assert scope["brand_name"] == "上汽大众"
    assert scope["brand_defaulted"] is False


def test_scope_does_not_match_known_brand_suffix_inside_longer_brand() -> None:
    scope = resolve_competitor_report_scope(
        "请输出一份上汽大众品牌的竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["大众"],
    )

    assert scope["brand_name"] == "上汽大众"
    assert scope["brand_defaulted"] is True


def test_scope_does_not_match_known_brand_possessive_inside_longer_brand() -> None:
    scope = resolve_competitor_report_scope(
        "上汽大众的竞品动态报告",
        today=date(2026, 7, 18),
        known_brands=["大众"],
    )

    assert scope["brand_name"] == "上汽大众"
    assert scope["brand_defaulted"] is True


def test_scope_defaults_natural_brand_without_known_brands() -> None:
    for message in ("比亚迪品牌的竞品动态报告", "比亚迪的竞品动态报告"):
        scope = resolve_competitor_report_scope(message, today=date(2026, 7, 18))

        assert scope["brand_name"] == "上汽大众", message
        assert scope["brand_defaulted"] is True, message


class FakeReportCursor:
    def __init__(self, works: list[dict[str, Any]], insights: dict[str, str], calls: list[tuple[str, Any]]) -> None:
        self.works = works
        self.insights = insights
        self.calls = calls
        self.rows: list[dict[str, Any]] = []

    def __enter__(self) -> "FakeReportCursor":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def _scoped(self, query: str, params: Any) -> list[dict[str, Any]]:
        normalized = " ".join(query.split())
        assert "WHERE w.brand_name = %s AND w.published_at >= %s AND w.published_at < %s" in normalized
        brand_name, start_date, end_date = params[:3]
        start = datetime.fromisoformat(str(start_date))
        end = datetime.fromisoformat(str(end_date))
        return [
            work
            for work in self.works
            if work["brand_name"] == brand_name and start <= work["published_at"] < end
        ]

    @staticmethod
    def _engagement(work: dict[str, Any]) -> int:
        return sum(int(work.get(key) or 0) for key in ("interaction_like_cnt", "comment_cnt", "favorite_cnt", "share_cnt"))

    def execute(self, query: str, params: Any = None) -> None:
        self.calls.append((query, params))
        if "CREATE TABLE IF NOT EXISTS data_asset.competitor_work_insight" in query:
            self.rows = []
            return
        scoped = self._scoped(query, params)
        normalized = " ".join(query.split())
        expression = "coalesce(interaction_like_cnt,0)+coalesce(comment_cnt,0)+coalesce(favorite_cnt,0)+coalesce(share_cnt,0)"
        assert expression in normalized
        if "AS average_engagement" in query:
            total = sum(self._engagement(work) for work in scoped)
            self.rows = [{
                "work_count": len(scoped),
                "account_count": len({work["author_name"] for work in scoped}),
                "total_engagement": total,
                "average_engagement": total / len(scoped) if scoped else 0,
            }]
        elif "AS publish_date" in query:
            grouped: dict[date, list[dict[str, Any]]] = {}
            for work in scoped:
                grouped.setdefault(work["published_at"].date(), []).append(work)
            self.rows = [
                {
                    "publish_date": day,
                    "work_count": len(day_works),
                    "total_engagement": sum(self._engagement(work) for work in day_works),
                }
                for day, day_works in sorted(grouped.items())
            ]
        elif "GROUP BY author_name, account_type, is_official" in normalized:
            grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
            for work in scoped:
                key = (work["author_name"], work["account_type"], work["is_official"])
                grouped.setdefault(key, []).append(work)
            self.rows = sorted(
                [
                    {
                        "author_name": key[0],
                        "account_type": key[1],
                        "is_official": key[2],
                        "work_count": len(account_works),
                        "total_engagement": sum(self._engagement(work) for work in account_works),
                    }
                    for key, account_works in grouped.items()
                ],
                key=lambda row: (-row["total_engagement"], str(row["author_name"])),
            )
        elif "AS topic" in query:
            topics: dict[str, list[dict[str, Any]]] = {}
            for work in scoped:
                for topic in work["topic_tags"].split(",") if work.get("topic_tags") else []:
                    topics.setdefault(topic.strip().lstrip("#"), []).append(work)
            self.rows = sorted(
                [
                    {
                        "topic": topic,
                        "work_count": len(topic_works),
                        "total_engagement": sum(self._engagement(work) for work in topic_works),
                    }
                    for topic, topic_works in topics.items()
                    if topic
                ],
                key=lambda row: (-row["work_count"], -row["total_engagement"], row["topic"]),
            )
        else:
            assert "LEFT JOIN data_asset.competitor_work_insight i ON i.work_id = w.work_id" in normalized
            assert "ORDER BY total_engagement DESC, published_at DESC, work_id ASC" in normalized
            assert "LIMIT 3" in normalized, "Top works SQL must include LIMIT 3"
            for field in (
                "w.title",
                "w.author_name",
                "w.brand_name",
                "w.account_type",
                "w.is_official",
                "w.published_at",
                "w.topic_tags",
                "w.video_url",
                "w.interaction_like_cnt",
                "w.comment_cnt",
                "w.favorite_cnt",
                "w.share_cnt",
            ):
                assert field in normalized
            ranked = sorted(
                scoped,
                key=lambda work: (-self._engagement(work), -work["published_at"].timestamp(), work["work_id"]),
            )[:3]
            self.rows = [
                {**work, "total_engagement": self._engagement(work), "insight_markdown": self.insights.get(work["work_id"])}
                for work in ranked
            ]

    def fetchone(self) -> dict[str, Any] | None:
        return self.rows[0] if self.rows else None

    def fetchall(self) -> list[dict[str, Any]]:
        return self.rows


class FakeReportConnection:
    def __init__(self, works: list[dict[str, Any]], insights: dict[str, str]) -> None:
        self.works = works
        self.insights = insights
        self.calls: list[tuple[str, Any]] = []

    def __enter__(self) -> "FakeReportConnection":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def cursor(self) -> FakeReportCursor:
        return FakeReportCursor(self.works, self.insights, self.calls)


def test_fake_cursor_rejects_top_query_without_limit() -> None:
    cursor = FakeReportCursor([], {}, [])

    query = f"""
        SELECT w.work_id AS work_id, w.title, w.author_name, w.brand_name,
               w.account_type, w.is_official, w.published_at, w.topic_tags, w.video_url,
               w.interaction_like_cnt, w.comment_cnt, w.favorite_cnt, w.share_cnt,
               {competitor_tools.TOTAL_ENGAGEMENT_SQL} AS total_engagement,
               i.insight_markdown
        FROM data_asset.competitor_work w
        LEFT JOIN data_asset.competitor_work_insight i ON i.work_id = w.work_id
        WHERE {competitor_tools.SCOPE_SQL}
        ORDER BY total_engagement DESC, published_at DESC, work_id ASC
    """

    with pytest.raises(AssertionError, match="LIMIT 3"):
        cursor.execute(query, ["比亚迪", datetime(2026, 7, 1), datetime(2026, 8, 1)])


def _work(
    work_id: str,
    *,
    brand_name: str = "比亚迪",
    published_at: str,
    likes: int,
    comments: int = 0,
    favorites: int = 0,
    shares: int = 0,
    author_name: str = "账号A",
    topic_tags: str = "新能源,发布会",
) -> dict[str, Any]:
    return {
        "work_id": work_id,
        "title": f"原始标题-{work_id}",
        "author_name": author_name,
        "brand_name": brand_name,
        "account_type": "官方号" if author_name == "账号A" else "经销商",
        "is_official": author_name == "账号A",
        "published_at": datetime.fromisoformat(published_at),
        "topic_tags": topic_tags,
        "video_url": f"https://example.test/{work_id}",
        "interaction_like_cnt": likes,
        "comment_cnt": comments,
        "favorite_cnt": favorites,
        "share_cnt": shares,
    }


def test_dataset_filters_before_top3_and_returns_grounded_aggregates(monkeypatch) -> None:
    works = [
        _work("w-001", published_at="2026-07-10T10:00:00", likes=30, comments=10, favorites=5, shares=5),
        _work("w-002", published_at="2026-07-12T10:00:00", likes=30, comments=10),
        _work("w-003", published_at="2026-07-12T10:00:00", likes=35, favorites=5, author_name="账号B"),
        _work("w-004", published_at="2026-07-11T10:00:00", likes=9, shares=1, author_name="账号B"),
        _work("outside-range", published_at="2026-06-30T23:59:59", likes=999),
        _work("other-brand", brand_name="上汽大众", published_at="2026-07-15T10:00:00", likes=888),
    ]
    connection = FakeReportConnection(
        works,
        {
            "w-001": "按作品 ID 命中的解读",
            "outside-range": "不应进入范围",
            "other-brand": "同标题也不能串入",
        },
    )
    monkeypatch.setattr(competitor_tools.psycopg, "connect", lambda *_args, **_kwargs: connection)

    dataset = collect_competitor_report_dataset("比亚迪", "2026-07-01", "2026-07-31", database_url="fake-db")

    assert dataset["overview"] == {
        "work_count": 4,
        "account_count": 2,
        "total_engagement": 140,
        "average_engagement": 35,
    }
    assert [row["work_id"] for row in dataset["top_works"]] == ["w-001", "w-002", "w-003"]
    assert dataset["top_works"][0]["total_engagement"] == 50
    assert dataset["top_works"][0]["insight_markdown"] == "按作品 ID 命中的解读"
    assert dataset["top_works"][1]["insight_markdown"] == "无"
    assert dataset["top_works"][0]["title"] == "原始标题-w-001"
    assert dataset["top_works"][0]["video_url"] == "https://example.test/w-001"
    assert dataset["daily_trend"][0]["publish_date"] == "2026-07-10"
    assert dataset["account_contribution"][0]["author_name"] == "账号A"
    assert {row["topic"]: row["work_count"] for row in dataset["topic_distribution"]} == {
        "新能源": 4,
        "发布会": 4,
    }
    assert set(dataset) == {
        "brand_name",
        "start_date",
        "end_date",
        "overview",
        "daily_trend",
        "account_contribution",
        "topic_distribution",
        "top_works",
        "data_notes",
    }

    expression = "coalesce(interaction_like_cnt,0)+coalesce(comment_cnt,0)+coalesce(favorite_cnt,0)+coalesce(share_cnt,0)"
    assert "CREATE TABLE IF NOT EXISTS data_asset.competitor_work_insight" in connection.calls[0][0]
    scoped_queries = [query for query, params in connection.calls if params is not None]
    overview_query = next(query for query in scoped_queries if "AS average_engagement" in query)
    daily_query = next(query for query in scoped_queries if "AS publish_date" in query)
    account_query = next(query for query in scoped_queries if "GROUP BY author_name, account_type, is_official" in query)
    topic_query = next(query for query in scoped_queries if "AS topic" in query)
    top_query = next(query for query in scoped_queries if "LEFT JOIN data_asset.competitor_work_insight" in query)
    assert expression in overview_query
    assert expression in daily_query
    assert expression in account_query
    assert expression in topic_query
    assert expression in top_query
    assert "LIMIT 3" in top_query
    assert all(
        params[:3] == ["比亚迪", datetime(2026, 7, 1), datetime(2026, 8, 1)]
        for _query, params in connection.calls
        if params is not None
    )


def test_dataset_returns_top_n_when_fewer_than_three_works(monkeypatch) -> None:
    connection = FakeReportConnection(
        [_work("only-work", published_at="2026-07-18T12:00:00", likes=3)],
        {},
    )
    monkeypatch.setattr(competitor_tools.psycopg, "connect", lambda *_args, **_kwargs: connection)

    dataset = collect_competitor_report_dataset("比亚迪", "2026-07-18", "2026-07-18", database_url="fake-db")

    assert [row["work_id"] for row in dataset["top_works"]] == ["only-work"]
    assert dataset["top_works"][0]["insight_markdown"] == "无"
    assert any("仅有 1 条作品" in note for note in dataset["data_notes"])
