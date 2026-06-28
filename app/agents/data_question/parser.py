from __future__ import annotations

from typing import Any

from app.agents.data_question.prompts import build_action_prompt
from app.agents.data_question.state import ALLOWED_ACTIONS, DataQuestionState, METRIC_CATALOG
from app.services.comment_user_ai_profile import call_openai_compatible_json
from app.services.system_settings import get_runtime_ai_config


def normalize_history(history: list[dict[str, Any]] | None) -> list[dict[str, str]]:
    normalized = []
    for item in (history or [])[-10:]:
        role = str(item.get("role") or "")
        content = str(item.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            normalized.append({"role": role, "content": content})
    return normalized


def runtime_ai_config() -> dict[str, Any]:
    config = get_runtime_ai_config()
    if not config.get("base_url") or not config.get("api_key") or not config.get("model_name"):
        raise ValueError("请先在系统管理中维护并启用默认AI模型参数。")
    return config


def call_configured_llm(prompt: str) -> dict[str, Any]:
    config = runtime_ai_config()
    return call_openai_compatible_json(
        prompt,
        base_url=str(config["base_url"]),
        api_key=str(config["api_key"]),
        model=str(config["model_name"]),
        timeout_seconds=int(config.get("timeout_seconds") or 60),
    )


def infer_metric_from_text(text: str) -> str | None:
    normalized = text.lower()
    if "声量" in normalized:
        return "total_volume"
    if "帖子" in normalized or "主贴" in normalized or "内容数" in normalized:
        return "content_count"
    if "评论" in normalized:
        return "comment_count"
    if "kol" in normalized or "koc" in normalized:
        return "kol_count"
    if "互动" in normalized:
        return "total_engagement"
    return None


def carry_pending_event_clarification(state: DataQuestionState) -> None:
    if state.get("action") != "resolve_event":
        return
    history = state.get("history") or []
    for index in range(len(history) - 1, 0, -1):
        current = history[index]
        previous = history[index - 1]
        if current["role"] != "assistant" or "哪个事件" not in current["content"] or previous["role"] != "user":
            continue
        metric = infer_metric_from_text(previous["content"])
        if metric:
            state["action"] = "get_event_metric"
            state["arguments"] = {"event_name": state["question"], "metric": metric}
        return


def understand(state: DataQuestionState) -> DataQuestionState:
    decision = call_configured_llm(build_action_prompt(state))
    state["action"] = str(decision.get("action") or "")
    state["arguments"] = decision.get("arguments") if isinstance(decision.get("arguments"), dict) else {}
    state["needs_clarification"] = bool(decision.get("needs_clarification"))
    state["clarification_question"] = str(decision.get("clarification_question") or "").strip()
    carry_pending_event_clarification(state)
    return state


def validate(state: DataQuestionState) -> DataQuestionState:
    if state.get("needs_clarification"):
        return state
    action = state.get("action") or ""
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"不支持的问数动作：{action or '空动作'}。")

    arguments = state.setdefault("arguments", {})
    if "days" in arguments:
        try:
            arguments["days"] = max(1, min(int(arguments["days"]), 365))
        except (TypeError, ValueError) as exc:
            raise ValueError("days必须是1到365之间的整数。") from exc

    if action in {"get_event_metric", "rank_events"}:
        metric = str(arguments.get("metric") or "")
        if metric not in METRIC_CATALOG:
            state["needs_clarification"] = True
            state["clarification_question"] = state.get("clarification_question") or "你想查看声量、帖子、评论、KOL还是互动量？"

    if action == "get_event_metric" and not (state.get("event_id") or arguments.get("event_name")):
        state["needs_clarification"] = True
        state["clarification_question"] = state.get("clarification_question") or "你想查看哪个事件？"

    if action == "resolve_event" and not arguments.get("event_name"):
        state["needs_clarification"] = True
        state["clarification_question"] = state.get("clarification_question") or "请告诉我需要查找的事件名称。"
    return state


def route_after_validate(state: DataQuestionState) -> str:
    return "clarify" if state.get("needs_clarification") else "execute_tool"
