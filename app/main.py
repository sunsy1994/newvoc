from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import ETL_SCRIPT_PATH, SCRIPT_BACKUP_DIR, TASKS_DIR
from app.routers.tasks import router as tasks_router
from app.services.agent_error_log import AgentErrorLog
from app.services.script_manager import ScriptManager
from app.services.task_store import TaskStore


def create_app(
    tasks_dir: Path | None = None,
    script_path: Path | None = None,
    script_backup_dir: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="AutoVOC Task Workbench")
    resolved_tasks_dir = tasks_dir or TASKS_DIR
    app.state.task_store = TaskStore(resolved_tasks_dir)
    app.state.script_manager = ScriptManager(script_path or ETL_SCRIPT_PATH, script_backup_dir or SCRIPT_BACKUP_DIR)
    app.state.agent_error_log = AgentErrorLog(resolved_tasks_dir.parent / "agent_error_questions.jsonl")
    app.include_router(tasks_router)
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    return app


app = create_app()
