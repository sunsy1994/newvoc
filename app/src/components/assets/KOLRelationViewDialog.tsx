import { useMemo, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import type { EventLibraryItem } from '@/types/eventAsset';
import type { KOLItem } from './data/kolLibraryData';
import type { AssetPageChangeHandler } from './assetNavigation';

type RelationViewProps = {
  open: boolean;
  kol: KOLItem | null;
  event: EventLibraryItem | null;
  onOpenChange: (open: boolean) => void;
  onPageChange?: AssetPageChangeHandler;
};

type AudienceMode = 'mindset' | 'stage';

type ContentNode = {
  id: string;
  title: string;
  type: '测评' | '体验' | '对比' | '观点';
  comments: number;
  interaction: number;
  highConfidenceRatio: number;
  effectiveRatio: number;
  platform: string;
};

type AudienceNode = {
  id: string;
  label: string;
  comments: number;
};

type SankeyNode = {
  id: string;
  label: string;
  value: number;
  kind: 'kol' | 'content' | 'audience';
  x: number;
  y: number;
  w: number;
  h: number;
  color: string;
  meta?: {
    content?: ContentNode;
    audienceLabel?: string;
  };
};

type SankeyLink = {
  sourceId: string;
  targetId: string;
  value: number;
};

type LinkMeta = {
  sourceId: string;
  targetId: string;
  commentCount: number;
  contentTotalComments: number;
  highConfidenceRatio: number;
};

type HoverInfo =
  | { type: 'node'; node: SankeyNode }
  | { type: 'link'; link: SankeyLink; source: SankeyNode; target: SankeyNode; meta?: LinkMeta }
  | null;

const CONTENT_TYPES = ['测评', '体验', '对比', '观点'] as const;
const TIME_OPTIONS = ['近7天', '近30天', '近90天', '全部时间'] as const;
const SVG_WIDTH = 1020;
const SVG_HEIGHT = 540;
const COL_TOP = 24;
const COL_BOTTOM = SVG_HEIGHT - 24;
const KOL_X = 40;
const CONTENT_X = 390;
const AUDIENCE_X = 760;
const NODE_W = 220;

function uniqueByOrder(values: string[]) {
  return [...new Set(values)];
}

function normalize(weights: number[]) {
  const total = weights.reduce((sum, value) => sum + value, 0) || 1;
  return weights.map((value) => value / total);
}

function splitToParts(total: number, count: number, seed: number) {
  if (count <= 0) return [];
  const weights = Array.from({ length: count }, (_, index) => ((seed + (index + 3) * 17) % 37) + 10);
  const normalized = normalize(weights);
  const base = normalized.map((ratio) => Math.floor(total * ratio));
  let rest = total - base.reduce((sum, value) => sum + value, 0);
  let cursor = 0;
  while (rest > 0) {
    base[cursor % base.length] += 1;
    cursor += 1;
    rest -= 1;
  }
  return base;
}

function layoutColumn<T extends { value: number }>(
  items: T[],
  opts: {
    top: number;
    bottom: number;
    gap: number;
    minHeight: number;
  }
) {
  if (items.length === 0) return [] as Array<T & { y: number; h: number }>;
  const { top, bottom, gap, minHeight } = opts;
  const available = Math.max(0, bottom - top - gap * (items.length - 1));
  const base = minHeight * items.length;
  const rest = Math.max(0, available - base);
  const total = items.reduce((sum, item) => sum + item.value, 0) || 1;
  let y = top;
  return items.map((item) => {
    const h = minHeight + (item.value / total) * rest;
    const placed = { ...item, y, h };
    y += h + gap;
    return placed;
  });
}

function buildContentNodes(kol: KOLItem): ContentNode[] {
  const baseWeights = [30, 24, 26, 20];
  const weights = [...baseWeights];

  if (kol.roleTags.some((tag) => tag.includes('测评'))) weights[0] += 8;
  if (kol.roleTags.some((tag) => tag.includes('种草'))) weights[1] += 6;
  if (kol.roleTags.some((tag) => tag.includes('解释'))) weights[3] += 4;
  if (kol.roleTags.some((tag) => tag.includes('争议'))) weights[2] += 5;

  const ratios = normalize(weights);

  return CONTENT_TYPES.map((type, index) => {
    const ratio = ratios[index];
    const comments = Math.max(1, Math.round(kol.totalComments * ratio));
    const interaction = Math.max(1, Math.round(kol.totalEngagement * ratio));
    const highConfidenceRatio = Math.max(0.08, Math.min(0.8, kol.highConfidenceRatio + (index - 1.5) * 0.03));
    const effectiveRatio = Math.max(0.05, Math.min(0.9, kol.effectiveEngagementRate + (1.2 - index) * 0.025));
    return {
      id: `content-${index}`,
      title: `${kol.nickname}-${type}向内容`,
      type,
      comments,
      interaction,
      highConfidenceRatio: Number(highConfidenceRatio.toFixed(2)),
      effectiveRatio: Number(effectiveRatio.toFixed(2)),
      platform: kol.platform,
    };
  });
}

export default function KOLRelationViewDialog({
  open,
  kol,
  event,
  onOpenChange,
  onPageChange,
}: RelationViewProps) {
  const [audienceMode, setAudienceMode] = useState<AudienceMode>('mindset');
  const [contentType, setContentType] = useState('全部内容类型');
  const [timeRange, setTimeRange] = useState<(typeof TIME_OPTIONS)[number]>('近30天');
  const [highConfidenceOnly, setHighConfidenceOnly] = useState(false);
  const [highInteractionOnly, setHighInteractionOnly] = useState(false);
  const [hoverInfo, setHoverInfo] = useState<HoverInfo>(null);

  const baseContents = useMemo(() => (kol ? buildContentNodes(kol) : []), [kol]);

  const filteredContents = useMemo(() => {
    const timeRatioMap: Record<(typeof TIME_OPTIONS)[number], number> = {
      近7天: 0.45,
      近30天: 0.78,
      近90天: 0.95,
      全部时间: 1,
    };
    const timeRatio = timeRatioMap[timeRange];
    const scaled = baseContents.map((item) => ({
      ...item,
      comments: Math.max(1, Math.round(item.comments * timeRatio)),
      interaction: Math.max(1, Math.round(item.interaction * timeRatio)),
    }));

    const avgInteraction = scaled.reduce((sum, item) => sum + item.interaction, 0) / (scaled.length || 1);
    const threshold = Math.round(avgInteraction * 1.05);

    return scaled.filter((item) => {
      const matchType = contentType === '全部内容类型' || item.type === contentType;
      const matchHighConfidence = !highConfidenceOnly || item.highConfidenceRatio >= 0.35;
      const matchHighInteraction = !highInteractionOnly || item.interaction >= threshold;
      return matchType && matchHighConfidence && matchHighInteraction;
    });
  }, [baseContents, contentType, highConfidenceOnly, highInteractionOnly, timeRange]);

  const audienceLabels = useMemo(() => {
    if (!kol) return [];
    if (audienceMode === 'mindset') {
      return uniqueByOrder([...kol.mindsetTop3, '价格敏感型', '智能科技型', '家庭出行型']).slice(0, 6);
    }
    return uniqueByOrder([...kol.stageTop3, '未知']).slice(0, 5);
  }, [audienceMode, kol]);

  const graph = useMemo(() => {
    if (!kol) {
      return {
        nodes: [] as SankeyNode[],
        links: [] as SankeyLink[],
        linkMetaMap: new Map<string, LinkMeta>(),
      };
    }

    const totalContentComments = filteredContents.reduce((sum, item) => sum + item.comments, 0) || 1;
    const kolNode: SankeyNode = {
      id: 'kol-node',
      label: kol.nickname,
      value: totalContentComments,
      kind: 'kol',
      x: KOL_X,
      y: Math.round((SVG_HEIGHT - 86) / 2),
      w: NODE_W,
      h: 86,
      color: '#2563EB',
    };

    const contentLayout = layoutColumn(
      [...filteredContents]
        .sort((a, b) => b.comments - a.comments)
        .map((content) => ({ content, value: content.comments })),
      { top: COL_TOP, bottom: COL_BOTTOM, gap: 10, minHeight: 42 }
    );

    const contentNodes: SankeyNode[] = contentLayout.map(({ content, y, h }) => ({
      id: content.id,
      label: content.type,
      value: content.comments,
      kind: 'content',
      x: CONTENT_X,
      y,
      w: NODE_W,
      h: Math.round(h),
      color: '#60A5FA',
      meta: { content },
    }));

    const audienceAccumulator = new Map<string, number>();
    const contentToAudience = new Map<string, Array<{ label: string; comments: number }>>();

    contentNodes.forEach((node, index) => {
      const parts = splitToParts(node.value, audienceLabels.length, index * 13 + 7);
      const links = audienceLabels.map((label, i) => ({ label, comments: parts[i] ?? 0 })).filter((item) => item.comments > 0);
      contentToAudience.set(node.id, links);
      links.forEach((item) => {
        audienceAccumulator.set(item.label, (audienceAccumulator.get(item.label) ?? 0) + item.comments);
      });
    });

    const audienceList: AudienceNode[] = [...audienceAccumulator.entries()]
      .map(([label, comments]) => ({ id: `aud-${label}`, label, comments }))
      .sort((a, b) => b.comments - a.comments);

    const audienceLayout = layoutColumn(
      audienceList.map((item) => ({ item, value: item.comments })),
      { top: COL_TOP, bottom: COL_BOTTOM, gap: 12, minHeight: 48 }
    );

    const audienceNodes: SankeyNode[] = audienceLayout.map(({ item, y, h }) => ({
      id: item.id,
      label: item.label,
      value: item.comments,
      kind: 'audience',
      x: AUDIENCE_X,
      y,
      w: NODE_W,
      h: Math.round(h),
      color: audienceMode === 'mindset' ? '#10B981' : '#F59E0B',
      meta: { audienceLabel: item.label },
    }));

    const links: SankeyLink[] = [];
    const linkMetaMap = new Map<string, LinkMeta>();

    contentNodes.forEach((node) => {
      links.push({ sourceId: kolNode.id, targetId: node.id, value: node.value });
      const flow = contentToAudience.get(node.id) ?? [];
      const content = node.meta?.content;
      flow.forEach((item) => {
        const targetId = `aud-${item.label}`;
        const link = { sourceId: node.id, targetId, value: item.comments };
        links.push(link);
        if (content) {
          linkMetaMap.set(
            `${link.sourceId}-${link.targetId}`,
            {
              sourceId: link.sourceId,
              targetId: link.targetId,
              commentCount: item.comments,
              contentTotalComments: content.comments,
              highConfidenceRatio: content.highConfidenceRatio,
            }
          );
        }
      });
    });

    return { nodes: [kolNode, ...contentNodes, ...audienceNodes], links, linkMetaMap };
  }, [audienceLabels, audienceMode, filteredContents, kol]);

  const nodeById = useMemo(() => {
    const map = new Map<string, SankeyNode>();
    graph.nodes.forEach((node) => map.set(node.id, node));
    return map;
  }, [graph.nodes]);

  const maxLinkValue = useMemo(() => Math.max(...graph.links.map((item) => item.value), 1), [graph.links]);

  const handleNodeClick = (node: SankeyNode) => {
    if (!onPageChange || !kol) return;
    if (node.kind === 'content') {
      onPageChange('content-library', {
        eventId: kol.eventId,
        kolId: kol.id,
        keyword: kol.nickname,
        includeKOL: true,
      });
      onOpenChange(false);
    }
    if (node.kind === 'audience') {
      onPageChange('comment-library', {
        eventId: kol.eventId,
        kolId: kol.id,
        keyword: kol.nickname,
        includeKOL: true,
      });
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[92vh] !w-[96vw] !max-w-[1200px] overflow-y-auto p-0" showCloseButton>
        <div className="border-b border-gray-200 px-6 py-4">
          <DialogHeader>
            <DialogTitle className="text-xl text-gray-900">关系视图</DialogTitle>
            <DialogDescription>
              {kol?.nickname ?? 'KOL'} 在 {event?.name ?? '当前事件'} 中的 KOL → 内容 → 评论者群体 连接关系
            </DialogDescription>
          </DialogHeader>
        </div>

        {!kol ? (
          <div className="px-6 py-10 text-center text-sm text-gray-500">未选择KOL，无法生成关系视图。</div>
        ) : (
          <div className="space-y-4 px-6 py-4">
            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant={audienceMode === 'mindset' ? 'default' : 'outline'}
                onClick={() => setAudienceMode('mindset')}
              >
                看心智
              </Button>
              <Button
                size="sm"
                variant={audienceMode === 'stage' ? 'default' : 'outline'}
                onClick={() => setAudienceMode('stage')}
              >
                看阶段
              </Button>
              <p className="text-xs text-gray-500">模式切换将改变右侧评论者标签节点</p>
            </div>

            <div className="grid grid-cols-1 gap-3 rounded-xl border border-gray-200 bg-gray-50 p-3 md:grid-cols-4">
              <div>
                <p className="mb-1 text-xs font-medium text-gray-600">内容类型</p>
                <Select value={contentType} onValueChange={setContentType}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="全部内容类型">全部内容类型</SelectItem>
                    {CONTENT_TYPES.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <p className="mb-1 text-xs font-medium text-gray-600">时间范围</p>
                <Select value={timeRange} onValueChange={(value) => setTimeRange(value as (typeof TIME_OPTIONS)[number])}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{TIME_OPTIONS.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="flex items-end">
                <label className="flex h-10 w-full items-center gap-2 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-700">
                  <Checkbox checked={highConfidenceOnly} onCheckedChange={(checked) => setHighConfidenceOnly(Boolean(checked))} />
                  只看高置信评论
                </label>
              </div>
              <div className="flex items-end">
                <label className="flex h-10 w-full items-center gap-2 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-700">
                  <Checkbox checked={highInteractionOnly} onCheckedChange={(checked) => setHighInteractionOnly(Boolean(checked))} />
                  只看高互动内容
                </label>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1fr_320px]">
              <div className="rounded-xl border border-gray-200 bg-white p-3">
                <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-gray-600">
                  <Badge className="bg-blue-100 text-blue-700">KOL</Badge>
                  <Badge className="bg-sky-100 text-sky-700">内容</Badge>
                  <Badge className={audienceMode === 'mindset' ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}>
                    {audienceMode === 'mindset' ? '评论者心智标签' : '评论者阶段标签'}
                  </Badge>
                  <span>点击内容节点跳转内容库，点击标签节点跳转评论库</span>
                </div>

                {graph.nodes.length <= 1 ? (
                  <div className="flex h-[560px] items-center justify-center text-sm text-gray-500">
                    当前筛选条件下暂无可展示节点
                  </div>
                ) : (
                  <svg viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`} className="h-[560px] w-full">
                    {graph.links.filter((link) => link.sourceId === 'kol-node').map((link) => {
                      const source = nodeById.get(link.sourceId);
                      const target = nodeById.get(link.targetId);
                      if (!source || !target) return null;
                      const sx = source.x + source.w;
                      const sy = source.y + source.h / 2;
                      const tx = target.x;
                      const ty = target.y + target.h / 2;
                      const width = 1.6 + (link.value / maxLinkValue) * 7;
                      const d = `M ${sx} ${sy} C ${sx + 95} ${sy}, ${tx - 95} ${ty}, ${tx} ${ty}`;
                      return (
                        <path
                          key={`${link.sourceId}-${link.targetId}`}
                          d={d}
                          fill="none"
                          stroke="#93C5FD"
                          strokeOpacity={0.52}
                          strokeWidth={width}
                          strokeLinecap="round"
                          className="cursor-pointer transition-opacity hover:stroke-blue-500"
                          onMouseEnter={() => setHoverInfo({ type: 'link', link, source, target })}
                        />
                      );
                    })}
                    {graph.links.filter((link) => link.sourceId !== 'kol-node').map((link) => {
                      const source = nodeById.get(link.sourceId);
                      const target = nodeById.get(link.targetId);
                      if (!source || !target) return null;
                      const sx = source.x + source.w;
                      const sy = source.y + source.h / 2;
                      const tx = target.x;
                      const ty = target.y + target.h / 2;
                      const width = 1.6 + (link.value / maxLinkValue) * 7;
                      const d = `M ${sx} ${sy} C ${sx + 95} ${sy}, ${tx - 95} ${ty}, ${tx} ${ty}`;
                      const stroke = audienceMode === 'mindset' ? '#86EFAC' : '#FCD34D';
                      const hoverStroke = audienceMode === 'mindset' ? 'hover:stroke-emerald-500' : 'hover:stroke-amber-500';
                      const metaKey = `${link.sourceId}-${link.targetId}`;
                      return (
                        <path
                          key={metaKey}
                          d={d}
                          fill="none"
                          stroke={stroke}
                          strokeOpacity={0.5}
                          strokeWidth={width}
                          strokeLinecap="round"
                          className={`cursor-pointer transition-opacity ${hoverStroke}`}
                          onMouseEnter={() =>
                            setHoverInfo({
                              type: 'link',
                              link,
                              source,
                              target,
                              meta: graph.linkMetaMap.get(metaKey),
                            })
                          }
                        />
                      );
                    })}

                    {graph.nodes.map((node) => (
                      <g
                        key={node.id}
                        className={node.kind === 'kol' ? '' : 'cursor-pointer'}
                        onMouseEnter={() => setHoverInfo({ type: 'node', node })}
                        onClick={() => handleNodeClick(node)}
                      >
                        <rect x={node.x} y={node.y} width={node.w} height={node.h} rx={10} fill={node.color} fillOpacity={0.95} />
                        <text x={node.x + 12} y={node.y + 22} fill="#fff" fontSize="12" fontWeight="600">
                          {node.label}
                        </text>
                        {node.h > 40 && (
                          <text x={node.x + 12} y={node.y + 40} fill="#E5E7EB" fontSize="11">
                            评论量 {node.value}
                          </text>
                        )}
                      </g>
                    ))}
                  </svg>
                )}
              </div>

              <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
                <p className="text-sm font-semibold text-gray-900">节点信息</p>
                {!hoverInfo ? (
                  <p className="mt-2 text-xs text-gray-500">悬浮节点或流线可查看详情。</p>
                ) : hoverInfo.type === 'node' ? (
                  <div className="mt-3 space-y-2 text-xs text-gray-700">
                    <p>名称：<span className="font-medium text-gray-900">{hoverInfo.node.label}</span></p>
                    <p>类型：{hoverInfo.node.kind === 'kol' ? 'KOL' : hoverInfo.node.kind === 'content' ? '内容' : '评论者标签'}</p>
                    <p>评论量：{hoverInfo.node.value}</p>
                    {hoverInfo.node.meta?.content && (
                      <>
                        <p>内容标题：{hoverInfo.node.meta.content.title}</p>
                        <p>内容类型：{hoverInfo.node.meta.content.type}</p>
                        <p>平台：{hoverInfo.node.meta.content.platform}</p>
                        <p>综合互动量：{hoverInfo.node.meta.content.interaction}</p>
                        <p>高置信评论占比：{Math.round(hoverInfo.node.meta.content.highConfidenceRatio * 100)}%</p>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="mt-3 space-y-2 text-xs text-gray-700">
                    <p>流向：<span className="font-medium text-gray-900">{hoverInfo.source.label} → {hoverInfo.target.label}</span></p>
                    <p>评论数：{hoverInfo.link.value}</p>
                    {hoverInfo.meta && (
                      <>
                        <p>占该内容评论比例：{Math.round((hoverInfo.meta.commentCount / (hoverInfo.meta.contentTotalComments || 1)) * 100)}%</p>
                        <p>高置信评论占比：{Math.round(hoverInfo.meta.highConfidenceRatio * 100)}%</p>
                      </>
                    )}
                  </div>
                )}

                <div className="mt-4 space-y-2">
                  <p className="text-sm font-semibold text-gray-900">快速跳转</p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() =>
                      kol &&
                      onPageChange?.('content-library', {
                        eventId: kol.eventId,
                        kolId: kol.id,
                        keyword: kol.nickname,
                        includeKOL: true,
                      })
                    }
                  >
                    查看内容库
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() =>
                      kol &&
                      onPageChange?.('comment-library', {
                        eventId: kol.eventId,
                        kolId: kol.id,
                        keyword: kol.nickname,
                        includeKOL: true,
                      })
                    }
                  >
                    查看评论库
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
