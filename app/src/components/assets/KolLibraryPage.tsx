import { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  BarChart3,
  ChevronRight,
  FileText,
  Filter,
  MessageSquare,
  Network,
  Search,
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
  domainOptions,
  fansRangeOptions,
  kolLibraryData,
  platformOptions,
  sortOptions,
  type KOLItem,
} from './data/kolLibraryData';
import type { AssetNavigationContext, AssetPageChangeHandler } from './assetNavigation';
import AssetFilterField from './AssetFilterField';
import KOLRelationViewDialog from './KOLRelationViewDialog';
import { getEventStoryFocus } from './eventVocStrategy';

interface KolLibraryPageProps {
  onPageChange: AssetPageChangeHandler;
  navigationContext?: AssetNavigationContext;
}

type SortKey = (typeof sortOptions)[number]['value'];
const formatter = new Intl.NumberFormat('zh-CN');

function fanThreshold(label: string) {
  if (label === '10万+') return 100000;
  if (label === '30万+') return 300000;
  if (label === '50万+') return 500000;
  if (label === '100万+') return 1000000;
  return 0;
}

function getKolUseCase(kol: KOLItem, eventType: string) {
  const scenario = getEventStoryFocus(eventType).scenario;
  const riskText = kol.riskScore >= 0.45 ? '需控制争议放大' : '风险可控';
  if (scenario === '营销事件') {
    if (kol.effectiveEngagementRate >= 0.35) return `优先用于精准投放和种草转化，${riskText}。`;
    return `适合品牌声量补充，投放前需验证目标人群匹配度，${riskText}。`;
  }

  if (kol.roleTags.includes('高证据型') || kol.roleTags.includes('证据型')) {
    return `适合作为证据解释或问题澄清节点，${riskText}。`;
  }
  return `适合监测舆情扩散路径，不建议直接作为回应主节点，${riskText}。`;
}

export default function KolLibraryPage({ onPageChange, navigationContext }: KolLibraryPageProps) {
  const [selectedEventId, setSelectedEventId] = useState(navigationContext?.eventId ?? 'EVT-2026-001');
  const [keyword, setKeyword] = useState(navigationContext?.keyword ?? '');
  const [platform, setPlatform] = useState<(typeof platformOptions)[number]>('全部平台');
  const [domain, setDomain] = useState<(typeof domainOptions)[number]>('全部领域');
  const [authorType, setAuthorType] = useState<(typeof authorTypeOptions)[number]>('全部类型');
  const [fansRange, setFansRange] = useState<(typeof fansRangeOptions)[number]>('全部粉丝');
  const [sortBy, setSortBy] = useState<SortKey>('totalEngagement');
  const [selectedKOL, setSelectedKOL] = useState<KOLItem | null>(null);
  const [relationKOL, setRelationKOL] = useState<KOLItem | null>(null);

  const selectedEvent = useMemo(
    () => eventLibraryData.find((event) => event.id === selectedEventId) ?? eventLibraryData[0],
    [selectedEventId]
  );
  const selectedEventFocus = useMemo(() => getEventStoryFocus(selectedEvent.type), [selectedEvent.type]);

  const list = useMemo(() => {
    const minFans = fanThreshold(fansRange);
    return kolLibraryData
      .filter((item) => item.eventId === selectedEvent.id)
      .filter((item) => {
        const q = keyword.trim().toLowerCase();
        const keywordMatched = q.length === 0 || item.nickname.toLowerCase().includes(q);
        const platformMatched = platform === '全部平台' || item.platform === platform;
        const domainMatched = domain === '全部领域' || item.domain === domain;
        const authorMatched = authorType === '全部类型' || item.authorType === authorType;
        const fansMatched = item.fans >= minFans;
        return keywordMatched && platformMatched && domainMatched && authorMatched && fansMatched;
      })
      .sort((a, b) => Number(b[sortBy]) - Number(a[sortBy]));
  }, [authorType, domain, fansRange, keyword, platform, selectedEvent.id, sortBy]);

  const summary = useMemo(() => {
    const totalKOL = list.length;
    const postedKOL = list.filter((item) => item.eventPosts > 0).length;
    const totalEngagement = list.reduce((sum, item) => sum + item.totalEngagement, 0);
    const totalComments = list.reduce((sum, item) => sum + item.totalComments, 0);
    const highEngagement = list.filter((item) => item.totalEngagement >= 20000).length;
    const highRisk = list.filter((item) => item.riskScore >= 0.45).length;
    const highIntent = list.filter((item) => item.roleTags.includes('高意向触发型')).length;
    return { totalKOL, postedKOL, totalEngagement, totalComments, highEngagement, highRisk, highIntent };
  }, [list]);

  useEffect(() => {
    setSelectedEventId(navigationContext?.eventId ?? 'EVT-2026-001');
    setKeyword(navigationContext?.keyword ?? '');
    setSelectedKOL(
      navigationContext?.kolId
        ? kolLibraryData.find((item) => item.id === navigationContext.kolId) ?? null
        : null
    );
  }, [navigationContext]);

  const jumpToPage = (
    page: 'content-library' | 'comment-library' | 'author-library',
    context?: AssetNavigationContext
  ) => {
    setSelectedKOL(null);
    onPageChange(page, context);
  };

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
                <span>KOL库</span>
              </div>
              <h1 className="mt-1 text-xl font-semibold text-gray-900">KOL库</h1>
              <p className="text-sm text-gray-500">事件内重点传播节点列表，定位高价值与高风险KOL</p>
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
            <div className="mt-3 rounded-xl border border-blue-100 bg-white/70 p-3">
              <div className="flex flex-wrap items-center gap-2">
                <Badge className={selectedEventFocus.scenario === '营销事件' ? 'bg-blue-100 text-blue-700' : 'bg-orange-100 text-orange-700'}>
                  {selectedEventFocus.scenario}
                </Badge>
                <span className="font-medium text-blue-950">{selectedEventFocus.coreQuestion}</span>
              </div>
              <p className="mt-1 text-xs text-blue-800">KOL库在这里不做达人榜，而是判断“谁吸引了什么人，以及适合承担什么传播/解释角色”。</p>
            </div>
          </div>
        </motion.section>

        <section className="grid grid-cols-2 gap-4 lg:grid-cols-7">
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">KOL总数</p><p className="mt-2 text-2xl font-semibold">{summary.totalKOL}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">发文KOL</p><p className="mt-2 text-2xl font-semibold">{summary.postedKOL}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">总互动量</p><p className="mt-2 text-2xl font-semibold">{formatter.format(summary.totalEngagement)}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">总评论量</p><p className="mt-2 text-2xl font-semibold">{formatter.format(summary.totalComments)}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">高互动KOL</p><p className="mt-2 text-2xl font-semibold text-blue-700">{summary.highEngagement}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">高风险KOL</p><p className="mt-2 text-2xl font-semibold text-red-600">{summary.highRisk}</p></div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs text-gray-500">高意向带动</p><p className="mt-2 text-2xl font-semibold text-emerald-700">{summary.highIntent}</p></div>
        </section>

        <section className="rounded-3xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
            <AssetFilterField label="搜索" className="xl:col-span-2">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="搜索KOL昵称" className="pl-10" />
              </div>
            </AssetFilterField>
            <AssetFilterField label="平台"><Select value={platform} onValueChange={(v) => setPlatform(v as (typeof platformOptions)[number])}><SelectTrigger><SelectValue placeholder="平台" /></SelectTrigger><SelectContent>{platformOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="领域"><Select value={domain} onValueChange={(v) => setDomain(v as (typeof domainOptions)[number])}><SelectTrigger><SelectValue placeholder="领域" /></SelectTrigger><SelectContent>{domainOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="作者类型"><Select value={authorType} onValueChange={(v) => setAuthorType(v as (typeof authorTypeOptions)[number])}><SelectTrigger><SelectValue placeholder="作者类型" /></SelectTrigger><SelectContent>{authorTypeOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="粉丝区间"><Select value={fansRange} onValueChange={(v) => setFansRange(v as (typeof fansRangeOptions)[number])}><SelectTrigger><SelectValue placeholder="粉丝区间" /></SelectTrigger><SelectContent>{fansRangeOptions.map((i) => <SelectItem key={i} value={i}>{i}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="排序方式"><Select value={sortBy} onValueChange={(v) => setSortBy(v as SortKey)}><SelectTrigger><SelectValue placeholder="排序" /></SelectTrigger><SelectContent>{sortOptions.map((i) => <SelectItem key={i.value} value={i.value}>{i.label}</SelectItem>)}</SelectContent></Select></AssetFilterField>
          </div>
        </section>

        <section className="space-y-3">
          {list.map((kol) => (
            <article key={kol.id} className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div className="flex items-start gap-3">
                  <img src={kol.avatar} alt={kol.nickname} className="h-12 w-12 rounded-full object-cover" />
                  <div>
                    <p className="text-base font-semibold text-gray-900">{kol.nickname}</p>
                    <div className="mt-1 flex flex-wrap gap-2 text-xs">
                      <Badge variant="outline">{kol.platform}</Badge>
                      <Badge variant="outline">{kol.domain}</Badge>
                      <Badge variant="outline">{kol.authorType}</Badge>
                      {kol.roleTags.map((tag) => <Badge key={tag} className="bg-blue-100 text-blue-700">{tag}</Badge>)}
                    </div>
                    <p className="mt-2 text-xs text-gray-500">粉丝量：{formatter.format(kol.fans)}</p>
                  </div>
                </div>

                <div className="grid min-w-[420px] grid-cols-3 gap-2 text-sm">
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">发文数</p><p className="font-semibold">{kol.eventPosts}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">总互动量</p><p className="font-semibold">{formatter.format(kol.totalEngagement)}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">评论总量</p><p className="font-semibold">{formatter.format(kol.totalComments)}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">篇均互动</p><p className="font-semibold">{formatter.format(kol.avgEngagement)}</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">有效互动率</p><p className="font-semibold text-emerald-700">{Math.round(kol.effectiveEngagementRate * 100)}%</p></div>
                  <div className="rounded-xl border border-gray-100 bg-gray-50/70 p-2"><p className="text-xs text-gray-500">风险值</p><p className={`font-semibold ${kol.riskScore >= 0.45 ? 'text-red-600' : 'text-gray-900'}`}>{Math.round(kol.riskScore * 100)}%</p></div>
                </div>
              </div>

              <div className="mt-3 rounded-xl border border-gray-100 bg-gray-50/50 p-3 text-xs text-gray-600">
                <p>评论者心智 Top3：{kol.mindsetTop3.join(' / ')}</p>
                <p className="mt-1">评论者阶段 Top3：{kol.stageTop3.join(' / ')}</p>
                <p className="mt-1">评论者意向 Top3：{kol.intentionTop3.join(' / ')}</p>
                <div className="mt-3 rounded-lg border border-white bg-white p-2 text-sm text-gray-700">
                  <p className="text-xs font-medium text-gray-500">建议使用方式</p>
                  <p className="mt-1">{getKolUseCase(kol, selectedEvent.type)}</p>
                </div>
              </div>

              <div className="mt-3 flex items-center justify-between border-t border-gray-100 pt-3">
                <p className="text-xs text-gray-500">{kol.summary}</p>
                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 px-2 text-xs"
                    onClick={() =>
                      onPageChange('content-library', {
                        eventId: kol.eventId,
                        kolId: kol.id,
                        keyword: kol.nickname,
                        includeKOL: true,
                      })
                    }
                  >
                    查看内容
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 px-2 text-xs"
                    onClick={() =>
                      onPageChange('comment-library', {
                        eventId: kol.eventId,
                        kolId: kol.id,
                        keyword: kol.nickname,
                        includeKOL: true,
                      })
                    }
                  >
                    查看评论
                  </Button>
                  <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => setSelectedKOL(kol)}>查看详情</Button>
                </div>
              </div>
            </article>
          ))}
        </section>
      </div>

      <Sheet open={Boolean(selectedKOL)} onOpenChange={(open) => !open && setSelectedKOL(null)}>
        <SheetContent className="w-full sm:max-w-xl">
          {selectedKOL && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-8">{selectedKOL.nickname} · 事件影响详情</SheetTitle>
                <SheetDescription>{selectedKOL.summary}</SheetDescription>
              </SheetHeader>

              <div className="space-y-4 px-4 pb-6 text-sm">
                <div className="rounded-xl border border-gray-200 bg-gray-50/70 p-3">
                  <p className="font-medium text-gray-800">基础信息</p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-gray-600">
                    <p>平台：{selectedKOL.platform}</p>
                    <p>粉丝量：{formatter.format(selectedKOL.fans)}</p>
                    <p>领域：{selectedKOL.domain}</p>
                    <p>作者类型：{selectedKOL.authorType}</p>
                    <p>事件发文：{selectedKOL.eventPosts}</p>
                    <p>事件互动：{formatter.format(selectedKOL.totalEngagement)}</p>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">传播效果与风险</p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-gray-600">
                    <p>评论总量：{formatter.format(selectedKOL.totalComments)}</p>
                    <p>篇均互动：{formatter.format(selectedKOL.avgEngagement)}</p>
                    <p>高置信评论占比：{Math.round(selectedKOL.highConfidenceRatio * 100)}%</p>
                    <p>有效互动率：{Math.round(selectedKOL.effectiveEngagementRate * 100)}%</p>
                    <p className="col-span-2">风险值：<span className={selectedKOL.riskScore >= 0.45 ? 'text-red-600 font-semibold' : 'font-semibold'}>{Math.round(selectedKOL.riskScore * 100)}%</span></p>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">受众心智画像</p>
                  <div className="mt-2 space-y-1 text-gray-600">
                    <p>心智 Top3：{selectedKOL.mindsetTop3.join(' / ')}</p>
                    <p>阶段 Top3：{selectedKOL.stageTop3.join(' / ')}</p>
                    <p>意向 Top3：{selectedKOL.intentionTop3.join(' / ')}</p>
                  </div>
                </div>

                <div className="rounded-xl border border-slate-200 bg-slate-50/70 p-3">
                  <p className="font-medium text-gray-800">投放/响应建议</p>
                  <p className="mt-2 text-gray-700">{getKolUseCase(selectedKOL, selectedEvent.type)}</p>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">代表性评论样本</p>
                  <div className="mt-2 space-y-2">
                    {selectedKOL.representativeComments.map((item) => (
                      <div key={item.text} className="rounded-lg border border-gray-100 bg-gray-50/70 p-2">
                        <Badge variant="outline">{item.type}</Badge>
                        <p className="mt-1 text-xs text-gray-700">{item.text}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-3">
                  <p className="font-medium text-blue-900">快捷跳转</p>
                  <div className="mt-2 grid grid-cols-2 gap-2">
                    <Button
                      variant="outline"
                      className="justify-start gap-2 bg-white"
                      onClick={() =>
                        jumpToPage('content-library', {
                          eventId: selectedKOL.eventId,
                          kolId: selectedKOL.id,
                          keyword: selectedKOL.nickname,
                          includeKOL: true,
                        })
                      }
                    >
                      <FileText className="h-4 w-4" />
                      内容库
                    </Button>
                    <Button
                      variant="outline"
                      className="justify-start gap-2 bg-white"
                      onClick={() =>
                        jumpToPage('comment-library', {
                          eventId: selectedKOL.eventId,
                          kolId: selectedKOL.id,
                          keyword: selectedKOL.nickname,
                          includeKOL: true,
                        })
                      }
                    >
                      <MessageSquare className="h-4 w-4" />
                      评论库
                    </Button>
                    <Button
                      variant="outline"
                      className="justify-start gap-2 bg-white"
                      onClick={() =>
                        jumpToPage('author-library', {
                          eventId: selectedKOL.eventId,
                          keyword: selectedKOL.nickname,
                          includeKOL: true,
                        })
                      }
                    >
                      <Users className="h-4 w-4" />
                      作者详情
                    </Button>
                    <Button
                      variant="outline"
                      className="justify-start gap-2 bg-white"
                      onClick={() => {
                        setRelationKOL(selectedKOL);
                        setSelectedKOL(null);
                      }}
                    >
                      <Network className="h-4 w-4" />
                      关系视图
                    </Button>
                  </div>
                </div>

                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Filter className="h-3.5 w-3.5" />
                  可解释结论：优先选择高有效互动率且风险可控的KOL作为传播节点
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>

      <KOLRelationViewDialog
        open={Boolean(relationKOL)}
        kol={relationKOL}
        event={selectedEvent ?? null}
        onOpenChange={(open) => !open && setRelationKOL(null)}
        onPageChange={onPageChange}
      />
    </div>
  );
}
