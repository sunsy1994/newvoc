"use client";

import { useMemo, useState } from "react";

import type { VolumeTrendPoint } from "@/types/vocMarket";

type VolumeTrendChartProps = {
  data: VolumeTrendPoint[];
};

type TrendKey = "total_volume" | "content_count" | "comment_count";

const series: Array<{ key: TrendKey; label: string; color: string; width: number }> = [
  { key: "total_volume", label: "总声量", color: "var(--theme-ink)", width: 3 },
  { key: "content_count", label: "主贴声量", color: "var(--voc-chart-5)", width: 2.5 },
  { key: "comment_count", label: "评论声量", color: "var(--voc-chart-1)", width: 2.5 },
];

const chart = { left: 34, right: 520, top: 24, bottom: 156 };

function formatDate(date: string) {
  const [, month, day] = date.split("-");
  return month && day ? `${month}-${day}` : date;
}

function pointFor(data: VolumeTrendPoint[], index: number, key: TrendKey, max: number) {
  const x = chart.left + (index / Math.max(data.length - 1, 1)) * (chart.right - chart.left);
  const y = chart.bottom - ((data[index][key] || 0) / max) * (chart.bottom - chart.top);
  return { x, y };
}

function buildPoints(data: VolumeTrendPoint[], key: TrendKey, max: number) {
  if (data.length === 1) {
    const y = pointFor(data, 0, key, max).y;
    return `${chart.left},${y} ${chart.right},${y}`;
  }
  return data.map((_, index) => {
    const point = pointFor(data, index, key, max);
    return `${point.x},${point.y}`;
  }).join(" ");
}

export function VolumeTrendChart({ data }: VolumeTrendChartProps) {
  const [activeKeys, setActiveKeys] = useState<TrendKey[]>(["total_volume", "content_count", "comment_count"]);

  const max = useMemo(() => {
    const values = data.flatMap((item) => activeKeys.map((key) => item[key] || 0));
    return Math.max(...values, 1);
  }, [activeKeys, data]);

  if (!data.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-2xl bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
        缺少发布时间，暂时无法展示声量趋势
      </div>
    );
  }

  function toggleSeries(key: TrendKey) {
    setActiveKeys((current) => (current.includes(key) ? current.filter((item) => item !== key) : [...current, key]));
  }

  return (
    <div className="overflow-hidden rounded-2xl bg-[var(--theme-soft-panel)] p-4">
      <svg viewBox="0 0 540 210" className="h-72 w-full" role="img" aria-label="声量趋势折线图">
        {[24, 68, 112, 156].map((y) => (
          <line key={y} x1="34" y1={y} x2="520" y2={y} stroke="#e8ecf3" strokeWidth="1" />
        ))}
        <line x1="34" y1="156" x2="520" y2="156" stroke="#d9deea" strokeWidth="1" />
        {series.map((item) =>
          activeKeys.includes(item.key) ? (
            <g key={item.key}>
              <polyline
                points={buildPoints(data, item.key, max)}
                fill="none"
                stroke={item.color}
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={item.width}
              />
              {data.map((point, index) => {
                const { x, y } = pointFor(data, index, item.key, max);
                return (
                  <circle key={`${item.key}-${point.date}`} cx={x} cy={y} r="4.5" fill="white" stroke={item.color} strokeWidth="2">
                    <title>{`${point.date}\n${item.label}: ${(point[item.key] || 0).toLocaleString("zh-CN")}`}</title>
                  </circle>
                );
              })}
            </g>
          ) : null,
        )}
        {data.map((item, index) => {
          const x = chart.left + (index / Math.max(data.length - 1, 1)) * (chart.right - chart.left);
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
                active ? "border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-body)]" : "border-transparent bg-transparent text-[var(--theme-muted)]"
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
