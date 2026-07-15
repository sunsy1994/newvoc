"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { Database, Download, RefreshCw, Search, TableProperties, X } from "lucide-react";

import { DataPagination } from "@/components/shared/DataPagination";
import { StructuredReportView } from "@/components/voc/ReportAiSummaryCard";
import { apiBaseUrl } from "@/config/navigation";
import type { AssetListPayload, AssetPageConfig } from "@/types/assets";
import type { StructuredReport } from "@/types/vocMarket";

const defaultPageSize = 10;

type LoadState = "idle" | "loading" | "error";

function buildApiUrl(endpoint: string, params?: URLSearchParams) {
  const query = params?.toString();
  return `${apiBaseUrl}${endpoint}${query ? `?${query}` : ""}`;
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

function AssetMetric({ label, value, tone }: { label: string; value: string; tone: "purple" | "blue" | "teal" }) {
  const toneClass = {
    purple: "bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)]",
    blue: "bg-[var(--theme-soft-panel)] text-[var(--voc-chart-5)]",
    teal: "bg-[var(--theme-status-bg)] text-[var(--theme-status-text)]",
  }[tone];

  return (
    <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className={`mb-3 inline-flex h-8 w-8 items-center justify-center rounded-xl ${toneClass}`}>
        {tone === "purple" ? <Database className="h-4 w-4" /> : <TableProperties className="h-4 w-4" />}
      </div>
      <p className="text-xs text-[#8b92a1]">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">{value}</p>
    </div>
  );
}

export function AssetLibraryPage({ config }: { config: AssetPageConfig }) {
  const [payload, setPayload] = useState<AssetListPayload | null>(null);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [query, setQuery] = useState("");
  const [draftQuery, setDraftQuery] = useState("");
  const [offset, setOffset] = useState(0);
  const [pageSize, setPageSize] = useState(defaultPageSize);
  const [openReport, setOpenReport] = useState<StructuredReport | null>(null);

  const total = payload?.total ?? 0;
  const rows = payload?.rows ?? [];
  const columns = payload?.columns ?? [];
  const isReportAsset = config.assetKey === "reports";

  const params = useMemo(() => {
    const nextParams = new URLSearchParams({ limit: String(pageSize), offset: String(offset) });
    if (query.trim()) nextParams.set("q", query.trim());
    return nextParams;
  }, [offset, pageSize, query]);

  const exportUrl = useMemo(() => {
    const exportParams = new URLSearchParams(params);
    exportParams.delete("limit");
    exportParams.delete("offset");
    return buildApiUrl(`/assets/${config.assetKey}/export`, exportParams);
  }, [config.assetKey, params]);

  const loadRows = useCallback(async () => {
    setLoadState("loading");
    try {
      const response = await fetch(buildApiUrl(`/assets/${config.assetKey}`, params), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setPayload((await response.json()) as AssetListPayload);
      setLoadState("idle");
    } catch {
      setPayload(null);
      setLoadState("error");
    }
  }, [config.assetKey, params]);

  useEffect(() => {
    loadRows();
  }, [loadRows]);

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOffset(0);
    setQuery(draftQuery);
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">{config.eyebrow}</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">{config.title}</h1>
        </div>
        <a
          href={exportUrl}
          className="inline-flex h-10 items-center gap-2 rounded-lg bg-[var(--sys-icon-fill)] px-4 text-sm font-semibold text-white shadow-[0_12px_22px_rgba(93,150,145,0.16)]"
        >
          <Download className="h-4 w-4" />
          导出Excel
        </a>
      </header>

      <section className="grid gap-3 md:grid-cols-3">
        <AssetMetric label="资产总数" value={total.toLocaleString("zh-CN")} tone="purple" />
        <AssetMetric label="当前页资产" value={rows.length.toLocaleString("zh-CN")} tone="blue" />
        <AssetMetric label="业务字段" value={columns.length.toLocaleString("zh-CN")} tone="teal" />
      </section>

      <section className="rounded-2xl border border-[#e8ecf3] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-[#151720]">{config.listTitle}</h2>
            <p className="mt-1 text-xs text-[#8b92a1]">
              {loadState === "error" ? "加载失败，请检查后端和数据库连接。" : config.listMeta}
            </p>
          </div>
          <form className="flex flex-wrap items-center gap-2" onSubmit={submitSearch}>
            <div className="flex h-10 min-w-72 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3">
              <Search className="h-4 w-4 text-[#8b92a1]" />
              <input
                value={draftQuery}
                onChange={(event) => setDraftQuery(event.target.value)}
                placeholder={config.searchPlaceholder}
                className="min-w-0 flex-1 bg-transparent text-sm text-[#151720] outline-none placeholder:text-[#a3a9b5]"
              />
            </div>
            <button type="submit" className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#151720] px-4 text-sm font-semibold text-white">
              <Search className="h-4 w-4" />
              查询
            </button>
            <button
              type="button"
              onClick={() => loadRows()}
              className="inline-flex h-10 items-center justify-center rounded-lg border border-[#e8ecf3] bg-white px-3 text-[#596070]"
              title="刷新"
            >
              <RefreshCw className="h-4 w-4" />
            </button>
          </form>
        </div>

        <div className="overflow-hidden rounded-xl border border-[#e8ecf3]">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-[#f7f9fc] text-xs font-semibold text-[#7b8190]">
                <tr>
                  {columns.map((column) => (
                    <th key={column.key} className="whitespace-nowrap px-4 py-3">
                      {column.label}
                    </th>
                  ))}
                  {isReportAsset ? <th className="whitespace-nowrap px-4 py-3">操作</th> : null}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#eef1f6]">
                {rows.map((row, rowIndex) => (
                  <tr key={`${rowIndex}-${String(row[columns[0]?.key] ?? rowIndex)}`} className="text-[#3d4351]">
                    {columns.map((column) => (
                      <td key={column.key} className="max-w-80 whitespace-nowrap px-4 py-3 text-xs">
                        <span className="block overflow-hidden text-ellipsis">{formatCellValue(row[column.key])}</span>
                      </td>
                    ))}
                    {isReportAsset ? (
                      <td className="whitespace-nowrap px-4 py-3 text-xs">
                        <button
                          type="button"
                          onClick={() => {
                            const summary = row.summary_json as { structured_report?: StructuredReport } | undefined;
                            setOpenReport(summary?.structured_report ?? null);
                          }}
                          className="rounded-lg border border-[var(--sys-border)] bg-white px-3 py-1.5 font-semibold text-[var(--sys-icon-fill)] transition hover:border-[var(--sys-icon-fill)] hover:bg-[var(--theme-soft-panel)]"
                        >
                          查看
                        </button>
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {loadState === "loading" ? (
            <div className="border-t border-[#eef1f6] p-6 text-center text-sm text-[#8b92a1]">正在加载资产数据...</div>
          ) : null}
          {loadState !== "loading" && rows.length === 0 ? (
            <div className="border-t border-[#eef1f6] p-6 text-center text-sm text-[#8b92a1]">暂无资产数据。</div>
          ) : null}
        </div>

        <DataPagination
          total={total}
          offset={offset}
          pageSize={pageSize}
          onOffsetChange={setOffset}
          onPageSizeChange={setPageSize}
        />
      </section>
      {openReport ? (
        <div className="fixed inset-0 z-[80] flex items-center justify-center bg-black/20 p-4 backdrop-blur-sm">
          <div className="max-h-[88vh] w-full max-w-5xl overflow-hidden rounded-[28px] border border-[var(--theme-border)] bg-[var(--theme-white)] shadow-[0_24px_80px_rgba(26,32,44,0.2)]">
            <header className="flex items-center justify-between gap-3 border-b border-[var(--theme-border)] bg-[linear-gradient(135deg,var(--theme-selected-bg),var(--theme-card))] p-5">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--theme-muted)]">Report Asset</p>
                <h2 className="mt-1 text-xl font-semibold tracking-tight text-[var(--theme-ink)]">{openReport.title}</h2>
              </div>
              <button
                type="button"
                onClick={() => setOpenReport(null)}
                className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-body)] transition hover:bg-[var(--theme-hover-bg)]"
                aria-label="关闭报告"
              >
                <X className="h-4 w-4" />
              </button>
            </header>
            <div className="max-h-[calc(88vh-86px)] overflow-auto p-5">
              <StructuredReportView report={openReport} />
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}
