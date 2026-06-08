"use client";

import { useMemo, useState } from "react";

import type { VolumeTrendPoint } from "@/types/vocMarket";

type VolumeTrendChartProps = {
  data: VolumeTrendPoint[];
};

type TrendKey = "total_volume" | "content_count" | "comment_count";

const series: Array<{ key: TrendKey; label: string; color: string; width: number }> = [
  { key: "total_volume", label: "总声量", color: "#5347CE", width: 3 },
  { key: "content_count", label: "主贴声量", color: "#4896FE", width: 2.5 },
  { key: "comment_count", label: "评论声量", color: "#16C8C7", width: 2.5 },
];

function formatDate(date: string) {
  const [, month, day] = date.split("-");
  return month && day ? `${month}-${day}` : date;
}

function buildPoints(data: VolumeTrendPoint[], key: TrendKey, max: number) {
  const left = 34;
  const right = 520;
  const top = 24;
  const bottom = 156;
  if (data.length === 1) {
    const y = bottom - ((data[0][key] || 0) / max) * (bottom - top);
    return `${left},${y} ${right},${y}`;
  }
  return data
    .map((item, index) => {
      const x = left + (index / Math.max(data.length - 1, 1)) * (right - left);
      const y = bottom - ((item[key] || 0) / max) * (bottom - top);
      return `${x},${y}`;
    })
    .join(" ");
}

export function VolumeTrendChart({ data }: VolumeTrendChartProps) {
  const [activeKeys, setActiveKeys] = useState<TrendKey[]>(["total_volume", "content_count", "comment_count"]);

  const max = useMemo(() => {
    const values = data.flatMap((item) => activeKeys.map((key) => item[key] || 0));
    return Math.max(...values, 1);
  }, [activeKeys, data]);

  if (!data.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-2xl bg-[#f7f9fc] text-sm text-[#8b92a1]">
        缺少发布时间，暂无法展示声量趋势
      </div>
    );
  }

  function toggleSeries(key: TrendKey) {
    setActiveKeys((current) => (current.includes(key) ? current.filter((item) => item !== key) : [...current, key]));
  }

  return (
    <div className="overflow-hidden rounded-2xl bg-[#f7f9fc] p-4">
      <svg viewBox="0 0 540 210" className="h-72 w-full" role="img" aria-label="声量趋势折线图">
        {[24, 68, 112, 156].map((y) => (
          <line key={y} x1="34" y1={y} x2="520" y2={y} stroke="#e8ecf3" strokeWidth="1" />
        ))}
        <line x1="34" y1="156" x2="520" y2="156" stroke="#d9deea" strokeWidth="1" />
        {series.map((item) =>
          activeKeys.includes(item.key) ? (
            <polyline
              key={item.key}
              points={buildPoints(data, item.key, max)}
              fill="none"
              stroke={item.color}
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={item.width}
            />
          ) : null,
        )}
        {data.map((item, index) => {
          const x = 34 + (index / Math.max(data.length - 1, 1)) * (520 - 34);
          return (
            <g key={item.date}>
              <line x1={x} y1="156" x2={x} y2="161" stroke="#b8bfcc" strokeWidth="1" />
              <text x={x} y="182" textAnchor="middle" className="fill-[#8b92a1] text-[10px]">
                {formatDate(item.date)}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="mt-2 flex flex-wrap gap-2 text-xs">
        {series.map((item) => {
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
