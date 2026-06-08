"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, FileCode2, Loader2, Play, RefreshCw, Save, ServerCog } from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import type { EtlScriptPayload } from "@/types/etlScript";
import type { ImportTask } from "@/types/tasks";

type LoadState = "idle" | "loading" | "error";

function buildApiUrl(endpoint: string) {
  return `${apiBaseUrl}${endpoint}`;
}

function formatDate(value?: string | null) {
  if (!value) return "-";
  return value.replace("T", " ").replace("Z", "").slice(0, 19);
}

function formatSize(size: number) {
  if (size < 1024) return `${size} B`;
  return `${(size / 1024).toFixed(1)} KB`;
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

function StatCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <p className="text-xs text-[#8b92a1]">{label}</p>
      <p className="mt-1 truncate text-lg font-semibold tracking-tight text-[#151720]" title={value}>
        {value}
      </p>
    </div>
  );
}

export function ScriptMaintenancePage() {
  const [script, setScript] = useState<EtlScriptPayload | null>(null);
  const [content, setContent] = useState("");
  const [tasks, setTasks] = useState<ImportTask[]>([]);
  const [selectedBatchId, setSelectedBatchId] = useState("");
  const [loadState, setLoadState] = useState<LoadState>("loading");
  const [saveState, setSaveState] = useState<LoadState>("idle");
  const [runState, setRunState] = useState<LoadState>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [runResult, setRunResult] = useState<ImportTask | null>(null);

  const isDirty = useMemo(() => Boolean(script && content !== script.content), [content, script]);

  const loadScript = useCallback(async () => {
    setLoadState("loading");
    setMessage(null);
    try {
      const response = await fetch(buildApiUrl("/etl/script"), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = (await response.json()) as EtlScriptPayload;
      setScript(payload);
      setContent(payload.content);
      setLoadState("idle");
    } catch {
      setLoadState("error");
      setMessage("脚本加载失败，请检查后端服务。");
    }
  }, []);

  const loadTasks = useCallback(async () => {
    try {
      const response = await fetch(buildApiUrl("/tasks"), { cache: "no-store" });
      if (!response.ok) return;
      const nextTasks = (await response.json()) as ImportTask[];
      setTasks(nextTasks);
      setSelectedBatchId((current) => current || nextTasks[0]?.batch_id || "");
    } catch {
      setTasks([]);
    }
  }, []);

  useEffect(() => {
    loadScript();
    loadTasks();
  }, [loadScript, loadTasks]);

  async function saveScript() {
    setSaveState("loading");
    setMessage("正在保存脚本并生成备份...");
    try {
      const response = await fetch(buildApiUrl("/etl/script"), {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = (await response.json()) as EtlScriptPayload;
      setScript(payload);
      setContent(payload.content);
      setSaveState("idle");
      setMessage("已保存，旧脚本已自动备份。");
    } catch {
      setSaveState("error");
      setMessage("保存失败，请检查脚本文件权限或后端日志。");
    }
  }

  async function runScript() {
    if (!selectedBatchId) return;
    setRunState("loading");
    setRunResult(null);
    setMessage("正在用选中批次试跑当前脚本...");
    try {
      const response = await fetch(buildApiUrl("/etl/script/test-run"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ batch_id: selectedBatchId }),
      });
      const payload = (await response.json()) as ImportTask | { detail?: string };
      if (!response.ok) throw new Error("detail" in payload ? String(payload.detail) : `HTTP ${response.status}`);
      setRunResult(payload as ImportTask);
      setRunState("idle");
      setMessage((payload as ImportTask).status === "success" ? "试跑成功，结果已更新。" : "试跑完成，但状态不是成功，请查看错误信息。");
      await loadTasks();
    } catch (error) {
      setRunState("error");
      setMessage(error instanceof Error ? error.message : "试跑失败，请查看后端日志。");
    }
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">Task Management</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">脚本维护</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={loadScript}
            className="inline-flex h-10 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-4 text-sm font-semibold text-[#596070]"
          >
            <RefreshCw className="h-4 w-4" />
            重新读取
          </button>
          <button
            type="button"
            disabled={!isDirty || saveState === "loading"}
            onClick={saveScript}
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#5347CE] px-4 text-sm font-semibold text-white shadow-[0_12px_22px_rgba(83,71,206,0.22)] disabled:cursor-not-allowed disabled:opacity-40"
          >
            {saveState === "loading" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            保存并备份
          </button>
        </div>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <StatCard label="脚本文件" value={script?.path.split(/[\\/]/).pop() ?? "-"} />
        <StatCard label="文件大小" value={script ? formatSize(script.size) : "-"} />
        <StatCard label="更新时间" value={formatDate(script?.updated_at)} />
        <StatCard label="备份数量" value={`${script?.backups.length ?? 0} 个`} />
      </section>

      {message ? (
        <div className="flex items-center gap-2 rounded-2xl border border-[#e8ecf3] bg-white px-4 py-3 text-sm text-[#596070] shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          {saveState === "error" || runState === "error" || loadState === "error" ? (
            <AlertTriangle className="h-4 w-4 text-[#d94a4a]" />
          ) : (
            <CheckCircle2 className="h-4 w-4 text-[#16C8C7]" />
          )}
          {message}
        </div>
      ) : null}

      <section className="grid gap-4 xl:grid-cols-[1fr_360px]">
        <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <div className="mb-4 flex items-start gap-3">
            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#f0efff] text-[#5347CE]">
              <FileCode2 className="h-4 w-4" />
            </div>
            <div className="min-w-0">
              <h2 className="text-sm font-semibold text-[#151720]">ETL 脚本内容</h2>
              <p className="mt-1 truncate text-xs text-[#8b92a1]" title={script?.path}>
                {script?.path ?? "读取脚本中..."}
              </p>
            </div>
          </div>
          <textarea
            value={content}
            onChange={(event) => setContent(event.target.value)}
            spellCheck={false}
            className="h-[620px] w-full resize-y rounded-2xl border border-[#e8ecf3] bg-[#0f1420] p-4 font-mono text-xs leading-5 text-[#edf2ff] outline-none focus:border-[#887CFD] focus:ring-4 focus:ring-[#887CFD]/10"
            placeholder={loadState === "loading" ? "正在读取脚本..." : "暂无脚本内容"}
          />
        </section>

        <aside className="space-y-4">
          <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
            <div className="mb-4 flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#eef6ff] text-[#4896FE]">
                <ServerCog className="h-4 w-4" />
              </div>
              <div>
                <h2 className="text-sm font-semibold text-[#151720]">批次试跑</h2>
                <p className="mt-1 text-xs leading-5 text-[#8b92a1]">用当前脚本对已上传批次重新执行 ETL。</p>
              </div>
            </div>
            <select
              value={selectedBatchId}
              onChange={(event) => setSelectedBatchId(event.target.value)}
              className="h-10 w-full rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-sm text-[#596070] outline-none focus:border-[#5347CE]"
            >
              <option value="">选择批次</option>
              {tasks.map((task) => (
                <option key={task.batch_id} value={task.batch_id}>
                  {task.batch_id} / {statusLabel(task.status)}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={!selectedBatchId || runState === "loading"}
              onClick={runScript}
              className="mt-3 inline-flex h-10 w-full items-center justify-center gap-2 rounded-lg bg-[#151720] px-4 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-40"
            >
              {runState === "loading" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
              用选中批次试跑
            </button>
            {runResult ? (
              <div className="mt-4 rounded-xl border border-[#e8ecf3] bg-[#f7f9fc] p-3">
                <div className="flex items-center justify-between gap-2">
                  <span className="truncate text-xs font-semibold text-[#151720]">{runResult.batch_id}</span>
                  <span className={`rounded-lg px-2 py-1 text-[11px] font-semibold ${statusClass(runResult.status)}`}>{statusLabel(runResult.status)}</span>
                </div>
                {runResult.error_message ? <p className="mt-2 line-clamp-4 text-xs leading-5 text-[#d94a4a]">{runResult.error_message}</p> : null}
              </div>
            ) : null}
          </section>

          <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
            <h2 className="text-sm font-semibold text-[#151720]">最近备份</h2>
            <div className="mt-3 max-h-80 space-y-2 overflow-y-auto pr-1">
              {script?.backups.length ? null : <p className="rounded-xl bg-[#f7f9fc] p-3 text-xs text-[#8b92a1]">暂无备份文件</p>}
              {script?.backups.map((backup) => (
                <div key={backup.path} className="rounded-xl border border-[#e8ecf3] bg-white p-3">
                  <p className="truncate text-xs font-semibold text-[#151720]" title={backup.name}>
                    {backup.name}
                  </p>
                  <p className="mt-1 text-[11px] text-[#8b92a1]">
                    {formatDate(backup.created_at)} / {formatSize(backup.size)}
                  </p>
                </div>
              ))}
            </div>
          </section>
        </aside>
      </section>
    </div>
  );
}
