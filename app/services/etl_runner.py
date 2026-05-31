from __future__ import annotations

import traceback
from typing import Any

from etl.event_voc_ods_etl import run_etl

from app.services.task_store import TaskStore, utc_now_iso


class EtlRunner:
    def __init__(self, store: TaskStore) -> None:
        self.store = store

    def run_task(self, batch_id: str) -> dict[str, Any]:
        self.store.update_task(
            batch_id,
            status="running",
            started_at=utc_now_iso(),
            finished_at=None,
            error_message=None,
        )
        try:
            summary = run_etl(
                input_dir=self.store.input_dir(batch_id),
                output_dir=self.store.output_dir(batch_id),
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
            error_message=None,
        )
