import { ChannelStackedBars } from "@/components/voc/ChannelStackedBars";
import { HotPostList } from "@/components/voc/HotPostList";
import { KolTypeBars } from "@/components/voc/KolTypeBars";
import { MetricCard } from "@/components/voc/MetricCard";
import { VolumeTrendChart } from "@/components/voc/VolumeTrendChart";
import { serverApiBaseUrl } from "@/config/navigation";
import type { MarketDashboardPayload, VocEvent } from "@/types/vocMarket";

async function getEvents(): Promise<VocEvent[]> {
  try {
    const response = await fetch(`${serverApiBaseUrl}/voc/events`, { cache: "no-store" });
    if (!response.ok) return [];
    const payload = (await response.json()) as { events?: VocEvent[] };
    return payload.events ?? [];
  } catch {
    return [];
  }
}

async function getMarketDashboard(eventId: string): Promise<MarketDashboardPayload | null> {
  try {
    const response = await fetch(`${serverApiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/market-dashboard`, {
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as MarketDashboardPayload;
  } catch {
    return null;
  }
}

function formatNumber(value: number) {
  return value.toLocaleString("zh-CN");
}

type PageProps = {
  searchParams?: {
    event_id?: string;
  };
};

export default async function MarketDashboardPage({ searchParams }: PageProps) {
  const events = await getEvents();
  const selectedEventId = searchParams?.event_id ?? events[0]?.event_id;
  const dashboard = selectedEventId ? await getMarketDashboard(selectedEventId) : null;
  const metrics = dashboard?.overview_metrics;

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-zinc-200/80 bg-white p-6 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-400">VOC Event</p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">市场看板</h1>
            <p className="mt-2 text-sm text-zinc-500">基于真实入库资产查看事件声量、渠道、KOL类型和热门内容。</p>
          </div>
          <form>
            <select
              name="event_id"
              defaultValue={selectedEventId}
              className="min-w-64 rounded-full border border-zinc-200 bg-zinc-50 px-4 py-2 text-sm text-zinc-700 outline-none"
            >
              {events.map((event) => (
                <option key={event.event_id} value={event.event_id}>
                  {event.event_name}
                </option>
              ))}
            </select>
            <button className="ml-2 rounded-full bg-zinc-950 px-4 py-2 text-sm font-medium text-white">查看</button>
          </form>
        </div>
        {dashboard?.event ? (
          <div className="mt-5 flex flex-wrap gap-2 text-xs text-zinc-500">
            <span className="rounded-full bg-zinc-100 px-3 py-1">{dashboard.event.event_status ?? "未知状态"}</span>
            <span className="rounded-full bg-zinc-100 px-3 py-1">{dashboard.event.brand_name ?? "未填品牌"}</span>
            <span className="rounded-full bg-zinc-100 px-3 py-1">{dashboard.event.model_name ?? "未填车型"}</span>
            <span className="rounded-full bg-zinc-100 px-3 py-1">{dashboard.event.event_type ?? "未填类型"}</span>
          </div>
        ) : null}
      </section>

      {metrics ? (
        <section className="grid gap-3 md:grid-cols-5">
          <MetricCard label="总声量" value={formatNumber(metrics.total_volume)} hint="主贴 + 评论" />
          <MetricCard label="主贴数" value={formatNumber(metrics.content_count)} />
          <MetricCard label="评论数" value={formatNumber(metrics.comment_count)} />
          <MetricCard
            label="KOL发声"
            value={`${formatNumber(metrics.kol_count)} 位`}
            hint={`贡献 ${formatNumber(metrics.kol_content_count)} 条主贴`}
          />
          <MetricCard label="总互动量" value={formatNumber(metrics.total_engagement)} />
        </section>
      ) : (
        <div className="rounded-3xl border border-dashed border-zinc-200 bg-white p-10 text-center text-sm text-zinc-400">
          暂无事件数据，请先导入并运行ETL。
        </div>
      )}

      {dashboard ? (
        <>
          <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
            <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-zinc-950">声量趋势</h2>
              <p className="mt-1 text-xs text-zinc-400">按发布时间聚合</p>
              <div className="mt-5">
                <VolumeTrendChart data={dashboard.volume_trend} />
              </div>
            </article>
            <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-zinc-950">KOL类型分布</h2>
              <p className="mt-1 text-xs text-zinc-400">来自KOL画像表</p>
              <div className="mt-5">
                <KolTypeBars data={dashboard.kol_type_distribution} />
              </div>
            </article>
          </section>

          <section className="grid gap-4 lg:grid-cols-[1fr_0.9fr]">
            <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-zinc-950">渠道分布</h2>
              <p className="mt-1 text-xs text-zinc-400">主贴 + 评论堆积</p>
              <div className="mt-5">
                <ChannelStackedBars data={dashboard.channel_distribution} />
              </div>
            </article>
            <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
              <h2 className="text-base font-semibold text-zinc-950">热门帖子榜</h2>
              <p className="mt-1 text-xs text-zinc-400">按底表总互动量倒序</p>
              <div className="mt-5">
                <HotPostList posts={dashboard.hot_posts} />
              </div>
            </article>
          </section>
        </>
      ) : null}
    </div>
  );
}
