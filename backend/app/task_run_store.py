import json
from pathlib import Path

from .config import CALC_RUN_STORE_PATH
from .task_schemas import CalcTaskRun


def _read_raw() -> list[dict]:
    path = Path(CALC_RUN_STORE_PATH)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def list_task_runs() -> list[CalcTaskRun]:
    rows = _read_raw()
    runs = [CalcTaskRun.model_validate(item) for item in rows]
    return sorted(runs, key=lambda item: item.started_at, reverse=True)


def save_task_runs(runs: list[CalcTaskRun]) -> None:
    Path(CALC_RUN_STORE_PATH).write_text(
        json.dumps([item.model_dump(mode="json") for item in runs], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def upsert_task_run(run: CalcTaskRun) -> None:
    runs = {item.run_id: item for item in list_task_runs()}
    runs[run.run_id] = run
    save_task_runs(list(runs.values()))
