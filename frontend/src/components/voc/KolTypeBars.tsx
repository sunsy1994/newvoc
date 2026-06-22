"use client";

import { useState } from "react";

import type { KolTypeDistributionItem, UserProfileDistributionItem } from "@/types/vocMarket";

type KolTypeBarsProps = {
  data: KolTypeDistributionItem[];
  userProfiles: UserProfileDistributionItem[];
};

type TabKey = "kol" | "user";

const MAX_VISIBLE_DISTRIBUTION_ITEMS = 5;

function buildCompactRows(rows: Array<{ label: string; value: number }>, otherLabel: string) {
  const sortedRows = rows
    .filter((item) => item.label && Number(item.value ?? 0) > 0)
    .sort((left, right) => right.value - left.value);
  const visibleRows = sortedRows.slice(0, MAX_VISIBLE_DISTRIBUTION_ITEMS);
  const otherRows = sortedRows.slice(MAX_VISIBLE_DISTRIBUTION_ITEMS);
  const otherValue = otherRows.reduce((sum, item) => sum + item.value, 0);

  if (!otherRows.length) return visibleRows;
  return [...visibleRows, { label: otherLabel, value: otherValue }];
}

function DistributionBars({
  rows,
  emptyText,
  valueSuffix,
}: {
  rows: Array<{ label: string; value: number }>;
  emptyText: string;
  valueSuffix: string;
}) {
  if (!rows.length) {
    return (
      <div className="flex h-64 items-center justify-center rounded-2xl bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
        {emptyText}
      </div>
    );
  }

  const max = Math.max(...rows.map((item) => item.value), 1);

  return (
    <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-4">
      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        {rows.map((item) => (
          <div key={item.label} title={`${item.label}: ${item.value.toLocaleString("zh-CN")}${valueSuffix}`}>
            <div className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-3 py-2 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
              <div className="mb-1.5 flex justify-between gap-3 text-xs text-[var(--theme-body)]">
                <span className="truncate font-medium">{item.label}</span>
                <span className="shrink-0 text-[var(--theme-muted)]">{item.value.toLocaleString("zh-CN")}{valueSuffix}</span>
              </div>
              <div className="h-1.5 overflow-hidden rounded-full bg-[var(--theme-soft-panel)]">
                <div className="h-full rounded-full bg-[var(--voc-chart-4)] transition-[width]" style={{ width: `${(item.value / max) * 100}%` }} />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function KolTypeBars({ data, userProfiles }: KolTypeBarsProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("kol");
  const kolRows = buildCompactRows(
    data.map((item) => ({ label: item.kol_main_type, value: item.kol_count })),
    "其他类型",
  );
  const userRows = buildCompactRows(
    userProfiles.map((item) => ({ label: item.main_label, value: item.user_cnt })),
    "其他画像",
  );

  return (
    <div>
      <div className="mb-3 inline-flex rounded-lg bg-[var(--theme-soft-panel)] p-1 text-xs font-medium text-[var(--theme-body)]">
        <button
          type="button"
          onClick={() => setActiveTab("kol")}
          className={`rounded-md px-3 py-1.5 transition ${activeTab === "kol" ? "bg-[var(--theme-white)] text-[var(--theme-primary)] shadow-sm" : ""}`}
        >
          KOL类型
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("user")}
          className={`rounded-md px-3 py-1.5 transition ${activeTab === "user" ? "bg-[var(--theme-white)] text-[var(--theme-primary)] shadow-sm" : ""}`}
        >
          用户画像
        </button>
      </div>
      {activeTab === "kol" ? (
        <DistributionBars rows={kolRows} emptyText="尚未维护KOL画像" valueSuffix="位" />
      ) : (
        <DistributionBars rows={userRows} emptyText="尚未维护评论用户画像" valueSuffix="人" />
      )}
    </div>
  );
}
