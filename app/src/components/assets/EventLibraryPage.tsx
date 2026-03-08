import { useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowUpDown,
  BookOpenCheck,
  CalendarRange,
  ChevronRight,
  Database,
  Eye,
  Filter,
  MessageSquare,
  Network,
  Search,
  Shapes,
  TrendingUp,
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  eventLibraryData,
  eventTypeOptions,
  statusOptions,
  timeRangeOptions,
  type EventLibraryItem,
} from './data/eventLibraryData';

type SortKey = 'updatedAt' | 'contentCount' | 'commentCount' | 'authorCount' | 'heat' | 'growth';

const SORT_OPTIONS: { label: string; value: SortKey }[] = [
  { label: '最近更新时间', value: 'updatedAt' },
  { label: '内容数', value: 'contentCount' },
  { label: '评论数', value: 'commentCount' },
  { label: '作者数', value: 'authorCount' },
  { label: '热度', value: 'heat' },
  { label: '增速', value: 'growth' },
];

const numberFormatter = new Intl.NumberFormat('zh-CN');

function formatNumber(value: number) {
  return numberFormatter.format(value);
}

function statusBadgeClass(status: EventLibraryItem['status']) {
  if (status === '进行中') return 'bg-emerald-100 text-emerald-700';
  if (status === '已结束') return 'bg-amber-100 text-amber-700';
  return 'bg-slate-100 text-slate-700';
}

function riskBadgeClass(riskLevel: EventLibraryItem['riskLevel']) {
  if (riskLevel === '高') return 'bg-red-100 text-red-700';
  if (riskLevel === '中') return 'bg-orange-100 text-orange-700';
  return 'bg-sky-100 text-sky-700';
}

export default function EventLibraryPage() {
  const [keyword, setKeyword] = useState('');
  const [timeRange, setTimeRange] = useState<(typeof timeRangeOptions)[number]>('近30天');
  const [eventType, setEventType] = useState<(typeof eventTypeOptions)[number]>('全部');
  const [status, setStatus] = useState<(typeof statusOptions)[number]>('全部');
  const [brand, setBrand] = useState('全部品牌');
  const [platform, setPlatform] = useState('全部平台');
  const [sortBy, setSortBy] = useState<SortKey>('updatedAt');
  const [selectedEvent, setSelectedEvent] = useState<EventLibraryItem | null>(null);

  const brandOptions = useMemo(() => ['全部品牌', ...new Set(eventLibraryData.map((item) => item.brand))], []);
  const platformOptions = useMemo(
    () => ['全部平台', ...new Set(eventLibraryData.flatMap((item) => item.platforms))],
    []
  );

  const filteredEvents = useMemo(() => {
    const now = new Date('2026-03-08');

    const rangeDays = {
      全部时间: Number.POSITIVE_INFINITY,
      近7天: 7,
      近30天: 30,
      近90天: 90,
    }[timeRange];

    return eventLibraryData
      .filter((item) => {
        const q = keyword.trim().toLowerCase();
        const matchKeyword =
          q.length === 0 ||
          item.name.toLowerCase().includes(q) ||
          item.brand.toLowerCase().includes(q) ||
          item.model.toLowerCase().includes(q) ||
          item.keywords.some((tag) => tag.toLowerCase().includes(q));

        const daysDiff = Math.floor(
          (now.getTime() - new Date(item.updatedAt).getTime()) / (1000 * 60 * 60 * 24)
        );
        const matchTimeRange = rangeDays === Number.POSITIVE_INFINITY || daysDiff <= rangeDays;
        const matchType = eventType === '全部' || item.type === eventType;
        const matchStatus = status === '全部' || item.status === status;
        const matchBrand = brand === '全部品牌' || item.brand === brand;
        const matchPlatform = platform === '全部平台' || item.platforms.includes(platform);

        return matchKeyword && matchTimeRange && matchType && matchStatus && matchBrand && matchPlatform;
      })
      .sort((a, b) => {
        if (sortBy === 'updatedAt') {
          return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
        }
        return Number(b[sortBy]) - Number(a[sortBy]);
      });
  }, [brand, eventType, keyword, platform, sortBy, status, timeRange]);

  const summary = useMemo(() => {
    const totalContent = filteredEvents.reduce((sum, item) => sum + item.contentCount, 0);
    const totalComment = filteredEvents.reduce((sum, item) => sum + item.commentCount, 0);
    const runningCount = filteredEvents.filter((item) => item.status === '进行中').length;
    const highRiskCount = filteredEvents.filter((item) => item.riskLevel === '高').length;
    return { totalContent, totalComment, runningCount, highRiskCount };
  }, [filteredEvents]);

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#f7f9fc] via-[#f4f6fb] to-[#edf2f7] p-6">
      <div className="mx-auto max-w-7xl space-y-6">
        <motion.section
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="rounded-3xl border border-gray-200/80 bg-white/90 p-5 shadow-sm backdrop-blur"
        >
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600">
                <Database className="h-5 w-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">事件库</h1>
                <p className="text-sm text-gray-500">数据资产总入口，统一定位、管理和分发事件上下文</p>
              </div>
            </div>
            <div className="relative w-full max-w-md">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input
                value={keyword}
                onChange={(event) => setKeyword(event.target.value)}
                placeholder="搜索事件名、车型、品牌、关键词"
                className="pl-10"
              />
            </div>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-6">
            <div className="xl:col-span-1">
              <Select value={timeRange} onValueChange={(value) => setTimeRange(value as (typeof timeRangeOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="时间范围" /></SelectTrigger>
                <SelectContent>
                  {timeRangeOptions.map((item) => (
                    <SelectItem key={item} value={item}>{item}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="xl:col-span-1">
              <Select value={eventType} onValueChange={(value) => setEventType(value as (typeof eventTypeOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="事件类型" /></SelectTrigger>
                <SelectContent>
                  {eventTypeOptions.map((item) => (
                    <SelectItem key={item} value={item}>{item}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="xl:col-span-1">
              <Select value={brand} onValueChange={setBrand}>
                <SelectTrigger><SelectValue placeholder="品牌/车型" /></SelectTrigger>
                <SelectContent>
                  {brandOptions.map((item) => (
                    <SelectItem key={item} value={item}>{item}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="xl:col-span-1">
              <Select value={status} onValueChange={(value) => setStatus(value as (typeof statusOptions)[number])}>
                <SelectTrigger><SelectValue placeholder="事件状态" /></SelectTrigger>
                <SelectContent>
                  {statusOptions.map((item) => (
                    <SelectItem key={item} value={item}>{item}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="xl:col-span-1">
              <Select value={platform} onValueChange={setPlatform}>
                <SelectTrigger><SelectValue placeholder="平台范围" /></SelectTrigger>
                <SelectContent>
                  {platformOptions.map((item) => (
                    <SelectItem key={item} value={item}>{item}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="xl:col-span-1">
              <Select value={sortBy} onValueChange={(value) => setSortBy(value as SortKey)}>
                <SelectTrigger>
                  <ArrowUpDown className="mr-2 h-4 w-4 text-gray-400" />
                  <SelectValue placeholder="排序字段" />
                </SelectTrigger>
                <SelectContent>
                  {SORT_OPTIONS.map((item) => (
                    <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </motion.section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">事件总量</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{filteredEvents.length}</p>
            <p className="mt-1 text-xs text-gray-400">已匹配当前筛选条件</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">进行中事件</p>
            <p className="mt-2 text-2xl font-semibold text-emerald-700">{summary.runningCount}</p>
            <p className="mt-1 text-xs text-gray-400">建议优先跟踪增长与风险</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">内容/评论规模</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">
              {formatNumber(summary.totalContent)} / {formatNumber(summary.totalComment)}
            </p>
            <p className="mt-1 text-xs text-gray-400">内容数 / 评论数</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">高风险事件</p>
            <p className="mt-2 text-2xl font-semibold text-red-600">{summary.highRiskCount}</p>
            <p className="mt-1 text-xs text-gray-400">建议进入详情核查事件命题</p>
          </div>
        </section>

        <section className="overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-gray-100 px-5 py-4">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <p className="text-sm font-medium text-gray-700">事件列表（表格 + 摘要）</p>
            </div>
            <p className="text-xs text-gray-500">点击任一事件可查看详情并一键进入下游页面</p>
          </div>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>事件</TableHead>
                  <TableHead>品牌/车型</TableHead>
                  <TableHead>类型</TableHead>
                  <TableHead>时间范围</TableHead>
                  <TableHead>状态</TableHead>
                  <TableHead>平台</TableHead>
                  <TableHead>内容</TableHead>
                  <TableHead>评论</TableHead>
                  <TableHead>作者</TableHead>
                  <TableHead>热度/增速</TableHead>
                  <TableHead>快捷操作</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredEvents.map((item) => (
                  <TableRow
                    key={item.id}
                    className="cursor-pointer"
                    onClick={() => setSelectedEvent(item)}
                  >
                    <TableCell className="min-w-[260px] align-top">
                      <p className="font-medium text-gray-900">{item.name}</p>
                      <p className="mt-1 line-clamp-2 text-xs text-gray-500">{item.description}</p>
                    </TableCell>
                    <TableCell className="whitespace-nowrap">{item.brand} / {item.model}</TableCell>
                    <TableCell>{item.type}</TableCell>
                    <TableCell className="whitespace-nowrap">{item.startDate} ~ {item.endDate}</TableCell>
                    <TableCell>
                      <Badge className={statusBadgeClass(item.status)}>{item.status}</Badge>
                    </TableCell>
                    <TableCell>{item.platforms.length}</TableCell>
                    <TableCell>{formatNumber(item.contentCount)}</TableCell>
                    <TableCell>{formatNumber(item.commentCount)}</TableCell>
                    <TableCell>{formatNumber(item.authorCount)}</TableCell>
                    <TableCell>
                      <div className="text-xs text-gray-600">
                        <p>热度 {item.heat}</p>
                        <p className={item.growth >= 0 ? 'text-emerald-600' : 'text-red-600'}>
                          {item.growth >= 0 ? '+' : ''}{item.growth.toFixed(1)}%
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="outline" size="sm" className="h-7 px-2 text-xs">内容</Button>
                        <Button variant="outline" size="sm" className="h-7 px-2 text-xs">评论</Button>
                        <Button variant="outline" size="sm" className="h-7 px-2 text-xs">关系</Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </section>
      </div>

      <Sheet open={Boolean(selectedEvent)} onOpenChange={(open) => !open && setSelectedEvent(null)}>
        <SheetContent className="w-full sm:max-w-xl">
          {selectedEvent && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-8">{selectedEvent.name}</SheetTitle>
                <SheetDescription>{selectedEvent.description}</SheetDescription>
              </SheetHeader>

              <div className="space-y-5 px-4 pb-6">
                <div className="grid grid-cols-2 gap-3 rounded-xl border border-gray-200 bg-gray-50/70 p-3">
                  <div>
                    <p className="text-xs text-gray-500">事件ID</p>
                    <p className="mt-1 text-sm font-medium">{selectedEvent.id}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">更新时间</p>
                    <p className="mt-1 text-sm font-medium">{selectedEvent.updatedAt}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">事件类型</p>
                    <p className="mt-1 text-sm font-medium">{selectedEvent.type}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">状态</p>
                    <Badge className={statusBadgeClass(selectedEvent.status)}>{selectedEvent.status}</Badge>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-xl border border-gray-200 p-3">
                    <p className="text-xs text-gray-500">内容数</p>
                    <p className="mt-1 text-lg font-semibold">{formatNumber(selectedEvent.contentCount)}</p>
                  </div>
                  <div className="rounded-xl border border-gray-200 p-3">
                    <p className="text-xs text-gray-500">评论数</p>
                    <p className="mt-1 text-lg font-semibold">{formatNumber(selectedEvent.commentCount)}</p>
                  </div>
                  <div className="rounded-xl border border-gray-200 p-3">
                    <p className="text-xs text-gray-500">作者数</p>
                    <p className="mt-1 text-lg font-semibold">{formatNumber(selectedEvent.authorCount)}</p>
                  </div>
                  <div className="rounded-xl border border-gray-200 p-3">
                    <p className="text-xs text-gray-500">KOL数</p>
                    <p className="mt-1 text-lg font-semibold">{formatNumber(selectedEvent.kolCount)}</p>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-gray-800">
                    <TrendingUp className="h-4 w-4 text-blue-600" />
                    分析辅助字段
                  </div>
                  <div className="mt-3 grid grid-cols-3 gap-2 text-sm">
                    <p>热度：<span className="font-semibold">{selectedEvent.heat}</span></p>
                    <p>
                      增速：
                      <span className={`font-semibold ${selectedEvent.growth >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                        {selectedEvent.growth >= 0 ? '+' : ''}{selectedEvent.growth.toFixed(1)}%
                      </span>
                    </p>
                    <p>
                      风险：
                      <Badge className={riskBadgeClass(selectedEvent.riskLevel)}>{selectedEvent.riskLevel}</Badge>
                    </p>
                  </div>
                  <div className="mt-3">
                    <p className="text-xs text-gray-500">事件主命题 Top3</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {selectedEvent.topics.map((topic) => (
                        <Badge key={topic} variant="outline">{topic}</Badge>
                      ))}
                    </div>
                  </div>
                </div>

                <div className="rounded-xl border border-blue-100 bg-blue-50/60 p-4">
                  <p className="text-sm font-medium text-blue-900">快速进入下游页面（自动带入事件上下文）</p>
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    <Button variant="outline" className="justify-start gap-2 bg-white">
                      <BookOpenCheck className="h-4 w-4" />
                      查看内容
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white">
                      <MessageSquare className="h-4 w-4" />
                      查看评论
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white">
                      <Users className="h-4 w-4" />
                      查看作者
                    </Button>
                    <Button variant="outline" className="justify-start gap-2 bg-white">
                      <Network className="h-4 w-4" />
                      关系视图
                    </Button>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <CalendarRange className="h-4 w-4" />
                    {selectedEvent.startDate} ~ {selectedEvent.endDate}
                  </div>
                  <div className="flex items-center gap-1">
                    <Shapes className="h-4 w-4" />
                    {selectedEvent.platforms.join(' / ')}
                  </div>
                  <div className="col-span-2 flex items-center gap-1">
                    <Eye className="h-4 w-4" />
                    事件详情页入口将承接完整字段与历史操作记录
                    <ChevronRight className="h-4 w-4" />
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
