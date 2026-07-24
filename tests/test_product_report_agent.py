from __future__ import annotations


def sample_product_dashboard() -> dict:
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
        "product_focus_story": {
            "summary": {
                "top_aspect": "外观",
                "aspect_count": 5,
                "total_mentions": 120,
                "rule_based_conclusion": "用户讨论集中在外观与价格。",
            },
            "aspects": [
                {
                    "aspect": "外观",
                    "comment_count": 48,
                    "mention_rate": 40.0,
                    "positive_rate": 72.9,
                    "negative_rate": 8.3,
                    "purchase_signal_rate": 18.8,
                    "evidence_comments": [{"comment_text": "这个外观确实好看", "interaction_cnt": 8}],
                },
                {
                    "aspect": "价格",
                    "comment_count": 30,
                    "mention_rate": 25.0,
                    "positive_rate": 10.0,
                    "negative_rate": 56.7,
                    "purchase_signal_rate": 12.0,
                    "evidence_comments": [{"comment_text": "价格如果再低一点就好了", "interaction_cnt": 6}],
                },
            ],
        },
        "product_opportunity_story": {
            "summary": {
                "surprise_point": "外观",
                "pain_point": "价格",
                "conversion_point": "品牌",
                "rule_based_conclusion": "外观可作为放大点，价格是主要异议。",
            },
            "surprise_points": [{"aspect": "外观", "opportunity_score": 38.2}],
            "pain_points": [{"aspect": "价格", "opportunity_score": 22.4}],
            "conversion_points": [{"aspect": "品牌", "opportunity_score": 14.1}],
        },
        "product_pko_story": {
            "summary": {
                "pko_comment_count": 22,
                "top_explicit_target": "ID.4",
                "top_dimension": "价格",
                "advantage_dimension": "外观",
                "disadvantage_dimension": "价格",
                "explicit_target_rate": 63.6,
                "clear_result_rate": 72.7,
                "rule_based_conclusion": "明确对比对象以 ID.4 为主，价格维度劣势更集中。",
            },
            "explicit_target_distribution": [{"label": "ID.4", "count": 8, "rate": 36.4}],
            "dimension_distribution": [{"label": "价格", "count": 10, "rate": 45.5}],
            "result_distribution": [
                {"label": "本车优势", "count": 7, "rate": 31.8},
                {"label": "本车劣势", "count": 9, "rate": 40.9},
            ],
            "dimension_result_matrix": [
                {
                    "dimension": "价格",
                    "total_count": 10,
                    "advantage_count": 1,
                    "disadvantage_count": 7,
                    "neutral_count": 2,
                    "top_target": "ID.4",
                }
            ],
            "evidence_comments": [
                {
                    "comment_id": "pko_001",
                    "target": "ID.4",
                    "dimension": "价格",
                    "result": "本车劣势",
                    "reason": "同价位配置感知不足",
                    "comment_text": "和ID.4比，价格没优势。",
                    "interaction_cnt": 9,
                    "published_at": "2026-05-20",
                }
            ],
        },
    }


def test_build_product_report_context_keeps_product_story_sections() -> None:
    from app.services.report_agent import build_product_report_context

    context = build_product_report_context(sample_product_dashboard())

    assert context["event_overview"]["event_name"] == "ID.AURA T6 launch"
    assert context["product_focus"]["summary"]["top_aspect"] == "外观"
    assert context["product_opportunity"]["summary"]["pain_point"] == "价格"
    assert context["pko"]["summary"]["top_explicit_target"] == "ID.4"
    assert context["evidence_comments"][0]["comment_text"] == "和ID.4比，价格没优势。"


def test_render_product_report_prompt_injects_json_context() -> None:
    from app.services.report_agent import render_product_report_prompt

    prompt = render_product_report_prompt(
        "Summarize product VOC.\nInput:\n{{product_context_json}}",
        {"product_focus": {"summary": {"top_aspect": "外观"}}},
    )

    assert "{{product_context_json}}" not in prompt
    assert '"top_aspect": "外观"' in prompt
    assert "只使用给定信息" in prompt


def test_run_product_report_agent_returns_fixed_narrative_and_builder_charts(monkeypatch) -> None:
    from app.services import report_agent

    captured = {}
    monkeypatch.setattr(report_agent, "get_voc_event_product_dashboard", lambda event_id, database_url=None: sample_product_dashboard())
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
            "prompt_version": "product_report_v2",
            "prompt_content": (
                '{"headline":"","executive_summary":"","section_insights":'
                '{"product_focus":"","product_sentiment":"","product_opportunity":"",'
                '"product_pko_relationships":"","product_pko_results":""},'
                '"data_notes":[]}\n{{product_context_json}}'
            ),
        },
    )

    def fake_call(prompt, *, base_url, api_key, model, timeout_seconds):
        captured.update({"prompt": prompt, "base_url": base_url, "model": model})
        return {
            "headline": "产品测试标题",
            "executive_summary": "产品测试摘要",
            "section_insights": {
                "product_focus": "关注判断",
                "product_sentiment": " ",
                "product_opportunity": "机会判断",
                "product_pko_relationships": "对比关系判断",
                "product_pko_results": "对比结果判断",
            },
            "data_notes": ["产品数据说明"],
            "structured_report": {
                "charts": [{"chart_id": "llm-chart", "template_id": "F3", "data": [{"value": 999}]}],
            },
        }

    monkeypatch.setattr(report_agent, "call_openai_compatible_json", fake_call)
    monkeypatch.setattr(report_agent, "save_product_report_agent_result", lambda result, database_url=None: result)

    result = report_agent.run_product_report_agent("event_001")

    assert result["event_id"] == "event_001"
    assert result["prompt_version"] == "product_report_v2"
    assert result["summary"]["report_narrative"] == {
        "headline": "产品测试标题",
        "executive_summary": "产品测试摘要",
            "section_insights": {
                "product_focus": "关注判断",
                "product_sentiment": "用户讨论集中在外观与价格。",
            "product_opportunity": "机会判断",
            "product_pko_relationships": "对比关系判断",
            "product_pko_results": "对比结果判断",
        },
        "data_notes": ["产品数据说明"],
    }
    charts = result["summary"]["structured_report"]["charts"]
    assert [chart["template_id"] for chart in charts] == ["F5", "F6", "F5", "L12", "F7"]
    assert [chart["insight"] for chart in charts] == ["关注判断", "用户讨论集中在外观与价格。", "机会判断", "对比关系判断", "对比结果判断"]
    assert charts[0]["data"] == result["context"]["product_focus"]["aspects"]
    assert charts[3]["data"][0]["comment_id"] == "pko_001"
    assert all(chart["chart_id"] != "llm-chart" for chart in charts)
    assert result["context"]["product_focus"]["summary"]["top_aspect"] == "外观"
    assert "ID.AURA T6 launch" in result["rendered_prompt"]
    assert captured["base_url"] == "https://llm.example/v1"
    assert captured["model"] == "report-model"


def test_product_report_agent_api_runs_and_reads_latest(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    def fake_run(event_id, **kwargs):
        return {
            "event_id": event_id,
            "prompt_version": "product_report_v1",
            "summary": {"report_markdown": "# Product Report", "data_notes": []},
            "context": {"product_focus": {"summary": {"top_aspect": "外观"}}},
            "rendered_prompt": "Product report",
        }

    def fake_latest(event_id, **kwargs):
        return {
            "event_id": event_id,
            "prompt_version": "product_report_v1",
            "generated_at": "2026-06-23T10:00:00",
            "summary": {"report_markdown": "# Cached Product Report", "data_notes": []},
            "context": {"product_focus": {"summary": {"top_aspect": "外观"}}},
            "rendered_prompt": "Cached product report",
        }

    monkeypatch.setattr("app.routers.tasks.run_product_report_agent", fake_run)
    monkeypatch.setattr("app.routers.tasks.get_latest_product_report_agent_result", fake_latest)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    run_response = client.post("/api/voc/events/event_001/product/report-agent/run")
    latest_response = client.get("/api/voc/events/event_001/product/report-agent/latest")

    assert run_response.status_code == 200
    assert run_response.json()["summary"]["report_markdown"] == "# Product Report"
    assert latest_response.status_code == 200
    assert latest_response.json()["summary"]["report_markdown"] == "# Cached Product Report"


def test_product_report_agent_api_returns_404_without_cached_summary(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    monkeypatch.setattr("app.routers.tasks.get_latest_product_report_agent_result", lambda event_id, **kwargs: None)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.get("/api/voc/events/event_001/product/report-agent/latest")

    assert response.status_code == 404
