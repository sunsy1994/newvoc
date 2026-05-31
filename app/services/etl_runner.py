from __future__ import annotations

import importlib.util
import sys
import traceback
from pathlib import Path
from typing import Any

from app.config import DATABASE_URL, ETL_SCRIPT_PATH
from app.services.db_loader import load_etl_outputs
from app.services.task_store import TaskStore, utc_now_iso


class EtlRunner:
    def __init__(self, store: TaskStore, script_path: Path | None = None) -> None:
        self.store = store
        self.script_path = script_path or ETL_SCRIPT_PATH

    def run_task(self, batch_id: str) -> dict[str, Any]:
        self.store.update_task(
            batch_id,
            status="running",
            started_at=utc_now_iso(),
            finished_at=None,
            error_message=None,
        )
        try:
            run_etl = load_run_etl(self.script_path)
            summary = run_etl(
                input_dir=self.store.input_dir(batch_id),
                output_dir=self.store.output_dir(batch_id),
            )
            db_loaded = load_etl_outputs(
                output_dir=self.store.output_dir(batch_id),
                batch_id=batch_id,
                database_url=DATABASE_URL,
            )
        except Exception as exc:
            return self.store.update_task(
                batch_id,
                status="failed",
                finished_at=utc_now_iso(),
                error_message=f"{exc}\n{traceback.format_exc()}",
            )

        return self.store.update_task(
            batch_id,
            status="success",
            finished_at=utc_now_iso(),
            summary=summary,
            db_loaded=db_loaded,
            error_message=None,
        )


def load_run_etl(script_path: Path):
    module_name = f"event_voc_ods_etl_runtime_{script_path.stat().st_mtime_ns}"
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load ETL script: {script_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    if not hasattr(module, "run_etl"):
        raise RuntimeError(f"ETL script does not define run_etl: {script_path}")
    return module.run_etl
