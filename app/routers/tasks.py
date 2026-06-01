from __future__ import annotations

import shutil
from pathlib import Path
from typing import Annotated

import psycopg
import pandas as pd
from pydantic import BaseModel
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse

from app.config import TEMPLATE_DIR
from app.services.asset_library import list_assets
from app.services.etl_flow import build_flow_nodes
from app.services.etl_runner import EtlRunner
from app.services.script_manager import ScriptManager
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


class ScriptSaveRequest(BaseModel):
    content: str


class ScriptTestRunRequest(BaseModel):
    batch_id: str


def get_store(request: Request) -> TaskStore:
    return request.app.state.task_store


def get_script_manager(request: Request) -> ScriptManager:
    return request.app.state.script_manager


def upload_suffix(upload_file: UploadFile) -> str:
    suffix = Path(upload_file.filename or "").suffix.lower()
    return suffix if suffix in {".xlsx", ".csv"} else ".xlsx"


def save_upload(upload_file: UploadFile, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as output:
        shutil.copyfileobj(upload_file.file, output)


@router.get("/api/tasks")
def list_tasks(request: Request) -> list[dict]:
    return get_store(request).list_tasks()


@router.get("/api/assets/{asset_key}")
def get_assets(asset_key: str, q: str | None = None, limit: int = 50, offset: int = 0) -> dict:
    try:
        return list_assets(asset_key, q=q, limit=limit, offset=offset)
    except KeyError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/etl/flow")
def get_etl_flow(request: Request, batch_id: str | None = None) -> dict:
    summary = None
    if batch_id:
        try:
            summary = get_store(request).get_task(batch_id).get("summary", {})
        except KeyError:
            raise HTTPException(status_code=404, detail="Task not found")
    return {"nodes": build_flow_nodes(summary)}


@router.get("/api/etl/script")
def get_etl_script(request: Request) -> dict:
    return get_script_manager(request).read_script()


@router.put("/api/etl/script")
def save_etl_script(request: Request, payload: ScriptSaveRequest) -> dict:
    return get_script_manager(request).save_script(payload.content)


@router.post("/api/etl/script/test-run")
def test_run_etl_script(request: Request, payload: ScriptTestRunRequest) -> dict:
    try:
        get_store(request).get_task(payload.batch_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
    return EtlRunner(get_store(request), get_script_manager(request).script_path).run_task(payload.batch_id)


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
    save_upload(event_file, input_dir / f"event_upload{upload_suffix(event_file)}")
    save_upload(content_file, input_dir / f"content_upload{upload_suffix(content_file)}")
    save_upload(comment_file, input_dir / f"comment_upload{upload_suffix(comment_file)}")
    return task


@router.post("/api/tasks/{batch_id}/run")
def run_task(request: Request, batch_id: str) -> dict:
    try:
        return EtlRunner(get_store(request), get_script_manager(request).script_path).run_task(batch_id)
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
