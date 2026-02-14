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
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  contentRankData,
  keywordData,
  kolInfluenceData,
  marketKPIData,
  platformData,
  volumeTrendData,
} from './data/marketChartData';

const sentimentPalette = ['#1f8a70', '#f59e0b', '#ef4444'];

function formatWan(value: number) {
  return value >= 10000 ? `${(value / 10000).toFixed(1)}万` : value.toLocaleString();
}

function Card({ title, subtitle, children }: { title: string; subtitle?: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm">
      <div className="mb-4">
        <h3 className="text-base font-semibold text-gray-900">{title}</h3>
        {subtitle ? <p className="mt-1 text-xs text-gray-500">{subtitle}</p> : null}
      </div>
      {children}
    </div>
  );
}

export default function MarketDashboard() {
  const totalVolume = Number(marketKPIData.find((item) => item.type === 'volume')?.value ?? 0);
  const interaction = Number(marketKPIData.find((item) => item.type === 'interaction')?.value ?? 0);
  const breakout = Number(marketKPIData.find((item) => item.type === 'index')?.value ?? 0);
  const kolContribution = Number(marketKPIData.find((item) => item.type === 'kol')?.value ?? 0);
  const negativeRatio = Number(marketKPIData.find((item) => item.type === 'negative')?.value ?? 0);

  const monthlyVolumeData = volumeTrendData.slice(-6).map((item, idx) => ({
    month: `M${idx + 1}`,
    volume: item.myVolume,
    interaction: item.interaction,
  }));

  const sentimentData = [
    { name: '正面', value: 67.2 },
    { name: '中性', value: 24.6 },
    { name: '负面', value: 8.2 },
  ];

  const platformBars = [...platformData]
    .sort((a, b) => b.volume - a.volume)
    .slice(0, 5)
    .map((item) => ({
      name: item.platform,
      ratio: Number(((item.volume / totalVolume) * 100).toFixed(1)),
    }));

  const kolRankData = [...kolInfluenceData]
    .map((k) => ({
      ...k,
      score: Math.round(k.interactionRate * 6 + k.trustLevel * 0.8 + k.fans / 100000),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);

  const contentPerformanceData = contentRankData.map((item) => ({
    type: item.type,
    interaction: item.avgInteraction,
    share: Math.round(item.avgInteraction * 0.2),
    comment: Math.round(item.avgInteraction * 0.12),
  }));

  const claimAcceptanceData = [
    { name: '认同', value: 61, color: '#1f8a70' },
    { name: '观望', value: 24, color: '#f59e0b' },
    { name: '质疑', value: 15, color: '#ef4444' },
  ];

  const claimTrendData = [
    { t: 'W1', positive: 58, negative: 17 },
    { t: 'W2', positive: 60, negative: 16 },
    { t: 'W3', positive: 63, negative: 15 },
    { t: 'W4', positive: 61, negative: 17 },
    { t: 'W5', positive: 64, negative: 14 },
    { t: 'W6', positive: 66, negative: 13 },
  ];

  const feedbackThemeData = keywordData
    .slice(0, 6)
    .map((item) => ({
      theme: item.text,
      positive: item.sentiment > 0 ? Math.round(item.frequency / 400) : Math.round(item.frequency / 1000),
      negative: item.sentiment < 0 ? Math.round(item.frequency / 350) : Math.round(item.frequency / 1300),
    }));

  const interactionTopicData = contentRankData
    .slice(0, 5)
    .map((item) => ({ topic: item.type, value: item.avgInteraction }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.35 }}
      className="space-y-6"
    >
      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm xl:col-span-8">
          <p className="text-xs uppercase tracking-[0.14em] text-gray-500">品牌传播概况</p>
          <h2 className="mt-2 text-4xl font-semibold text-gray-900">{formatWan(totalVolume)} 条</h2>
          <p className="mt-1 text-sm text-emerald-600">市场传播总声量，较上周期 +34%</p>

          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
            <div className="rounded-xl border border-gray-100 bg-gray-50 p-3">
              <p className="text-xs text-gray-500">总互动量</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{formatWan(interaction * 10000)}</p>
            </div>
            <div className="rounded-xl border border-gray-100 bg-gray-50 p-3">
              <p className="text-xs text-gray-500">破圈指数</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{breakout}%</p>
            </div>
            <div className="rounded-xl border border-gray-100 bg-gray-50 p-3">
              <p className="text-xs text-gray-500">KOL贡献度</p>
              <p className="mt-1 text-lg font-semibold text-gray-900">{kolContribution}%</p>
            </div>
          </div>

          <div className="mt-5 h-56">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyVolumeData}>
                <defs>
                  <linearGradient id="volumeFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#2563eb" stopOpacity={0.35} />
                    <stop offset="100%" stopColor="#2563eb" stopOpacity={0.03} />
                  </linearGradient>
                </defs>
                <CartesianGrid stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip />
                <Area type="monotone" dataKey="volume" stroke="#2563eb" fill="url(#volumeFill)" strokeWidth={2.5} />
                <Line type="monotone" dataKey="interaction" stroke="#0f172a" strokeWidth={1.8} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="space-y-6 xl:col-span-4">
          <Card title="品牌认知度" subtitle="正面 / 中性 / 负面情感结构">
            <div className="h-44">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={sentimentData} dataKey="value" nameKey="name" innerRadius={45} outerRadius={70}>
                    {sentimentData.map((_, i) => (
                      <Cell key={i} fill={sentimentPalette[i]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-2">
              {sentimentData.map((item, index) => (
                <div key={item.name} className="flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 text-gray-600">
                    <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: sentimentPalette[index] }} />
                    {item.name}
                  </div>
                  <span className="font-medium text-gray-900">{item.value}%</span>
                </div>
              ))}
            </div>
          </Card>

          <Card title="平台贡献分布" subtitle="类似 Spending by Category">
            <div className="space-y-3">
              {platformBars.map((item) => (
                <div key={item.name}>
                  <div className="mb-1 flex items-center justify-between text-xs text-gray-600">
                    <span>{item.name}</span>
                    <span>{item.ratio}%</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                    <div className="h-full rounded-full bg-gradient-to-r from-[#3b82f6] to-[#1d4ed8]" style={{ width: `${item.ratio}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm xl:col-span-5">
          <h3 className="text-base font-semibold text-gray-900">KOL排行榜</h3>
          <p className="mt-1 text-xs text-gray-500">综合粉丝量、互动率、信任度计算影响力</p>
          <div className="mt-4 space-y-3">
            {kolRankData.map((item, idx) => (
              <div key={item.name} className="rounded-xl border border-gray-100 p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-slate-900 text-xs text-white">{idx + 1}</span>
                    <p className="text-sm font-medium text-gray-900">{item.name}</p>
                  </div>
                  <p className="text-sm font-semibold text-blue-600">{item.score}</p>
                </div>
                <div className="mt-2 grid grid-cols-3 gap-2 text-xs text-gray-500">
                  <span>粉丝 {formatWan(item.fans)}</span>
                  <span>互动 {item.interactionRate}%</span>
                  <span>情感 {item.trustLevel}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm xl:col-span-7">
          <h3 className="text-base font-semibold text-gray-900">传播内容分析</h3>
          <p className="mt-1 text-xs text-gray-500">对比不同内容类型的互动、分享、评论表现</p>
          <div className="mt-3 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={contentPerformanceData}>
                <CartesianGrid stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="type" tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip />
                <Legend />
                <Bar dataKey="interaction" name="互动量" fill="#2563eb" radius={[5, 5, 0, 0]} />
                <Bar dataKey="share" name="分享量" fill="#14b8a6" radius={[5, 5, 0, 0]} />
                <Bar dataKey="comment" name="评论量" fill="#f59e0b" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm xl:col-span-5">
          <h3 className="text-base font-semibold text-gray-900">品牌主张认同度</h3>
          <p className="mt-1 text-xs text-gray-500">“智能不贵”主张下的用户态度分布</p>
          <div className="mt-2 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={claimAcceptanceData} dataKey="value" nameKey="name" outerRadius={90}>
                  {claimAcceptanceData.map((item) => (
                    <Cell key={item.name} fill={item.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm xl:col-span-7">
          <h3 className="text-base font-semibold text-gray-900">品牌主张情感趋势</h3>
          <p className="mt-1 text-xs text-gray-500">观察认同度变化，及时调整传播策略</p>
          <div className="mt-3 h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={claimTrendData}>
                <CartesianGrid stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="t" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="positive" name="正向认同" stroke="#10b981" strokeWidth={2.4} />
                <Line type="monotone" dataKey="negative" name="负向反馈" stroke="#ef4444" strokeWidth={2.2} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-6 xl:grid-cols-12">
        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm xl:col-span-6">
          <h3 className="text-base font-semibold text-gray-900">用户评论分析与反馈</h3>
          <p className="mt-1 text-xs text-gray-500">按主题对比正负情感评论量</p>
          <div className="mt-3 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={feedbackThemeData}>
                <CartesianGrid stroke="#f1f5f9" vertical={false} />
                <XAxis dataKey="theme" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                <Tooltip />
                <Legend />
                <Bar dataKey="positive" name="正面评论" stackId="a" fill="#16a34a" />
                <Bar dataKey="negative" name="负面评论" stackId="a" fill="#ef4444" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="rounded-2xl border border-gray-200 bg-white p-5 shadow-sm xl:col-span-6">
          <h3 className="text-base font-semibold text-gray-900">互动话题热度</h3>
          <p className="mt-1 text-xs text-gray-500">识别最容易引发用户讨论的内容主题</p>
          <div className="mt-3 h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={interactionTopicData} layout="vertical">
                <CartesianGrid stroke="#f1f5f9" horizontal={false} />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                <YAxis dataKey="topic" type="category" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} width={80} />
                <Tooltip />
                <Bar dataKey="value" fill="#0ea5e9" radius={[0, 6, 6, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 rounded-xl border border-red-100 bg-red-50 px-3 py-2 text-xs text-red-700">
            当前负向情感占比 {negativeRatio}% ，建议优先跟进“价格贵”“卡顿”相关反馈。
          </div>
        </div>
      </section>
    </motion.div>
  );
}
