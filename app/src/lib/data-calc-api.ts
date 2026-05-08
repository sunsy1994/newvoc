import { calcGraph, calcTaskDetails, calcTasks, calcRuns } from '@/components/data-access/data/dataCalcMock';
import type { CalcGraphResponse, CalcTask, CalcTaskDetail, CalcTaskRun } from '@/types/dataCalc';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

function apiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

async function safeJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function normalizeRun(run: any): CalcTaskRun {
  return {
    runId: run.runId ?? run.run_id,
    taskId: run.taskId ?? run.task_id,
    status: run.status,
    triggerType: run.triggerType ?? run.trigger_type,
    startedAt: run.startedAt ?? run.started_at,
    finishedAt: run.finishedAt ?? run.finished_at,
    durationMs: run.durationMs ?? run.duration_ms,
    processedRows: run.processedRows ?? run.processed_rows ?? 0,
    outputRows: run.outputRows ?? run.output_rows ?? 0,
    errorMessage: run.errorMessage ?? run.error_message,
    logPath: run.logPath ?? run.log_path,
  };
}

function normalizeTask(task: any): CalcTask {
  return {
    taskId: task.taskId ?? task.task_id,
    taskName: task.taskName ?? task.task_name,
    taskGroup: task.taskGroup ?? task.task_group,
    taskDesc: task.taskDesc ?? task.task_desc,
    scriptPath: task.scriptPath ?? task.script_path,
    entryFunc: task.entryFunc ?? task.entry_func,
    inputTables: task.inputTables ?? task.input_tables ?? [],
    outputTables: task.outputTables ?? task.output_tables ?? [],
    runMode: task.runMode ?? task.run_mode,
    isEnabled: task.isEnabled ?? task.is_enabled,
    status: task.status,
    lastRunAt: task.lastRunAt ?? task.last_run_at,
    latestRun: task.latestRun || task.latest_run ? normalizeRun(task.latestRun ?? task.latest_run) : undefined,
  };
}

function normalizeTaskDetail(task: any): CalcTaskDetail {
  return {
    ...normalizeTask(task),
    scriptContent: task.scriptContent ?? task.script_content,
    recentRuns: (task.recentRuns ?? task.recent_runs ?? []).map(normalizeRun),
  };
}

export async function getCalcGraph(): Promise<CalcGraphResponse> {
  try {
    return await safeJson<CalcGraphResponse>(apiUrl('/api/data-calc/graph'));
  } catch {
    return calcGraph;
  }
}

export async function getCalcTasks(): Promise<CalcTask[]> {
  try {
    const payload = await safeJson<any[]>(apiUrl('/api/data-calc/tasks'));
    return payload.map(normalizeTask);
  } catch {
    return calcTasks;
  }
}

export async function getCalcTaskDetail(taskId: string): Promise<CalcTaskDetail> {
  try {
    const payload = await safeJson<any>(apiUrl(`/api/data-calc/tasks/${taskId}`));
    return normalizeTaskDetail(payload);
  } catch {
    return calcTaskDetails[taskId] ?? {
      ...calcTasks[0],
      scriptContent: '# task not found',
      recentRuns: calcRuns.filter((item) => item.taskId === taskId),
    };
  }
}

export async function runCalcTask(taskId: string): Promise<{ accepted: boolean; runId: string; message: string }> {
  try {
    return await safeJson(apiUrl(`/api/data-calc/tasks/${taskId}/run`), {
      method: 'POST',
    });
  } catch {
    return {
      accepted: true,
      runId: `mock-run-${taskId}-${Date.now()}`,
      message: `已触发 ${taskId}，当前为前端 mock 执行。`,
    };
  }
}
