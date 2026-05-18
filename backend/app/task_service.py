import importlib
import time
import uuid
from datetime import datetime

from .config import CALC_LOG_DIR
from .database import engine
from .task_registry import get_calc_task, list_calc_tasks, read_script_content
from .task_run_store import list_task_runs, upsert_task_run
from .task_schemas import (
    CalcGraphEdge,
    CalcGraphNode,
    CalcGraphResponse,
    CalcRunTriggerResponse,
    CalcTask,
    CalcTaskDetail,
    CalcTaskRun,
)


class TaskExecutionError(Exception):
    pass


def _latest_runs() -> dict[str, CalcTaskRun]:
    mapping: dict[str, CalcTaskRun] = {}
    for run in list_task_runs():
        if run.task_id not in mapping:
            mapping[run.task_id] = run
    return mapping


def list_tasks_with_state() -> list[CalcTask]:
    latest = _latest_runs()
    tasks: list[CalcTask] = []
    for item in list_calc_tasks():
        run = latest.get(item["task_id"])
        status = "idle"
        last_run_at = None
        if run:
            status = "running" if run.status == "running" else "success" if run.status == "success" else "failed"
            last_run_at = run.finished_at or run.started_at
        tasks.append(
            CalcTask(
                task_id=item["task_id"],
                task_name=item["task_name"],
                task_group=item["task_group"],
                task_desc=item["task_desc"],
                script_path=item["script_path"],
                entry_func=item["entry_func"],
                input_tables=item["input_tables"],
                output_tables=item["output_tables"],
                run_mode=item["run_mode"],
                is_enabled=item["is_enabled"],
                status=status,
                last_run_at=last_run_at,
                latest_run=run,
            )
        )
    return tasks


def get_task_detail(task_id: str) -> CalcTaskDetail:
    task = get_calc_task(task_id)
    if not task:
        raise TaskExecutionError(f"Task not found: {task_id}")
    tasks = {item.task_id: item for item in list_tasks_with_state()}
    current = tasks[task_id]
    recent_runs = [item for item in list_task_runs() if item.task_id == task_id][:10]
    return CalcTaskDetail(
        **current.model_dump(),
        script_content=read_script_content(task),
        recent_runs=recent_runs,
    )


def build_graph() -> CalcGraphResponse:
    tasks = list_tasks_with_state()
    nodes: list[CalcGraphNode] = []
    edges: list[CalcGraphEdge] = []

    source_tables = {}
    output_tables = {}

    for task in tasks:
        task_node_id = f"task-{task.task_id}"
        nodes.append(
            CalcGraphNode(
                id=task_node_id,
                name=task.task_name,
                group="task",
                description=task.task_desc,
                status=task.status,
            )
        )

        for table in task.input_tables:
            node_id = f"src-{table}"
            if node_id not in source_tables:
                source_tables[node_id] = CalcGraphNode(
                    id=node_id,
                    name=table,
                    group="source",
                    description="输入表",
                    status="idle",
                )
            edges.append(CalcGraphEdge(source=node_id, target=task_node_id))

        for table in task.output_tables:
            node_id = f"out-{table}"
            if node_id not in output_tables:
                output_tables[node_id] = CalcGraphNode(
                    id=node_id,
                    name=table,
                    group="output",
                    description="输出表",
                    status=task.status,
                )
            edges.append(CalcGraphEdge(source=task_node_id, target=node_id))

    return CalcGraphResponse(
        nodes=[*source_tables.values(), *nodes, *output_tables.values()],
        edges=edges,
    )


def _write_log(task_id: str, content: str) -> str:
    path = CALC_LOG_DIR / f"{task_id}.log"
    path.write_text(content, encoding="utf-8")
    return str(path)


def _run_task_module(task: dict) -> dict:
    if engine is None:
        return {"processed_rows": 0, "output_rows": 0, "message": "DATABASE_URL not configured"}
    module = importlib.import_module(task["module_path"])
    entry = getattr(module, task["entry_func"])
    return entry(engine, {})


def run_task(task_id: str) -> CalcRunTriggerResponse:
    task = get_calc_task(task_id)
    if not task:
        raise TaskExecutionError(f"Task not found: {task_id}")

    run_id = f"run-{task_id}-{uuid.uuid4().hex[:8]}"
    started_at = datetime.now()
    run = CalcTaskRun(
        run_id=run_id,
        task_id=task_id,
        status="running",
        trigger_type="manual",
        started_at=started_at.strftime("%Y-%m-%d %H:%M:%S"),
    )
    upsert_task_run(run)

    try:
        begin = time.perf_counter()
        result = _run_task_module(task)
        duration_ms = int((time.perf_counter() - begin) * 1000)
        finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_path = _write_log(task_id, f"[{finished_at}] success\n{result}\n")
        upsert_task_run(
            CalcTaskRun(
                run_id=run_id,
                task_id=task_id,
                status="success",
                trigger_type="manual",
                started_at=run.started_at,
                finished_at=finished_at,
                duration_ms=duration_ms,
                processed_rows=int(result.get("processed_rows", 0)),
                output_rows=int(result.get("output_rows", 0)),
                log_path=log_path,
            )
        )
        return CalcRunTriggerResponse(
            accepted=True,
            run_id=run_id,
            message=result.get("message", f"{task_id} executed"),
        )
    except Exception as exc:
        finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_path = _write_log(task_id, f"[{finished_at}] failed\n{exc}\n")
        upsert_task_run(
            CalcTaskRun(
                run_id=run_id,
                task_id=task_id,
                status="failed",
                trigger_type="manual",
                started_at=run.started_at,
                finished_at=finished_at,
                duration_ms=None,
                processed_rows=0,
                output_rows=0,
                error_message=str(exc),
                log_path=log_path,
            )
        )
        raise TaskExecutionError(str(exc)) from exc
