from typing import Any


def run_event_report_agent(*args: Any, **kwargs: Any) -> dict[str, Any]:
    from app.agents.report.graph import run_event_report_agent as runner

    return runner(*args, **kwargs)

__all__ = ["run_event_report_agent"]
