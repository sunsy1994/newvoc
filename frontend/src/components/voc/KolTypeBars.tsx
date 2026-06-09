"use client";

import { useState } from "react";

import type { KolTypeDistributionItem, UserProfileDistributionItem } from "@/types/vocMarket";

type KolTypeBarsProps = {
  data: KolTypeDistributionItem[];
  userProfiles: UserProfileDistributionItem[];
};

type TabKey = "kol" | "user";

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
      <div className="flex h-64 items-center justify-center rounded-2xl bg-[#f7f9fc] text-sm text-[#8b92a1]">
        {emptyText}
      </div>
    );
  }

  const max = Math.max(...rows.map((item) => item.value), 1);

  return (
    <div className="space-y-4 rounded-2xl bg-[#f7f9fc] p-4">
      {rows.slice(0, 8).map((item) => (
        <div key={item.label} title={`${item.label}: ${item.value.toLocaleString("zh-CN")}${valueSuffix}`}>
          <div className="mb-2 flex justify-between gap-3 text-xs text-[#6f7685]">
            <span className="truncate">{item.label}</span>
            <span>{item.value.toLocaleString("zh-CN")}{valueSuffix}</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-white">
            <div className="h-full rounded-full bg-[#887CFD] transition-[width]" style={{ width: `${(item.value / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

export function KolTypeBars({ data, userProfiles }: KolTypeBarsProps) {
  const [activeTab, setActiveTab] = useState<TabKey>("kol");
  const kolRows = data.map((item) => ({ label: item.kol_main_type, value: item.kol_count }));
  const userRows = userProfiles.map((item) => ({ label: item.main_label, value: item.user_cnt }));

  return (
    <div>
      <div className="mb-3 inline-flex rounded-lg bg-[#f0f2f7] p-1 text-xs font-medium text-[#6f7685]">
        <button
          type="button"
          onClick={() => setActiveTab("kol")}
          className={`rounded-md px-3 py-1.5 transition ${activeTab === "kol" ? "bg-white text-[#5347CE] shadow-sm" : ""}`}
        >
          KOL类型
        </button>
        <button
          type="button"
          onClick={() => setActiveTab("user")}
          className={`rounded-md px-3 py-1.5 transition ${activeTab === "user" ? "bg-white text-[#5347CE] shadow-sm" : ""}`}
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
