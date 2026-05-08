import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowRight,
  Building2,
  CircleHelp,
  Lightbulb,
  Network,
  Sparkles,
  TrendingUp,
  UserRound,
} from 'lucide-react';
import { ResponsiveContainer, Sankey } from 'recharts';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { type CompetitorContentItem } from './data/competitorLibraryData';
import { formatNumber, getEngagement, HIGH_INTERACTION_THRESHOLD } from './competitorLibraryUtils';

type NodeKind = 'brand' | 'author' | 'proposition';

type DrillDownPayload = {
  brand?: string;
  authorType?: '官方' | '经销商';
  proposition?: string;
};

interface BrandRelationshipSankeyProps {
  items: CompetitorContentItem[];
  timeRangeLabel: string;
  selectedBrand?: string;
  onDrillDown: (payload: DrillDownPayload) => void;
}

interface SankeyNodeMeta {
  id: string;
  name: string;
  shortName: string;
  kind: NodeKind;
  color: string;
  contentCount: number;
  totalEngagement: number;
  accountCount: number;
  propositionCategory?: string;
}

interface SankeyLinkMeta {
  source: number;
  target: number;
  value: number;
  color: string;
  sourceId: string;
  targetId: string;
  totalEngagement: number;
  accountCount: number;
  titles: string[];
  ratio: number;
  authorType?: '官方' | '经销商';
  proposition?: string;
}

interface HoverInfoNode {
  type: 'node';
  data: SankeyNodeMeta;
}

interface HoverInfoLink {
  type: 'link';
  data: SankeyLinkMeta;
}

type HoverInfo = HoverInfoNode | HoverInfoLink | null;

function getAuthorColor(authorType: '官方' | '经销商') {
  return authorType === '官方' ? '#2563EB' : '#0F766E';
}

function getPropositionColor(name: string) {
  if (/价格|权益|低息|金融|补贴|团购/.test(name)) return '#F59E0B';
  if (/家庭|品牌|安心|安全/.test(name)) return '#64748B';
  if (/智能|智驾|科技|座舱|空间/.test(name)) return '#06B6D4';
  if (/热点|借势|开学季|春运/.test(name)) return '#F43F5E';
  return '#8B5CF6';
}

function truncateLabel(value: string, maxLength = 7) {
  return value.length > maxLength ? `${value.slice(0, maxLength)}…` : value;
}

function buildRelationshipGraph(items: CompetitorContentItem[], activeBrand: string, timeRangeLabel: string) {
  const brandItems = items.filter((item) => item.brand === activeBrand);
  if (brandItems.length === 0) return null;

  const brandTotalEngagement = brandItems.reduce((sum, item) => sum + getEngagement(item), 0);
  const propositionSource = new Map<string, CompetitorContentItem[]>();
  const authorAccountMap = new Map<'官方' | '经销商', Set<string>>();
  const authorBuckets = new Map<'官方' | '经销商', CompetitorContentItem[]>();
  const propositionByAuthor = new Map<string, CompetitorContentItem[]>();

  brandItems.forEach((item) => {
    const authorKey = item.authorType === '官方' ? '官方' : '经销商';
    const primaryProposition = item.propositionTags[0] ?? '其他命题';

    if (!authorBuckets.has(authorKey)) authorBuckets.set(authorKey, []);
    authorBuckets.get(authorKey)?.push(item);

    if (!authorAccountMap.has(authorKey)) authorAccountMap.set(authorKey, new Set<string>());
    authorAccountMap.get(authorKey)?.add(item.author);

    if (!propositionSource.has(primaryProposition)) propositionSource.set(primaryProposition, []);
    propositionSource.get(primaryProposition)?.push(item);

    const propositionBucketKey = `${authorKey}@@${primaryProposition}`;
    if (!propositionByAuthor.has(propositionBucketKey)) propositionByAuthor.set(propositionBucketKey, []);
    propositionByAuthor.get(propositionBucketKey)?.push(item);
  });

  const sortedPropositions = [...propositionSource.entries()]
    .map(([name, propositionItems]) => ({
      name,
      items: propositionItems,
      count: propositionItems.length,
      engagement: propositionItems.reduce((sum, item) => sum + getEngagement(item), 0),
      accountCount: new Set(propositionItems.map((item) => item.author)).size,
    }))
    .sort((a, b) => {
      if (b.count !== a.count) return b.count - a.count;
      return b.engagement - a.engagement;
    });

  const topPropositions = sortedPropositions.slice(0, 6);
  const hiddenPropositions = sortedPropositions.slice(6);
  if (hiddenPropositions.length > 0) {
    topPropositions.push({
      name: '其他命题',
      items: hiddenPropositions.flatMap((item) => item.items),
      count: hiddenPropositions.reduce((sum, item) => sum + item.count, 0),
      engagement: hiddenPropositions.reduce((sum, item) => sum + item.engagement, 0),
      accountCount: new Set(hiddenPropositions.flatMap((item) => item.items.map((row) => row.author))).size,
    });
  }

  const allowedPropositions = new Set(topPropositions.map((item) => item.name));
  const normalizedProposition = (value: string) => (allowedPropositions.has(value) ? value : '其他命题');

  const nodes: SankeyNodeMeta[] = [];
  const links: SankeyLinkMeta[] = [];

  const pushNode = (node: SankeyNodeMeta) => {
    nodes.push(node);
    return nodes.length - 1;
  };

  const brandIndex = pushNode({
    id: `brand-${activeBrand}`,
    name: activeBrand,
    shortName: activeBrand,
    kind: 'brand',
    color: '#111827',
    contentCount: brandItems.length,
    totalEngagement: brandTotalEngagement,
    accountCount: new Set(brandItems.map((item) => item.author)).size,
  });

  const authorIndexMap = new Map<'官方' | '经销商', number>();
  (['官方', '经销商'] as const).forEach((authorType) => {
    const bucket = authorBuckets.get(authorType) ?? [];
    if (bucket.length === 0) return;
    authorIndexMap.set(
      authorType,
      pushNode({
        id: `author-${authorType}`,
        name: authorType === '官方' ? '官方账号' : '经销商账号',
        shortName: authorType === '官方' ? '官方' : '经销商',
        kind: 'author',
        color: getAuthorColor(authorType),
        contentCount: bucket.length,
        totalEngagement: bucket.reduce((sum, item) => sum + getEngagement(item), 0),
        accountCount: authorAccountMap.get(authorType)?.size ?? 0,
      })
    );
  });

  const propositionIndexMap = new Map<string, number>();
  topPropositions.forEach((item) => {
    propositionIndexMap.set(
      item.name,
      pushNode({
        id: `proposition-${item.name}`,
        name: item.name,
        shortName: truncateLabel(item.name),
        kind: 'proposition',
        color: getPropositionColor(item.name),
        contentCount: item.count,
        totalEngagement: item.engagement,
        accountCount: item.accountCount,
        propositionCategory: /价格|权益|低息|金融|补贴|团购/.test(item.name)
          ? '价格 / 金融'
          : /家庭|品牌|安心|安全/.test(item.name)
            ? '品牌 / 家庭'
            : /智能|智驾|科技|座舱|空间/.test(item.name)
              ? '科技 / 场景'
              : /热点|借势|开学季|春运/.test(item.name)
                ? '热点借势'
                : '其他',
      })
    );
  });

  authorIndexMap.forEach((nodeIndex, authorType) => {
    const bucket = authorBuckets.get(authorType) ?? [];
    const value = bucket.length;
    links.push({
      source: brandIndex,
      target: nodeIndex,
      value,
      color: getAuthorColor(authorType),
      sourceId: nodes[brandIndex].id,
      targetId: nodes[nodeIndex].id,
      totalEngagement: bucket.reduce((sum, item) => sum + getEngagement(item), 0),
      accountCount: authorAccountMap.get(authorType)?.size ?? 0,
      titles: bucket.slice(0, 2).map((item) => item.title),
      ratio: value / brandItems.length,
      authorType,
    });
  });

  propositionByAuthor.forEach((bucket, key) => {
    const [authorType] = key.split('@@') as ['官方' | '经销商', string];
    const propositionName = normalizedProposition(bucket[0]?.propositionTags[0] ?? '其他命题');
    const sourceIndex = authorIndexMap.get(authorType);
    const targetIndex = propositionIndexMap.get(propositionName);

    if (sourceIndex === undefined || targetIndex === undefined) return;

    const sameLink = links.find(
      (item) => item.source === sourceIndex && item.target === targetIndex && item.proposition === propositionName
    );

    if (sameLink) {
      const accountSet = new Set<string>(bucket.map((item) => item.author));
      sameLink.value += bucket.length;
      sameLink.totalEngagement += bucket.reduce((sum, item) => sum + getEngagement(item), 0);
      sameLink.accountCount = Math.max(sameLink.accountCount, accountSet.size);
      sameLink.titles = [...sameLink.titles, ...bucket.slice(0, 2).map((item) => item.title)].slice(0, 2);
      sameLink.ratio = sameLink.value / ((authorBuckets.get(authorType) ?? []).length || 1);
      return;
    }

    links.push({
      source: sourceIndex,
      target: targetIndex,
      value: bucket.length,
      color: nodes[targetIndex].color,
      sourceId: nodes[sourceIndex].id,
      targetId: nodes[targetIndex].id,
      totalEngagement: bucket.reduce((sum, item) => sum + getEngagement(item), 0),
      accountCount: new Set(bucket.map((item) => item.author)).size,
      titles: bucket.slice(0, 2).map((item) => item.title),
      ratio: bucket.length / ((authorBuckets.get(authorType) ?? []).length || 1),
      authorType,
      proposition: propositionName,
    });
  });

  const officialCount = authorBuckets.get('官方')?.length ?? 0;
  const dealerCount = authorBuckets.get('经销商')?.length ?? 0;
  const dominantSpeaker = dealerCount > officialCount ? '经销商账号' : officialCount > dealerCount ? '官方账号' : '官方与经销商同步';
  const topTopics = topPropositions.slice(0, 2).map((item) => `“${item.name}”`).join('和');
  const widestTopic = [...topPropositions].sort((a, b) => {
    if (b.accountCount !== a.accountCount) return b.accountCount - a.accountCount;
    return b.count - a.count;
  })[0];

  const topDealerAccounts = [...new Set(brandItems.filter((item) => item.authorType === '经销商').map((item) => item.author))]
    .map((author) => {
      const posts = brandItems.filter((item) => item.author === author);
      return {
        author,
        count: posts.length,
        engagement: posts.reduce((sum, item) => sum + getEngagement(item), 0),
      };
    })
    .sort((a, b) => {
      if (b.count !== a.count) return b.count - a.count;
      return b.engagement - a.engagement;
    })
    .slice(0, 3);

  const topContent = [...brandItems]
    .sort((a, b) => getEngagement(b) - getEngagement(a))
    .slice(0, 3)
    .map((item) => ({
      id: item.id,
      title: item.title,
      engagement: getEngagement(item),
      authorType: item.authorType,
      proposition: item.propositionTags[0] ?? '其他命题',
    }));

  return {
    chartData: {
      nodes,
      links,
    },
    summary: `在${timeRangeLabel}内，${activeBrand}的传播动作主要由${dominantSpeaker}推动，核心命题集中在${topTopics || '“其他命题”'}，其中${widestTopic ? `“${widestTopic.name}”覆盖账号最多` : '命题分布相对平均'}。`,
    stats: {
      totalCount: brandItems.length,
      totalEngagement: brandTotalEngagement,
      officialCount,
      dealerCount,
      accountCount: new Set(brandItems.map((item) => item.author)).size,
    },
    topPropositions,
    topDealerAccounts,
    topContent,
  };
}

export default function BrandRelationshipSankey({
  items,
  timeRangeLabel,
  selectedBrand,
  onDrillDown,
}: BrandRelationshipSankeyProps) {
  const availableBrands = useMemo(() => {
    return [...new Set(items.map((item) => item.brand))].sort((a, b) => {
      const aCount = items.filter((item) => item.brand === a).length;
      const bCount = items.filter((item) => item.brand === b).length;
      return bCount - aCount;
    });
  }, [items]);

  const [localBrand, setLocalBrand] = useState(selectedBrand && selectedBrand !== '全部品牌' ? selectedBrand : '');
  const [hoverInfo, setHoverInfo] = useState<HoverInfo>(null);

  useEffect(() => {
    if (selectedBrand && selectedBrand !== '全部品牌' && availableBrands.includes(selectedBrand)) {
      setLocalBrand(selectedBrand);
      return;
    }
    if (!availableBrands.includes(localBrand)) {
      setLocalBrand(availableBrands[0] ?? '');
    }
  }, [availableBrands, localBrand, selectedBrand]);

  const activeBrand = selectedBrand && selectedBrand !== '全部品牌' ? selectedBrand : localBrand;
  const graph = useMemo(() => buildRelationshipGraph(items, activeBrand, timeRangeLabel), [activeBrand, items, timeRangeLabel]);

  const activeKey =
    hoverInfo?.type === 'node' ? hoverInfo.data.id : hoverInfo?.type === 'link' ? `${hoverInfo.data.sourceId}-${hoverInfo.data.targetId}` : '';

  if (availableBrands.length === 0 || !graph) {
    return (
      <section className="rounded-[28px] border border-dashed border-slate-300/90 bg-white/80 p-6 shadow-sm backdrop-blur">
        <div className="flex items-center gap-3 text-slate-700">
          <Network className="h-5 w-5" />
          <div>
            <h3 className="text-lg font-semibold">单品牌竞品传播动作图</h3>
            <p className="text-sm text-slate-500">当前筛选范围内暂无可用于生成关系图的数据。</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 18 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="overflow-hidden rounded-[30px] border border-slate-200/80 bg-[radial-gradient(circle_at_top_left,_rgba(14,165,233,0.18),_transparent_28%),linear-gradient(145deg,_rgba(255,255,255,0.96),_rgba(241,245,249,0.92))] shadow-[0_24px_60px_rgba(15,23,42,0.08)]"
    >
      <div className="border-b border-slate-200/80 px-6 py-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-3xl">
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-sky-200/80 bg-white/80 px-3 py-1 text-[11px] font-medium uppercase tracking-[0.22em] text-sky-700">
              <Sparkles className="h-3.5 w-3.5" />
              Brand Narrative Flow
            </div>
            <div className="flex items-center gap-2">
              <h3 className="text-2xl font-semibold tracking-tight text-slate-950">单品牌竞品传播动作图</h3>
              <Tooltip>
                <TooltipTrigger asChild>
                  <button type="button" className="rounded-full p-1 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700">
                    <CircleHelp className="h-4 w-4" />
                  </button>
                </TooltipTrigger>
                <TooltipContent side="right" className="max-w-xs bg-slate-950 text-slate-50">
                  三层结构：品牌 → 发声主体 → 传播命题。流线宽度默认按内容数计算，hover 查看互动量、覆盖账号和代表内容。
                </TooltipContent>
              </Tooltip>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-600">{graph.summary}</p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Select value={activeBrand} onValueChange={setLocalBrand}>
              <SelectTrigger className="w-[180px] border-slate-200 bg-white/80">
                <SelectValue placeholder="选择品牌" />
              </SelectTrigger>
              <SelectContent>
                {availableBrands.map((brand) => (
                  <SelectItem key={brand} value={brand}>
                    {brand}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <div className="grid min-w-[280px] grid-cols-2 gap-2 sm:grid-cols-4">
              <div className="rounded-2xl border border-slate-200/80 bg-white/85 px-3 py-2">
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">内容数</p>
                <p className="mt-1 text-lg font-semibold text-slate-950">{graph.stats.totalCount}</p>
              </div>
              <div className="rounded-2xl border border-slate-200/80 bg-white/85 px-3 py-2">
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">账号数</p>
                <p className="mt-1 text-lg font-semibold text-slate-950">{graph.stats.accountCount}</p>
              </div>
              <div className="rounded-2xl border border-slate-200/80 bg-white/85 px-3 py-2">
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">官方</p>
                <p className="mt-1 text-lg font-semibold text-blue-700">{graph.stats.officialCount}</p>
              </div>
              <div className="rounded-2xl border border-slate-200/80 bg-white/85 px-3 py-2">
                <p className="text-[11px] uppercase tracking-[0.18em] text-slate-400">经销商</p>
                <p className="mt-1 text-lg font-semibold text-teal-700">{graph.stats.dealerCount}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 p-6 xl:grid-cols-[minmax(0,1.5fr)_360px]">
        <div className="rounded-[28px] border border-slate-200/70 bg-slate-950/[0.02] p-4">
          <div className="mb-4 flex flex-wrap items-center gap-3 text-xs text-slate-500">
            <Badge className="bg-slate-950 text-white hover:bg-slate-900">品牌</Badge>
            <Badge className="bg-blue-600 text-white hover:bg-blue-600">官方</Badge>
            <Badge className="bg-teal-700 text-white hover:bg-teal-700">经销商</Badge>
            <span>命题按品类分色，默认展示 Top 6，其余合并为“其他命题”。</span>
          </div>

          <div className="h-[420px]">
            <ResponsiveContainer width="100%" height="100%">
              <Sankey
                data={graph.chartData}
                nodePadding={24}
                nodeWidth={18}
                margin={{ left: 18, right: 160, top: 24, bottom: 24 }}
                iterations={48}
                linkCurvature={0.45}
                node={(props: any) => {
                  const node = props.payload as SankeyNodeMeta | undefined;
                  if (!node) return <g />;
                  const isActive =
                    !hoverInfo ||
                    hoverInfo.type === 'node'
                      ? hoverInfo?.type !== 'node' || hoverInfo.data.id === node.id
                      : hoverInfo.data.sourceId === node.id || hoverInfo.data.targetId === node.id;

                  const fillOpacity = isActive ? 1 : 0.28;

                  return (
                    <g
                      onMouseEnter={() => setHoverInfo({ type: 'node', data: node })}
                      onMouseLeave={() => setHoverInfo(null)}
                      onClick={() => {
                        if (node.kind === 'author') {
                          onDrillDown({
                            brand: activeBrand,
                            authorType: node.shortName as '官方' | '经销商',
                          });
                        }
                        if (node.kind === 'proposition') {
                          onDrillDown({
                            brand: activeBrand,
                            proposition: node.name === '其他命题' ? undefined : node.name,
                          });
                        }
                      }}
                      className={node.kind !== 'brand' ? 'cursor-pointer' : ''}
                    >
                      <rect
                        x={props.x}
                        y={props.y}
                        width={props.width}
                        height={Math.max(props.height, 16)}
                        rx={8}
                        fill={node.color}
                        fillOpacity={fillOpacity}
                        stroke="rgba(255,255,255,0.65)"
                        strokeWidth={1}
                      />
                      <text
                        x={(props.x ?? 0) + (props.width ?? 0) + 10}
                        y={(props.y ?? 0) + Math.max((props.height ?? 16) / 2, 12)}
                        fill={isActive ? '#0F172A' : '#94A3B8'}
                        fontSize={12}
                        dominantBaseline="middle"
                        fontWeight={600}
                      >
                        {node.name}
                      </text>
                      <text
                        x={(props.x ?? 0) + (props.width ?? 0) + 10}
                        y={(props.y ?? 0) + Math.max((props.height ?? 16) / 2, 12) + 15}
                        fill={isActive ? '#64748B' : '#CBD5E1'}
                        fontSize={11}
                        dominantBaseline="middle"
                      >
                        {node.contentCount} 条
                      </text>
                    </g>
                  );
                }}
                link={(props: any) => {
                  const link = props.payload as SankeyLinkMeta | undefined;
                  if (!link) return <g />;

                  const path = `M${props.sourceX},${props.sourceY}C${props.sourceControlX},${props.sourceY} ${props.targetControlX},${props.targetY} ${props.targetX},${props.targetY}`;
                  const isActive =
                    !hoverInfo ||
                    (hoverInfo.type === 'node'
                      ? hoverInfo.data.id === link.sourceId || hoverInfo.data.id === link.targetId
                      : `${link.sourceId}-${link.targetId}` === activeKey);

                  return (
                    <path
                      d={path}
                      fill="none"
                      stroke={link.color}
                      strokeOpacity={isActive ? 0.78 : 0.16}
                      strokeWidth={Math.max(props.linkWidth, 10)}
                      strokeLinecap="round"
                      onMouseEnter={() => setHoverInfo({ type: 'link', data: link })}
                      onMouseLeave={() => setHoverInfo(null)}
                      onClick={() =>
                        onDrillDown({
                          brand: activeBrand,
                          authorType: link.authorType,
                          proposition: link.proposition,
                        })
                      }
                      className="cursor-pointer transition-opacity"
                    />
                  );
                }}
              />
            </ResponsiveContainer>
          </div>

          <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-slate-500">
            <Lightbulb className="h-4 w-4 text-amber-500" />
            点击主体节点、命题节点或流线，会联动下方内容列表到相应筛选条件。
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
              <Network className="h-4 w-4 text-sky-600" />
              Hover 详情
            </div>
            {!hoverInfo && (
              <div className="rounded-2xl border border-dashed border-slate-200 p-4 text-sm leading-6 text-slate-500">
                将鼠标移到节点或流线上查看细节，包括内容数、覆盖账号数、互动量和代表内容。
              </div>
            )}
            {hoverInfo?.type === 'node' && (
              <div className="space-y-3">
                <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-950">{hoverInfo.data.name}</p>
                      <p className="text-xs text-slate-500">
                        {hoverInfo.data.kind === 'brand'
                          ? '品牌主节点'
                          : hoverInfo.data.kind === 'author'
                            ? '发声主体节点'
                            : `传播命题 · ${hoverInfo.data.propositionCategory ?? '其他'}`}
                      </p>
                    </div>
                    <span className="rounded-full px-2 py-1 text-[11px] font-medium" style={{ backgroundColor: `${hoverInfo.data.color}18`, color: hoverInfo.data.color }}>
                      {hoverInfo.data.contentCount} 条内容
                    </span>
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                    <div className="rounded-xl bg-white p-3">
                      <p className="text-slate-400">覆盖账号</p>
                      <p className="mt-1 font-semibold text-slate-900">{hoverInfo.data.accountCount}</p>
                    </div>
                    <div className="rounded-xl bg-white p-3">
                      <p className="text-slate-400">综合互动</p>
                      <p className="mt-1 font-semibold text-slate-900">{formatNumber(hoverInfo.data.totalEngagement)}</p>
                    </div>
                    <div className="rounded-xl bg-white p-3">
                      <p className="text-slate-400">节点层级</p>
                      <p className="mt-1 font-semibold text-slate-900">
                        {hoverInfo.data.kind === 'brand' ? '品牌' : hoverInfo.data.kind === 'author' ? '主体' : '命题'}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
            {hoverInfo?.type === 'link' && (
              <div className="space-y-3">
                <div className="rounded-2xl border border-slate-200 bg-slate-50/80 p-4">
                  <div className="flex items-center gap-2 text-sm font-semibold text-slate-950">
                    <ArrowRight className="h-4 w-4 text-sky-600" />
                    流线详情
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-xs">
                    <div className="rounded-xl bg-white p-3">
                      <p className="text-slate-400">内容数</p>
                      <p className="mt-1 font-semibold text-slate-900">{hoverInfo.data.value}</p>
                    </div>
                    <div className="rounded-xl bg-white p-3">
                      <p className="text-slate-400">占比</p>
                      <p className="mt-1 font-semibold text-slate-900">{Math.round(hoverInfo.data.ratio * 100)}%</p>
                    </div>
                    <div className="rounded-xl bg-white p-3">
                      <p className="text-slate-400">覆盖账号</p>
                      <p className="mt-1 font-semibold text-slate-900">{hoverInfo.data.accountCount}</p>
                    </div>
                  </div>
                  <div className="mt-3 rounded-xl bg-white p-3 text-xs text-slate-600">
                    <p>综合互动量：<span className="font-semibold text-slate-900">{formatNumber(hoverInfo.data.totalEngagement)}</span></p>
                    {hoverInfo.data.titles.length > 0 && (
                      <div className="mt-2 space-y-1">
                        {hoverInfo.data.titles.map((title) => (
                          <p key={title} className="line-clamp-2">
                            {title}
                          </p>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
              <TrendingUp className="h-4 w-4 text-amber-500" />
              Top 命题
            </div>
            <div className="space-y-2">
              {graph.topPropositions.map((item, index) => (
                <button
                  key={item.name}
                  type="button"
                  onClick={() => onDrillDown({ brand: activeBrand, proposition: item.name === '其他命题' ? undefined : item.name })}
                  className="flex w-full cursor-pointer items-center justify-between rounded-2xl border border-slate-200 bg-slate-50/80 px-3 py-3 text-left transition hover:border-slate-300 hover:bg-white"
                >
                  <div>
                    <p className="text-sm font-semibold text-slate-900">#{index + 1} {item.name}</p>
                    <p className="text-xs text-slate-500">内容 {item.count} 条 · 账号 {item.accountCount} 个</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-slate-950">{formatNumber(item.engagement)}</p>
                    <p className="text-[11px] text-slate-400">互动量</p>
                  </div>
                </button>
              ))}
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
              <Building2 className="h-4 w-4 text-teal-600" />
              Top 经销商账号
            </div>
            <div className="space-y-2">
              {graph.topDealerAccounts.length === 0 && (
                <div className="rounded-2xl border border-dashed border-slate-200 p-4 text-sm text-slate-500">
                  当前品牌暂无经销商账号样本。
                </div>
              )}
              {graph.topDealerAccounts.map((row, index) => (
                <div key={row.author} className="rounded-2xl border border-slate-200 bg-slate-50/80 px-3 py-3">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">#{index + 1} {row.author}</p>
                      <p className="text-xs text-slate-500">发文 {row.count} 条</p>
                    </div>
                    <p className="text-sm font-semibold text-slate-950">{formatNumber(row.engagement)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[28px] border border-slate-200/80 bg-white/90 p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-900">
              <UserRound className="h-4 w-4 text-violet-600" />
              高互动样本
            </div>
            <div className="space-y-2">
              {graph.topContent.map((item) => (
                <Button
                  key={item.id}
                  type="button"
                  variant="ghost"
                  onClick={() => onDrillDown({ brand: activeBrand, proposition: item.proposition })}
                  className="h-auto w-full justify-between rounded-2xl border border-slate-200 bg-slate-50/80 px-3 py-3 text-left hover:bg-white"
                >
                  <div className="pr-3">
                    <p className="line-clamp-2 text-sm font-semibold text-slate-900">{item.title}</p>
                    <p className="mt-1 text-xs text-slate-500">{item.authorType} · {item.proposition}</p>
                  </div>
                  <div className="shrink-0 text-right">
                    <p className="text-sm font-semibold text-slate-950">{formatNumber(item.engagement)}</p>
                    <p className="text-[11px] text-slate-400">
                      {item.engagement >= HIGH_INTERACTION_THRESHOLD ? '高互动' : '常规'}
                    </p>
                  </div>
                </Button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </motion.section>
  );
}
