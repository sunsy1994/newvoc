from __future__ import annotations

from typing import Any

from app.agents.data_question.parser import call_configured_llm
from app.agents.qa.prompts import build_decision_prompt, build_revision_prompt
from app.agents.qa.state import QaAgentState


def normalize_qa_history(
    history: list[dict[str, Any]] | None,
    *,
    limit: int = 6,
    max_chars: int = 1200,
) -> list[dict[str, str]]:
    normalized = []
    for item in history or []:
        role = str(item.get("role") or "")
        content = str(item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            normalized.append({"role": role, "content": content[:max_chars]})
    return normalized[-limit:]


def decide(state: QaAgentState) -> dict[str, Any]:
    payload = call_configured_llm(build_decision_prompt(state))
    arguments = payload.get("arguments")
    return {
        "tool_name": str(payload.get("tool_name") or "").strip(),
        "arguments": arguments if isinstance(arguments, dict) else {},
        "finish": bool(payload.get("finish")),
        "needs_clarification": bool(payload.get("needs_clarification")),
        "clarification_question": str(payload.get("clarification_question") or "").strip(),
    }


def revise(state: QaAgentState) -> dict[str, Any]:
    payload = call_configured_llm(build_revision_prompt(state))
    answer = str(payload.get("answer") or "").strip()
    if not answer:
        raise ValueError("AI没有返回可展示的问答答案。")
    suggestions = payload.get("suggested_questions")
    return {
        "answer": answer,
        "sufficient": bool(payload.get("sufficient")),
        "missing_evidence": str(payload.get("missing_evidence") or "").strip(),
        "suggested_questions": [str(item) for item in suggestions[:3]] if isinstance(suggestions, list) else [],
    }
