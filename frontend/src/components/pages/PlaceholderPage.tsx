type PlaceholderPageProps = {
  title: string;
  description: string;
};

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <section className="space-y-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-zinc-400">AutoVOC</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-zinc-950">{title}</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-500">{description}</p>
      </div>
      <div className="rounded-[28px] border border-dashed border-zinc-200 bg-zinc-50/70 p-10 text-sm text-zinc-400">
        这里会在后续阶段接入真实业务组件。
      </div>
    </section>
  );
}
