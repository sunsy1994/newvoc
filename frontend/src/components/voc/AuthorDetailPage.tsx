import Link from "next/link";
import { ArrowLeft, BadgeCheck, ExternalLink, FileText, MessageCircle, RadioTower, Sparkles, UsersRound } from "lucide-react";

import type { AuthorContentItem, AuthorDetailPayload, AuthorEventItem } from "@/types/vocMarket";

import { AuthorSankey } from "./AuthorSankey";

type AuthorDetailPageProps = {
  payload: AuthorDetailPayload;
  showBackLink?: boolean;
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;
const formatDate = (value?: string | null) => (value ? value.slice(0, 10) : "暂无");

function MetricPill({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] px-4 py-3 shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
      <p className="text-[11px] font-medium text-[var(--theme-muted)]">{label}</p>
      <strong className="mt-2 block text-lg font-semibold text-[var(--theme-ink)]">{value}</strong>
    </div>
  );
}

function EmptyPanel({ text }: { text: string }) {
  return (
    <div className="flex h-36 items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)] text-sm text-[var(--theme-muted)]">
      {text}
    </div>
  );
}

function EventRows({ events }: { events: AuthorEventItem[] }) {
  if (!events.length) return <EmptyPanel text="暂无参与事件数据" />;
  return (
    <div className="max-h-[420px] overflow-y-auto pr-1 space-y-2">
      {events.slice(0, 8).map((event) => (
        <div key={event.event_id} className="grid min-h-[86px] gap-3 rounded-xl bg-[var(--theme-white)] px-3 py-3 text-xs shadow-sm md:grid-cols-[minmax(0,1.4fr)_auto_auto_auto]">
          <div className="min-w-0">
            <Link href={`/voc/events/market?event_id=${encodeURIComponent(event.event_id)}`} className="line-clamp-2 font-semibold leading-5 text-[var(--theme-ink)] hover:text-[var(--theme-primary)]">
              {event.event_name}
            </Link>
            <p className="mt-1 truncate text-[var(--theme-muted)]">{event.brand_name ?? "未填品牌"} · {event.model_name ?? "未填车型"} · {event.event_status ?? "未知状态"}</p>
          </div>
          <span className="whitespace-nowrap text-[var(--theme-body)]">{formatNumber(event.content_count)} 篇内容</span>
          <span className="whitespace-nowrap text-[var(--theme-body)]">{formatNumber(event.received_comment_count)} 条评论</span>
          <span className="whitespace-nowrap font-semibold text-[var(--theme-primary)]">{formatNumber(event.total_engagement)}</span>
        </div>
      ))}
    </div>
  );
}

function ContentRows({ contents }: { contents: AuthorContentItem[] }) {
  if (!contents.length) return <EmptyPanel text="暂无发布内容数据" />;
  return (
    <div className="max-h-[420px] overflow-y-auto pr-1 space-y-2">
      {contents.slice(0, 10).map((content) => (
        <div key={content.content_id} className="grid min-h-[86px] gap-3 rounded-xl bg-[var(--theme-white)] px-3 py-3 text-xs shadow-sm md:grid-cols-[minmax(0,1fr)_auto]">
          <div className="min-w-0 flex-1">
            <p className="line-clamp-2 font-semibold leading-5 text-[var(--theme-ink)]">{content.title || "未命名内容"}</p>
            <p className="mt-1 truncate text-[var(--theme-muted)]">
              {content.event_name ?? "未知事件"} · {content.platform ?? "未知平台"} · {formatDate(content.published_at)}
            </p>
          </div>
          <div className="flex shrink-0 items-center justify-end gap-2 whitespace-nowrap">
            <span className="rounded-lg bg-[var(--theme-chip)] px-2.5 py-1 font-semibold text-[var(--theme-primary)]">{formatNumber(content.engagement_total)}</span>
            {content.source_url ? (
              <a href={content.source_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1 font-medium text-[var(--theme-body)] hover:text-[var(--theme-primary)]">
                原帖
                <ExternalLink className="h-3 w-3" />
              </a>
            ) : null}
          </div>
        </div>
      ))}
    </div>
  );
}

export function AuthorDetailPage({ payload, showBackLink = true }: AuthorDetailPageProps) {
  const { author, metrics, kol_profile: kolProfile, comment_quality: quality } = payload;
  const summary = quality?.summary;
  const hasKolProfile = Boolean(kolProfile && Object.keys(kolProfile).length);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <Link href="/voc/events/market" className="author-back-link mb-3 inline-flex items-center gap-2 text-xs font-medium text-[var(--theme-muted)] hover:text-[var(--theme-primary)]">
            <ArrowLeft className="h-3.5 w-3.5" />
            返回市场看板
          </Link>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Author Intelligence</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--theme-ink)]">{author.author_name ?? "未知作者"}</h1>
        </div>
        <div className="flex flex-wrap justify-end gap-2 text-xs">
          <span className="inline-flex items-center gap-1 rounded-lg bg-[var(--theme-chip)] px-3 py-1.5 font-medium text-[var(--theme-primary)]">
            <UsersRound className="h-3.5 w-3.5" />
            {author.platform ?? "未知平台"}
          </span>
          <span className="rounded-lg bg-[var(--theme-white)] px-3 py-1.5 text-[var(--theme-body)] shadow-[0_8px_20px_rgba(26,32,44,0.03)]">
            {author.is_kol ? "KOL作者" : author.author_type ?? "普通作者"}
          </span>
          {author.author_home_url ? (
            <a href={author.author_home_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 rounded-lg bg-[var(--theme-white)] px-3 py-1.5 text-[var(--theme-body)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] hover:text-[var(--theme-primary)]">
              主页
              <ExternalLink className="h-3 w-3" />
            </a>
          ) : null}
        </div>
      </header>

      <section className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
          <Sparkles className="h-4 w-4 text-[var(--theme-primary)]" />
          作者画像
        </div>
        <div className="grid gap-3 md:grid-cols-4">
          <MetricPill label="参与事件" value={`${formatNumber(metrics.event_count)} 个`} />
          <MetricPill label="发布内容" value={`${formatNumber(metrics.content_count)} 篇`} />
          <MetricPill label="收到评论" value={`${formatNumber(metrics.received_comment_count)} 条`} />
          <MetricPill label="总互动量" value={formatNumber(metrics.total_engagement)} />
        </div>
        <div className="mt-4 rounded-2xl bg-gradient-to-r from-[var(--theme-soft-panel)] to-[var(--theme-selected-bg)] p-4 text-sm leading-6 text-[var(--theme-body)]">
          {hasKolProfile
            ? `该作者全局画像为「${kolProfile?.kol_main_type ?? "未维护类型"}」，内容倾向「${kolProfile?.content_tendency ?? "未维护"}」，车型关注「${kolProfile?.car_focus ?? "未维护"}」。${kolProfile?.remark ?? ""}`
            : "该作者暂未维护KOL画像。作者画像按历史发布内容沉淀，不随单个事件变化。"}
        </div>
      </section>

      <section className="grid gap-4 xl:grid-cols-[0.95fr_1.05fr]">
        <article className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
            <RadioTower className="h-4 w-4 text-[var(--voc-chart-5)]" />
            参与事件
          </div>
          <EventRows events={payload.events} />
        </article>

        <article className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
            <FileText className="h-4 w-4 text-[var(--voc-chart-3)]" />
            发布内容
          </div>
          <ContentRows contents={payload.contents} />
        </article>
      </section>

      <section className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-sm font-semibold text-[var(--theme-ink)]">
            <BadgeCheck className="h-4 w-4 text-[var(--theme-primary)]" />
            评论质量与吸引画像
          </div>
          <span className="rounded-lg bg-[var(--theme-soft-panel)] px-2.5 py-1 text-xs text-[var(--theme-muted)]">{"作者 -> 事件 -> 用户画像"}</span>
        </div>
        <div className="mb-4 grid gap-3 md:grid-cols-4">
          <MetricPill label="已打标评论" value={`${formatNumber(summary?.labeled_comment_count)} 条`} />
          <MetricPill label="有效评论" value={`${formatNumber(summary?.vehicle_related_count)} 条`} />
          <MetricPill label="无效评论" value={`${formatNumber(summary?.invalid_comment_count)} 条`} />
          <MetricPill label="有效评论率" value={formatPercent(summary?.vehicle_related_rate)} />
        </div>
        <AuthorSankey sankey={payload.sankey} />
      </section>
    </div>
  );
}
