from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def test_qa_agent_has_focused_package_boundary() -> None:
    root = Path("app/agents/qa")
    for name in ["__init__.py", "state.py", "tools.py", "prompts.py", "parser.py", "graph.py"]:
        assert (root / name).exists()

    from app.agents.qa import run_qa_agent

    assert callable(run_qa_agent)


def test_qa_history_keeps_latest_six_valid_bounded_messages() -> None:
    from app.agents.qa.parser import normalize_qa_history

    history = [
        {"role": "system", "content": "不可进入上下文"},
        *({"role": "user" if index % 2 == 0 else "assistant", "content": f"消息{index}"} for index in range(7)),
        {"role": "assistant", "content": "  "},
        {"role": "user", "content": "价格" * 700},
    ]

    normalized = normalize_qa_history(history)

    assert len(normalized) == 6
    assert [item["content"] for item in normalized[:2]] == ["消息2", "消息3"]
    assert normalized[-1]["role"] == "user"
    assert len(normalized[-1]["content"]) == 1200


def test_qa_prompts_include_follow_up_history_as_context_not_facts() -> None:
    from app.agents.qa.prompts import build_decision_prompt, build_revision_prompt

    state = {
        "question": "那价格呢？",
        "history": [
            {"role": "user", "content": "IDT6上市的用户主要认可什么？"},
            {"role": "assistant", "content": "用户主要认可外观。"},
        ],
        "event": {"event_name": "IDT6上市"},
        "time_scope": {"label": "事件完整周期"},
        "observations": [],
        "round_count": 0,
    }

    decision_prompt = build_decision_prompt(state)
    revision_prompt = build_revision_prompt(state)

    for prompt in (decision_prompt, revision_prompt):
        assert "IDT6上市的用户主要认可什么" in prompt
        assert "那价格呢" in prompt
        assert "历史回答不是事实来源" in prompt


def test_default_time_scope_is_last_30_calendar_days_in_shanghai() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 7, 6, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    scope = resolve_time_scope("最近情况怎么样？", asked_at=asked_at)

    assert scope == {
        "mode": "default_30_days",
        "start_date": "2026-06-07",
        "end_date": "2026-07-06",
        "label": "2026-06-07 至 2026-07-06（提问时点近30天）",
    }


def test_explicit_time_scope_overrides_default_range() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 7, 6, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    scope = resolve_time_scope("分析2026-05-01到2026-05-10的事件", asked_at=asked_at)

    assert scope["mode"] == "explicit"
    assert scope["start_date"] == "2026-05-01"
    assert scope["end_date"] == "2026-05-10"
    assert "用户指定" in scope["label"]


def test_specific_event_uses_full_event_period_when_time_is_not_explicit() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 7, 6, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    event = {"event_name": "IDT6上市", "start_time": "2026-05-17T09:00:00", "end_time": "2026-05-20T18:00:00"}
    scope = resolve_time_scope("这个事件为什么爆发？", asked_at=asked_at, event=event)

    assert scope == {
        "mode": "event_period",
        "start_date": "2026-05-17",
        "end_date": "2026-05-20",
        "label": "2026-05-17 至 2026-05-20（事件完整周期）",
    }


def test_market_tool_wraps_existing_dashboard_with_scope(monkeypatch) -> None:
    from app.agents.qa import tools

    dashboard = {
        "event": {"event_id": "event_001", "event_name": "IDT6上市"},
        "overview_metrics": {"total_volume": 273},
        "volume_rhythm": {"summary": {"peak_volume_rate": 77.3}},
    }
    monkeypatch.setattr(tools, "get_voc_event_market_dashboard", lambda event_id: dashboard)
    monkeypatch.setattr(tools, "build_market_report_context", lambda payload: {"scale": payload["overview_metrics"], "rhythm": payload["volume_rhythm"]["summary"]})
    scope = {"mode": "event_period", "start_date": "2026-05-17", "end_date": "2026-05-20", "label": "事件完整周期"}

    result = tools.execute_qa_tool("get_market_story", {"event_id": "event_001"}, scope)

    assert result["tool_name"] == "get_market_story"
    assert result["event"]["event_name"] == "IDT6上市"
    assert result["time_scope"] == scope
    assert result["facts"]["scale"]["total_volume"] == 273
    assert result["data_scope"] == "市场看板结构化数据"


def test_qa_tools_reject_unregistered_action() -> None:
    from app.agents.qa.tools import execute_qa_tool

    try:
        execute_qa_tool("run_sql", {}, {"label": "近30天"})
    except ValueError as exc:
        assert "不支持的问答工具" in str(exc)
    else:
        raise AssertionError("unregistered tool must be rejected")


def test_qa_agent_revises_previous_draft_and_stops_when_sufficient(monkeypatch) -> None:
    from app.agents.qa import graph, parser, tools

    decisions = iter(
        [
            {"tool_name": "get_market_story", "arguments": {"event_id": "event_001"}, "finish": False},
            {"tool_name": "get_product_story", "arguments": {"event_id": "event_001"}, "finish": False},
        ]
    )
    previous_drafts: list[str] = []
    revisions = iter(
        [
            {"answer": "第一轮：声量在首日集中。", "sufficient": False, "missing_evidence": "需要产品反馈", "suggested_questions": []},
            {"answer": "第二轮修正：传播集中，同时外观评价积极。", "sufficient": True, "missing_evidence": "", "suggested_questions": ["价格反馈如何？"]},
        ]
    )
    monkeypatch.setattr(parser, "decide", lambda state: next(decisions))

    def fake_revise(state: dict) -> dict:
        previous_drafts.append(state.get("draft_answer") or "")
        return next(revisions)

    monkeypatch.setattr(parser, "revise", fake_revise)
    monkeypatch.setattr(tools, "resolve_event_context", lambda **kwargs: {"event_id": "event_001", "event_name": "IDT6上市", "start_time": "2026-05-17", "end_time": "2026-05-20"})
    monkeypatch.setattr(
        tools,
        "execute_qa_tool",
        lambda name, arguments, scope: {
            "tool_name": name,
            "event": {"event_id": "event_001", "event_name": "IDT6上市", "start_time": "2026-05-17", "end_time": "2026-05-20"},
            "time_scope": scope,
            "data_scope": "事件看板结构化数据",
            "facts": {"round": name},
            "evidence": [],
            "notes": [],
        },
    )

    result = graph.run_qa_agent(
        "IDT6上市为什么爆发？",
        event_id="event_001",
        asked_at=datetime(2026, 7, 6, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
    )

    assert previous_drafts == ["", "第一轮：声量在首日集中。"]
    assert result["react_rounds"] == 2
    assert result["answer"].startswith("第二轮修正")
    assert result["event_name"] == "IDT6上市"
    assert result["time_scope"]["mode"] == "event_period"
    assert "事件名称：IDT6上市" in result["answer"]
    assert "统计区间：2026-05-17 至 2026-05-20" in result["answer"]


def test_qa_agent_never_executes_more_than_three_tool_rounds(monkeypatch) -> None:
    from app.agents.qa import graph, parser, tools

    calls: list[str] = []
    monkeypatch.setattr(parser, "decide", lambda state: {"tool_name": "list_events", "arguments": {}, "finish": False})
    monkeypatch.setattr(
        parser,
        "revise",
        lambda state: {"answer": f"第{state['round_count']}轮草稿", "sufficient": False, "missing_evidence": "仍需证据", "suggested_questions": []},
    )
    monkeypatch.setattr(tools, "resolve_event_context", lambda **kwargs: None)

    def fake_tool(name: str, arguments: dict, scope: dict) -> dict:
        calls.append(name)
        return {"tool_name": name, "event": {"event_name": "未指定事件"}, "time_scope": scope, "data_scope": "事件资产列表", "facts": {}, "evidence": [], "notes": []}

    monkeypatch.setattr(tools, "execute_qa_tool", fake_tool)
    result = graph.run_qa_agent(
        "最近有哪些异常事件？",
        asked_at=datetime(2026, 7, 6, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai")),
    )

    assert calls == ["list_events", "list_events", "list_events"]
    assert result["react_rounds"] == 3
    assert result["answer"].startswith("第3轮草稿")


def test_qa_agent_rejects_invalid_tool_before_execution(monkeypatch) -> None:
    from app.agents.qa import graph, parser, tools

    monkeypatch.setattr(parser, "decide", lambda state: {"tool_name": "run_sql", "arguments": {}, "finish": False})
    monkeypatch.setattr(tools, "resolve_event_context", lambda **kwargs: None)
    monkeypatch.setattr(tools, "execute_qa_tool", lambda *args: (_ for _ in ()).throw(AssertionError("tool must not run")))

    try:
        graph.run_qa_agent("执行SQL")
    except ValueError as exc:
        assert "不支持的问答工具" in str(exc)
    else:
        raise AssertionError("invalid action must be rejected")
