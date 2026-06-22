import { Activity, CalendarDays, HelpCircle, RadioTower, Waves } from "lucide-react";

import type { VolumeRhythm, VolumeTrendPoint } from "@/types/vocMarket";

import { VolumeTrendChart } from "./VolumeTrendChart";

type VolumeRhythmStoryCardProps = {
  trend: VolumeTrendPoint[];
  rhythm?: VolumeRhythm;
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

function formatDate(date?: string | null) {
  if (!date) return "暂无";
  const [, month, day] = date.split("-");
  return month && day ? `${month}-${day}` : date;
}

function RhythmStat({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-4 py-3 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
      <div className="flex items-center justify-between gap-3">
        <p className="text-[11px] font-medium text-[var(--theme-muted)]">{label}</p>
        <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-[var(--theme-chip)] text-[var(--theme-primary)]">{icon}</span>
      </div>
      <strong className="mt-2 block text-lg font-semibold text-[var(--theme-ink)]">{value}</strong>
    </div>
  );
}

function RuleTooltip() {
  return (
    <div className="group relative">
      <button
        type="button"
        aria-label="查看传播规模与节奏计算规则"
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-muted)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] transition hover:text-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-selected-bg)]"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
      <div className="pointer-events-none absolute right-0 top-10 z-20 hidden w-80 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4 text-xs leading-5 text-[var(--theme-body)] shadow-[0_18px_48px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
        <p className="mb-2 font-semibold text-[var(--theme-ink)]">计算规则</p>
        <p>累计声量 = 每日主贴数 + 评论数求和。</p>
        <p>峰值贡献 = 峰值日声量 / 累计声量。</p>
        <p>集中爆发：峰值贡献 ≥ 50%。</p>
        <p>持续发酵：活跃天数 ≥ 5 且峰值贡献 ≤ 40%。</p>
        <p>二次传播：除主峰外，存在相隔超过 1 天且声量 ≥ 主峰 50% 的日期。</p>
        <p>评论滞后 = 评论峰值日期 - 主贴峰值日期。</p>
        <p className="mt-2 text-[var(--theme-muted)]">该结论为规则计算结果，不是 AI 生成。</p>
      </div>
    </div>
  );
}

export function VolumeRhythmStoryCard({ trend, rhythm }: VolumeRhythmStoryCardProps) {
  const summary = rhythm?.summary;
  const conclusion = summary?.rule_based_conclusion ?? "缺少发布时间趋势数据，暂时无法判断传播规模与节奏。";
  const lagDays = summary?.content_comment_lag_days;
  const lagLabel =
    lagDays === null || lagDays === undefined
      ? "暂无"
      : lagDays > 0
        ? `滞后 ${lagDays} 天`
        : lagDays < 0
          ? `提前 ${Math.abs(lagDays)} 天`
          : "同日";

  return (
    <article className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Volume Rhythm Story</p>
          <h2 className="mt-1 text-base font-semibold text-[var(--theme-ink)]">传播规模与节奏</h2>
        </div>
        <div className="flex items-center gap-2">
          <RuleTooltip />
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-chip)] px-3 py-1.5 text-xs font-medium text-[var(--theme-primary)]">
            <RadioTower className="h-3.5 w-3.5" />
            {summary?.rhythm_type ?? "暂无数据"}
          </span>
        </div>
      </div>

      <div className="rounded-2xl bg-gradient-to-r from-[var(--theme-soft-panel)] to-[var(--theme-selected-bg)] p-4 text-sm leading-6 text-[var(--theme-body)]">
        {conclusion}
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <RhythmStat label="累计声量" value={formatNumber(summary?.total_volume)} icon={<Activity className="h-3.5 w-3.5" />} />
        <RhythmStat label="峰值日期" value={formatDate(summary?.peak_date)} icon={<CalendarDays className="h-3.5 w-3.5" />} />
        <RhythmStat label="峰值贡献" value={formatPercent(summary?.peak_volume_rate)} icon={<Waves className="h-3.5 w-3.5" />} />
        <RhythmStat label="评论滞后" value={lagLabel} icon={<RadioTower className="h-3.5 w-3.5" />} />
      </div>

      <div className="mt-4 flex flex-wrap gap-2 text-xs text-[var(--theme-body)]">
        <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">活跃 {formatNumber(summary?.active_days)} 天</span>
        <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">峰值声量 {formatNumber(summary?.peak_volume)} 条</span>
        <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1">
          {summary?.has_secondary_peak ? `二次传播峰值 ${summary.secondary_peak_count} 个` : "未观察到明显二次传播"}
        </span>
      </div>

      <div className="mt-5">
        <VolumeTrendChart data={trend} />
      </div>
    </article>
  );
}
