"use client";

import { useState } from "react";
import { Gauge, HelpCircle, MapPinned, MousePointerClick, RadioTower } from "lucide-react";

import type { ChannelDistributionItem, HotPostItem, PlatformStory } from "@/types/vocMarket";

import { ChannelStackedBars } from "./ChannelStackedBars";
import { EvidenceRankList, type EvidenceRankItem } from "./EvidenceRankList";
import { HotPostList } from "./HotPostList";

type PlatformStoryCardProps = {
  story?: PlatformStory;
  channels: ChannelDistributionItem[];
  eventId: string;
  hotPosts: HotPostItem[];
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

type EvidenceTab = "efficiency" | "hot";

function PlatformMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-card)] px-4 py-3 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
      <p className="text-[11px] font-medium text-[var(--theme-muted)]">{label}</p>
      <strong className="mt-2 block text-lg font-semibold text-[var(--theme-title)]">{value}</strong>
    </div>
  );
}

function RuleTooltip() {
  return (
    <div className="group relative">
      <button
        type="button"
        aria-label="查看平台效率计算规则"
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-card)] text-[var(--theme-muted)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] transition hover:text-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-selected-bg)]"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
      <div className="pointer-events-none absolute right-0 top-10 z-20 hidden w-80 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-card)] p-4 text-xs leading-5 text-[var(--theme-body)] shadow-[0_18px_48px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
        <p className="mb-2 font-semibold text-[var(--theme-title)]">计算规则</p>
        <p>平台声量 = 平台主贴数 + 平台评论数。</p>
        <p>声量贡献 = 平台声量 / 全部平台声量。</p>
        <p>单帖互动 = 平台总互动量 / 平台主贴数。</p>
        <p>有效评论率 = 车相关评论数 / 已打标评论数。</p>
        <p>中/强购买信号率 = 中/强购买信号评论数 / 已打标评论数。</p>
        <p>核心平台：按声量优先，其次按互动量选择。</p>
        <p className="mt-2 text-[var(--theme-muted)]">该结论为规则计算结果，不是 AI 生成。</p>
      </div>
    </div>
  );
}

function PlatformEfficiencyList({ story }: { story?: PlatformStory }) {
  const efficiencyItems: EvidenceRankItem[] = (story?.platform_efficiency ?? []).map((item) => ({
    id: item.platform,
    title: item.platform,
    meta: `单帖 ${formatNumber(item.engagement_per_content)} · 有效 ${formatPercent(item.effective_comment_rate)} · 信号 ${formatPercent(item.purchase_signal_rate)}`,
    value: formatPercent(item.volume_rate),
    valueLabel: "声量",
  }));

  return <EvidenceRankList items={efficiencyItems} emptyText="暂无平台效率数据" />;
}

export function PlatformStoryCard({ story, channels, eventId, hotPosts }: PlatformStoryCardProps) {
  const [activeEvidence, setActiveEvidence] = useState<EvidenceTab>("efficiency");
  const summary = story?.summary;
  const conclusion = summary?.rule_based_conclusion ?? "暂无平台分布数据，暂时无法判断渠道选择。";

  return (
    <article className="voc-story-card rounded-[20px] border border-[var(--theme-border)] bg-[var(--theme-card)] p-5 shadow-[0_12px_32px_rgba(31,43,39,0.045)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Platform Efficiency Story</p>
          <h2 className="mt-1 text-base font-semibold text-[var(--theme-title)]">平台效率与渠道选择</h2>
        </div>
        <div className="flex items-center gap-2">
          <RuleTooltip />
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-chip)] px-3 py-1.5 text-xs font-medium text-[var(--theme-primary)]">
            <MapPinned className="h-3.5 w-3.5" />
            {summary?.core_platform ?? "暂无数据"}
          </span>
        </div>
      </div>

      <div className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4 text-sm leading-6 text-[var(--theme-body)]">
        {conclusion}
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <PlatformMetric label="核心平台" value={summary?.core_platform ?? "暂无"} />
        <PlatformMetric label="声量贡献" value={formatPercent(summary?.core_platform_volume_rate)} />
        <PlatformMetric label="单帖互动" value={formatNumber(summary?.core_platform_engagement_per_content)} />
        <PlatformMetric label="购买信号" value={formatPercent(summary?.core_platform_purchase_signal_rate)} />
      </div>

      <div className="mt-5 grid items-start gap-4 xl:grid-cols-[1.55fr_0.85fr]">
        <div className="min-w-0">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--theme-title)]">
            <MousePointerClick className="h-4 w-4 text-[var(--voc-chart-4)]" />
            平台声量分布
          </div>
          <ChannelStackedBars data={channels} maxVisible={10} />
        </div>

        <div className="min-w-0">
          <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-[var(--theme-title)]">
              {activeEvidence === "efficiency" ? <Gauge className="h-4 w-4 text-[var(--theme-primary)]" /> : <RadioTower className="h-4 w-4 text-[var(--theme-primary)]" />}
              选择证据
            </div>
            <div className="inline-flex rounded-lg bg-[var(--theme-soft-panel)] p-1 text-xs font-medium text-[var(--theme-body)]">
              <button
                type="button"
                onClick={() => setActiveEvidence("efficiency")}
                className={`rounded-md px-3 py-1.5 transition ${activeEvidence === "efficiency" ? "bg-[var(--theme-card)] text-[var(--theme-primary)] shadow-sm" : ""}`}
              >
                效率排行
              </button>
              <button
                type="button"
                onClick={() => setActiveEvidence("hot")}
                className={`rounded-md px-3 py-1.5 transition ${activeEvidence === "hot" ? "bg-[var(--theme-card)] text-[var(--theme-primary)] shadow-sm" : ""}`}
              >
                热门证据
              </button>
            </div>
          </div>
          <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-4">
            {activeEvidence === "efficiency" ? <PlatformEfficiencyList story={story} /> : <HotPostList eventId={eventId} posts={hotPosts} />}
          </div>
        </div>
      </div>
    </article>
  );
}
