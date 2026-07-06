from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

from app.agents.data_question import run_data_question_agent
from app.agents.qa import run_qa_agent


AgentCapability = Literal["data_question", "qa", "report", "insight"]
AgentRunner = Callable[..., dict[str, Any]]

AGENT_RUNNERS: dict[str, AgentRunner] = {
    "data_question": run_data_question_agent,
    "qa": run_qa_agent,
}


class AgentCapabilityUnavailableError(ValueError):
    pass


def dispatch_agent(
    capability: AgentCapability | str,
    message: str,
    *,
    event_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    runner = AGENT_RUNNERS.get(capability)
    if runner is None:
        raise AgentCapabilityUnavailableError(f"Agent 能力 {capability} 尚未接入。")
    return runner(message, event_id=event_id, history=history)
