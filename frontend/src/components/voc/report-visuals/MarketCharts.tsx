import type { ReportVisualChart } from "./types";

type ChartProps = { chart: ReportVisualChart };

const num = (value: unknown) => typeof value === "number" && Number.isFinite(value) ? Math.max(0, value) : 0;
const text = (value: unknown) => typeof value === "string" ? value.trim() : "";
const compact = (value: number) => new Intl.NumberFormat("zh-CN", { notation: "compact", maximumFractionDigits: 1 }).format(value);

function EmptyChart() {
  return <div className="py-16 text-center text-sm text-[var(--theme-muted)]">暂无可用数据</div>;
}

export function M1VolumeRhythm({ chart }: ChartProps) {
  const rows = chart.data.slice(0, 30);
  if (!rows.length) return <EmptyChart />;
  const totals = rows.map((row) => num(row.content_count) + num(row.comment_count));
  const max = Math.max(...totals, 1);
  const width = 760;
  const height = 280;
  const slot = width / rows.length;
  const barWidth = Math.max(8, Math.min(28, slot * 0.56));
  return (
    <svg aria-label="传播结果与节奏图" role="img" viewBox={`0 0 ${width} ${height}`} className="h-auto w-full">
      <line x1="0" y1="238" x2={width} y2="238" stroke="var(--theme-border)" />
      {rows.map((row, index) => {
        const content = num(row.content_count);
        const comments = num(row.comment_count);
        const total = content + comments;
        const contentHeight = 190 * content / max;
        const commentHeight = 190 * comments / max;
        const x = index * slot + (slot - barWidth) / 2;
        const peak = total === max;
        return (
          <g key={`${text(row.date)}-${index}`}>
            <rect x={x} y={238 - contentHeight} width={barWidth} height={contentHeight} rx="4" fill="var(--theme-primary)" opacity="0.42" />
            <rect x={x} y={238 - contentHeight - commentHeight} width={barWidth} height={commentHeight} rx="4" fill="var(--theme-primary)" opacity="0.9" />
            {peak ? <circle cx={x + barWidth / 2} cy={Math.max(18, 228 - contentHeight - commentHeight)} r="4" fill="var(--theme-primary)" /> : null}
            <text x={x + barWidth / 2} y="260" textAnchor="middle" fontSize="10" fill="var(--theme-muted)">{text(row.date).slice(5)}</text>
          </g>
        );
      })}
    </svg>
  );
}

export function M2TopicDrivers({ chart }: ChartProps) {
  const rows = [...chart.data].sort((a, b) => num(b.comment_count) - num(a.comment_count) || num(b.total_engagement) - num(a.total_engagement)).slice(0, 10);
  if (!rows.length) return <EmptyChart />;
  const max = Math.max(...rows.map((row) => num(row.comment_count)), 1);
  return (
    <div aria-label="话题驱动图" role="img" className="space-y-3">
      {rows.map((row, index) => (
        <div key={`${text(row.topic)}-${index}`} className="grid grid-cols-[minmax(90px,160px)_minmax(120px,1fr)_auto] items-center gap-3">
          <span className="truncate text-sm font-medium text-[var(--theme-ink)]">{text(row.topic) || "未命名话题"}</span>
          <div className="h-3 overflow-hidden rounded-full bg-[var(--theme-selected-bg)]"><div className="h-full rounded-full bg-[var(--theme-primary)]" style={{ width: `${Math.max(3, num(row.comment_count) / max * 100)}%` }} /></div>
          <span className="whitespace-nowrap text-xs text-[var(--theme-muted)]">{compact(num(row.comment_count))} 评论 · {compact(num(row.content_count))} 内容 · {compact(num(row.total_engagement))} 互动</span>
        </div>
      ))}
    </div>
  );
}

export function M3SubjectContribution({ chart }: ChartProps) {
  const rows = [...chart.data].sort((a, b) => num(b.total_engagement) - num(a.total_engagement)).slice(0, 5);
  if (!rows.length) return <EmptyChart />;
  const maxEngagement = Math.max(...rows.map((row) => num(row.total_engagement)), 1);
  const maxContent = Math.max(...rows.map((row) => num(row.content_count)), 1);
  return (
    <div aria-label="传播主体图" role="img" className="space-y-4">
      {rows.map((row, index) => {
        const ratio = num(row.total_engagement) / maxEngagement;
        const dot = 8 + 10 * num(row.content_count) / maxContent;
        return <div key={`${text(row.author_name)}-${index}`} className="grid grid-cols-[150px_1fr_90px] items-center gap-3">
          <div className="min-w-0"><p className="truncate text-sm font-medium text-[var(--theme-ink)]">{text(row.author_name) || "未知作者"}</p><p className="truncate text-xs text-[var(--theme-muted)]">{text(row.author_type) || text(row.kol_type)}</p></div>
          <div className="relative h-6"><div className="absolute left-0 top-1/2 h-px -translate-y-1/2 bg-[var(--theme-primary)] opacity-45" style={{ width: `${Math.max(4, ratio * 100)}%` }} /><span className="absolute top-1/2 block -translate-x-1/2 -translate-y-1/2 rounded-full bg-[var(--theme-primary)]" style={{ left: `${Math.max(4, ratio * 100)}%`, width: dot, height: dot }} /></div>
          <span className="text-right text-xs text-[var(--theme-muted)]">{compact(num(row.total_engagement))} 互动<br />{compact(num(row.content_count))} 内容</span>
        </div>;
      })}
    </div>
  );
}

export function M4ChannelEfficiency({ chart }: ChartProps) {
  const rows = chart.data.slice(0, 8);
  if (!rows.length) return <EmptyChart />;
  if (rows.length === 1) {
    const row = rows[0];
    return <div aria-label="渠道效率图" role="img" className="flex min-h-56 items-center justify-center"><div className="rounded-full border border-[var(--theme-border)] bg-[var(--theme-selected-bg)] px-10 py-8 text-center"><p className="font-semibold text-[var(--theme-ink)]">{text(row.platform)}</p><p className="mt-2 text-sm text-[var(--theme-muted)]">{compact(num(row.total_volume))} 声量 · {compact(num(row.engagement_per_content))} 单内容互动</p></div></div>;
  }
  const maxX = Math.max(...rows.map((row) => num(row.total_volume)), 1);
  const maxY = Math.max(...rows.map((row) => num(row.engagement_per_content)), 1);
  return <svg aria-label="渠道效率图" role="img" viewBox="0 0 760 300" className="h-auto w-full">
    <line x1="54" y1="252" x2="730" y2="252" stroke="var(--theme-border)" /><line x1="54" y1="24" x2="54" y2="252" stroke="var(--theme-border)" />
    {rows.map((row, index) => { const x = 70 + num(row.total_volume) / maxX * 630; const y = 238 - num(row.engagement_per_content) / maxY * 190; return <g key={`${text(row.platform)}-${index}`}><circle cx={x} cy={y} r="9" fill="var(--theme-primary)" opacity="0.82" /><text x={x + 13} y={y - 8} fontSize="12" fill="var(--theme-ink)">{text(row.platform)}</text></g>; })}
    <text x="640" y="282" fontSize="11" fill="var(--theme-muted)">传播规模 →</text><text x="12" y="18" fontSize="11" fill="var(--theme-muted)">单内容互动 ↑</text>
  </svg>;
}
