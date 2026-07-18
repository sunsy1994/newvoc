"use client";

import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { BarChart3, CalendarDays, Download, RefreshCw, Search, TableProperties } from "lucide-react";

import { DataPagination } from "@/components/shared/DataPagination";
import { apiBaseUrl } from "@/config/navigation";
import type { CompetitorListPayload, CompetitorOptionsPayload, CompetitorPageConfig, CompetitorWorkInsight } from "@/types/competitors";

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

function toDateInputValue(date: Date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function SummaryTile({ label, value, tone }: { label: string; value: string; tone: "purple" | "blue" | "teal" }) {
  const toneClass = {
    purple: "bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)]",
    blue: "bg-[var(--theme-soft-panel)] text-[var(--voc-chart-5)]",
    teal: "bg-[var(--theme-status-bg)] text-[var(--theme-status-text)]",
  }[tone];

  return (
    <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className={`mb-3 inline-flex h-8 w-8 items-center justify-center rounded-xl ${toneClass}`}>
        {tone === "purple" ? <TableProperties className="h-4 w-4" /> : <BarChart3 className="h-4 w-4" />}
      </div>
      <p className="text-xs text-[#8b92a1]">{label}</p>
      <p className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">{value}</p>
    </div>
  );
}

export function CompetitorLibraryPage({ config }: { config: CompetitorPageConfig }) {
  const [payload, setPayload] = useState<CompetitorListPayload | null>(null);
  const [options, setOptions] = useState<CompetitorOptionsPayload>({ brands: [], account_types: [] });
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [query, setQuery] = useState("");
  const [draftQuery, setDraftQuery] = useState("");
  const [brandName, setBrandName] = useState("");
  const [accountType, setAccountType] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [offset, setOffset] = useState(0);
  const [pageSize, setPageSize] = useState(defaultPageSize);
  const [selectedWork, setSelectedWork] = useState<Record<string, unknown> | null>(null);
  const [insightMarkdown, setInsightMarkdown] = useState("");
  const [isInsightLoading, setIsInsightLoading] = useState(false);
  const [isInsightSaving, setIsInsightSaving] = useState(false);
  const [insightError, setInsightError] = useState("");

  const total = payload?.total ?? 0;
  const rows = payload?.rows ?? [];

  const params = useMemo(() => {
    const nextParams = new URLSearchParams({ limit: String(pageSize), offset: String(offset) });
    if (query.trim()) nextParams.set("q", query.trim());
    if (config.mode === "works") {
      if (brandName) nextParams.set("brand_name", brandName);
      if (accountType) nextParams.set("account_type", accountType);
      if (startDate) nextParams.set("start_date", startDate);
      if (endDate) nextParams.set("end_date", endDate);
    }
    return nextParams;
  }, [accountType, brandName, config.mode, endDate, offset, pageSize, query, startDate]);

  const exportUrl = useMemo(() => {
    const exportParams = new URLSearchParams(params);
    exportParams.delete("limit");
    exportParams.delete("offset");
    return buildApiUrl(config.exportEndpoint, exportParams);
  }, [config.exportEndpoint, params]);

  const loadOptions = useCallback(async () => {
    if (config.mode !== "works") return;
    try {
      const response = await fetch(buildApiUrl("/competitors/options"), { cache: "no-store" });
      if (!response.ok) return;
      const nextOptions = (await response.json()) as CompetitorOptionsPayload;
      setOptions({
        brands: nextOptions.brands ?? [],
        account_types: nextOptions.account_types ?? [],
      });
    } catch {
      setOptions({ brands: [], account_types: [] });
    }
  }, [config.mode]);

  const loadRows = useCallback(async () => {
    setLoadState("loading");
    try {
      const response = await fetch(buildApiUrl(config.listEndpoint, params), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setPayload((await response.json()) as CompetitorListPayload);
      setLoadState("idle");
    } catch {
      setPayload(null);
      setLoadState("error");
    }
  }, [config.listEndpoint, params]);

  useEffect(() => {
    loadOptions();
  }, [loadOptions]);

  useEffect(() => {
    loadRows();
  }, [loadRows]);

  function submitFilters(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOffset(0);
    setQuery(draftQuery);
  }

  function applyQuickRange(days: number | null) {
    if (days === null) {
      setStartDate("");
      setEndDate("");
      setOffset(0);
      return;
    }
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - days + 1);
    setStartDate(toDateInputValue(start));
    setEndDate(toDateInputValue(end));
    setOffset(0);
  }

  async function openInsight(row: Record<string, unknown>) {
    const workId = String(row.work_id ?? "");
    if (!workId) return;

    setSelectedWork(row);
    setInsightMarkdown("");
    setInsightError("");
    setIsInsightLoading(true);
    try {
      const response = await fetch(buildApiUrl(`/competitors/works/${workId}/insight`), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const insight = (await response.json()) as CompetitorWorkInsight;
      setInsightMarkdown(insight.insight_markdown ?? "");
    } catch {
      setInsightError("解读加载失败，请稍后重试。");
    } finally {
      setIsInsightLoading(false);
    }
  }

  async function saveInsight(clear = false) {
    const workId = String(selectedWork?.work_id ?? "");
    if (!workId) return;

    setInsightError("");
    setIsInsightSaving(true);
    try {
      const response = clear
        ? await fetch(buildApiUrl(`/competitors/works/${workId}/insight`), { method: "DELETE" })
        : await fetch(buildApiUrl(`/competitors/works/${workId}/insight`), {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ insight_markdown: insightMarkdown }),
          });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      if (clear) setInsightMarkdown("");
      await loadRows();
    } catch {
      setInsightError(clear ? "解读清空失败，请稍后重试。" : "解读保存失败，请稍后重试。");
    } finally {
      setIsInsightSaving(false);
    }
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
        <SummaryTile label={config.mode === "accounts" ? "账号总数" : "作品总数"} value={total.toLocaleString("zh-CN")} tone="purple" />
        <SummaryTile
          label={config.mode === "accounts" ? "当前页账号" : "当前页作品"}
          value={rows.length.toLocaleString("zh-CN")}
          tone="blue"
        />
        <SummaryTile
          label={config.mode === "accounts" ? "查询范围" : "发布时间范围"}
          value={config.mode === "accounts" ? "全量" : startDate || endDate ? "已筛选" : "全量"}
          tone="teal"
        />
      </section>

      <section className="rounded-2xl border border-[#e8ecf3] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-[#151720]">{config.listTitle}</h2>
            <p className="mt-1 text-xs text-[#8b92a1]">
              {loadState === "error" ? "加载失败，请检查后端和数据库连接。" : config.listMeta}
            </p>
          </div>
          <form className="flex flex-wrap items-center justify-end gap-2" onSubmit={submitFilters}>
            <div className="flex h-10 min-w-64 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3">
              <Search className="h-4 w-4 text-[#8b92a1]" />
              <input
                value={draftQuery}
                onChange={(event) => setDraftQuery(event.target.value)}
                placeholder={config.searchPlaceholder}
                className="min-w-0 flex-1 bg-transparent text-sm text-[#151720] outline-none placeholder:text-[#a3a9b5]"
              />
            </div>
            {config.mode === "works" ? (
              <>
                <select
                  value={brandName}
                  onChange={(event) => {
                    setOffset(0);
                    setBrandName(event.target.value);
                  }}
                  className="h-10 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-sm text-[#596070] outline-none focus:border-[var(--sys-icon-fill)]"
                >
                  <option value="">全部品牌</option>
                  {options.brands.map((brand) => (
                    <option key={brand} value={brand}>
                      {brand}
                    </option>
                  ))}
                </select>
                <select
                  value={accountType}
                  onChange={(event) => {
                    setOffset(0);
                    setAccountType(event.target.value);
                  }}
                  className="h-10 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-sm text-[#596070] outline-none focus:border-[var(--sys-icon-fill)]"
                >
                  <option value="">全部账号类型</option>
                  {options.account_types.map((type) => (
                    <option key={type} value={type}>
                      {type}
                    </option>
                  ))}
                </select>
                <div className="flex h-10 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3">
                  <CalendarDays className="h-4 w-4 text-[#8b92a1]" />
                  <input
                    type="date"
                    value={startDate}
                    onChange={(event) => {
                      setOffset(0);
                      setStartDate(event.target.value);
                    }}
                    className="bg-transparent text-sm text-[#596070] outline-none"
                    aria-label="开始日期"
                  />
                  <span className="text-xs text-[#a3a9b5]">至</span>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(event) => {
                      setOffset(0);
                      setEndDate(event.target.value);
                    }}
                    className="bg-transparent text-sm text-[#596070] outline-none"
                    aria-label="结束日期"
                  />
                </div>
              </>
            ) : null}
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

        {config.mode === "works" ? (
          <div className="mb-4 flex flex-wrap gap-2">
            {[
              ["近7天", 7],
              ["近30天", 30],
              ["近90天", 90],
            ].map(([label, days]) => (
              <button
                key={label}
                type="button"
                onClick={() => applyQuickRange(Number(days))}
                className="h-8 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-xs font-medium text-[#596070]"
              >
                {label}
              </button>
            ))}
            <button
              type="button"
              onClick={() => applyQuickRange(null)}
              className="h-8 rounded-lg border border-[#e8ecf3] bg-white px-3 text-xs font-medium text-[#596070]"
            >
              全部
            </button>
          </div>
        ) : null}

        <div className="overflow-hidden rounded-xl border border-[#e8ecf3]">
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="bg-[#f7f9fc] text-xs font-semibold text-[#7b8190]">
                <tr>
                  {(payload?.columns ?? []).map((column) => (
                    <th key={column.key} className="whitespace-nowrap px-4 py-3">
                      {column.label}
                    </th>
                  ))}
                  {config.mode === "works" ? (
                    <th className="whitespace-nowrap px-4 py-3">解读维护</th>
                  ) : null}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#eef1f6]">
                {payload?.rows.map((row, rowIndex) => (
                  <tr key={`${rowIndex}-${String(row[payload.columns[0]?.key] ?? rowIndex)}`} className="text-[#3d4351]">
                    {payload.columns.map((column) => (
                      <td key={column.key} className="max-w-80 whitespace-nowrap px-4 py-3 text-xs">
                        <span className="block overflow-hidden text-ellipsis">{formatCellValue(row[column.key])}</span>
                      </td>
                    ))}
                    {config.mode === "works" ? (
                      <td className="whitespace-nowrap px-4 py-3 text-xs">
                        <button
                          type="button"
                          onClick={() => openInsight(row)}
                          className="rounded-md border border-[#dfe5ee] bg-white px-2.5 py-1.5 font-medium text-[#485160] hover:border-[var(--sys-icon-fill)] hover:text-[var(--sys-icon-fill)]"
                        >
                          维护解读（{row.has_insight === true ? "已维护" : "未维护"}）
                        </button>
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {loadState === "loading" ? (
            <div className="border-t border-[#eef1f6] p-6 text-center text-sm text-[#8b92a1]">正在加载竞品数据...</div>
          ) : null}
          {loadState !== "loading" && (!payload || payload.rows.length === 0) ? (
            <div className="border-t border-[#eef1f6] p-6 text-center text-sm text-[#8b92a1]">暂无竞品数据。</div>
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

      {config.mode === "works" && selectedWork ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#151720]/30 p-4">
          <section className="w-full max-w-3xl rounded-2xl bg-white p-6 shadow-[0_24px_64px_rgba(21,23,32,0.22)]" role="dialog" aria-modal="true" aria-label="维护作品解读">
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-medium text-[#8b92a1]">竞品作品库</p>
                <h2 className="mt-1 text-lg font-semibold text-[#151720]">维护解读</h2>
              </div>
              <button
                type="button"
                onClick={() => setSelectedWork(null)}
                className="rounded-lg border border-[#e8ecf3] px-3 py-1.5 text-sm text-[#596070]"
              >
                关闭
              </button>
            </div>
            <dl className="mt-5 grid gap-3 rounded-xl bg-[#f7f9fc] p-4 text-sm text-[#596070] sm:grid-cols-2">
              <div><dt className="text-xs text-[#8b92a1]">标题</dt><dd className="mt-1 text-[#151720]">{formatCellValue(selectedWork.title)}</dd></div>
              <div><dt className="text-xs text-[#8b92a1]">作者</dt><dd className="mt-1 text-[#151720]">{formatCellValue(selectedWork.author_name)}</dd></div>
              <div><dt className="text-xs text-[#8b92a1]">品牌</dt><dd className="mt-1 text-[#151720]">{formatCellValue(selectedWork.brand_name)}</dd></div>
              <div><dt className="text-xs text-[#8b92a1]">发布时间</dt><dd className="mt-1 text-[#151720]">{formatCellValue(selectedWork.published_at)}</dd></div>
            </dl>
            <textarea
              value={insightMarkdown}
              onChange={(event) => setInsightMarkdown(event.target.value)}
              disabled={isInsightLoading || isInsightSaving}
              placeholder={isInsightLoading ? "正在加载解读..." : "填写作品解读（Markdown）"}
              className="mt-4 h-64 w-full resize-y rounded-xl border border-[#dfe5ee] p-3 font-mono text-sm leading-6 text-[#151720] outline-none focus:border-[var(--sys-icon-fill)]"
            />
            {insightError ? <p className="mt-2 text-sm text-[#c65c5c]">{insightError}</p> : null}
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => saveInsight(true)}
                disabled={isInsightLoading || isInsightSaving}
                className="rounded-lg border border-[#e8ecf3] px-4 py-2 text-sm font-medium text-[#596070] disabled:cursor-not-allowed disabled:opacity-50"
              >
                清空解读
              </button>
              <button
                type="button"
                onClick={() => saveInsight()}
                disabled={isInsightLoading || isInsightSaving}
                className="rounded-lg bg-[var(--sys-icon-fill)] px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isInsightSaving ? "保存中..." : "保存解读"}
              </button>
            </div>
          </section>
        </div>
      ) : null}
    </div>
  );
}
