import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowUpDown,
  BarChart3,
  BookOpenCheck,
  CalendarRange,
  ChevronRight,
  ExternalLink,
  Filter,
  MessageSquare,
  Network,
  Search,
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
  confidenceOptions,
  contentLibraryData,
  contentTypeOptions,
  interactionRangeOptions,
  platformOptions,
  publishRangeOptions,
  tagFilterOptions,
  type ContentLibraryItem,
} from './data/contentLibraryData';

interface ContentLibraryPageProps {
  onPageChange: (page: string) => void;
}

const numberFormatter = new Intl.NumberFormat('zh-CN');

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

export default function ContentLibraryPage({ onPageChange }: ContentLibraryPageProps) {
  const [selectedEventId, setSelectedEventId] = useState('EVT-2026-001');
  const [keyword, setKeyword] = useState('');
  const [platform, setPlatform] = useState<(typeof platformOptions)[number]>('全部平台');
  const [contentType, setContentType] = useState<(typeof contentTypeOptions)[number]>('全部类型');
  const [authorType, setAuthorType] = useState<(typeof authorTypeOptions)[number]>('全部作者');
  const [publishRange, setPublishRange] = useState<(typeof publishRangeOptions)[number]>('近30天');
  const [interactionRange, setInteractionRange] = useState<(typeof interactionRangeOptions)[number]>('全部互动');
  const [tagFilter, setTagFilter] = useState<(typeof tagFilterOptions)[number]>('全部标签');
  const [confidence, setConfidence] = useState<(typeof confidenceOptions)[number]>('全部样本');
  const [selectedContent, setSelectedContent] = useState<ContentLibraryItem | null>(null);

  const selectedEvent = useMemo(
    () => eventLibraryData.find((event) => event.id === selectedEventId) ?? eventLibraryData[0],
    [selectedEventId]
  );

  const filteredList = useMemo(() => {
    const now = new Date('2026-03-08');
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

        const tagMatched =
          tagFilter === '全部标签' ||
          (tagFilter === '命题' && item.propositionTags.length > 0) ||
          (tagFilter === '问题' && item.issueTags.length > 0) ||
          (tagFilter === '证据' && item.evidenceTags.length > 0);

        return (
          keywordMatched &&
          rangeMatched &&
          platformMatched &&
          contentTypeMatched &&
          authorTypeMatched &&
          interactionMatched &&
          confidenceMatched &&
          tagMatched
        );
      })
      .sort((a, b) => b.engagementTotal - a.engagementTotal);
  }, [
    authorType,
    confidence,
    contentType,
    interactionRange,
    keyword,
    platform,
    publishRange,
    selectedEvent.id,
    tagFilter,
  ]);

  const summary = useMemo(() => {
    const totalComments = filteredList.reduce((sum, item) => sum + item.commentCount, 0);
    const totalEngagement = filteredList.reduce((sum, item) => sum + item.engagementTotal, 0);
    const kolCount = filteredList.filter((item) => item.isKOL).length;
    const highConfidenceCount = filteredList.filter((item) => item.isHighConfidenceSample).length;
    return { totalComments, totalEngagement, kolCount, highConfidenceCount };
  }, [filteredList]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f7f9fc] via-[#f4f6fb] to-[#edf2f7] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <motion.section
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="rounded-3xl border border-gray-200/80 bg-white/90 p-5 shadow-sm backdrop-blur"
        >
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <button
                  onClick={() => onPageChange('event-library')}
                  className="rounded-md px-2 py-1 hover:bg-gray-100"
                >
                  返回事件库
                </button>
                <ChevronRight className="h-4 w-4" />
                <span>内容库</span>
              </div>
              <h1 className="mt-1 text-xl font-semibold text-gray-900">内容库</h1>
              <p className="text-sm text-gray-500">事件内内容资产池，连接评论分析、作者分析与关系视图</p>
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
              <Button variant="outline" className="gap-2">
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
          </div>
        </motion.section>

        <section className="rounded-3xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3 xl:grid-cols-8">
            <div className="xl:col-span-2">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  value={keyword}
                  onChange={(event) => setKeyword(event.target.value)}
                  placeholder="搜索标题/摘要/作者"
                  className="pl-10"
                />
              </div>
            </div>
            <div><Select value={platform} onValueChange={(v) => setPlatform(v as (typeof platformOptions)[number])}><SelectTrigger><SelectValue placeholder="平台" /></SelectTrigger><SelectContent>{platformOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></div>
            <div><Select value={contentType} onValueChange={(v) => setContentType(v as (typeof contentTypeOptions)[number])}><SelectTrigger><SelectValue placeholder="内容类型" /></SelectTrigger><SelectContent>{contentTypeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></div>
            <div><Select value={authorType} onValueChange={(v) => setAuthorType(v as (typeof authorTypeOptions)[number])}><SelectTrigger><SelectValue placeholder="作者类型" /></SelectTrigger><SelectContent>{authorTypeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></div>
            <div><Select value={publishRange} onValueChange={(v) => setPublishRange(v as (typeof publishRangeOptions)[number])}><SelectTrigger><SelectValue placeholder="发布时间" /></SelectTrigger><SelectContent>{publishRangeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></div>
            <div><Select value={interactionRange} onValueChange={(v) => setInteractionRange(v as (typeof interactionRangeOptions)[number])}><SelectTrigger><ArrowUpDown className="mr-2 h-4 w-4 text-gray-400" /><SelectValue placeholder="互动量区间" /></SelectTrigger><SelectContent>{interactionRangeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></div>
            <div className="flex gap-2">
              <Select value={tagFilter} onValueChange={(v) => setTagFilter(v as (typeof tagFilterOptions)[number])}><SelectTrigger><SelectValue placeholder="标签" /></SelectTrigger><SelectContent>{tagFilterOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select>
              <Select value={confidence} onValueChange={(v) => setConfidence(v as (typeof confidenceOptions)[number])}><SelectTrigger><SelectValue placeholder="样本" /></SelectTrigger><SelectContent>{confidenceOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select>
            </div>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">内容条数</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{filteredList.length}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">评论总量</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{formatNumber(summary.totalComments)}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">综合互动量</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{formatNumber(summary.totalEngagement)}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">KOL / 高置信</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{summary.kolCount} / {summary.highConfidenceCount}</p>
          </div>
        </section>

        <section className="space-y-3">
          {filteredList.map((item) => (
            <article
              key={item.id}
              className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
            >
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="max-w-4xl">
                  <h3 className="text-base font-semibold text-gray-900">{item.title}</h3>
                  <p className="mt-1 text-sm text-gray-600">{item.summary}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge variant="outline">{item.platform}</Badge>
                    <Badge variant="outline">{item.contentType}</Badge>
                    <Badge variant="outline">{item.mediaForm}</Badge>
                    <Badge className={item.isKOL ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'}>
                      {item.authorType}{item.isKOL ? ' · KOL' : ''}
                    </Badge>
                    {item.isHighConfidenceSample && <Badge className="bg-emerald-100 text-emerald-700">高置信样本</Badge>}
                  </div>
                </div>
                <div className="min-w-[280px] rounded-xl border border-gray-100 bg-gray-50/60 p-3 text-sm">
                  <div className="grid grid-cols-2 gap-2">
                    <p>点赞：{formatNumber(item.likeCount)}</p>
                    <p>评论：{formatNumber(item.commentCount)}</p>
                    <p>转发：{formatNumber(item.shareCount)}</p>
                    <p>收藏：{formatNumber(item.favoriteCount)}</p>
                    <p className="col-span-2 font-medium text-gray-900">
                      综合互动：{formatNumber(item.engagementTotal)}
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-100 pt-3 text-xs text-gray-500">
                <div className="flex flex-wrap items-center gap-3">
                  <span className="inline-flex items-center gap-1">
                    <UserCircle2 className="h-3.5 w-3.5" />
                    {item.authorName}
                  </span>
                  <span className="inline-flex items-center gap-1">
                    <CalendarRange className="h-3.5 w-3.5" />
                    {item.publishedAt}
                  </span>
                  <span>事件：{item.eventName}</span>
                </div>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs">查看评论</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs">作者详情</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => setSelectedContent(item)}>内容详情</Button>
                </div>
              </div>
            </article>
          ))}
        </section>
      </div>

      <Sheet open={Boolean(selectedContent)} onOpenChange={(open) => !open && setSelectedContent(null)}>
        <SheetContent className="w-full sm:max-w-xl">
          {selectedContent && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-8">{selectedContent.title}</SheetTitle>
                <SheetDescription>{selectedContent.summary}</SheetDescription>
              </SheetHeader>

              <div className="space-y-4 px-4 pb-6 text-sm">
                <div className="rounded-xl border border-gray-200 bg-gray-50/70 p-3">
                  <p className="font-medium text-gray-800">原文与作者</p>
                  <div className="mt-2 space-y-1 text-gray-600">
                    <p>内容ID：{selectedContent.id}</p>
                    <p>作者：{selectedContent.authorName}（{selectedContent.authorType}）</p>
                    <p>事件：{selectedContent.eventName}</p>
                    <a
                      href={selectedContent.sourceUrl}
                      target="_blank"
                      rel="noreferrer"
                      className="inline-flex items-center gap-1 text-blue-600 hover:underline"
                    >
                      查看原始链接
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">互动数据明细</p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-gray-600">
                    <p>点赞：{formatNumber(selectedContent.likeCount)}</p>
                    <p>评论：{formatNumber(selectedContent.commentCount)}</p>
                    <p>转发：{formatNumber(selectedContent.shareCount)}</p>
                    <p>收藏：{formatNumber(selectedContent.favoriteCount)}</p>
                    <p className="col-span-2 font-medium text-gray-900">综合互动：{formatNumber(selectedContent.engagementTotal)}</p>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">标签摘要</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {selectedContent.propositionTags.map((tag) => <Badge key={`p-${tag}`} variant="outline">命题 · {tag}</Badge>)}
                    {selectedContent.issueTags.map((tag) => <Badge key={`i-${tag}`} variant="outline">问题 · {tag}</Badge>)}
                    {selectedContent.evidenceTags.map((tag) => <Badge key={`e-${tag}`} variant="outline">证据 · {tag}</Badge>)}
                  </div>
                  <p className="mt-2 text-xs text-gray-500">标签置信度：{(selectedContent.tagConfidence * 100).toFixed(0)}%</p>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">人群/心智分布</p>
                  <div className="mt-2 space-y-2">
                    {selectedContent.mindsetDistribution.map((mindset) => (
                      <div key={mindset.label}>
                        <div className="mb-1 flex items-center justify-between text-xs text-gray-600">
                          <span>{mindset.label}</span>
                          <span>{mindset.value}%</span>
                        </div>
                        <div className="h-2 overflow-hidden rounded bg-gray-100">
                          <div className="h-full rounded bg-blue-500" style={{ width: `${mindset.value}%` }} />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-3">
                  <p className="font-medium text-blue-900">快捷联动</p>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    <Button variant="outline" className="justify-start gap-2 bg-white">
                      <MessageSquare className="h-4 w-4" />
                      查看评论
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white">
                      <Users className="h-4 w-4" />
                      作者详情
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white">
                      <BookOpenCheck className="h-4 w-4" />
                      同作者内容
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white">
                      <Network className="h-4 w-4" />
                      关系视图
                    </Button>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Filter className="h-3.5 w-3.5" />
                  默认保持事件上下文，仅展示当前事件内容资产
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
