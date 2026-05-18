from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class CalcTaskRun(BaseModel):
    run_id: str
    task_id: str
    status: Literal["queued", "running", "success", "failed"]
    trigger_type: Literal["manual", "batch", "schedule"]
    started_at: str
    finished_at: str | None = None
    duration_ms: int | None = None
    processed_rows: int = 0
    output_rows: int = 0
    error_message: str | None = None
    log_path: str | None = None


class CalcTask(BaseModel):
    task_id: str
    task_name: str
    task_group: str
    task_desc: str
    script_path: str
    entry_func: str
    input_tables: list[str]
    output_tables: list[str]
    run_mode: Literal["manual", "batch", "schedule"]
    is_enabled: bool
    status: Literal["idle", "running", "success", "failed"] = "idle"
    last_run_at: str | None = None
    latest_run: CalcTaskRun | None = None


class CalcTaskDetail(CalcTask):
    script_content: str
    recent_runs: list[CalcTaskRun]


class CalcGraphNode(BaseModel):
    id: str
    name: str
    group: Literal["source", "task", "output"]
    description: str
    status: Literal["idle", "running", "success", "failed"]


class CalcGraphEdge(BaseModel):
    source: str
    target: str


class CalcGraphResponse(BaseModel):
    nodes: list[CalcGraphNode]
    edges: list[CalcGraphEdge]


class CalcRunTriggerResponse(BaseModel):
    accepted: bool
    run_id: str
    message: str
