type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
  tone?: "purple" | "blue" | "teal" | "violet" | "neutral";
  icon?: React.ReactNode;
};

const toneClasses = {
  purple: "bg-[var(--theme-chip)] text-[var(--theme-primary)]",
  blue: "bg-[var(--theme-soft-panel)] text-[var(--voc-chart-5)]",
  teal: "bg-[var(--theme-soft-panel)] text-[var(--voc-chart-3)]",
  violet: "bg-[var(--theme-selected-bg)] text-[var(--voc-chart-4)]",
  neutral: "bg-[var(--theme-soft-panel)] text-[var(--theme-body)]",
};

export function MetricCard({ label, value, hint, tone = "neutral", icon }: MetricCardProps) {
  return (
    <article className="flex min-h-[138px] flex-col rounded-[18px] border border-[var(--theme-border)] bg-[var(--theme-white)] p-4 shadow-[0_10px_26px_rgba(31,43,39,0.04)]">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs font-medium text-[var(--theme-body)]">{label}</p>
        <span className={`flex h-8 w-8 items-center justify-center rounded-[10px] ${toneClasses[tone]}`}>
          {icon}
        </span>
      </div>
      <strong className="mt-4 block text-[28px] font-semibold leading-none tracking-[-0.04em] text-[var(--theme-ink)]">{value}</strong>
      {hint ? <span className="mt-auto pt-3 text-[11px] text-[var(--theme-muted)]">{hint}</span> : null}
    </article>
  );
}
