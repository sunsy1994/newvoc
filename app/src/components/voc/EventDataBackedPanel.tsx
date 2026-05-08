import { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, BarChart3, CheckCircle2, Database, LineChart, Loader2 } from 'lucide-react';

type DepartmentKey = 'market' | 'product' | 'sales' | 'service' | 'pr';

interface EventDataBackedPanelProps {
  selectedDepartment: number;
}

interface SourceState {
  loading: boolean;
  error: string;
  event: any | null;
  trend: any[];
  comments: any[];
  contents: any[];
  kols: any[];
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

const departmentKeys: DepartmentKey[] = ['market', 'product', 'sales', 'service', 'pr'];

const departmentMeta: Record<DepartmentKey, { title: string; question: string }> = {
  market: { title: '市场部', question: '这次传播有没有形成真实车相关讨论？' },
  product: { title: '产品部', question: '用户具体在夸什么、吐槽什么？' },
  sales: { title: '销售部', question: '价格与购买决策障碍有没有被讨论？' },
  service: { title: '售后部', question: '售后与服务问题有没有形成可见信号？' },
  pr: { title: '公关部', question: '负向舆情有没有扩散迹象？' },
};

const unsupportedByDepartment: Record<DepartmentKey, string[]> = {
  market: ['有效互动率：缺少 is_vehicle_related_comment 字段', '目标人群匹配度：缺少目标人群配置', 'AI摘要：缺少基于真实聚合结果的后端生成接口'],
  product: ['证据强度：当前导入模板没有 evidence_tag 字段', '问题处置路径：缺少 OTA/服务/硬件分流数据', '影响面四象限：缺少购买影响/使用影响标注'],
  sales: ['真实价格接受/成交判断：缺少报价、订单、DCC/CRM 数据', '竞品价格对比：缺少稳定竞品实体抽取字段'],
  service: ['门店/区域服务差异：缺少门店ID和区域评价结构化字段', '解决速度/重复进店：缺少工单闭环数据'],
  pr: ['完整传播链路：缺少转发/引用关系', '谣言识别：缺少事实库和人工真伪标注', 'KOL态度变化：缺少跨期历史汇总'],
};

function apiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

async function getJson(path: string) {
  const response = await fetch(apiUrl(path));
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json();
}

function pick<T>(value: any, snake: string, camel: string, fallback: T): T {
  return (value?.[snake] ?? value?.[camel] ?? fallback) as T;
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('zh-CN').format(Math.round(value || 0));
}

function formatPercent(value: number) {
  const normalized = value <= 1 ? value * 100 : value;
  return `${normalized.toFixed(1)}%`;
}

function getCommentField(comment: any, snake: string, camel: string) {
  return String(comment?.[snake] ?? comment?.[camel] ?? '').trim();
}

function countTop(values: string[], limit = 5) {
  const counts = new Map<string, number>();
  values.filter(Boolean).forEach((value) => counts.set(value, (counts.get(value) ?? 0) + 1));
  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([label, value]) => ({ label, value }));
}

function StatCard({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="text-xs text-slate-500">{label}</p>
      <p className="mt-2 text-2xl font-semibold text-slate-900">{value}</p>
      <p className="mt-1 text-xs text-slate-400">{hint}</p>
    </div>
  );
}

function SourceBadge({ children }: { children: string }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full border border-blue-100 bg-blue-50 px-2 py-1 text-xs text-blue-700">
      <Database className="h-3 w-3" />
      {children}
    </span>
  );
}

function TopList({ title, items, emptyText }: { title: string; items: { label: string; value: number }[]; emptyText: string }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-900">{title}</h3>
        <SourceBadge>评论标签聚合</SourceBadge>
      </div>
      {items.length === 0 ? (
        <p className="text-sm text-slate-500">{emptyText}</p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.label}>
              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-700">{item.label}</span>
                <span className="text-slate-500">{formatNumber(item.value)}</span>
              </div>
              <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-blue-500" style={{ width: `${Math.min(item.value * 8, 100)}%` }} />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function UnsupportedList({ items }: { items: string[] }) {
  return (
    <div className="rounded-2xl border border-amber-200 bg-amber-50/70 p-4">
      <div className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 text-amber-600" />
        <h3 className="text-sm font-semibold text-amber-950">暂不展示：当前底表/ETL不支撑</h3>
      </div>
      <ul className="mt-3 space-y-2 text-sm text-amber-900">
        {items.map((item) => (
          <li key={item} className="flex gap-2">
            <span className="mt-2 h-1.5 w-1.5 rounded-full bg-amber-500" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default function EventDataBackedPanel({ selectedDepartment }: EventDataBackedPanelProps) {
  const department = departmentKeys[selectedDepartment] ?? 'market';
  const meta = departmentMeta[department];
  const [state, setState] = useState<SourceState>({
    loading: true,
    error: '',
    event: null,
    trend: [],
    comments: [],
    contents: [],
    kols: [],
  });

  useEffect(() => {
    let mounted = true;

    async function load() {
      setState((current) => ({ ...current, loading: true, error: '' }));
      try {
        const eventsPayload = await getJson('/api/assets/events?page_size=1&sort_by=updatedAt&sort_order=desc');
        const event = eventsPayload?.items?.[0];
        if (!event) {
          throw new Error('没有可用事件，请先导入事件、内容、评论并运行ETL作业。');
        }
        const eventId = pick<string>(event, 'id', 'id', '');
        const [detail, trend, commentsPayload, contentsPayload, kolsPayload] = await Promise.all([
          getJson(`/api/assets/events/${eventId}`),
          getJson(`/api/assets/events/${eventId}/trend`),
          getJson(`/api/assets/comments?event_id=${encodeURIComponent(eventId)}`),
          getJson(`/api/assets/contents?event_id=${encodeURIComponent(eventId)}`),
          getJson(`/api/assets/kols?event_id=${encodeURIComponent(eventId)}`),
        ]);

        if (!mounted) return;
        setState({
          loading: false,
          error: '',
          event: detail,
          trend: Array.isArray(trend) ? trend : [],
          comments: commentsPayload?.items ?? [],
          contents: contentsPayload?.items ?? [],
          kols: kolsPayload?.items ?? [],
        });
      } catch (error) {
        if (!mounted) return;
        setState({
          loading: false,
          error: error instanceof Error ? error.message : '真实数据接口不可用',
          event: null,
          trend: [],
          comments: [],
          contents: [],
          kols: [],
        });
      }
    }

    load();
    return () => {
      mounted = false;
    };
  }, []);

  const derived = useMemo(() => {
    const issueTop = countTop(state.comments.map((item) => getCommentField(item, 'issue_tag', 'issueTag')));
    const propositionTop = countTop(state.comments.map((item) => getCommentField(item, 'proposition_tag', 'propositionTag')));
    const sentimentTop = countTop(state.comments.map((item) => getCommentField(item, 'sentiment_tag', 'sentimentTag')));
    const stageTop = countTop(state.comments.map((item) => getCommentField(item, 'stage_tag', 'stageTag')));
    const authorTypeTop = countTop(state.contents.map((item) => getCommentField(item, 'author_type', 'authorType')));
    const priceComments = state.comments.filter((item) => {
      const text = `${getCommentField(item, 'issue_tag', 'issueTag')} ${getCommentField(item, 'text', 'text')}`;
      return /价|贵|优惠|性价比|值不值|降价/.test(text);
    });
    const serviceComments = state.comments.filter((item) => {
      const text = `${getCommentField(item, 'issue_tag', 'issueTag')} ${getCommentField(item, 'text', 'text')}`;
      return /售后|服务|等待|维修|充电|门店/.test(text);
    });
    const negativeComments = state.comments.filter((item) => {
      const sentiment = getCommentField(item, 'sentiment_tag', 'sentimentTag');
      return ['负向', '强负面', '负面', '消极'].includes(sentiment);
    });
    return { issueTop, propositionTop, sentimentTop, stageTop, authorTypeTop, priceComments, serviceComments, negativeComments };
  }, [state.comments, state.contents]);

  if (state.loading) {
    return (
      <div className="flex min-h-[360px] items-center justify-center rounded-3xl border border-slate-200 bg-white">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" />
          正在读取后端真实数据...
        </div>
      </div>
    );
  }

  if (state.error || !state.event) {
    return (
      <div className="rounded-3xl border border-amber-200 bg-amber-50 p-6">
        <div className="flex items-center gap-2 text-amber-900">
          <AlertTriangle className="h-5 w-5" />
          <h2 className="font-semibold">未展示样例数据</h2>
        </div>
        <p className="mt-2 text-sm text-amber-900">
          {state.error || '真实数据接口不可用。'} 当前页面已关闭静态样例卡片，请先启动后端、导入数据并运行ETL作业。
        </p>
      </div>
    );
  }

  const contentCount = pick<number>(state.event, 'content_count', 'contentCount', 0);
  const commentCount = pick<number>(state.event, 'comment_count', 'commentCount', 0);
  const authorCount = pick<number>(state.event, 'author_count', 'authorCount', 0);
  const kolCount = pick<number>(state.event, 'kol_count', 'kolCount', 0);
  const totalEngagement = pick<number>(state.event, 'total_engagement', 'totalEngagement', 0);
  const negativeRatio = pick<number>(state.event, 'negative_ratio', 'negativeRatio', 0);
  const growth = pick<number>(state.event, 'growth', 'growth', 0);
  const heat = pick<number>(state.event, 'heat', 'heat', 0);
  const platforms = pick<string[]>(state.event, 'platforms', 'platforms', []);
  const topics = pick<string[]>(state.event, 'topics', 'topics', []);
  const latestTrend = state.trend[state.trend.length - 1];

  return (
    <div className="space-y-4">
      <section className="rounded-3xl border border-blue-100 bg-white p-5 shadow-sm">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="text-xs text-blue-600">{meta.title} · 真实数据视图</p>
            <h2 className="mt-1 text-2xl font-semibold text-slate-950">{meta.question}</h2>
            <p className="mt-1 text-sm text-slate-500">
              当前只展示 PostgreSQL 底表与 ETL 已经产出的字段。未接入的数据不会用样例补齐。
            </p>
          </div>
          <SourceBadge>ads_event_asset_overview / assets API</SourceBadge>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="内容数" value={formatNumber(contentCount)} hint="dwd_content + rel_event_content" />
        <StatCard label="评论数" value={formatNumber(commentCount)} hint="dwd_comment" />
        <StatCard label="作者数 / KOL数" value={`${formatNumber(authorCount)} / ${formatNumber(kolCount)}`} hint="author_id 与 is_kol 聚合" />
        <StatCard label="总互动量" value={formatNumber(totalEngagement)} hint="赞评转藏合计" />
        <StatCard label="负向评论占比" value={formatPercent(negativeRatio)} hint="sentiment_tag 聚合" />
        <StatCard label="热度分" value={heat.toFixed(1)} hint="ETL heat_score" />
        <StatCard label="近窗增速" value={formatPercent(growth)} hint="recent_heat vs prev_heat" />
        <StatCard label="最新趋势日" value={latestTrend ? pick<string>(latestTrend, 'stat_date', 'statDate', '-') : '-'} hint="ads_event_trend_daily" />
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-900">平台与话题</h3>
            <SourceBadge>事件概览聚合</SourceBadge>
          </div>
          <div className="space-y-3 text-sm">
            <p className="text-slate-600">平台：{platforms.length ? platforms.join('、') : '暂无平台字段'}</p>
            <p className="text-slate-600">Top话题：{topics.length ? topics.join('、') : '暂无 opinion/intention 标签'}</p>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-slate-900">趋势数据</h3>
            <SourceBadge>ads_event_trend_daily</SourceBadge>
          </div>
          {state.trend.length === 0 ? (
            <p className="text-sm text-slate-500">暂无趋势ETL结果。</p>
          ) : (
            <div className="space-y-2">
              {state.trend.slice(-5).map((item) => (
                <div key={pick<string>(item, 'stat_date', 'statDate', '')} className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-sm">
                  <span className="text-slate-600">{pick<string>(item, 'stat_date', 'statDate', '')}</span>
                  <span className="text-slate-900">
                    内容 {formatNumber(pick<number>(item, 'content_count', 'contentCount', 0))} · 评论 {formatNumber(pick<number>(item, 'comment_count', 'commentCount', 0))}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {department === 'market' && (
          <>
            <TopList title="主命题/意图Top" items={derived.propositionTop} emptyText="暂无 intention_tag/proposition_tag 数据。" />
            <TopList title="来源结构" items={derived.authorTypeTop} emptyText="暂无 author_type 数据。" />
          </>
        )}
        {department === 'product' && (
          <>
            <TopList title="问题标签Top" items={derived.issueTop} emptyText="暂无 opinion_tag/issue_tag 数据。" />
            <TopList title="情绪分布" items={derived.sentimentTop} emptyText="暂无 sentiment_tag 数据。" />
          </>
        )}
        {department === 'sales' && (
          <>
            <StatCard label="价格相关评论" value={formatNumber(derived.priceComments.length)} hint="issue/text 命中价格表达" />
            <TopList title="用户阶段Top" items={derived.stageTop} emptyText="暂无 stage_tag 数据。" />
          </>
        )}
        {department === 'service' && (
          <>
            <StatCard label="服务相关评论" value={formatNumber(derived.serviceComments.length)} hint="issue/text 命中服务表达" />
            <TopList title="服务/问题标签Top" items={derived.issueTop} emptyText="暂无服务类 issue_tag 数据。" />
          </>
        )}
        {department === 'pr' && (
          <>
            <StatCard label="负向评论数" value={formatNumber(derived.negativeComments.length)} hint="sentiment_tag=负向/强负面" />
            <TopList title="负向相关问题Top" items={derived.issueTop} emptyText="暂无负向问题标签。" />
          </>
        )}
        <UnsupportedList items={unsupportedByDepartment[department]} />
      </section>

      <section className="rounded-2xl border border-emerald-200 bg-emerald-50/70 p-4">
        <div className="flex items-center gap-2 text-emerald-900">
          <CheckCircle2 className="h-4 w-4" />
          <h3 className="text-sm font-semibold">当前可放心展示</h3>
        </div>
        <div className="mt-3 grid grid-cols-1 gap-2 text-sm text-emerald-900 md:grid-cols-2">
          <p className="inline-flex items-center gap-2"><BarChart3 className="h-4 w-4" />事件规模、互动、负向占比、热度与增速</p>
          <p className="inline-flex items-center gap-2"><LineChart className="h-4 w-4" />按日趋势、平台列表、话题/问题/阶段标签Top</p>
        </div>
      </section>
    </div>
  );
}
