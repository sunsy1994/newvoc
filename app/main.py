from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import TASKS_DIR
from app.routers.tasks import router as tasks_router
from app.services.task_store import TaskStore


def create_app(tasks_dir: Path | None = None) -> FastAPI:
    app = FastAPI(title="AutoVOC Task Workbench")
    app.state.task_store = TaskStore(tasks_dir or TASKS_DIR)
    app.include_router(tasks_router)
    return app


app = create_app()
