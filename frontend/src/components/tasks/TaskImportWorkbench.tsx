"use client";

import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  CheckCircle2,
  Database,
  Download,
  FileSpreadsheet,
  Loader2,
  Play,
  RefreshCw,
  UploadCloud,
  XCircle,
} from "lucide-react";

import { DataPagination } from "@/components/shared/DataPagination";
import { apiBaseUrl } from "@/config/navigation";
import type { ImportTask, TaskTablePayload, TaskTablesPayload } from "@/types/tasks";

const defaultPageSize = 10;

type LoadState = "idle" | "loading" | "error";

const summaryLabels: Array<[string, string]> = [
  ["ods_event_upload", "事件ODS"],
  ["ods_content_upload", "内容ODS"],
  ["ods_comment_upload", "评论ODS"],
  ["dwd_content", "标准内容"],
  ["dwd_comment", "标准评论"],
  ["rejected_comment", "拒绝评论"],
];

function buildApiUrl(endpoint: string, params?: URLSearchParams) {
  const query = params?.toString();
  return `${apiBaseUrl}${endpoint}${query ? `?${query}` : ""}`;
}

function statusLabel(status: string) {
  return { uploaded: "待执行", running: "运行中", success: "成功", failed: "失败" }[status] ?? status;
}

function statusClass(status: string) {
  if (status === "success") return "bg-[#eafafa] text-[#0f9695]";
  if (status === "failed") return "bg-[#fff0f0] text-[#d94a4a]";
  if (status === "running") return "bg-[#eef6ff] text-[#4896FE]";
  return "bg-[#f0efff] text-[#5347CE]";
}

function formatCellValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "boolean") return value ? "是" : "否";
  if (typeof value === "number") return value.toLocaleString("zh-CN");
  if (typeof value === "string") {
    if (/^\d{4}-\d{2}-\d{2}T/.test(value)) return value.replace("T", " ").slice(0, 19);
    return value;
  }
  return JSON.stringify(value);
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <p className="text-xs text-[#8b92a1]">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">{value}</p>
    </div>
  );
}

function FileInput({ label, name }: { label: string; name: string }) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold text-[#596070]">{label}</span>
      <input
        name={name}
        type="file"
        accept=".xlsx,.csv"
        required
        className="h-10 w-full rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 py-2 text-sm text-[#596070] file:mr-3 file:rounded-md file:border-0 file:bg-white file:px-2 file:py-1 file:text-xs file:font-medium file:text-[#5347CE]"
      />
    </label>
  );
}

export function TaskImportWorkbench() {
  const [tasks, setTasks] = useState<ImportTask[]>([]);
  const [selectedBatchId, setSelectedBatchId] = useState<string | null>(null);
  const [selectedTask, setSelectedTask] = useState<ImportTask | null>(null);
  const [tables, setTables] = useState<string[]>([]);
  const [selectedTable, setSelectedTable] = useState("");
  const [tablePayload, setTablePayload] = useState<TaskTablePayload | null>(null);
  const [taskLoadState, setTaskLoadState] = useState<LoadState>("idle");
  const [tableLoadState, setTableLoadState] = useState<LoadState>("idle");
  const [uploadMessage, setUploadMessage] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [pageSize, setPageSize] = useState(defaultPageSize);
  const uploadFormRef = useRef<HTMLFormElement | null>(null);

  const tableTotal = tablePayload?.total ?? 0;
  const tableRows = tablePayload?.rows ?? [];
  const tableColumns = tablePayload?.columns ?? [];

  const tableParams = useMemo(() => {
    return new URLSearchParams({ limit: String(pageSize), offset: String(offset) });
  }, [offset, pageSize]);

  const loadTasks = useCallback(async () => {
    setTaskLoadState("loading");
    try {
      const response = await fetch(buildApiUrl("/tasks"), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const nextTasks = (await response.json()) as ImportTask[];
      setTasks(nextTasks);
      setTaskLoadState("idle");
      if (!selectedBatchId && nextTasks.length > 0) setSelectedBatchId(nextTasks[0].batch_id);
    } catch {
      setTaskLoadState("error");
    }
  }, [selectedBatchId]);

  const loadSelectedTask = useCallback(async () => {
    if (!selectedBatchId) {
      setSelectedTask(null);
      setTables([]);
      setSelectedTable("");
      setTablePayload(null);
      return;
    }
    try {
      const response = await fetch(buildApiUrl(`/tasks/${selectedBatchId}`), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setSelectedTask((await response.json()) as ImportTask);
    } catch {
      setSelectedTask(null);
    }
  }, [selectedBatchId]);

  const loadTables = useCallback(async () => {
    if (!selectedBatchId) return;
    try {
      const response = await fetch(buildApiUrl(`/tasks/${selectedBatchId}/tables`), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = (await response.json()) as TaskTablesPayload;
      setTables(payload.tables ?? []);
      setSelectedTable((current) => (current && payload.tables.includes(current) ? current : payload.tables[0] ?? ""));
      setOffset(0);
    } catch {
      setTables([]);
      setSelectedTable("");
      setTablePayload(null);
    }
  }, [selectedBatchId]);

  const loadTable = useCallback(async () => {
    if (!selectedBatchId || !selectedTable) {
      setTablePayload(null);
      return;
    }
    setTableLoadState("loading");
    try {
      const response = await fetch(buildApiUrl(`/tasks/${selectedBatchId}/tables/${selectedTable}`, tableParams), {
        cache: "no-store",
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setTablePayload((await response.json()) as TaskTablePayload);
      setTableLoadState("idle");
    } catch {
      setTablePayload(null);
      setTableLoadState("error");
    }
  }, [selectedBatchId, selectedTable, tableParams]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  useEffect(() => {
    loadSelectedTask();
    loadTables();
  }, [loadSelectedTask, loadTables]);

  useEffect(() => {
    loadTable();
  }, [loadTable]);

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setUploadMessage("正在上传...");
    const formData = new FormData(event.currentTarget);
    try {
      const response = await fetch(buildApiUrl("/tasks/upload"), { method: "POST", body: formData });
      const task = (await response.json()) as ImportTask;
      if (!response.ok) throw new Error(String((task as Record<string, unknown>).detail ?? "上传失败"));
      setUploadMessage(`已创建批次：${task.batch_id}`);
      uploadFormRef.current?.reset();
      setSelectedBatchId(task.batch_id);
      await loadTasks();
    } catch (error) {
      setUploadMessage(error instanceof Error ? error.message : "上传失败");
    }
  }

  async function runSelectedTask() {
    if (!selectedBatchId) return;
    setSelectedTask((task) => (task ? { ...task, status: "running" } : task));
    const response = await fetch(buildApiUrl(`/tasks/${selectedBatchId}/run`), { method: "POST" });
    if (response.ok) {
      setSelectedTask((await response.json()) as ImportTask);
      await Promise.all([loadTasks(), loadTables()]);
    }
  }

  function selectTask(batchId: string) {
    setSelectedBatchId(batchId);
    setSelectedTable("");
    setTablePayload(null);
    setOffset(0);
  }

  const exportTableUrl =
    selectedBatchId && selectedTable ? buildApiUrl(`/tasks/${selectedBatchId}/tables/${selectedTable}/export`) : "#";

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">Task Management</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">导入任务</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <a className="h-9 rounded-lg border border-[#e8ecf3] bg-white px-3 py-2 text-xs font-medium text-[#596070]" href={buildApiUrl("/templates/event_upload_template.xlsx")}>
            事件模板
          </a>
          <a className="h-9 rounded-lg border border-[#e8ecf3] bg-white px-3 py-2 text-xs font-medium text-[#596070]" href={buildApiUrl("/templates/content_upload_template.xlsx")}>
            内容模板
          </a>
          <a className="h-9 rounded-lg border border-[#e8ecf3] bg-white px-3 py-2 text-xs font-medium text-[#596070]" href={buildApiUrl("/templates/comment_upload_template.xlsx")}>
            评论模板
          </a>
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <div className="mb-4 flex items-start gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#f0efff] text-[#5347CE]">
              <UploadCloud className="h-4 w-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold text-[#151720]">上传原始数据</h2>
              <p className="mt-1 text-xs leading-5 text-[#8b92a1]">事件、内容、评论三张 ODS 文件需同时上传。</p>
            </div>
          </div>
          <form ref={uploadFormRef} className="space-y-3" onSubmit={handleUpload}>
            <FileInput label="事件表" name="event_file" />
            <FileInput label="内容表" name="content_file" />
            <FileInput label="评论表" name="comment_file" />
            <button className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#5347CE] px-4 text-sm font-semibold text-white shadow-[0_12px_22px_rgba(83,71,206,0.22)]">
              <UploadCloud className="h-4 w-4" />
              创建导入批次
            </button>
          </form>
          {uploadMessage ? <p className="mt-3 rounded-xl border border-[#e8ecf3] bg-[#f7f9fc] px-3 py-2 text-xs text-[#596070]">{uploadMessage}</p> : null}
        </section>

        <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <div className="mb-4 flex items-center justify-between gap-3">
            <div>
              <h2 className="text-sm font-semibold text-[#151720]">ETL 作业情况</h2>
              <p className="mt-1 text-xs text-[#8b92a1]">{taskLoadState === "error" ? "任务加载失败" : `共 ${tasks.length} 个批次`}</p>
            </div>
            <button
              type="button"
              onClick={() => loadTasks()}
              className="inline-flex h-9 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-3 text-xs font-medium text-[#596070]"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              刷新
            </button>
          </div>
          <div className="max-h-80 space-y-2 overflow-y-auto pr-1">
            {tasks.length === 0 ? <p className="rounded-xl bg-[#f7f9fc] p-4 text-sm text-[#8b92a1]">还没有导入批次。</p> : null}
            {tasks.map((task) => (
              <button
                key={task.batch_id}
                type="button"
                onClick={() => selectTask(task.batch_id)}
                className={`w-full rounded-xl border p-3 text-left transition ${
                  task.batch_id === selectedBatchId ? "border-[#5347CE] bg-[#f7f6ff]" : "border-[#e8ecf3] bg-white hover:bg-[#f7f9fc]"
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <strong className="text-xs font-semibold text-[#151720]">{task.batch_id}</strong>
                  <span className={`rounded-lg px-2 py-1 text-[11px] font-semibold ${statusClass(task.status)}`}>{statusLabel(task.status)}</span>
                </div>
                <p className="mt-1 text-xs text-[#8b92a1]">{formatCellValue(task.created_at)}</p>
              </button>
            ))}
          </div>
        </section>
      </section>

      <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-[#151720]">作业结果</h2>
            <p className="mt-1 text-xs text-[#8b92a1]">{selectedTask ? `${selectedTask.batch_id} / ${statusLabel(selectedTask.status)}` : "请选择一个批次"}</p>
          </div>
          <button
            type="button"
            disabled={!selectedBatchId || selectedTask?.status === "running"}
            onClick={runSelectedTask}
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#151720] px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            {selectedTask?.status === "running" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            运行 ETL
          </button>
        </div>

        <section className="mb-4 grid gap-3 md:grid-cols-3 lg:grid-cols-6">
          {summaryLabels.map(([key, label]) => (
            <Metric key={key} label={label} value={String(selectedTask?.summary?.[key] ?? "-")} />
          ))}
        </section>

        {selectedTask?.error_message ? (
          <pre className="mb-4 max-h-52 overflow-auto rounded-xl border border-[#ffd7d7] bg-[#fff7f7] p-4 text-xs text-[#b33a3a]">{selectedTask.error_message}</pre>
        ) : null}

        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap items-center gap-2">
            <select
              value={selectedTable}
              onChange={(event) => {
                setOffset(0);
                setSelectedTable(event.target.value);
              }}
              className="h-10 min-w-64 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-sm text-[#596070] outline-none focus:border-[#5347CE]"
            >
              <option value="">选择输出表</option>
              {tables.map((table) => (
                <option key={table} value={table}>
                  {table}
                </option>
              ))}
            </select>
            <span className="text-xs text-[#8b92a1]">{tablePayload ? `${tablePayload.total.toLocaleString("zh-CN")} 行` : "暂无输出表"}</span>
          </div>
          <a
            href={exportTableUrl}
            className={`inline-flex h-10 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-4 text-sm font-semibold text-[#151720] ${
              selectedBatchId && selectedTable ? "" : "pointer-events-none opacity-40"
            }`}
          >
            <Download className="h-4 w-4 text-[#4896FE]" />
            导出Excel
          </a>
        </div>

        <div className="overflow-hidden rounded-xl border border-[#e8ecf3]">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-[#f7f9fc] text-xs font-semibold text-[#7b8190]">
                <tr>
                  {tableColumns.map((column) => (
                    <th key={column} className="whitespace-nowrap px-4 py-3">
                      {column}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#eef1f6]">
                {tableRows.map((row, rowIndex) => (
                  <tr key={`${rowIndex}-${String(row[tableColumns[0]] ?? rowIndex)}`} className="text-[#3d4351]">
                    {tableColumns.map((column) => (
                      <td key={column} className="max-w-80 whitespace-nowrap px-4 py-3 text-xs">
                        <span className="block overflow-hidden text-ellipsis">{formatCellValue(row[column])}</span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {tableLoadState === "loading" ? (
            <div className="border-t border-[#eef1f6] p-6 text-center text-sm text-[#8b92a1]">正在加载表数据...</div>
          ) : null}
          {tableLoadState !== "loading" && (!tablePayload || tableRows.length === 0) ? (
            <div className="border-t border-[#eef1f6] p-6 text-center text-sm text-[#8b92a1]">暂无表数据。</div>
          ) : null}
        </div>

        <DataPagination
          total={tableTotal}
          offset={offset}
          pageSize={pageSize}
          onOffsetChange={setOffset}
          onPageSizeChange={setPageSize}
        />
      </section>
    </div>
  );
}
