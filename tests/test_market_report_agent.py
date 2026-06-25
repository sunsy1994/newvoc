from __future__ import annotations


def sample_market_dashboard() -> dict:
    return {
        "event": {
            "event_id": "event_001",
            "event_name": "ID.AURA T6 launch",
            "brand_name": "FAW-Volkswagen",
            "model_name": "ID.AURA T6",
            "event_type": "new_launch",
            "event_status": "active",
            "start_time": "2026-05-10",
            "end_time": "2026-05-24",
        },
        "overview_metrics": {
            "total_volume": 273,
            "content_count": 20,
            "comment_count": 253,
            "kol_count": 3,
            "kol_content_count": 8,
            "total_engagement": 12000,
        },
        "volume_rhythm": {
            "summary": {
                "rhythm_type": "burst",
                "peak_date": "2026-05-17",
                "peak_volume": 211,
                "peak_volume_rate": 77.3,
                "has_secondary_peak": False,
                "rule_based_conclusion": "The event volume concentrated on one peak day.",
            }
        },
        "subject_story": {
            "summary": {
                "dominant_subject_type": "KOL",
                "kol_engagement_rate": 68.5,
                "top_kol_type": "vehicle review KOL",
                "rule_based_conclusion": "KOL content drove most of the engagement.",
            },
            "top_authors": [{"author_name": "Auto Reviewer A", "content_count": 3, "total_engagement": 6000}],
        },
        "platform_story": {
            "summary": {
                "core_platform": "Douyin",
                "core_platform_volume_rate": 82.1,
                "core_platform_effective_comment_rate": 84.3,
                "core_platform_purchase_signal_rate": 19.8,
                "rule_based_conclusion": "Douyin contributed the main event volume.",
            },
            "platform_efficiency": [{"platform": "Douyin", "total_volume": 220}],
        },
        "comment_quality": {
            "summary": {
                "labeled_comment_count": 253,
                "vehicle_related_rate": 84.3,
                "top_aspect": "appearance",
                "top_intent": "purchase intention",
                "positive_rate": 52.4,
                "negative_rate": 12.8,
                "mid_high_purchase_signal_rate": 19.8,
                "rule_based_conclusion": "Users discussed appearance with visible purchase signals.",
            },
            "sentiment_distribution": [{"label": "positive", "count": 120, "rate": 52.4}],
            "purchase_signal_distribution": [{"label": "strong", "count": 18, "rate": 7.1}],
        },
        "user_profile_distribution": [{"main_label": "family travel", "user_cnt": 51}],
        "regional_response_story": {"summary": {"top_location": "Shanghai", "top_location_comment_rate": 31.2}},
        "topic_spread_story": {
            "summary": {"top_topic": "#T6", "topic_count": 6, "top_topic_comment_count": 120},
            "topics": [{"topic": "#T6", "content_count": 6, "comment_count": 120, "total_engagement": 9000}],
        },
        "hot_posts": [{"title": "T6 real experience", "total_engagement": 9000, "platform": "Douyin"}],
    }


def test_build_market_report_context_keeps_business_story_sections() -> None:
    from app.services.report_agent import build_market_report_context

    context = build_market_report_context(sample_market_dashboard())

    assert context["event_overview"]["event_name"] == "ID.AURA T6 launch"
    assert context["event_overview"]["start_time"] == "2026-05-10"
    assert context["scale"]["total_volume"] == 273
    assert context["rhythm"]["rhythm_type"] == "burst"
    assert context["hot_topics"]["summary"]["top_topic"] == "#T6"
    assert context["kol_and_authors"]["summary"]["top_kol_type"] == "vehicle review KOL"
    assert context["audience"]["user_profile_distribution"][0]["main_label"] == "family travel"
    assert context["feedback_quality"]["summary"]["mid_high_purchase_signal_rate"] == 19.8
    assert context["evidence"]["hot_posts"][0]["title"] == "T6 real experience"


def test_render_market_report_prompt_injects_json_context() -> None:
    from app.services.report_agent import render_market_report_prompt

    prompt = render_market_report_prompt(
        "Summarize the market dashboard.\nInput:\n{{market_context_json}}",
        {"event_overview": {"event_name": "ID.AURA T6 launch"}},
    )

    assert "{{market_context_json}}" not in prompt
    assert '"event_name": "ID.AURA T6 launch"' in prompt
    assert "只使用给定信息" in prompt


def test_normalize_market_report_summary_keeps_markdown_report_and_notes() -> None:
    from app.services.report_agent import normalize_market_report_summary

    summary = normalize_market_report_summary(
        {
            "report_markdown": "# Market Report\n\n## Event\nLaunch event",
            "data_notes": ["Comment location is not real user residence."],
        }
    )

    assert summary["report_markdown"].startswith("# Market Report")
    assert summary["data_notes"] == ["Comment location is not real user residence."]


def test_run_market_report_agent_returns_prompt_and_context_for_transparency(monkeypatch) -> None:
    from app.services import report_agent

    captured = {}
    monkeypatch.setattr(report_agent, "get_voc_event_market_dashboard", lambda event_id, database_url=None: sample_market_dashboard())
    monkeypatch.setattr(
        report_agent,
        "get_runtime_ai_config",
        lambda database_url=None: {
            "base_url": "https://llm.example/v1",
            "api_key": "secret",
            "model_name": "report-model",
            "timeout_seconds": 30,
        },
    )
    monkeypatch.setattr(
        report_agent,
        "get_default_prompt_template",
        lambda scene, database_url=None: {
            "prompt_version": "market_report_v1",
            "prompt_content": "Market report\n{{market_context_json}}",
        },
    )

    def fake_call(prompt, *, base_url, api_key, model, timeout_seconds):
        captured.update({"prompt": prompt, "base_url": base_url, "api_key": api_key, "model": model, "timeout_seconds": timeout_seconds})
        return {
            "report_markdown": "# Market Report\n\n## Event Overview\nThis is a new launch event.",
            "data_notes": ["Input is based on event-level VOC data."],
        }

    monkeypatch.setattr(report_agent, "call_openai_compatible_json", fake_call)
    monkeypatch.setattr(report_agent, "save_market_report_agent_result", lambda result, database_url=None: result)

    result = report_agent.run_market_report_agent("event_001")

    assert result["event_id"] == "event_001"
    assert result["prompt_version"] == "market_report_v1"
    assert result["summary"]["report_markdown"].startswith("# Market Report")
    assert result["summary"]["data_notes"] == ["Input is based on event-level VOC data."]
    assert result["context"]["event_overview"]["event_name"] == "ID.AURA T6 launch"
    assert result["rendered_prompt"] == captured["prompt"]
    assert "ID.AURA T6 launch" in result["rendered_prompt"]
    assert captured["base_url"] == "https://llm.example/v1"
    assert captured["model"] == "report-model"


def test_run_market_report_agent_falls_back_to_builtin_prompt(monkeypatch) -> None:
    from app.services import report_agent

    monkeypatch.setattr(report_agent, "get_voc_event_market_dashboard", lambda event_id, database_url=None: sample_market_dashboard())
    monkeypatch.setattr(
        report_agent,
        "get_runtime_ai_config",
        lambda database_url=None: {
            "base_url": "https://llm.example/v1",
            "api_key": "secret",
            "model_name": "report-model",
            "timeout_seconds": 30,
        },
    )
    monkeypatch.setattr(report_agent, "get_default_prompt_template", lambda scene, database_url=None: (_ for _ in ()).throw(ValueError("missing")))
    monkeypatch.setattr(report_agent, "call_openai_compatible_json", lambda *args, **kwargs: {"report_markdown": "# ok"})
    monkeypatch.setattr(report_agent, "save_market_report_agent_result", lambda result, database_url=None: result)

    result = report_agent.run_market_report_agent("event_001")

    assert result["prompt_version"] == report_agent.DEFAULT_MARKET_REPORT_PROMPT_VERSION
    assert result["summary"]["report_markdown"] == "# ok"


def test_market_report_agent_api_runs_summary(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    captured = {}

    def fake_run(event_id, **kwargs):
        captured["event_id"] = event_id
        return {
            "event_id": event_id,
            "prompt_version": "market_report_v1",
            "summary": {
                "report_markdown": "# Market Report\n\nThis is a launch event.",
                "data_notes": [],
            },
            "context": {"event_overview": {"event_name": "ID.AURA T6 launch"}},
            "rendered_prompt": "Market report",
        }

    monkeypatch.setattr("app.routers.tasks.run_market_report_agent", fake_run)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.post("/api/voc/events/event_001/market/report-agent/run")

    assert response.status_code == 200
    assert response.json()["summary"]["report_markdown"].startswith("# Market Report")
    assert response.json()["rendered_prompt"] == "Market report"
    assert captured["event_id"] == "event_001"


def test_market_report_agent_api_returns_latest_cached_summary(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    captured = {}

    def fake_latest(event_id, **kwargs):
        captured["event_id"] = event_id
        return {
            "event_id": event_id,
            "prompt_version": "market_report_v1",
            "generated_at": "2026-06-22T10:00:00",
            "summary": {
                "report_markdown": "# Cached Market Report\n\nThis is cached.",
                "data_notes": [],
            },
            "context": {"event_overview": {"event_name": "ID.AURA T6 launch"}},
            "rendered_prompt": "Cached prompt",
        }

    monkeypatch.setattr("app.routers.tasks.get_latest_market_report_agent_result", fake_latest)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.get("/api/voc/events/event_001/market/report-agent/latest")

    assert response.status_code == 200
    assert response.json()["summary"]["report_markdown"].startswith("# Cached Market Report")
    assert response.json()["rendered_prompt"] == "Cached prompt"
    assert captured["event_id"] == "event_001"


def test_market_report_agent_api_returns_404_without_cached_summary(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    monkeypatch.setattr("app.routers.tasks.get_latest_market_report_agent_result", lambda event_id, **kwargs: None)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.get("/api/voc/events/event_001/market/report-agent/latest")

    assert response.status_code == 404
