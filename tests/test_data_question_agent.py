from __future__ import annotations

from pathlib import Path


def test_data_question_agent_has_focused_package_boundary() -> None:
    root = Path("app/agents/data_question")

    assert (root / "__init__.py").exists()
    assert (root / "graph.py").exists()
    assert (root / "state.py").exists()
    assert (root / "parser.py").exists()
    assert (root / "tools.py").exists()
    assert (root / "prompts.py").exists()

    from app.agents.data_question import run_data_question_agent

    assert callable(run_data_question_agent)


def sample_market_dashboard() -> dict:
    return {
        "event": {"event_id": "event_001", "event_name": "ID.AURA T6 上市"},
        "overview_metrics": {
            "total_volume": 273,
            "content_count": 20,
            "comment_count": 253,
            "kol_count": 3,
            "total_engagement": 12000,
        },
    }


def sample_home_dashboard() -> dict:
    return {
        "key_events": [
            {
                "event_id": "event_001",
                "event_name": "ID.AURA T6 上市",
                "brand_name": "一汽大众-大众品牌",
                "total_volume": 273,
            },
            {
                "event_id": "event_002",
                "event_name": "竞品新车上市",
                "brand_name": "竞品品牌",
                "total_volume": 99,
            },
        ]
    }


def configured_runtime() -> dict:
    return {
        "base_url": "https://llm.example/v1",
        "api_key": "secret",
        "model_name": "configured-model",
        "timeout_seconds": 45,
    }


def test_data_question_agent_uses_configured_llm_and_real_event_tool(monkeypatch) -> None:
    from app.agents.data_question import graph, parser, tools

    llm_calls: list[tuple[str, dict]] = []
    responses = iter(
        [
            {
                "action": "list_events",
                "arguments": {"days": 30},
                "needs_clarification": False,
                "clarification_question": "",
            },
            {
                "answer": "我先按近30天查看。系统共记录2个重点事件，其中ID.AURA T6上市声量最高。",
                "suggested_questions": ["分析这些事件的话题表现"],
            },
        ]
    )

    def fake_llm(prompt: str, **kwargs) -> dict:
        llm_calls.append((prompt, kwargs))
        return next(responses)

    monkeypatch.setattr(parser, "get_runtime_ai_config", lambda: configured_runtime())
    monkeypatch.setattr(parser, "call_openai_compatible_json", fake_llm)
    monkeypatch.setattr(tools, "get_auto_voc_home", lambda days=30: sample_home_dashboard())

    result = graph.run_data_question_agent(
        "近期有哪些事件？",
        history=[{"role": "user", "content": "帮我看看近期情况"}],
    )

    assert result["status"] == "answered"
    assert result["answer"] == "我先按近30天查看。系统共记录2个重点事件，其中ID.AURA T6上市声量最高。"
    assert result["suggested_questions"] == ["哪个事件声量最高？", "哪个事件评论最多？", "哪个事件的KOL最多？"]
    assert result["requires_clarification"] is False
    assert len(llm_calls) == 2
    assert all(call[1]["model"] == "configured-model" for call in llm_calls)
    assert "帮我看看近期情况" in llm_calls[0][0]
    assert "ID.AURA T6 上市" in llm_calls[1][0]
    assert "建议问题必须能由现有问数工具回答" in llm_calls[1][0]
    assert "event_001" not in result["answer"]


def test_data_question_agent_carries_pending_metric_into_event_clarification_reply(monkeypatch) -> None:
    from app.agents.data_question import graph, parser, tools

    captured = {}
    responses = iter(
        [
            {
                "action": "resolve_event",
                "arguments": {"event_name": "IDT6上市"},
                "needs_clarification": False,
                "clarification_question": "",
            },
            {"answer": "IDT6上市事件共有253条评论。", "suggested_questions": []},
        ]
    )
    monkeypatch.setattr(parser, "get_runtime_ai_config", lambda: configured_runtime())
    monkeypatch.setattr(parser, "call_openai_compatible_json", lambda prompt, **kwargs: next(responses))
    monkeypatch.setattr(tools, "list_voc_events", lambda q=None, limit=20: {"events": [{"event_id": "event_001", "event_name": "IDT6上市"}]})
    def fake_dashboard(event_id: str) -> dict:
        captured["event_id"] = event_id
        return sample_market_dashboard()

    monkeypatch.setattr(tools, "get_voc_event_market_dashboard", fake_dashboard)

    result = graph.run_data_question_agent(
        "IDT6上市",
        history=[
            {"role": "user", "content": "评论数是多少？"},
            {"role": "assistant", "content": "你想查看哪个事件？"},
        ],
    )

    assert result["status"] == "answered"
    assert result["answer"] == "IDT6上市事件共有253条评论。"
    assert captured == {"event_id": "event_001"}


def test_data_question_agent_queries_event_metric_then_composes_answer(monkeypatch) -> None:
    from app.agents.data_question import graph, parser, tools

    responses = iter(
        [
            {
                "action": "get_event_metric",
                "arguments": {"metric": "comment_count"},
                "needs_clarification": False,
                "clarification_question": "",
            },
            {"answer": "这个事件共有253条评论。", "suggested_questions": []},
        ]
    )
    monkeypatch.setattr(parser, "get_runtime_ai_config", lambda: configured_runtime())
    monkeypatch.setattr(parser, "call_openai_compatible_json", lambda prompt, **kwargs: next(responses))
    monkeypatch.setattr(tools, "get_voc_event_market_dashboard", lambda event_id: sample_market_dashboard())

    result = graph.run_data_question_agent("这个事件有多少评论？", event_id="event_001")

    assert result["status"] == "answered"
    assert result["answer"] == "这个事件共有253条评论。"
    assert "event_001" not in result["answer"]


def test_data_question_agent_returns_llm_clarification_without_running_tool(monkeypatch) -> None:
    from app.agents.data_question import graph, parser, tools

    monkeypatch.setattr(parser, "get_runtime_ai_config", lambda: configured_runtime())
    monkeypatch.setattr(
        parser,
        "call_openai_compatible_json",
        lambda prompt, **kwargs: {
            "action": "get_event_metric",
            "arguments": {"metric": "comment_count"},
            "needs_clarification": True,
            "clarification_question": "你想查看哪个事件的评论数？",
        },
    )
    monkeypatch.setattr(
        tools,
        "get_voc_event_market_dashboard",
        lambda event_id: (_ for _ in ()).throw(AssertionError("tool must not run")),
    )

    result = graph.run_data_question_agent("评论数是多少？")

    assert result == {
        "status": "needs_clarification",
        "answer": "你想查看哪个事件的评论数？",
        "suggested_questions": [],
        "requires_clarification": True,
    }


def test_data_question_agent_rejects_unknown_llm_action(monkeypatch) -> None:
    from app.agents.data_question import graph, parser

    monkeypatch.setattr(parser, "get_runtime_ai_config", lambda: configured_runtime())
    monkeypatch.setattr(
        parser,
        "call_openai_compatible_json",
        lambda prompt, **kwargs: {
            "action": "run_sql",
            "arguments": {"sql": "DROP TABLE data_asset.dwd_comment"},
            "needs_clarification": False,
            "clarification_question": "",
        },
    )

    try:
        graph.run_data_question_agent("执行SQL")
    except ValueError as exc:
        assert "不支持的问数动作" in str(exc)
    else:
        raise AssertionError("unknown action must be rejected")


def test_data_question_agent_api_forwards_chat_history(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    captured = {}

    def fake_dispatch(capability: str, message: str, **kwargs) -> dict:
        captured.update(capability=capability, message=message, **kwargs)
        return {
            "status": "answered",
            "answer": "近30天有2个重点事件。",
            "suggested_questions": ["哪个事件声量最高？"],
            "requires_clarification": False,
        }

    monkeypatch.setattr("app.routers.tasks.dispatch_agent", fake_dispatch)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))
    history = [
        {"role": "user", "content": "近期情况怎么样？"},
        {"role": "assistant", "content": "你想查看事件还是用户？"},
    ]

    response = client.post(
        "/api/agents/data-question/run",
        json={"question": "近期有哪些事件？", "event_id": None, "history": history},
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "近30天有2个重点事件。"
    assert captured == {
        "capability": "data_question",
        "message": "近期有哪些事件？",
        "event_id": None,
        "history": history,
    }
