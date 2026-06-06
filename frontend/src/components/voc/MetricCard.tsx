type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
};

export function MetricCard({ label, value, hint }: MetricCardProps) {
  return (
    <article className="rounded-3xl border border-zinc-200/80 bg-white p-5 shadow-sm">
      <p className="text-xs font-medium text-zinc-500">{label}</p>
      <strong className="mt-3 block text-2xl font-semibold tracking-tight text-zinc-950">{value}</strong>
      {hint ? <span className="mt-2 block text-xs text-zinc-400">{hint}</span> : null}
    </article>
  );
}
