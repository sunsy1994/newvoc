import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  BarChart3,
  ChevronRight,
  ExternalLink,
  Filter,
  MessageCircleMore,
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
  commentLibraryData,
  confidenceOptions,
  contentTypeSourceOptions,
  evidenceOptions,
  interactionRangeOptions,
  issueOptions,
  mindsetOptions,
  platformOptions,
  propositionOptions,
  publishRangeOptions,
  sentimentOptions,
  stageOptions,
  type CommentLibraryItem,
} from './data/commentLibraryData';

interface CommentLibraryPageProps {
  onPageChange: (page: string) => void;
}

function getInteractionThreshold(range: string) {
  if (range === '300+') return 300;
  if (range === '500+') return 500;
  if (range === '800+') return 800;
  if (range === '1,000+') return 1000;
  return 0;
}

const numberFormatter = new Intl.NumberFormat('zh-CN');
function formatNumber(value: number) {
  return numberFormatter.format(value);
}

function confidenceBadge(confidence: number) {
  return confidence >= 0.9 ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-700';
}

function sentimentBadge(sentiment: CommentLibraryItem['sentimentTag']) {
  if (sentiment === '积极') return 'bg-emerald-100 text-emerald-700';
  if (sentiment === '中性') return 'bg-slate-100 text-slate-700';
  if (sentiment === '负面') return 'bg-orange-100 text-orange-700';
  return 'bg-red-100 text-red-700';
}

export default function CommentLibraryPage({ onPageChange }: CommentLibraryPageProps) {
  const [selectedEventId, setSelectedEventId] = useState('EVT-2026-001');
  const [keyword, setKeyword] = useState('');
  const [platform, setPlatform] = useState<(typeof platformOptions)[number]>('全部平台');
  const [sourceType, setSourceType] = useState<(typeof contentTypeSourceOptions)[number]>('全部来源');
  const [confidence, setConfidence] = useState<(typeof confidenceOptions)[number]>('全部置信度');
  const [publishRange, setPublishRange] = useState<(typeof publishRangeOptions)[number]>('近30天');
  const [interactionRange, setInteractionRange] = useState<(typeof interactionRangeOptions)[number]>('全部互动');
  const [mindset, setMindset] = useState<(typeof mindsetOptions)[number]>('全部心智');
  const [stage, setStage] = useState<(typeof stageOptions)[number]>('全部阶段');
  const [proposition, setProposition] = useState<(typeof propositionOptions)[number]>('全部命题');
  const [issue, setIssue] = useState<(typeof issueOptions)[number]>('全部问题');
  const [evidence, setEvidence] = useState<(typeof evidenceOptions)[number]>('全部证据');
  const [sentiment, setSentiment] = useState<(typeof sentimentOptions)[number]>('全部情绪');
  const [selectedComment, setSelectedComment] = useState<CommentLibraryItem | null>(null);

  const selectedEvent = useMemo(
    () => eventLibraryData.find((event) => event.id === selectedEventId) ?? eventLibraryData[0],
    [selectedEventId]
  );

  const filteredComments = useMemo(() => {
    const now = new Date('2026-03-08');
    const daysRange = {
      全部时间: Number.POSITIVE_INFINITY,
      近7天: 7,
      近30天: 30,
      近90天: 90,
    }[publishRange];
    const minInteraction = getInteractionThreshold(interactionRange);

    return commentLibraryData
      .filter((item) => item.eventId === selectedEvent.id)
      .filter((item) => {
        const q = keyword.trim().toLowerCase();
        const keywordMatched =
          q.length === 0 ||
          item.text.toLowerCase().includes(q) ||
          item.contentTitle.toLowerCase().includes(q) ||
          item.commentAuthorName.toLowerCase().includes(q);

        const dayDiff = Math.floor(
          (now.getTime() - new Date(item.publishedAt.replace(' ', 'T')).getTime()) / (1000 * 60 * 60 * 24)
        );

        const rangeMatched = daysRange === Number.POSITIVE_INFINITY || dayDiff <= daysRange;
        const platformMatched = platform === '全部平台' || item.platform === platform;
        const sourceMatched =
          sourceType === '全部来源' ||
          (sourceType === 'KOL内容下' && item.fromKOLContent) ||
          (sourceType === '普通用户内容下' && !item.fromKOLContent);
        const confidenceMatched = confidence === '全部置信度' || item.confidence >= 0.9;
        const interactionMatched = item.interactionCount >= minInteraction;
        const mindsetMatched = mindset === '全部心智' || item.mindsetTag === mindset;
        const stageMatched = stage === '全部阶段' || item.stageTag === stage;
        const propositionMatched = proposition === '全部命题' || item.propositionTag === proposition;
        const issueMatched = issue === '全部问题' || item.issueTag === issue;
        const evidenceMatched = evidence === '全部证据' || item.evidenceTag === evidence;
        const sentimentMatched = sentiment === '全部情绪' || item.sentimentTag === sentiment;

        return (
          keywordMatched &&
          rangeMatched &&
          platformMatched &&
          sourceMatched &&
          confidenceMatched &&
          interactionMatched &&
          mindsetMatched &&
          stageMatched &&
          propositionMatched &&
          issueMatched &&
          evidenceMatched &&
          sentimentMatched
        );
      })
      .sort((a, b) => b.interactionCount - a.interactionCount);
  }, [
    confidence,
    evidence,
    interactionRange,
    issue,
    keyword,
    mindset,
    platform,
    proposition,
    publishRange,
    selectedEvent.id,
    sentiment,
    sourceType,
    stage,
  ]);

  const summary = useMemo(() => {
    const totalLikes = filteredComments.reduce((sum, item) => sum + item.likeCount, 0);
    const highConfidenceCount = filteredComments.filter((item) => item.confidence >= 0.9).length;
    const strongNegativeCount = filteredComments.filter((item) => item.sentimentTag === '强负面').length;
    return { totalLikes, highConfidenceCount, strongNegativeCount };
  }, [filteredComments]);

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
                <span>评论库</span>
              </div>
              <h1 className="mt-1 text-xl font-semibold text-gray-900">评论库</h1>
              <p className="text-sm text-gray-500">VOC核心证据页，支持多标签筛选、样本查看与证据追溯</p>
            </div>
            <div className="flex items-center gap-2">
              <Select value={selectedEvent.id} onValueChange={setSelectedEventId}>
                <SelectTrigger className="min-w-[260px]"><SelectValue placeholder="切换事件" /></SelectTrigger>
                <SelectContent>
                  {eventLibraryData.map((event) => (
                    <SelectItem key={event.id} value={event.id}>{event.name}</SelectItem>
                  ))}
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

        <section className="rounded-3xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3 xl:grid-cols-6">
            <div className="xl:col-span-2">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="搜索评论/内容/用户" className="pl-10" />
              </div>
            </div>
            <Select value={platform} onValueChange={(v) => setPlatform(v as (typeof platformOptions)[number])}><SelectTrigger><SelectValue placeholder="平台" /></SelectTrigger><SelectContent>{platformOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={sourceType} onValueChange={(v) => setSourceType(v as (typeof contentTypeSourceOptions)[number])}><SelectTrigger><SelectValue placeholder="评论来源作者类型" /></SelectTrigger><SelectContent>{contentTypeSourceOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={confidence} onValueChange={(v) => setConfidence(v as (typeof confidenceOptions)[number])}><SelectTrigger><SelectValue placeholder="置信度" /></SelectTrigger><SelectContent>{confidenceOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={publishRange} onValueChange={(v) => setPublishRange(v as (typeof publishRangeOptions)[number])}><SelectTrigger><SelectValue placeholder="时间范围" /></SelectTrigger><SelectContent>{publishRangeOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={interactionRange} onValueChange={(v) => setInteractionRange(v as (typeof interactionRangeOptions)[number])}><SelectTrigger><SelectValue placeholder="互动区间" /></SelectTrigger><SelectContent>{interactionRangeOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={mindset} onValueChange={(v) => setMindset(v as (typeof mindsetOptions)[number])}><SelectTrigger><SelectValue placeholder="心智标签" /></SelectTrigger><SelectContent>{mindsetOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={stage} onValueChange={(v) => setStage(v as (typeof stageOptions)[number])}><SelectTrigger><SelectValue placeholder="阶段标签" /></SelectTrigger><SelectContent>{stageOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={proposition} onValueChange={(v) => setProposition(v as (typeof propositionOptions)[number])}><SelectTrigger><SelectValue placeholder="命题标签" /></SelectTrigger><SelectContent>{propositionOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={issue} onValueChange={(v) => setIssue(v as (typeof issueOptions)[number])}><SelectTrigger><SelectValue placeholder="问题标签" /></SelectTrigger><SelectContent>{issueOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={evidence} onValueChange={(v) => setEvidence(v as (typeof evidenceOptions)[number])}><SelectTrigger><SelectValue placeholder="证据标签" /></SelectTrigger><SelectContent>{evidenceOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
            <Select value={sentiment} onValueChange={(v) => setSentiment(v as (typeof sentimentOptions)[number])}><SelectTrigger><SelectValue placeholder="情绪/态度" /></SelectTrigger><SelectContent>{sentimentOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">评论样本</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{filteredComments.length}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">累计点赞</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{formatNumber(summary.totalLikes)}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">高置信评论</p>
            <p className="mt-2 text-2xl font-semibold text-emerald-700">{summary.highConfidenceCount}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">强负面评论</p>
            <p className="mt-2 text-2xl font-semibold text-red-600">{summary.strongNegativeCount}</p>
          </div>
        </section>

        <section className="space-y-3">
          {filteredComments.map((comment) => (
            <article key={comment.id} className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div className="max-w-4xl">
                  <p className="text-[15px] leading-6 text-gray-900">“{comment.text}”</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge variant="outline">{comment.platform}</Badge>
                    <Badge className={sentimentBadge(comment.sentimentTag)}>{comment.sentimentTag}</Badge>
                    <Badge variant="outline">{comment.mindsetTag}</Badge>
                    <Badge variant="outline">{comment.stageTag}</Badge>
                    <Badge className={confidenceBadge(comment.confidence)}>置信 {Math.round(comment.confidence * 100)}%</Badge>
                    {comment.confidence >= 0.9 && <Badge className="bg-emerald-100 text-emerald-700">高置信样本</Badge>}
                  </div>
                </div>
                <div className="min-w-[260px] rounded-xl border border-gray-100 bg-gray-50/70 p-3 text-sm">
                  <p>点赞：{formatNumber(comment.likeCount)}</p>
                  <p>互动：{formatNumber(comment.interactionCount)}</p>
                  <p>来源：{comment.fromKOLContent ? 'KOL内容下' : '普通用户内容下'}</p>
                  <p>发布时间：{comment.publishedAt}</p>
                </div>
              </div>

              <div className="mt-3 rounded-xl border border-gray-100 bg-gray-50/50 p-3 text-xs text-gray-600">
                <p>所属内容：{comment.contentTitle}</p>
                <p className="mt-1">内容作者：{comment.contentAuthor}（{comment.contentAuthorType}）</p>
                <p className="mt-1">标签：命题[{comment.propositionTag}] · 问题[{comment.issueTag}] · 证据[{comment.evidenceTag}]</p>
              </div>

              <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-100 pt-3 text-xs text-gray-500">
                <span className="inline-flex items-center gap-1"><UserCircle2 className="h-3.5 w-3.5" />评论作者：{comment.commentAuthorName}</span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" className="h-7 px-2 text-xs">所属内容</Button>
                  <Button variant="outline" size="sm" className="h-7 px-2 text-xs">作者详情</Button>
                  <Button variant="outline" size="sm" className="h-7 px-2 text-xs" onClick={() => setSelectedComment(comment)}>证据详情</Button>
                </div>
              </div>
            </article>
          ))}
        </section>
      </div>

      <Sheet open={Boolean(selectedComment)} onOpenChange={(open) => !open && setSelectedComment(null)}>
        <SheetContent className="w-full sm:max-w-xl">
          {selectedComment && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-8">评论证据详情</SheetTitle>
                <SheetDescription>{selectedComment.contentTitle}</SheetDescription>
              </SheetHeader>

              <div className="space-y-4 px-4 pb-6 text-sm">
                <div className="rounded-xl border border-gray-200 bg-gray-50/70 p-3">
                  <p className="font-medium text-gray-800">原评论全文</p>
                  <p className="mt-2 text-gray-700">“{selectedComment.text}”</p>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">来源与定位</p>
                  <div className="mt-2 space-y-1 text-gray-600">
                    <p>事件：{eventLibraryData.find((e) => e.id === selectedComment.eventId)?.name}</p>
                    <p>内容：{selectedComment.contentTitle}</p>
                    <p>内容作者：{selectedComment.contentAuthor}（{selectedComment.contentAuthorType}）</p>
                    <p>评论作者：{selectedComment.commentAuthorName}</p>
                    <p>发布时间：{selectedComment.publishedAt}</p>
                    <a href={selectedComment.sourceUrl} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-blue-600 hover:underline">
                      原始链接
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">标签明细与打标原因</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    <Badge variant="outline">心智 · {selectedComment.mindsetTag}</Badge>
                    <Badge variant="outline">阶段 · {selectedComment.stageTag}</Badge>
                    <Badge variant="outline">命题 · {selectedComment.propositionTag}</Badge>
                    <Badge variant="outline">问题 · {selectedComment.issueTag}</Badge>
                    <Badge variant="outline">证据 · {selectedComment.evidenceTag}</Badge>
                    <Badge className={sentimentBadge(selectedComment.sentimentTag)}>{selectedComment.sentimentTag}</Badge>
                    <Badge className={confidenceBadge(selectedComment.confidence)}>置信度 {Math.round(selectedComment.confidence * 100)}%</Badge>
                  </div>
                  <div className="mt-3 rounded-lg border border-amber-100 bg-amber-50/70 p-2 text-xs text-amber-900">
                    <span className="inline-flex items-center gap-1 font-medium"><AlertTriangle className="h-3.5 w-3.5" />打标原因：</span>
                    {selectedComment.labelingReason}
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">相似评论推荐</p>
                  <ul className="mt-2 space-y-1 text-xs text-gray-600">
                    {selectedComment.similarComments.map((item) => (
                      <li key={item} className="flex items-center gap-1">
                        <MessageCircleMore className="h-3.5 w-3.5 text-gray-400" />
                        {item}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-3">
                  <p className="font-medium text-blue-900">证据追溯</p>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    <Button variant="outline" className="justify-start gap-2 bg-white"><Filter className="h-4 w-4" />所属内容</Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white"><Users className="h-4 w-4" />作者详情</Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white"><BarChart3 className="h-4 w-4" />所属事件</Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white"><Network className="h-4 w-4" />关系视图</Button>
                  </div>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>
    </div>
  );
}
