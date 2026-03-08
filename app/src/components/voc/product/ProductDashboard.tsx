import { motion } from 'framer-motion';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  Treemap,
  XAxis,
  YAxis,
} from 'recharts';

interface HeroKPI {
  label: string;
  value: string;
  delta: string;
  insight: string;
}

interface IssueDomain {
  issue: string;
  share: number;
  growth24h: number;
}

interface SourcePlatformRow {
  platform: string;
  车主: number;
  试驾: number;
  观望: number;
  转述: number;
}

interface TrendPoint {
  time: string;
  [key: string]: string | number;
}

interface HeatmapRow {
  issue: string;
  抖音: number;
  小红书: number;
  微博: number;
  懂车帝: number;
}

interface SignalCard {
  title: string;
  sample: string;
  score: string;
}

interface EvidenceRow {
  issue: string;
  亲历车主试驾: number;
  视频实测: number;
  截图故障码: number;
  对比引用: number;
  转述: number;
}

interface EvidenceBubble {
  issue: string;
  evidenceStrength: number;
  acceleration: number;
  impact: number;
  controllability: 'OTA可修' | '服务可缓解' | '需硬件改动';
}

interface EvidenceWall {
  issue: string;
  comment: string;
  source: string;
}

interface ImpactQuadrant {
  issue: string;
  purchaseImpact: number;
  usageImpact: number;
}

interface ImpactStackRow {
  issue: string;
  购买型表达: number;
  使用型表达: number;
}

interface PathTreeNode {
  name: string;
  size?: number;
  children?: PathTreeNode[];
}

interface PriorityBoardItem {
  issue: string;
  priorityIndex: number;
  acceleration: number;
  evidenceStrength: number;
  impactScore: number;
  path: string;
  eta: '快' | '中' | '慢';
}

const heroKpis: HeroKPI[] = [
  {
    label: '产品相关讨论量',
    value: '9.6万条',
    delta: '+22.4%',
    insight: '过滤非产品话题后，占事件总讨论 74%',
  },
  {
    label: '负面强情绪占比',
    value: '31%',
    delta: '+4.1%',
    insight: '愤怒/嘲讽/失望表达抬升，需快速压制',
  },
  {
    label: '跨平台覆盖',
    value: '4个平台',
    delta: '+1',
    insight: '从垂类平台外溢至泛社媒，进入破圈阶段',
  },
  {
    label: '证据可信占比',
    value: '57%',
    delta: '+6.0%',
    insight: '车主亲历与试驾实测合计占比持续提升',
  },
  {
    label: '高风险问题数',
    value: '5个',
    delta: '+2',
    insight: '已形成标签化表达，需分路径处置',
  },
];

const issueDomainData: IssueDomain[] = [
  { issue: '车机卡顿', share: 24, growth24h: 18.5 },
  { issue: '续航偏差', share: 18, growth24h: 12.1 },
  { issue: '充电速度', share: 14, growth24h: 9.4 },
  { issue: '异响问题', share: 11, growth24h: 21.7 },
  { issue: '做工细节', share: 9, growth24h: 5.6 },
  { issue: '智驾稳定性', share: 8, growth24h: 16.3 },
];

const sourcePlatformData: SourcePlatformRow[] = [
  { platform: '抖音', 车主: 21, 试驾: 26, 观望: 34, 转述: 19 },
  { platform: '小红书', 车主: 18, 试驾: 31, 观望: 29, 转述: 22 },
  { platform: '微博', 车主: 12, 试驾: 18, 观望: 38, 转述: 32 },
  { platform: '懂车帝', 车主: 28, 试驾: 32, 观望: 24, 转述: 16 },
];

const painAccelerationTrend: TrendPoint[] = [
  { time: 'D-4', 车机卡顿: 680, 续航偏差: 520, 充电速度: 390, 异响问题: 260, 智驾稳定性: 300 },
  { time: 'D-3', 车机卡顿: 730, 续航偏差: 560, 充电速度: 410, 异响问题: 280, 智驾稳定性: 320 },
  { time: 'D-2', 车机卡顿: 820, 续航偏差: 610, 充电速度: 450, 异响问题: 340, 智驾稳定性: 390 },
  { time: 'D-1', 车机卡顿: 940, 续航偏差: 690, 充电速度: 520, 异响问题: 430, 智驾稳定性: 470 },
  { time: 'D0', 车机卡顿: 1260, 续航偏差: 840, 充电速度: 680, 异响问题: 610, 智驾稳定性: 720 },
  { time: 'D+1', 车机卡顿: 1350, 续航偏差: 900, 充电速度: 730, 异响问题: 720, 智驾稳定性: 780 },
  { time: 'D+2', 车机卡顿: 1520, 续航偏差: 980, 充电速度: 790, 异响问题: 810, 智驾稳定性: 860 },
];

const heatmapData: HeatmapRow[] = [
  { issue: '车机卡顿', 抖音: 86, 小红书: 58, 微博: 72, 懂车帝: 81 },
  { issue: '续航偏差', 抖音: 69, 小红书: 62, 微博: 55, 懂车帝: 77 },
  { issue: '充电速度', 抖音: 64, 小红书: 71, 微博: 49, 懂车帝: 68 },
  { issue: '异响问题', 抖音: 53, 小红书: 45, 微博: 74, 懂车帝: 61 },
  { issue: '智驾稳定性', 抖音: 58, 小红书: 66, 微博: 51, 懂车帝: 72 },
];

const signalCards: SignalCard[] = [
  {
    title: '标签化信号 01',
    sample: '“智驾不敢开，最后还得自己接管”',
    score: '48h 复现率 37%',
  },
  {
    title: '标签化信号 02',
    sample: '“冬天续航打骨折，通勤都得算电量”',
    score: '72h 复现率 29%',
  },
  {
    title: '标签化信号 03',
    sample: '“车机像手机老化，一卡就全车跟着慢”',
    score: '24h 增速 +18.5%',
  },
];

const evidenceTypeData: EvidenceRow[] = [
  { issue: '车机卡顿', 亲历车主试驾: 34, 视频实测: 22, 截图故障码: 16, 对比引用: 18, 转述: 10 },
  { issue: '续航偏差', 亲历车主试驾: 30, 视频实测: 27, 截图故障码: 14, 对比引用: 17, 转述: 12 },
  { issue: '充电速度', 亲历车主试驾: 26, 视频实测: 31, 截图故障码: 18, 对比引用: 15, 转述: 10 },
  { issue: '异响问题', 亲历车主试驾: 38, 视频实测: 18, 截图故障码: 21, 对比引用: 12, 转述: 11 },
  { issue: '智驾稳定性', 亲历车主试驾: 24, 视频实测: 33, 截图故障码: 12, 对比引用: 19, 转述: 12 },
];

const evidenceBubbleData: EvidenceBubble[] = [
  { issue: '车机卡顿', evidenceStrength: 78, acceleration: 19, impact: 86, controllability: 'OTA可修' },
  { issue: '续航偏差', evidenceStrength: 74, acceleration: 12, impact: 90, controllability: '需硬件改动' },
  { issue: '充电速度', evidenceStrength: 69, acceleration: 10, impact: 71, controllability: '服务可缓解' },
  { issue: '异响问题', evidenceStrength: 82, acceleration: 22, impact: 75, controllability: '需硬件改动' },
  { issue: '智驾稳定性', evidenceStrength: 72, acceleration: 16, impact: 88, controllability: 'OTA可修' },
];

const evidenceWall: EvidenceWall[] = [
  {
    issue: '车机卡顿',
    comment: '导航+音乐同时开就卡，倒车影像会延迟，视频里录出来了。',
    source: '来源：车主实拍视频',
  },
  {
    issue: '续航偏差',
    comment: '表显还剩 120km，实际跑了 70km 就提示低电，连续两周都这样。',
    source: '来源：亲历车主 + 行车记录截图',
  },
  {
    issue: '异响问题',
    comment: '过减速带中控右侧持续异响，4S复检后仍复现。',
    source: '来源：售后工单截图',
  },
];

const impactQuadrantData: ImpactQuadrant[] = [
  { issue: '车机卡顿', purchaseImpact: 68, usageImpact: 82 },
  { issue: '续航偏差', purchaseImpact: 84, usageImpact: 79 },
  { issue: '充电速度', purchaseImpact: 61, usageImpact: 66 },
  { issue: '异响问题', purchaseImpact: 49, usageImpact: 75 },
  { issue: '智驾稳定性', purchaseImpact: 88, usageImpact: 71 },
];

const impactStackData: ImpactStackRow[] = [
  { issue: '车机卡顿', 购买型表达: 38, 使用型表达: 62 },
  { issue: '续航偏差', 购买型表达: 57, 使用型表达: 43 },
  { issue: '充电速度', 购买型表达: 46, 使用型表达: 54 },
  { issue: '异响问题', 购买型表达: 29, 使用型表达: 71 },
  { issue: '智驾稳定性', 购买型表达: 63, 使用型表达: 37 },
];

const pathTreeData: PathTreeNode[] = [
  {
    name: '处置路径',
    children: [
      { name: 'OTA可修', children: [{ name: '车机卡顿', size: 42 }, { name: '智驾稳定性', size: 36 }] },
      { name: '服务可缓解', children: [{ name: '充电速度', size: 28 }] },
      { name: '需硬件改动', children: [{ name: '续航偏差', size: 34 }, { name: '异响问题', size: 31 }] },
    ],
  },
];

const priorityBoardData: PriorityBoardItem[] = [
  { issue: '智驾稳定性', priorityIndex: 92, acceleration: 16, evidenceStrength: 72, impactScore: 86, path: 'OTA修复+策略回归', eta: '快' },
  { issue: '车机卡顿', priorityIndex: 89, acceleration: 19, evidenceStrength: 78, impactScore: 84, path: 'OTA性能优化', eta: '快' },
  { issue: '续航偏差', priorityIndex: 86, acceleration: 12, evidenceStrength: 74, impactScore: 90, path: '硬件改版+标定修正', eta: '慢' },
  { issue: '异响问题', priorityIndex: 81, acceleration: 22, evidenceStrength: 82, impactScore: 73, path: '供应链批次排查', eta: '中' },
  { issue: '充电速度', priorityIndex: 74, acceleration: 10, evidenceStrength: 69, impactScore: 68, path: '服务流程优化', eta: '中' },
];

const colorScale = ['#eff6ff', '#dbeafe', '#bfdbfe', '#93c5fd', '#60a5fa', '#3b82f6'];

function getHeatColor(value: number) {
  if (value >= 80) return colorScale[5];
  if (value >= 70) return colorScale[4];
  if (value >= 60) return colorScale[3];
  if (value >= 50) return colorScale[2];
  if (value >= 40) return colorScale[1];
  return colorScale[0];
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

export default function ProductDashboard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="space-y-4 font-['Noto_Sans_SC']"
    >
      <section className="relative overflow-hidden rounded-3xl border border-blue-200/80 bg-[radial-gradient(circle_at_12%_18%,rgba(56,189,248,0.16),transparent_42%),radial-gradient(circle_at_92%_0%,rgba(99,102,241,0.12),transparent_38%),linear-gradient(135deg,#f7fbff,#eef6ff,#e9f2ff)] p-5 text-slate-900 shadow-sm">
        <div className="absolute right-4 top-4 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-xs text-blue-700">
          产品问题战情视图
        </div>
        <p className="text-xs uppercase tracking-[0.2em] text-blue-600">Module A 事件产品态势卡</p>
        <h2 className="mt-2 font-['Noto_Serif_SC'] text-2xl md:text-3xl">30秒看懂：产品问题宇宙与加速方向</h2>
        <p className="mt-2 max-w-3xl text-sm text-slate-600">
          这个视图用于快速判断“问题是什么、在哪儿扩散、证据够不够硬、该先处理谁”，支持产品、质量、服务协同决策。
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
        <div className="xl:col-span-5">
          <SectionCard title="Top 问题域（近24h增速）" subtitle="问题占比 + 增速箭头，识别加速风险">
            <div className="space-y-3">
              {issueDomainData.map((item) => (
                <div key={item.issue}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="text-slate-700">{item.issue}</span>
                    <span className={item.growth24h >= 0 ? 'text-blue-600' : 'text-slate-500'}>
                      {item.growth24h >= 0 ? '↑' : '↓'} {Math.abs(item.growth24h).toFixed(1)}%
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-blue-100">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-sky-400 to-indigo-500"
                      style={{ width: `${item.share * 3}%` }}
                    />
                  </div>
                  <p className="mt-1 text-xs text-slate-500">问题域占比 {item.share}%</p>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-7">
          <SectionCard title="来源结构 × 平台" subtitle="车主/试驾/观望/转述构成，判断证据可信度前置线索">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={sourcePlatformData}>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="platform" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Bar dataKey="车主" stackId="a" fill="#0ea5e9" />
                  <Bar dataKey="试驾" stackId="a" fill="#3b82f6" />
                  <Bar dataKey="观望" stackId="a" fill="#6366f1" />
                  <Bar dataKey="转述" stackId="a" fill="#94a3b8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-7">
          <SectionCard title="Module B 痛点加速度趋势" subtitle="Top5 问题互动加权声量，标注是否正在标签化">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={painAccelerationTrend}>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Line dataKey="车机卡顿" stroke="#0ea5e9" strokeWidth={2.4} dot={false} />
                  <Line dataKey="续航偏差" stroke="#3b82f6" strokeWidth={2.2} dot={false} />
                  <Line dataKey="充电速度" stroke="#6366f1" strokeWidth={2.2} dot={false} />
                  <Line dataKey="异响问题" stroke="#1d4ed8" strokeWidth={2.2} dot={false} />
                  <Line dataKey="智驾稳定性" stroke="#334155" strokeWidth={2.2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-5 space-y-4">
          <SectionCard title="问题 × 平台热力" subtitle="看问题是否跨圈层扩散">
            <div className="space-y-2">
              {heatmapData.map((row) => (
                <div key={row.issue} className="grid grid-cols-5 gap-1.5">
                  <div className="truncate rounded-lg bg-slate-50 px-2 py-1 text-xs text-slate-600">{row.issue}</div>
                  {(['抖音', '小红书', '微博', '懂车帝'] as const).map((platform) => (
                    <div
                      key={`${row.issue}-${platform}`}
                      className="rounded-lg px-2 py-1 text-center text-xs font-medium text-slate-700"
                      style={{ backgroundColor: getHeatColor(row[platform]) }}
                    >
                      {row[platform]}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </SectionCard>

          <SectionCard title="标签化信号卡片" subtitle="固定话术/段子化表达（原声示例）">
            <div className="space-y-2.5">
              {signalCards.map((item) => (
                <div key={item.title} className="rounded-2xl border border-blue-100 bg-blue-50/60 p-3">
                  <p className="text-xs font-medium text-blue-700">{item.title}</p>
                  <p className="mt-1 text-sm text-slate-800">{item.sample}</p>
                  <p className="mt-2 text-xs text-slate-500">{item.score}</p>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-6">
          <SectionCard title="Module C 证据类型分布" subtitle="各问题证据类型构成，区分硬问题与情绪噪音">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={evidenceTypeData}>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="issue" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Bar dataKey="亲历车主试驾" stackId="a" fill="#0ea5e9" />
                  <Bar dataKey="视频实测" stackId="a" fill="#3b82f6" />
                  <Bar dataKey="截图故障码" stackId="a" fill="#6366f1" />
                  <Bar dataKey="对比引用" stackId="a" fill="#1d4ed8" />
                  <Bar dataKey="转述" stackId="a" fill="#94a3b8" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-6">
          <SectionCard title="证据强度 × 加速度气泡图" subtitle="X=证据强度，Y=加速度，气泡=影响面，颜色=可控性">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 12, right: 20, left: 8, bottom: 8 }}>
                  <CartesianGrid stroke="#dbeafe" />
                  <XAxis
                    type="number"
                    dataKey="evidenceStrength"
                    domain={[40, 100]}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 11 }}
                    name="证据强度"
                    unit="%"
                  />
                  <YAxis
                    type="number"
                    dataKey="acceleration"
                    domain={[0, 30]}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 11 }}
                    name="加速度"
                    unit="%"
                  />
                  <Tooltip
                    contentStyle={{ background: '#fff', border: '1px solid #bfdbfe', borderRadius: '12px' }}
                    formatter={(value: number, name: string) => `${value}${name === '加速度' ? '%' : ''}`}
                  />
                  <Scatter data={evidenceBubbleData} dataKey="impact">
                    {evidenceBubbleData.map((item) => (
                      <Cell
                        key={item.issue}
                        fill={
                          item.controllability === 'OTA可修'
                            ? '#0ea5e9'
                            : item.controllability === '服务可缓解'
                              ? '#3b82f6'
                              : '#334155'
                        }
                      />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-6">
          <SectionCard title="证据墙（Top问题原声）" subtitle="每个问题 1 条典型评论 + 证据来源">
            <div className="space-y-2.5">
              {evidenceWall.map((item) => (
                <div key={item.issue} className="rounded-2xl border border-blue-100 bg-white p-3">
                  <p className="text-xs text-blue-700">{item.issue}</p>
                  <p className="mt-1 text-sm text-slate-800">{item.comment}</p>
                  <p className="mt-2 text-xs text-slate-500">{item.source}</p>
                </div>
              ))}
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-6">
          <SectionCard title="Module D 影响面四象限" subtitle="横轴购买影响，纵轴使用影响，识别阻碍成交 vs 拖累口碑">
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 20, left: 6, bottom: 8 }}>
                  <CartesianGrid stroke="#dbeafe" />
                  <ReferenceLine x={50} stroke="#93c5fd" strokeDasharray="4 4" />
                  <ReferenceLine y={50} stroke="#93c5fd" strokeDasharray="4 4" />
                  <XAxis
                    type="number"
                    dataKey="purchaseImpact"
                    domain={[20, 100]}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 11 }}
                    name="购买影响"
                    unit="%"
                  />
                  <YAxis
                    type="number"
                    dataKey="usageImpact"
                    domain={[20, 100]}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#64748b', fontSize: 11 }}
                    name="使用影响"
                    unit="%"
                  />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Scatter data={impactQuadrantData} fill="#2563eb" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-12">
        <div className="xl:col-span-6">
          <SectionCard title="问题表达占比（购买型 vs 使用型）" subtitle="用于判断处理目标是“促成交”还是“稳口碑”">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={impactStackData}>
                  <CartesianGrid stroke="#dbeafe" vertical={false} />
                  <XAxis dataKey="issue" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 11 }} />
                  <Tooltip contentStyle={{ background: '#fff', border: '1px solid #bfdbfe', borderRadius: '12px' }} />
                  <Bar dataKey="购买型表达" stackId="a" fill="#2563eb" />
                  <Bar dataKey="使用型表达" stackId="a" fill="#0ea5e9" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </SectionCard>
        </div>

        <div className="xl:col-span-6">
          <SectionCard title="Module E 问题 → 处置路径" subtitle="Treemap：OTA / 服务 / 改款分流，避免产品部被动挨打">
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <Treemap
                  data={pathTreeData}
                  dataKey="size"
                  nameKey="name"
                  aspectRatio={4 / 3}
                  stroke="#ffffff"
                  fill="#3b82f6"
                />
              </ResponsiveContainer>
            </div>
            <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-600">
              <span className="rounded-full border border-blue-200 bg-blue-50 px-2 py-1">OTA可修：蓝</span>
              <span className="rounded-full border border-indigo-200 bg-indigo-50 px-2 py-1">服务可缓解：靛</span>
              <span className="rounded-full border border-slate-300 bg-slate-50 px-2 py-1">需硬件改动：深灰</span>
            </div>
          </SectionCard>
        </div>
      </section>

      <section>
        <SectionCard title="优先级看板（按优先级指数排序）" subtitle="卡片内展示：加速度、证据强度、影响面、路径建议">
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
            {priorityBoardData.map((item) => (
              <div key={item.issue} className="rounded-2xl border border-blue-100 bg-blue-50/45 p-3">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-slate-900">{item.issue}</p>
                  <span className="rounded-full border border-blue-200 bg-white px-2 py-1 text-xs text-blue-700">
                    优先级 {item.priorityIndex}
                  </span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-2 text-xs text-slate-500">
                  <span>加速度 {formatDelta(item.acceleration)}</span>
                  <span>证据强度 {item.evidenceStrength}%</span>
                  <span>影响面 {item.impactScore}</span>
                  <span>预计周期 {item.eta}</span>
                </div>
                <p className="mt-2 text-xs text-slate-700">路径建议：{item.path}</p>
              </div>
            ))}
          </div>
        </SectionCard>
      </section>
    </motion.div>
  );
}
