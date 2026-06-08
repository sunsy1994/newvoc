"use client";

import { ChangeEvent, FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  Database,
  Download,
  FileSpreadsheet,
  RefreshCw,
  Search,
  UploadCloud,
} from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import type { ProfileBatchesPayload, ProfileListPayload, ProfilePageConfig } from "@/types/profiles";

const pageSize = 50;

type LoadState = "idle" | "loading" | "error";

function formatCellValue(value: unknown) {
  if (value === null || value === undefined || value === "") return "-";
  if (typeof value === "number") return value.toLocaleString("zh-CN");
  if (typeof value === "string") {
    const dateLike = /^\d{4}-\d{2}-\d{2}T/.test(value);
    if (dateLike) return value.replace("T", " ").slice(0, 19);
    return value;
  }
  return JSON.stringify(value);
}

function buildApiUrl(endpoint: string, params?: URLSearchParams) {
  const query = params?.toString();
  return `${apiBaseUrl}${endpoint}${query ? `?${query}` : ""}`;
}

function formatUploadSuccess(mode: ProfilePageConfig["mode"], payload: Record<string, unknown>) {
  if (mode === "kols") {
    return `已上传 ${Number(payload.loaded ?? 0).toLocaleString("zh-CN")} 条KOL画像`;
  }
  return `已上传 ${Number(payload.raw_loaded ?? 0).toLocaleString("zh-CN")} 条LLM结果，生成 ${Number(
    payload.profiles_loaded ?? 0,
  ).toLocaleString("zh-CN")} 条用户画像`;
}

function ProfileCard({
  title,
  meta,
  icon,
  children,
}: {
  title: string;
  meta?: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className="mb-4 flex items-start gap-3">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#f0efff] text-[#5347CE]">{icon}</div>
        <div>
          <h2 className="text-sm font-semibold text-[#151720]">{title}</h2>
          {meta ? <p className="mt-1 text-xs leading-5 text-[#8b92a1]">{meta}</p> : null}
        </div>
      </div>
      {children}
    </section>
  );
}

function StatusMessage({ message }: { message: string | null }) {
  if (!message) return null;
  return (
    <div className="rounded-xl border border-[#e8ecf3] bg-[#f7f9fc] px-3 py-2 text-xs text-[#596070]">
      {message}
    </div>
  );
}

export function ProfileMaintenancePage({ config }: { config: ProfilePageConfig }) {
  const [payload, setPayload] = useState<ProfileListPayload | null>(null);
  const [batches, setBatches] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const [draftQuery, setDraftQuery] = useState("");
  const [batch, setBatch] = useState("");
  const [offset, setOffset] = useState(0);
  const [sampleDays, setSampleDays] = useState(7);
  const [loadState, setLoadState] = useState<LoadState>("idle");
  const [message, setMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const total = payload?.total ?? 0;
  const startRow = total > 0 ? offset + 1 : 0;
  const endRow = Math.min(offset + pageSize, total);
  const hasPrev = offset > 0;
  const hasNext = offset + pageSize < total;

  const loadBatches = useCallback(async () => {
    const response = await fetch(buildApiUrl(config.batchesEndpoint), { cache: "no-store" });
    if (!response.ok) return;
    const nextPayload = (await response.json()) as ProfileBatchesPayload;
    setBatches(nextPayload.batches ?? []);
  }, [config.batchesEndpoint]);

  const loadProfiles = useCallback(async () => {
    setLoadState("loading");
    const params = new URLSearchParams({ limit: String(pageSize), offset: String(offset) });
    if (query.trim()) params.set("q", query.trim());
    if (batch) params.set("profile_batch", batch);

    try {
      const response = await fetch(buildApiUrl(config.listEndpoint, params), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const nextPayload = (await response.json()) as ProfileListPayload;
      setPayload(nextPayload);
      setLoadState("idle");
    } catch {
      setPayload(null);
      setLoadState("error");
    }
  }, [batch, config.listEndpoint, offset, query]);

  useEffect(() => {
    loadBatches();
  }, [loadBatches]);

  useEffect(() => {
    loadProfiles();
  }, [loadProfiles]);

  const exportUrl = useMemo(() => {
    if (!config.sampleDays) return buildApiUrl(config.exportEndpoint);
    const params = new URLSearchParams({ days: String(Math.max(1, sampleDays)) });
    return buildApiUrl(config.exportEndpoint, params);
  }, [config.exportEndpoint, config.sampleDays, sampleDays]);

  function submitSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setOffset(0);
    setQuery(draftQuery);
  }

  function handleBatchChange(event: ChangeEvent<HTMLSelectElement>) {
    setOffset(0);
    setBatch(event.target.value);
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      setMessage("请先选择要上传的 Excel 文件。");
      return;
    }
    const formData = new FormData();
    formData.append("profile_file", file);
    setMessage("正在上传画像文件...");

    try {
      const response = await fetch(buildApiUrl(config.uploadEndpoint), {
        method: "POST",
        body: formData,
      });
      const result = (await response.json()) as Record<string, unknown>;
      if (!response.ok) {
        setMessage(String(result.detail ?? "上传失败，请检查文件字段。"));
        return;
      }
      setMessage(formatUploadSuccess(config.mode, result));
      if (fileInputRef.current) fileInputRef.current.value = "";
      setOffset(0);
      await Promise.all([loadProfiles(), loadBatches()]);
    } catch {
      setMessage("上传失败，请确认后端服务和 PostgreSQL 已启动。");
    }
  }

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">{config.eyebrow}</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">{config.title}</h1>
        </div>
        <div className="inline-flex items-center gap-2 rounded-2xl border border-[#e8ecf3] bg-white px-3 py-2 text-xs text-[#7b8190] shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
          <Database className="h-3.5 w-3.5 text-[#5347CE]" />
          PostgreSQL 实时读取
        </div>
      </header>

      <section className="grid gap-4 lg:grid-cols-[0.92fr_1.08fr]">
        <ProfileCard
          title={config.sampleTitle}
          meta={config.sampleMeta}
          icon={<FileSpreadsheet className="h-4 w-4" />}
        >
          <div className="flex flex-wrap items-center gap-2">
            {config.sampleDays ? (
              <input
                type="number"
                min={1}
                max={365}
                value={sampleDays}
                onChange={(event) => setSampleDays(Number(event.target.value || 1))}
                className="h-10 w-28 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-sm font-medium text-[#151720] outline-none focus:border-[#5347CE]"
              />
            ) : null}
            <a
              href={exportUrl}
              className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#5347CE] px-4 text-sm font-semibold text-white shadow-[0_12px_22px_rgba(83,71,206,0.22)]"
            >
              <Download className="h-4 w-4" />
              导出样本
            </a>
          </div>
        </ProfileCard>

        <ProfileCard title={config.uploadTitle} meta={config.uploadMeta} icon={<UploadCloud className="h-4 w-4" />}>
          <form className="flex flex-wrap items-center gap-2" onSubmit={handleUpload}>
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls"
              className="h-10 min-w-0 flex-1 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 py-2 text-sm text-[#596070] file:mr-3 file:rounded-md file:border-0 file:bg-white file:px-2 file:py-1 file:text-xs file:font-medium file:text-[#5347CE]"
            />
            <button
              type="submit"
              className="inline-flex h-10 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-white px-4 text-sm font-semibold text-[#151720] shadow-[0_8px_20px_rgba(26,32,44,0.03)]"
            >
              <UploadCloud className="h-4 w-4 text-[#4896FE]" />
              上传入库
            </button>
          </form>
          <div className="mt-3">
            <StatusMessage message={message} />
          </div>
        </ProfileCard>
      </section>

      <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-[#151720]">{config.listTitle}</h2>
            <p className="mt-1 text-xs text-[#8b92a1]">
              {loadState === "error" ? "加载失败，请检查后端和数据库连接。" : `共 ${total.toLocaleString("zh-CN")} 条`}
            </p>
          </div>
          <form className="flex flex-wrap items-center gap-2" onSubmit={submitSearch}>
            <div className="flex h-10 min-w-64 items-center gap-2 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3">
              <Search className="h-4 w-4 text-[#8b92a1]" />
              <input
                value={draftQuery}
                onChange={(event) => setDraftQuery(event.target.value)}
                placeholder={config.searchPlaceholder}
                className="min-w-0 flex-1 bg-transparent text-sm text-[#151720] outline-none placeholder:text-[#a3a9b5]"
              />
            </div>
            <select
              value={batch}
              onChange={handleBatchChange}
              className="h-10 rounded-lg border border-[#e8ecf3] bg-[#f7f9fc] px-3 text-sm text-[#596070] outline-none focus:border-[#5347CE]"
            >
              <option value="">全部批次</option>
              {batches.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <button
              type="submit"
              className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#151720] px-4 text-sm font-semibold text-white"
            >
              <Search className="h-4 w-4" />
              查询
            </button>
            <button
              type="button"
              onClick={() => loadProfiles()}
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
                  {(payload?.columns ?? []).map((column) => (
                    <th key={column.key} className="whitespace-nowrap px-4 py-3">
                      {column.label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[#eef1f6]">
                {payload?.rows.map((row, rowIndex) => (
                  <tr key={`${rowIndex}-${String(row[payload.columns[0]?.key] ?? rowIndex)}`} className="text-[#3d4351]">
                    {payload.columns.map((column) => (
                      <td key={column.key} className="max-w-72 whitespace-nowrap px-4 py-3 text-xs">
                        <span className="block overflow-hidden text-ellipsis">{formatCellValue(row[column.key])}</span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {loadState === "loading" ? (
            <div className="border-t border-[#eef1f6] p-6 text-center text-sm text-[#8b92a1]">正在加载画像数据...</div>
          ) : null}
          {loadState !== "loading" && (!payload || payload.rows.length === 0) ? (
            <div className="border-t border-[#eef1f6] p-6 text-center text-sm text-[#8b92a1]">暂无已入库画像。</div>
          ) : null}
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-xs text-[#7b8190]">
          <span>
            显示 {startRow.toLocaleString("zh-CN")} - {endRow.toLocaleString("zh-CN")} / {total.toLocaleString("zh-CN")}
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              disabled={!hasPrev}
              onClick={() => setOffset(Math.max(0, offset - pageSize))}
              className="inline-flex h-9 items-center gap-1 rounded-lg border border-[#e8ecf3] bg-white px-3 font-medium text-[#596070] disabled:cursor-not-allowed disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
              上一页
            </button>
            <button
              type="button"
              disabled={!hasNext}
              onClick={() => setOffset(offset + pageSize)}
              className="inline-flex h-9 items-center gap-1 rounded-lg border border-[#e8ecf3] bg-white px-3 font-medium text-[#596070] disabled:cursor-not-allowed disabled:opacity-40"
            >
              下一页
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
