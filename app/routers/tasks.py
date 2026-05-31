from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.config import TEMPLATE_DIR
from app.services.etl_runner import EtlRunner
from app.services.task_store import TaskStore


ALLOWED_TABLES = {
    "ods_event_upload",
    "ods_content_upload",
    "ods_comment_upload",
    "dwd_event",
    "dwd_content",
    "dwd_author",
    "dwd_comment",
    "rel_event_content",
    "rel_author_content",
    "ads_event_overview",
    "ads_event_trend_daily",
    "ads_event_content_rank",
    "ads_event_location_distribution",
    "rejected_content",
    "rejected_comment",
}

ALLOWED_TEMPLATES = {
    "event_upload_template.csv",
    "event_upload_template.xlsx",
    "content_upload_template.csv",
    "content_upload_template.xlsx",
    "comment_upload_template.csv",
    "comment_upload_template.xlsx",
}


router = APIRouter()


def get_store(request: Request) -> TaskStore:
    return request.app.state.task_store


def save_upload(upload_file: UploadFile, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as output:
        shutil.copyfileobj(upload_file.file, output)


@router.get("/api/tasks")
def list_tasks(request: Request) -> list[dict]:
    return get_store(request).list_tasks()


@router.post("/api/tasks/upload")
def upload_task(
    request: Request,
    event_file: Annotated[UploadFile, File()],
    content_file: Annotated[UploadFile, File()],
    comment_file: Annotated[UploadFile, File()],
) -> dict:
    store = get_store(request)
    task = store.create_task(
        input_files={
            "event_upload": event_file.filename or "event_upload.xlsx",
            "content_upload": content_file.filename or "content_upload.xlsx",
            "comment_upload": comment_file.filename or "comment_upload.xlsx",
        }
    )
    input_dir = store.input_dir(task["batch_id"])
    save_upload(event_file, input_dir / "event_upload.xlsx")
    save_upload(content_file, input_dir / "content_upload.xlsx")
    save_upload(comment_file, input_dir / "comment_upload.xlsx")
    return task


@router.post("/api/tasks/{batch_id}/run")
def run_task(request: Request, batch_id: str) -> dict:
    try:
        return EtlRunner(get_store(request)).run_task(batch_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/api/tasks/{batch_id}")
def get_task(request: Request, batch_id: str) -> dict:
    try:
        return get_store(request).get_task(batch_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/api/tasks/{batch_id}/tables")
def list_task_tables(request: Request, batch_id: str) -> dict:
    store = get_store(request)
    output_dir = store.output_dir(batch_id)
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Task output not found")
    tables = sorted(path.stem for path in output_dir.glob("*.csv") if path.stem in ALLOWED_TABLES)
    return {"batch_id": batch_id, "tables": tables}


@router.get("/api/tasks/{batch_id}/tables/{table_name}")
def preview_task_table(request: Request, batch_id: str, table_name: str, limit: int = 50, offset: int = 0) -> dict:
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail="Table not found")
    table_path = get_store(request).output_dir(batch_id) / f"{table_name}.csv"
    if not table_path.exists():
        raise HTTPException(status_code=404, detail="Table not found")
    dataframe = pd.read_csv(table_path, encoding="utf-8-sig")
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    page = dataframe.iloc[offset : offset + limit].fillna("")
    return {
        "batch_id": batch_id,
        "table": table_name,
        "total": int(len(dataframe)),
        "columns": dataframe.columns.tolist(),
        "rows": page.to_dict(orient="records"),
    }


@router.get("/api/templates/{template_name}")
def download_template(template_name: str) -> FileResponse:
    if template_name not in ALLOWED_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    return FileResponse(template_path, filename=template_name)
