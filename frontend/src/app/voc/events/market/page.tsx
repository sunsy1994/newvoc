import { serverApiBaseUrl } from "@/config/navigation";

type VocEvent = {
  event_id: string;
  event_name: string;
  brand_name?: string;
  model_name?: string;
  event_type?: string;
  content_cnt?: number;
  comment_cnt?: number;
  kol_content_cnt?: number;
  author_cnt?: number;
  total_engagement?: number;
};

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

export default async function MarketDashboardPage() {
  const events = await getEvents();
  const activeEvent = events[0];
  const metrics = [
    { label: "事件声量", value: activeEvent?.content_cnt ?? 0, hint: "内容资产汇总" },
    { label: "评论讨论", value: activeEvent?.comment_cnt ?? 0, hint: "评论资产汇总" },
    { label: "KOL发声", value: activeEvent?.kol_content_cnt ?? 0, hint: "已识别KOL内容" },
    { label: "总互动量", value: activeEvent?.total_engagement ?? 0, hint: "点赞/评论/收藏/分享" },
  ];

  return (
    <div className="space-y-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-400">VOC Event</p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">市场看板</h1>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">
            这里承接 VOC看事件 的市场部视角：先看事件传播表现、KOL发声和用户画像结论，不展示原始底表。
          </p>
        </div>
        <button className="rounded-full bg-zinc-950 px-4 py-2 text-sm font-medium text-white shadow-sm">
          {activeEvent ? activeEvent.event_name : "暂无事件"}
        </button>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        {metrics.map((item) => (
          <article key={item.label} className="rounded-3xl border border-zinc-200/80 bg-zinc-50/80 p-5">
            <p className="text-xs text-zinc-500">{item.label}</p>
            <strong className="mt-3 block text-3xl font-semibold text-zinc-950">
              {item.value.toLocaleString("zh-CN")}
            </strong>
            <span className="mt-2 block text-xs text-zinc-400">{item.hint}</span>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-zinc-950">事件传播摘要</h2>
          <p className="mt-2 text-sm text-zinc-500">
            {activeEvent
              ? `${activeEvent.brand_name ?? ""} ${activeEvent.model_name ?? ""} / ${activeEvent.event_type ?? ""}`
              : "请先确认 FastAPI 服务已启动，并且已有事件数据。"}
          </p>
          <div className="mt-5 h-56 rounded-3xl border border-dashed border-zinc-200 bg-zinc-50/70" />
        </article>
        <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-zinc-950">KOL与用户洞察</h2>
          <div className="mt-5 space-y-3">
            {["KOL类型分布", "吸引用户画像", "投放策略线索"].map((label) => (
              <div key={label} className="rounded-2xl bg-zinc-50 px-4 py-3 text-sm text-zinc-600">{label}</div>
            ))}
          </div>
        </article>
      </section>
    </div>
  );
}
