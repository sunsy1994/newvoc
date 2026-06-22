"use client";

import { HelpCircle, MoreHorizontal, Search, SignalHigh, UserRound, UserRoundCheck, UsersRound, X } from "lucide-react";
import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";

import { apiBaseUrl } from "@/config/navigation";
import type {
  SalesLeadProfileDistributionItem,
  SalesLeadProfileSegment,
  SalesLeadQuality,
  SalesLeadSankeyLink,
  SalesLeadSankeyNode,
  SalesLeadUserInsightProfile,
} from "@/types/vocMarket";

type SalesLeadQualityStoryCardProps = {
  quality?: SalesLeadQuality;
  eventId?: string;
};

const formatNumber = (value?: number | null) => Number(value ?? 0).toLocaleString("zh-CN");
const formatPercent = (value?: number | null) => `${Number(value ?? 0).toFixed(1)}%`;

const nodeColors: Record<string, string> = {
  all: "var(--sales-sankey-root)",
  vehicle_related: "var(--sales-sankey-vehicle)",
  not_vehicle_related: "var(--sales-sankey-neutral)",
  sales_intent: "var(--sales-sankey-sales)",
  non_sales_intent: "var(--sales-sankey-neutral)",
  signal_strong: "var(--sales-sankey-strong)",
  signal_mid: "var(--sales-sankey-mid)",
  signal_weak: "var(--sales-sankey-weak)",
  signal_none: "var(--sales-sankey-neutral)",
  signal_unknown: "var(--sales-sankey-neutral)",
};

const pieColors = ["var(--voc-chart-1)", "var(--voc-chart-2)", "var(--voc-chart-3)", "var(--voc-chart-4)", "var(--voc-chart-5)", "var(--voc-chart-6)"];
const hiddenProfileLabel = ["未", "画像用户"].join("");
const purchaseSignalFilters = ["全部", "强购买信号", "中购买信号", "弱购买信号", "无购买信号"] as const;
const profileStatusFilters = ["全部", "已画像", "未画像"] as const;
const userSortOptions = ["按购买信号", "按评论时间", "按画像状态"] as const;

type PurchaseSignalFilter = (typeof purchaseSignalFilters)[number];
type ProfileStatusFilter = (typeof profileStatusFilters)[number];
type UserSortOption = (typeof userSortOptions)[number];

function RuleTooltip() {
  return (
    <div className="group relative">
      <button
        type="button"
        aria-label="查看销售线索漏斗计算规则"
        className="flex h-8 w-8 items-center justify-center rounded-lg border border-[var(--theme-border)] bg-[var(--theme-white)] text-[var(--theme-muted)] shadow-[0_8px_20px_rgba(26,32,44,0.03)] transition hover:text-[var(--theme-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--theme-selected-bg)]"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
      <div className="pointer-events-none absolute right-0 top-10 z-20 hidden w-80 rounded-2xl border border-[var(--theme-border)] bg-white p-4 text-xs leading-5 text-[var(--theme-body)] shadow-[0_18px_48px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
        <p className="mb-2 font-semibold text-[var(--theme-ink)]">计算规则</p>
        <p>销售相关意图包含：购买意向、询价、价格敏感、到店、试驾、下订；中/强购买信号也会进入销售相关人群。</p>
        <p>强购买比例 = 强购买信号评论数 / 已打标评论数。</p>
        <p>用户画像占比来自评论用户画像结果表；未匹配到画像的用户归为未画像。</p>
        <p>字段来源：comment_label_json.purchase_signal、comment_label_json.comment_intent。</p>
      </div>
    </div>
  );
}

function nodeValue(nodeId: string, links: SalesLeadSankeyLink[]) {
  const incoming = links.filter((link) => link.target === nodeId).reduce((sum, link) => sum + link.value, 0);
  const outgoing = links.filter((link) => link.source === nodeId).reduce((sum, link) => sum + link.value, 0);
  return Math.max(incoming, outgoing);
}

function nodeRate(nodeId: string, value: number, total: number) {
  if (nodeId === "all") return "";
  return total ? formatPercent((value * 100) / total) : "0.0%";
}

function buildNodePosition(node: SalesLeadSankeyNode, indexInLayer: number, layerSize: number) {
  const xByLayer = [18, 230, 418, 604];
  const baseY = layerSize === 1 ? 218 : layerSize === 2 ? 142 : 58;
  const gap = layerSize === 1 ? 0 : layerSize === 2 ? 156 : 86;
  return { x: xByLayer[node.layer] ?? 18, y: baseY + indexInLayer * gap };
}

function SalesLeadSankey({
  nodes,
  links,
  selectedSegmentId,
  onSelectSegment,
}: {
  nodes: SalesLeadSankeyNode[];
  links: SalesLeadSankeyLink[];
  selectedSegmentId: string;
  onSelectSegment: (segmentId: string) => void;
}) {
  const layers = nodes.reduce<Record<number, SalesLeadSankeyNode[]>>((acc, node) => {
    acc[node.layer] = [...(acc[node.layer] ?? []), node];
    return acc;
  }, {});
  const positions = new Map<string, { x: number; y: number }>();
  Object.values(layers).forEach((layerNodes) => {
    layerNodes.forEach((node, index) => {
      positions.set(node.id, buildNodePosition(node, index, layerNodes.length));
    });
  });

  const total = nodeValue("all", links);
  const maxLink = Math.max(...links.map((link) => link.value), 1);

  return (
    <div className="flex h-full min-h-[520px] flex-col rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-[var(--theme-ink)]">线索质量漏斗</h3>
        <span className="rounded-full bg-[var(--theme-soft-panel)] px-2.5 py-1 text-[11px] text-[var(--theme-muted)]">点击节点查看画像</span>
      </div>
      <div className="overflow-x-auto">
        <svg className="h-[500px] min-w-[780px]" viewBox="0 0 800 500" role="img" aria-label="销售线索桑基图">
          <defs>
            <filter id="lead-node-shadow" x="-20%" y="-30%" width="150%" height="160%">
              <feDropShadow dx="0" dy="10" stdDeviation="10" floodColor="#1a202c" floodOpacity="0.08" />
            </filter>
          </defs>

          {links.map((link) => {
            const source = positions.get(link.source);
            const target = positions.get(link.target);
            if (!source || !target) return null;
            const segmentId = `${link.source}->${link.target}`;
            const strokeWidth = Math.max(5, (link.value / maxLink) * 30);
            const sourceColor = nodeColors[link.source] ?? "var(--theme-primary)";
            const path = `M ${source.x + 152} ${source.y + 30} C ${source.x + 214} ${source.y + 30}, ${target.x - 74} ${target.y + 30}, ${target.x} ${target.y + 30}`;
            return (
              <path
                key={segmentId}
                d={path}
                fill="none"
                stroke={sourceColor}
                strokeLinecap="round"
                strokeOpacity={selectedSegmentId === segmentId ? 0.46 : 0.16}
                strokeWidth={strokeWidth}
                className="cursor-pointer transition"
                onClick={() => onSelectSegment(segmentId)}
              >
                <title>{`${link.source} -> ${link.target}: ${formatNumber(link.value)} 条`}</title>
              </path>
            );
          })}

          {nodes.map((node) => {
            const position = positions.get(node.id);
            if (!position) return null;
            const value = nodeValue(node.id, links);
            const isSelected = selectedSegmentId === node.id;
            return (
              <g key={node.id} transform={`translate(${position.x}, ${position.y})`} filter="url(#lead-node-shadow)" className="cursor-pointer" onClick={() => onSelectSegment(node.id)}>
                <rect width="154" height="60" rx="16" fill={isSelected ? "var(--theme-selected-bg)" : "var(--theme-white)"} stroke={isSelected ? "var(--theme-selected-border)" : "var(--theme-border)"} strokeWidth={isSelected ? 2 : 1} />
                <circle cx="18" cy="30" r="6" fill={nodeColors[node.id] ?? "var(--theme-primary)"} />
                <text x="34" y="25" className="fill-[#151720] text-[13px] font-semibold">
                  {node.label}
                </text>
                <text x="34" y="43" className="fill-[#8b92a1] text-[11px]">
                  {formatNumber(value)} 条
                </text>
                {nodeRate(node.id, value, total) ? (
                  <text x="116" y="43" className="fill-[#8b92a1] text-[11px]">
                    {nodeRate(node.id, value, total)}
                  </text>
                ) : null}
              </g>
            );
          })}
        </svg>
      </div>
      <div className="mt-auto flex flex-wrap gap-5 border-t border-[var(--theme-border)] pt-4 text-[11px] text-[var(--theme-muted)]">
        <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[var(--sales-sankey-root)]" />基础数据</span>
        <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[var(--sales-sankey-sales)]" />相关或有意向</span>
        <span className="inline-flex items-center gap-2"><i className="h-2 w-2 rounded-full bg-[var(--sales-sankey-neutral)]" />非相关/无信号</span>
        <span>节点百分比为占全部已打标评论比例</span>
      </div>
    </div>
  );
}

function ProfileDistributionBars({ data }: { data: SalesLeadProfileDistributionItem[] }) {
  const rows = data.slice(0, 6);
  const totalUsers = rows.reduce((sum, item) => sum + item.user_count, 0);
  return (
    <div className="mt-3 overflow-hidden rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-2.5" aria-label="画像占比条形 画像占比堆叠条">
      {rows.length ? (
        <>
          <div className="flex items-center justify-between gap-3 text-xs">
            <span className="font-medium text-[var(--theme-ink)]">画像占比</span>
            <span className="shrink-0 text-[var(--theme-muted)]">{formatNumber(totalUsers)} users</span>
          </div>
          <div className="mt-2 flex h-2.5 w-full overflow-hidden rounded-full bg-[var(--theme-track)]">
            {rows.map((item, index) => (
              <span
                key={item.main_label}
                className="h-full min-w-px"
                style={{
                  flexBasis: 0,
                  flexGrow: Math.max(0, item.user_count),
                  backgroundColor: item.main_label === hiddenProfileLabel ? "var(--profile-unprofiled)" : pieColors[index] ?? "var(--profile-completed)",
                }}
                title={`${item.main_label}: ${formatPercent(item.rate)}`}
              />
            ))}
          </div>
          <div className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1">
            {rows.map((item, index) => (
              <div key={item.main_label} className="flex min-w-0 items-center justify-between gap-2 text-[10px]">
                <span className="flex min-w-0 items-center gap-2 font-medium text-[var(--theme-body)]">
                  <i className="h-2 w-2 shrink-0 rounded-full" style={{ backgroundColor: item.main_label === hiddenProfileLabel ? "var(--profile-unprofiled)" : pieColors[index] ?? "var(--profile-completed)" }} />
                  <span className="truncate">{item.main_label}</span>
                </span>
                <span className="shrink-0 text-[var(--theme-muted)]">
                  {formatNumber(item.user_count)} · {formatPercent(item.rate)}
                </span>
              </div>
            ))}
          </div>
        </>
      ) : null}
      {!rows.length ? <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-6 text-center text-sm text-[var(--theme-muted)]">暂无画像占比</div> : null}
    </div>
  );
}

function StatMiniCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex h-[58px] min-w-0 flex-col justify-center rounded-xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] px-3 py-2">
      <p className="truncate text-[10px] text-[var(--theme-muted)]">{label}</p>
      <strong className="mt-1 block truncate text-sm font-semibold text-[var(--theme-ink)]">{value}</strong>
    </div>
  );
}

function ProfilePanel({ segment, onOpenUsers }: { segment?: SalesLeadProfileSegment; onOpenUsers: () => void }) {
  if (!segment) {
    return (
      <aside className="rounded-[24px] border border-dashed border-[var(--theme-border)] bg-[var(--theme-white)] p-5 text-sm text-[var(--theme-muted)]">
        点击左侧桑基节点后查看用户画像分布。
      </aside>
    );
  }
  const topProfile = segment.profile_distribution.find((item) => item.main_label && item.main_label !== hiddenProfileLabel);
  const topProfileLabel = topProfile ? `${topProfile.main_label} ${formatPercent(topProfile.rate)}` : "-";

  return (
    <aside className="flex h-full min-w-0 flex-col overflow-hidden rounded-[24px] border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="flex shrink-0 items-start justify-between gap-3">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Lead Intelligence</p>
          <h3 className="mt-1 text-base font-semibold text-[var(--theme-ink)]">用户画像占比</h3>
          <p className="mt-1 text-xs text-[var(--theme-muted)]">{segment.label}</p>
        </div>
        <UsersRound className="h-5 w-5 text-[var(--theme-primary)]" />
      </div>

      <ProfileDistributionBars data={segment.profile_distribution} />

      <div className="mt-3 grid shrink-0 grid-cols-2 gap-2">
        <StatMiniCard label="用户数" value={formatNumber(segment.summary.user_count)} />
        <StatMiniCard label="中/强信号" value={formatNumber(segment.summary.mid_high_purchase_signal_count)} />
        <StatMiniCard label="最多画像用户" value={topProfileLabel} />
        <StatMiniCard label="覆盖内容" value={formatNumber(segment.summary.content_count)} />
      </div>

      <div className="mt-2.5 flex shrink-0 items-center justify-between">
        <h4 className="text-xs font-semibold text-[var(--theme-ink)]">高价值用户 Top 5</h4>
      </div>
      <div className="mt-2 min-h-0 flex-1 space-y-1 overflow-hidden">
        {segment.users.slice(0, 5).map((user) => (
          <div key={user.comment_user_id} className="flex min-h-[30px] items-center gap-2.5 rounded-xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] px-2 py-0.5">
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[var(--theme-track)] text-[var(--theme-muted)]">
              <UserRound className="h-3.5 w-3.5" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-xs font-semibold text-[var(--theme-ink)]">{user.comment_author_name}</p>
            </div>
            <span
              className={`max-w-20 shrink-0 truncate rounded-full px-2 py-0.5 text-[10px] ${
                user.main_label === hiddenProfileLabel ? "bg-[var(--profile-missing-bg)] text-[var(--profile-missing-text)]" : "bg-[var(--theme-selected-bg)] text-[var(--theme-selected-border)]"
              }`}
            >
              {user.main_label}
            </span>
          </div>
        ))}
      </div>

      <button type="button" onClick={onOpenUsers} className="mt-auto h-9 w-full rounded-xl bg-[var(--theme-primary)] text-sm font-semibold text-white shadow-[0_12px_22px_rgba(45,43,49,0.18)] hover:bg-[var(--theme-primary-hover)]">
        查看全部用户
      </button>

    </aside>
  );
}

function getUserProfileStatus(user: SalesLeadProfileSegment["users"][number]) {
  return user.main_label && user.main_label !== hiddenProfileLabel ? "已画像" : "未画像";
}

function getUserPurchaseSignal(user: SalesLeadProfileSegment["users"][number]) {
  if (user.purchase_signal === "强") return "强购买信号";
  if (user.purchase_signal === "中") return "中购买信号";
  if (user.purchase_signal === "弱") return "弱购买信号";
  if (user.purchase_signal === "无") return "无购买信号";
  return "未标注购买信号";
}

function purchaseSignalBadgeClass(signal: string) {
  if (signal === "强购买信号") return "bg-[var(--sales-chip-strong)] text-[var(--sales-chip-strong-text)]";
  if (signal === "中购买信号") return "bg-[var(--sales-chip-mid)] text-[var(--sales-chip-mid-text)]";
  if (signal === "弱购买信号") return "bg-[var(--sales-chip-weak)] text-[var(--sales-chip-weak-text)]";
  return "bg-[var(--theme-soft-panel)] text-[var(--theme-muted)]";
}

function profileStatusBadgeClass(status: string) {
  return status === "已画像" ? "bg-[var(--theme-status-bg)] text-[var(--theme-status-text)]" : "bg-[var(--profile-missing-bg)] text-[var(--theme-muted)]";
}

function matchesPurchaseSignal(user: SalesLeadProfileSegment["users"][number], filter: PurchaseSignalFilter) {
  if (filter === "全部") return true;
  return getUserPurchaseSignal(user) === filter;
}

function buildUserInsightUrl(eventId: string, commentUserId: string) {
  return `${apiBaseUrl}/voc/events/${encodeURIComponent(eventId)}/comment-users/${encodeURIComponent(commentUserId)}/insight-profile`;
}

function buildUserAiProfileUrl(commentUserId: string) {
  return `${apiBaseUrl}/profiles/comment-users/${encodeURIComponent(commentUserId)}/ai-run`;
}

const profileRadarDimensions = ["决策风格", "核心关注点", "用车场景", "价格敏感度", "服务偏好", "品牌态度"] as const;

function buildDimensionRadarLabels(radarLabels: SalesLeadUserInsightProfile["radar_labels"]) {
  return profileRadarDimensions.map((dimension) => {
    const dimensionLabels = radarLabels.filter((item) => item.dimension === dimension);
    const maxScore = Math.max(0, ...dimensionLabels.map((item) => Number(item.score ?? 0)));
    const supportCount = dimensionLabels.reduce((sum, item) => sum + Number(item.support_count ?? 0), 0);
    return {
      dimension,
      label: dimension,
      score: maxScore,
      support_count: supportCount,
    };
  });
}

function ProfileRadarChart({ radar_labels }: { radar_labels: SalesLeadUserInsightProfile["radar_labels"] }) {
  const labels = buildDimensionRadarLabels(radar_labels);
  const topSubLabels = [...radar_labels]
    .filter((item) => Number(item.score ?? 0) > 0)
    .sort((a, b) => Number(b.score ?? 0) - Number(a.score ?? 0))
    .slice(0, 5);
  const size = 260;
  const center = size / 2;
  const maxRadius = 92;
  const levels = [0.25, 0.5, 0.75, 1];
  const points = labels.map((item, index) => {
    const angle = -Math.PI / 2 + (Math.PI * 2 * index) / Math.max(labels.length, 1);
    const radius = (Math.max(0, Math.min(100, item.score)) * maxRadius) / 100;
    return {
      ...item,
      x: center + Math.cos(angle) * radius,
      y: center + Math.sin(angle) * radius,
      axisX: center + Math.cos(angle) * maxRadius,
      axisY: center + Math.sin(angle) * maxRadius,
      labelX: center + Math.cos(angle) * (maxRadius + 24),
      labelY: center + Math.sin(angle) * (maxRadius + 24),
    };
  });
  const polygon = points.map((point) => `${point.x},${point.y}`).join(" ");

  return (
    <div className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4">
      <div className="mb-2 flex items-center justify-between">
        <h4 className="text-sm font-semibold text-[var(--theme-ink)]">画像维度雷达</h4>
        <span className="text-xs text-[var(--theme-muted)]">未命中维度 = 0</span>
      </div>
      <svg viewBox={`0 0 ${size} ${size}`} className="mx-auto h-[280px] w-full max-w-[320px]" role="img" aria-label="用户画像标签雷达图">
        {levels.map((level) => {
          const gridPoints = labels
            .map((_, index) => {
              const angle = -Math.PI / 2 + (Math.PI * 2 * index) / labels.length;
              const radius = maxRadius * level;
              return `${center + Math.cos(angle) * radius},${center + Math.sin(angle) * radius}`;
            })
            .join(" ");
          return <polygon key={level} points={gridPoints} fill="none" stroke="#e5e9f2" strokeWidth="1" />;
        })}
        {points.map((point) => (
          <line key={`axis-${point.label}`} x1={center} y1={center} x2={point.axisX} y2={point.axisY} stroke="#e5e9f2" strokeWidth="1" />
        ))}
        <polygon points={polygon} fill="rgba(217,130,82,0.12)" stroke="var(--theme-selected-border)" strokeWidth="2" />
        {points.map((point) => (
          <g key={point.label}>
            <circle cx={point.x} cy={point.y} r="4" fill="var(--sales-sankey-root)">
              <title>{`${point.label}: ${point.score}`}</title>
            </circle>
            <text x={point.labelX} y={point.labelY} textAnchor="middle" className="fill-[#596070] text-[10px]">
              {point.label}
            </text>
          </g>
        ))}
      </svg>
      <div className="mt-2 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)]/70 p-3">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs font-semibold text-[var(--theme-ink)]">命中子标签</span>
          <span className="text-[11px] text-[var(--theme-muted)]">Top {topSubLabels.length || 0}</span>
        </div>
        {topSubLabels.length ? (
          <div className="flex flex-wrap gap-2">
            {topSubLabels.map((item) => (
              <span key={`${item.dimension}-${item.label}`} className="inline-flex items-center gap-1 rounded-full bg-[var(--theme-selected-bg)] px-2.5 py-1 text-[11px] font-medium text-[var(--theme-selected-border)]">
                {item.label}
                <b className="font-semibold">{formatNumber(item.score)}</b>
              </span>
            ))}
          </div>
        ) : (
          <p className="text-xs text-[var(--theme-muted)]">暂无命中子标签，雷达维度按 0 展示。</p>
        )}
      </div>
    </div>
  );
}

function sentimentToScore(sentiment?: string | null) {
  const value = (sentiment ?? "").trim();
  if (["正向", "正面", "positive", "Positive"].includes(value)) return 1;
  if (["负向", "负面", "negative", "Negative"].includes(value)) return -1;
  return 0;
}

function sentimentLabel(score: number) {
  if (score > 0) return "正面";
  if (score < 0) return "负面";
  return "中性";
}

function sentimentEmoji(score: number) {
  if (score > 0) return "😊";
  if (score < 0) return "😟";
  return "😐";
}

function buildSmoothTimelinePath(points: Array<{ x: number; y: number }>) {
  if (!points.length) return "";
  if (points.length === 1) return `M ${points[0].x} ${points[0].y}`;
  return points
    .map((point, index) => {
      if (index === 0) return `M ${point.x} ${point.y}`;
      const previous = points[index - 1];
      const controlDistance = Math.max(18, (point.x - previous.x) * 0.42);
      return `C ${previous.x + controlDistance} ${previous.y}, ${point.x - controlDistance} ${point.y}, ${point.x} ${point.y}`;
    })
    .join(" ");
}

function EmotionTimelineChart({ comments, onOpenComments }: { comments: SalesLeadUserInsightProfile["comments"]; onOpenComments: () => void }) {
  const timeline = comments
    .map((comment) => ({
      ...comment,
      sentimentScore: sentimentToScore(comment.comment_sentiment),
    }))
    .sort((a, b) => String(a.published_at ?? "").localeCompare(String(b.published_at ?? ""), "zh-CN"));
  const width = 620;
  const height = 280;
  const paddingX = 56;
  const yByScore = (score: number) => (score > 0 ? 72 : score < 0 ? 208 : 140);
  const xByIndex = (index: number) => {
    if (timeline.length <= 1) return width / 2;
    return paddingX + (index * (width - paddingX * 2)) / (timeline.length - 1);
  };
  const points = timeline.map((item, index) => ({
    ...item,
    x: xByIndex(index),
    y: yByScore(item.sentimentScore),
  }));
  const smoothPath = buildSmoothTimelinePath(points);

  return (
    <div className="rounded-2xl border border-[var(--theme-border)] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold text-[var(--theme-ink)]">情绪曲线</h4>
          <p className="mt-1 text-xs text-[var(--theme-muted)]">按该用户全部评论发布时间绘制</p>
        </div>
        <button
          type="button"
          onClick={onOpenComments}
          className="rounded-full border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] px-2.5 py-1 text-xs font-medium text-[var(--theme-primary)] transition hover:border-[var(--theme-primary)] hover:bg-[var(--theme-primary-soft)]"
        >
          查看全部评论 · {formatNumber(timeline.length)}
        </button>
      </div>
      {timeline.length ? (
        <svg viewBox={`0 0 ${width} ${height}`} className="h-[280px] w-full" role="img" aria-label="用户评论情绪曲线">
          <defs>
            <linearGradient id="sentiment-line-gradient" x1="0" x2="1" y1="0" y2="0">
              <stop offset="0%" stopColor="var(--sales-sankey-root)" />
              <stop offset="55%" stopColor="var(--sales-sankey-sales)" />
              <stop offset="100%" stopColor="var(--sales-sankey-strong)" />
            </linearGradient>
          </defs>
          {[72, 140, 208].map((y, index) => (
            <line key={y} x1="48" x2={width - 28} y1={y} y2={y} stroke={index === 1 ? "#dfe5ef" : "#edf0f5"} strokeDasharray={index === 1 ? "4 4" : "0"} />
          ))}
          <text x="12" y="76" className="fill-[var(--sales-sankey-root)] text-[11px]">正面</text>
          <text x="12" y="144" className="fill-[#8b92a1] text-[11px]">中性</text>
          <text x="12" y="212" className="fill-[#e4577d] text-[11px]">负面</text>
          {points.length > 1 ? <path d={smoothPath} fill="none" stroke="url(#sentiment-line-gradient)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" /> : null}
          {points.map((point, index) => (
            <g key={`${point.comment_id}-${index}`}>
              <circle cx={point.x} cy={point.y} r="11" fill="white" stroke={point.sentimentScore > 0 ? "var(--sales-sankey-root)" : point.sentimentScore < 0 ? "var(--sales-sankey-strong)" : "var(--sales-sankey-neutral)"} strokeWidth="1.5">
                <title>{`${point.published_at || "未知时间"}\n${sentimentLabel(point.sentimentScore)} · ${point.comment_text}`}</title>
              </circle>
              <text x={point.x} y={point.y + 4} textAnchor="middle" className="text-[13px]">
                {sentimentEmoji(point.sentimentScore)}
              </text>
              {index === 0 || index === points.length - 1 || index % 2 === 0 ? (
                <text x={point.x} y="258" textAnchor="middle" className="fill-[#8b92a1] text-[10px]">
                  {String(point.published_at || "").slice(5, 10) || "-"}
                </text>
              ) : null}
            </g>
          ))}
        </svg>
      ) : (
        <div className="flex h-[280px] items-center justify-center rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">暂无可绘制的评论情绪</div>
      )}
    </div>
  );
}

function CommentListDrawer({ comments, onClose }: { comments: SalesLeadUserInsightProfile["comments"]; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-[70] flex justify-end bg-[var(--theme-ink)]/20 backdrop-blur-sm">
      <div className="h-full w-full max-w-[680px] overflow-hidden rounded-l-[28px] border-l border-[var(--theme-border)] bg-white shadow-[0_24px_80px_rgba(26,32,44,0.18)]">
        <div className="flex items-start justify-between border-b border-[var(--theme-border)] px-6 py-5">
          <div>
            <p className="text-xs font-medium text-[var(--theme-muted)]">Comment Timeline</p>
            <h4 className="mt-1 text-xl font-semibold text-[var(--theme-ink)]">全部评论</h4>
            <p className="mt-2 text-sm text-[var(--theme-muted)]">共 {formatNumber(comments.length)} 条，按发布时间倒序展示。</p>
          </div>
          <button type="button" onClick={onClose} className="rounded-xl border border-[var(--theme-border)] bg-white p-2 text-[var(--theme-muted)] transition hover:text-[var(--theme-ink)]">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="h-[calc(100%-96px)] overflow-y-auto px-6 py-4">
          <div className="space-y-2">
            {comments.map((comment) => (
              <div key={comment.comment_id} className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-3">
                <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
                  {comment.purchase_signal ? <span className="rounded-full bg-[var(--theme-selected-bg)] px-2 py-1 text-[var(--theme-selected-border)]">{comment.purchase_signal}</span> : null}
                  {comment.comment_intent ? <span className="rounded-full bg-[var(--theme-chip)] px-2 py-1 text-[var(--theme-selected-text)]">{comment.comment_intent}</span> : null}
                  {comment.comment_sentiment ? <span className="rounded-full bg-[var(--theme-status-bg)] px-2 py-1 text-[var(--theme-status-text)]">{comment.comment_sentiment}</span> : null}
                </div>
                <p className="text-sm leading-6 text-[var(--theme-ink)]">{comment.comment_text}</p>
                <p className="mt-2 truncate text-xs text-[var(--theme-muted)]">{comment.content_title || "未关联内容"} · {comment.published_at || "未知时间"}</p>
              </div>
            ))}
            {!comments.length ? <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-8 text-center text-sm text-[var(--theme-muted)]">暂无评论</div> : null}
          </div>
        </div>
      </div>
    </div>
  );
}

function UserInsightDrawer({
  eventId,
  user,
  onClose,
}: {
  eventId?: string;
  user?: SalesLeadProfileSegment["users"][number];
  onClose: () => void;
}) {
  const [insight, setInsight] = useState<SalesLeadUserInsightProfile | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isCommentListOpen, setIsCommentListOpen] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!eventId || !user) return;
    let cancelled = false;
    setIsLoading(true);
    setError("");
    setInsight(null);
    fetch(buildUserInsightUrl(eventId, user.comment_user_id), { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error("load failed");
        return (await response.json()) as SalesLeadUserInsightProfile;
      })
      .then((payload) => {
        if (!cancelled) setInsight(payload);
      })
      .catch(() => {
        if (!cancelled) setError("用户洞察档案加载失败");
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [eventId, user]);

  if (!user) return null;
  const profile_summary = insight?.profile_summary;

  return (
    <div className="fixed inset-0 z-[60] flex justify-end bg-[var(--theme-ink)]/20 backdrop-blur-sm">
      <div className="h-full w-full max-w-[82vw] overflow-y-auto rounded-l-[28px] border-l border-[var(--theme-border)] bg-[var(--theme-page)] shadow-[0_24px_80px_rgba(26,32,44,0.18)]">
        <div className="sticky top-0 z-10 flex items-start justify-between border-b border-[var(--theme-border)] bg-white/90 px-6 py-5 backdrop-blur">
          <div>
            <button type="button" onClick={onClose} className="mb-2 text-xs font-medium text-[var(--theme-muted)] hover:text-[var(--theme-primary)]">← 返回用户列表</button>
            <p className="text-xs font-medium text-[var(--theme-muted)]">User Insight Profile</p>
            <h3 className="mt-1 text-2xl font-semibold text-[var(--theme-ink)]">用户洞察档案</h3>
            <p className="mt-2 text-sm text-[var(--theme-muted)]">基于该用户评论与画像标签分数生成，仅用于后续销售评分，不代表最终用户画像。</p>
          </div>
          <button type="button" onClick={onClose} className="rounded-xl border border-[var(--theme-border)] bg-white p-2 text-[var(--theme-muted)] transition hover:text-[var(--theme-ink)]">
            <X className="h-4 w-4" />
          </button>
        </div>

        {isLoading ? <div className="p-10 text-center text-sm text-[var(--theme-muted)]">正在加载用户洞察档案...</div> : null}
        {error ? <div className="m-6 rounded-2xl border border-[var(--sales-chip-strong)] bg-[var(--theme-white)] p-5 text-sm text-[var(--sales-chip-strong-text)]">{error}</div> : null}
        {insight ? (
          <div className="space-y-4 p-6">
            <section className="grid gap-4 rounded-2xl border border-[var(--theme-border)] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)] xl:grid-cols-[1.35fr_repeat(4,1fr)]">
              <div className="flex min-w-0 items-center gap-3 border-r border-[var(--theme-border)] pr-4">
                <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-[var(--theme-primary)] text-xl font-semibold text-white">
                  <UserRound className="h-7 w-7" />
                </span>
                <div className="min-w-0">
                  <h4 className="truncate text-base font-semibold text-[var(--theme-ink)]">{insight.user.comment_author_name || user.comment_author_name}</h4>
                  <p className="mt-1 truncate text-xs text-[var(--theme-muted)]">用户ID：{insight.user.comment_user_id}</p>
                  <p className="mt-1 truncate text-xs text-[var(--theme-muted)]">数据来源：{insight.user.platform || "公网评论"}</p>
                </div>
              </div>
              <StatMiniCard label="评论总数" value={formatNumber(profile_summary?.total_comments)} />
              <StatMiniCard label="有效评论" value={formatNumber(profile_summary?.valid_comments)} />
              <StatMiniCard label="有效评论率" value={formatPercent(profile_summary?.valid_comment_rate)} />
              <StatMiniCard label="主标签分数" value={formatNumber(profile_summary ? profile_summary.main_score : undefined)} />
            </section>

            <section className="grid gap-4 xl:grid-cols-[1fr_1fr]">
              <ProfileRadarChart radar_labels={insight.radar_labels} />
              <EmotionTimelineChart comments={insight.comments} onOpenComments={() => setIsCommentListOpen(true)} />
            </section>

            <section className="rounded-2xl border border-[var(--theme-border)] bg-white p-4 shadow-[0_8px_24px_rgba(26,32,44,0.04)]">
              <div className="mb-3 flex items-center justify-between">
                <h4 className="text-sm font-semibold text-[var(--theme-ink)]">标签证据</h4>
                <span className="text-xs text-[var(--theme-muted)]">{profile_summary?.main_label || "未画像"}</span>
              </div>
              <div className="grid gap-2 xl:grid-cols-2">
                {insight.key_evidence.slice(0, 6).map((evidence, index) => (
                  <div key={`${evidence.label}-${evidence.comment_id}-${index}`} className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-3">
                    <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
                      <span className="rounded-full bg-[var(--theme-selected-bg)] px-2 py-1 font-medium text-[var(--theme-selected-border)]">{evidence.label}</span>
                    <span className="rounded-full bg-[var(--theme-status-bg)] px-2 py-1 text-[var(--theme-status-text)]">分数 {formatNumber(evidence.score)}</span>
                    </div>
                    <p className="text-sm leading-6 text-[var(--theme-ink)]">“{evidence.evidence_text || evidence.comment_text}”</p>
                    <p className="mt-2 text-xs leading-5 text-[var(--theme-muted)]">原因：{evidence.reason || "暂无原因"}</p>
                  </div>
                ))}
                {!insight.key_evidence.length ? <div className="rounded-2xl border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-8 text-center text-sm text-[var(--theme-muted)]">暂无标签证据</div> : null}
              </div>
            </section>

            {isCommentListOpen ? <CommentListDrawer comments={insight.comments} onClose={() => setIsCommentListOpen(false)} /> : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function UserListDrawer({
  eventId,
  segment,
  onClose,
  onOpenInsight,
}: {
  eventId?: string;
  segment?: SalesLeadProfileSegment;
  onClose: () => void;
  onOpenInsight: (user: SalesLeadProfileSegment["users"][number]) => void;
}) {
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [purchaseSignalFilter, setPurchaseSignalFilter] = useState<PurchaseSignalFilter>("全部");
  const [profileStatusFilter, setProfileStatusFilter] = useState<ProfileStatusFilter>("全部");
  const [sortBy, setSortBy] = useState<UserSortOption>("按购买信号");
  const [profilingUserId, setProfilingUserId] = useState<string | null>(null);
  const [profileRunMessage, setProfileRunMessage] = useState("");
  const [profileRunError, setProfileRunError] = useState("");
  if (!segment) return null;

  const profiledUsers = segment.users.filter((user) => getUserProfileStatus(user) === "已画像").length;
  const filteredUsers = segment.users
    .filter((user) => {
      const normalizedQuery = query.trim().toLowerCase();
      const queryMatched =
        !normalizedQuery ||
        user.comment_author_name.toLowerCase().includes(normalizedQuery) ||
        user.representative_comment.toLowerCase().includes(normalizedQuery);
      const purchaseMatched = matchesPurchaseSignal(user, purchaseSignalFilter);
      const profileMatched = profileStatusFilter === "全部" || getUserProfileStatus(user) === profileStatusFilter;
      return queryMatched && purchaseMatched && profileMatched;
    })
    .sort((a, b) => {
      if (sortBy === "按购买信号") {
        const signalOrder: Record<string, number> = { 强: 4, 中: 3, 弱: 2, 无: 1 };
        return (signalOrder[b.purchase_signal] ?? 0) - (signalOrder[a.purchase_signal] ?? 0);
      }
      if (sortBy === "按画像状态") return getUserProfileStatus(a).localeCompare(getUserProfileStatus(b), "zh-CN");
      return 0;
    });

  async function onProfileUser(user: SalesLeadProfileSegment["users"][number]) {
    setProfilingUserId(user.comment_user_id);
    setProfileRunMessage("");
    setProfileRunError("");
    try {
      const response = await fetch(buildUserAiProfileUrl(user.comment_user_id), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          profile_batch: "ai_profile",
          prompt_version: "comment_user_profile_v1",
        }),
      });
      if (!response.ok) {
        const payload = (await response.json().catch(() => ({}))) as { detail?: string };
        throw new Error(payload.detail || "画像生成失败");
      }
      const payload = (await response.json()) as { comment_count?: number; db_loaded?: { profiles_loaded?: number } };
      setProfileRunMessage(`已完成画像：抽取 ${formatNumber(payload.comment_count)} 条全库评论，写入 ${formatNumber(payload.db_loaded?.profiles_loaded)} 个画像结果。`);
      router.refresh();
    } catch (error) {
      setProfileRunError(error instanceof Error ? error.message : "画像生成失败");
    } finally {
      setProfilingUserId(null);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-[var(--theme-ink)]/20 backdrop-blur-sm">
      <div className="h-full w-full max-w-[80vw] translate-x-0 overflow-hidden rounded-l-[28px] border-l border-[var(--theme-border)] bg-white shadow-[0_24px_80px_rgba(26,32,44,0.18)]">
        <div className="flex items-start justify-between border-b border-[var(--theme-border)] px-6 py-5">
          <div>
            <p className="text-xs text-[var(--theme-muted)]">{segment.label}</p>
            <h3 className="mt-1 text-xl font-semibold text-[var(--theme-ink)]">全部用户</h3>
            <p className="mt-2 text-sm text-[var(--theme-muted)]">
              共 {formatNumber(segment.summary.user_count)} 位用户，其中 {formatNumber(segment.summary.mid_high_purchase_signal_count)} 位具有中/强购买信号，{formatNumber(profiledUsers)} 位已完成画像。
            </p>
          </div>
          <button type="button" onClick={onClose} className="rounded-xl border border-[var(--theme-border)] p-2 text-[var(--theme-muted)] transition hover:text-[var(--theme-ink)]">
            <X className="h-4 w-4" />
          </button>
        </div>

        <div className="flex h-[calc(100%-116px)] flex-col px-6 py-5">
          {profileRunMessage ? (
            <div className="mb-3 rounded-2xl border border-[var(--theme-status-bg)] bg-[var(--theme-status-bg)] px-4 py-3 text-sm text-[var(--theme-status-text)]">{profileRunMessage}</div>
          ) : null}
          {profileRunError ? (
            <div className="mb-3 rounded-2xl border border-[var(--sales-chip-strong)] bg-[var(--sales-chip-strong)] px-4 py-3 text-sm text-[var(--sales-chip-strong-text)]">{profileRunError}</div>
          ) : null}
          <div className="mb-4 flex flex-wrap items-center gap-3 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-3">
            <label className="relative min-w-64 flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--theme-muted)]" />
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="搜索用户昵称 / 评论内容"
                className="h-10 w-full rounded-xl border border-[var(--theme-border)] bg-white pl-9 pr-3 text-sm text-[var(--theme-ink)] outline-none transition placeholder:text-[var(--theme-muted)] focus:border-[var(--theme-primary)]"
              />
            </label>
            <select value={purchaseSignalFilter} onChange={(event) => setPurchaseSignalFilter(event.target.value as PurchaseSignalFilter)} className="h-10 rounded-xl border border-[var(--theme-border)] bg-white px-3 text-sm text-[var(--theme-body)] outline-none">
              {purchaseSignalFilters.map((option) => (
                <option key={option} value={option}>购买信号筛选：{option}</option>
              ))}
            </select>
            <select value={profileStatusFilter} onChange={(event) => setProfileStatusFilter(event.target.value as ProfileStatusFilter)} className="h-10 rounded-xl border border-[var(--theme-border)] bg-white px-3 text-sm text-[var(--theme-body)] outline-none">
              {profileStatusFilters.map((option) => (
                <option key={option} value={option}>画像状态筛选：{option}</option>
              ))}
            </select>
            <select value={sortBy} onChange={(event) => setSortBy(event.target.value as UserSortOption)} className="h-10 rounded-xl border border-[var(--theme-border)] bg-white px-3 text-sm text-[var(--theme-body)] outline-none">
              {userSortOptions.map((option) => (
                <option key={option} value={option}>排序：{option}</option>
              ))}
            </select>
          </div>

          <div className="min-h-0 flex-1 overflow-hidden rounded-2xl border border-[var(--theme-border)] bg-white">
            <div className="grid grid-cols-[1.25fr_2fr_0.9fr_0.8fr_0.42fr] bg-[var(--theme-soft-panel)] px-4 py-3 text-[11px] font-semibold text-[var(--theme-muted)]">
              <span>用户</span>
              <span>评论摘要</span>
              <span>购买信号</span>
              <span>画像状态</span>
              <span className="text-right">操作</span>
            </div>
            <div className="max-h-full overflow-y-auto">
              {filteredUsers.map((user) => {
                const signal = getUserPurchaseSignal(user);
                const profileStatus = getUserProfileStatus(user);
                return (
                  <div key={user.comment_user_id} className="grid min-h-14 grid-cols-[1.25fr_2fr_0.9fr_0.8fr_0.42fr] items-center border-t border-[var(--theme-border)] px-4 py-2.5">
                    <div className="flex min-w-0 items-center gap-3">
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--theme-track)] text-[var(--theme-muted)]">
                        <UserRound className="h-4 w-4" />
                      </span>
                      <div className="min-w-0">
                        <p className="truncate text-sm font-semibold text-[var(--theme-ink)]">{user.comment_author_name}</p>
                        <p className="truncate text-xs text-[var(--theme-muted)]">公网评论用户</p>
                      </div>
                    </div>
                    <p className="line-clamp-2 pr-5 text-sm leading-5 text-[var(--theme-body)]">{user.representative_comment}</p>
                    <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${purchaseSignalBadgeClass(signal)}`}>{signal}</span>
                    <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${profileStatusBadgeClass(profileStatus)}`}>{profileStatus}</span>
                    <div className="group relative flex justify-end">
                      <button type="button" className="rounded-lg p-1.5 text-[var(--theme-muted)] transition hover:bg-[var(--theme-soft-panel)] hover:text-[var(--theme-ink)]" aria-label="用户操作">
                        <MoreHorizontal className="h-4 w-4" />
                      </button>
                      <div className="pointer-events-auto absolute right-0 top-7 z-10 hidden w-28 rounded-xl border border-[var(--theme-border)] bg-white p-1 text-xs text-[var(--theme-body)] shadow-[0_12px_32px_rgba(26,32,44,0.12)] group-hover:block group-focus-within:block">
                        <button type="button" onClick={() => onOpenInsight(user)} className="block w-full rounded-lg px-2 py-1.5 text-left hover:bg-[var(--theme-soft-panel)]">查看详情</button>
                        <button type="button" className="block w-full rounded-lg px-2 py-1.5 text-left hover:bg-[var(--theme-soft-panel)]">查看评论</button>
                        <button
                          type="button"
                          onClick={() => onProfileUser(user)}
                          disabled={profilingUserId === user.comment_user_id}
                          className="block w-full rounded-lg px-2 py-1.5 text-left hover:bg-[var(--theme-soft-panel)] disabled:cursor-wait disabled:text-[var(--theme-muted)]"
                        >
                          {profilingUserId === user.comment_user_id ? "正在画像" : "去画像"}
                        </button>
                        <button type="button" className="block w-full rounded-lg px-2 py-1.5 text-left hover:bg-[var(--theme-soft-panel)]">标记跟进</button>
                      </div>
                    </div>
                  </div>
                );
              })}
              {!filteredUsers.length ? <div className="py-16 text-center text-sm text-[var(--theme-muted)]">暂无匹配用户</div> : null}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function SalesLeadQualityStoryCard({ quality, eventId }: SalesLeadQualityStoryCardProps) {
  const [selectedSegmentId, setSelectedSegmentId] = useState("sales_intent");
  const [isUserListOpen, setIsUserListOpen] = useState(false);
  const [selectedInsightUser, setSelectedInsightUser] = useState<SalesLeadProfileSegment["users"][number] | undefined>();
  const summary = quality?.summary;
  const segments = quality?.profile_segments ?? [];
  const selectedSegment = useMemo(
    () => segments.find((segment) => segment.segment_id === selectedSegmentId) ?? segments.find((segment) => segment.segment_id === "all"),
    [segments, selectedSegmentId],
  );
  const headline = summary
    ? `销售相关意图占比 ${formatPercent(summary.sales_intent_rate)}，强购买比例 ${formatPercent(summary.strong_purchase_signal_rate)}。`
    : "补充 comment_label_json.purchase_signal 和 comment_intent 后，这里会展示销售线索漏斗。";

  return (
    <article className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
      <div className="mb-5 flex flex-wrap items-start justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[var(--theme-muted)]">Sales Lead Funnel</p>
          <h2 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--theme-ink)]">线索质量</h2>
          <p className="mt-2 max-w-4xl text-sm leading-6 text-[var(--theme-body)]">{headline}</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-selected-bg)] px-3 py-1.5 text-xs font-medium text-[var(--theme-selected-border)]">
            <SignalHigh className="h-3.5 w-3.5" />
            中/强信号 {formatPercent(summary?.mid_high_purchase_signal_rate)}
          </span>
          <span className="inline-flex items-center gap-1.5 rounded-lg bg-[var(--theme-selected-bg)] px-3 py-1.5 text-xs font-medium text-[var(--theme-selected-border)]">
            <UserRoundCheck className="h-3.5 w-3.5" />
            销售相关意图占比 {formatPercent(summary?.sales_intent_rate)}
          </span>
          <RuleTooltip />
        </div>
      </div>

      <div className="grid items-stretch gap-4 xl:grid-cols-[2fr_1fr]">
        {quality?.sankey ? (
          <SalesLeadSankey nodes={quality.sankey.nodes} links={quality.sankey.links} selectedSegmentId={selectedSegmentId} onSelectSegment={setSelectedSegmentId} />
        ) : (
          <div className="flex h-80 items-center justify-center rounded-[24px] border border-dashed border-[var(--theme-border)] bg-[var(--theme-soft-panel)] text-sm text-[var(--theme-muted)]">
            暂无线索漏斗数据
          </div>
        )}

        <ProfilePanel segment={selectedSegment} onOpenUsers={() => setIsUserListOpen(true)} />
      </div>

      {isUserListOpen ? (
        <UserListDrawer
          eventId={eventId}
          segment={selectedSegment}
          onClose={() => setIsUserListOpen(false)}
          onOpenInsight={(user) => setSelectedInsightUser(user)}
        />
      ) : null}
      {selectedInsightUser ? <UserInsightDrawer eventId={eventId} user={selectedInsightUser} onClose={() => setSelectedInsightUser(undefined)} /> : null}
    </article>
  );
}
