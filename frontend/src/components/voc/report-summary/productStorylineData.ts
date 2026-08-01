import type { ReportVisualChart } from "@/components/voc/report-visuals/types";
import type { ReportStoryChapter, ReportStoryline } from "@/types/vocMarket";

const CHAPTER_IDS: ReportStoryChapter["chapter_id"][] = [
  "focus",
  "attitude",
  "comparison",
  "evidence",
];

export type ProductStorylineMetric = {
  label: string;
  value: string;
};

export type ProductStorylineEvidence = {
  commentId: string;
  commentText: string;
  dimension: string;
  target: string;
  resultBucket?: string;
};

export type ProductStorylineView = {
  headline: string;
  lead: string;
  chapters: Array<{
    chapterId: ReportStoryChapter["chapter_id"];
    title: string;
    conclusion: string;
    body: string;
    metrics: ProductStorylineMetric[];
    evidence: ProductStorylineEvidence[];
  }>;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function text(value: unknown): string | undefined {
  return typeof value === "string" && value.trim() ? value.trim() : undefined;
}

function number(value: unknown): number | undefined {
  return typeof value === "number" && Number.isFinite(value) && value >= 0
    ? value
    : undefined;
}

function formatted(value: number): string {
  return Number.isInteger(value) ? String(value) : String(Math.round(value * 10) / 10);
}

function percent(value: number): string {
  return `${formatted(value)}%`;
}

function chartRows(charts: ReportVisualChart[], templateId: ReportVisualChart["template_id"]) {
  return charts.find((chart) => chart.template_id === templateId)?.data ?? [];
}

function focusMetrics(charts: ReportVisualChart[]): ProductStorylineMetric[] {
  return chartRows(charts, "P1").flatMap((row) => {
    const aspect = text(row.aspect);
    const mentionRate = number(row.mention_rate);
    return aspect && mentionRate !== undefined
      ? [{ label: `${aspect}提及率`, value: percent(mentionRate) }]
      : [];
  }).slice(0, 3);
}

const OPPORTUNITY_LABELS: Record<string, string> = {
  surprise: "惊喜点",
  pain: "风险点",
  conversion: "机会点",
};

function opportunityMetrics(
  charts: ReportVisualChart[],
  pointType?: string,
): ProductStorylineMetric[] {
  return chartRows(charts, "P3").flatMap((row) => {
    const type = text(row.point_type);
    const aspect = text(row.aspect);
    const score = number(row.opportunity_score);
    if (!type || !OPPORTUNITY_LABELS[type] || (pointType && type !== pointType) || !aspect || score === undefined) {
      return [];
    }
    return [{ label: `${OPPORTUNITY_LABELS[type]} · ${aspect}`, value: formatted(score) }];
  }).slice(0, 3);
}

function opportunitySummaryMetrics(charts: ReportVisualChart[]): ProductStorylineMetric[] {
  return ["surprise", "pain", "conversion"]
    .flatMap((pointType) => opportunityMetrics(charts, pointType).slice(0, 1));
}

function pkoMetrics(charts: ReportVisualChart[]): ProductStorylineMetric[] {
  return chartRows(charts, "P4").flatMap((row) => {
    const dimension = text(row.dimension);
    if (!dimension) return [];
    const counts = ["advantage_count", "disadvantage_count", "neutral_count", "unclear_count"]
      .map((key) => number(row[key]))
      .filter((value): value is number => value !== undefined);
    return counts.length
      ? [{ label: `${dimension}对比`, value: formatted(counts.reduce((sum, value) => sum + value, 0)) }]
      : [];
  }).slice(0, 3);
}

const METRIC_RESOLVERS: Record<string, (charts: ReportVisualChart[]) => ProductStorylineMetric[]> = {
  "product_focus.summary": (charts) => focusMetrics(charts).slice(0, 1),
  "product_focus.aspects": focusMetrics,
  "product_opportunity.summary": opportunitySummaryMetrics,
  "product_opportunity.surprise_points": (charts) => opportunityMetrics(charts, "surprise"),
  "product_opportunity.pain_points": (charts) => opportunityMetrics(charts, "pain"),
  "product_opportunity.conversion_points": (charts) => opportunityMetrics(charts, "conversion"),
  "pko.summary": (charts) => pkoMetrics(charts).slice(0, 1),
  "pko.dimension_result_matrix": pkoMetrics,
};

function evidenceById(charts: ReportVisualChart[]) {
  const records = new Map<string, ProductStorylineEvidence>();
  for (const row of chartRows(charts, "L6")) {
    const commentId = text(row.comment_id);
    const commentText = text(row.comment_text);
    const dimension = text(row.dimension);
    const target = text(row.target);
    if (!commentId || !commentText || !dimension || !target || records.has(commentId)) continue;
    records.set(commentId, {
      commentId,
      commentText,
      dimension,
      target,
      resultBucket: text(row.result_bucket),
    });
  }
  return records;
}

export function isReportStoryline(value: unknown): value is ReportStoryline {
  if (!isRecord(value) || typeof value.headline !== "string" || typeof value.lead !== "string") return false;
  if (!Array.isArray(value.chapters) || value.chapters.length !== CHAPTER_IDS.length) return false;
  return value.chapters.every((chapter, index) => (
    isRecord(chapter)
    && chapter.chapter_id === CHAPTER_IDS[index]
    && Boolean(text(chapter.title))
    && Boolean(text(chapter.conclusion))
    && typeof chapter.body === "string"
    && Array.isArray(chapter.metric_refs)
    && chapter.metric_refs.length <= 4
    && chapter.metric_refs.every((ref) => typeof ref === "string")
    && Array.isArray(chapter.evidence_refs)
    && chapter.evidence_refs.length <= 2
    && chapter.evidence_refs.every((ref) => typeof ref === "string")
  ));
}

export function buildProductStorylineView(
  storyline: unknown,
  charts: ReportVisualChart[],
): ProductStorylineView | null {
  if (!isReportStoryline(storyline)) return null;
  const evidence = evidenceById(charts);
  return {
    headline: storyline.headline,
    lead: storyline.lead,
    chapters: storyline.chapters.map((chapter) => ({
      chapterId: chapter.chapter_id,
      title: chapter.title,
      conclusion: chapter.conclusion,
      body: chapter.body,
      metrics: chapter.metric_refs.flatMap((ref) => METRIC_RESOLVERS[ref]?.(charts) ?? []),
      evidence: chapter.evidence_refs.flatMap((commentId) => {
        const record = evidence.get(commentId);
        return record ? [record] : [];
      }),
    })),
  };
}
