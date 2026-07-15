from __future__ import annotations

import json
import re
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.insight import parser, tools
from app.agents.insight.state import MAX_MODEL_ROUNDS, InsightAgentState


RESULT_LIST_FIELDS = (
    "reaction_cards",
    "audience_cards",
    "impact_cards",
    "expression_themes",
    "evidence_comments",
    "similar_events",
    "limitations",
)


def _normalized_history(history: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    result = []
    for item in (history or [])[-10:]:
        role = str(item.get("role") or "")
        content = str(item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            result.append({"role": role, "content": content})
    return result


def _empty_insight_result(state: InsightAgentState) -> dict[str, Any]:
    gate = state.get("gate") or {}
    return {
        "status": state.get("status") or "insufficient_data",
        "scenario": state.get("scenario") or {},
        "confidence": "insufficient" if state.get("status") == "insufficient_data" else "low",
        "data_scope": {
            "candidate_event_count": len(state.get("candidate_events") or []),
            "similar_event_count": len(state.get("similar_events") or []),
            "relevant_comment_count": int(gate.get("comment_count") or 0),
        },
        **{field: [] for field in RESULT_LIST_FIELDS},
    }


def collect_candidates_node(state: InsightAgentState) -> InsightAgentState:
    state["candidate_events"] = tools.list_candidate_events({}, event_id=state.get("event_id"), limit=30)
    state["react_rounds"] = 0
    return state


def parse_and_rank_node(state: InsightAgentState) -> InsightAgentState:
    parsed = parser.parse_and_rank(
        state.get("question") or "",
        state.get("candidate_events") or [],
        state.get("history") or [],
    )
    state["react_rounds"] = 1
    state["scenario"] = parsed.get("scenario") or {}
    state["clarification_question"] = str(parsed.get("clarification_question") or "")
    if parsed.get("status") == "needs_clarification":
        state["status"] = "needs_clarification"
        return state

    refreshed = tools.list_candidate_events(state["scenario"], event_id=state.get("event_id"), limit=100)
    by_id = {str(item.get("event_id")): item for item in refreshed}
    ranked_events = []
    for ranking in parsed.get("ranked_events") or []:
        if ranking.get("similarity") not in {"strong", "medium"}:
            continue
        event = by_id.get(str(ranking.get("event_id") or ""))
        if not event:
            continue
        ranked_events.append({**event, **ranking})
    state["candidate_events"] = refreshed
    state["similar_events"] = ranked_events[:5]
    return state


def route_after_parse(state: InsightAgentState) -> str:
    return "finalize" if state.get("status") == "needs_clarification" else "collect_evidence"


def collect_evidence_node(state: InsightAgentState) -> InsightAgentState:
    evidence_events = []
    for candidate in state.get("similar_events") or []:
        evidence = tools.get_event_reaction_evidence(candidate, state.get("scenario") or {})
        evidence["similarity"] = candidate.get("similarity")
        evidence["similarities"] = candidate.get("similarities") or []
        evidence["differences"] = candidate.get("differences") or []
        evidence_events.append(evidence)
    state["similar_events"] = evidence_events
    return state


def evidence_gate_node(state: InsightAgentState) -> InsightAgentState:
    gate_input = [
        {**item, "evidence_comments": item.get("evidence_comments") or []}
        for item in state.get("similar_events") or []
    ]
    state["gate"] = tools.evaluate_evidence_gate(gate_input)
    state["status"] = str(state["gate"]["status"])
    return state


def route_after_gate(state: InsightAgentState) -> str:
    return "simulate" if state.get("status") == "completed" else "finalize"


def simulate_node(state: InsightAgentState) -> InsightAgentState:
    state["draft_simulation"] = parser.simulate_reactions(
        state.get("scenario") or {},
        state.get("similar_events") or [],
    )
    state["react_rounds"] = int(state.get("react_rounds") or 0) + 1
    return state


def _iter_evidence_ids(simulation: dict[str, Any]) -> list[str]:
    result = []
    for field in ("reaction_cards", "audience_cards", "impact_cards"):
        for card in simulation.get(field) or []:
            result.extend(str(value) for value in card.get("evidence_event_ids") or [])
    return result


def review_simulation(simulation: dict[str, Any], *, accepted_event_ids: set[str]) -> list[str]:
    issues = []
    rendered = json.dumps(simulation, ensure_ascii=False, default=str)
    if re.search(r"\d+(?:\.\d+)?\s*%", rendered):
        issues.append("不得生成精确反应百分比")
    evidence_ids = _iter_evidence_ids(simulation)
    if any(event_id not in accepted_event_ids for event_id in evidence_ids):
        issues.append("结论引用了未通过证据门槛的事件")
    if any(not (card.get("evidence_event_ids") or []) for field in ("reaction_cards", "audience_cards", "impact_cards") for card in simulation.get(field) or []):
        issues.append("主要判断缺少事件证据引用")
    if any(keyword in rendered for keyword in ("建议", "应该立即", "营销动作")):
        issues.append("不得输出产品或营销建议")
    return issues


def review_node(state: InsightAgentState) -> InsightAgentState:
    accepted_ids = {
        str((item.get("event") or {}).get("event_id") or "")
        for item in state.get("similar_events") or []
    }
    draft = state.get("draft_simulation") or {}
    issues = review_simulation(draft, accepted_event_ids=accepted_ids)
    if issues and int(state.get("react_rounds") or 0) < MAX_MODEL_ROUNDS:
        draft = parser.revise_simulation(
            state.get("scenario") or {},
            state.get("similar_events") or [],
            draft,
            issues,
        )
        state["react_rounds"] = int(state.get("react_rounds") or 0) + 1
        issues = review_simulation(draft, accepted_event_ids=accepted_ids)
    state["draft_simulation"] = draft
    state["review_issues"] = issues
    if issues:
        state["status"] = "partial"
    return state


def _similar_event_cards(state: InsightAgentState) -> list[dict[str, Any]]:
    cards = []
    for item in state.get("similar_events") or []:
        event = item.get("event") or {}
        cards.append(
            {
                "event_id": event.get("event_id"),
                "event_name": event.get("event_name"),
                "brand_name": event.get("brand_name"),
                "model_name": event.get("model_name"),
                "relation_type": event.get("relation_type"),
                "similarity": item.get("similarity"),
                "similarities": item.get("similarities") or [],
                "differences": item.get("differences") or [],
                "comment_count": len(item.get("evidence_comments") or []),
            }
        )
    return cards


def _evidence_comment_cards(state: InsightAgentState) -> list[dict[str, Any]]:
    comments = []
    for item in state.get("similar_events") or []:
        event = item.get("event") or {}
        for comment in item.get("evidence_comments") or []:
            comments.append(
                {
                    **comment,
                    "event_id": event.get("event_id"),
                    "event_name": event.get("event_name"),
                    "relation_type": event.get("relation_type"),
                }
            )
    return comments[:30]


def finalize_node(state: InsightAgentState) -> InsightAgentState:
    status = state.get("status") or "insufficient_data"
    result = _empty_insight_result(state)
    result["similar_events"] = _similar_event_cards(state)
    result["evidence_comments"] = _evidence_comment_cards(state)
    if status == "completed":
        draft = state.get("draft_simulation") or {}
        for field in ("reaction_cards", "audience_cards", "impact_cards", "expression_themes", "limitations"):
            result[field] = draft.get(field) or []
        result["confidence"] = "medium"
        answer = "已基于相似历史事件和真实评论完成用户反应推演。"
    elif status == "partial":
        result["limitations"] = (state.get("review_issues") or []) + ["当前事件只覆盖部分场景，不形成完整用户反应结论。"]
        answer = "当前只找到部分相似事件，已展示可用证据和推演边界。"
    elif status == "needs_clarification":
        answer = state.get("clarification_question") or "请补充需要推演的具体企业动作。"
    else:
        answer = "暂无此类数据推演。当前事件库未找到足够相似的历史事件，或相关评论证据未达到推演门槛。"
    state["result"] = {
        "status": status,
        "answer": answer,
        "suggested_questions": [],
        "requires_clarification": status == "needs_clarification",
        "insight_result": result,
        "react_rounds": int(state.get("react_rounds") or 0),
    }
    return state


def build_insight_graph():
    graph = StateGraph(InsightAgentState)
    graph.add_node("collect_candidates", collect_candidates_node)
    graph.add_node("parse_and_rank", parse_and_rank_node)
    graph.add_node("collect_evidence", collect_evidence_node)
    graph.add_node("evidence_gate", evidence_gate_node)
    graph.add_node("simulate", simulate_node)
    graph.add_node("review", review_node)
    graph.add_node("finalize", finalize_node)
    graph.set_entry_point("collect_candidates")
    graph.add_edge("collect_candidates", "parse_and_rank")
    graph.add_conditional_edges("parse_and_rank", route_after_parse, {"collect_evidence": "collect_evidence", "finalize": "finalize"})
    graph.add_edge("collect_evidence", "evidence_gate")
    graph.add_conditional_edges("evidence_gate", route_after_gate, {"simulate": "simulate", "finalize": "finalize"})
    graph.add_edge("simulate", "review")
    graph.add_edge("review", "finalize")
    graph.add_edge("finalize", END)
    return graph.compile()


def run_insight_agent(
    message: str,
    event_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    result = build_insight_graph().invoke(
        {
            "question": message.strip(),
            "event_id": event_id,
            "history": _normalized_history(history),
        }
    )
    return result["result"]
