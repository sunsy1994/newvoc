type MetricCardProps = {
  label: string;
  value: string;
  hint?: string;
  tone?: "purple" | "blue" | "teal" | "violet" | "neutral";
};

const toneClasses = {
  purple: "bg-[#f0efff] text-[#5347CE]",
  blue: "bg-[#eef6ff] text-[#4896FE]",
  teal: "bg-[#e9fbfa] text-[#16C8C7]",
  violet: "bg-[#f3f1ff] text-[#887CFD]",
  neutral: "bg-[#f2f4f8] text-[#596070]",
};

export function MetricCard({ label, value, hint, tone = "neutral" }: MetricCardProps) {
  return (
    <article className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium text-[#6f7685]">{label}</p>
        <span className={`h-7 w-7 rounded-lg ${toneClasses[tone]}`} />
      </div>
      <strong className="mt-3 block text-[26px] font-semibold leading-none tracking-tight text-[#151720]">{value}</strong>
      {hint ? <span className="mt-3 inline-flex rounded-md bg-[#f5f7fb] px-2 py-1 text-[11px] text-[#7b8190]">{hint}</span> : null}
    </article>
  );
}
