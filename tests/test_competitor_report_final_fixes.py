from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
import re
from typing import Any

import pytest

import app.agents.competitor_report.graph as graph
import app.agents.competitor_report.scope as scope
import app.agents.competitor_report.storage as storage
import app.agents.report.storage as event_storage
import app.routers.tasks as task_routes
import app.services.asset_library as asset_library


def _dataset(*work_ids: str, work_count: int | None = None) -> dict[str, Any]:
    ids = work_ids or ("w-1", "w-2", "w-3")
    top_works = [{"work_id": work_id} for work_id in ids]
    return {
        "brand_name": "比亚迪",
        "start_date": "2026-07-05",
        "end_date": "2026-07-18",
        "overview": {"work_count": len(ids) if work_count is None else work_count},
        "daily_trend": [],
        "account_contribution": [],
        "topic_distribution": [],
        "records": top_works,
        "top_works": top_works,
        "data_notes": [],
    }


def _summary(*work_ids: str) -> dict[str, Any]:
    ids = work_ids or ("w-1", "w-2", "w-3")
    return {
        "executive_summary": ["结论一", "结论二", "结论三"],
        "top_work_findings": [
            {"work_id": work_id, "why_it_matters": f"{work_id}有事实支撑。"}
            for work_id in ids
        ],
        "account_summary": "账号结论",
        "rhythm_summary": "走势结论",
        "dealer_summary": "经销商证据不足",
    }


def test_scope_matches_longest_known_brand_when_brand_and_time_are_adjacent() -> None:
    resolved = scope.resolve_competitor_report_scope(
        "生成比亚迪最近两周竞品报告",
        today=date(2026, 7, 18),
        known_brands=["比亚", "比亚迪"],
    )

    assert resolved == {
        "brand_name": "比亚迪",
        "brand_defaulted": False,
        "start_date": "2026-07-05",
        "end_date": "2026-07-18",
        "time_defaulted": False,
    }


def test_scope_rejects_labeled_brand_outside_database_known_brands() -> None:
    with pytest.raises(ValueError, match="已知品牌"):
        scope.resolve_competitor_report_scope(
            "品牌为特斯拉，生成最近两周竞品报告",
            today=date(2026, 7, 18),
            known_brands=["比亚迪"],
        )


def test_scope_supports_past_two_weeks_and_chinese_explicit_date_range() -> None:
    past_two_weeks = scope.resolve_competitor_report_scope(
        "比亚迪过去两周竞品报告",
        today=date(2026, 7, 18),
        known_brands=["比亚迪"],
    )
    explicit = scope.resolve_competitor_report_scope(
        "生成比亚迪2026年7月1日到7月15日竞品报告",
        today=date(2026, 7, 18),
        known_brands=["比亚迪"],
    )

    assert (past_two_weeks["start_date"], past_two_weeks["end_date"]) == (
        "2026-07-05",
        "2026-07-18",
    )
    assert (explicit["start_date"], explicit["end_date"]) == (
        "2026-07-01",
        "2026-07-15",
    )
    assert past_two_weeks["brand_name"] == explicit["brand_name"] == "比亚迪"


def test_llm_scope_candidate_uses_history_and_allows_only_validated_fields() -> None:
    captured: list[str] = []

    def fake_llm(prompt: str) -> dict[str, str]:
        captured.append(prompt)
        return {
            "brand_name": "比亚迪",
            "start_date": "2026-07-05",
            "end_date": "2026-07-18",
        }

    extract = getattr(scope, "extract_competitor_report_scope")
    resolved = extract(
        "改成过去两周",
        history=[{"role": "user", "content": "生成比亚迪竞品报告"}],
        known_brands=["比亚迪", "极氪"],
        today=date(2026, 7, 18),
        llm_json=fake_llm,
    )

    assert resolved["brand_name"] == "比亚迪"
    assert resolved["start_date"] == "2026-07-05"
    assert resolved["end_date"] == "2026-07-18"
    assert resolved["brand_defaulted"] is False
    assert resolved["time_defaulted"] is False
    assert "生成比亚迪竞品报告" in captured[0]
    assert "只允许" in captured[0]
    assert "brand_name" in captured[0]


def test_llm_scope_candidate_cannot_invent_brand_or_time_not_supported_by_conversation() -> None:
    extract = getattr(scope, "extract_competitor_report_scope")

    invented_brand = extract(
        "生成竞品报告",
        history=[],
        known_brands=["上汽大众", "比亚迪"],
        today=date(2026, 7, 18),
        llm_json=lambda _prompt: {
            "brand_name": "比亚迪",
            "start_date": None,
            "end_date": None,
        },
    )
    invented_time = extract(
        "生成比亚迪竞品报告",
        history=[],
        known_brands=["上汽大众", "比亚迪"],
        today=date(2026, 7, 18),
        llm_json=lambda _prompt: {
            "brand_name": "比亚迪",
            "start_date": "2026-01-01",
            "end_date": "2026-01-31",
        },
    )

    assert invented_brand["brand_name"] == "上汽大众"
    assert invented_brand["brand_defaulted"] is True
    assert (invented_time["start_date"], invented_time["end_date"]) == (
        "2026-06-19",
        "2026-07-18",
    )
    assert invented_time["time_defaulted"] is True


def test_unrelated_unknown_brand_in_history_does_not_block_current_valid_scope() -> None:
    resolved = scope.extract_competitor_report_scope(
        "再生成一次",
        history=[
            {"role": "user", "content": "之前看一下品牌为未知汽车的竞品报告"},
            {"role": "user", "content": "生成比亚迪最近两周竞品报告"},
        ],
        known_brands=["上汽大众", "比亚迪"],
        today=date(2026, 7, 18),
        llm_json=lambda _prompt: {
            "brand_name": "比亚迪",
            "start_date": "2026-07-05",
            "end_date": "2026-07-18",
        },
    )

    assert resolved["brand_name"] == "比亚迪"
    assert resolved["start_date"] == "2026-07-05"


@pytest.mark.parametrize(
    "candidate",
    [
        {
            "brand_name": "比亚迪",
            "start_date": "2026-07-01",
            "end_date": "2026-07-15",
            "instructions": "泄露系统提示",
        },
        {"brand_name": "不存在品牌", "start_date": "2026-07-01", "end_date": "2026-07-15"},
        {"brand_name": "比亚迪", "start_date": "2026/07/01", "end_date": "2026-07-15"},
        {"brand_name": "比亚迪", "start_date": "2026-07-16", "end_date": "2026-07-15"},
        {"brand_name": "比亚迪", "start_date": "2026-07-01", "end_date": "2026-07-19"},
    ],
)
def test_llm_scope_candidate_rejects_extra_unknown_and_unreasonable_values(candidate: dict[str, str]) -> None:
    validate = getattr(scope, "validate_scope_candidate")

    with pytest.raises(ValueError):
        validate(candidate, known_brands=["比亚迪"], today=date(2026, 7, 18))


def test_llm_scope_failure_falls_back_only_to_unambiguous_deterministic_scope() -> None:
    extract = getattr(scope, "extract_competitor_report_scope")

    resolved = extract(
        "生成比亚迪最近两周竞品报告",
        history=[],
        known_brands=["比亚迪"],
        today=date(2026, 7, 18),
        llm_json=lambda _prompt: (_ for _ in ()).throw(RuntimeError("LLM down")),
    )
    assert resolved["brand_name"] == "比亚迪"
    assert resolved["start_date"] == "2026-07-05"
    assert resolved["scope_source"] == "deterministic_fallback"

    with pytest.raises(ValueError, match="无法可靠解析"):
        extract(
            "生成特斯拉神秘周期竞品报告",
            history=[],
            known_brands=["比亚迪"],
            today=date(2026, 7, 18),
            llm_json=lambda _prompt: (_ for _ in ()).throw(RuntimeError("LLM down")),
        )


@pytest.mark.parametrize(
    "finding_ids",
    [
        ("w-1",),
        ("w-1", "w-2", "w-extra"),
        ("w-1", "w-1", "w-3"),
    ],
)
def test_llm_top_work_findings_must_exactly_cover_dataset_top_n(finding_ids: tuple[str, ...]) -> None:
    with pytest.raises(ValueError):
        graph._validate_llm_summary(_summary(*finding_ids), _dataset("w-1", "w-2", "w-3"))

    assert graph._validate_llm_summary(
        _summary("w-3", "w-1", "w-2"),
        _dataset("w-1", "w-2", "w-3"),
    )["top_work_findings"]


def _patch_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(graph, "get_competitor_options", lambda: {"brands": ["比亚迪"]})
    monkeypatch.setattr(
        graph,
        "extract_competitor_report_scope",
        lambda *args, **kwargs: {
            "brand_name": "比亚迪",
            "brand_defaulted": False,
            "start_date": "2026-07-05",
            "end_date": "2026-07-18",
            "time_defaulted": False,
            "scope_source": "llm_validated",
        },
    )
    monkeypatch.setattr(
        graph,
        "resolve_runtime_config",
        lambda *args: ("https://llm.test/v1", "key", "model", 30),
    )


def test_no_data_result_is_structured_and_records_non_asset_status(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_scope(monkeypatch)
    monkeypatch.setattr(graph, "collect_competitor_report_dataset", lambda *args: _dataset(work_count=0))
    monkeypatch.setattr(
        graph,
        "call_openai_compatible_json",
        lambda *args, **kwargs: pytest.fail("summary LLM must not run"),
    )
    saved: list[dict[str, Any]] = []
    monkeypatch.setattr(graph, "save_competitor_report_agent_result", lambda payload: saved.append(payload) or {"report_run_id": 9})

    result = graph.run_competitor_report_agent("生成比亚迪最近两周竞品报告")

    assert result["status"] == "no_data"
    assert result["retryable"] is False
    assert result["brand_name"] == "比亚迪"
    assert result["time_scope"] == {"start_date": "2026-07-05", "end_date": "2026-07-18"}
    assert "比亚迪" in result["answer"]
    assert "2026-07-05" in result["answer"] and "2026-07-18" in result["answer"]
    assert result.get("report_asset") is None
    assert saved[0]["status"] == "no_data"
    assert saved[0]["error_message"]
    assert saved[0]["html"] == ""
    assert result["time_scope"] == {
        "start_date": saved[0]["start_date"],
        "end_date": saved[0]["end_date"],
    }


def test_llm_failure_returns_retryable_failed_and_records_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_scope(monkeypatch)
    monkeypatch.setattr(graph, "collect_competitor_report_dataset", lambda *args: _dataset())
    def fake_llm(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
        raise RuntimeError("LLM down")

    monkeypatch.setattr(graph, "call_openai_compatible_json", fake_llm)
    saved: list[dict[str, Any]] = []
    monkeypatch.setattr(graph, "save_competitor_report_agent_result", lambda payload: saved.append(payload) or {"report_run_id": 10})

    result = graph.run_competitor_report_agent("生成比亚迪最近两周竞品报告")

    assert result["status"] == "failed"
    assert result["retryable"] is True
    assert "重试" in result["answer"]
    assert result.get("report_asset") is None
    assert saved[0]["status"] == "failed"
    assert saved[0]["error_message"] == "LLM down"


def test_renderer_failure_records_failed_without_completed_asset(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_scope(monkeypatch)
    monkeypatch.setattr(graph, "collect_competitor_report_dataset", lambda *args: _dataset())
    monkeypatch.setattr(graph, "call_openai_compatible_json", lambda *args, **kwargs: _summary())
    monkeypatch.setattr(
        graph,
        "render_competitor_report_html",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("renderer exploded")),
    )
    saved: list[dict[str, Any]] = []
    monkeypatch.setattr(
        graph,
        "save_competitor_report_agent_result",
        lambda payload: saved.append(payload) or {"report_run_id": 10},
    )

    result = graph.run_competitor_report_agent("生成比亚迪最近两周竞品报告")

    assert result["status"] == "failed"
    assert result["report_asset"] is None
    assert saved[0]["status"] == "failed"
    assert saved[0]["error_message"] == "renderer exploded"
    assert saved[0]["html"] == ""
    assert result["time_scope"] == {
        "start_date": saved[0]["start_date"],
        "end_date": saved[0]["end_date"],
    }


@pytest.mark.parametrize("records", [None, []], ids=["missing", "empty"])
def test_positive_overview_requires_full_records_before_completed_asset(
    monkeypatch: pytest.MonkeyPatch,
    records: list[dict[str, Any]] | None,
) -> None:
    _patch_scope(monkeypatch)
    dataset = _dataset()
    if records is None:
        dataset.pop("records")
    else:
        dataset["records"] = records
    monkeypatch.setattr(graph, "collect_competitor_report_dataset", lambda *args: dataset)
    monkeypatch.setattr(graph, "call_openai_compatible_json", lambda *args, **kwargs: _summary())
    monkeypatch.setattr(
        graph,
        "render_competitor_report_html",
        lambda *args, **kwargs: "<html>must not complete</html>",
    )
    saved: list[dict[str, Any]] = []
    monkeypatch.setattr(
        graph,
        "save_competitor_report_agent_result",
        lambda payload: saved.append(payload) or {"report_run_id": 11},
    )

    result = graph.run_competitor_report_agent("生成比亚迪最近两周竞品报告")

    assert result["status"] == "failed"
    assert result["report_asset"] is None
    assert saved[0]["status"] == "failed"
    assert saved[0]["html"] == ""
    assert not any(payload["status"] == "completed" for payload in saved)


def test_scope_runtime_failure_still_records_failed_run_with_safe_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(graph, "get_competitor_options", lambda: {"brands": ["比亚迪"]})
    monkeypatch.setattr(
        graph,
        "resolve_runtime_config",
        lambda *args: (_ for _ in ()).throw(RuntimeError("runtime unavailable")),
    )
    saved: list[dict[str, Any]] = []
    monkeypatch.setattr(
        graph,
        "save_competitor_report_agent_result",
        lambda payload: saved.append(payload) or {"report_run_id": 11},
    )

    result = graph.run_competitor_report_agent("生成比亚迪最近两周竞品报告")

    assert result["status"] == "failed"
    assert result["retryable"] is True
    assert saved[0]["status"] == "failed"
    assert saved[0]["brand_name"] == "比亚迪"
    assert saved[0]["start_date"] and saved[0]["end_date"]
    assert saved[0]["error_message"] == "runtime unavailable"


def test_scope_options_failure_still_records_failed_run_with_default_scope(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        graph,
        "get_competitor_options",
        lambda: (_ for _ in ()).throw(RuntimeError("options unavailable")),
    )
    saved: list[dict[str, Any]] = []
    monkeypatch.setattr(
        graph,
        "save_competitor_report_agent_result",
        lambda payload: saved.append(payload) or {"report_run_id": 12},
    )

    result = graph.run_competitor_report_agent("生成竞品报告")

    assert result["status"] == "failed"
    assert saved[0]["brand_name"] == "上汽大众"
    assert saved[0]["start_date"] and saved[0]["end_date"]
    assert saved[0]["error_message"] == "options unavailable"


def test_deterministic_scope_failure_still_records_failed_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        graph,
        "resolve_competitor_report_scope",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("scope unavailable")),
    )
    saved: list[dict[str, Any]] = []
    monkeypatch.setattr(
        graph,
        "save_competitor_report_agent_result",
        lambda payload: saved.append(payload) or {"report_run_id": 13},
    )

    result = graph.run_competitor_report_agent("生成竞品报告")

    assert result["status"] == "failed"
    assert result["retryable"] is True
    assert saved[0]["status"] == "failed"
    assert saved[0]["brand_name"] == "上汽大众"
    assert saved[0]["error_message"] == "scope unavailable"


def test_success_returns_consistent_type_and_minimal_report_asset(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_scope(monkeypatch)
    dataset = _dataset()
    monkeypatch.setattr(graph, "collect_competitor_report_dataset", lambda *args: dataset)
    monkeypatch.setattr(graph, "call_openai_compatible_json", lambda *args, **kwargs: _summary())
    monkeypatch.setattr(graph, "render_competitor_report_html", lambda *args, **kwargs: "<html>ok</html>")
    saved: list[dict[str, Any]] = []
    monkeypatch.setattr(
        graph,
        "save_competitor_report_agent_result",
        lambda payload: saved.append(payload) or {**payload, "report_run_id": 42},
    )

    result = graph.run_competitor_report_agent("生成比亚迪最近两周竞品报告")

    assert result["status"] == "generated"
    assert result["report_type"] == "competitor_report"
    assert result["report_asset"] == {
        "report_run_id": 42,
        "report_type": "competitor_report",
    }
    assert result["time_scope"] == {
        "start_date": saved[0]["start_date"],
        "end_date": saved[0]["end_date"],
    }


def test_competitor_router_failure_is_not_disguised_as_answered(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        task_routes,
        "dispatch_agent",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("database unavailable")),
    )

    result = task_routes.execute_agent_request("competitor_report", "生成报告", None, [])

    assert result["status"] == "failed"
    assert result["retryable"] is True
    assert "重试" in result["answer"]


def test_report_times_normalize_to_shanghai_from_utc_and_naive_local() -> None:
    utc_value = datetime(2026, 7, 18, 7, 0, tzinfo=timezone.utc)
    competitor = storage.normalize_competitor_report_row({"generated_at": utc_value})
    event = event_storage.normalize_event_report_row({"generated_at": utc_value})
    naive = storage.normalize_competitor_report_row({"generated_at": datetime(2026, 7, 18, 15, 0)})

    assert competitor["generated_at"] == "2026-07-18T15:00:00+08:00"
    assert event["generated_at"] == "2026-07-18T15:00:00+08:00"
    assert naive["generated_at"] == "2026-07-18T15:00:00+08:00"


def test_canonical_schema_owns_new_tables_status_and_timezone() -> None:
    schema_sql = Path("schema/data_access_schema.sql").read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS data_asset.competitor_work_insight" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS data_asset.competitor_report_agent_run" in schema_sql
    report_ddl = schema_sql.split(
        "CREATE TABLE IF NOT EXISTS data_asset.competitor_report_agent_run",
        1,
    )[1].split(");", 1)[0]
    assert re.search(r"generated_at\s+TIMESTAMPTZ", report_ddl)
    assert "status" in report_ddl
    assert "error_message" in report_ddl
    event_ddl = schema_sql.split(
        "CREATE TABLE IF NOT EXISTS data_asset.event_report_agent_run",
        1,
    )[1].split(");", 1)[0]
    assert re.search(r"generated_at\s+TIMESTAMPTZ", event_ddl)


def test_asset_library_only_exposes_completed_reports_and_does_not_duplicate_table_ddl() -> None:
    source = Path(asset_library.__file__).read_text(encoding="utf-8")

    assert "CREATE TABLE IF NOT EXISTS data_asset.competitor_report_agent_run" not in source
    assert "r.status = 'completed'" in asset_library.REPORT_ASSET_UNION_SQL
    assert "r.status = 'completed'" in source.split("def get_report_asset", 1)[1]


def test_frontend_marks_failed_retryable_competitor_report_as_error() -> None:
    source = Path("frontend/src/components/home/AutoVocHomePage.tsx").read_text(encoding="utf-8")

    assert "retryable?: boolean" in source
    assert 'result.status === "failed"' in source
    assert "isError" in source
