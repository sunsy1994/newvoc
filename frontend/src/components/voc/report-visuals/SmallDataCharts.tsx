import { reportChartTheme as theme } from "./chartTheme";
import { ReportVisualShell } from "./ReportVisualShell";
import type { ReportVisualChart } from "./types";

type SmallDataChartProps = {
  chart: ReportVisualChart;
};

type SentimentRates = {
  positiveRate: number;
  neutralRate: number;
  negativeRate: number;
};

type L15Row = SentimentRates & {
  aspect: string;
};

function readString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function readRate(value: unknown): number | undefined {
  if (value === null || value === undefined || (typeof value === "string" && !value.trim())) {
    return undefined;
  }
  const rate = typeof value === "number" ? value : Number(value);
  return Number.isFinite(rate) && rate >= 0 && rate <= 100 ? rate : undefined;
}

function formatRate(rate: number): string {
  const rounded = Math.round(rate * 100) / 100;
  return `${Number.isInteger(rounded) ? rounded : rounded.toFixed(2).replace(/0$/, "")}%`;
}

export function normalizeL15Rows(data: Array<Record<string, unknown>>): L15Row[] {
  return data.flatMap((row) => {
    const aspect = readString(row.aspect);
    const positiveRate = readRate(row.positive_rate);
    const negativeRate = readRate(row.negative_rate);
    if (!aspect || positiveRate === undefined || negativeRate === undefined || positiveRate + negativeRate > 100) {
      return [];
    }
    return [{ aspect, positiveRate, neutralRate: 100 - positiveRate - negativeRate, negativeRate }];
  });
}

export function allocateSentimentTicks(
  rates: SentimentRates,
  tickCount = 20,
): { positive: number; neutral: number; negative: number } {
  const safeTickCount = Number.isFinite(tickCount) ? Math.max(0, Math.floor(tickCount)) : 20;
  const entries = [
    ["positive", rates.positiveRate],
    ["neutral", rates.neutralRate],
    ["negative", rates.negativeRate],
  ] as const;
  const exact = entries.map(([key, value], index) => ({ key, index, exact: (value / 100) * safeTickCount }));
  const base = exact.map((item) => ({ ...item, count: Math.floor(item.exact) }));
  let remaining = safeTickCount - base.reduce((sum, item) => sum + item.count, 0);
  base
    .sort((left, right) => (right.exact - right.count) - (left.exact - left.count) || right.index - left.index)
    .forEach((item) => {
      if (remaining > 0) {
        item.count += 1;
        remaining -= 1;
      }
    });
  return Object.fromEntries(base.map(({ key, count }) => [key, count])) as {
    positive: number;
    neutral: number;
    negative: number;
  };
}

function sentimentColor(state: "positive" | "neutral" | "negative"): string {
  if (state === "positive") return theme.primary;
  if (state === "negative") return "var(--voc-chart-6)";
  return theme.muted;
}

export function L15BallotTally({ chart }: SmallDataChartProps) {
  const rows = normalizeL15Rows(chart.data);
  const height = Math.max(320, 68 + rows.length * 78);

  return (
    <ReportVisualShell chart={chart} hasData={rows.length > 0}>
      <svg viewBox={`0 0 400 ${height}`} role="img" aria-label={`${chart.title}情感计票图`}>
        <g aria-label="图例：正向、中性、负向">
          {(["positive", "neutral", "negative"] as const).map((state, index) => (
            <g key={state} transform={`translate(${132 + index * 74} 16)`}>
              <circle r="3" fill={sentimentColor(state)} />
              <text x="7" y="3" fontSize="7" fill={theme.body}>
                {{ positive: "正向", neutral: "中性", negative: "负向" }[state]}
              </text>
            </g>
          ))}
        </g>
        {rows.map((row, rowIndex) => {
          const base = 54 + rowIndex * 78;
          const allocation = allocateSentimentTicks(row);
          const states = [
            ...Array.from({ length: allocation.positive }, () => "positive" as const),
            ...Array.from({ length: allocation.neutral }, () => "neutral" as const),
            ...Array.from({ length: allocation.negative }, () => "negative" as const),
          ];
          return (
            <g key={row.aspect} aria-label={`${row.aspect}：正向${formatRate(row.positiveRate)}，中性${formatRate(row.neutralRate)}，负向${formatRate(row.negativeRate)}`}>
              <title>{`${row.aspect}：正向 ${formatRate(row.positiveRate)}，中性 ${formatRate(row.neutralRate)}，负向 ${formatRate(row.negativeRate)}`}</title>
              <text x="20" y={base - 16} fontSize="8" fontWeight="800" fill={theme.ink}>
                {row.aspect}
              </text>
              <text x="20" y={base - 5} fontSize="7" fill={theme.muted}>
                正 {formatRate(row.positiveRate)} · 中 {formatRate(row.neutralRate)} · 负 {formatRate(row.negativeRate)}
              </text>
              <line x1="20" y1={base} x2="380" y2={base} stroke={theme.border} strokeWidth="0.7" />
              {states.map((state, tickIndex) => {
                const x = 20 + tickIndex * 18.2;
                const height = state === "neutral" ? 9 : 15;
                return (
                  <line
                    key={tickIndex}
                    data-sentiment-tick={`${row.aspect}-${tickIndex}`}
                    x1={x}
                    x2={x}
                    y1={base}
                    y2={base - height}
                    stroke={sentimentColor(state)}
                    strokeWidth={state === "neutral" ? "0.8" : "1.4"}
                  />
                );
              })}
              {Array.from({ length: 2 }, (_, markerIndex) => (
                <circle key={markerIndex} cx={20 + markerIndex * 182} cy={base + 4} r="1" fill={theme.border} />
              ))}
            </g>
          );
        })}
        <text x="200" y={height - 12} textAnchor="middle" fontSize="7" fontWeight="600" fill={theme.muted}>
          一格 = 5% · 每行 20 格
        </text>
      </svg>
    </ReportVisualShell>
  );
}
