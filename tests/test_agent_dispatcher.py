from __future__ import annotations

import pytest


def test_dispatcher_routes_data_question_with_context(monkeypatch) -> None:
    from app.agents.core import dispatcher

    captured = {}

    def fake_run(message: str, event_id: str | None = None, history: list[dict] | None = None) -> dict:
        captured.update(message=message, event_id=event_id, history=history)
        return {"status": "answered", "answer": "近30天有2个事件。"}

    monkeypatch.setitem(dispatcher.AGENT_RUNNERS, "data_question", fake_run)
    history = [{"role": "user", "content": "看看近期情况"}]

    result = dispatcher.dispatch_agent(
        "data_question",
        "近期有哪些事件？",
        event_id="event_001",
        history=history,
    )

    assert result == {"status": "answered", "answer": "近30天有2个事件。"}
    assert captured == {
        "message": "近期有哪些事件？",
        "event_id": "event_001",
        "history": history,
    }


@pytest.mark.parametrize("capability", ["qa", "report", "insight"])
def test_dispatcher_rejects_known_but_unavailable_capability(capability: str) -> None:
    from app.agents.core.dispatcher import AgentCapabilityUnavailableError, dispatch_agent

    with pytest.raises(AgentCapabilityUnavailableError, match="尚未接入"):
        dispatch_agent(capability, "测试问题")


def test_unified_agent_api_dispatches_selected_capability(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    captured = {}

    def fake_dispatch(capability: str, message: str, **kwargs) -> dict:
        captured.update(capability=capability, message=message, **kwargs)
        return {
            "status": "answered",
            "answer": "近30天有2个重点事件。",
            "suggested_questions": [],
            "requires_clarification": False,
        }

    monkeypatch.setattr("app.routers.tasks.dispatch_agent", fake_dispatch)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))
    history = [{"role": "user", "content": "看看近期情况"}]

    response = client.post(
        "/api/agents/run",
        json={
            "capability": "data_question",
            "message": "近期有哪些事件？",
            "event_id": "event_001",
            "history": history,
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "近30天有2个重点事件。"
    assert captured == {
        "capability": "data_question",
        "message": "近期有哪些事件？",
        "event_id": "event_001",
        "history": history,
    }


def test_unified_agent_api_reports_unavailable_capability(tmp_path) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))
    response = client.post(
        "/api/agents/run",
        json={"capability": "insight", "message": "分析这个事件"},
    )

    assert response.status_code == 501
    assert "尚未接入" in response.json()["detail"]
