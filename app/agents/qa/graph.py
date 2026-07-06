from __future__ import annotations

from datetime import datetime
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.qa import parser, tools
from app.agents.qa.state import MAX_REACT_ROUNDS, QaAgentState


def initialize_node(state: QaAgentState) -> QaAgentState:
    asked_at = datetime.fromisoformat(state["asked_at"])
    event = tools.resolve_event_context(event_id=state.get("event_id"), event_name=None)
    state["event"] = event or {}
    state["time_scope"] = tools.resolve_time_scope(state["question"], asked_at=asked_at, event=event)
    state["round_count"] = 0
    state["observations"] = []
    state["draft_answer"] = ""
    state["suggested_questions"] = []
    return state


def decide_node(state: QaAgentState) -> QaAgentState:
    decision = parser.decide(state)
    state["action"] = decision.get("tool_name") or ""
    state["arguments"] = decision.get("arguments") or {}
    state["needs_clarification"] = bool(decision.get("needs_clarification"))
    state["clarification_question"] = decision.get("clarification_question") or ""
    state["sufficient"] = bool(decision.get("finish"))
    if not state["needs_clarification"] and not state["sufficient"] and state["action"] not in tools.ALLOWED_TOOLS:
        raise ValueError(f"不支持的问答工具：{state['action'] or '空工具'}。")
    return state


def route_after_decide(state: QaAgentState) -> str:
    if state.get("needs_clarification"):
        return "clarify"
    if state.get("sufficient"):
        return "finalize"
    return "execute_tool"


def execute_tool_node(state: QaAgentState) -> QaAgentState:
    arguments = dict(state.get("arguments") or {})
    if state.get("event_id") and not arguments.get("event_id"):
        arguments["event_id"] = state["event_id"]
    observation = tools.execute_qa_tool(state["action"], arguments, state["time_scope"])
    state["round_count"] = int(state.get("round_count") or 0) + 1
    event = observation.get("event") or state.get("event") or {}
    if event.get("event_id"):
        state["event"] = event
        state["event_id"] = str(event["event_id"])
        state["time_scope"] = tools.resolve_time_scope(
            state["question"], asked_at=datetime.fromisoformat(state["asked_at"]), event=event
        )
        observation["time_scope"] = state["time_scope"]
    state.setdefault("observations", []).append(observation)
    return state


def revise_node(state: QaAgentState) -> QaAgentState:
    revision = parser.revise(state)
    state["draft_answer"] = revision["answer"]
    state["sufficient"] = bool(revision.get("sufficient"))
    state["suggested_questions"] = revision.get("suggested_questions") or []
    return state


def route_after_revise(state: QaAgentState) -> str:
    if state.get("sufficient") or int(state.get("round_count") or 0) >= MAX_REACT_ROUNDS:
        return "finalize"
    return "decide"


def clarify_node(state: QaAgentState) -> QaAgentState:
    state["answer"] = state.get("clarification_question") or "请补充需要分析的事件名称。"
    return state


def finalize_node(state: QaAgentState) -> QaAgentState:
    event_name = str((state.get("event") or {}).get("event_name") or "跨事件范围")
    scope = state.get("time_scope") or {}
    data_scopes = list(dict.fromkeys(str(item.get("data_scope")) for item in state.get("observations") or [] if item.get("data_scope")))
    data_scope = "、".join(data_scopes) or "当前可用事件数据"
    answer = state.get("draft_answer") or "当前证据不足，暂时无法形成可靠回答。"
    footer = f"事件名称：{event_name}\n统计区间：{scope.get('label', '未确定')}\n数据口径：{data_scope}"
    state["answer"] = answer if "统计区间：" in answer else f"{answer}\n\n{footer}"
    state["data_scope"] = data_scope
    return state


def build_qa_graph():
    graph = StateGraph(QaAgentState)
    graph.add_node("initialize", initialize_node)
    graph.add_node("decide", decide_node)
    graph.add_node("execute_tool", execute_tool_node)
    graph.add_node("revise", revise_node)
    graph.add_node("clarify", clarify_node)
    graph.add_node("finalize", finalize_node)
    graph.set_entry_point("initialize")
    graph.add_edge("initialize", "decide")
    graph.add_conditional_edges("decide", route_after_decide, {"clarify": "clarify", "finalize": "finalize", "execute_tool": "execute_tool"})
    graph.add_edge("execute_tool", "revise")
    graph.add_conditional_edges("revise", route_after_revise, {"decide": "decide", "finalize": "finalize"})
    graph.add_edge("clarify", END)
    graph.add_edge("finalize", END)
    return graph.compile()

def run_qa_agent(
    question: str,
    event_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
    *,
    asked_at: datetime | None = None,
) -> dict[str, Any]:
    anchor = asked_at or datetime.now(tools.SHANGHAI_TZ)
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=tools.SHANGHAI_TZ)
    else:
        anchor = anchor.astimezone(tools.SHANGHAI_TZ)
    result = build_qa_graph().invoke(
        {
            "question": question.strip(),
            "event_id": event_id,
            "history": parser.normalize_qa_history(history),
            "asked_at": anchor.isoformat(),
        }
    )
    needs_clarification = bool(result.get("needs_clarification"))
    return {
        "status": "needs_clarification" if needs_clarification else "answered",
        "answer": result.get("answer") or "",
        "suggested_questions": result.get("suggested_questions") or [],
        "requires_clarification": needs_clarification,
        "event_name": (result.get("event") or {}).get("event_name") or "跨事件范围",
        "time_scope": result.get("time_scope") or {},
        "data_scope": result.get("data_scope") or "",
        "react_rounds": int(result.get("round_count") or 0),
    }
