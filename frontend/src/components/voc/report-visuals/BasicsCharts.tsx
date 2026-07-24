import { reportChartTheme as theme } from "./chartTheme";
import { ReportVisualShell } from "./ReportVisualShell";
import type { ReportVisualChart } from "./types";

type BasicsChartProps = {
  chart: ReportVisualChart;
};

type Segment = {
  label: string;
  value: number;
};

type SingleValueRow = {
  label: string;
  value: number;
};

type PairedValueRow = {
  label: string;
  first: number;
  second: number;
};

type StackedValueRow = {
  label: string;
  segments: Segment[];
};

type ScatterPoint = {
  label: string;
  x: number;
  y: number;
};

const labelKeys = ["label", "name", "date", "platform", "category", "dimension"];
const valueKeys = ["value", "count", "total", "percentage", "percent", "rate", "total_volume"];

function finiteNumber(value: unknown): number | undefined {
  if (value === null || value === undefined || (typeof value === "string" && !value.trim())) {
    return undefined;
  }
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) ? Math.max(0, number) : undefined;
}

function readOptionalNumber(row: Record<string, unknown>, keys: string[]): number | undefined {
  for (const key of keys) {
    const value = finiteNumber(row[key]);
    if (value !== undefined) return value;
  }
  return undefined;
}

function readNumber(row: Record<string, unknown>, keys: string[], fallback = 0): number {
  return readOptionalNumber(row, keys) ?? fallback;
}

function readString(row: Record<string, unknown>, keys: string[]): string | undefined {
  for (const key of keys) {
    const value = row[key];
    if (typeof value === "string" && value.trim()) return value.trim();
  }
  return undefined;
}

function readLabel(row: Record<string, unknown>, index: number): string {
  return readString(row, labelKeys) ?? `项目 ${index + 1}`;
}

function truncateSvgLabel(label: string, maxChars: number): string {
  return label.length > maxChars ? `${label.slice(0, Math.max(1, maxChars - 1))}…` : label;
}

function allocateTicks(values: number[], tickTotal = 100): number[] {
  const total = values.reduce((sum, value) => sum + value, 0);
  if (total <= 0) return values.map(() => 0);

  const quotas = values.map((value) => (value / total) * tickTotal);
  const ticks = quotas.map(Math.floor);
  let remainder = tickTotal - ticks.reduce((sum, value) => sum + value, 0);
  const order = quotas
    .map((quota, index) => ({ index, fraction: quota - ticks[index] }))
    .sort((a, b) => b.fraction - a.fraction || a.index - b.index);

  for (let index = 0; index < remainder; index += 1) {
    ticks[order[index].index] += 1;
  }
  return ticks;
}

export function mapF5Rows(data: Array<Record<string, unknown>>): SingleValueRow[] {
  return data.flatMap((row) => {
    const topic = readString(row, ["topic"]);
    if (topic) {
      const value = readOptionalNumber(row, ["comment_count"]);
      return value !== undefined ? [{ label: topic, value }] : [];
    }

    const aspect = readString(row, ["aspect"]);
    if (aspect) {
      const value =
        readOptionalNumber(row, ["opportunity_score"]) ??
        readOptionalNumber(row, ["mention_rate"]);
      return value !== undefined ? [{ label: aspect, value }] : [];
    }

    const label = readString(row, ["label"]);
    const value = readOptionalNumber(row, ["count", "rate"]);
    return label && value !== undefined ? [{ label, value }] : [];
  });
}

export function mapF6Rows(data: Array<Record<string, unknown>>): PairedValueRow[] {
  return data.flatMap((row) => {
    const aspect = readString(row, ["aspect"]);
    if (aspect) {
      const first = readOptionalNumber(row, ["positive_rate"]);
      const second = readOptionalNumber(row, ["negative_rate"]);
      return first !== undefined && second !== undefined ? [{ label: aspect, first, second }] : [];
    }

    const platform = readString(row, ["platform"]);
    const first = readOptionalNumber(row, ["comment_count"]);
    const second = readOptionalNumber(row, ["high_intent_comment_count"]);
    return platform && first !== undefined && second !== undefined
      ? [{ label: platform, first, second }]
      : [];
  });
}

export function mapF7Rows(data: Array<Record<string, unknown>>): StackedValueRow[] {
  const fields = [
    ["advantage_count", "优势"],
    ["disadvantage_count", "劣势"],
    ["neutral_count", "中性"],
    ["unclear_count", "不明确"],
  ] as const;

  return data.flatMap((row) => {
    const label = readString(row, ["dimension"]);
    const segments = fields.flatMap(([key, segmentLabel]) => {
      const value = readOptionalNumber(row, [key]);
      return value === undefined ? [] : [{ label: segmentLabel, value }];
    });
    return label && segments.length ? [{ label, segments }] : [];
  });
}

export function mapF8Points(data: Array<Record<string, unknown>>): ScatterPoint[] {
  return data.flatMap((row) => {
    const label = readString(row, ["platform"]);
    const x = readOptionalNumber(row, ["total_volume"]);
    const y = readOptionalNumber(row, ["engagement_per_content"]);
    return label && x !== undefined && y !== undefined ? [{ label, x, y }] : [];
  });
}

export function proportionalLength(value: number, maxValue: number, length: number): number {
  return maxValue > 0 ? (Math.max(0, value) / maxValue) * length : 0;
}

export function boundedUnitCount(value: number, maxValue: number, limit = 80): number {
  if (value <= 0 || maxValue <= 0) return 0;
  return Math.min(limit, Math.max(1, Math.round((value / maxValue) * limit)));
}

function ChartMotionStyles() {
  return (
    <style>{`
      .report-chart-reveal { animation: report-chart-reveal 480ms ease-out both; }
      .report-chart-point:focus-visible { outline: none; }
      .report-chart-point:focus-visible circle {
        stroke: var(--theme-ink);
        stroke-width: 2;
      }
      @keyframes report-chart-reveal { from { opacity: 0; transform: translateY(3px); } }
      @media (prefers-reduced-motion: reduce) {
        .report-chart-reveal { animation: none; }
      }
    `}</style>
  );
}

function polarPoint(cx: number, cy: number, radius: number, degrees: number) {
  const radians = (degrees * Math.PI) / 180;
  return [cx + radius * Math.cos(radians), cy + radius * Math.sin(radians)] as const;
}

export function F3HairlineArea({ chart }: BasicsChartProps) {
  const rows = chart.data.map((row, index) => ({
    label: readLabel(row, index),
    value: readNumber(row, valueKeys),
  }));
  const maxValue = Math.max(1, ...rows.map((row) => row.value));
  const left = 32;
  const right = 376;
  const base = 238;
  const x = (index: number) =>
    rows.length === 1 ? (left + right) / 2 : left + (index / (rows.length - 1)) * (right - left);
  const y = (value: number) => base - (value / maxValue) * 176;
  const peakIndex = rows.reduce(
    (best, row, index) => (row.value > rows[best].value ? index : best),
    0,
  );
  const peak = rows[peakIndex] ?? { label: "", value: 0 };

  return (
    <ReportVisualShell chart={chart}>
      <svg viewBox="0 0 400 280" role="img" aria-label={`${chart.title}趋势图`}>
        <ChartMotionStyles />
        <line x1="24" y1={base} x2="384" y2={base} stroke={theme.border} />
        {rows.map((row, index) => (
          <line
            key={`${row.label}-${index}`}
            className="report-chart-reveal"
            x1={x(index)}
            x2={x(index)}
            y1={base}
            y2={y(row.value)}
            stroke={index === peakIndex ? theme.primary : theme.muted}
            strokeWidth={index === peakIndex ? 1.5 : 0.8}
          />
        ))}
        <path
          d={`M ${rows.map((row, index) => `${x(index)} ${y(row.value)}`).join(" L ")}`}
          fill="none"
          stroke={theme.primary}
          strokeWidth="1.5"
        />
        <circle cx={x(peakIndex)} cy={y(peak.value)} r="4" fill={theme.primary}>
          <title>{`${peak.label}：${peak.value}`}</title>
        </circle>
        <text
          x={x(peakIndex)}
          y={y(peak.value) - 10}
          textAnchor="middle"
          fontSize="10"
          fontWeight="700"
          fill={theme.ink}
        >
          {peak.value}
        </text>
        {rows.map((row, index) =>
          index === 0 || index === rows.length - 1 || index === Math.floor(rows.length / 2) ? (
            <text
              key={`axis-${row.label}-${index}`}
              x={x(index)}
              y={base + 18}
              textAnchor="middle"
              fontSize="9"
              fill={theme.muted}
            >
              {truncateSvgLabel(row.label, 10)}
            </text>
          ) : null,
        )}
      </svg>
    </ReportVisualShell>
  );
}

export function F4TickDonut({ chart }: BasicsChartProps) {
  const rows = chart.data.map((row, index) => ({
    label: readLabel(row, index),
    value: readNumber(row, valueKeys),
  }));
  const tickCounts = allocateTicks(rows.map((row) => row.value));
  const colors = [theme.primary, theme.secondary, theme.ink, theme.muted];
  const tickRows = rows.flatMap((row, segmentIndex) =>
    Array.from({ length: tickCounts[segmentIndex] }, (_, index) => ({
      row,
      segmentIndex,
      tickIndex: tickCounts.slice(0, segmentIndex).reduce((sum, value) => sum + value, 0) + index,
    })),
  );
  const cx = 200;
  const cy = 132;
  const radius = 62;

  return (
    <ReportVisualShell chart={chart}>
      <svg viewBox="0 0 400 280" role="img" aria-label={`${chart.title}百分比环图`}>
        <ChartMotionStyles />
        {tickRows.map(({ row, segmentIndex, tickIndex }) => {
          const angle = tickIndex * 3.6 - 90;
          const [x1, y1] = polarPoint(cx, cy, radius, angle);
          const [x2, y2] = polarPoint(cx, cy, radius + 14, angle);
          return (
            <line
              key={`${row.label}-${tickIndex}`}
              className="report-chart-reveal"
              x1={x1}
              y1={y1}
              x2={x2}
              y2={y2}
              stroke={colors[segmentIndex % colors.length]}
              strokeWidth="1.2"
            />
          );
        })}
        <text x={cx} y={cy} textAnchor="middle" fontSize="24" fontWeight="700" fill={theme.ink}>
          {tickRows.length}
        </text>
        <text x={cx} y={cy + 16} textAnchor="middle" fontSize="8" fill={theme.muted}>
          TICKS · 1 = 1%
        </text>
        {rows.map((row, index) => (
          <g key={`${row.label}-${index}`} transform={`translate(${30 + (index % 2) * 190} ${226 + Math.floor(index / 2) * 22})`}>
            <line x1="0" y1="-3" x2="14" y2="-3" stroke={colors[index % colors.length]} strokeWidth="2" />
            <text x="20" fontSize="9" fill={theme.body}>
              {truncateSvgLabel(row.label, 12)} · {tickCounts[index]}%
            </text>
          </g>
        ))}
      </svg>
    </ReportVisualShell>
  );
}

export function F5TickRows({ chart }: BasicsChartProps) {
  const rows = mapF5Rows(chart.data);
  const maxValue = Math.max(1, ...rows.map((row) => row.value));
  const rowHeight = Math.min(42, 210 / Math.max(1, rows.length));
  const availableWidth = 230;

  return (
    <ReportVisualShell chart={chart} hasData={rows.length > 0}>
      <svg viewBox="0 0 400 280" role="img" aria-label={`${chart.title}横向条形图`}>
        <ChartMotionStyles />
        {rows.map((row, rowIndex) => {
          const y = 30 + rowIndex * rowHeight;
          const width = proportionalLength(row.value, maxValue, availableWidth);
          const ticks = boundedUnitCount(row.value, maxValue);
          return (
            <g key={`${row.label}-${rowIndex}`}>
              <text x="92" y={y + 4} textAnchor="end" fontSize="9" fill={theme.body}>
                {truncateSvgLabel(row.label, 12)}
              </text>
              <line x1="104" y1={y + 8} x2={104 + availableWidth} y2={y + 8} stroke={theme.border} />
              {Array.from({ length: ticks }, (_, tickIndex) => (
                <line
                  key={tickIndex}
                  className="report-chart-reveal"
                  x1={104 + ((tickIndex + 0.5) / Math.max(1, ticks)) * width}
                  x2={104 + ((tickIndex + 0.5) / Math.max(1, ticks)) * width}
                  y1={y + 8}
                  y2={y - 4}
                  stroke={theme.primary}
                />
              ))}
              <text x={112 + width} y={y + 4} fontSize="11" fontWeight="700" fill={theme.ink}>
                {row.value}
              </text>
            </g>
          );
        })}
      </svg>
    </ReportVisualShell>
  );
}

export function F6PairedRungs({ chart }: BasicsChartProps) {
  const rows = mapF6Rows(chart.data);
  const maxValue = Math.max(1, ...rows.flatMap((row) => [row.first, row.second]));
  const base = 230;
  const rungHeight = 165;
  const columnWidth = 320 / Math.max(1, rows.length);

  return (
    <ReportVisualShell chart={chart} hasData={rows.length > 0}>
      <svg viewBox="0 0 400 280" role="img" aria-label={`${chart.title}双系列比较图`}>
        <ChartMotionStyles />
        <line x1="30" y1={base + 4} x2="370" y2={base + 4} stroke={theme.border} />
        {rows.map((row, index) => {
          const center = 40 + columnWidth * index + columnWidth / 2;
          return (
            <g key={`${row.label}-${index}`}>
              {[
                { value: row.first, x: center - 10, color: theme.secondary },
                { value: row.second, x: center + 10, color: theme.primary },
              ].map((series, seriesIndex) => {
                const rungCount = boundedUnitCount(series.value, maxValue);
                const height = proportionalLength(series.value, maxValue, rungHeight);
                return (
                  <g key={seriesIndex}>
                    {Array.from({ length: rungCount }, (_, rungIndex) => {
                      const y = base - ((rungIndex + 0.5) / Math.max(1, rungCount)) * height;
                      return (
                        <line
                          key={rungIndex}
                          className="report-chart-reveal"
                          x1={series.x - 8}
                          x2={series.x + 8}
                          y1={y}
                          y2={y}
                          stroke={series.color}
                        />
                      );
                    })}
                    <text
                      x={series.x}
                      y={base - height - 8}
                      textAnchor="middle"
                      fontSize="9"
                      fontWeight="700"
                      fill={series.color}
                    >
                      {series.value}
                    </text>
                  </g>
                );
              })}
              <text x={center} y={base + 20} textAnchor="middle" fontSize="8" fill={theme.muted}>
                {truncateSvgLabel(row.label, 9)}
              </text>
            </g>
          );
        })}
      </svg>
    </ReportVisualShell>
  );
}

export function F7StackedRungs({ chart }: BasicsChartProps) {
  const rows = mapF7Rows(chart.data);
  const colors = [theme.primary, theme.secondary, theme.ink, theme.muted];
  const rowHeight = Math.min(44, 210 / Math.max(1, rows.length));
  const left = 108;
  const availableWidth = 250;

  return (
    <ReportVisualShell chart={chart} hasData={rows.length > 0}>
      <svg viewBox="0 0 400 280" role="img" aria-label={`${chart.title}堆叠条形图`}>
        <ChartMotionStyles />
        {rows.map((row, rowIndex) => {
          const y = 34 + rowIndex * rowHeight;
          const rowTotal = row.segments.reduce((sum, segment) => sum + segment.value, 0);
          let offset = 0;
          return (
            <g key={`${row.label}-${rowIndex}`}>
              <text x={left - 10} y={y + 3} textAnchor="end" fontSize="9" fill={theme.body}>
                {truncateSvgLabel(row.label, 12)}
              </text>
              <line x1={left} x2={left + availableWidth} y1={y} y2={y} stroke={theme.border} strokeWidth="12" />
              {row.segments.map((segment, segmentIndex) => {
                const segmentWidth =
                  rowTotal === 0 ? 0 : (segment.value / rowTotal) * availableWidth;
                const start = left + offset;
                offset += segmentWidth;
                return (
                  <line
                    key={`${segment.label}-${segmentIndex}`}
                    className="report-chart-reveal"
                    x1={start}
                    x2={start + segmentWidth}
                    y1={y}
                    y2={y}
                    stroke={colors[segmentIndex % colors.length]}
                    strokeWidth="10"
                  >
                    <title>{`${segment.label}：${segment.value} / ${rowTotal}`}</title>
                  </line>
                );
              })}
              <text x={left + availableWidth + 8} y={y + 3} fontSize="9" fontWeight="700" fill={theme.ink}>
                {rowTotal}
              </text>
            </g>
          );
        })}
      </svg>
    </ReportVisualShell>
  );
}

export function F8PlumbScatter({ chart }: BasicsChartProps) {
  const points = mapF8Points(chart.data);
  const xMax = Math.max(1, ...points.map((point) => point.x));
  const yMax = Math.max(1, ...points.map((point) => point.y));
  const left = 48;
  const right = 368;
  const top = 34;
  const base = 232;
  const mapX = (value: number) => left + (value / xMax) * (right - left);
  const mapY = (value: number) => base - (value / yMax) * (base - top);

  return (
    <ReportVisualShell chart={chart} hasData={points.length > 0}>
      <svg viewBox="0 0 400 280" role="img" aria-label={`${chart.title}散点图`}>
        <ChartMotionStyles />
        {Array.from({ length: 21 }, (_, index) => {
          const x = left + (index / 20) * (right - left);
          return (
            <line
              key={index}
              x1={x}
              x2={x}
              y1={base}
              y2={base - (index % 5 === 0 ? 7 : 4)}
              stroke={theme.border}
            />
          );
        })}
        <line x1={left - 6} x2={right + 6} y1={base} y2={base} stroke={theme.border} />
        {points.map((point, index) => {
          const x = mapX(point.x);
          const y = mapY(point.y);
          return (
            <g
              key={`${point.label}-${index}`}
              tabIndex={0}
              role="img"
              aria-label={`${point.label}，X ${point.x}，Y ${point.y}`}
              className="report-chart-point report-chart-reveal"
            >
              <title>{`${point.label}：X ${point.x} · Y ${point.y}`}</title>
              <line x1={x} x2={x} y1={base} y2={y} stroke={theme.muted} strokeWidth="0.7" />
              <circle cx={x} cy={y} r="4" fill={theme.primary} />
              <text
                x={x}
                y={y - 9}
                textAnchor="middle"
                fontSize="8"
                fontWeight="700"
                fill={theme.ink}
              >
                {truncateSvgLabel(point.label, 9)}
              </text>
            </g>
          );
        })}
      </svg>
    </ReportVisualShell>
  );
}
