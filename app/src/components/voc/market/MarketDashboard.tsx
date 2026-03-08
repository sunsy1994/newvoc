import { motion } from 'framer-motion';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from 'recharts';
import {
  contentRankData,
  keywordData,
  kolInfluenceData,
  marketKPIData,
  platformData,
  volumeTrendData,
} from './data/marketChartData';

interface HeroKPI {
  label: string;
  value: string;
  delta: string;
  insight: string;
}

interface MessageMemory {
  phrase: string;
  count: number;
  sentiment: '正向' | '中性' | '负向';
}

interface FunnelStage {
  stage: string;
  rate: number;
}

interface KOLPerformance {
  name: string;
  engagement: number;
  qualifiedRate: number;
  sentimentNet: number;
  misunderstandingRate: number;
  impactIndex: number;
}

const sentimentColorMap = {
  正向: '#38bdf8',
  中性: '#60a5fa',
  负向: '#fb7185',
} as const;

const funnelData: FunnelStage[] = [
  { stage: '曝光', rate: 100 },
  { stage: '提及卖点', rate: 54 },
  { stage: '复述主张', rate: 37 },
  { stage: '表达兴趣', rate: 19 },
];

const memoryPoints: MessageMemory[] = [
  { phrase: '续航够扎实，通勤和周末出行都稳', count: 1842, sentiment: '正向' },
  { phrase: '智能座舱上手快，家里老人也能用', count: 1610, sentiment: '正向' },
  { phrase: '配置高是高，但预算压力确实大', count: 1238, sentiment: '中性' },
  { phrase: '智能被理解成花哨，实用价值没讲透', count: 908, sentiment: '负向' },
];

const intentMix = [
  { stage: '了解', value: 32, color: '#0ea5e9' },
  { stage: '对比', value: 26, color: '#14b8a6' },
  { stage: '试驾', value: 22, color: '#f59e0b' },
  { stage: '购买意向', value: 14, color: '#22c55e' },
  { stage: '放弃', value: 6, color: '#ef4444' },
];

function formatWan(value: number) {
  return value >= 10000 ? `${(value / 10000).toFixed(1)}万` : value.toLocaleString();
}

function formatDelta(value: number) {
  return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
}

function SectionCard({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-3xl border border-blue-100 bg-white/95 p-4 shadow-sm backdrop-blur-sm">
      <h3 className="font-['Noto_Serif_SC'] text-base text-slate-900">{title}</h3>
      <p className="mt-1 text-xs text-slate-500">{subtitle}</p>
      <div className="mt-3">{children}</div>
    </div>
  );
}

export default function MarketDashboard() {
  const totalVolume = Number(marketKPIData.find((item) => item.type === 'volume')?.value ?? 0);
  const acceleration = 18.4;
  const ugcShare = 61;
  const trackedPlatforms = platformData.length;
  const sov = 37.8;

  const heroKpis: HeroKPI[] = [
    {
      label: '事件热度 Heat',
      value: `${formatWan(totalVolume)} 条`,
      delta: '+34.0%',
      insight: '上市日 D0 达峰，D+7 出现二次传播峰值',
    },
    {
      label: '热度增速 Acceleration',
      value: `${acceleration}%`,
      delta: '+5.6%',
      insight: '近72h 增速回升，二创内容开始接力',
    },
    {
      label: '平台覆盖 Platform Mix',
      value: `${trackedPlatforms} 个`,
      delta: '+1',
      insight: '小红书渗透率提升最快，达人扩散明显',
    },
    {
      label: 'UGC 占比 Source Mix',
      value: `${ugcShare}%`,
      delta: '+8.0%',
      insight: '自来水讨论超过KOL，口碑进入自然发酵期',
    },
    {
      label: '声量份额 SOV',
      value: `${sov}%`,
      delta: '+4.2%',
      insight: '同赛道对比领先 2.4pct，抢占发布窗口成功',
    },
  ];

  const heatTrendData = volumeTrendData.map((item, index) => ({
    time: item.date,
    heat: item.myVolume,
    acceleration:
      index === 0 ? 0 : Number((((item.myVolume - volumeTrendData[index - 1].myVolume) / volumeTrendData[index - 1].myVolume) * 100).toFixed(1)),
    milestone: item.milestone ?? '',
  }));

  const sourceMixData = platformData.map((platform, index) => {
    const kolRatio = 34 + (index % 3) * 5;
    const ownedRatio = 12 + (index % 2) * 3;
    const kol = Math.round((platform.volume * kolRatio) / 100);
    const owned = Math.round((platform.volume * ownedRatio) / 100);
    const ugc = Math.max(0, platform.volume - kol - owned);
    return {
      platform: platform.platform,
      KOL: kol,
      UGC: ugc,
      官方: owned,
    };
  });

  const topicShareData = [
    { topic: '值不值', share: 27, change: 3.2 },
    { topic: '续航', share: 21, change: 1.7 },
    { topic: '智能', share: 18, change: -2.1 },
    { topic: '空间', share: 16, change: 1.1 },
    { topic: '品牌信任', share: 12, change: -0.6 },
  ];

  const kolPerformance: KOLPerformance[] = [...kolInfluenceData]
    .map((item) => {
      const engagement = Math.round(item.interactionRate * item.fans * 0.015);
      const qualifiedRate = Number((item.interactionRate * 3.6).toFixed(1));
      const sentimentNet = Number(((item.trustLevel - 55) / 4).toFixed(1));
      const misunderstandingRate = Number((Math.max(2, 19 - item.trustLevel * 0.16)).toFixed(1));
      const impactIndex = Math.round(engagement * (qualifiedRate / 100) * (1 + sentimentNet / 20));
      return {
        name: item.name,
        engagement,
        qualifiedRate,
        sentimentNet,
        misunderstandingRate,
        impactIndex,
      };
    })
    .sort((a, b) => b.impactIndex - a.impactIndex)
    .slice(0, 6);

  const scatterData = kolPerformance.map((item) => ({
    x: item.qualifiedRate,
    y: item.engagement,
    z: item.impactIndex,
    name: item.name,
    sentimentNet: item.sentimentNet,
  }));

  const audienceMixData = [
    { platform: '抖音', 车主: 23, 准车主: 31, 观望党: 28, 竞品对比党: 11, 路人: 7 },
    { platform: '小红书', 车主: 19, 准车主: 38, 观望党: 26, 竞品对比党: 10, 路人: 7 },
    { platform: '懂车帝', 车主: 34, 准车主: 29, 观望党: 18, 竞品对比党: 14, 路人: 5 },
    { platform: '微博', 车主: 14, 准车主: 21, 观望党: 35, 竞品对比党: 16, 路人: 14 },
  ];

  const penetrationGapData = [
    { crowd: '准车主', target: 36, actual: 33 },
    { crowd: '竞品对比党', target: 18, actual: 13 },
    { crowd: '科技敏感人群', target: 24, actual: 19 },
    { crowd: '家庭用户', target: 22, actual: 27 },
  ];

  const topicEmotionData = keywordData.slice(0, 6).map((item) => ({
    name: item.text,
    positive: item.sentiment > 0 ? Math.round(item.frequency / 250) : Math.round(item.frequency / 800),
    negative: item.sentiment < 0 ? Math.round(item.frequency / 260) : Math.round(item.frequency / 1100),
  }));

  const contentEffectData = contentRankData.map((item) => ({
    type: item.type,
    engagement: item.avgInteraction,
    qualified: Math.round(item.avgInteraction * 0.25),
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-4 font-['Noto_Sans_SC']"
    >
      <section className="relative overflow-hidden rounded-3xl border border-blue-200/80 bg-[radial-gradient(circle_at_12%_18%,rgba(56,189,248,0.18),transparent_42%),radial-gradient(circle_at_92%_0%,rgba(59,130,246,0.12),transparent_38%),linear-gradient(135deg,#f7fbff,#eef6ff,#e9f2ff)] p-5 text-slate-900 shadow-sm">
        <div className="absolute right-4 top-4 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs text-blue-700">
          营销战情室实时视图
        </div>
        <p className="text-xs uppercase tracking-[0.2em] text-blue-600">Module A 事件总览</p>
        <h2 className="mt-2 font-['Noto_Serif_SC'] text-2xl md:text-3xl">这波上市传播，整体打得怎么样</h2>
        <p className="mt-2 max-w-3xl text-sm text-slate-600">
          看板将“声量”升级为“态势判断”：是否在涨、为什么涨、还能不能继续涨，以及哪些平台在接管传播。
        </p>

        <div className="mt-4 grid grid-cols-1 gap-2 md:grid-cols-2 xl:grid-cols-5">
          {heroKpis.map((item) => (
            <div key={item.label} className="rounded-2xl border border-blue-100 bg-white p-3">
              <p className="text-xs text-slate-400">{item.label}</p>
              <p className="mt-1 text-xl font-semibold text-slate-900">{item.value}</p>
              <p className="mt-1 text-xs text-blue-600">{item.delta}</p>
              <p className="mt-1 text-xs text-slate-400">{item.insight}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-7">
          <SectionCard title="热度趋势与增速" subtitle="折线标注关键节点，判断热度是否进入可持续扩散">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={heatTrendData}>
                  <defs>
                    <linearGradient id="heatFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#38bdf8" stopOpacity={0.55} />
                      <stop offset="100%" stopColor="#38bdf8" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ background: '#ffffff', border: '1px solid #bfdbfe', borderRadius: '12px', color: '#0f172a' }}
                    formatter={(value: number, name: string) => (name === 'heat' ? `${formatWan(value)} 条` : `${formatDelta(value)}`)}
                  />
                  <Area dataKey="heat" name="heat" stroke="#38bdf8" fill="url(#heatFill)" strokeWidth={2.6} />
                  <Line dataKey="acceleration" name="acceleration" stroke="#34d399" strokeWidth={2.2} dot={false} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-5">
          <SectionCard title="平台与来源结构" subtitle="按平台拆解 KOL / UGC / 官方来源，快速识别传播引擎">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sourceMixData}>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="platform" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="UGC" stackId="a" fill="#0ea5e9" />
                  <Bar dataKey="KOL" stackId="a" fill="#14b8a6" />
                  <Bar dataKey="官方" stackId="a" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-5">
          <SectionCard title="Module B 主命题占比 Top5" subtitle="横向条形 + 24h 变化箭头，识别命题竞争态势">
            <div className="space-y-3">
              {topicShareData.map((item) => (
                <div key={item.topic}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-slate-700">{item.topic}</span>
                    <span className={item.change >= 0 ? 'text-emerald-600' : 'text-rose-600'}>
                      {item.change >= 0 ? '↑' : '↓'} {Math.abs(item.change).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-blue-100">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-emerald-400"
                      style={{ width: `${item.share}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-slate-500">命题占比 {item.share}%</p>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-4">
          <SectionCard title="记忆点 Top 句" subtitle="不是词云，直接沉淀可复用表达">
            <div className="space-y-2.5">
              {memoryPoints.map((item) => (
                <div key={item.phrase} className="rounded-2xl border border-blue-100 bg-blue-50/50 p-3">
                  <p className="text-sm text-slate-800">{item.phrase}</p>
                  <div className="mt-2 flex items-center justify-between text-xs">
                    <span className="text-slate-400">出现 {item.count.toLocaleString()} 次</span>
                    <span style={{ color: sentimentColorMap[item.sentiment] }}>{item.sentiment}</span>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-3">
          <SectionCard title="主张拉通漏斗" subtitle="曝光到兴趣的转化链路">
            <div className="space-y-3">
              {funnelData.map((item, index) => (
                <div key={item.stage}>
                  <div className="mb-1 flex items-center justify-between text-xs text-slate-600">
                    <span>{item.stage}</span>
                    <span>{item.rate}%</span>
                  </div>
                  <div className="h-2.5 overflow-hidden rounded-full bg-blue-100">
                    <div
                      className="h-full rounded-full"
                      style={{
                        width: `${item.rate}%`,
                        background:
                          index < 2 ? 'linear-gradient(90deg,#38bdf8,#34d399)' : 'linear-gradient(90deg,#f59e0b,#f97316)',
                      }}
                    />
                  </div>
                </div>
              ))}
              <div className="rounded-xl border border-rose-200 bg-rose-50 p-3 text-xs text-rose-700">
                主张偏移率 18.6%，集中在“智能=花哨”的误解路径。
              </div>
            </div>
          </SectionCard>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-7">
          <SectionCard title="Module C KOL/内容有效性象限" subtitle="X=有效互动率，Y=互动量，气泡=贡献指数，颜色=情绪净值">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid stroke="#dbeafe" />
                  <XAxis
                    dataKey="x"
                    type="number"
                    name="有效互动率"
                    unit="%"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 11 }}
                  />
                  <YAxis
                    dataKey="y"
                    type="number"
                    name="互动量"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 11 }}
                  />
                  <ZAxis dataKey="z" range={[120, 920]} name="贡献指数" />
                  <Tooltip
                    cursor={{ strokeDasharray: '4 4' }}
                    contentStyle={{ background: '#ffffff', border: '1px solid #bfdbfe', borderRadius: '12px' }}
                    formatter={(value: number, name: string) => (name === '有效互动率' ? `${value}%` : value.toLocaleString())}
                  />
                  <Scatter data={scatterData} fill="#0ea5e9">
                    {scatterData.map((item) => (
                      <Cell key={item.name} fill={item.sentimentNet > 3 ? '#22c55e' : item.sentimentNet > 0 ? '#0ea5e9' : '#fb7185'} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-5">
          <SectionCard title="KOL 贡献指数榜单" subtitle="量 × 质 × 风险综合排序，定位高热高效与高热误伤">
            <div className="space-y-2.5">
              {kolPerformance.map((item, index) => (
                <div key={item.name} className="rounded-2xl border border-blue-100 bg-white p-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm text-slate-800">
                      {index + 1}. {item.name}
                    </p>
                    <p className="text-sm font-semibold text-blue-600">{item.impactIndex.toLocaleString()}</p>
                  </div>
                  <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-slate-400">
                    <span>互动量 {formatWan(item.engagement)}</span>
                    <span>有效互动率 {item.qualifiedRate}%</span>
                    <span className={item.sentimentNet >= 0 ? 'text-emerald-600' : 'text-rose-600'}>
                      情绪净值 {item.sentimentNet}
                    </span>
                    <span className={item.misunderstandingRate < 8 ? 'text-emerald-600' : 'text-amber-600'}>
                      误伤率 {item.misunderstandingRate}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-7">
          <SectionCard title="Module D 圈层与人群穿透" subtitle="不同平台人群结构对比，识别触达偏差与补量机会">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={audienceMixData}>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="platform" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="车主" stackId="a" fill="#0ea5e9" />
                  <Bar dataKey="准车主" stackId="a" fill="#22c55e" />
                  <Bar dataKey="观望党" stackId="a" fill="#f59e0b" />
                  <Bar dataKey="竞品对比党" stackId="a" fill="#f97316" />
                  <Bar dataKey="路人" stackId="a" fill="#94a3b8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-5 space-y-4">
          <SectionCard title="圈层穿透差 Penetration Gap" subtitle="目标圈层占比 vs 实际占比">
            <div className="space-y-2.5">
              {penetrationGapData.map((item) => {
                const gap = item.actual - item.target;
                return (
                  <div key={item.crowd}>
                    <div className="mb-1 flex items-center justify-between text-xs text-slate-600">
                      <span>{item.crowd}</span>
                      <span className={gap >= 0 ? 'text-emerald-600' : 'text-rose-600'}>
                        {gap >= 0 ? '+' : ''}
                        {gap}pct
                      </span>
                    </div>
                    <div className="h-2 rounded-full bg-blue-100">
                      <div className="h-full rounded-full bg-sky-500" style={{ width: `${item.actual}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </SectionCard>

          <SectionCard title="意向漏斗 Intent Mix" subtitle="了解→对比→试驾→购买意向→放弃">
            <div className="space-y-2">
              {intentMix.map((item) => (
                <div key={item.stage} className="rounded-xl border border-blue-100 bg-blue-50/50 p-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-600">{item.stage}</span>
                    <span className="text-slate-800">{item.value}%</span>
                  </div>
                  <div className="mt-2 h-1.5 rounded-full bg-blue-100">
                    <div className="h-full rounded-full" style={{ width: `${item.value}%`, backgroundColor: item.color }} />
                  </div>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-6">
          <SectionCard title="内容主题正负反馈" subtitle="验证话题质量，避免高热低质内容占据主舞台">
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={topicEmotionData}>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="positive" name="正向" fill="#22c55e" />
                  <Bar dataKey="negative" name="负向" fill="#fb7185" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-6">
          <SectionCard title="内容形态效率对比" subtitle="从互动量与有效互动双指标看内容策略">
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={contentEffectData}>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="type" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#ffffff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Legend wrapperStyle={{ fontSize: '12px' }} />
                  <Bar dataKey="engagement" name="互动量" fill="#0ea5e9" />
                  <Bar dataKey="qualified" name="有效互动量" fill="#f59e0b" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>
      </section>
    </motion.div>
  );
}

