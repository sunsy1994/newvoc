"use client";

import { useMemo, useState } from "react";

import type { ChannelDistributionItem } from "@/types/vocMarket";

type ChannelStackedBarsProps = {
  data: ChannelDistributionItem[];
};

type ChannelKey = "content_count" | "comment_count";

const channelSeries: Array<{ key: ChannelKey; label: string; color: string }> = [
  { key: "content_count", label: "主贴", color: "#4896FE" },
  { key: "comment_count", label: "评论", color: "#16C8C7" },
];

export function ChannelStackedBars({ data }: ChannelStackedBarsProps) {
  const [activeKeys, setActiveKeys] = useState<ChannelKey[]>(["content_count", "comment_count"]);
  const rows = data.slice(0, 8);

  const max = useMemo(() => {
    return Math.max(
      ...rows.map((item) => activeKeys.reduce((sum, key) => sum + (item[key] || 0), 0)),
      1,
    );
  }, [activeKeys, rows]);

  if (!data.length) {
    return (
      <div className="flex h-72 items-center justify-center rounded-2xl bg-[#f7f9fc] text-sm text-[#8b92a1]">
        缺少渠道字段，暂时无法展示渠道分布
      </div>
    );
  }

  function toggleSeries(key: ChannelKey) {
    setActiveKeys((current) => (current.includes(key) ? current.filter((item) => item !== key) : [...current, key]));
  }

  return (
    <div className="rounded-2xl bg-[#f7f9fc] p-5">
      <div className="flex h-72 items-end justify-between gap-3 border-b border-[#d9deea] px-2 pb-7">
        {rows.map((item) => {
          const activeContent = activeKeys.includes("content_count") ? item.content_count || 0 : 0;
          const activeComment = activeKeys.includes("comment_count") ? item.comment_count || 0 : 0;
          const contentHeight = (activeContent / max) * 210;
          const commentHeight = (activeComment / max) * 210;
          const activeTotal = activeContent + activeComment;
          const tooltip = `${item.channel}\n主贴: ${(item.content_count || 0).toLocaleString("zh-CN")}\n评论: ${(item.comment_count || 0).toLocaleString("zh-CN")}\n总声量: ${(item.total_volume || 0).toLocaleString("zh-CN")}`;

          return (
            <div key={item.channel} className="relative flex h-full min-w-0 flex-1 flex-col items-center justify-end">
              <div className="mb-2 text-[11px] font-semibold text-[#3a4050]">{activeTotal.toLocaleString("zh-CN")}</div>
              <div className="flex w-full max-w-14 flex-col justify-end overflow-hidden rounded-t-xl bg-white shadow-inner shadow-[#dfe5ef]/60" title={tooltip}>
                <div className="bg-[#16C8C7] transition-[height]" style={{ height: `${commentHeight}px` }} />
                <div className="bg-[#4896FE] transition-[height]" style={{ height: `${contentHeight}px` }} />
              </div>
              <span className="absolute -bottom-6 max-w-20 truncate text-[10px] text-[#8b92a1]" title={item.channel}>{item.channel}</span>
            </div>
          );
        })}
      </div>
      <div className="mt-4 flex flex-wrap gap-2 text-xs">
        {channelSeries.map((item) => {
          const active = activeKeys.includes(item.key);
          return (
            <button
              key={item.key}
              type="button"
              onClick={() => toggleSeries(item.key)}
              className={`inline-flex items-center gap-2 rounded-lg border px-2.5 py-1.5 transition ${
                active ? "border-[#e8ecf3] bg-white text-[#3a4050]" : "border-transparent bg-transparent text-[#a1a7b3]"
              }`}
            >
              <i className="h-2 w-2 rounded-full" style={{ backgroundColor: active ? item.color : "#c7ccd6" }} />
              {item.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
