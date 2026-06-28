from __future__ import annotations

from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.data_question import parser, tools
from app.agents.data_question.prompts import build_answer_prompt
from app.agents.data_question.state import DataQuestionState, SUGGESTIONS_BY_ACTION


def clarify_node(state: DataQuestionState) -> DataQuestionState:
    state["status"] = "needs_clarification"
    state["answer"] = state.get("clarification_question") or "请补充一下你想查询的事件或指标。"
    state["suggested_questions"] = []
    return state


def execute_tool_node(state: DataQuestionState) -> DataQuestionState:
    state["tool_result"] = tools.execute_tool(state)
    return state


def compose_node(state: DataQuestionState) -> DataQuestionState:
    payload = parser.call_configured_llm(build_answer_prompt(state))
    answer = str(payload.get("answer") or "").strip()
    if not answer:
        raise ValueError("AI没有返回可展示的问数答案。")
    state["status"] = "answered"
    state["answer"] = answer
    state["suggested_questions"] = SUGGESTIONS_BY_ACTION.get(state.get("action") or "", [])
    return state


def build_data_question_graph():
    graph = StateGraph(DataQuestionState)
    graph.add_node("understand", parser.understand)
    graph.add_node("validate", parser.validate)
    graph.add_node("clarify", clarify_node)
    graph.add_node("execute_tool", execute_tool_node)
    graph.add_node("compose", compose_node)
    graph.set_entry_point("understand")
    graph.add_edge("understand", "validate")
    graph.add_conditional_edges("validate", parser.route_after_validate, {"clarify": "clarify", "execute_tool": "execute_tool"})
    graph.add_edge("clarify", END)
    graph.add_edge("execute_tool", "compose")
    graph.add_edge("compose", END)
    return graph.compile()


def run_data_question_agent(
    question: str,
    event_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = build_data_question_graph().invoke(
        {"question": question.strip(), "event_id": event_id, "history": parser.normalize_history(history)}
    )
    return {
        "status": result.get("status"),
        "answer": result.get("answer") or "",
        "suggested_questions": result.get("suggested_questions") or [],
        "requires_clarification": result.get("status") == "needs_clarification",
    }
