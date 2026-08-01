import { reportChartTheme as theme } from "./chartTheme";
import { ReportVisualShell } from "./ReportVisualShell";
import type { ReportVisualChart } from "./types";

type ChartProps = { chart: ReportVisualChart };

function text(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function number(value: unknown): number | undefined {
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : undefined;
}

function percent(value: number | undefined): string {
  return value === undefined ? "--" : `${Math.round(value * 10) / 10}%`;
}

function count(value: number | undefined): string {
  return value === undefined ? "--" : new Intl.NumberFormat("zh-CN").format(value);
}

export function P1ProductFocusBars({ chart }: ChartProps) {
  const rows = chart.data.flatMap((row) => {
    const aspect = text(row.aspect);
    const mentionRate = number(row.mention_rate);
    if (!aspect || mentionRate === undefined) return [];
    return [{ aspect, mentionRate, commentCount: number(row.comment_count), positiveRate: number(row.positive_rate) }];
  });

  return (
    <ReportVisualShell chart={chart} hasData={rows.length > 0}>
      <div className="grid gap-x-8 gap-y-5 lg:grid-cols-2" data-product-continuous-bar>
        {rows.map((row, index) => (
          <div key={row.aspect} className="min-w-0">
            <div className="mb-2 flex items-end justify-between gap-4">
              <div className="flex min-w-0 items-center gap-2">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--theme-soft-panel)] text-[11px] font-bold text-[var(--theme-primary)]">
                  {index + 1}
                </span>
                <span className="truncate text-sm font-semibold text-[var(--theme-ink)]">{row.aspect}</span>
              </div>
              <span className="shrink-0 text-lg font-semibold tabular-nums text-[var(--theme-ink)]">{percent(row.mentionRate)}</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-[var(--theme-soft-panel)]">
              <div
                className="h-full rounded-full bg-gradient-to-r from-[var(--theme-primary)] to-[var(--theme-selected-text)] shadow-[0_4px_12px_rgba(26,164,164,0.22)]"
                style={{ width: `${Math.min(100, row.mentionRate)}%` }}
              />
            </div>
            <div className="mt-2 flex gap-4 text-xs text-[var(--theme-muted)]">
              <span>评论 <b className="font-semibold text-[var(--theme-body)]">{count(row.commentCount)}</b></span>
              <span>正向 <b className="font-semibold text-emerald-600">{percent(row.positiveRate)}</b></span>
            </div>
          </div>
        ))}
      </div>
    </ReportVisualShell>
  );
}

export function P2SentimentStack({ chart }: ChartProps) {
  const rows = chart.data.flatMap((row) => {
    const aspect = text(row.aspect);
    const positive = number(row.positive_rate);
    const neutral = number(row.neutral_rate);
    const negative = number(row.negative_rate);
    if (!aspect || positive === undefined || neutral === undefined || negative === undefined) return [];
    return [{ aspect, positive, neutral, negative }];
  });

  return (
    <ReportVisualShell chart={chart} hasData={rows.length > 0}>
      <div className="space-y-5" data-product-sentiment-stack>
        <div className="flex flex-wrap gap-4 text-xs text-[var(--theme-muted)]">
          {[["bg-emerald-500", "正向"], ["bg-slate-300", "中性"], ["bg-rose-400", "负向"]].map(([tone, label]) => (
            <span key={label} className="flex items-center gap-1.5"><i className={`h-2 w-2 rounded-full ${tone}`} />{label}</span>
          ))}
        </div>
        {rows.map((row) => (
          <div key={row.aspect}>
            <div className="mb-2 flex items-center justify-between gap-3 text-xs">
              <span className="font-semibold text-[var(--theme-ink)]">{row.aspect}</span>
              <span className="tabular-nums text-[var(--theme-muted)]">正 {percent(row.positive)} · 负 {percent(row.negative)}</span>
            </div>
            <div className="flex h-3.5 overflow-hidden rounded-full bg-[var(--theme-soft-panel)]" aria-label={`${row.aspect}正向${percent(row.positive)}，中性${percent(row.neutral)}，负向${percent(row.negative)}`}>
              <span className="h-full bg-emerald-500" style={{ width: `${row.positive}%` }} />
              <span className="h-full bg-slate-300" style={{ width: `${row.neutral}%` }} />
              <span className="h-full bg-rose-400" style={{ width: `${row.negative}%` }} />
            </div>
          </div>
        ))}
      </div>
    </ReportVisualShell>
  );
}

const laneConfig = {
  surprise: { title: "惊喜点", eyebrow: "超预期反馈", shell: "border-emerald-200 bg-emerald-50/70", badge: "bg-emerald-100 text-emerald-700" },
  conversion: { title: "机会点", eyebrow: "转化潜力", shell: "border-sky-200 bg-sky-50/70", badge: "bg-sky-100 text-sky-700" },
  pain: { title: "风险点", eyebrow: "负面与阻力", shell: "border-rose-200 bg-rose-50/70", badge: "bg-rose-100 text-rose-700" },
} as const;

export function P3OpportunityLanes({ chart }: ChartProps) {
  const rows = chart.data.flatMap((row) => {
    const type = text(row.point_type) as keyof typeof laneConfig | undefined;
    const aspect = text(row.aspect);
    const score = number(row.opportunity_score);
    if (!type || !laneConfig[type] || !aspect || score === undefined) return [];
    return [{ type, aspect, score, mentionRate: number(row.mention_rate) }];
  });

  return (
    <ReportVisualShell chart={chart} hasData={rows.length > 0}>
      <div className="grid gap-3 sm:grid-cols-3" data-product-opportunity-lane>
        {(Object.keys(laneConfig) as Array<keyof typeof laneConfig>).map((type) => {
          const config = laneConfig[type];
          const items = rows.filter((row) => row.type === type);
          return (
            <section key={type} className={`min-w-0 rounded-2xl border p-3 ${config.shell}`}>
              <p className={`inline-flex rounded-full px-2 py-1 text-[10px] font-bold ${config.badge}`}>{config.title}</p>
              <p className="mt-2 text-[11px] text-[var(--theme-muted)]">{config.eyebrow}</p>
              <div className="mt-3 space-y-2">
                {items.length ? items.map((item) => (
                  <div key={`${type}-${item.aspect}`} className="rounded-xl border border-white/80 bg-white/90 p-3 shadow-[0_6px_18px_rgba(30,50,70,0.06)]">
                    <p className="truncate text-sm font-semibold text-[var(--theme-ink)]">{item.aspect}</p>
                    <div className="mt-2 flex items-end justify-between gap-2">
                      <span className="text-[10px] text-[var(--theme-muted)]">机会分</span>
                      <b className="text-lg tabular-nums text-[var(--theme-ink)]">{item.score.toFixed(1)}</b>
                    </div>
                    {item.mentionRate !== undefined ? <p className="mt-1 text-[10px] text-[var(--theme-muted)]">提及占比 {percent(item.mentionRate)}</p> : null}
                  </div>
                )) : <p className="py-4 text-center text-xs text-[var(--theme-muted)]">暂无</p>}
              </div>
            </section>
          );
        })}
      </div>
    </ReportVisualShell>
  );
}

const matrixColumns = [
  { key: "advantage_count", label: "优势", tone: "bg-emerald-500" },
  { key: "neutral_count", label: "中性", tone: "bg-slate-400" },
  { key: "disadvantage_count", label: "劣势", tone: "bg-rose-400" },
  { key: "unclear_count", label: "未明确", tone: "bg-amber-400" },
] as const;

export function P4PkoMatrix({ chart }: ChartProps) {
  const rows = chart.data.flatMap((row) => {
    const dimension = text(row.dimension);
    if (!dimension) return [];
    const values = matrixColumns.map(({ key }) => number(row[key]) ?? 0);
    return [{ dimension, values, total: values.reduce((sum, value) => sum + value, 0), target: text(row.top_target) }];
  });
  const max = Math.max(1, ...rows.flatMap((row) => row.values));

  return (
    <ReportVisualShell chart={chart} hasData={rows.length > 0}>
      <div className="overflow-x-auto" data-product-pko-matrix>
        <div className="min-w-[680px]">
          <div className="grid grid-cols-[minmax(140px,1.4fr)_repeat(4,minmax(90px,1fr))_90px] gap-2 px-3 pb-2 text-xs font-medium text-[var(--theme-muted)]">
            <span>产品维度</span>
            {matrixColumns.map((column) => <span key={column.key} className="text-center">{column.label}</span>)}
            <span className="text-right">对比总量</span>
          </div>
          <div className="space-y-2">
            {rows.map((row) => (
              <div key={row.dimension} className="grid grid-cols-[minmax(140px,1.4fr)_repeat(4,minmax(90px,1fr))_90px] items-center gap-2 rounded-xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)]/40 p-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold text-[var(--theme-ink)]">{row.dimension}</p>
                  {row.target ? <p className="mt-1 truncate text-[10px] text-[var(--theme-muted)]">主要对比 {row.target}</p> : null}
                </div>
                {row.values.map((value, index) => (
                  <div key={matrixColumns[index].key} className="flex justify-center">
                    <span
                      className={`flex h-9 min-w-12 items-center justify-center rounded-xl text-xs font-bold text-white ${matrixColumns[index].tone}`}
                      style={{ opacity: value ? 0.35 + (value / max) * 0.65 : 0.12 }}
                      title={`${matrixColumns[index].label} ${value}`}
                    >
                      {value}
                    </span>
                  </div>
                ))}
                <span className="text-right text-base font-semibold tabular-nums text-[var(--theme-ink)]">{row.total}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </ReportVisualShell>
  );
}
