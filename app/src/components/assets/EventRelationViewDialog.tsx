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
import type { AssetPageChangeHandler } from './assetNavigation';
import type { EventLibraryItem } from '@/types/eventAsset';

type RelationViewProps = {
  open: boolean;
  event: EventLibraryItem | null;
  onOpenChange: (open: boolean) => void;
  onPageChange?: AssetPageChangeHandler;
};

type SpeakerType = 'KOL' | '作者' | '媒体号' | '品牌号';

type ContentNode = {
  id: string;
  title: string;
  type: string;
  platform: string;
  author: string;
  speakerType: SpeakerType;
  interaction: number;
  comments: number;
  importance: number;
};

type SankeyNode = {
  id: string;
  label: string;
  value: number;
  kind: 'event' | 'content' | 'speaker';
  x: number;
  y: number;
  w: number;
  h: number;
  color: string;
  meta?: ContentNode;
};

type SankeyLink = {
  sourceId: string;
  targetId: string;
  value: number;
};

type HoverInfo =
  | { type: 'node'; node: SankeyNode }
  | { type: 'link'; link: SankeyLink; source: SankeyNode; target: SankeyNode }
  | null;

const CONTENT_TYPES = ['主贴', '视频', '图文', '测评内容', '提车内容', '对比内容'] as const;
const SPEAKER_TYPES: SpeakerType[] = ['KOL', '作者', '媒体号', '品牌号'];
const TIME_OPTIONS = ['近7天', '近30天', '近90天', '全部时间'] as const;
const SVG_WIDTH = 1020;
const SVG_HEIGHT = 540;
const COL_TOP = 24;
const COL_BOTTOM = SVG_HEIGHT - 24;
const EVENT_X = 40;
const CONTENT_X = 390;
const SPEAKER_X = 760;
const NODE_W = 220;

function normalizeWeights(weights: number[]) {
  const total = weights.reduce((sum, value) => sum + value, 0) || 1;
  return weights.map((value) => value / total);
}

function speakerByContentType(type: string, eventType: EventLibraryItem['type']): SpeakerType {
  if (type === '视频' || type === '测评内容') return 'KOL';
  if (type === '图文' || type === '提车内容') return '作者';
  if (type === '主贴') return eventType === '品牌传播' ? '品牌号' : '媒体号';
  return eventType === '竞品对比' ? '媒体号' : '品牌号';
}

function authorBySpeakerType(type: SpeakerType, brand: string) {
  if (type === 'KOL') return '头部KOL账号';
  if (type === '媒体号') return '行业媒体账号';
  if (type === '品牌号') return `${brand}官方号`;
  return '核心作者账号';
}

function buildContents(event: EventLibraryItem): ContentNode[] {
  const base = [24, 20, 18, 15, 13, 10];
  const weights = [...base];

  if (event.type === '新品上市') {
    weights[1] += 4;
    weights[3] += 3;
    weights[4] += 2;
  }
  if (event.type === '质量争议') {
    weights[0] += 4;
    weights[5] += 3;
  }
  if (event.type === '服务体验') {
    weights[2] += 3;
    weights[0] += 2;
  }
  if (event.type === '品牌传播') {
    weights[1] += 3;
    weights[2] += 2;
  }
  if (event.type === '竞品对比') {
    weights[5] += 5;
    weights[3] += 2;
  }

  const normalized = normalizeWeights(weights);
  return CONTENT_TYPES.map((type, index) => {
    const ratio = normalized[index];
    const interaction = Math.round(event.commentCount * ratio * 0.9 + event.heat * 70);
    const comments = Math.round(event.commentCount * ratio);
    const speakerType = speakerByContentType(type, event.type);
    return {
      id: `content-${index}`,
      title: `${event.name}-${type}`,
      type,
      platform: event.platforms[index % event.platforms.length] ?? '全平台',
      author: authorBySpeakerType(speakerType, event.brand),
      speakerType,
      interaction,
      comments,
      importance: Math.max(1, Math.round(event.contentCount * ratio)),
    };
  });
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
  const totalValue = items.reduce((sum, item) => sum + item.value, 0) || 1;

  let y = top;
  return items.map((item) => {
    const h = minHeight + (item.value / totalValue) * rest;
    const placed = { ...item, y, h };
    y += h + gap;
    return placed;
  });
}

export default function EventRelationViewDialog({ open, event, onOpenChange, onPageChange }: RelationViewProps) {
  const [platform, setPlatform] = useState('全部平台');
  const [contentType, setContentType] = useState('全部内容类型');
  const [speakerType, setSpeakerType] = useState('全部主体类型');
  const [timeRange, setTimeRange] = useState<(typeof TIME_OPTIONS)[number]>('近30天');
  const [highOnly, setHighOnly] = useState(false);
  const [hoverInfo, setHoverInfo] = useState<HoverInfo>(null);

  const platformOptions = useMemo(
    () => ['全部平台', ...(event ? event.platforms : [])],
    [event]
  );

  const contentBase = useMemo(() => (event ? buildContents(event) : []), [event]);

  const filteredContent = useMemo(() => {
    const timeRatioMap: Record<(typeof TIME_OPTIONS)[number], number> = {
      近7天: 0.45,
      近30天: 0.78,
      近90天: 0.95,
      全部时间: 1,
    };
    const timeRatio = timeRatioMap[timeRange];
    const scaled = contentBase.map((item) => ({
      ...item,
      importance: Math.max(1, Math.round(item.importance * timeRatio)),
      interaction: Math.max(1, Math.round(item.interaction * timeRatio)),
      comments: Math.max(1, Math.round(item.comments * timeRatio)),
    }));

    const avgInteraction =
      scaled.reduce((sum, item) => sum + item.interaction, 0) / (scaled.length || 1);
    const highThreshold = Math.round(avgInteraction * 1.05);

    return scaled.filter((item) => {
      const matchPlatform = platform === '全部平台' || item.platform === platform;
      const matchContent = contentType === '全部内容类型' || item.type === contentType;
      const matchSpeaker = speakerType === '全部主体类型' || item.speakerType === speakerType;
      const matchHigh = !highOnly || item.interaction >= highThreshold;
      return matchPlatform && matchContent && matchSpeaker && matchHigh;
    });
  }, [contentBase, contentType, highOnly, platform, speakerType, timeRange]);

  const graph = useMemo(() => {
    if (!event) return { nodes: [] as SankeyNode[], links: [] as SankeyLink[] };

    const speakerMap = new Map<SpeakerType, number>();
    filteredContent.forEach((item) => {
      speakerMap.set(item.speakerType, (speakerMap.get(item.speakerType) ?? 0) + item.importance);
    });

    const totalImportance = filteredContent.reduce((sum, item) => sum + item.importance, 0) || 1;
    const eventNodeHeight = 86;
    const eventNode: SankeyNode = {
      id: 'event-node',
      label: event.name,
      value: totalImportance,
      kind: 'event',
      x: EVENT_X,
      y: Math.round((SVG_HEIGHT - eventNodeHeight) / 2),
      w: NODE_W,
      h: eventNodeHeight,
      color: '#2563EB',
    };

    const sortedContent = [...filteredContent].sort((a, b) => b.importance - a.importance);
    const contentLayout = layoutColumn(
      sortedContent.map((item) => ({ item, value: item.importance })),
      { top: COL_TOP, bottom: COL_BOTTOM, gap: 10, minHeight: 38 }
    );
    const contentNodes: SankeyNode[] = contentLayout.map(({ item, y, h }) => ({
        id: item.id,
        label: item.type,
        value: item.importance,
        kind: 'content',
        x: CONTENT_X,
        y,
        w: NODE_W,
        h: Math.round(h),
        color: '#60A5FA',
        meta: item,
      })
    );

    const speakerEntries = [...speakerMap.entries()].sort((a, b) => b[1] - a[1]);
    const speakerLayout = layoutColumn(
      speakerEntries.map(([type, value]) => ({ type, value })),
      { top: COL_TOP, bottom: COL_BOTTOM, gap: 12, minHeight: 44 }
    );
    const speakerNodes: SankeyNode[] = speakerLayout.map(({ type, value, y, h }) => ({
        id: `speaker-${type}`,
        label: type,
        value,
        kind: 'speaker',
        x: SPEAKER_X,
        y,
        w: NODE_W,
        h: Math.round(h),
        color: type === 'KOL' ? '#10B981' : type === '作者' ? '#06B6D4' : type === '媒体号' ? '#A855F7' : '#F59E0B',
      })
    );

    const links: SankeyLink[] = [];
    contentNodes.forEach((node) => {
      links.push({ sourceId: eventNode.id, targetId: node.id, value: node.value });
      const speakerId = `speaker-${node.meta?.speakerType as SpeakerType}`;
      links.push({ sourceId: node.id, targetId: speakerId, value: node.value });
    });

    return { nodes: [eventNode, ...contentNodes, ...speakerNodes], links };
  }, [event, filteredContent]);

  const nodeById = useMemo(() => {
    const map = new Map<string, SankeyNode>();
    graph.nodes.forEach((node) => map.set(node.id, node));
    return map;
  }, [graph.nodes]);

  const maxLinkValue = useMemo(
    () => Math.max(...graph.links.map((link) => link.value), 1),
    [graph.links]
  );

  const handleNodeJump = (node: SankeyNode) => {
    if (!onPageChange || !event) return;
    if (node.kind === 'content') {
      onPageChange('content-library', { eventId: event.id });
      onOpenChange(false);
      return;
    }
    if (node.kind === 'speaker') {
      const target = node.label === 'KOL' ? 'kol-library' : 'author-library';
      onPageChange(target, {
        eventId: event.id,
        includeKOL: node.label === 'KOL',
      });
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[92vh] !w-[96vw] !max-w-[1200px] overflow-y-auto p-0" showCloseButton>
        <div className="border-b border-gray-200 px-6 py-4">
          <DialogHeader>
            <DialogTitle className="text-xl text-gray-900">事件传播图</DialogTitle>
            <DialogDescription>
              展示 事件 → 内容 → 发声主体 的传播承载关系，定位关键内容节点与关键发声主体
            </DialogDescription>
          </DialogHeader>
        </div>

        {!event ? (
          <div className="px-6 py-10 text-center text-sm text-gray-500">未选择事件，无法生成关系视图。</div>
        ) : (
          <div className="space-y-4 px-6 py-4">
            <div className="grid grid-cols-1 gap-3 rounded-xl border border-gray-200 bg-gray-50 p-3 md:grid-cols-5">
              <div>
                <p className="mb-1 text-xs font-medium text-gray-600">平台</p>
                <Select value={platform} onValueChange={setPlatform}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{platformOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
                </Select>
              </div>
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
                <p className="mb-1 text-xs font-medium text-gray-600">主体类型</p>
                <Select value={speakerType} onValueChange={setSpeakerType}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="全部主体类型">全部主体类型</SelectItem>
                    {SPEAKER_TYPES.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}
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
                  <Checkbox checked={highOnly} onCheckedChange={(checked) => setHighOnly(Boolean(checked))} />
                  只看高互动内容
                </label>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1fr_320px]">
              <div className="rounded-xl border border-gray-200 bg-white p-3">
                <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-gray-600">
                  <Badge className="bg-blue-100 text-blue-700">事件</Badge>
                  <Badge className="bg-sky-100 text-sky-700">内容</Badge>
                  <Badge className="bg-emerald-100 text-emerald-700">发声主体</Badge>
                  <span>点击内容节点可跳转内容库，点击主体节点可跳转KOL/作者库</span>
                </div>

                {graph.nodes.length <= 1 ? (
                  <div className="flex h-[520px] items-center justify-center text-sm text-gray-500">
                    当前筛选条件下暂无可展示节点
                  </div>
                ) : (
                  <svg viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`} className="h-[560px] w-full">
                    {graph.links.filter((link) => link.sourceId === 'event-node').map((link) => {
                      const source = nodeById.get(link.sourceId);
                      const target = nodeById.get(link.targetId);
                      if (!source || !target) return null;
                      const sx = source.x + source.w;
                      const sy = source.y + source.h / 2;
                      const tx = target.x;
                      const ty = target.y + target.h / 2;
                      const width = 1.5 + (link.value / maxLinkValue) * 7;
                      const d = `M ${sx} ${sy} C ${sx + 95} ${sy}, ${tx - 95} ${ty}, ${tx} ${ty}`;
                      return (
                        <path
                          key={`${link.sourceId}-${link.targetId}`}
                          d={d}
                          fill="none"
                          stroke="#93C5FD"
                          strokeOpacity={0.5}
                          strokeWidth={width}
                          strokeLinecap="round"
                          className="cursor-pointer transition-opacity hover:stroke-blue-500"
                          onMouseEnter={() => setHoverInfo({ type: 'link', link, source, target })}
                        />
                      );
                    })}
                    {graph.links.filter((link) => link.sourceId !== 'event-node').map((link) => {
                      const source = nodeById.get(link.sourceId);
                      const target = nodeById.get(link.targetId);
                      if (!source || !target) return null;
                      const sx = source.x + source.w;
                      const sy = source.y + source.h / 2;
                      const tx = target.x;
                      const ty = target.y + target.h / 2;
                      const width = 1.5 + (link.value / maxLinkValue) * 7;
                      const d = `M ${sx} ${sy} C ${sx + 95} ${sy}, ${tx - 95} ${ty}, ${tx} ${ty}`;
                      return (
                        <path
                          key={`${link.sourceId}-${link.targetId}`}
                          d={d}
                          fill="none"
                          stroke="#86EFAC"
                          strokeOpacity={0.48}
                          strokeWidth={width}
                          strokeLinecap="round"
                          className="cursor-pointer transition-opacity hover:stroke-emerald-500"
                          onMouseEnter={() => setHoverInfo({ type: 'link', link, source, target })}
                        />
                      );
                    })}

                    {graph.nodes.map((node) => (
                      <g
                        key={node.id}
                        className={`${node.kind === 'event' ? '' : 'cursor-pointer'}`}
                        onMouseEnter={() => setHoverInfo({ type: 'node', node })}
                        onClick={() => handleNodeJump(node)}
                      >
                        <rect
                          x={node.x}
                          y={node.y}
                          width={node.w}
                          height={node.h}
                          rx={10}
                          fill={node.color}
                          fillOpacity={0.95}
                        />
                        <text x={node.x + 12} y={node.y + 22} fill="#fff" fontSize="12" fontWeight="600">
                          {node.label}
                        </text>
                        {node.h > 40 && (
                          <text x={node.x + 12} y={node.y + 40} fill="#E5E7EB" fontSize="11">
                            权重 {node.value}
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
                    <p>类型：{hoverInfo.node.kind === 'event' ? '事件' : hoverInfo.node.kind === 'content' ? '内容' : '发声主体'}</p>
                    <p>权重：{hoverInfo.node.value}</p>
                    {hoverInfo.node.meta && (
                      <>
                        <p>内容标题：{hoverInfo.node.meta.title}</p>
                        <p>平台：{hoverInfo.node.meta.platform}</p>
                        <p>作者：{hoverInfo.node.meta.author}</p>
                        <p>内容类型：{hoverInfo.node.meta.type}</p>
                        <p>综合互动量：{hoverInfo.node.meta.interaction}</p>
                        <p>评论量：{hoverInfo.node.meta.comments}</p>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="mt-3 space-y-2 text-xs text-gray-700">
                    <p>流向：<span className="font-medium text-gray-900">{hoverInfo.source.label} → {hoverInfo.target.label}</span></p>
                    <p>流线权重：{hoverInfo.link.value}</p>
                  </div>
                )}

                <div className="mt-4 space-y-2">
                  <p className="text-sm font-semibold text-gray-900">快速跳转</p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => event && onPageChange?.('content-library', { eventId: event.id })}
                  >
                    查看内容库
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => event && onPageChange?.('kol-library', { eventId: event.id, includeKOL: true })}
                  >
                    查看KOL库
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full justify-start"
                    onClick={() => event && onPageChange?.('author-library', { eventId: event.id })}
                  >
                    查看作者库
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
