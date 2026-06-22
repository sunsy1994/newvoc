"use client";

import { useState } from "react";
import { HelpCircle, RadioTower, Sparkles, UsersRound } from "lucide-react";

import type { SubjectStory, UserProfileDistributionItem } from "@/types/vocMarket";

import { KolTypeBars } from "./KolTypeBars";
import { AuthorDetailDrawer } from "./AuthorDetailDrawer";

type SubjectStoryCardProps = {
  story?: SubjectStory;
  userProfiles: UserProfileDistributionItem[];
};

const MAX_VISIBLE_SUBJECT_ITEMS = 5;

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

function SubjectMetric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-4 py-3 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
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
        aria-label="查看传播主体计算规则"
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-muted)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] transition hover:text-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-selected-bg)]"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
      <div className="pointer-events-none absolute right-0 top-10 z-20 hidden w-80 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-4 text-xs leading-5 text-[var(--theme-body)] shadow-[0_18px_48px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
        <p className="mb-2 font-semibold text-[var(--theme-ink)]">计算规则</p>
        <p>主体类型：作者 is_kol=true 归为 KOL，否则使用作者类型。</p>
        <p>主体贡献：按该主体下主贴的总互动量求和。</p>
        <p>KOL带动：KOL互动贡献占比 ≥ 50%。</p>
        <p>最高KOL类型：按 KOL 类型的总互动量取最大值。</p>
        <p>Top作者：按总互动量、评论数、主贴数排序。</p>
        <p className="mt-2 text-[var(--theme-muted)]">该结论为规则计算结果，不是 AI 生成。</p>
      </div>
    </div>
  );
}

function SubjectDistribution({ story }: { story?: SubjectStory }) {
  const rows = story?.subject_distribution ?? [];
  const max = Math.max(...rows.map((item) => item.count), 1);
  if (!rows.length) {
    return (
      <div className="flex h-52 items-center justify-center rounded-2xl bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
        暂无作者主体数据
      </div>
    );
  }
  return (
    <div className="space-y-3 rounded-2xl bg-[var(--theme-soft-panel)] p-4">
      {rows.slice(0, 6).map((item) => (
        <div key={item.label} title={`${item.label}: ${formatNumber(item.count)}互动，占比 ${formatPercent(item.rate)}`}>
          <div className="mb-1.5 flex items-center justify-between gap-3 text-xs">
            <span className="truncate font-medium text-[var(--theme-body)]">{item.label}</span>
            <span className="shrink-0 text-[var(--theme-muted)]">{formatNumber(item.count)} · {formatPercent(item.rate)}</span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-[var(--theme-white)]">
            <div className="h-full rounded-full bg-[var(--theme-primary)]" style={{ width: `${(item.count / max) * 100}%` }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function TopAuthors({ story, onSelectAuthor }: { story?: SubjectStory; onSelectAuthor: (authorId: string) => void }) {
  const topAuthors = (story?.top_authors ?? []).slice(0, MAX_VISIBLE_SUBJECT_ITEMS);
  if (!topAuthors.length) return null;
  return (
    <div className="mt-4 rounded-2xl bg-[var(--theme-soft-panel)] p-4">
      <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
        <UsersRound className="h-4 w-4 text-[var(--theme-primary)]" />
        贡献作者 Top 5
      </div>
      <div className="space-y-2">
        {topAuthors.map((author, index) => (
          <div key={`${author.author_id ?? author.author_name}-${index}`} className="flex items-center justify-between gap-3 rounded-xl bg-[var(--theme-white)] px-3 py-2 text-xs shadow-sm">
            <div className="min-w-0">
              {author.author_id ? (
                <button
                  type="button"
                  onClick={() => onSelectAuthor(author.author_id as string)}
                  className="block truncate font-medium text-[var(--theme-ink)] transition hover:text-[var(--theme-primary)]"
                >
                  {index + 1}. {author.author_name}
                </button>
              ) : (
                <p className="truncate font-medium text-[var(--theme-ink)]">{index + 1}. {author.author_name}</p>
              )}
              <p className="mt-0.5 text-[var(--theme-muted)]">{author.subject_type} · {formatNumber(author.content_count)} 篇 · {formatNumber(author.comment_count)} 评论</p>
            </div>
            <span className="shrink-0 rounded-lg bg-[var(--theme-chip)] px-2.5 py-1 font-semibold text-[var(--theme-primary)]">
              {formatNumber(author.total_engagement)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SubjectStoryCard({ story, userProfiles }: SubjectStoryCardProps) {
  const [selectedAuthorId, setSelectedAuthorId] = useState<string | null>(null);
  const summary = story?.summary;
  const conclusion = summary?.rule_based_conclusion ?? "暂无作者主体数据，暂时无法判断是谁带动本次传播。";

  return (
    <article className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Subject Drive Story</p>
          <h2 className="mt-1 text-base font-semibold text-[var(--theme-ink)]">传播主体与KOL带动</h2>
        </div>
        <div className="flex items-center gap-2">
          <RuleTooltip />
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-chip)] px-3 py-1.5 text-xs font-medium text-[var(--theme-primary)]">
            <RadioTower className="h-3.5 w-3.5" />
            {summary?.subject_pattern ?? "暂无数据"}
          </span>
        </div>
      </div>

      <div className="rounded-2xl bg-gradient-to-r from-[var(--theme-soft-panel)] to-[var(--theme-selected-bg)] p-4 text-sm leading-6 text-[var(--theme-body)]">
        {conclusion}
      </div>

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <SubjectMetric label="主导主体" value={summary?.dominant_subject_type ?? "暂无"} />
        <SubjectMetric label="KOL互动贡献" value={formatPercent(summary?.kol_engagement_rate)} />
        <SubjectMetric label="最高KOL类型" value={summary?.top_kol_type ?? "暂无"} />
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
        <div>
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
            <Sparkles className="h-4 w-4 text-[var(--theme-primary)]" />
            主体贡献
          </div>
          <SubjectDistribution story={story} />
        </div>
        <div>
          <KolTypeBars data={story?.kol_type_distribution ?? []} userProfiles={userProfiles} />
        </div>
      </div>

      <TopAuthors story={story} onSelectAuthor={setSelectedAuthorId} />
      <AuthorDetailDrawer authorId={selectedAuthorId} onClose={() => setSelectedAuthorId(null)} />
    </article>
  );
}
