"use client";

import { useMemo, useState } from "react";

import type { ChannelDistributionItem } from "@/types/vocMarket";

type ChannelStackedBarsProps = {
  data: ChannelDistributionItem[];
  maxVisible?: number;
};

type ChannelKey = "content_count" | "comment_count";

const channelSeries: Array<{ key: ChannelKey; label: string; color: string }> = [
  { key: "content_count", label: "主贴", color: "var(--voc-chart-5)" },
  { key: "comment_count", label: "评论", color: "var(--voc-chart-1)" },
];

export function ChannelStackedBars({ data, maxVisible = 8 }: ChannelStackedBarsProps) {
  const [activeKeys, setActiveKeys] = useState<ChannelKey[]>(["content_count", "comment_count"]);
  const rows = data.slice(0, maxVisible);

  const max = useMemo(() => {
    return Math.max(
      ...rows.map((item) => activeKeys.reduce((sum, key) => sum + (item[key] || 0), 0)),
      1,
    );
  }, [activeKeys, rows]);

  if (!data.length) {
    return (
      <div className="flex h-72 items-center justify-center rounded-2xl bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
        缺少渠道字段，暂时无法展示渠道分布
      </div>
    );
  }

  function toggleSeries(key: ChannelKey) {
    setActiveKeys((current) => (current.includes(key) ? current.filter((item) => item !== key) : [...current, key]));
  }

  return (
    <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-5">
      <div className="flex h-72 items-end justify-between gap-3 border-b border-[var(--theme-border)] px-2 pb-7">
        {rows.map((item) => {
          const activeContent = activeKeys.includes("content_count") ? item.content_count || 0 : 0;
          const activeComment = activeKeys.includes("comment_count") ? item.comment_count || 0 : 0;
          const contentHeight = (activeContent / max) * 210;
          const commentHeight = (activeComment / max) * 210;
          const activeTotal = activeContent + activeComment;
          const tooltip = `${item.channel}\n主贴: ${(item.content_count || 0).toLocaleString("zh-CN")}\n评论: ${(item.comment_count || 0).toLocaleString("zh-CN")}\n总声量: ${(item.total_volume || 0).toLocaleString("zh-CN")}`;

          return (
            <div key={item.channel} className="relative flex h-full min-w-0 flex-1 flex-col items-center justify-end">
              <div className="mb-2 text-[11px] font-semibold text-[var(--theme-body)]">{activeTotal.toLocaleString("zh-CN")}</div>
              <div className="flex w-full max-w-14 flex-col justify-end overflow-hidden rounded-t-xl bg-[var(--theme-white)] shadow-inner shadow-[#dfe5ef]/60" title={tooltip}>
                <div className="transition-[height]" style={{ height: `${commentHeight}px`, backgroundColor: "var(--voc-chart-1)" }} />
                <div className="transition-[height]" style={{ height: `${contentHeight}px`, backgroundColor: "var(--voc-chart-5)" }} />
              </div>
              <span className="absolute -bottom-6 max-w-20 truncate text-[10px] text-[var(--theme-muted)]" title={item.channel}>{item.channel}</span>
            </div>
          );
        })}
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-2 text-xs">
        {channelSeries.map((item) => {
          const active = activeKeys.includes(item.key);
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => toggleSeries(item.key)}
              className={`inline-flex items-center gap-2 rounded-lg border px-2.5 py-1.5 transition ${
                active ? "border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-body)]" : "border-transparent bg-transparent text-[var(--theme-muted)]"
              }`}
            >
              <i className="h-2 w-2 rounded-full" style={{ backgroundColor: active ? item.color : "#c7ccd6" }} />
              {item.label}
            </button>
          );
        })}
        {data.length > rows.length ? (
          <span className="rounded-lg bg-[var(--theme-white)] px-2.5 py-1.5 text-[var(--theme-muted)] shadow-[0_6px_14px_rgba(26,32,44,0.04)]">
            展示前 {rows.length} / 共 {data.length} 个平台
          </span>
        ) : null}
      </div>
    </div>
  );
}
