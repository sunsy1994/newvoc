import json
from datetime import datetime
from pathlib import Path

from .config import JOB_STORE_PATH
from .schemas import ImportJobRecord


def _read_raw() -> list[dict]:
    path = Path(JOB_STORE_PATH)
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def list_jobs() -> list[ImportJobRecord]:
    rows = _read_raw()
    jobs = [ImportJobRecord.model_validate(item) for item in rows]
    return sorted(jobs, key=lambda item: item.created_at, reverse=True)


def save_jobs(jobs: list[ImportJobRecord]) -> None:
    payload = [item.model_dump(mode="json") for item in jobs]
    Path(JOB_STORE_PATH).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def upsert_job(job: ImportJobRecord) -> None:
    jobs = list_jobs()
    mapping = {item.job_id: item for item in jobs}
    mapping[job.job_id] = job
    save_jobs(list(mapping.values()))


def update_job(job_id: str, **updates) -> ImportJobRecord:
    jobs = {item.job_id: item for item in list_jobs()}
    current = jobs[job_id]
    data = current.model_dump()
    data.update(updates)
    data["updated_at"] = datetime.now()
    updated = ImportJobRecord.model_validate(data)
    jobs[job_id] = updated
    save_jobs(list(jobs.values()))
    return updated
