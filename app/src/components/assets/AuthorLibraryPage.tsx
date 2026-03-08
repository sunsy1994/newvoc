import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  ChevronRight,
  FileText,
  Filter,
  MessageSquare,
  Search,
  ShieldCheck,
  UserRound,
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
  authorLibraryData,
  authorTypeOptions,
  contentTypeOptions,
  platformOptions,
  sentimentOptions,
  sortOptions,
  stageOptions,
  timeRangeOptions,
  type AuthorLibraryItem,
} from './data/authorLibraryData';

interface AuthorLibraryPageProps {
  onPageChange: (page: string) => void;
}

type SortKey = (typeof sortOptions)[number]['value'];
const formatter = new Intl.NumberFormat('zh-CN');

function confidenceBadge(value: number) {
  return value >= 0.85 ? 'bg-emerald-100 text-emerald-700' : value >= 0.7 ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-700';
}

export default function AuthorLibraryPage({ onPageChange }: AuthorLibraryPageProps) {
  const [selectedEventId, setSelectedEventId] = useState('EVT-2026-001');
  const [keyword, setKeyword] = useState('');
  const [platform, setPlatform] = useState<(typeof platformOptions)[number]>('全部平台');
  const [authorType, setAuthorType] = useState<(typeof authorTypeOptions)[number]>('全部作者类型');
  const [stage, setStage] = useState<(typeof stageOptions)[number]>('全部阶段');
  const [timeRange, setTimeRange] = useState<(typeof timeRangeOptions)[number]>('事件全周期');
  const [contentType, setContentType] = useState<(typeof contentTypeOptions)[number]>('全部内容类型');
  const [sentiment, setSentiment] = useState<(typeof sentimentOptions)[number]>('全部情绪');
  const [includeKOL, setIncludeKOL] = useState<'默认排除KOL' | '包含KOL'>('默认排除KOL');
  const [sortBy, setSortBy] = useState<SortKey>('posts');
  const [selectedAuthor, setSelectedAuthor] = useState<AuthorLibraryItem | null>(null);

  const selectedEvent = useMemo(
    () => eventLibraryData.find((event) => event.id === selectedEventId) ?? eventLibraryData[0],
    [selectedEventId]
  );

  const list = useMemo(() => {
    const filtered = authorLibraryData
      .filter((item) => item.eventId === selectedEvent.id)
      .filter((item) => {
        const q = keyword.trim().toLowerCase();
        const keywordMatched = q.length === 0 || item.nickname.toLowerCase().includes(q);
        const platformMatched = platform === '全部平台' || item.platform === platform;
        const authorTypeMatched = authorType === '全部作者类型' || item.authorType === authorType;
        const stageMatched = stage === '全部阶段' || item.stageTag === stage;
        const kolMatched = includeKOL === '包含KOL' || !item.isKOL;
        const contentTypeMatched =
          contentType === '全部内容类型' ||
          item.topContentTypes.includes(contentType);
        const sentimentMatched = sentiment === '全部情绪';
        const timeMatched = Boolean(timeRange); // 预留时间筛选位
        return keywordMatched && platformMatched && authorTypeMatched && stageMatched && kolMatched && contentTypeMatched && sentimentMatched && timeMatched;
      })
      .sort((a, b) => Number(b[sortBy]) - Number(a[sortBy]));
    return filtered;
  }, [authorType, contentType, includeKOL, keyword, platform, selectedEvent.id, sentiment, sortBy, stage, timeRange]);

  const summary = useMemo(() => {
    const totalAuthors = list.length;
    const postedAuthors = list.filter((item) => item.posts > 0).length;
    const highEvidence = list.filter((item) => item.evidenceStrength >= 80).length;
    const highEngagement = list.filter((item) => item.totalEngagement >= 8000).length;
    const highControversy = list.filter((item) => item.highControversy).length;
    const highOwner = list.filter((item) => item.stageTag === '车主' && item.stageConfidence >= 0.85).length;
    const highTestDrive = list.filter((item) => item.stageTag === '试驾' && item.stageConfidence >= 0.85).length;
    return { totalAuthors, postedAuthors, highEvidence, highEngagement, highControversy, highOwner, highTestDrive };
  }, [list]);

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
                <button onClick={() => onPageChange('event-library')} className="rounded-md px-2 py-1 hover:bg-gray-100">返回事件库</button>
                <ChevronRight className="h-4 w-4" />
                <span>作者库</span>
              </div>
              <h1 className="mt-1 text-xl font-semibold text-gray-900">作者库</h1>
              <p className="text-sm text-gray-500">事件内发声主体管理页，识别高证据/高争议/高价值作者</p>
            </div>
            <div className="flex items-center gap-2">
              <Select value={selectedEvent.id} onValueChange={setSelectedEventId}>
                <SelectTrigger className="min-w-[260px]"><SelectValue placeholder="切换事件" /></SelectTrigger>
                <SelectContent>
                  {eventLibraryData.map((event) => <SelectItem key={event.id} value={event.id}>{event.name}</SelectItem>)}
                </SelectContent>
              </Select>
              <Button variant="outline" className="gap-2"><BarChart3 className="h-4 w-4" />事件概览</Button>
            </div>
          </div>

          <div className="mt-4 rounded-2xl border border-blue-100 bg-blue-50/60 p-4 text-sm">
            <div className="grid grid-cols-1 gap-2 md:grid-cols-4">
              <p>当前事件：<span className="font-medium text-blue-950">{selectedEvent.name}</span></p>
              <p>品牌/车型：<span className="font-medium text-blue-950">{selectedEvent.brand} / {selectedEvent.model}</span></p>
              <p>时间范围：<span className="font-medium text-blue-950">{selectedEvent.startDate} ~ {selectedEvent.endDate}</span></p>
              <p>状态：<Badge className="bg-emerald-100 text-emerald-700">{selectedEvent.status}</Badge></p>
            </div>
          </div>
        </motion.section>

        <section className="grid grid-cols-2 gap-4 lg:grid-cols-7">
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">作者总数</p><p className="mt-2 text-2xl font-semibold">{summary.totalAuthors}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">发文作者</p><p className="mt-2 text-2xl font-semibold">{summary.postedAuthors}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">高证据作者</p><p className="mt-2 text-2xl font-semibold text-emerald-700">{summary.highEvidence}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">高互动作者</p><p className="mt-2 text-2xl font-semibold text-blue-700">{summary.highEngagement}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">高争议作者</p><p className="mt-2 text-2xl font-semibold text-red-600">{summary.highControversy}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">高置信车主</p><p className="mt-2 text-2xl font-semibold">{summary.highOwner}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">高置信试驾</p><p className="mt-2 text-2xl font-semibold">{summary.highTestDrive}</p></div>
        </section>

        <section className="rounded-3xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3 xl:grid-cols-6">
            <div className="xl:col-span-2">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="搜索作者昵称" className="pl-10" />
              </div>
            </div>
            <Select value={platform} onValueChange={(v) => setPlatform(v as (typeof platformOptions)[number])}><SelectTrigger><SelectValue placeholder="平台" /></SelectTrigger><SelectContent>{platformOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={authorType} onValueChange={(v) => setAuthorType(v as (typeof authorTypeOptions)[number])}><SelectTrigger><SelectValue placeholder="作者类型" /></SelectTrigger><SelectContent>{authorTypeOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={stage} onValueChange={(v) => setStage(v as (typeof stageOptions)[number])}><SelectTrigger><SelectValue placeholder="阶段标签" /></SelectTrigger><SelectContent>{stageOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={timeRange} onValueChange={(v) => setTimeRange(v as (typeof timeRangeOptions)[number])}><SelectTrigger><SelectValue placeholder="发布时间" /></SelectTrigger><SelectContent>{timeRangeOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={includeKOL} onValueChange={(v) => setIncludeKOL(v as '默认排除KOL' | '包含KOL')}><SelectTrigger><SelectValue placeholder="是否KOL" /></SelectTrigger><SelectContent><SelectItem value="默认排除KOL">默认排除KOL</SelectItem><SelectItem value="包含KOL">包含KOL</SelectItem></SelectContent></Select>
            <Select value={contentType} onValueChange={(v) => setContentType(v as (typeof contentTypeOptions)[number])}><SelectTrigger><SelectValue placeholder="内容类型" /></SelectTrigger><SelectContent>{contentTypeOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={sentiment} onValueChange={(v) => setSentiment(v as (typeof sentimentOptions)[number])}><SelectTrigger><SelectValue placeholder="情绪倾向" /></SelectTrigger><SelectContent>{sentimentOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={sortBy} onValueChange={(v) => setSortBy(v as SortKey)}><SelectTrigger><SelectValue placeholder="排序" /></SelectTrigger><SelectContent>{sortOptions.map((i) => <SelectItem key={i.value} value={i.value}>{i.label}</SelectItem>)}</SelectContent></Select>
          </div>
        </section>

        <section className="space-y-3">
          {list.map((author) => (
            <article key={author.id} className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <UserRound className="h-4 w-4 text-gray-500" />
                    <p className="text-base font-semibold text-gray-900">{author.nickname}</p>
                    <Badge variant="outline">{author.platform}</Badge>
                    <Badge variant="outline">{author.authorType}</Badge>
                    <Badge className={confidenceBadge(author.stageConfidence)}>
                      {author.stageTag} · {Math.round(author.stageConfidence * 100)}%
                    </Badge>
                  </div>
                  <div className="mt-2 flex flex-wrap gap-2 text-xs">
                    {author.roleTags.map((tag) => <Badge key={tag} className="bg-blue-100 text-blue-700">{tag}</Badge>)}
                    {author.highValue && <Badge className="bg-emerald-100 text-emerald-700">高价值作者</Badge>}
                    {author.highControversy && <Badge className="bg-red-100 text-red-700">高争议作者</Badge>}
                    {author.highConfidence && <Badge className="bg-slate-100 text-slate-700">高置信作者</Badge>}
                  </div>
                </div>

                <div className="grid min-w-[460px] grid-cols-3 gap-2 text-sm">
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">发文数</p><p className="font-semibold">{author.posts}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">总互动量</p><p className="font-semibold">{formatter.format(author.totalEngagement)}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">评论触发量</p><p className="font-semibold">{formatter.format(author.commentTriggerCount)}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">证据强度</p><p className="font-semibold text-emerald-700">{author.evidenceStrength}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">争议值</p><p className={`font-semibold ${author.controversyScore >= 40 ? 'text-red-600' : 'text-gray-900'}`}>{author.controversyScore}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">证据类型</p><p className="font-semibold">{author.evidenceType}</p></div>
                </div>
              </div>

              <div className="mt-3 rounded-xl border border-gray-100 bg-gray-50/50 p-3 text-xs text-gray-600">
                <p>涉及内容类型 Top：{author.topContentTypes.join(' / ')}</p>
                <p className="mt-1">命题 Top：{author.propositionTop.join(' / ')}</p>
                <p className="mt-1">问题标签 Top：{author.issueTop.join(' / ')}</p>
              </div>

              <div className="mt-3 flex items-center justify-between border-t border-gray-100 pt-3">
                <p className="text-xs text-gray-500">{author.aiSummary}</p>
                <div className="flex gap-2">
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs">查看内容</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs">查看评论</Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => setSelectedAuthor(author)}>查看详情</Button>
                </div>
              </div>
            </article>
          ))}
        </section>
      </div>

      <Sheet open={Boolean(selectedAuthor)} onOpenChange={(open) => !open && setSelectedAuthor(null)}>
        <SheetContent className="w-full sm:max-w-xl">
          {selectedAuthor && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-8">{selectedAuthor.nickname} · 事件档案</SheetTitle>
                <SheetDescription>{selectedAuthor.aiSummary}</SheetDescription>
              </SheetHeader>

              <div className="space-y-4 px-4 pb-6 text-sm">
                <div className="rounded-xl border border-gray-200 bg-gray-50/70 p-3">
                  <p className="font-medium text-gray-800">作者基础信息</p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-gray-600">
                    <p>平台：{selectedAuthor.platform}</p>
                    <p>类型：{selectedAuthor.authorType}</p>
                    <p>阶段：{selectedAuthor.stageTag}</p>
                    <p>阶段置信：{Math.round(selectedAuthor.stageConfidence * 100)}%</p>
                    <p>发文数：{selectedAuthor.posts}</p>
                    <p>评论触发：{formatter.format(selectedAuthor.commentTriggerCount)}</p>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">阶段识别依据</p>
                  <div className="mt-2 rounded-lg border border-amber-100 bg-amber-50/70 p-2 text-xs text-amber-900">
                    <span className="font-medium">识别说明：</span>{selectedAuthor.stageReason}
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">本事件内容表现</p>
                  <div className="mt-2 space-y-2">
                    {selectedAuthor.contentTimeline.map((item) => (
                      <div key={item.title} className="rounded-lg border border-gray-100 bg-gray-50/70 p-2 text-xs text-gray-700">
                        <p className="font-medium">{item.title}</p>
                        <p className="mt-1">{item.publishedAt} · {item.contentType} · 互动 {formatter.format(item.engagement)} · 评论 {formatter.format(item.comments)}</p>
                        <p className="mt-1">命题[{item.propositionTag}] 问题[{item.issueTag}]</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">命题/问题分布与证据价值</p>
                  <div className="mt-2 space-y-1 text-gray-600">
                    <p>命题 Top：{selectedAuthor.propositionTop.join(' / ')}</p>
                    <p>问题 Top：{selectedAuthor.issueTop.join(' / ')}</p>
                    <p>证据强度评分：<span className="font-semibold text-emerald-700">{selectedAuthor.evidenceStrength}</span></p>
                    <p>证据类型：{selectedAuthor.evidenceType}</p>
                    <p>可复现描述：{selectedAuthor.reproducible ? '是' : '否'}</p>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">代表性内容与典型评论</p>
                  <div className="mt-2 space-y-1 text-xs text-gray-700">
                    {selectedAuthor.representativeContents.map((item) => <p key={item}>内容：{item}</p>)}
                    {selectedAuthor.representativeComments.map((item) => <p key={item}>评论：{item}</p>)}
                  </div>
                </div>

                <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-3">
                  <p className="font-medium text-blue-900">快捷跳转</p>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    <Button variant="outline" className="justify-start gap-2 bg-white"><FileText className="h-4 w-4" />内容详情</Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white"><MessageSquare className="h-4 w-4" />评论库</Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white"><BarChart3 className="h-4 w-4" />事件详情</Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white"><ShieldCheck className="h-4 w-4" />证据追踪</Button>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Filter className="h-3.5 w-3.5" />
                  结论可解释：阶段识别依据 + 证据强度 + 代表样本三者联动
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
