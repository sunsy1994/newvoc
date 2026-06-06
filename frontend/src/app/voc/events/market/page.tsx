const metrics = [
  { label: "事件声量", value: "25", hint: "内容资产汇总" },
  { label: "评论讨论", value: "19", hint: "有效评论沉淀" },
  { label: "KOL发声", value: "6", hint: "已识别KOL内容" },
  { label: "用户画像", value: "1", hint: "已回灌标签分布" },
];

export default function MarketDashboardPage() {
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
        <button className="rounded-full bg-zinc-950 px-4 py-2 text-sm font-medium text-white shadow-sm">选择事件</button>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        {metrics.map((item) => (
          <article key={item.label} className="rounded-3xl border border-zinc-200/80 bg-zinc-50/80 p-5">
            <p className="text-xs text-zinc-500">{item.label}</p>
            <strong className="mt-3 block text-3xl font-semibold text-zinc-950">{item.value}</strong>
            <span className="mt-2 block text-xs text-zinc-400">{item.hint}</span>
          </article>
        ))}
      </section>

      <section className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <article className="rounded-[28px] border border-zinc-200/80 bg-white p-6 shadow-sm">
          <h2 className="text-base font-semibold text-zinc-950">事件传播摘要</h2>
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
