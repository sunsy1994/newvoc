from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest


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


def test_relative_month_time_scope_overrides_default_range() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 7, 7, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    scope = resolve_time_scope("idt6上市这个事件，近三个月用户在外观维度热议什么？", asked_at=asked_at)

    assert scope["mode"] == "relative"
    assert scope["start_date"] == "2026-04-07"
    assert scope["end_date"] == "2026-07-07"
    assert scope["source"] == "user_relative_phrase"
    assert scope["anchor_date"] == "2026-07-07"
    assert "自然月" in scope["label"]


def test_relative_time_scope_overrides_event_period() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 7, 7, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    event = {"event_name": "IDT6上市", "start_time": "2026-05-17T09:00:00", "end_time": "2026-05-20T18:00:00"}
    scope = resolve_time_scope("这个事件近三个月外观热议什么？", asked_at=asked_at, event=event)

    assert scope["mode"] == "relative"
    assert scope["start_date"] == "2026-04-07"
    assert scope["end_date"] == "2026-07-07"


def test_today_and_yesterday_time_scope_use_ask_date() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 7, 7, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))

    today_scope = resolve_time_scope("今天外观讨论怎么样？", asked_at=asked_at)
    yesterday_scope = resolve_time_scope("昨天外观讨论怎么样？", asked_at=asked_at)

    assert today_scope["start_date"] == "2026-07-07"
    assert today_scope["end_date"] == "2026-07-07"
    assert today_scope["source"] == "user_relative_phrase"
    assert yesterday_scope["start_date"] == "2026-07-06"
    assert yesterday_scope["end_date"] == "2026-07-06"


def test_business_week_and_month_time_scopes_do_not_include_future_dates() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 7, 7, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))

    this_week = resolve_time_scope("本周外观讨论怎么样？", asked_at=asked_at)
    last_week = resolve_time_scope("上周外观讨论怎么样？", asked_at=asked_at)
    this_month = resolve_time_scope("本月外观讨论怎么样？", asked_at=asked_at)
    last_month = resolve_time_scope("上月外观讨论怎么样？", asked_at=asked_at)

    assert this_week["start_date"] == "2026-07-06"
    assert this_week["end_date"] == "2026-07-07"
    assert last_week["start_date"] == "2026-06-29"
    assert last_week["end_date"] == "2026-07-05"
    assert this_month["start_date"] == "2026-07-01"
    assert this_month["end_date"] == "2026-07-07"
    assert last_month["start_date"] == "2026-06-01"
    assert last_month["end_date"] == "2026-06-30"


def test_named_month_time_scope_uses_anchor_year_and_past_month() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 1, 8, 10, 30, tzinfo=ZoneInfo("Asia/Shanghai"))
    scope = resolve_time_scope("12月外观讨论怎么样？", asked_at=asked_at)

    assert scope["mode"] == "named_month"
    assert scope["start_date"] == "2025-12-01"
    assert scope["end_date"] == "2025-12-31"
    assert scope["source"] == "user_month_phrase"


def test_resolve_time_scope_supports_named_month_last_week() -> None:
    from app.agents.qa.tools import resolve_time_scope

    asked_at = datetime(2026, 7, 28, 12, tzinfo=ZoneInfo("Asia/Shanghai"))

    assert resolve_time_scope("生成2026年5月最后一周的竞品动态报告", asked_at=asked_at) == {
        "mode": "named_month_last_week",
        "start_date": "2026-05-25",
        "end_date": "2026-05-31",
        "label": "2026-05-25 至 2026-05-31（用户指定2026年5月最后一周）",
        "source": "user_month_last_week_phrase",
        "anchor_date": "2026-07-28",
    }
    assert resolve_time_scope("生成5月最后一周的竞品动态报告", asked_at=asked_at)["start_date"] == "2026-05-25"
    assert resolve_time_scope("生成5月报告", asked_at=asked_at)["start_date"] == "2026-05-01"


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


def test_explicit_scope_routes_market_tool_to_time_slice(monkeypatch) -> None:
    from app.agents.qa import tools

    captured: dict[str, str] = {}

    def fake_slice(event_id: str, start_date: str, end_date: str) -> dict:
        captured.update(event_id=event_id, start_date=start_date, end_date=end_date)
        return {"summary": {"content_count": 9}, "hot_posts": []}

    monkeypatch.setattr(tools.time_slice, "get_market_slice", fake_slice)
    monkeypatch.setattr(
        tools,
        "get_voc_event_market_dashboard",
        lambda event_id: (_ for _ in ()).throw(AssertionError("explicit scope must not use full dashboard")),
    )
    scope = {
        "mode": "explicit",
        "start_date": "2026-05-01",
        "end_date": "2026-05-10",
        "label": "用户指定",
    }

    result = tools.execute_qa_tool("get_market_story", {"event_id": "event_001"}, scope)

    assert captured == {"event_id": "event_001", "start_date": "2026-05-01", "end_date": "2026-05-10"}
    assert result["facts"]["summary"]["content_count"] == 9
    assert result["data_scope"] == "市场数据（按统计区间切片）"


def test_discussion_evidence_always_uses_resolved_time_scope(monkeypatch) -> None:
    from app.agents.qa import tools

    captured: dict[str, str] = {}

    def fake_slice(event_id: str, aspect: str, start_date: str, end_date: str) -> dict:
        captured.update(event_id=event_id, aspect=aspect, start_date=start_date, end_date=end_date)
        return {"total": 1, "comments": [{"comment_text": "外观不错"}]}

    monkeypatch.setattr(tools.time_slice, "get_discussion_slice", fake_slice)
    scope = {
        "mode": "event_period",
        "start_date": "2026-05-17",
        "end_date": "2026-05-20",
        "label": "事件完整周期",
    }

    result = tools.execute_qa_tool(
        "get_discussion_evidence",
        {"event_id": "event_001", "event_name": "IDT6上市", "aspect": "外观"},
        scope,
    )

    assert captured == {
        "event_id": "event_001",
        "aspect": "外观",
        "start_date": "2026-05-17",
        "end_date": "2026-05-20",
    }
    assert result["facts"] == {"aspect": "外观", "total": 1}
    assert result["evidence"][0]["comment_text"] == "外观不错"


def test_explicit_time_scope_rejects_reversed_dates() -> None:
    from app.agents.qa.tools import resolve_time_scope

    with pytest.raises(ValueError, match="开始日期"):
        resolve_time_scope("分析2026-05-10到2026-05-01的事件")


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


def test_qa_agent_asks_for_aspect_before_discussion_evidence(monkeypatch) -> None:
    from app.agents.qa import graph, parser, tools

    monkeypatch.setattr(
        parser,
        "decide",
        lambda state: {
            "tool_name": "get_discussion_evidence",
            "arguments": {"event_id": "event_001"},
            "finish": False,
        },
    )
    monkeypatch.setattr(
        tools,
        "resolve_event_context",
        lambda **kwargs: {
            "event_id": "event_001",
            "event_name": "IDT6上市",
            "start_time": "2026-05-17",
            "end_time": "2026-05-20",
        },
    )
    monkeypatch.setattr(tools, "execute_qa_tool", lambda *args: (_ for _ in ()).throw(AssertionError("tool must not run without aspect")))

    result = graph.run_qa_agent("把这个事件的评论证据列出来", event_id="event_001")

    assert result["status"] == "needs_clarification"
    assert result["requires_clarification"] is True
    assert "产品关注点" in result["answer"]
    assert result["react_rounds"] == 0


def test_qa_agent_infers_discussion_aspect_from_question(monkeypatch) -> None:
    from app.agents.qa import graph, parser, tools

    captured_arguments: dict[str, str] = {}
    monkeypatch.setattr(
        parser,
        "decide",
        lambda state: {
            "tool_name": "get_discussion_evidence",
            "arguments": {"event_id": "event_001"},
            "finish": False,
        },
    )
    monkeypatch.setattr(
        parser,
        "revise",
        lambda state: {
            "answer": "外观惊喜点主要来自造型和辨识度。",
            "sufficient": True,
            "suggested_questions": [],
        },
    )
    monkeypatch.setattr(
        tools,
        "resolve_event_context",
        lambda **kwargs: {
            "event_id": "event_001",
            "event_name": "IDT6上市",
            "start_time": "2026-05-17",
            "end_time": "2026-05-20",
        },
    )

    def fake_tool(name: str, arguments: dict, scope: dict) -> dict:
        captured_arguments.update(arguments)
        return {
            "tool_name": name,
            "event": {"event_id": "event_001", "event_name": "IDT6上市"},
            "time_scope": scope,
            "data_scope": "产品关注点原始评论（按统计区间切片）",
            "facts": {"aspect": arguments["aspect"], "total": 1},
            "evidence": [{"comment_text": "外观很惊艳"}],
            "notes": [],
        }

    monkeypatch.setattr(tools, "execute_qa_tool", fake_tool)

    result = graph.run_qa_agent("idt6上市外观的惊喜点说了什么", event_id="event_001")

    assert captured_arguments["aspect"] == "外观"
    assert result["status"] == "answered"
    assert result["react_rounds"] == 1


def test_qa_agent_infers_event_from_question(monkeypatch) -> None:
    from app.agents.qa import graph, parser, tools

    captured_arguments: dict[str, str] = {}
    monkeypatch.setattr(
        parser,
        "decide",
        lambda state: {
            "tool_name": "get_discussion_evidence",
            "arguments": {},
            "finish": False,
        },
    )
    monkeypatch.setattr(
        parser,
        "revise",
        lambda state: {
            "answer": "外观惊喜点主要来自造型和辨识度。",
            "sufficient": True,
            "suggested_questions": [],
        },
    )
    monkeypatch.setattr(
        tools,
        "list_voc_events",
        lambda q=None, limit=20: {
            "events": [
                {
                    "event_id": "EVT-2026-001",
                    "event_name": "IDT6上市",
                    "brand_name": "一汽大众",
                    "model_name": "ID.AURA T6",
                    "start_time": "2026-05-14",
                    "end_time": "2026-05-20",
                }
            ]
        },
    )

    def fake_tool(name: str, arguments: dict, scope: dict) -> dict:
        captured_arguments.update(arguments)
        return {
            "tool_name": name,
            "event": {"event_id": arguments["event_id"], "event_name": "IDT6上市"},
            "time_scope": scope,
            "data_scope": "产品关注点原始评论（按统计区间切片）",
            "facts": {"aspect": arguments["aspect"], "total": 1},
            "evidence": [{"comment_text": "外观很惊艳"}],
            "notes": [],
        }

    monkeypatch.setattr(tools, "execute_qa_tool", fake_tool)

    result = graph.run_qa_agent("idt6上市外观的惊喜点说了什么")

    assert captured_arguments["event_id"] == "EVT-2026-001"
    assert captured_arguments["aspect"] == "外观"
    assert result["event_name"] == "IDT6上市"


def test_qa_agent_routes_kol_profile_overlap_to_market_story(monkeypatch) -> None:
    from app.agents.qa import graph, parser, tools

    calls: list[str] = []
    monkeypatch.setattr(
        parser,
        "decide",
        lambda state: {
            "tool_name": "get_discussion_evidence",
            "arguments": {},
            "finish": False,
        },
    )
    monkeypatch.setattr(
        parser,
        "revise",
        lambda state: {
            "answer": "KOL画像与目标用户重合度需要结合KOL类型和已画像用户分布判断。",
            "sufficient": True,
            "suggested_questions": [],
        },
    )
    monkeypatch.setattr(
        tools,
        "list_voc_events",
        lambda q=None, limit=20: {
            "events": [
                {
                    "event_id": "EVT-2026-001",
                    "event_name": "IDT6上市",
                    "start_time": "2026-05-14",
                    "end_time": "2026-05-20",
                }
            ]
        },
    )

    def fake_tool(name: str, arguments: dict, scope: dict) -> dict:
        calls.append(name)
        return {
            "tool_name": name,
            "event": {"event_id": arguments["event_id"], "event_name": "IDT6上市"},
            "time_scope": scope,
            "data_scope": "市场看板结构化数据",
            "facts": {"kol_and_authors": {}, "audience": {}},
            "evidence": [],
            "notes": [],
        }

    monkeypatch.setattr(tools, "execute_qa_tool", fake_tool)

    result = graph.run_qa_agent("这些KOL的粉丝画像与IDT6的目标用户重合度如何？")

    assert calls == ["get_market_story"]
    assert result["status"] == "answered"


def test_qa_agent_carries_event_from_history_for_follow_up(monkeypatch) -> None:
    from app.agents.qa import graph, parser, tools

    captured_arguments: dict[str, str] = {}
    monkeypatch.setattr(
        parser,
        "decide",
        lambda state: {
            "tool_name": "get_market_story",
            "arguments": {},
            "finish": False,
        },
    )
    monkeypatch.setattr(
        parser,
        "revise",
        lambda state: {
            "answer": "这些KOL与目标用户有一定重合。",
            "sufficient": True,
            "suggested_questions": [],
        },
    )
    monkeypatch.setattr(
        tools,
        "list_voc_events",
        lambda q=None, limit=20: {
            "events": [
                {
                    "event_id": "EVT-2026-001",
                    "event_name": "IDT6上市",
                    "start_time": "2026-05-14",
                    "end_time": "2026-05-20",
                }
            ]
        },
    )

    def fake_tool(name: str, arguments: dict, scope: dict) -> dict:
        captured_arguments.update(arguments)
        return {
            "tool_name": name,
            "event": {"event_id": arguments["event_id"], "event_name": "IDT6上市"},
            "time_scope": scope,
            "data_scope": "市场看板结构化数据",
            "facts": {},
            "evidence": [],
            "notes": [],
        }

    monkeypatch.setattr(tools, "execute_qa_tool", fake_tool)

    result = graph.run_qa_agent(
        "这些KOL的粉丝画像与目标用户重合度如何？",
        history=[{"role": "assistant", "content": "事件名称：IDT6上市\n统计区间：2026-05-14 至 2026-05-20"}],
    )

    assert captured_arguments["event_id"] == "EVT-2026-001"
    assert result["event_name"] == "IDT6上市"
