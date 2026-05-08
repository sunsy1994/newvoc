import { useMemo, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { CompetitorContentItem } from './data/competitorLibraryData';
import { formatNumber, getEngagement } from './competitorLibraryUtils';

type SubjectType = '官方' | '经销商';

type RelationViewProps = {
  open: boolean;
  items: CompetitorContentItem[];
  initialBrand?: string;
  timeRangeLabel: string;
  onOpenChange: (open: boolean) => void;
  onDrillDown: (payload: { brand?: string; authorType?: SubjectType; proposition?: string }) => void;
};

type GraphNode = {
  id: string;
  label: string;
  value: number;
  kind: 'brand' | 'subject' | 'proposition';
  x: number;
  y: number;
  w: number;
  h: number;
  color: string;
  meta?: {
    accountCount?: number;
    totalEngagement?: number;
    proposition?: string;
    authorType?: SubjectType;
  };
};

type GraphLink = {
  sourceId: string;
  targetId: string;
  value: number;
  accountCount: number;
  engagement: number;
  titles: string[];
  authorType?: SubjectType;
  proposition?: string;
};

type HoverInfo =
  | { type: 'node'; node: GraphNode }
  | { type: 'link'; link: GraphLink; source: GraphNode; target: GraphNode }
  | null;

const TIME_OPTIONS = ['近7天', '近30天', '全部时间'] as const;
const SVG_WIDTH = 1040;
const SVG_HEIGHT = 560;
const TOP = 26;
const BOTTOM = SVG_HEIGHT - 26;
const BRAND_X = 40;
const SUBJECT_X = 390;
const PROPOSITION_X = 740;
const NODE_W = 220;

function propositionColor(name: string) {
  if (/价格|权益|低息|金融|补贴|团购/.test(name)) return '#F59E0B';
  if (/家庭|品牌|安心|安全/.test(name)) return '#64748B';
  if (/智能|智驾|科技|座舱|空间/.test(name)) return '#06B6D4';
  if (/热点|借势|开学季|春运/.test(name)) return '#F43F5E';
  return '#8B5CF6';
}

function layoutColumn<T extends { value: number }>(
  items: T[],
  opts: { top: number; bottom: number; gap: number; minHeight: number }
) {
  if (items.length === 0) return [] as Array<T & { y: number; h: number }>;
  const available = Math.max(0, opts.bottom - opts.top - opts.gap * (items.length - 1));
  const base = opts.minHeight * items.length;
  const rest = Math.max(0, available - base);
  const total = items.reduce((sum, item) => sum + item.value, 0) || 1;
  let y = opts.top;
  return items.map((item) => {
    const h = opts.minHeight + (item.value / total) * rest;
    const placed = { ...item, y, h };
    y += h + opts.gap;
    return placed;
  });
}

function buildGraph(items: CompetitorContentItem[], activeBrand: string) {
  const brandItems = items.filter((item) => item.brand === activeBrand);
  if (brandItems.length === 0) {
    return { nodes: [] as GraphNode[], links: [] as GraphLink[], summary: '' };
  }

  const groupedBySubject = new Map<SubjectType, CompetitorContentItem[]>();
  const groupedByPair = new Map<string, CompetitorContentItem[]>();
  const propositionSummary = new Map<string, CompetitorContentItem[]>();

  brandItems.forEach((item) => {
    const authorType: SubjectType = item.authorType === '官方' ? '官方' : '经销商';
    const proposition = item.propositionTags[0] ?? '其他命题';
    const pairKey = `${authorType}@@${proposition}`;

    if (!groupedBySubject.has(authorType)) groupedBySubject.set(authorType, []);
    groupedBySubject.get(authorType)?.push(item);

    if (!groupedByPair.has(pairKey)) groupedByPair.set(pairKey, []);
    groupedByPair.get(pairKey)?.push(item);

    if (!propositionSummary.has(proposition)) propositionSummary.set(proposition, []);
    propositionSummary.get(proposition)?.push(item);
  });

  const topPropositions = [...propositionSummary.entries()]
    .map(([name, rows]) => ({
      name,
      rows,
      value: rows.length,
      engagement: rows.reduce((sum, item) => sum + getEngagement(item), 0),
      accountCount: new Set(rows.map((item) => item.author)).size,
    }))
    .sort((a, b) => {
      if (b.value !== a.value) return b.value - a.value;
      return b.engagement - a.engagement;
    })
    .slice(0, 6);

  const propositionSet = new Set(topPropositions.map((item) => item.name));

  const brandNode: GraphNode = {
    id: `brand-${activeBrand}`,
    label: activeBrand,
    value: brandItems.length,
    kind: 'brand',
    x: BRAND_X,
    y: Math.round((SVG_HEIGHT - 92) / 2),
    w: NODE_W,
    h: 92,
    color: '#2563EB',
    meta: {
      accountCount: new Set(brandItems.map((item) => item.author)).size,
      totalEngagement: brandItems.reduce((sum, item) => sum + getEngagement(item), 0),
    },
  };

  const subjectLayout = layoutColumn(
    (['官方', '经销商'] as const)
      .map((authorType) => {
        const rows = groupedBySubject.get(authorType) ?? [];
        return {
          authorType,
          rows,
          value: rows.length,
          accountCount: new Set(rows.map((item) => item.author)).size,
          engagement: rows.reduce((sum, item) => sum + getEngagement(item), 0),
        };
      })
      .filter((item) => item.value > 0),
    { top: TOP, bottom: BOTTOM, gap: 16, minHeight: 62 }
  );

  const subjectNodes: GraphNode[] = subjectLayout.map((item) => ({
    id: `subject-${item.authorType}`,
    label: item.authorType === '官方' ? '官方账号' : '经销商账号',
    value: item.value,
    kind: 'subject',
    x: SUBJECT_X,
    y: Math.round(item.y),
    w: NODE_W,
    h: Math.round(item.h),
    color: item.authorType === '官方' ? '#60A5FA' : '#10B981',
    meta: {
      authorType: item.authorType,
      accountCount: item.accountCount,
      totalEngagement: item.engagement,
    },
  }));

  const propositionLayout = layoutColumn(
    topPropositions.map((item) => ({
      proposition: item.name,
      value: item.value,
      accountCount: item.accountCount,
      engagement: item.engagement,
    })),
    { top: TOP, bottom: BOTTOM, gap: 12, minHeight: 44 }
  );

  const propositionNodes: GraphNode[] = propositionLayout.map((item) => ({
    id: `proposition-${item.proposition}`,
    label: item.proposition,
    value: item.value,
    kind: 'proposition',
    x: PROPOSITION_X,
    y: Math.round(item.y),
    w: NODE_W,
    h: Math.round(item.h),
    color: propositionColor(item.proposition),
    meta: {
      proposition: item.proposition,
      accountCount: item.accountCount,
      totalEngagement: item.engagement,
    },
  }));

  const links: GraphLink[] = [];

  subjectNodes.forEach((node) => {
    const authorType = node.meta?.authorType as SubjectType;
    const rows = groupedBySubject.get(authorType) ?? [];
    links.push({
      sourceId: brandNode.id,
      targetId: node.id,
      value: rows.length,
      accountCount: new Set(rows.map((item) => item.author)).size,
      engagement: rows.reduce((sum, item) => sum + getEngagement(item), 0),
      titles: rows.slice(0, 2).map((item) => item.title),
      authorType,
    });
  });

  propositionNodes.forEach((node) => {
    subjectNodes.forEach((subjectNode) => {
      const authorType = subjectNode.meta?.authorType as SubjectType;
      const proposition = node.meta?.proposition ?? '';
      const rows = groupedByPair.get(`${authorType}@@${proposition}`) ?? [];
      if (rows.length === 0) return;
      links.push({
        sourceId: subjectNode.id,
        targetId: node.id,
        value: rows.length,
        accountCount: new Set(rows.map((item) => item.author)).size,
        engagement: rows.reduce((sum, item) => sum + getEngagement(item), 0),
        titles: rows.slice(0, 2).map((item) => item.title),
        authorType,
        proposition,
      });
    });
  });

  const topTwo = topPropositions.slice(0, 2).map((item) => `“${item.name}”`).join('和');
  const officialCount = groupedBySubject.get('官方')?.length ?? 0;
  const dealerCount = groupedBySubject.get('经销商')?.length ?? 0;
  const dominant = dealerCount > officialCount ? '经销商账号' : officialCount > dealerCount ? '官方账号' : '官方与经销商同步';

  return {
    nodes: [brandNode, ...subjectNodes, ...propositionNodes],
    links,
    summary: `${activeBrand}当前传播主要由${dominant}推动，核心命题集中在${topTwo || '“其他命题”'}。`,
    propositionSet,
  };
}

export default function CompetitorRelationViewDialog({
  open,
  items,
  initialBrand,
  timeRangeLabel,
  onOpenChange,
  onDrillDown,
}: RelationViewProps) {
  const availableBrands = useMemo(() => [...new Set(items.map((item) => item.brand))], [items]);
  const [brand, setBrand] = useState(initialBrand && initialBrand !== '全部品牌' ? initialBrand : '');
  const [timeRange, setTimeRange] = useState<(typeof TIME_OPTIONS)[number]>(
    timeRangeLabel === '近30天' || timeRangeLabel === '全部时间' ? timeRangeLabel : '近7天'
  );
  const [onlyHot, setOnlyHot] = useState(false);
  const [onlyHigh, setOnlyHigh] = useState(false);
  const [hoverInfo, setHoverInfo] = useState<HoverInfo>(null);

  const activeBrand = availableBrands.includes(brand) ? brand : availableBrands[0] ?? '';

  const scopedItems = useMemo(() => {
    return items.filter((item) => {
      const byBrand = item.brand === activeBrand;
      const byHot = !onlyHot || Boolean(item.hotEvent);
      const byHigh = !onlyHigh || getEngagement(item) >= 10000;
      const byTime =
        timeRange === '全部时间'
          ? true
          : timeRange === '近30天'
            ? true
            : new Date(item.publishedAt).getTime() >= new Date('2026-03-03').getTime();
      return byBrand && byHot && byHigh && byTime;
    });
  }, [activeBrand, items, onlyHigh, onlyHot, timeRange]);

  const graph = useMemo(() => buildGraph(scopedItems, activeBrand), [activeBrand, scopedItems]);
  const nodeById = useMemo(() => {
    const map = new Map<string, GraphNode>();
    graph.nodes.forEach((node) => map.set(node.id, node));
    return map;
  }, [graph.nodes]);
  const maxLinkValue = useMemo(() => Math.max(...graph.links.map((item) => item.value), 1), [graph.links]);

  const handleNodeClick = (node: GraphNode) => {
    if (node.kind === 'subject') {
      onDrillDown({ brand: activeBrand, authorType: node.meta?.authorType });
      onOpenChange(false);
    }
    if (node.kind === 'proposition') {
      onDrillDown({ brand: activeBrand, proposition: node.meta?.proposition });
      onOpenChange(false);
    }
  };

  const quickBrands = useMemo(() => {
    return availableBrands.map((brandName) => ({
      brand: brandName,
      count: items.filter((item) => item.brand === brandName).length,
    })).sort((a, b) => b.count - a.count);
  }, [availableBrands, items]);

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-h-[92vh] !w-[96vw] !max-w-[1220px] overflow-y-auto p-0" showCloseButton>
        <div className="border-b border-gray-200 px-6 py-4">
          <DialogHeader>
            <DialogTitle className="text-xl text-gray-900">关系视图</DialogTitle>
            <DialogDescription>
              展示 品牌 → 发声主体 → 传播命题 的传播动作关系，辅助定位单品牌近期主推方向。
            </DialogDescription>
          </DialogHeader>
        </div>

        {graph.nodes.length === 0 ? (
          <div className="px-6 py-10 text-center text-sm text-gray-500">当前筛选条件下暂无可展示节点。</div>
        ) : (
          <div className="space-y-4 px-6 py-4">
            <div className="grid grid-cols-1 gap-3 rounded-xl border border-gray-200 bg-gray-50 p-3 md:grid-cols-4">
              <div>
                <p className="mb-1 text-xs font-medium text-gray-600">品牌</p>
                <Select value={activeBrand} onValueChange={setBrand}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{availableBrands.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
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
                  <Checkbox checked={onlyHot} onCheckedChange={(checked) => setOnlyHot(Boolean(checked))} />
                  只看热点命中内容
                </label>
              </div>
              <div className="flex items-end">
                <label className="flex h-10 w-full items-center gap-2 rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-700">
                  <Checkbox checked={onlyHigh} onCheckedChange={(checked) => setOnlyHigh(Boolean(checked))} />
                  只看高互动内容
                </label>
              </div>
            </div>

            <div className="rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm text-gray-600">
              {graph.summary}
            </div>

            <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1fr_320px]">
              <div className="rounded-xl border border-gray-200 bg-white p-3">
                <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-gray-600">
                  <Badge className="bg-blue-100 text-blue-700">品牌</Badge>
                  <Badge className="bg-sky-100 text-sky-700">发声主体</Badge>
                  <Badge className="bg-emerald-100 text-emerald-700">传播命题</Badge>
                  <span>点击主体或命题节点，可直接联动回竞品内容列表</span>
                </div>

                <svg viewBox={`0 0 ${SVG_WIDTH} ${SVG_HEIGHT}`} className="h-[560px] w-full">
                  {graph.links.map((link) => {
                    const source = nodeById.get(link.sourceId);
                    const target = nodeById.get(link.targetId);
                    if (!source || !target) return null;
                    const sx = source.x + source.w;
                    const sy = source.y + source.h / 2;
                    const tx = target.x;
                    const ty = target.y + target.h / 2;
                    const width = 1.8 + (link.value / maxLinkValue) * 8;
                    const stroke = source.kind === 'brand' ? '#93C5FD' : target.color;
                    const d = `M ${sx} ${sy} C ${sx + 95} ${sy}, ${tx - 95} ${ty}, ${tx} ${ty}`;
                    return (
                      <path
                        key={`${link.sourceId}-${link.targetId}`}
                        d={d}
                        fill="none"
                        stroke={stroke}
                        strokeOpacity={0.46}
                        strokeWidth={width}
                        strokeLinecap="round"
                        className="cursor-pointer transition-opacity hover:opacity-90"
                        onMouseEnter={() => setHoverInfo({ type: 'link', link, source, target })}
                        onMouseLeave={() => setHoverInfo(null)}
                        onClick={() => {
                          onDrillDown({ brand: activeBrand, authorType: link.authorType, proposition: link.proposition });
                          onOpenChange(false);
                        }}
                      />
                    );
                  })}

                  {graph.nodes.map((node) => (
                    <g
                      key={node.id}
                      className={node.kind === 'brand' ? '' : 'cursor-pointer'}
                      onMouseEnter={() => setHoverInfo({ type: 'node', node })}
                      onMouseLeave={() => setHoverInfo(null)}
                      onClick={() => handleNodeClick(node)}
                    >
                      <rect x={node.x} y={node.y} width={node.w} height={node.h} rx={10} fill={node.color} fillOpacity={0.95} />
                      <text x={node.x + 12} y={node.y + 22} fill="#fff" fontSize="12" fontWeight="600">
                        {node.label}
                      </text>
                      {node.h > 40 && (
                        <text x={node.x + 12} y={node.y + 40} fill="#E5E7EB" fontSize="11">
                          内容数 {node.value}
                        </text>
                      )}
                    </g>
                  ))}
                </svg>
              </div>

              <div className="rounded-xl border border-gray-200 bg-gray-50 p-3">
                <p className="text-sm font-semibold text-gray-900">节点信息</p>
                {!hoverInfo ? (
                  <p className="mt-2 text-xs text-gray-500">悬浮节点或流线可查看详情。</p>
                ) : hoverInfo.type === 'node' ? (
                  <div className="mt-3 space-y-2 text-xs text-gray-700">
                    <p>名称：<span className="font-medium text-gray-900">{hoverInfo.node.label}</span></p>
                    <p>类型：{hoverInfo.node.kind === 'brand' ? '品牌' : hoverInfo.node.kind === 'subject' ? '发声主体' : '传播命题'}</p>
                    <p>内容数：{hoverInfo.node.value}</p>
                    <p>覆盖账号：{hoverInfo.node.meta?.accountCount ?? 0}</p>
                    <p>综合互动量：{formatNumber(hoverInfo.node.meta?.totalEngagement ?? 0)}</p>
                  </div>
                ) : (
                  <div className="mt-3 space-y-2 text-xs text-gray-700">
                    <p>流向：<span className="font-medium text-gray-900">{hoverInfo.source.label} → {hoverInfo.target.label}</span></p>
                    <p>内容数：{hoverInfo.link.value}</p>
                    <p>覆盖账号：{hoverInfo.link.accountCount}</p>
                    <p>综合互动量：{formatNumber(hoverInfo.link.engagement)}</p>
                    {hoverInfo.link.titles.slice(0, 2).map((title) => <p key={title}>代表内容：{title}</p>)}
                  </div>
                )}

                <div className="mt-4 space-y-2">
                  <p className="text-sm font-semibold text-gray-900">品牌快捷切换</p>
                  {quickBrands.slice(0, 5).map((item) => (
                    <Button key={item.brand} variant="outline" size="sm" className="w-full justify-between" onClick={() => setBrand(item.brand)}>
                      <span>{item.brand}</span>
                      <span>{item.count} 条</span>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
