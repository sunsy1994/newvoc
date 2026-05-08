import { useMemo, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import {
  ArrowUpDown,
  CalendarRange,
  ExternalLink,
  Filter,
  Orbit,
  Search,
  Shapes,
  Star,
  Target,
  Trophy,
  UserCircle2,
  Users,
  Zap,
  Network,
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import CompetitorRelationViewDialog from './CompetitorRelationViewDialog';
import {
  authorTypeOptions,
  competitorLibraryData,
  interactionRangeOptions,
  pinOptions,
  platformOptions,
  sortOptions,
  timeRangeOptions,
  type CompetitorContentItem,
} from './data/competitorLibraryData';
import {
  filterCompetitorItems,
  formatNumber,
  getDateText,
  getDaysDiff,
  getEngagement,
  HIGH_INTERACTION_THRESHOLD,
} from './competitorLibraryUtils';
import AssetFilterField from './AssetFilterField';

type SortKey = (typeof sortOptions)[number]['value'];

export default function CompetitorLibraryPage() {
  const [keyword, setKeyword] = useState('');
  const [brand, setBrand] = useState('全部品牌');
  const [model, setModel] = useState('全部车型');
  const [platform, setPlatform] = useState<(typeof platformOptions)[number]>('全部平台');
  const [authorType, setAuthorType] = useState<(typeof authorTypeOptions)[number]>('全部作者类型');
  const [proposition, setProposition] = useState('全部命题');
  const [timeRange, setTimeRange] = useState<(typeof timeRangeOptions)[number]>('近7天');
  const [pinFilter, setPinFilter] = useState<(typeof pinOptions)[number]>('全部');
  const [interactionRange, setInteractionRange] = useState<(typeof interactionRangeOptions)[number]>('全部互动');
  const [onlyHotEvent, setOnlyHotEvent] = useState(false);
  const [onlyHighInteraction, setOnlyHighInteraction] = useState(false);
  const [sortBy, setSortBy] = useState<SortKey>('publishedAt');
  const [rankingRange, setRankingRange] = useState<'近7天' | '近30天'>('近7天');
  const [selectedItem, setSelectedItem] = useState<CompetitorContentItem | null>(null);
  const [relationViewOpen, setRelationViewOpen] = useState(false);
  const [relationBrand, setRelationBrand] = useState<string>('');
  const contentListRef = useRef<HTMLElement | null>(null);

  const brandOptions = useMemo(
    () => ['全部品牌', ...new Set(competitorLibraryData.map((item) => item.brand))],
    []
  );
  const modelOptions = useMemo(
    () => ['全部车型', ...new Set(competitorLibraryData.map((item) => item.model))],
    []
  );
  const propositionOptions = useMemo(
    () => ['全部命题', ...new Set(competitorLibraryData.flatMap((item) => item.propositionTags))],
    []
  );

  const filteredList = useMemo(() => {
    return filterCompetitorItems(competitorLibraryData, {
      keyword,
      brand,
      model,
      platform,
      authorType,
      proposition,
      timeRange,
      pinFilter,
      interactionRange,
      onlyHotEvent,
      onlyHighInteraction,
    }).sort((a, b) => {
        if (sortBy === 'publishedAt') {
          return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
        }
        if (sortBy === 'engagement') return getEngagement(b) - getEngagement(a);
        if (sortBy === 'isPinned') return Number(b.isPinned) - Number(a.isPinned);
        return b[sortBy] - a[sortBy];
      });
  }, [
    authorType,
    brand,
    interactionRange,
    keyword,
    model,
    onlyHighInteraction,
    onlyHotEvent,
    pinFilter,
    platform,
    proposition,
    sortBy,
    timeRange,
  ]);

  const summary = useMemo(() => {
    const brandCount = new Set(filteredList.map((item) => item.brand)).size;
    const modelCount = new Set(filteredList.map((item) => item.model)).size;
    const officialCount = filteredList.filter((item) => item.authorType === '官方').length;
    const dealerCount = filteredList.filter((item) => item.authorType === '经销商').length;
    const highInteractionCount = filteredList.filter((item) => getEngagement(item) >= HIGH_INTERACTION_THRESHOLD).length;
    const sevenDayCount = filteredList.filter((item) => {
      const dayDiff = getDaysDiff(item.publishedAt);
      return dayDiff <= 7;
    }).length;

    return {
      brandCount,
      modelCount,
      officialCount,
      dealerCount,
      highInteractionCount,
      sevenDayCount,
    };
  }, [filteredList]);

  const trendData = useMemo(() => {
    const keys = ['2026-03-03', '2026-03-04', '2026-03-05', '2026-03-06', '2026-03-07', '2026-03-08', '2026-03-09'];
    const countMap = new Map<string, number>();
    keys.forEach((key) => countMap.set(key, 0));
    filteredList.forEach((item) => {
      const dateKey = getDateText(item.publishedAt);
      countMap.set(dateKey, (countMap.get(dateKey) ?? 0) + 1);
    });
    return keys.map((key) => ({ date: key.slice(5), value: countMap.get(key) ?? 0 }));
  }, [filteredList]);

  const ratio = useMemo(() => {
    const total = summary.officialCount + summary.dealerCount;
    if (total === 0) return { official: 0, dealer: 0 };
    return {
      official: Math.round((summary.officialCount / total) * 100),
      dealer: Math.round((summary.dealerCount / total) * 100),
    };
  }, [summary.dealerCount, summary.officialCount]);

  const rankingBase = useMemo(() => {
    return filterCompetitorItems(competitorLibraryData, {
      keyword,
      brand,
      model,
      platform,
      authorType,
      proposition,
      timeRange: rankingRange,
      pinFilter,
      interactionRange,
      onlyHotEvent,
      onlyHighInteraction,
    });
  }, [
    authorType,
    brand,
    interactionRange,
    keyword,
    model,
    onlyHighInteraction,
    onlyHotEvent,
    pinFilter,
    platform,
    proposition,
    rankingRange,
  ]);

  const relationScope = useMemo(() => {
    return filterCompetitorItems(competitorLibraryData, {
      keyword: '',
      brand: '全部品牌',
      model,
      platform,
      authorType: '全部作者类型',
      proposition: '全部命题',
      timeRange,
      pinFilter,
      interactionRange,
      onlyHotEvent,
      onlyHighInteraction,
    });
  }, [interactionRange, model, onlyHighInteraction, onlyHotEvent, pinFilter, platform, timeRange]);

  const handleRelationDrillDown = ({
    brand: nextBrand,
    authorType: nextAuthorType,
    proposition: nextProposition,
  }: {
    brand?: string;
    authorType?: '官方' | '经销商';
    proposition?: string;
  }) => {
    if (nextBrand) setBrand(nextBrand);
    setAuthorType(nextAuthorType ?? '全部作者类型');
    setProposition(nextProposition ?? '全部命题');
    contentListRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const activeRanking = useMemo(() => {
    const map = new Map<
      string,
      {
        brand: string;
        posts: CompetitorContentItem[];
      }
    >();
    rankingBase.forEach((item) => {
      const key = item.brand;
      const bucket = map.get(key);
      if (!bucket) {
        map.set(key, { brand: item.brand, posts: [item] });
      } else {
        bucket.posts.push(item);
      }
    });

    return [...map.values()]
      .map((group) => {
        const postCount = group.posts.length;
        const sevenDayCount = group.posts.filter((item) => getDaysDiff(item.publishedAt) <= 7).length;
        const accountCount = new Set(group.posts.map((item) => item.author)).size;
        const officialCount = group.posts.filter((item) => item.authorType === '官方').length;
        const dealerCount = group.posts.filter((item) => item.authorType === '经销商').length;
        const trendDays = ['2026-03-03', '2026-03-04', '2026-03-05', '2026-03-06', '2026-03-07', '2026-03-08', '2026-03-09'];
        const trendMap = new Map<string, number>();
        trendDays.forEach((day) => trendMap.set(day, 0));
        group.posts.forEach((item) => {
          const key = getDateText(item.publishedAt);
          trendMap.set(key, (trendMap.get(key) ?? 0) + 1);
        });
        const trend = trendDays.map((day) => trendMap.get(day) ?? 0);
        const total = officialCount + dealerCount;
        const officialRatio = total === 0 ? 0 : Math.round((officialCount / total) * 100);
        const dealerRatio = total === 0 ? 0 : Math.round((dealerCount / total) * 100);
        const conclusion =
          dealerRatio > officialRatio
            ? `近${rankingRange === '近7天' ? '7' : '30'}天发文最密集，主要由经销商体系推动。`
            : `官方与经销商同步发声，当前动作集中。`;
        return {
          key: group.brand,
          brand: group.brand,
          postCount,
          sevenDayCount,
          accountCount,
          officialRatio,
          dealerRatio,
          trend,
          conclusion,
        };
      })
      .sort((a, b) => {
        if (b.postCount !== a.postCount) return b.postCount - a.postCount;
        if (b.sevenDayCount !== a.sevenDayCount) return b.sevenDayCount - a.sevenDayCount;
        return b.accountCount - a.accountCount;
      })
      .slice(0, 5);
  }, [rankingBase]);

  const highInteractionRanking = useMemo(() => {
    return [...rankingBase]
      .sort((a, b) => getEngagement(b) - getEngagement(a))
      .slice(0, 5)
      .map((item) => {
        const engagement = getEngagement(item);
        const conclusion = item.contentType.includes('权益')
          ? '属于价格权益型高互动内容。'
          : `以“${item.propositionTags[0] ?? '核心卖点'}”表达起量明显。`;
        const blocks = [
          { label: '赞', value: item.likeCount, width: Math.max(5, Math.round((item.likeCount / engagement) * 100)), color: 'bg-blue-500' },
          { label: '评', value: item.commentCount, width: Math.max(5, Math.round((item.commentCount / engagement) * 100)), color: 'bg-emerald-500' },
          { label: '藏', value: item.favoriteCount, width: Math.max(5, Math.round((item.favoriteCount / engagement) * 100)), color: 'bg-violet-500' },
          { label: '转', value: item.shareCount, width: Math.max(5, Math.round((item.shareCount / engagement) * 100)), color: 'bg-amber-500' },
        ];
        return { item, engagement, conclusion, blocks };
      });
  }, [rankingBase]);

  const hotspotRanking = useMemo(() => {
    const allByAuthor = new Map<string, CompetitorContentItem[]>();
    rankingBase.forEach((item) => {
      const bucket = allByAuthor.get(item.author);
      if (!bucket) allByAuthor.set(item.author, [item]);
      else bucket.push(item);
    });
    const hotspotItems = rankingBase.filter((item) => Boolean(item.hotEvent));
    const byAuthor = new Map<string, CompetitorContentItem[]>();
    hotspotItems.forEach((item) => {
      const bucket = byAuthor.get(item.author);
      if (!bucket) byAuthor.set(item.author, [item]);
      else bucket.push(item);
    });
    return [...byAuthor.entries()]
      .map(([author, items]) => {
        const hotEngagement = items.reduce((sum, item) => sum + getEngagement(item), 0);
        const eventMap = new Map<string, number>();
        items.forEach((item) => {
          const key = item.hotEvent ?? '其他热点';
          eventMap.set(key, (eventMap.get(key) ?? 0) + 1);
        });
        const topEvent =
          [...eventMap.entries()].sort((a, b) => b[1] - a[1])[0]?.[0] ?? '热点话题';
        const allCount = allByAuthor.get(author)?.length ?? items.length;
        const hotRatio = Math.round((items.length / allCount) * 100);
        const authorType = items[0]?.authorType ?? '其他';
        const conclusion = `近${rankingRange === '近7天' ? '7' : '30'}天多次借势“${topEvent}”，热点内容占比 ${hotRatio}% 。`;
        return {
          author,
          authorType,
          topEvent,
          hitCount: items.length,
          hotContentCount: items.length,
          hotEngagement,
          hotRatio,
          conclusion,
        };
      })
      .sort((a, b) => {
        if (b.hitCount !== a.hitCount) return b.hitCount - a.hitCount;
        if (b.hotEngagement !== a.hotEngagement) return b.hotEngagement - a.hotEngagement;
        return b.hotRatio - a.hotRatio;
      })
      .slice(0, 5);
  }, [rankingBase, rankingRange]);

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
            <div>
              <h1 className="text-xl font-semibold text-gray-900">竞品资产库</h1>
              <p className="text-sm text-gray-500">用于查看核心竞品在重点平台上的传播内容与动作</p>
            </div>
            <div className="relative w-full max-w-md">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <Input
                value={keyword}
                onChange={(event) => setKeyword(event.target.value)}
                placeholder="搜索标题/作者/车型/品牌"
                className="pl-10"
              />
            </div>
          </div>

          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-3">
            <AssetFilterField label="品牌"><Select value={brand} onValueChange={setBrand}><SelectTrigger><SelectValue placeholder="品牌" /></SelectTrigger><SelectContent>{brandOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="车型"><Select value={model} onValueChange={setModel}><SelectTrigger><SelectValue placeholder="车型" /></SelectTrigger><SelectContent>{modelOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="平台"><Select value={platform} onValueChange={(value) => setPlatform(value as (typeof platformOptions)[number])}><SelectTrigger><SelectValue placeholder="平台" /></SelectTrigger><SelectContent>{platformOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="作者类型"><Select value={authorType} onValueChange={(value) => setAuthorType(value as (typeof authorTypeOptions)[number])}><SelectTrigger><SelectValue placeholder="作者类型" /></SelectTrigger><SelectContent>{authorTypeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="传播命题"><Select value={proposition} onValueChange={setProposition}><SelectTrigger><Target className="mr-2 h-4 w-4 text-gray-400" /><SelectValue placeholder="传播命题" /></SelectTrigger><SelectContent>{propositionOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="时间范围"><Select value={timeRange} onValueChange={(value) => setTimeRange(value as (typeof timeRangeOptions)[number])}><SelectTrigger><CalendarRange className="mr-2 h-4 w-4 text-gray-400" /><SelectValue placeholder="时间范围" /></SelectTrigger><SelectContent>{timeRangeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="是否置顶"><Select value={pinFilter} onValueChange={(value) => setPinFilter(value as (typeof pinOptions)[number])}><SelectTrigger><Star className="mr-2 h-4 w-4 text-gray-400" /><SelectValue placeholder="是否置顶" /></SelectTrigger><SelectContent>{pinOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="互动区间"><Select value={interactionRange} onValueChange={(value) => setInteractionRange(value as (typeof interactionRangeOptions)[number])}><SelectTrigger><ArrowUpDown className="mr-2 h-4 w-4 text-gray-400" /><SelectValue placeholder="互动区间" /></SelectTrigger><SelectContent>{interactionRangeOptions.map((item) => <SelectItem key={item} value={item}>{item}</SelectItem>)}</SelectContent></Select></AssetFilterField>
            <AssetFilterField label="排序字段"><Select value={sortBy} onValueChange={(value) => setSortBy(value as SortKey)}><SelectTrigger><Filter className="mr-2 h-4 w-4 text-gray-400" /><SelectValue placeholder="排序字段" /></SelectTrigger><SelectContent>{sortOptions.map((item) => <SelectItem key={item.value} value={item.value}>{item.label}</SelectItem>)}</SelectContent></Select></AssetFilterField>
          </div>

          <div className="mt-3 flex flex-wrap items-center gap-2">
            <Button
              type="button"
              variant={onlyHotEvent ? 'default' : 'outline'}
              className={onlyHotEvent ? 'bg-rose-600 hover:bg-rose-600' : ''}
              onClick={() => setOnlyHotEvent((prev) => !prev)}
            >
              <Zap className="mr-2 h-4 w-4" />
              只看热点命中内容
            </Button>
            <Button
              type="button"
              variant={onlyHighInteraction ? 'default' : 'outline'}
              className={onlyHighInteraction ? 'bg-amber-500 text-white hover:bg-amber-500' : ''}
              onClick={() => setOnlyHighInteraction((prev) => !prev)}
            >
              <Trophy className="mr-2 h-4 w-4" />
              只看高互动内容
            </Button>
            {(proposition !== '全部命题' || onlyHotEvent || onlyHighInteraction || authorType !== '全部作者类型') && (
              <p className="text-xs text-gray-500">
                当前精筛：{proposition !== '全部命题' ? `命题 ${proposition}` : '全部命题'}
                {authorType !== '全部作者类型' ? ` / 主体 ${authorType}` : ''}
                {onlyHotEvent ? ' / 热点命中' : ''}
                {onlyHighInteraction ? ' / 高互动' : ''}
              </p>
            )}
          </div>
        </motion.section>

        <section className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-7">
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">竞品品牌数</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{summary.brandCount}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">竞品车型数</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{summary.modelCount}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">内容总数</p>
            <p className="mt-2 text-2xl font-semibold text-gray-900">{filteredList.length}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">官方账号内容数</p>
            <p className="mt-2 text-2xl font-semibold text-blue-700">{summary.officialCount}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">经销商内容数</p>
            <p className="mt-2 text-2xl font-semibold text-emerald-700">{summary.dealerCount}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">高互动内容数</p>
            <p className="mt-2 text-2xl font-semibold text-orange-600">{summary.highInteractionCount}</p>
          </div>
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <p className="text-xs text-gray-500">近7天新增内容数</p>
            <p className="mt-2 text-2xl font-semibold text-violet-700">{summary.sevenDayCount}</p>
          </div>
        </section>

        <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm xl:col-span-2">
            <div className="mb-4 flex items-center gap-2 text-sm font-medium text-gray-700">
              <Shapes className="h-4 w-4 text-blue-600" />
              竞品发文趋势（近7天）
            </div>
            <div className="flex h-44 items-end gap-3 rounded-xl bg-gray-50/70 p-4">
              {trendData.map((item) => {
                const height = item.value === 0 ? 8 : 14 + item.value * 18;
                return (
                  <div key={item.date} className="flex flex-1 flex-col items-center justify-end gap-2">
                    <div className="w-full rounded-md bg-blue-500/85 transition-all" style={{ height }} />
                    <p className="text-xs text-gray-500">{item.date}</p>
                    <p className="text-xs font-medium text-gray-700">{item.value}</p>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center gap-2 text-sm font-medium text-gray-700">
              <Users className="h-4 w-4 text-emerald-600" />
              官方 / 经销商结构
            </div>
            <div className="space-y-4">
              <div>
                <div className="mb-1 flex items-center justify-between text-xs text-gray-500">
                  <span>官方</span>
                  <span>{ratio.official}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                  <div className="h-full rounded-full bg-blue-500" style={{ width: `${ratio.official}%` }} />
                </div>
              </div>
              <div>
                <div className="mb-1 flex items-center justify-between text-xs text-gray-500">
                  <span>经销商</span>
                  <span>{ratio.dealer}%</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                  <div className="h-full rounded-full bg-emerald-500" style={{ width: `${ratio.dealer}%` }} />
                </div>
              </div>
              <p className="text-xs text-gray-500">用于判断竞品动作是总部主导还是经销商体系放大。</p>
            </div>
          </div>
        </section>

        <section ref={contentListRef} className="grid grid-cols-1 gap-4 xl:grid-cols-3">
          <div className="space-y-3 xl:col-span-2">
            {filteredList.map((item) => {
              const engagement = getEngagement(item);
              return (
                <article
                  key={item.id}
                  className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="max-w-4xl">
                      <h3 className="text-base font-semibold text-gray-900">{item.title}</h3>
                      <div className="mt-2 flex flex-wrap gap-2">
                        <Badge variant="outline">{item.brand}</Badge>
                        <Badge variant="outline">{item.model}</Badge>
                        <Badge className={item.authorType === '官方' ? 'bg-blue-100 text-blue-700' : 'bg-emerald-100 text-emerald-700'}>
                          {item.authorType}
                        </Badge>
                        {item.isPinned && <Badge className="bg-amber-100 text-amber-700">置顶</Badge>}
                        {item.hotEvent && <Badge className="bg-rose-100 text-rose-700">借势 · {item.hotEvent}</Badge>}
                      </div>
                    </div>

                    <div className="min-w-[300px] rounded-xl border border-gray-100 bg-gray-50/60 p-3 text-sm">
                      <div className="grid grid-cols-2 gap-2">
                        <p>点赞：{formatNumber(item.likeCount)}</p>
                        <p>评论：{formatNumber(item.commentCount)}</p>
                        <p>收藏：{formatNumber(item.favoriteCount)}</p>
                        <p>分享：{formatNumber(item.shareCount)}</p>
                        <p className="col-span-2 font-medium text-gray-900">综合互动：{formatNumber(engagement)}</p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-3 flex flex-wrap items-center justify-between gap-2 border-t border-gray-100 pt-3 text-xs text-gray-500">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="inline-flex items-center gap-1">
                        <UserCircle2 className="h-3.5 w-3.5" />
                        {item.author}
                      </span>
                      <span className="inline-flex items-center gap-1">
                        <CalendarRange className="h-3.5 w-3.5" />
                        {item.publishedAt}
                      </span>
                      <span>{item.platform}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => setSelectedItem(item)}>
                        查看详情
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="h-7 px-2 text-xs"
                        onClick={() => {
                          setRelationBrand(item.brand);
                          setRelationViewOpen(true);
                        }}
                      >
                        <Network className="mr-1 h-3.5 w-3.5" />
                        关系视图
                      </Button>
                      <Button size="sm" variant="outline" className="h-7 px-2 text-xs" asChild>
                        <a href={item.videoUrl} target="_blank" rel="noreferrer">查看原视频</a>
                      </Button>
                      <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => setKeyword(item.author)}>同作者内容</Button>
                      <Button size="sm" variant="outline" className="h-7 px-2 text-xs" onClick={() => setModel(item.model)}>同车型内容</Button>
                    </div>
                  </div>
                </article>
              );
            })}
            {filteredList.length === 0 && (
              <div className="rounded-2xl border border-dashed border-gray-200 bg-white p-10 text-center text-sm text-gray-500">
                当前筛选条件下暂无内容，请放宽品牌、命题或互动门槛。
              </div>
            )}
          </div>

          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between gap-2">
              <div className="flex items-center gap-2 text-sm font-medium text-gray-700">
                <Trophy className="h-4 w-4 text-amber-600" />
                榜单中心
              </div>
              <div className="flex items-center gap-1 rounded-lg border border-gray-200 p-1">
                <button
                  type="button"
                  onClick={() => setRankingRange('近7天')}
                  className={`rounded-md px-2 py-1 text-xs ${rankingRange === '近7天' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
                >
                  近7天
                </button>
                <button
                  type="button"
                  onClick={() => setRankingRange('近30天')}
                  className={`rounded-md px-2 py-1 text-xs ${rankingRange === '近30天' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-100'}`}
                >
                  近30天
                </button>
              </div>
            </div>

            <Tabs defaultValue="active" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="active">活跃榜</TabsTrigger>
                <TabsTrigger value="interaction">高互动榜</TabsTrigger>
                <TabsTrigger value="hotspot">热点命中榜</TabsTrigger>
              </TabsList>

              <TabsContent value="active" className="mt-3 space-y-2">
                {activeRanking.map((row, index) => (
                  <div key={row.key} className="rounded-xl border border-gray-100 bg-gray-50/70 p-3">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-semibold text-gray-900">#{index + 1} {row.brand}</p>
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-6 px-2 text-xs"
                          onClick={() => {
                            setBrand(row.brand);
                            setModel('全部车型');
                          }}
                        >
                          查看内容
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="h-6 px-2 text-xs"
                          onClick={() => {
                            setRelationBrand(row.brand);
                            setRelationViewOpen(true);
                          }}
                        >
                          <Network className="mr-1 h-3.5 w-3.5" />
                          关系视图
                        </Button>
                      </div>
                    </div>
                    <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                      <p>发文总数 <span className="font-semibold text-gray-900">{row.postCount}</span></p>
                      <p>近7天 <span className="font-semibold text-gray-900">{row.sevenDayCount}</span></p>
                      <p>覆盖账号 <span className="font-semibold text-gray-900">{row.accountCount}</span></p>
                    </div>
                    <div className="mt-2">
                      <div className="mb-1 flex items-center justify-between text-[11px] text-gray-500">
                        <span>官方 / 经销商</span>
                        <span>{row.officialRatio}% / {row.dealerRatio}%</span>
                      </div>
                      <div className="h-1.5 overflow-hidden rounded-full bg-gray-100">
                        <div className="h-full bg-blue-500" style={{ width: `${row.officialRatio}%` }} />
                      </div>
                    </div>
                    <div className="mt-2 rounded-md bg-white p-1">
                      {(() => {
                        const width = 140;
                        const height = 24;
                        const max = Math.max(...row.trend, 1);
                        const step = row.trend.length > 1 ? width / (row.trend.length - 1) : width;
                        const points = row.trend
                          .map((point, i) => {
                            const x = i * step;
                            const y = height - (point / max) * height;
                            return `${x},${y}`;
                          })
                          .join(' ');

                        return (
                          <svg viewBox={`0 0 ${width} ${height}`} className="h-8 w-full overflow-visible">
                            <polyline points={points} fill="none" stroke="#60A5FA" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            {row.trend.map((point, i) => {
                              const x = i * step;
                              const y = height - (point / max) * height;
                              return <circle key={`${row.key}-${i}`} cx={x} cy={y} r="1.8" fill="#3B82F6" />;
                            })}
                          </svg>
                        );
                      })()}
                    </div>
                    <p className="mt-2 text-[11px] text-gray-600">{row.conclusion}</p>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="interaction" className="mt-3 space-y-2">
                {highInteractionRanking.map((row, index) => (
                  <div key={row.item.id} className="rounded-xl border border-gray-100 bg-gray-50/70 p-3">
                    <p className="line-clamp-2 text-sm font-semibold text-gray-900">#{index + 1} {row.item.title}</p>
                    <p className="mt-1 text-xs text-gray-500">
                      {row.item.brand} · {row.item.model} · {row.item.author}（{row.item.authorType}）
                    </p>
                    <p className="mt-1 text-xs font-medium text-orange-700">综合互动 {formatNumber(row.engagement)}</p>
                    <div className="mt-2 flex h-2 overflow-hidden rounded-full bg-gray-100">
                      {row.blocks.map((block) => (
                        <div key={`${row.item.id}-${block.label}`} className={block.color} style={{ width: `${block.width}%` }} title={`${block.label} ${formatNumber(block.value)}`} />
                      ))}
                    </div>
                    <div className="mt-2 flex flex-wrap gap-1">
                      {row.item.topicTags.slice(0, 2).map((tag) => <Badge key={tag} variant="outline" className="text-[10px]">{tag}</Badge>)}
                      {row.item.propositionTags.slice(0, 1).map((tag) => <Badge key={tag} className="bg-blue-100 text-[10px] text-blue-700">{tag}</Badge>)}
                    </div>
                    <p className="mt-2 text-[11px] text-gray-600">{row.conclusion}</p>
                    <div className="mt-2 flex gap-1">
                      <Button size="sm" variant="outline" className="h-6 px-2 text-xs" onClick={() => setSelectedItem(row.item)}>详情</Button>
                      <Button size="sm" variant="outline" className="h-6 px-2 text-xs" asChild>
                        <a href={row.item.videoUrl} target="_blank" rel="noreferrer">原视频</a>
                      </Button>
                      <Button size="sm" variant="outline" className="h-6 px-2 text-xs" onClick={() => setKeyword(row.item.author)}>同作者</Button>
                    </div>
                  </div>
                ))}
              </TabsContent>

              <TabsContent value="hotspot" className="mt-3 space-y-2">
                {hotspotRanking.length === 0 && (
                  <div className="rounded-xl border border-dashed border-gray-200 p-4 text-center text-xs text-gray-500">
                    当前筛选范围内暂无热点命中样本
                  </div>
                )}
                {hotspotRanking.map((row, index) => (
                  <div key={`${row.author}-${index}`} className="rounded-xl border border-gray-100 bg-gray-50/70 p-3">
                    <div className="flex items-start justify-between gap-2">
                      <p className="text-sm font-semibold text-gray-900">#{index + 1} {row.author}</p>
                      <Badge className={row.authorType === '官方' ? 'bg-blue-100 text-blue-700' : 'bg-emerald-100 text-emerald-700'}>
                        {row.authorType}
                      </Badge>
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-xs">
                      <p>热点Top1 <span className="font-semibold text-gray-900">{row.topEvent}</span></p>
                      <p>命中次数 <span className="font-semibold text-gray-900">{row.hitCount}</span></p>
                      <p>热点内容 <span className="font-semibold text-gray-900">{row.hotContentCount}</span></p>
                      <p>热点互动 <span className="font-semibold text-gray-900">{formatNumber(row.hotEngagement)}</span></p>
                    </div>
                    <div className="mt-2">
                      <div className="mb-1 flex items-center justify-between text-[11px] text-gray-500">
                        <span>热点内容占比</span>
                        <span>{row.hotRatio}%</span>
                      </div>
                      <div className="h-1.5 overflow-hidden rounded-full bg-gray-100">
                        <div className="h-full bg-rose-500" style={{ width: `${row.hotRatio}%` }} />
                      </div>
                    </div>
                    <p className="mt-2 text-[11px] text-gray-600">{row.conclusion}</p>
                    <Button size="sm" variant="outline" className="mt-2 h-6 px-2 text-xs" onClick={() => setKeyword(row.author)}>
                      查看该账号热点内容
                    </Button>
                  </div>
                ))}
              </TabsContent>
            </Tabs>

            <div className="mt-2 flex items-center justify-between text-xs text-gray-500">
              <span>默认展示 Top 5，可通过筛选查看全部结果。</span>
              <span className="inline-flex items-center gap-1"><Orbit className="h-3.5 w-3.5" />榜单联动当前筛选条件</span>
            </div>
          </div>
        </section>
      </div>

      <Sheet open={Boolean(selectedItem)} onOpenChange={(open) => !open && setSelectedItem(null)}>
        <SheetContent className="w-full sm:max-w-xl">
          {selectedItem && (
            <>
              <SheetHeader>
                <SheetTitle className="pr-8">{selectedItem.title}</SheetTitle>
                <SheetDescription>{selectedItem.brand} / {selectedItem.model} / {selectedItem.authorType}</SheetDescription>
              </SheetHeader>

              <div className="space-y-4 px-4 pb-6 text-sm">
                <div className="rounded-xl border border-gray-200 bg-gray-50/70 p-3">
                  <p className="font-medium text-gray-800">基础信息卡</p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-gray-600">
                    <p>内容ID：{selectedItem.id}</p>
                    <p>发布时间：{selectedItem.publishedAt}</p>
                    <p>品牌：{selectedItem.brand}</p>
                    <p>车型：{selectedItem.model}</p>
                    <p>作者：{selectedItem.author}</p>
                    <p>作者类型：{selectedItem.authorType}</p>
                    <p>是否置顶：{selectedItem.isPinned ? '是' : '否'}</p>
                    <a href={selectedItem.videoUrl} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-blue-600 hover:underline">
                      视频链接
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">互动表现</p>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-gray-600">
                    <p>点赞：{formatNumber(selectedItem.likeCount)}</p>
                    <p>评论：{formatNumber(selectedItem.commentCount)}</p>
                    <p>收藏：{formatNumber(selectedItem.favoriteCount)}</p>
                    <p>分享：{formatNumber(selectedItem.shareCount)}</p>
                    <p className="col-span-2 font-medium text-gray-900">综合互动量：{formatNumber(getEngagement(selectedItem))}</p>
                  </div>
                </div>

                <div className="rounded-xl border border-gray-200 p-3">
                  <p className="font-medium text-gray-800">话题与表达</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {selectedItem.topicTags.map((tag) => <Badge key={tag} variant="outline">{tag}</Badge>)}
                    {selectedItem.propositionTags.map((tag) => <Badge key={tag} className="bg-blue-100 text-blue-700">{tag}</Badge>)}
                    <Badge className="bg-violet-100 text-violet-700">{selectedItem.contentType}</Badge>
                  </div>
                </div>

                <div className="rounded-xl border border-amber-100 bg-amber-50/70 p-3">
                  <p className="font-medium text-amber-900">传播判断</p>
                  <p className="mt-2 text-xs text-amber-800">
                    {selectedItem.authorType === '经销商' ? '经销商体系统一促销内容' : '官方主导命题内容'}
                    ，当前为
                    {getEngagement(selectedItem) >= HIGH_INTERACTION_THRESHOLD ? '高互动样本' : '常规互动样本'}
                    {selectedItem.hotEvent ? `，存在借势 ${selectedItem.hotEvent} 的传播动作。` : '。'}
                  </p>
                </div>
              </div>
            </>
          )}
        </SheetContent>
      </Sheet>

      <CompetitorRelationViewDialog
        open={relationViewOpen}
        items={relationScope}
        initialBrand={relationBrand || brand}
        timeRangeLabel={timeRange}
        onOpenChange={setRelationViewOpen}
        onDrillDown={handleRelationDrillDown}
      />
    </div>
  );
}
