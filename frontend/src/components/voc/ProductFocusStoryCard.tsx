import { Crosshair, HelpCircle, PackageSearch } from "lucide-react";

import type { ProductFocusAspectItem, ProductFocusStory } from "@/types/vocMarket";

type ProductFocusStoryCardProps = {
  story?: ProductFocusStory;
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

function ProductMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-[var(--theme-border)] bg-white px-4 py-3 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
      <p className="text-[11px] font-medium text-[var(--theme-muted)]">{label}</p>
      <strong className="mt-2 block text-lg font-semibold text-[var(--theme-ink)]">{value}</strong>
    </div>
  );
}

function RuleTooltip() {
  return (
    <div className="group relative">
      <button
        type="button"
        aria-label="查看产品关注点计算规则"
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-muted)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] transition hover:text-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-selected-bg)]"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
      <div className="pointer-events-none absolute right-0 top-10 z-20 hidden w-80 rounded-2xl border border-[var(--theme-border)] bg-white p-4 text-xs leading-5 text-[var(--theme-body)] shadow-[0_18px_48px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
        <p className="mb-2 font-semibold text-[var(--theme-ink)]">计算规则</p>
        <p>产品点来自 comment_label_json.mentioned_aspect，可为数组或单个文本。</p>
        <p>提及率 = 该产品点提及次数 / 全部产品点提及次数。</p>
        <p>正向率、负向率来自 comment_sentiment。</p>
        <p>购买信号率 = purchase_signal 为“中/强”的评论数 / 该产品点提及次数。</p>
        <p className="mt-2 text-[var(--theme-muted)]">该结论为规则计算结果，不是 AI 生成。</p>
      </div>
    </div>
  );
}

function ProductQuadrantChart({ aspects }: { aspects: ProductFocusAspectItem[] }) {
  const positiveTone = "var(--voc-chart-3)";
  const negativeTone = "var(--voc-chart-6)";

  if (!aspects.length) {
    return (
      <div className="flex h-80 items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-white text-sm text-[var(--theme-muted)]">
        暂无产品关注点数据
      </div>
    );
  }

  const maxCount = Math.max(...aspects.map((item) => item.comment_count), 1);
  const maxMentionRate = Math.max(...aspects.map((item) => item.mention_rate), 1);
  const visibleAspects = aspects.slice(0, 12);

  return (
    <div className="rounded-2xl bg-[var(--theme-soft-panel)] p-4">
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
          <Crosshair className="h-4 w-4 text-[var(--voc-chart-3)]" />
          产品感知四象限
        </div>
        <div className="flex flex-wrap gap-2 text-[11px] text-[var(--theme-muted)]">
          <span className="rounded-lg bg-white px-2 py-1">X轴：相对提及率</span>
          <span className="rounded-lg bg-white px-2 py-1">Y轴：净正向感知</span>
          <span className="rounded-lg bg-white px-2 py-1">点大小：提及次数</span>
        </div>
      </div>

      <div className="relative h-[420px] overflow-hidden rounded-2xl border border-[var(--theme-border)] bg-white">
        <div className="absolute inset-y-8 left-1/2 w-px bg-[var(--theme-border)]" />
        <div className="absolute inset-x-8 top-1/2 h-px bg-[var(--theme-border)]" />
        <div className="absolute right-4 top-4 rounded-lg bg-[var(--theme-chip)] px-2 py-1 text-[11px] font-medium text-[var(--voc-chart-3)]">高提及 · 正向强</div>
        <div className="absolute bottom-4 right-4 rounded-lg bg-[var(--sales-chip-strong)] px-2 py-1 text-[11px] font-medium text-[var(--voc-chart-6)]">高提及 · 负向强</div>
        <div className="absolute left-4 top-4 rounded-lg bg-[var(--theme-selected-bg)] px-2 py-1 text-[11px] font-medium text-[var(--theme-primary)]">低提及 · 潜在亮点</div>
        <div className="absolute bottom-4 left-4 rounded-lg bg-[var(--theme-soft-panel)] px-2 py-1 text-[11px] font-medium text-[var(--theme-muted)]">低提及 · 先观察</div>

        {visibleAspects.map((item) => {
          const x = Math.min(92, Math.max(8, (item.mention_rate / maxMentionRate) * 84 + 8));
          const netPositive = item.positive_rate - item.negative_rate;
          const y = Math.min(90, Math.max(10, 50 - netPositive / 2));
          const size = Math.max(34, Math.min(72, 30 + (item.comment_count / maxCount) * 42));
          const tone = netPositive >= 0 ? positiveTone : negativeTone;
          const tooltip = `${item.aspect}\n提及率: ${formatPercent(item.mention_rate)}\n正向率: ${formatPercent(item.positive_rate)}\n负向率: ${formatPercent(item.negative_rate)}\n购买信号率: ${formatPercent(item.purchase_signal_rate)}\n提及次数: ${formatNumber(item.comment_count)}`;
          return (
            <div
              key={item.aspect}
              className="group absolute -translate-x-1/2 -translate-y-1/2"
              style={{ left: `${x}%`, top: `${y}%` }}
              title={tooltip}
            >
              <div
                className="flex items-center justify-center rounded-full border-2 bg-white text-center text-[11px] font-semibold leading-3 text-[var(--theme-ink)] shadow-[0_10px_24px_rgba(26,32,44,0.10)] transition group-hover:scale-110"
                style={{ width: `${size}px`, height: `${size}px`, borderColor: tone }}
              >
                <span className="max-w-[58px] truncate px-1">{item.aspect}</span>
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-xs text-[var(--theme-muted)]">
        <span className="rounded-lg bg-white px-2.5 py-1">悬浮产品点查看提及率、正向率、负向率和购买信号率</span>
        {aspects.length > visibleAspects.length ? (
          <span className="rounded-lg bg-white px-2.5 py-1">展示前 {visibleAspects.length} / 共 {aspects.length} 个产品点</span>
        ) : null}
      </div>
    </div>
  );
}

export function ProductFocusStoryCard({ story }: ProductFocusStoryCardProps) {
  const summary = story?.summary;
  const aspects = story?.aspects ?? [];
  const conclusion =
    summary?.rule_based_conclusion ??
    "暂未从 comment_label_json 中解析到产品关注点。补充 mentioned_aspect 后，这里会展示用户记住了哪些产品点。";

  return (
    <article className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Product Focus Story</p>
          <h2 className="mt-1 text-base font-semibold text-[var(--theme-ink)]">产品关注点总览</h2>
        </div>
        <div className="flex items-center gap-2">
          <RuleTooltip />
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-selected-bg)] px-3 py-1.5 text-xs font-medium text-[var(--theme-primary)]">
            <PackageSearch className="h-3.5 w-3.5" />
            {summary?.top_aspect ?? "暂无产品点"}
          </span>
        </div>
      </div>

      <div className="rounded-2xl bg-gradient-to-r from-[var(--theme-soft-panel)] to-[var(--theme-chip)] p-4 text-sm leading-6 text-[var(--theme-body)]">
        {conclusion}
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-4">
        <ProductMetric label="产品点数量" value={`${formatNumber(summary?.aspect_count)} 个`} />
        <ProductMetric label="产品点提及" value={`${formatNumber(summary?.total_mentions)} 次`} />
        <ProductMetric label="最高正向点" value={summary?.top_positive_aspect ?? "暂无"} />
        <ProductMetric label="最高负向点" value={summary?.top_negative_aspect ?? "暂无"} />
      </div>

      <div className="mt-5">
        <ProductQuadrantChart aspects={aspects} />
      </div>
    </article>
  );
}


