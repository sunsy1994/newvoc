from __future__ import annotations

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


def test_dispatcher_registers_report_agent() -> None:
    from app.agents.core import dispatcher
    from app.agents.report import run_event_report_agent

    assert dispatcher.AGENT_RUNNERS["report"] is run_event_report_agent


def test_dispatcher_registers_explicit_competitor_report_agent() -> None:
    from app.agents.competitor_report import run_competitor_report_agent
    from app.agents.core import dispatcher

    assert dispatcher.AGENT_RUNNERS["competitor_report"] is run_competitor_report_agent


def test_dispatcher_does_not_forward_event_id_to_competitor_report(monkeypatch) -> None:
    from app.agents.core import dispatcher

    captured = {}

    def fake_run(message: str, history: list[dict] | None = None) -> dict:
        captured.update(message=message, history=history)
        return {"status": "generated", "answer": "已生成竞品动态报告。"}

    monkeypatch.setitem(dispatcher.AGENT_RUNNERS, "competitor_report", fake_run)
    history = [{"role": "user", "content": "查看竞品动态"}]

    result = dispatcher.dispatch_agent(
        "competitor_report",
        "生成比亚迪最近两周竞品动态报告",
        event_id="event_must_not_leak",
        history=history,
    )

    assert result["status"] == "generated"
    assert captured == {
        "message": "生成比亚迪最近两周竞品动态报告",
        "history": history,
    }


def test_dispatcher_registers_qa_agent() -> None:
    from app.agents.core import dispatcher
    from app.agents.qa import run_qa_agent

    assert dispatcher.AGENT_RUNNERS["qa"] is run_qa_agent


def test_dispatcher_registers_insight_agent() -> None:
    from app.agents.core import dispatcher
    from app.agents.insight import run_insight_agent

    assert dispatcher.AGENT_RUNNERS["insight"] is run_insight_agent


def test_unified_agent_api_returns_qa_scope_metadata(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    captured = {}

    def fake_dispatch(capability: str, message: str, **kwargs) -> dict:
        captured.update(capability=capability, message=message, **kwargs)
        return {
            "status": "answered",
            "answer": "传播峰值集中在首日。",
            "suggested_questions": [],
            "requires_clarification": False,
            "event_name": "IDT6上市",
            "time_scope": {"label": "2026-05-17 至 2026-05-20（事件完整周期）"},
            "data_scope": "市场看板结构化数据",
            "react_rounds": 2,
        }

    monkeypatch.setattr("app.routers.tasks.dispatch_agent", fake_dispatch)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))
    response = client.post(
        "/api/agents/run",
        json={"capability": "qa", "message": "这个事件为什么爆发？", "event_id": "event_001", "history": []},
    )

    assert response.status_code == 200
    assert response.json()["event_name"] == "IDT6上市"
    assert response.json()["react_rounds"] == 2
    assert captured["capability"] == "qa"


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


def test_unified_agent_api_dispatches_insight_with_conversation_context(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    captured = {}

    def fake_dispatch(capability: str, message: str, **kwargs) -> dict:
        captured.update(capability=capability, message=message, **kwargs)
        return {
            "status": "insufficient_data",
            "answer": "暂无此类数据推演。",
            "suggested_questions": [],
            "requires_clarification": False,
            "insight_result": {"reaction_cards": [], "similar_events": [], "limitations": []},
            "react_rounds": 1,
        }

    monkeypatch.setattr("app.routers.tasks.dispatch_agent", fake_dispatch)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))
    history = [{"role": "user", "content": "我准备做一次配置调整"}]
    response = client.post(
        "/api/agents/run",
        json={"capability": "insight", "message": "取消座椅通风后用户会怎么说？", "event_id": None, "history": history},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "insufficient_data"
    assert captured == {
        "capability": "insight",
        "message": "取消座椅通风后用户会怎么说？",
        "event_id": None,
        "history": history,
    }


def test_unified_qa_api_logs_unexpected_errors_and_returns_fallback(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    def fake_dispatch(capability: str, message: str, **kwargs) -> dict:
        raise RuntimeError("missing kol profile matrix")

    monkeypatch.setattr("app.routers.tasks.dispatch_agent", fake_dispatch)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.post(
        "/api/agents/run",
        json={"capability": "qa", "message": "这些KOL的粉丝画像与IDT6的目标用户重合度如何？", "history": []},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "answered"
    assert "当前没有数据支撑" in payload["answer"]
    assert payload["requires_clarification"] is False

    log_response = client.get("/api/system/agent-error-questions")

    assert log_response.status_code == 200
    records = log_response.json()["records"]
    assert records[0]["question"] == "这些KOL的粉丝画像与IDT6的目标用户重合度如何？"
    assert records[0]["capability"] == "qa"
    assert records[0]["error_reason"] == "missing kol profile matrix"


def test_unified_qa_api_logs_data_errors_and_returns_fallback(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    def fake_dispatch(capability: str, message: str, **kwargs) -> dict:
        raise ValueError("no evidence rows for requested question")

    monkeypatch.setattr("app.routers.tasks.dispatch_agent", fake_dispatch)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.post(
        "/api/agents/run",
        json={"capability": "qa", "message": "idt6上市外观的惊喜点说了什么", "history": []},
    )

    assert response.status_code == 200
    assert "当前没有数据支撑" in response.json()["answer"]

    records = client.get("/api/system/agent-error-questions").json()["records"]
    assert records[0]["question"] == "idt6上市外观的惊喜点说了什么"
    assert records[0]["error_reason"] == "no evidence rows for requested question"


def test_unified_qa_api_logs_insufficient_evidence_answers(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    def fake_dispatch(capability: str, message: str, **kwargs) -> dict:
        return {
            "status": "answered",
            "answer": "根据本次IDT6上市事件的数据，我们无法直接获取KOL的详细粉丝画像。",
            "suggested_questions": [],
            "requires_clarification": False,
        }

    monkeypatch.setattr("app.routers.tasks.dispatch_agent", fake_dispatch)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.post(
        "/api/agents/run",
        json={"capability": "qa", "message": "这些KOL的粉丝画像与IDT6的目标用户重合度如何？", "history": []},
    )

    assert response.status_code == 200
    assert "无法直接获取KOL的详细粉丝画像" in response.json()["answer"]

    records = client.get("/api/system/agent-error-questions").json()["records"]
    assert records[0]["question"] == "这些KOL的粉丝画像与IDT6的目标用户重合度如何？"
    assert records[0]["error_reason"] == "insufficient data support"
