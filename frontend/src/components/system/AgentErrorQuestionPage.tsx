"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { RefreshCw, TriangleAlert } from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import { DataPagination } from "@/components/shared/DataPagination";
import type { AgentErrorQuestionListPayload, AgentErrorQuestionRecord } from "@/types/system";

type LoadState = "idle" | "loading" | "error";

function formatDateTime(value: string) {
  if (!value) return "-";
  return value.replace("T", " ");
}

export function AgentErrorQuestionPage() {
  const [records, setRecords] = useState<AgentErrorQuestionRecord[]>([]);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [offset, setOffset] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const visibleRecords = useMemo(() => records.slice(offset, offset + pageSize), [offset, pageSize, records]);

  const loadRecords = useCallback(async () => {
    setLoadState("loading");
    try {
      const response = await fetch(`${apiBaseUrl}/system/agent-error-questions`, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = (await response.json()) as AgentErrorQuestionListPayload;
      setRecords(payload.records ?? []);
      setLoadState("idle");
    } catch {
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    loadRecords();
  }, [loadRecords]);

  useEffect(() => {
    if (offset < records.length || offset === 0) return;
    setOffset(Math.max(0, (Math.ceil(records.length / pageSize) - 1) * pageSize));
  }, [offset, pageSize, records.length]);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-[var(--sys-subtle)]">System Management</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--sys-title)]">异常问题记录</h1>
          <p className="mt-2 text-sm text-[var(--sys-body)]">记录 AI 问答、问数执行异常时的用户问题和后台报错原因，用于后续补数据和补工具。</p>
        </div>
        <button
          type="button"
          onClick={loadRecords}
          className="inline-flex h-10 items-center gap-2 rounded-[12px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-4 text-sm font-semibold text-[var(--sys-body)] shadow-[var(--sys-card-shadow)]"
        >
          <RefreshCw className="h-4 w-4" />
          刷新
        </button>
      </header>

      <section className="premium-card rounded-[20px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-6">
        <div className="mb-4 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)]">
            <TriangleAlert className="h-5 w-5" />
          </div>
          <div>
            <h2 className="text-[15px] font-semibold tracking-tight text-[var(--sys-title)]">异常问题表</h2>
            <p className="mt-1 text-xs text-[var(--sys-muted)]">共 {records.length} 条，最新问题排在最前。</p>
          </div>
        </div>

        <div className="overflow-hidden rounded-2xl border border-[var(--sys-input-border)]">
          <table className="w-full text-left text-sm">
            <thead className="bg-[var(--sys-panel-bg)] text-[11px] font-semibold uppercase tracking-[0.04em] text-[var(--sys-muted)]">
              <tr>
                <th className="w-40 px-4 py-3">时间</th>
                <th className="w-28 px-4 py-3">能力</th>
                <th className="px-4 py-3">用户问题</th>
                <th className="px-4 py-3">报错原因</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--sys-input-border)]">
              {visibleRecords.map((record) => (
                <tr key={record.record_id} className="bg-[var(--sys-card)] align-top">
                  <td className="px-4 py-3 text-xs text-[var(--sys-muted)]">{formatDateTime(record.created_at)}</td>
                  <td className="px-4 py-3 text-[var(--sys-body)]">{record.capability}</td>
                  <td className="px-4 py-3 leading-6 text-[var(--sys-ink)]">{record.question}</td>
                  <td className="px-4 py-3 font-mono text-xs leading-5 text-[var(--sys-body)]">{record.error_reason}</td>
                </tr>
              ))}
              {!records.length ? (
                <tr>
                  <td colSpan={4} className="px-4 py-10 text-center text-sm text-[var(--sys-muted)]">
                    {loadState === "loading" ? "正在加载..." : loadState === "error" ? "异常问题记录加载失败" : "暂无异常问题记录"}
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
        <DataPagination total={records.length} offset={offset} pageSize={pageSize} onOffsetChange={setOffset} onPageSizeChange={setPageSize} />
      </section>
    </div>
  );
}
