from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")


class TaskStore:
    def __init__(self, tasks_dir: Path) -> None:
        self.tasks_dir = Path(tasks_dir)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)

    def create_task(self, input_files: dict[str, str]) -> dict[str, Any]:
        batch_id = f"batch_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:8]}"
        now = utc_now_iso()
        task = {
            "batch_id": batch_id,
            "status": "uploaded",
            "created_at": now,
            "updated_at": now,
            "started_at": None,
            "finished_at": None,
            "input_files": input_files,
            "summary": {},
            "error_message": None,
        }
        task_dir = self.task_dir(batch_id)
        (task_dir / "input").mkdir(parents=True, exist_ok=True)
        (task_dir / "output").mkdir(parents=True, exist_ok=True)
        self._write_task(task)
        return task

    def get_task(self, batch_id: str) -> dict[str, Any]:
        task_path = self.task_dir(batch_id) / "task.json"
        if not task_path.exists():
            raise KeyError(f"Task not found: {batch_id}")
        return json.loads(task_path.read_text(encoding="utf-8"))

    def update_task(self, batch_id: str, **changes: Any) -> dict[str, Any]:
        task = self.get_task(batch_id)
        task.update(changes)
        task["updated_at"] = utc_now_iso()
        self._write_task(task)
        return task

    def list_tasks(self) -> list[dict[str, Any]]:
        tasks = []
        for task_path in self.tasks_dir.glob("batch_*/task.json"):
            tasks.append(json.loads(task_path.read_text(encoding="utf-8")))
        return sorted(tasks, key=lambda task: task["created_at"], reverse=True)

    def task_dir(self, batch_id: str) -> Path:
        return self.tasks_dir / batch_id

    def input_dir(self, batch_id: str) -> Path:
        return self.task_dir(batch_id) / "input"

    def output_dir(self, batch_id: str) -> Path:
        return self.task_dir(batch_id) / "output"

    def _write_task(self, task: dict[str, Any]) -> None:
        task_dir = self.task_dir(task["batch_id"])
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "task.json").write_text(
            json.dumps(task, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
