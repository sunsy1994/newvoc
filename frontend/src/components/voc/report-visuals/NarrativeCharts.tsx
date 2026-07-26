"use client";

import { useId, useState } from "react";

import { reportChartTheme as theme } from "./chartTheme";
import { ReportVisualShell } from "./ReportVisualShell";
import type { ReportVisualChart } from "./types";

type NarrativeChartProps = {
  chart: ReportVisualChart;
};

type ResultBucket = "advantage" | "disadvantage" | "neutral" | "unclear";

export type PkoRecord = {
  comment_id: string;
  target: string;
  dimension: string;
  result_bucket: ResultBucket;
  comment_text: string;
};

type FunnelStage = {
  label: string;
  count: number;
};

type HundredGroup = {
  key: string;
  label: string;
  count: number;
  is_remainder: boolean;
};

const RESULT_BUCKETS = new Set<ResultBucket>([
  "advantage",
  "disadvantage",
  "neutral",
  "unclear",
]);

const RISK_COLOR = "var(--voc-chart-6)";

export function resultBucketLabel(bucket: ResultBucket): string {
  return {
    advantage: "优势",
    disadvantage: "劣势",
    neutral: "中性",
    unclear: "不明确",
  }[bucket];
}

export function isL12ActivationKey(key: string): boolean {
  return key === "Enter" || key === " ";
}

function readString(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function readNumber(value: unknown): number | undefined {
  if (value === null || value === undefined || (typeof value === "string" && !value.trim())) {
    return undefined;
  }
  const number = typeof value === "number" ? value : Number(value);
  return Number.isFinite(number) && number >= 0 ? number : undefined;
}

function truncateLabel(label: string, maxChars: number): string {
  return label.length > maxChars ? `${label.slice(0, maxChars - 1)}…` : label;
}

function unique(values: string[]): string[] {
  return values.filter((value, index) => values.indexOf(value) === index);
}

function narrativeMotionStyles() {
  return (
    <style>{`
      .report-narrative-reveal { animation: report-narrative-reveal 520ms ease-out both; }
      .report-l12-record:focus-visible { outline: none; }
      .report-l12-record:focus-visible path { stroke-width: 2.4; opacity: 1; }
      @keyframes report-narrative-reveal {
        from { opacity: 0; transform: translateY(3px); }
      }
      @media (prefers-reduced-motion: reduce) {
        .report-narrative-reveal { animation: none; }
      }
    `}</style>
  );
}

export function mapL12Records(data: Array<Record<string, unknown>>): PkoRecord[] {
  return data.flatMap((row) => {
    const comment_id = readString(row.comment_id);
    const target = readString(row.target);
    const dimension = readString(row.dimension);
    const comment_text = readString(row.comment_text);
    const bucket = readString(row.result_bucket) ?? readString(row.result);
    if (
      !comment_id ||
      !target ||
      !dimension ||
      !comment_text ||
      !bucket ||
      !RESULT_BUCKETS.has(bucket as ResultBucket)
    ) {
      return [];
    }
    return [
      {
        comment_id,
        target,
        dimension,
        result_bucket: bucket as ResultBucket,
        comment_text,
      },
    ];
  });
}

export type L6Cluster = {
  dimension: string;
  totalCount: number;
  targets: Array<{
    target: string;
    count: number;
    records: PkoRecord[];
  }>;
};

export function bubbleRadius(count: number, maxCount: number): number {
  const safeMax = Math.max(1, maxCount);
  return Math.min(30, Math.max(10, 30 * Math.sqrt(Math.max(0, count) / safeMax)));
}

function mapL6Records(data: Array<Record<string, unknown>>): PkoRecord[] {
  return data.flatMap((row) => {
    const comment_id = readString(row.comment_id);
    const target = readString(row.target);
    const dimension = readString(row.dimension);
    const comment_text = readString(row.comment_text);
    const bucket = readString(row.result_bucket) ?? readString(row.result);
    if (!comment_id || !target || !dimension || !comment_text) return [];
    return [{
      comment_id,
      target,
      dimension,
      comment_text,
      result_bucket: RESULT_BUCKETS.has(bucket as ResultBucket)
        ? bucket as ResultBucket
        : "unclear",
    }];
  });
}

export function mapL6Clusters(data: Array<Record<string, unknown>>): L6Cluster[] {
  const byDimension = new Map<string, Map<string, PkoRecord[]>>();
  for (const record of mapL6Records(data)) {
    const targets = byDimension.get(record.dimension) ?? new Map<string, PkoRecord[]>();
    const records = targets.get(record.target) ?? [];
    records.push(record);
    targets.set(record.target, records);
    byDimension.set(record.dimension, targets);
  }
  return [...byDimension.entries()]
    .map(([dimension, targets]) => {
      const targetRows = [...targets.entries()]
        .map(([target, records]) => ({ target, count: records.length, records }))
        .sort((left, right) => right.count - left.count || left.target.localeCompare(right.target, "zh-CN"));
      return {
        dimension,
        totalCount: targetRows.reduce((sum, target) => sum + target.count, 0),
        targets: targetRows,
      };
    })
    .sort((left, right) => right.totalCount - left.totalCount || left.dimension.localeCompare(right.dimension, "zh-CN"));
}

function l6ClusterCenter(index: number, total: number): [number, number] {
  if (total === 1) return [420, 160];
  const angle = (index / total) * Math.PI * 2 - Math.PI / 2;
  return [420 + Math.cos(angle) * 178, 160 + Math.sin(angle) * 98];
}

export function L6ClusterField({ chart }: NarrativeChartProps) {
  const clusters = mapL6Clusters(chart.data);
  const [activeTarget, setActiveTarget] = useState<string | null>(null);
  const maxCount = Math.max(1, ...clusters.flatMap((cluster) => cluster.targets.map((target) => target.count)));

  return (
    <ReportVisualShell chart={chart} hasData={clusters.length > 0}>
      <svg viewBox="0 0 840 320" role="img" aria-label={`${chart.title}产品对比点簇图`}>
        {narrativeMotionStyles()}
        {clusters.map((cluster, clusterIndex) => {
          const [centerX, centerY] = l6ClusterCenter(clusterIndex, clusters.length);
          return (
            <g key={cluster.dimension}>
              {cluster.targets.map((target, targetIndex) => {
                const key = `${cluster.dimension}-${target.target}`;
                const angle = ((targetIndex * 137.508 + clusterIndex * 41) * Math.PI) / 180;
                const distance = 54 + (targetIndex % 2) * 18;
                const x = centerX + Math.cos(angle) * distance;
                const y = centerY + Math.sin(angle) * distance;
                const radius = bubbleRadius(target.count, maxCount);
                const isActive = activeTarget === key;
                return (
                  <g
                    key={key}
                    role="button"
                    tabIndex={0}
                    aria-label={`${cluster.dimension}与${target.target}对比${target.count}次`}
                    onFocus={() => setActiveTarget(key)}
                    onMouseEnter={() => setActiveTarget(key)}
                    onKeyDown={(event) => {
                      if (isL12ActivationKey(event.key)) {
                        event.preventDefault();
                        setActiveTarget(key);
                      }
                    }}
                  >
                    <title>{`${cluster.dimension} · ${target.target} · ${target.count} 次`}</title>
                    <path
                      d={`M ${centerX} ${centerY} Q ${(centerX + x) / 2} ${(centerY + y) / 2 - 16} ${x} ${y}`}
                      fill="none"
                      stroke={theme.border}
                      strokeWidth="0.9"
                      strokeDasharray="2 4"
                    />
                    <circle
                      className="report-narrative-reveal"
                      cx={x}
                      cy={y}
                      r={radius}
                      fill={theme.secondary}
                      opacity={activeTarget && !isActive ? 0.42 : 0.9}
                      stroke={isActive ? theme.ink : "none"}
                      strokeWidth="1.5"
                    />
                    <text x={x} y={y + 3} textAnchor="middle" fontSize="8" fontWeight="800" fill={theme.white}>
                      {target.count}
                    </text>
                    <text x={x} y={y + radius + 11} textAnchor="middle" fontSize="7.5" fontWeight="700" fill={theme.body}>
                      {truncateLabel(target.target, 9)} · {target.count}
                    </text>
                  </g>
                );
              })}
              <circle cx={centerX} cy={centerY} r="6.5" fill={theme.ink} />
              <text x={centerX} y={centerY + 31} textAnchor="middle" fontSize="8" fontWeight="800" fill={theme.ink}>
                {truncateLabel(cluster.dimension, 10)} · {cluster.totalCount}
              </text>
            </g>
          );
        })}
      </svg>
      <ul className="sr-only">
        {clusters.flatMap((cluster) => cluster.targets.flatMap((target) => target.records.map((record) => (
          <li key={`${cluster.dimension}-${target.target}-${record.comment_id}`}>
            {cluster.dimension}；{target.target}；{record.comment_text}
          </li>
        ))))}
      </ul>
    </ReportVisualShell>
  );
}

function bucketColor(bucket: ResultBucket): string {
  if (bucket === "advantage") return theme.primary;
  if (bucket === "disadvantage") return RISK_COLOR;
  if (bucket === "neutral") return theme.secondary;
  return theme.muted;
}

function groupY(index: number, total: number): number {
  return total <= 1 ? 154 : 34 + (index / (total - 1)) * 240;
}

export function L12TypeColonnade({ chart }: NarrativeChartProps) {
  const records = mapL12Records(chart.data);
  const targets = unique(records.map((record) => record.target));
  const dimensions = unique(records.map((record) => record.dimension));
  const descriptionBaseId = useId();
  const [activeIndex, setActiveIndex] = useState(0);
  const activeRecord = records[activeIndex] ?? records[0];
  const displayedCount =
    typeof chart.meta.displayed_count === "number"
    && Number.isSafeInteger(chart.meta.displayed_count)
    && chart.meta.displayed_count >= 0
      ? chart.meta.displayed_count
      : records.length;
  const totalCount =
    typeof chart.meta.total_count === "number"
    && Number.isSafeInteger(chart.meta.total_count)
    && chart.meta.total_count >= displayedCount
      ? chart.meta.total_count
      : displayedCount;

  return (
    <ReportVisualShell chart={chart} hasData={records.length > 0}>
      <svg viewBox="0 0 400 310" role="list" aria-label={`${chart.title}对比关系记录`}>
        {narrativeMotionStyles()}
        {targets.map((target, index) => {
          const y = groupY(index, targets.length);
          const count = records.filter((record) => record.target === target).length;
          return (
            <g key={target}>
              <text x="112" y={y + 3} textAnchor="end" fontSize="8" fill={theme.body}>
                {truncateLabel(target, 12)} · {count}
              </text>
              <rect x="117" y={y - 2} width="4" height="4" fill={theme.muted} />
            </g>
          );
        })}
        {records.map((record, index) => {
          const sourceY = groupY(targets.indexOf(record.target), targets.length);
          const targetY = groupY(dimensions.indexOf(record.dimension), dimensions.length);
          const offset = ((index % 5) - 2) * 1.1;
          const resultLabel = resultBucketLabel(record.result_bucket);
          const descriptionId = `${descriptionBaseId}-record-${index}`;
          const copy = `${record.target}，${record.dimension}，结果：${resultLabel}，${record.comment_text}`;
          return (
            <g
              key={`${record.comment_id}-${index}`}
              className="report-l12-record report-narrative-reveal"
              tabIndex={0}
              role="listitem"
              aria-label={copy}
              aria-describedby={descriptionId}
              onFocus={() => setActiveIndex(index)}
              onMouseEnter={() => setActiveIndex(index)}
              onKeyDown={(event) => {
                if (isL12ActivationKey(event.key)) {
                  event.preventDefault();
                  setActiveIndex(index);
                }
              }}
            >
              <title>{copy}</title>
              <path
                data-pko-record={record.comment_id}
                d={`M 123 ${sourceY + offset} C 196 ${sourceY + offset} 220 ${targetY + offset} 288 ${targetY + offset}`}
                fill="none"
                stroke={bucketColor(record.result_bucket)}
                strokeWidth="0.9"
                opacity="0.72"
              />
            </g>
          );
        })}
        {dimensions.map((dimension, index) => {
          const y = groupY(index, dimensions.length);
          const count = records.filter((record) => record.dimension === dimension).length;
          return (
            <g key={dimension}>
              <circle
                cx="293"
                cy={y}
                r={Math.min(9, 2.8 + count * 0.7)}
                fill={count >= 4 ? theme.primary : theme.secondary}
              />
              <text x={302 + Math.min(8, count)} y={y + 3} fontSize="8" fontWeight="700" fill={theme.ink}>
                {truncateLabel(dimension, 10)} · {count}
              </text>
            </g>
          );
        })}
      </svg>

      <p className="text-xs font-medium" style={{ color: theme.muted }}>
        展示 {displayedCount} / 总计 {totalCount} 条
      </p>
      {activeRecord ? (
        <div
          className="mt-3 rounded-xl border px-4 py-3"
          style={{ borderColor: theme.border, background: theme.panel }}
          aria-live="polite"
        >
          <p className="text-xs font-semibold" style={{ color: theme.ink }}>
            {activeRecord.target} → {activeRecord.dimension}
          </p>
          <p className="mt-1 text-xs font-semibold" style={{ color: theme.body }}>
            结果：{resultBucketLabel(activeRecord.result_bucket)}
          </p>
          <p className="mt-1 text-sm leading-6" style={{ color: theme.body }}>
            {activeRecord.comment_text}
          </p>
        </div>
      ) : null}
      <ul className="sr-only">
        {records.map((record, index) => (
          <li
            id={`${descriptionBaseId}-record-${index}`}
            key={`copy-${record.comment_id}-${index}`}
          >
            {record.target}；{record.dimension}；结果：
            {resultBucketLabel(record.result_bucket)}；{record.comment_text}
          </li>
        ))}
      </ul>
    </ReportVisualShell>
  );
}

export function mapL13Stages(data: Array<Record<string, unknown>>): FunnelStage[] {
  const stages = data.flatMap((row) => {
    const label = readString(row.stage);
    const count = readNumber(row.count);
    return label && count !== undefined ? [{ label, count }] : [];
  });
  if (!stages.length || stages[0].count <= 0) return [];
  return stages.some((stage, index) => index > 0 && stage.count > stages[index - 1].count)
    ? []
    : stages;
}

export function stageWidth(count: number, firstCount: number): number {
  return firstCount > 0 ? (Math.max(0, count) / firstCount) * 290 : 0;
}

export function L13HourglassStream({ chart }: NarrativeChartProps) {
  const stages = mapL13Stages(chart.data);
  const firstCount = stages[0]?.count ?? 0;
  const centerX = 185;
  const stageY = (index: number) => 34 + index * 64;

  return (
    <ReportVisualShell chart={chart} hasData={stages.length > 0}>
      <svg viewBox="0 0 400 280" role="img" aria-label={`${chart.title}阶段漏斗图`}>
        {narrativeMotionStyles()}
        {stages.map((stage, stageIndex) => {
          const y = stageY(stageIndex);
          const width = stageWidth(stage.count, firstCount);
          const halfWidth = width / 2;
          const tickCount = stage.count > 0 ? Math.max(1, Math.round((width / 290) * 80)) : 0;
          const nextStage = stages[stageIndex + 1];
          const nextHalfWidth = nextStage
            ? stageWidth(nextStage.count, firstCount) / 2
            : 0;
          return (
            <g key={`${stage.label}-${stageIndex}`}>
              {Array.from({ length: tickCount }, (_, tickIndex) => {
                const x =
                  centerX - halfWidth + ((tickIndex + 0.5) / Math.max(1, tickCount)) * width;
                return (
                  <line
                    key={`tick-${tickIndex}`}
                    className="report-narrative-reveal"
                    x1={x}
                    x2={x}
                    y1={y - 6}
                    y2={y + 6}
                    stroke={theme.ink}
                    strokeWidth="0.8"
                    opacity={0.55 + (tickIndex % 4) * 0.1}
                  />
                );
              })}
              {nextStage
                ? Array.from({ length: 34 }, (_, threadIndex) => {
                    const fraction = (threadIndex + 0.5) / 34;
                    const topX = centerX - halfWidth * 0.94 + fraction * halfWidth * 1.88;
                    const bottomX =
                      centerX - nextHalfWidth * 0.94 + fraction * nextHalfWidth * 1.88;
                    return (
                      <path
                        key={`thread-${threadIndex}`}
                        className="report-narrative-reveal"
                        d={`M ${topX} ${y + 8} C ${topX} ${y + 34} ${bottomX} ${stageY(stageIndex + 1) - 34} ${bottomX} ${stageY(stageIndex + 1) - 8}`}
                        fill="none"
                        stroke={theme.border}
                        strokeWidth="0.5"
                        opacity="0.45"
                      />
                    );
                  })
                : null}
              {nextStage ? (
                <text
                  x="26"
                  y={(y + stageY(stageIndex + 1)) / 2 + 3}
                  fontSize="8.5"
                  fontWeight="800"
                  fill={theme.muted}
                >
                  {stage.count > 0 ? Math.round((nextStage.count / stage.count) * 100) : 0}%
                </text>
              ) : null}
              <line
                x1={centerX + halfWidth + 6}
                x2="340"
                y1={y}
                y2={y}
                stroke={theme.border}
                strokeWidth="0.8"
              />
              <text x="344" y={y - 1} fontSize="7.5" fontWeight="700" fill={theme.body}>
                {truncateLabel(stage.label, 8)}
              </text>
              <text x="344" y={y + 11} fontSize="9.5" fontWeight="800" fill={theme.ink}>
                {stage.count.toLocaleString("zh-CN")}
              </text>
            </g>
          );
        })}
      </svg>
      <ol className="sr-only">
        {stages.map((stage, index) => (
          <li key={`stage-copy-${stage.label}-${index}`}>
            {stage.label}：{stage.count}，占首阶段 {((stage.count / firstCount) * 100).toFixed(1)}%
          </li>
        ))}
      </ol>
    </ReportVisualShell>
  );
}

export function allocateHundredCells(
  data: Array<Record<string, unknown>>,
): HundredGroup[] {
  const groups = data.flatMap((row) => {
    const label = readString(row.label);
    const percentage =
      readNumber(row.percentage) ?? readNumber(row.percent) ?? readNumber(row.rate);
    return label && percentage !== undefined
      ? [{ key: label, label, percentage }]
      : [];
  });
  const percentageTotal = groups.reduce((sum, group) => sum + group.percentage, 0);
  if (!groups.length || Math.abs(percentageTotal - 100) > 1.01) return [];

  const businessGroups = groups.map(({ key, label, percentage }) => ({
    key,
    label,
    count: Math.floor(percentage + 1e-9),
    is_remainder: false,
  }));
  const businessTotal = businessGroups.reduce((sum, group) => sum + group.count, 0);
  if (businessTotal > 100) return [];
  const remainder = 100 - businessTotal;
  return remainder
    ? [
        ...businessGroups,
        {
          key: "rounding_remainder",
          label: "舍入余量",
          count: remainder,
          is_remainder: true,
        },
      ]
    : businessGroups;
}

function hundredColor(group: HundredGroup): string {
  if (group.is_remainder) return theme.border;
  if (/负|劣|消极/.test(group.label)) return RISK_COLOR;
  if (/正|优|积极/.test(group.label)) return theme.primary;
  if (/中性|未明确|不明确/.test(group.label)) return theme.muted;
  return theme.secondary;
}

function clusterCenters(total: number): Array<[number, number]> {
  if (total === 1) return [[200, 150]];
  if (total === 2) return [[130, 155], [270, 155]];
  if (total === 3) return [[126, 128], [274, 116], [200, 238]];
  if (total === 4) return [[132, 140], [276, 116], [186, 252], [322, 238]];
  return Array.from({ length: total }, (_, index) => {
    const angle = (index / total) * Math.PI * 2 - Math.PI / 2;
    return [200 + Math.cos(angle) * 126, 160 + Math.sin(angle) * 104];
  });
}

export function L14HundredField({ chart }: NarrativeChartProps) {
  const groups = allocateHundredCells(chart.data);
  const centers = clusterCenters(groups.length);
  const cells = groups.flatMap((group, groupIndex) =>
    Array.from({ length: group.count }, (_, cellIndex) => ({
      group,
      groupIndex,
      cellIndex,
    })),
  );

  return (
    <ReportVisualShell chart={chart} hasData={cells.length === 100}>
      <svg viewBox="0 0 400 320" role="img" aria-label={`${chart.title}百分比百点图`}>
        {narrativeMotionStyles()}
        {centers.slice(1).map((center, index) => (
          <line
            key={`constellation-${index}`}
            x1={centers[index][0]}
            y1={centers[index][1]}
            x2={center[0]}
            y2={center[1]}
            stroke={theme.border}
            strokeWidth="0.7"
            strokeDasharray="2 5"
          />
        ))}
        {groups.map((group, groupIndex) => {
          const [centerX, centerY] = centers[groupIndex];
          const edge = group.count ? 4 + Math.sqrt(group.count - 1) * 6.35 : 0;
          return (
            <g key={`${group.key}-${groupIndex}`} data-hundred-group={group.key}>
              {Array.from({ length: group.count }, (_, cellIndex) => {
                const angle = ((cellIndex * 137.508 + groupIndex * 55) * Math.PI) / 180;
                const radius =
                  4 +
                  Math.sqrt(cellIndex) * 5.9 +
                  ((cellIndex * 17 + groupIndex * 13) % 7) * 0.38;
                const x = centerX + Math.cos(angle) * radius;
                const y = centerY + Math.sin(angle) * radius;
                return (
                  <circle
                    key={cellIndex}
                    data-hundred-cell={`${group.key}-${cellIndex}`}
                    className="report-narrative-reveal"
                    cx={x}
                    cy={y}
                    r={1.6 + ((cellIndex + groupIndex) % 4) * 0.35}
                    fill={hundredColor(group)}
                    opacity="0.9"
                  >
                    <title>{`${group.label}：第 ${cellIndex + 1} / ${group.count} 格`}</title>
                  </circle>
                );
              })}
              <circle cx={centerX} cy={centerY} r="2.4" fill={theme.ink} />
              <text
                x={centerX}
                y={centerY + edge + 14}
                textAnchor="middle"
                fontSize="8"
                fontWeight="800"
                fill={theme.ink}
              >
                {truncateLabel(group.label, 9)} · {group.count}
              </text>
            </g>
          );
        })}
        <text x="200" y="312" textAnchor="middle" fontSize="7" fontWeight="600" fill={theme.muted}>
          一格 = 一个百分点 · 合计 100
        </text>
      </svg>
      <ul className="sr-only">
        {groups.map((group) => (
          <li key={`hundred-copy-${group.key}`}>
            {group.label}：{group.count}%
          </li>
        ))}
      </ul>
    </ReportVisualShell>
  );
}
