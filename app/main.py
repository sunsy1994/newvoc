from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import TASKS_DIR
from app.routers.tasks import router as tasks_router
from app.services.task_store import TaskStore


def create_app(tasks_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="AutoVOC Task Workbench")
    app.state.task_store = TaskStore(tasks_dir or TASKS_DIR)
    app.include_router(tasks_router)
    static_dir = Path(__file__).resolve().parent / "static"
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/", include_in_schema=False)
    def home() -> FileResponse:
        return FileResponse(static_dir / "index.html")

    return app


app = create_app()
