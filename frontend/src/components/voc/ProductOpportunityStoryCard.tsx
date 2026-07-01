"use client";

import type { ReactNode } from "react";
import { useState } from "react";
import { AlertTriangle, HelpCircle, Megaphone, MessageSquareText, Sparkles, Target } from "lucide-react";

import type { ProductEvidenceComment, ProductOpportunityItem, ProductOpportunityStory } from "@/types/vocMarket";

type ProductOpportunityStoryCardProps = {
  opportunity?: ProductOpportunityStory;
};

type OpportunityFilter = "all" | "surprise_points" | "pain_points" | "conversion_points";

type RankedOpportunity = ProductOpportunityItem & {
  type_label: "惊喜点" | "吐槽点" | "转化点";
  accent: string;
  softBg: string;
  rateLabel: string;
  rateValue: number;
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

const filterOptions: Array<{ key: OpportunityFilter; label: string }> = [
  { key: "all", label: "全部" },
  { key: "surprise_points", label: "惊喜点" },
  { key: "pain_points", label: "吐槽点" },
  { key: "conversion_points", label: "转化点" },
];

function RuleTooltip() {
  return (
    <div className="group relative">
      <button
        type="button"
        aria-label="查看产品机会优先级计算规则"
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-muted)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] transition hover:text-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-selected-bg)]"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
      <div className="pointer-events-none absolute right-0 top-10 z-20 hidden w-80 rounded-2xl border border-[var(--theme-border)] bg-white p-4 text-xs leading-5 text-[var(--theme-body)] shadow-[0_18px_48px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
        <p className="mb-2 font-semibold text-[var(--theme-ink)]">机会分数计算公式</p>
        <p>惊喜点机会分数 = 提及率 × 正向率。</p>
        <p>吐槽点机会分数 = 提及率 × 负向率。</p>
        <p>转化点机会分数 = 提及率 × 中/强购买信号率。</p>
        <p className="mt-2 text-[var(--theme-muted)]">该结论为规则计算结果，不是 AI 生成。</p>
      </div>
    </div>
  );
}

function decorateItem(
  item: ProductOpportunityItem,
  type_label: RankedOpportunity["type_label"],
  accent: string,
  softBg: string,
  rateLabel: string,
  rateValue: number,
): RankedOpportunity {
  return { ...item, type_label, accent, softBg, rateLabel, rateValue };
}

function decorateOpportunities(opportunity?: ProductOpportunityStory): RankedOpportunity[] {
  return [
    ...(opportunity?.surprise_points ?? []).map((item) =>
      decorateItem(item, "惊喜点", "var(--voc-chart-3)", "var(--theme-chip)", "正向率", item.positive_rate),
    ),
    ...(opportunity?.pain_points ?? []).map((item) =>
      decorateItem(item, "吐槽点", "#EF4444", "#FFF1EF", "负向率", item.negative_rate),
    ),
    ...(opportunity?.conversion_points ?? []).map((item) =>
      decorateItem(item, "转化点", "var(--theme-primary)", "var(--theme-selected-bg)", "购买信号率", item.purchase_signal_rate),
    ),
  ];
}

function buildRankedBentoItems(opportunity?: ProductOpportunityStory): RankedOpportunity[] {
  const surpriseTop = opportunity?.surprise_points?.[0]
    ? decorateItem(opportunity.surprise_points[0], "惊喜点", "var(--voc-chart-3)", "var(--theme-chip)", "正向率", opportunity.surprise_points[0].positive_rate)
    : null;
  const painTop = opportunity?.pain_points?.[0]
    ? decorateItem(opportunity.pain_points[0], "吐槽点", "#EF4444", "#FFF1EF", "负向率", opportunity.pain_points[0].negative_rate)
    : null;
  const conversionTop = opportunity?.conversion_points?.[0]
    ? decorateItem(
        opportunity.conversion_points[0],
        "转化点",
        "var(--theme-primary)",
        "var(--theme-selected-bg)",
        "购买信号率",
        opportunity.conversion_points[0].purchase_signal_rate,
      )
    : null;

  const required = [surpriseTop, painTop, conversionTop].filter(Boolean) as RankedOpportunity[];
  const requiredKeys = new Set(required.map((item) => `${item.type_label}:${item.aspect}`));
  const rest = decorateOpportunities(opportunity)
    .filter((item) => !requiredKeys.has(`${item.type_label}:${item.aspect}`))
    .sort((a, b) => b.opportunity_score - a.opportunity_score || b.comment_count - a.comment_count);

  return [...required, ...rest].slice(0, 5);
}

function buildFilteredBentoItems(filter: OpportunityFilter, opportunity?: ProductOpportunityStory): RankedOpportunity[] {
  if (filter === "all") {
    return buildRankedBentoItems(opportunity);
  }

  const groupConfig = {
    surprise_points: {
      items: opportunity?.surprise_points ?? [],
      typeLabel: "惊喜点" as const,
      accent: "var(--voc-chart-3)",
      softBg: "var(--theme-chip)",
      rateLabel: "正向率",
      rateValue: (item: ProductOpportunityItem) => item.positive_rate,
    },
    pain_points: {
      items: opportunity?.pain_points ?? [],
      typeLabel: "吐槽点" as const,
      accent: "#EF4444",
      softBg: "#FFF1EF",
      rateLabel: "负向率",
      rateValue: (item: ProductOpportunityItem) => item.negative_rate,
    },
    conversion_points: {
      items: opportunity?.conversion_points ?? [],
      typeLabel: "转化点" as const,
      accent: "var(--theme-primary)",
      softBg: "var(--theme-selected-bg)",
      rateLabel: "购买信号率",
      rateValue: (item: ProductOpportunityItem) => item.purchase_signal_rate,
    },
  }[filter];

  return groupConfig.items
    .map((item) =>
      decorateItem(
        item,
        groupConfig.typeLabel,
        groupConfig.accent,
        groupConfig.softBg,
        groupConfig.rateLabel,
        groupConfig.rateValue(item),
      ),
    )
    .sort((a, b) => b.opportunity_score - a.opportunity_score || b.comment_count - a.comment_count)
    .slice(0, 5);
}

function StrategyCard({
  label,
  aspect,
  description,
  icon,
  accent,
  softBg,
}: {
  label: string;
  aspect?: string | null;
  description: string;
  icon: ReactNode;
  accent: string;
  softBg: string;
}) {
  return (
    <div className="rounded-2xl border border-[var(--theme-border)] bg-white p-4 shadow-[0_10px_24px_rgba(26,32,44,0.04)]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">{label}</p>
          <h3 className="mt-2 text-lg font-semibold text-[var(--theme-ink)]">{aspect || "暂无"}</h3>
        </div>
        <span className="flex h-10 w-10 items-center justify-center rounded-2xl" style={{ backgroundColor: softBg, color: accent }}>
          {icon}
        </span>
      </div>
      <p className="mt-3 text-xs leading-5 text-[var(--theme-muted)]">{description}</p>
    </div>
  );
}

function MetricPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2">
      <p className="text-[11px] text-[var(--theme-muted)]">{label}</p>
      <strong className="mt-1 block text-sm text-[var(--theme-ink)]">{value}</strong>
    </div>
  );
}

function AutoScrollComments({ comments }: { comments?: ProductEvidenceComment[] }) {
  const evidence = comments?.filter((comment) => comment.comment_text)?.slice(0, 6) ?? [];
  if (!evidence.length) {
    return (
      <div className="flex h-32 items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)]/70 text-xs text-[var(--theme-muted)]">
        暂无可展示的评论证据
      </div>
    );
  }

  const loopComments = evidence.length > 2 ? [...evidence, ...evidence] : evidence;
  return (
    <div className="relative h-36 overflow-hidden rounded-2xl border border-white/80 bg-[var(--theme-white)]/70">
      <div className="pointer-events-none absolute inset-x-0 top-0 z-10 h-8 bg-gradient-to-b from-white to-transparent" />
      <div className="pointer-events-none absolute inset-x-0 bottom-0 z-10 h-8 bg-gradient-to-t from-white to-transparent" />
      <div className={evidence.length > 2 ? "comment-evidence-track space-y-2 p-3" : "space-y-2 p-3"}>
        {loopComments.map((comment, index) => (
          <div key={`${comment.comment_id ?? comment.comment_text}-${index}`} className="rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2">
            <p className="line-clamp-2 text-xs leading-5 text-[var(--theme-body)]">{comment.comment_text}</p>
            <div className="mt-1 flex items-center justify-between gap-2 text-[11px] text-[var(--theme-muted)]">
              <span className="truncate">{comment.comment_author_name || "匿名用户"}</span>
              <span>{formatNumber(comment.interaction_cnt)} 互动</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function OpportunityBentoCard({ item, rank }: { item: RankedOpportunity; rank: number }) {
  const sizeClass =
    rank === 1
      ? "top-1-card md:col-span-7 md:row-span-2 min-h-[330px]"
      : rank === 2
        ? "top-2-card md:col-span-5 min-h-[188px]"
        : rank === 3
          ? "top-3-card md:col-span-5 min-h-[188px]"
          : rank === 4
            ? "top-4-card md:col-span-6 min-h-[150px]"
            : "top-5-card md:col-span-6 min-h-[150px]";
  const isHero = rank === 1;

  return (
    <article
      className={`${sizeClass} group relative overflow-hidden rounded-[22px] border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_14px_34px_rgba(26,32,44,0.05)] transition hover:-translate-y-0.5 hover:shadow-[0_18px_44px_rgba(26,32,44,0.09)]`}
    >
      <div
        className="absolute -right-10 -top-14 h-36 w-36 rounded-full opacity-20 blur-2xl"
        style={{ backgroundColor: item.accent }}
      />
      <div className="relative flex h-full flex-col gap-5">
        <div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="rounded-full bg-[var(--theme-ink)] px-3 py-1 text-xs font-semibold text-white">TOP {rank}</span>
            <span className="rounded-full px-3 py-1 text-xs font-semibold" style={{ backgroundColor: item.softBg, color: item.accent }}>
              {item.type_label}
            </span>
          </div>

          <h3 className={`${isHero ? "mt-7 text-3xl" : "mt-4 text-xl"} font-semibold tracking-tight text-[var(--theme-ink)]`}>
            {item.aspect}
          </h3>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs md:grid-cols-4">
          <MetricPill label="机会分数" value={formatNumber(item.opportunity_score)} />
          <MetricPill label="提及率" value={formatPercent(item.mention_rate)} />
          <MetricPill label={item.rateLabel} value={formatPercent(item.rateValue)} />
          <MetricPill label="评论量" value={formatNumber(item.comment_count)} />
        </div>

        {isHero ? (
          <div className="mt-auto">
            <div className="mb-2 flex items-center gap-2 text-xs font-semibold text-[var(--theme-ink)]">
              <Sparkles className="h-3.5 w-3.5" style={{ color: item.accent }} />
              评论证据
            </div>
            <AutoScrollComments comments={item.evidence_comments} />
          </div>
        ) : null}
      </div>
    </article>
  );
}

export function ProductOpportunityStoryCard({ opportunity }: ProductOpportunityStoryCardProps) {
  const [activeFilter, setActiveFilter] = useState<OpportunityFilter>("all");
  const ranked = buildFilteredBentoItems(activeFilter, opportunity);
  const conclusion =
    opportunity?.summary.rule_based_conclusion ??
    "暂未形成稳定的产品机会优先级。补充评论标签后，可识别惊喜点、吐槽点和转化点。";

  return (
    <section className="rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_12px_32px_rgba(31,43,39,0.045)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Product Opportunity Story</p>
          <h2 className="mt-1 text-xl font-semibold tracking-tight text-[var(--theme-ink)]">产品机会优先级</h2>
        </div>
        <RuleTooltip />
      </div>

      <div className="rounded-[18px] border border-[var(--theme-track)] bg-[var(--theme-soft-panel)] px-4 py-3.5 text-sm leading-6 text-[var(--theme-body)]">
        {conclusion}
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        <StrategyCard
          label="放大传播"
          aspect={opportunity?.summary.surprise_point}
          description="把用户已经自然认可的产品点，前置到传播标题、素材切片和KOL话术里。"
          icon={<Megaphone className="h-5 w-5" />}
          accent="var(--voc-chart-3)"
          softBg="var(--theme-chip)"
        />
        <StrategyCard
          label="修复异议"
          aspect={opportunity?.summary.pain_point}
          description="把负向集中点整理成解释口径，帮助产品、销售和传播统一回应。"
          icon={<AlertTriangle className="h-5 w-5" />}
          accent="#EF4444"
          softBg="#FFF1EF"
        />
        <StrategyCard
          label="转化话术"
          aspect={opportunity?.summary.conversion_point}
          description="把带来中/强购买信号的产品点，沉淀为到店、询价和外呼承接话术。"
          icon={<MessageSquareText className="h-5 w-5" />}
          accent="var(--theme-primary)"
          softBg="var(--theme-selected-bg)"
        />
      </div>

      <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">机会卡片筛选</p>
          <p className="mt-1 text-xs text-[var(--theme-muted)]">默认展示三类代表项，切换后查看单类 Top5。</p>
        </div>
        <div className="inline-flex rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-1 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
          {filterOptions.map((option) => {
            const isActive = option.key === activeFilter;
            return (
              <button
                key={option.key}
                type="button"
                onClick={() => setActiveFilter(option.key)}
                className={`rounded-xl px-3 py-1.5 text-xs font-semibold transition ${
                  isActive ? "bg-white text-[var(--theme-ink)] shadow-[0_8px_18px_rgba(26,32,44,0.08)]" : "text-[var(--theme-muted)] hover:text-[var(--theme-primary)]"
                }`}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </div>

      {ranked.length ? (
        <div className="mt-5 grid auto-rows-fr gap-3 lg:grid-cols-12">
          {ranked.map((item, index) => (
            <OpportunityBentoCard key={`${item.type_label}-${item.aspect}`} item={item} rank={index + 1} />
          ))}
        </div>
      ) : (
        <div className="mt-5 flex h-56 items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
          暂无产品机会优先级数据
        </div>
      )}

    </section>
  );
}



