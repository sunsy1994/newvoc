from __future__ import annotations


def sample_sales_dashboard() -> dict:
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
        "sales_lead_quality": {
            "summary": {
                "labeled_comment_count": 248,
                "vehicle_related_count": 205,
                "vehicle_related_rate": 82.7,
                "sales_intent_comment_count": 78,
                "sales_intent_rate": 31.5,
                "strong_signal_count": 27,
                "mid_signal_count": 24,
                "mid_high_purchase_signal_count": 51,
                "mid_high_purchase_signal_rate": 20.6,
                "rule_based_conclusion": "本事件产生了可跟进销售线索。",
            },
            "intent_distribution": [{"label": "询价", "count": 32, "rate": 41.0}],
            "purchase_signal_distribution": [
                {"label": "强购买信号", "count": 27, "rate": 34.6},
                {"label": "中购买信号", "count": 24, "rate": 30.8},
            ],
            "profile_segments": [
                {
                    "segment_id": "signal_strong",
                    "label": "强购买信号",
                    "summary": {"user_count": 12, "profiled_user_count": 4, "top_profile_label": "家庭出行型"},
                    "profile_distribution": [{"label": "家庭出行型", "count": 4, "rate": 33.3}],
                    "users": [{"comment_user_id": "u_001", "nickname": "九月九的酒", "platform": "懂车帝", "purchase_signal": "强"}],
                }
            ],
            "evidence_comments": [
                {
                    "comment_id": "c_001",
                    "comment_author_name": "九月九的酒",
                    "platform": "懂车帝",
                    "comment_text": "价格合适就准备去店里看看。",
                    "purchase_signal": "强",
                    "comment_intent": "询价",
                    "interaction_cnt": 8,
                }
            ],
        },
        "sales_lead_source_efficiency": {
            "summary": {
                "high_intent_comment_count": 51,
                "strong_signal_comment_count": 27,
                "top_platform": "懂车帝",
                "top_content": "T6 静态体验",
                "rule_based_conclusion": "懂车帝贡献了最多高意向线索。",
            },
            "platform_efficiency": [
                {
                    "platform": "懂车帝",
                    "total_comment_count": 100,
                    "high_intent_comment_count": 32,
                    "strong_signal_comment_count": 18,
                    "high_intent_rate": 32.0,
                }
            ],
            "content_leads": [
                {
                    "content_id": "post_001",
                    "title": "T6 静态体验",
                    "platform": "懂车帝",
                    "high_intent_comment_count": 16,
                    "strong_signal_comment_count": 7,
                }
            ],
            "lead_comments": [
                {
                    "comment_id": "c_002",
                    "comment_author_name": "e元船舶",
                    "platform": "抖音",
                    "comment_text": "想知道现在有没有优惠。",
                    "purchase_signal": "中",
                    "comment_intent": "优惠",
                    "interaction_cnt": 5,
                }
            ],
        },
    }


def test_build_sales_report_context_keeps_sales_story_sections() -> None:
    from app.services.report_agent import build_sales_report_context

    context = build_sales_report_context(sample_sales_dashboard())

    assert context["event_overview"]["event_name"] == "ID.AURA T6 launch"
    assert context["lead_quality"]["summary"]["sales_intent_comment_count"] == 78
    assert context["lead_quality"]["profile_segments"][0]["label"] == "强购买信号"
    assert context["lead_source"]["summary"]["top_platform"] == "懂车帝"
    assert context["recommended_follow_up_users"][0]["nickname"] == "九月九的酒"


def test_render_sales_report_prompt_injects_json_context() -> None:
    from app.services.report_agent import render_sales_report_prompt

    prompt = render_sales_report_prompt(
        "Summarize sales VOC.\nInput:\n{{sales_context_json}}",
        {"lead_quality": {"summary": {"sales_intent_comment_count": 78}}},
    )

    assert "{{sales_context_json}}" not in prompt
    assert '"sales_intent_comment_count": 78' in prompt
    assert "只使用给定信息" in prompt


def test_run_sales_report_agent_returns_fixed_narrative_and_builder_charts(monkeypatch) -> None:
    from app.services import report_agent

    captured = {}
    monkeypatch.setattr(report_agent, "get_voc_event_sales_dashboard", lambda event_id, database_url=None: sample_sales_dashboard())
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
            "prompt_version": "sales_report_v2",
            "prompt_content": (
                '{"headline":"","executive_summary":"","section_insights":'
                '{"sales_funnel":"","sales_signals":"","sales_intents":"","sales_sources":""},'
                '"data_notes":[]}\n{{sales_context_json}}'
            ),
        },
    )

    def fake_call(prompt, *, base_url, api_key, model, timeout_seconds):
        captured.update({"prompt": prompt, "base_url": base_url, "model": model})
        return {
            "headline": "销售测试标题",
            "executive_summary": "销售测试摘要",
            "section_insights": {
                "sales_funnel": "漏斗判断",
                "sales_signals": "信号判断",
                "sales_intents": "意图判断",
                "sales_sources": "",
            },
            "data_notes": ["销售数据说明"],
            "structured_report": {
                "charts": [{"chart_id": "llm-chart", "template_id": "F3", "data": [{"value": 999}]}],
            },
        }

    monkeypatch.setattr(report_agent, "call_openai_compatible_json", fake_call)
    monkeypatch.setattr(report_agent, "save_sales_report_agent_result", lambda result, database_url=None: result)

    result = report_agent.run_sales_report_agent("event_001")

    assert result["event_id"] == "event_001"
    assert result["prompt_version"] == "sales_report_v2"
    assert result["summary"]["report_narrative"] == {
        "headline": "销售测试标题",
        "executive_summary": "销售测试摘要",
        "section_insights": {
                "sales_funnel": "漏斗判断",
                "sales_signals": "信号判断",
                "sales_intents": "意图判断",
                "sales_sources": "懂车帝贡献了最多高意向线索。",
        },
        "data_notes": ["销售数据说明"],
    }
    charts = result["summary"]["structured_report"]["charts"]
    assert [chart["template_id"] for chart in charts] == ["L13", "F4", "F5", "F6"]
    assert [chart["insight"] for chart in charts] == ["漏斗判断", "信号判断", "意图判断", "懂车帝贡献了最多高意向线索。"]
    assert charts[0]["data"][-1] == {"stage": "中/强购买信号", "count": 51}
    assert all(chart["chart_id"] != "llm-chart" for chart in charts)
    assert result["context"]["lead_source"]["summary"]["top_platform"] == "懂车帝"
    assert "ID.AURA T6 launch" in result["rendered_prompt"]
    assert captured["base_url"] == "https://llm.example/v1"
    assert captured["model"] == "report-model"


def test_sales_report_agent_api_runs_and_reads_latest(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    def fake_run(event_id, **kwargs):
        return {
            "event_id": event_id,
            "prompt_version": "sales_report_v1",
            "summary": {"report_markdown": "# Sales Report", "data_notes": []},
            "context": {"lead_quality": {"summary": {"sales_intent_comment_count": 78}}},
            "rendered_prompt": "Sales report",
        }

    def fake_latest(event_id, **kwargs):
        return {
            "event_id": event_id,
            "prompt_version": "sales_report_v1",
            "generated_at": "2026-06-25T10:00:00",
            "summary": {"report_markdown": "# Cached Sales Report", "data_notes": []},
            "context": {"lead_quality": {"summary": {"sales_intent_comment_count": 78}}},
            "rendered_prompt": "Cached sales report",
        }

    monkeypatch.setattr("app.routers.tasks.run_sales_report_agent", fake_run)
    monkeypatch.setattr("app.routers.tasks.get_latest_sales_report_agent_result", fake_latest)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    run_response = client.post("/api/voc/events/event_001/sales/report-agent/run")
    latest_response = client.get("/api/voc/events/event_001/sales/report-agent/latest")

    assert run_response.status_code == 200
    assert run_response.json()["summary"]["report_markdown"] == "# Sales Report"
    assert latest_response.status_code == 200
    assert latest_response.json()["summary"]["report_markdown"] == "# Cached Sales Report"


def test_sales_report_agent_api_returns_404_without_cached_summary(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    monkeypatch.setattr("app.routers.tasks.get_latest_sales_report_agent_result", lambda event_id, **kwargs: None)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.get("/api/voc/events/event_001/sales/report-agent/latest")

    assert response.status_code == 404
