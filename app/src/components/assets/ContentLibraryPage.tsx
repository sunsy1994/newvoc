import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowUpDown,
  BarChart3,
  BookOpenCheck,
  CalendarRange,
  ChevronRight,
  ExternalLink,
  Filter,
  LayoutGrid,
  MessageSquare,
  Search,
  ShieldAlert,
  TrendingUp,
  UserCircle2,
  Users,
} from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { eventLibraryData } from './data/eventLibraryData';
import {
  authorTypeOptions,
  commentFocusOptions,
  confidenceOptions,
  contentLibraryData,
  contentSortOptions,
  contentTypeOptions,
  interactionRangeOptions,
  platformOptions,
  publishRangeOptions,
  tagFilterOptions,
  valueFilterOptions,
  type ContentDistributionItem,
  type ContentLibraryItem,
} from './data/contentLibraryData';
import type { AssetNavigationContext, AssetPageChangeHandler } from './assetNavigation';
import AssetFilterField from './AssetFilterField';
import { getEventStoryFocus } from './eventVocStrategy';

interface ContentLibraryPageProps {
  onPageChange: AssetPageChangeHandler;
  navigationContext?: AssetNavigationContext;
}

type SortKey = (typeof contentSortOptions)[number]['value'];

const numberFormatter = new Intl.NumberFormat('zh-CN');
const now = new Date('2026-03-08');

function formatNumber(value: number) {
  return numberFormatter.format(value);
}

function getInteractionThreshold(range: string) {
  if (range === '500+') return 500;
  if (range === '1,000+') return 1000;
  if (range === '3,000+') return 3000;
  if (range === '5,000+') return 5000;
  return 0;
}

function getValueLevelScore(level: ContentLibraryItem['valueLevel']) {
  if (level === '高') return 3;
  if (level === '中') return 2;
  return 1;
}

function getTagItems(item: ContentLibraryItem, tagFilter: (typeof tagFilterOptions)[number]) {
  if (tagFilter === '命题') return item.propositionTags;
  if (tagFilter === '问题') return item.issueTags;
  if (tagFilter === '证据') return item.evidenceTags;
  if (tagFilter === '风险') return item.riskTags;
  return [...item.propositionTags, ...item.issueTags, ...item.evidenceTags, ...item.riskTags];
}

function distributionBarColor(label: string) {
  if (label.includes('负') || label === '质疑') return 'bg-orange-500';
  if (label.includes('正') || label === '认可') return 'bg-emerald-500';
  if (label === '车主') return 'bg-blue-500';
  if (label === '准车主') return 'bg-sky-500';
  if (label === '试驾') return 'bg-indigo-500';
  return 'bg-slate-400';
}

function badgeClass(flag: string) {
  if (flag === '高证据') return 'bg-emerald-100 text-emerald-700';
  if (flag === '高争议') return 'bg-orange-100 text-orange-700';
  if (flag === '高意向') return 'bg-blue-100 text-blue-700';
  if (flag === '核心内容') return 'bg-slate-900 text-white';
  return 'bg-sky-100 text-sky-700';
}

function valueLevelClass(level: ContentLibraryItem['valueLevel']) {
  if (level === '高') return 'text-slate-950';
  if (level === '中') return 'text-slate-700';
  return 'text-slate-500';
}

function getContentDecisionSignal(item: ContentLibraryItem, eventType: string) {
  const scenario = getEventStoryFocus(eventType).scenario;
  if (scenario === '营销事件') {
    if (item.valueFlags.includes('高意向')) return '适合复用为精准投放素材，优先观察评论中的试驾/购买表达。';
    if (item.valueFlags.includes('高互动')) return '适合做声量放大素材，但需要同步核查有效互动率和误伤风险。';
    return '适合沉淀为补充素材，需继续观察是否能触发目标人群表达。';
  }

  if (item.valueFlags.includes('高证据')) return '适合作为产品/售后/公关响应证据，优先回溯高置信评论。';
  if (item.valueFlags.includes('高争议')) return '需要判断争议是否有真实证据支撑，避免只按热度响应。';
  return '适合作为舆情背景样本，重点看问题标签是否持续聚集。';
}

function DistributionBars({
  title,
  items,
}: {
  title: string;
  items: ContentDistributionItem[];
}) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
      <p className="text-sm font-medium text-gray-900">{title}</p>
      <div className="mt-3 space-y-3">
        {items.map((item) => (
          <div key={item.label}>
            <div className="mb-1 flex items-center justify-between text-xs text-gray-600">
              <span>{item.label}</span>
              <span>{item.value}%</span>
            </div>
            <div className="h-2 overflow-hidden rounded-full bg-gray-100">
              <div
                className={`h-full rounded-full ${distributionBarColor(item.label)}`}
                style={{ width: `${item.value}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ContentLibraryPage({ onPageChange, navigationContext }: ContentLibraryPageProps) {
  const [selectedEventId, setSelectedEventId] = useState(navigationContext?.eventId ?? 'EVT-2026-001');
  const [keyword, setKeyword] = useState(navigationContext?.keyword ?? '');
  const [platform, setPlatform] = useState<(typeof platformOptions)[number]>('全部平台');
  const [contentType, setContentType] = useState<(typeof contentTypeOptions)[number]>('全部类型');
  const [authorType, setAuthorType] = useState<(typeof authorTypeOptions)[number]>('全部作者');
  const [publishRange, setPublishRange] = useState<(typeof publishRangeOptions)[number]>('近30天');
  const [interactionRange, setInteractionRange] = useState<(typeof interactionRangeOptions)[number]>('全部互动');
  const [tagFilter, setTagFilter] = useState<(typeof tagFilterOptions)[number]>('全部标签');
  const [confidence, setConfidence] = useState<(typeof confidenceOptions)[number]>('全部样本');
  const [valueFilter, setValueFilter] = useState<(typeof valueFilterOptions)[number]>('全部价值');
  const [commentFocus, setCommentFocus] = useState<(typeof commentFocusOptions)[number]>('全部评论结构');
  const [sortBy, setSortBy] = useState<SortKey>('engagement');
  const [selectedContent, setSelectedContent] = useState<ContentLibraryItem | null>(null);
  const [lockedAuthorId, setLockedAuthorId] = useState<string | null>(navigationContext?.authorId ?? null);

  const selectedEvent = useMemo(
    () => eventLibraryData.find((event) => event.id === selectedEventId) ?? eventLibraryData[0],
    [selectedEventId]
  );
  const selectedEventFocus = useMemo(() => getEventStoryFocus(selectedEvent.type), [selectedEvent.type]);

  const filteredList = useMemo(() => {
    const rangeDays = {
      全部时间: Number.POSITIVE_INFINITY,
      近7天: 7,
      近30天: 30,
      近90天: 90,
    }[publishRange];
    const minEngagement = getInteractionThreshold(interactionRange);

    return contentLibraryData
      .filter((item) => item.eventId === selectedEvent.id)
      .filter((item) => {
        const q = keyword.trim().toLowerCase();
        const keywordMatched =
          q.length === 0 ||
          item.title.toLowerCase().includes(q) ||
          item.summary.toLowerCase().includes(q) ||
          item.authorName.toLowerCase().includes(q);

        const dayDiff = Math.floor(
          (now.getTime() - new Date(item.publishedAt.replace(' ', 'T')).getTime()) / (1000 * 60 * 60 * 24)
        );
        const rangeMatched = rangeDays === Number.POSITIVE_INFINITY || dayDiff <= rangeDays;
        const platformMatched = platform === '全部平台' || item.platform === platform;
        const contentTypeMatched = contentType === '全部类型' || item.contentType === contentType;
        const authorTypeMatched = authorType === '全部作者' || item.authorType === authorType;
        const interactionMatched = item.engagementTotal >= minEngagement;
        const confidenceMatched = confidence === '全部样本' || item.isHighConfidenceSample;
        const authorLockedMatched = lockedAuthorId === null || item.authorId === lockedAuthorId;
        const tagMatched = tagFilter === '全部标签' || getTagItems(item, tagFilter).length > 0;
        const valueMatched = valueFilter === '全部价值' || item.valueFlags.includes(valueFilter);
        const commentMatched =
          commentFocus === '全部评论结构' ||
          (commentFocus === '车主占比高' && item.commentProfile.ownerRate >= 30) ||
          (commentFocus === '试驾占比高' && item.commentProfile.testDriveRate >= 20) ||
          (commentFocus === '质疑占比高' && item.commentProfile.doubtRate >= 35) ||
          (commentFocus === '认可占比高' && item.commentProfile.approvalRate >= 45) ||
          (commentFocus === '高置信占比高' && item.commentProfile.highConfidenceRate >= 65) ||
          (commentFocus === '负向占比高' && item.commentProfile.negativeRate >= 35);

        return (
          keywordMatched &&
          rangeMatched &&
          platformMatched &&
          contentTypeMatched &&
          authorTypeMatched &&
          interactionMatched &&
          confidenceMatched &&
          tagMatched &&
          valueMatched &&
          commentMatched &&
          authorLockedMatched
        );
      })
      .sort((a, b) => {
        if (sortBy === 'comments') return b.commentCount - a.commentCount;
        if (sortBy === 'highConfidence') return b.commentProfile.highConfidenceRate - a.commentProfile.highConfidenceRate;
        if (sortBy === 'ownerRate') return b.commentProfile.ownerRate - a.commentProfile.ownerRate;
        if (sortBy === 'doubtRate') return b.commentProfile.doubtRate - a.commentProfile.doubtRate;
        if (sortBy === 'positiveRate') return b.commentProfile.positiveRate - a.commentProfile.positiveRate;
        if (sortBy === 'publishedAt') {
          return new Date(b.publishedAt.replace(' ', 'T')).getTime() - new Date(a.publishedAt.replace(' ', 'T')).getTime();
        }
        if (sortBy === 'valueLevel') return getValueLevelScore(b.valueLevel) - getValueLevelScore(a.valueLevel);
        return b.engagementTotal - a.engagementTotal;
      });
  }, [
    authorType,
    commentFocus,
    confidence,
    contentType,
    interactionRange,
    keyword,
    lockedAuthorId,
    platform,
    publishRange,
    selectedEvent.id,
    sortBy,
    tagFilter,
    valueFilter,
  ]);

  const summary = useMemo(() => {
    const totalComments = filteredList.reduce((sum, item) => sum + item.commentCount, 0);
    const totalEngagement = filteredList.reduce((sum, item) => sum + item.engagementTotal, 0);
    const kolCount = filteredList.filter((item) => item.isKOL).length;
    const highEngagementCount = filteredList.filter((item) => item.valueFlags.includes('高互动')).length;
    const highEvidenceCount = filteredList.filter((item) => item.valueFlags.includes('高证据')).length;
    const highControversyCount = filteredList.filter((item) => item.valueFlags.includes('高争议')).length;
    const averageHighConfidenceRate = filteredList.length === 0 ? 0 : Math.round(filteredList.reduce((sum, item) => sum + item.commentProfile.highConfidenceRate, 0) / filteredList.length);
    const typeMap = new Map<string, number>();
    filteredList.forEach((item) => {
      typeMap.set(item.contentType, (typeMap.get(item.contentType) ?? 0) + 1);
    });
    const topTypes = [...typeMap.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3);
    return {
      totalComments,
      totalEngagement,
      kolCount,
      highEngagementCount,
      highEvidenceCount,
      highControversyCount,
      averageHighConfidenceRate,
      topTypes,
    };
  }, [filteredList]);

  useEffect(() => {
    let cancelled = false;

    queueMicrotask(() => {
      if (cancelled) return;

      setSelectedEventId(navigationContext?.eventId ?? 'EVT-2026-001');
      setKeyword(navigationContext?.keyword ?? '');
      setLockedAuthorId(navigationContext?.authorId ?? null);
      setSelectedContent(
        navigationContext?.contentId
          ? contentLibraryData.find((item) => item.id === navigationContext.contentId) ?? null
          : null
      );
    });

    return () => {
      cancelled = true;
    };
  }, [navigationContext]);

  const jumpToPage = (page: 'comment-library' | 'author-library', context?: AssetNavigationContext) => {
    setSelectedContent(null);
    onPageChange(page, context);
  };

  const focusSameAuthorContent = (item: ContentLibraryItem) => {
    setSelectedContent(null);
    setSelectedEventId(item.eventId);
    setKeyword(item.authorName);
    setLockedAuthorId(item.authorId);
  };

  const resetFilters = () => {
    setKeyword('');
    setPlatform('全部平台');
    setContentType('全部类型');
    setAuthorType('全部作者');
    setPublishRange('近30天');
    setInteractionRange('全部互动');
    setTagFilter('全部标签');
    setConfidence('全部样本');
    setValueFilter('全部价值');
    setCommentFocus('全部评论结构');
    setSortBy('engagement');
    setLockedAuthorId(null);
  };

  const activeFilterTags = [
    keyword ? `搜索:${keyword}` : null,
    platform !== '全部平台' ? `平台:${platform}` : null,
    contentType !== '全部类型' ? `类型:${contentType}` : null,
    authorType !== '全部作者' ? `作者:${authorType}` : null,
    publishRange !== '近30天' ? `时间:${publishRange}` : null,
    interactionRange !== '全部互动' ? `互动:${interactionRange}` : null,
    tagFilter !== '全部标签' ? `标签:${tagFilter}` : null,
    confidence !== '全部样本' ? confidence : null,
    valueFilter !== '全部价值' ? `价值:${valueFilter}` : null,
    commentFocus !== '全部评论结构' ? `评论:${commentFocus}` : null,
    lockedAuthorId ? '限定作者' : null,
  ].filter(Boolean) as string[];

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f7f9fc] via-[#f4f7fb] to-[#edf2f7] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <motion.section
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="rounded-3xl border border-gray-200/80 bg-white/95 p-5 shadow-sm backdrop-blur"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <button onClick={() => onPageChange('event-library')} className="rounded-md px-2 py-1 hover:bg-gray-100">
                  返回事件库
                </button>
                <ChevronRight className="h-4 w-4" />
                <span>内容库</span>
              </div>
              <h1 className="mt-1 text-xl font-semibold text-gray-900">内容库</h1>
              <p className="text-sm text-gray-500">事件中的传播与表达载体层，连接评论、作者与关系分析</p>
            </div>
            <div className="flex items-center gap-2">
              <Select value={selectedEvent.id} onValueChange={setSelectedEventId}>
                <SelectTrigger className="min-w-[260px]">
                  <SelectValue placeholder="切换事件" />
                </SelectTrigger>
                <SelectContent>
                  {eventLibraryData.map((event) => (
                    <SelectItem key={event.id} value={event.id}>
                      {event.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button variant="outline" className="gap-2" onClick={() => onPageChange('event-library', { eventId: selectedEvent.id })}>
                <BarChart3 className="h-4 w-4" />
                事件概览
              </Button>
            </div>
          </div>

          <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50/60 p-4">
            <div className="grid grid-cols-1 gap-3 text-sm md:grid-cols-4">
              <p>当前事件：<span className="font-medium text-blue-950">{selectedEvent.name}</span></p>
              <p>品牌/车型：<span className="font-medium text-blue-950">{selectedEvent.brand} / {selectedEvent.model}</span></p>
              <p>时间范围：<span className="font-medium text-blue-950">{selectedEvent.startDate} ~ {selectedEvent.endDate}</span></p>
              <p>状态：<Badge className="bg-emerald-100 text-emerald-700">{selectedEvent.status}</Badge></p>
            </div>
            <div className="mt-3 rounded-xl border border-blue-100 bg-white/70 p-3 text-sm text-blue-950">
              <div className="flex flex-wrap items-center gap-2">
                <Badge className={selectedEventFocus.scenario === '营销事件' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'}>
                  {selectedEventFocus.scenario}
                </Badge>
                <span className="font-medium">{selectedEventFocus.coreQuestion}</span>
              </div>
              <p className="mt-1 text-xs text-blue-800">内容库在这里负责判断“哪些内容承载传播、带来有效人群，或能成为高置信证据”。</p>
            </div>
          </div>
        </motion.section>

        <section className="rounded-3xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
            <AssetFilterField label="搜索" className="xl:col-span-2">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input value={keyword} onChange={(event) => setKeyword(event.target.value)} placeholder="搜索标题 / 摘要 / 作者" className="pl-10" />
              </div>
            </AssetFilterField>
            <AssetFilterField label="排序">
              <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortKey)}>
                <SelectTrigger>
                  <ArrowUpDown className="mr-2 h-4 w-4 text-gray-400" />
                  <SelectValue placeholder="排序方式" />
                </SelectTrigger>
                <SelectContent>
                  {contentSortOptions.map((item) => (
                    <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="平台">
              <Select value={platform} onValueChange={(v) => setPlatform(v as (typeof platformOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="平台" /></SelectTrigger>
                <SelectContent>{platformOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="内容类型">
              <Select value={contentType} onValueChange={(v) => setContentType(v as (typeof contentTypeOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="内容类型" /></SelectTrigger>
                <SelectContent>{contentTypeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="作者类型">
              <Select value={authorType} onValueChange={(v) => setAuthorType(v as (typeof authorTypeOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="作者类型" /></SelectTrigger>
                <SelectContent>{authorTypeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="发布时间">
              <Select value={publishRange} onValueChange={(v) => setPublishRange(v as (typeof publishRangeOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="发布时间" /></SelectTrigger>
                <SelectContent>{publishRangeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="互动区间">
              <Select value={interactionRange} onValueChange={(v) => setInteractionRange(v as (typeof interactionRangeOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="互动量区间" /></SelectTrigger>
                <SelectContent>{interactionRangeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="标签维度">
              <Select value={tagFilter} onValueChange={(v) => setTagFilter(v as (typeof tagFilterOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="标签" /></SelectTrigger>
                <SelectContent>{tagFilterOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="价值筛选">
              <Select value={valueFilter} onValueChange={(v) => setValueFilter(v as (typeof valueFilterOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="价值筛选" /></SelectTrigger>
                <SelectContent>{valueFilterOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="评论结构">
              <Select value={commentFocus} onValueChange={(v) => setCommentFocus(v as (typeof commentFocusOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="评论结构" /></SelectTrigger>
                <SelectContent>{commentFocusOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
            <AssetFilterField label="样本">
              <Select value={confidence} onValueChange={(v) => setConfidence(v as (typeof confidenceOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="样本" /></SelectTrigger>
                <SelectContent>{confidenceOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent>
              </Select>
            </AssetFilterField>
          </div>

          <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-gray-100 pt-4">
            <div className="flex flex-wrap gap-2">
              {activeFilterTags.length === 0 ? (
                <span className="text-xs text-gray-500">当前使用默认筛选</span>
              ) : (
                activeFilterTags.map((tag) => (
                  <Badge key={tag} variant="outline" className="rounded-full bg-gray-50">{tag}</Badge>
                ))
              )}
            </div>
            <Button variant="outline" size="sm" className="h-7 px-3 text-xs" onClick={resetFilters}>清空筛选</Button>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4 xl:grid-cols-[1.6fr,1fr]">
          <div className="rounded-3xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-gray-900">内容总览</p>
                <p className="text-xs text-gray-500">点击重点指标可联动下方列表筛选</p>
              </div>
              <div className="rounded-full border border-blue-100 bg-blue-50 px-3 py-1 text-xs text-blue-700">
                内容总数 {filteredList.length}
              </div>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 lg:grid-cols-3">
              <button className="rounded-2xl border border-gray-200 bg-white p-4 text-left transition hover:border-blue-300 hover:bg-blue-50/60" onClick={() => setValueFilter('高互动')}>
                <p className="text-xs text-gray-500">高互动内容</p>
                <p className="mt-2 text-2xl font-semibold text-gray-900">{summary.highEngagementCount}</p>
              </button>
              <button className="rounded-2xl border border-gray-200 bg-white p-4 text-left transition hover:border-emerald-300 hover:bg-emerald-50/60" onClick={() => setValueFilter('高证据')}>
                <p className="text-xs text-gray-500">高证据内容</p>
                <p className="mt-2 text-2xl font-semibold text-emerald-700">{summary.highEvidenceCount}</p>
              </button>
              <button className="rounded-2xl border border-gray-200 bg-white p-4 text-left transition hover:border-orange-300 hover:bg-orange-50/60" onClick={() => setValueFilter('高争议')}>
                <p className="text-xs text-gray-500">高争议内容</p>
                <p className="mt-2 text-2xl font-semibold text-orange-700">{summary.highControversyCount}</p>
              </button>
              <button className="rounded-2xl border border-gray-200 bg-white p-4 text-left transition hover:border-sky-300 hover:bg-sky-50/60" onClick={() => setAuthorType('KOL')}>
                <p className="text-xs text-gray-500">KOL内容占比</p>
                <p className="mt-2 text-2xl font-semibold text-sky-700">
                  {filteredList.length === 0 ? 0 : Math.round((summary.kolCount / filteredList.length) * 100)}%
                </p>
              </button>
              <button className="rounded-2xl border border-gray-200 bg-white p-4 text-left transition hover:border-blue-300 hover:bg-blue-50/60" onClick={() => setCommentFocus('高置信占比高')}>
                <p className="text-xs text-gray-500">平均高置信评论占比</p>
                <p className="mt-2 text-2xl font-semibold text-blue-700">{summary.averageHighConfidenceRate}%</p>
              </button>
              <div className="rounded-2xl border border-gray-200 bg-gray-50/60 p-4">
                <p className="text-xs text-gray-500">评论总量</p>
                <p className="mt-2 text-2xl font-semibold text-gray-900">{formatNumber(summary.totalComments)}</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-sm font-medium text-gray-900">结构速览</p>
                <p className="text-xs text-gray-500">帮助快速识别事件里内容资产承担的角色</p>
              </div>
              <LayoutGrid className="h-4 w-4 text-gray-400" />
            </div>
            <div className="mt-4 space-y-4">
              <div>
                <div className="mb-2 flex items-center justify-between text-xs text-gray-500">
                  <span>主要内容类型 Top3</span>
                  <span>综合互动 {formatNumber(summary.totalEngagement)}</span>
                </div>
                <div className="space-y-2">
                  {summary.topTypes.map(([type, count]) => (
                    <div key={type}>
                      <div className="mb-1 flex items-center justify-between text-xs text-gray-600">
                        <span>{type}</span>
                        <span>{count} 条</span>
                      </div>
                      <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                        <div className="h-full rounded-full bg-slate-900" style={{ width: `${filteredList.length === 0 ? 0 : Math.round((count / filteredList.length) * 100)}%` }} />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="rounded-2xl border border-gray-200 bg-gray-50/70 p-4">
                <p className="text-xs text-gray-500">当前筛选下的重点判断</p>
                <div className="mt-3 space-y-2 text-sm text-gray-700">
                  <p className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                    高互动内容主要集中在 {summary.topTypes[0]?.[0] ?? '暂无'}。
                  </p>
                  <p className="flex items-center gap-2">
                    <ShieldAlert className="h-4 w-4 text-orange-600" />
                    高争议内容 {summary.highControversyCount} 条，建议优先查看质疑占比高的样本。
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="space-y-4">
          {filteredList.map((item) => (
            <article key={item.id} className="rounded-3xl border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md">
              <div className="grid gap-4 xl:grid-cols-[1.5fr,0.75fr,0.9fr]">
                <div>
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="outline">{item.platform}</Badge>
                    <Badge variant="outline">{item.contentType}</Badge>
                    <Badge variant="outline">{item.mediaForm}</Badge>
                    <Badge className={item.isKOL ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}>
                      {item.authorType}{item.isKOL ? ' · KOL' : ''}
                    </Badge>
                    {item.isHighConfidenceSample && <Badge className="bg-emerald-100 text-emerald-700">高置信样本</Badge>}
                    <Badge className={item.isCoreContent ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-700'}>价值等级 · {item.valueLevel}</Badge>
                  </div>
                  <h3 className="mt-3 text-lg font-semibold text-gray-900">{item.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-gray-600">{item.summary}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {item.valueFlags.map((flag) => <Badge key={flag} className={badgeClass(flag)}>{flag}</Badge>)}
                    <Badge variant="outline">角色 · {item.contentRole}</Badge>
                    {item.riskTags.map((tag) => <Badge key={tag} className="bg-orange-50 text-orange-700">风险 · {tag}</Badge>)}
                  </div>
                  <div className="mt-4 rounded-2xl border border-gray-200 bg-gray-50/70 p-4">
                    <p className={`text-sm font-medium ${valueLevelClass(item.valueLevel)}`}>{item.valueSummary}</p>
                    <div className="mt-3 rounded-xl border border-white bg-white p-3 text-sm text-gray-700">
                      <p className="text-xs font-medium text-gray-500">决策信号</p>
                      <p className="mt-1">{getContentDecisionSignal(item, selectedEvent.type)}</p>
                    </div>
                    <div className="mt-3 flex flex-wrap gap-2 text-xs text-gray-500">
                      <span className="inline-flex items-center gap-1"><UserCircle2 className="h-3.5 w-3.5" />{item.authorName}</span>
                      <span className="inline-flex items-center gap-1"><CalendarRange className="h-3.5 w-3.5" />{item.publishedAt}</span>
                      <span>事件：{item.eventName}</span>
                    </div>
                  </div>
                </div>

                <div className="rounded-2xl border border-gray-200 bg-gray-50/60 p-4">
                  <p className="text-xs text-gray-500">表现信息</p>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-sm text-gray-700">
                    <p>综合互动</p><p className="text-right font-semibold text-gray-900">{formatNumber(item.engagementTotal)}</p>
                    <p>评论数</p><p className="text-right font-semibold text-gray-900">{formatNumber(item.commentCount)}</p>
                    <p>点赞</p><p className="text-right">{formatNumber(item.likeCount)}</p>
                    <p>分享</p><p className="text-right">{formatNumber(item.shareCount)}</p>
                    <p>收藏</p><p className="text-right">{formatNumber(item.favoriteCount)}</p>
                    <p>标签置信度</p><p className="text-right">{Math.round(item.tagConfidence * 100)}%</p>
                  </div>
                </div>

                <div className="rounded-2xl border border-gray-200 bg-white p-4">
                  <p className="text-xs text-gray-500">评论结构摘要</p>
                  <div className="mt-3 space-y-3">
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div className="rounded-xl border border-gray-100 bg-blue-50/50 p-3">
                        <p className="text-xs text-gray-500">高置信占比</p>
                        <p className="mt-1 font-semibold text-blue-700">{item.commentProfile.highConfidenceRate}%</p>
                      </div>
                      <div className="rounded-xl border border-gray-100 bg-orange-50/50 p-3">
                        <p className="text-xs text-gray-500">质疑占比</p>
                        <p className="mt-1 font-semibold text-orange-700">{item.commentProfile.doubtRate}%</p>
                      </div>
                    </div>
                    <div className="space-y-2 text-xs text-gray-600">
                      <p>阶段 Top：<span className="font-medium text-gray-900">{item.commentProfile.stageTop}</span></p>
                      <p>态度 Top：<span className="font-medium text-gray-900">{item.commentProfile.attitudeTop}</span></p>
                      <p>车主 / 试驾：<span className="font-medium text-gray-900">{item.commentProfile.ownerRate}% / {item.commentProfile.testDriveRate}%</span></p>
                      <p>正向 / 负向：<span className="font-medium text-gray-900">{item.commentProfile.positiveRate}% / {item.commentProfile.negativeRate}%</span></p>
                    </div>
                    <div className="space-y-2">
                      {item.commentProfile.mindsetDistribution.map((mindset) => (
                        <div key={mindset.label}>
                          <div className="mb-1 flex items-center justify-between text-[11px] text-gray-500">
                            <span>{mindset.label}</span>
                            <span>{mindset.value}%</span>
                          </div>
                          <div className="h-1.5 overflow-hidden rounded-full bg-gray-100">
                            <div className="h-full rounded-full bg-slate-900" style={{ width: `${mindset.value}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-gray-100 pt-4">
                <div className="flex flex-wrap gap-2 text-xs text-gray-500">
                  <span>命题 Top1：{item.propositionTags[0] ?? '无'}</span>
                  <span>问题 Top1：{item.issueTags[0] ?? '无'}</span>
                  <span>证据 Top1：{item.evidenceTags[0] ?? '无'}</span>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => onPageChange('comment-library', { eventId: item.eventId, contentId: item.id, keyword: item.title })}>查看评论</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => onPageChange('author-library', { eventId: item.eventId, authorId: item.authorId, keyword: item.authorName, includeKOL: item.isKOL })}>作者详情</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => setSelectedContent(item)}>内容详情</Button>
                </div>
              </div>
            </article>
          ))}

          {filteredList.length === 0 && (
            <div className="rounded-3xl border border-dashed border-gray-300 bg-white p-10 text-center text-sm text-gray-500">
              当前筛选下没有匹配内容，建议放宽价值或评论结构条件。
            </div>
          )}
        </section>
      </div>

      <Sheet open={Boolean(selectedContent)} onOpenChange={(open) => !open && setSelectedContent(null)}>
        <SheetContent className="w-full overflow-y-auto sm:max-w-2xl">
          {selectedContent && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-8">{selectedContent.title}</SheetTitle>
                <SheetDescription>{selectedContent.summary}</SheetDescription>
              </SheetHeader>

              <div className="space-y-4 px-4 pb-6 text-sm">
                <div className="rounded-2xl border border-gray-200 bg-gray-50/70 p-4">
                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant="outline">{selectedContent.platform}</Badge>
                    <Badge variant="outline">{selectedContent.contentType}</Badge>
                    <Badge variant="outline">{selectedContent.mediaForm}</Badge>
                    <Badge className={badgeClass(selectedContent.valueFlags[0] ?? '高互动')}>价值等级 · {selectedContent.valueLevel}</Badge>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-gray-600">
                    <p>内容ID：{selectedContent.id}</p>
                    <p>所属事件：{selectedContent.eventName}</p>
                    <p>作者：{selectedContent.authorName}（{selectedContent.authorType}）</p>
                    <p>发布时间：{selectedContent.publishedAt}</p>
                    <p>内容角色：{selectedContent.contentRole}</p>
                    <p>事件关键内容：{selectedContent.isCoreContent ? '是' : '否'}</p>
                  </div>
                  <a href={selectedContent.sourceUrl} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-blue-600 hover:underline">
                    查看原始链接
                    <ExternalLink className="h-3.5 w-3.5" />
                  </a>
                </div>

                <div className="rounded-2xl border border-gray-200 p-4">
                  <p className="font-medium text-gray-900">内容表现概览</p>
                  <div className="mt-3 grid grid-cols-2 gap-2 text-gray-600">
                    <p>综合互动量：<span className="font-medium text-gray-900">{formatNumber(selectedContent.engagementTotal)}</span></p>
                    <p>评论数：<span className="font-medium text-gray-900">{formatNumber(selectedContent.commentCount)}</span></p>
                    <p>点赞数：{formatNumber(selectedContent.likeCount)}</p>
                    <p>收藏数：{formatNumber(selectedContent.favoriteCount)}</p>
                    <p>分享数：{formatNumber(selectedContent.shareCount)}</p>
                    <p>高置信评论占比：<span className="font-medium text-blue-700">{selectedContent.commentProfile.highConfidenceRate}%</span></p>
                    <p>车主评论占比：{selectedContent.commentProfile.ownerRate}%</p>
                    <p>试驾评论占比：{selectedContent.commentProfile.testDriveRate}%</p>
                  </div>
                </div>

                <div className="rounded-2xl border border-gray-200 p-4">
                  <p className="font-medium text-gray-900">内容标签与命题</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {selectedContent.propositionTags.map((tag) => <Badge key={`p-${tag}`} variant="outline">命题 · {tag}</Badge>)}
                    {selectedContent.issueTags.map((tag) => <Badge key={`i-${tag}`} variant="outline">问题 · {tag}</Badge>)}
                    {selectedContent.evidenceTags.map((tag) => <Badge key={`e-${tag}`} variant="outline">证据 · {tag}</Badge>)}
                    {selectedContent.riskTags.map((tag) => <Badge key={`r-${tag}`} className="bg-orange-50 text-orange-700">风险 · {tag}</Badge>)}
                  </div>
                  <p className="mt-3 text-xs text-gray-500">标签置信度 {Math.round(selectedContent.tagConfidence * 100)}%</p>
                </div>

                <div className="grid gap-4 lg:grid-cols-2">
                  <DistributionBars title="评论情绪分布" items={selectedContent.commentProfile.emotionDistribution} />
                  <DistributionBars title="评论态度分布" items={selectedContent.commentProfile.attitudeDistribution} />
                  <DistributionBars title="评论阶段分布" items={selectedContent.commentProfile.stageDistribution} />
                  <DistributionBars title="评论心智 Top" items={selectedContent.commentProfile.mindsetDistribution} />
                </div>

                <div className="rounded-2xl border border-gray-200 p-4">
                  <p className="font-medium text-gray-900">内容价值与风险判断</p>
                  <p className="mt-2 text-sm text-gray-700">{selectedContent.valueSummary}</p>
                  <div className="mt-3 space-y-2 text-gray-600">
                    {selectedContent.valueReasons.map((reason) => (
                      <p key={reason}>- {reason}</p>
                    ))}
                  </div>
                  <div className="mt-4 rounded-xl border border-orange-100 bg-orange-50/70 p-3 text-gray-700">
                    <p className="font-medium text-orange-900">风险判断</p>
                    <p className="mt-1">{selectedContent.riskSummary}</p>
                  </div>
                </div>

                <div className="rounded-2xl border border-gray-200 p-4">
                  <p className="font-medium text-gray-900">关联内容</p>
                  <div className="mt-3 space-y-2">
                    {selectedContent.relatedContents.length === 0 ? (
                      <p className="text-sm text-gray-500">暂无已配置的关联内容。</p>
                    ) : (
                      selectedContent.relatedContents.map((item) => (
                        <button
                          key={item.id}
                          className="w-full rounded-xl border border-gray-200 bg-gray-50/60 p-3 text-left transition hover:border-blue-300 hover:bg-blue-50/50"
                          onClick={() => {
                            const target = contentLibraryData.find((content) => content.id === item.id);
                            if (target) {
                              setSelectedContent(target);
                            }
                          }}
                        >
                          <p className="font-medium text-gray-900">{item.title}</p>
                          <p className="mt-1 text-xs text-gray-500">{item.reason}</p>
                        </button>
                      ))
                    )}
                  </div>
                </div>

                <div className="rounded-2xl border border-gray-200 p-4">
                  <p className="font-medium text-gray-900">代表性评论入口</p>
                  <div className="mt-3 space-y-2">
                    {selectedContent.representativeComments.map((comment) => (
                      <div key={comment.label} className="rounded-xl border border-gray-100 bg-gray-50/70 p-3">
                        <p className="text-xs font-medium text-gray-500">{comment.label}</p>
                        <p className="mt-1 text-sm text-gray-700">{comment.text}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-2xl border border-blue-100 bg-blue-50/60 p-4">
                  <p className="font-medium text-blue-900">快捷联动</p>
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    <Button variant="outline" className="justify-start gap-2 bg-white" onClick={() => jumpToPage('comment-library', { eventId: selectedContent.eventId, contentId: selectedContent.id, keyword: selectedContent.title })}>
                      <MessageSquare className="h-4 w-4" />
                      查看评论
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white" onClick={() => jumpToPage('author-library', { eventId: selectedContent.eventId, authorId: selectedContent.authorId, keyword: selectedContent.authorName, includeKOL: selectedContent.isKOL })}>
                      <Users className="h-4 w-4" />
                      作者详情
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white" onClick={() => focusSameAuthorContent(selectedContent)}>
                      <BookOpenCheck className="h-4 w-4" />
                      同作者内容
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white" onClick={() => onPageChange('event-library', { eventId: selectedContent.eventId })}>
                      <BarChart3 className="h-4 w-4" />
                      事件概览
                    </Button>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Filter className="h-3.5 w-3.5" />
                  当前详情仍保留事件上下文，适合作为评论库和作者库的中间跳板页。
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
