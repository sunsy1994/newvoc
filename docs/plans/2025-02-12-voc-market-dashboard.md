# VOC市场部BI图表页面重构 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 重构VOC看事件市场部BI图表页面，添加AI摘要功能，实现11个数据可视化图表，保持与管理工作台的视觉一致性。

**Architecture:**
- 在VocViewPage中添加AIReportButton和AIReportModal
- 创建MarketDashboard组件作为市场部图表容器
- 使用Grid布局实现响应式图表排列
- 复用管理工作台的样式规范和组件设计

**Tech Stack:** React 19, TypeScript, Tailwind CSS, Framer Motion, Recharts, react-wordcloud

---

## Task 1: 安装依赖 react-wordcloud

**Files:**
- Modify: `app/package.json`

**Step 1: 安装依赖**

```bash
cd app && npm install react-wordcloud
```

**Step 2: 验证安装**

Run: `cat app/package.json | grep react-wordcloud`
Expected: `"react-wordcloud": "^1.2.7"` (或类似版本号)

**Step 3: 提交**

```bash
git add app/package.json app/package-lock.json
git commit -m "chore: install react-wordcloud dependency"
```

---

## Task 2: 创建市场部类型定义文件

**Files:**
- Create: `app/src/components/voc/market/types.ts`

**Step 1: 创建types.ts**

```typescript
// 核心指标数据
export interface KPIData {
  title: string;
  value: number | string;
  change: number;
  comparison: string;
  type: 'volume' | 'index' | 'interaction' | 'nps' | 'kol' | 'negative';
  suffix?: string;
}

// 声量趋势数据
export interface VolumeTrendData {
  date: string;
  myVolume: number;
  competitorVolume?: number;
  interaction: number;
  milestone?: string;
}

// 平台声量数据
export interface PlatformData {
  platform: string;
  volume: number;
  category: 'vertical' | 'general';
}

// 关键词数据
export interface KeywordData {
  text: string;
  frequency: number;
  sentiment: number;
  sentimentIntensity: number;
}

// 渠道四象限数据
export interface ChannelQuadrantData {
  channel: string;
  volumeShare: number;
  interactionRate: number;
  positiveRatio: number;
  category: string;
}

// 内容类型排行数据
export interface ContentRankData {
  type: string;
  avgInteraction: number;
  positiveRatio: number;
  count: number;
  icon: string;
}

// KOL影响力数据
export interface KOLInfluenceData {
  name: string;
  interactionRate: number;
  trustLevel: number;
  fans: number;
  category: string;
}

// 雷达图数据
export interface RadarData {
  dimension: string;
  kolRatio: number;
  ownerRatio: number;
}

// KOL立场趋势数据
export interface KOLTrendData {
  week: string;
  [kolName: string]: number | string;
}

// AI摘要数据
export interface AIReportData {
  eventProgress: string[];
  keyMetrics: string[];
  alerts: string[];
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/types.ts
git commit -m "feat(market): add type definitions for market dashboard"
```

---

## Task 3: 创建市场部模拟数据

**Files:**
- Create: `app/src/components/voc/market/data/marketChartData.ts`

**Step 1: 创建marketChartData.ts**

```typescript
import { KPIData, VolumeTrendData, PlatformData, KeywordData, ChannelQuadrantData, ContentRankData, KOLInfluenceData, RadarData, KOLTrendData, AIReportData } from '../types';

export const marketKPIData: KPIData[] = [
  {
    title: '总声量',
    value: 128000,
    change: 34,
    comparison: '较上次上市增长34%',
    type: 'volume',
    suffix: '条'
  },
  {
    title: '破圈指数',
    value: 42,
    change: 8,
    comparison: '非汽车圈用户占比42%',
    type: 'index',
    suffix: '%'
  },
  {
    title: '总互动量',
    value: 85.6,
    change: 45,
    comparison: '互动率667%',
    type: 'interaction',
    suffix: '万'
  },
  {
    title: 'NPS估算',
    value: 68,
    change: -5,
    comparison: '68%推荐，12%劝阻',
    type: 'nps',
    suffix: '%'
  },
  {
    title: 'KOL贡献度',
    value: 56,
    change: 12,
    comparison: 'KOL内容互动占比',
    type: 'kol',
    suffix: '%'
  },
  {
    title: '负面情感占比',
    value: 8.2,
    change: -2.1,
    comparison: '在行业正常范围内',
    type: 'negative',
    suffix: '%'
  }
];

export const volumeTrendData: VolumeTrendData[] = [
  { date: 'D-3', myVolume: 3200, interaction: 18500, milestone: '预热期' },
  { date: 'D-2', myVolume: 5800, interaction: 32400 },
  { date: 'D-1', myVolume: 9200, interaction: 56800 },
  { date: 'D0', myVolume: 18500, interaction: 123000, milestone: '上市日' },
  { date: 'D+1', myVolume: 12400, interaction: 78500 },
  { date: 'D+2', myVolume: 8900, interaction: 54300 },
  { date: 'D+3', myVolume: 6400, interaction: 38600, milestone: '沉淀期' },
  { date: 'D+4', myVolume: 5200, interaction: 31200 },
  { date: 'D+5', myVolume: 4800, interaction: 28500 },
  { date: 'D+6', myVolume: 4200, interaction: 24800 },
  { date: 'D+7', myVolume: 8500, interaction: 52600, milestone: 'KOL日' },
  { date: 'D+8', myVolume: 6800, interaction: 41200 },
  { date: 'D+9', myVolume: 5400, interaction: 32500 },
  { date: 'D+10', myVolume: 4800, interaction: 28900 }
];

export const platformData: PlatformData[] = [
  { platform: '汽车之家', volume: 28160, category: 'vertical' },
  { platform: '懂车帝', volume: 20480, category: 'vertical' },
  { platform: '抖音', volume: 43520, category: 'general' },
  { platform: '微博', volume: 15360, category: 'general' },
  { platform: '小红书', volume: 12800, category: 'general' },
  { platform: '其他', volume: 7680, category: 'general' }
];

export const keywordData: KeywordData[] = [
  { text: '科技感', frequency: 15200, sentiment: 0.85, sentimentIntensity: 0.9 },
  { text: '智能', frequency: 12800, sentiment: 0.78, sentimentIntensity: 0.85 },
  { text: '设计', frequency: 9600, sentiment: 0.82, sentimentIntensity: 0.8 },
  { text: '价格贵', frequency: 7200, sentiment: -0.65, sentimentIntensity: 0.75 },
  { text: '续航', frequency: 5400, sentiment: 0.45, sentimentIntensity: 0.6 },
  { text: '舒适', frequency: 4800, sentiment: 0.72, sentimentIntensity: 0.7 },
  { text: '性价比', frequency: 4200, sentiment: -0.35, sentimentIntensity: 0.5 },
  { text: '卡顿', frequency: 3800, sentiment: -0.78, sentimentIntensity: 0.8 },
  { text: '噪音', frequency: 2400, sentiment: -0.62, sentimentIntensity: 0.65 },
  { text: '服务', frequency: 1800, sentiment: 0.55, sentimentIntensity: 0.55 },
  { text: '配置', frequency: 3200, sentiment: 0.38, sentimentIntensity: 0.45 },
  { text: '操控', frequency: 2800, sentiment: 0.68, sentimentIntensity: 0.6 }
];

export const channelQuadrantData: ChannelQuadrantData[] = [
  { channel: '抖音', volumeShare: 34, interactionRate: 8.7, positiveRatio: 78, category: 'douyin' },
  { channel: '汽车之家', volumeShare: 22, interactionRate: 4.2, positiveRatio: 82, category: 'qichezhijia' },
  { channel: '懂车帝', volumeShare: 16, interactionRate: 3.8, positiveRatio: 79, category: 'dongchidi' },
  { channel: '小红书', volumeShare: 10, interactionRate: 6.5, positiveRatio: 85, category: 'xiaohongshu' },
  { channel: '微博', volumeShare: 12, interactionRate: 2.3, positiveRatio: 58, category: 'weibo' },
  { channel: '其他', volumeShare: 6, interactionRate: 3.1, positiveRatio: 65, category: 'other' }
];

export const contentRankData: ContentRankData[] = [
  { type: '试驾体验', avgInteraction: 12500, positiveRatio: 82, count: 156, icon: '🚗' },
  { type: '车主分享', avgInteraction: 8900, positiveRatio: 88, count: 243, icon: '👤' },
  { type: '配置对比', avgInteraction: 7200, positiveRatio: 65, count: 128, icon: '📊' },
  { type: '新车亮相', avgInteraction: 15800, positiveRatio: 75, count: 86, icon: '✨' },
  { type: '价格解析', avgInteraction: 11200, positiveRatio: 52, count: 94, icon: '💰' }
];

export const kolInfluenceData: KOLInfluenceData[] = [
  { name: 'XX车评', interactionRate: 6.8, trustLevel: 76, fans: 2800000, category: 'pro' },
  { name: '科技博主A', interactionRate: 4.2, trustLevel: 68, fans: 1500000, category: 'tech' },
  { name: '时尚达人B', interactionRate: 3.5, trustLevel: 52, fans: 3200000, category: 'fashion' },
  { name: '真实车主C', interactionRate: 12.5, trustLevel: 88, fans: 85000, category: 'koc' },
  { name: '车评达人D', interactionRate: 2.8, trustLevel: 58, fans: 890000, category: 'pro' },
  { name: '科技博主E', interactionRate: 1.9, trustLevel: 62, fans: 1200000, category: 'tech' },
  { name: '真实车主F', interactionRate: 15.2, trustLevel: 92, fans: 52000, category: 'koc' },
  { name: '网红G', interactionRate: 3.2, trustLevel: 42, fans: 4500000, category: 'fashion' }
];

export const radarData: RadarData[] = [
  { dimension: '外观', kolRatio: 88, ownerRatio: 82 },
  { dimension: '智能', kolRatio: 92, ownerRatio: 65 },
  { dimension: '续航', kolRatio: 78, ownerRatio: 52 },
  { dimension: '空间', kolRatio: 85, ownerRatio: 78 },
  { dimension: '性价比', kolRatio: 72, ownerRatio: 45 },
  { dimension: '服务', kolRatio: 80, ownerRatio: 68 }
];

export const kolTrendData: KOLTrendData[] = [
  { week: 'W-1', 'XX车评': 0.65, '科技博主A': 0.58, '时尚达人B': 0.52 },
  { week: 'W0', 'XX车评': 0.78, '科技博主A': 0.62, '时尚达人B': 0.48 },
  { week: 'W+1', 'XX车评': 0.72, '科技博主A': 0.55, '时尚达人B': 0.35 },
  { week: 'W+2', 'XX车评': 0.68, '科技博主A': 0.42, '时尚达人B': 0.28 }
];

export const aiReportData: AIReportData = {
  eventProgress: [
    'D-3 预热期：声量日均3,200条，符合预期',
    'D0 上市日：声量峰值达18,500条，超预期15%',
    'D+3 沉淀期：声量衰减42%，低于行业平均'
  ],
  keyMetrics: [
    '总声量12.8万条，环比+34%',
    '破圈指数42%，成功突破垂类圈层',
    '互动量85.6万次，互动率667%'
  ],
  alerts: [
    '微博渠道互动率仅2.3%，需关注',
    '"恰饭"质疑词频上升，风险等级：中'
  ]
};
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/data/marketChartData.ts
git commit -m "feat(market): add mock data for market dashboard charts"
```

---

## Task 4: 创建AIReportButton组件

**Files:**
- Create: `app/src/components/voc/market/AIReportButton.tsx`

**Step 1: 创建AIReportButton.tsx**

```typescript
import { motion } from 'framer-motion';
import { Sparkles } from 'lucide-react';

interface AIReportButtonProps {
  onClick: () => void;
}

export default function AIReportButton({ onClick }: AIReportButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      animate={{
        scale: [1, 1.05, 1],
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
      className="relative flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all shadow-lg shadow-blue-500/30"
    >
      {/* Pulsing glow effect */}
      <motion.div
        animate={{
          opacity: [0.5, 1, 0.5],
          scale: [1, 1.2, 1],
        }}
        transition={{
          duration: 2,
          repeat: Infinity,
          ease: 'easeInOut',
        }}
        className="absolute inset-0 bg-blue-400 rounded-xl blur-lg -z-10"
      />

      {/* Animated icon */}
      <div className="relative">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 8, repeat: Infinity, ease: 'linear' }}
          className="absolute inset-0"
        >
          <div className="absolute -top-0.5 left-1/2 w-1 h-1 bg-white rounded-full"></div>
        </motion.div>
        <Sparkles className="w-4 h-4" />
      </div>

      <span className="text-sm font-medium">AI摘要</span>
    </motion.button>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/AIReportButton.tsx
git commit -m "feat(market): add AIReportButton component"
```

---

## Task 5: 创建AIReportModal组件

**Files:**
- Create: `app/src/components/voc/market/AIReportModal.tsx`

**Step 1: 创建AIReportModal.tsx**

```typescript
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar, BarChart3, AlertTriangle } from 'lucide-react';
import { AIReportData } from './types';

interface AIReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: AIReportData;
}

export default function AIReportModal({ isOpen, onClose, data }: AIReportModalProps) {
  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              transition={{ duration: 0.2 }}
              className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-hidden"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-gray-100">
                <div className="flex items-center gap-2">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-400 via-blue-500 to-blue-700 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30">
                    <BarChart3 className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold text-gray-900">传播战果快报</h2>
                    <p className="text-sm text-gray-500">AI智能分析</p>
                  </div>
                </div>
                <button
                  onClick={onClose}
                  className="w-8 h-8 flex items-center justify-center rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              {/* Content */}
              <div className="p-6 overflow-y-auto max-h-[60vh]">
                {/* 事件进展 */}
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                      <Calendar className="w-4 h-4 text-blue-600" />
                    </div>
                    <h3 className="text-base font-semibold text-gray-900">事件进展</h3>
                  </div>
                  <div className="ml-10 space-y-2">
                    {data.eventProgress.map((item, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2"></div>
                        <p className="text-sm text-gray-700">{item}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 关键数据 */}
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 bg-emerald-50 rounded-lg flex items-center justify-center">
                      <BarChart3 className="w-4 h-4 text-emerald-600" />
                    </div>
                    <h3 className="text-base font-semibold text-gray-900">关键数据</h3>
                  </div>
                  <div className="ml-10 space-y-2">
                    {data.keyMetrics.map((item, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-2"></div>
                        <p className="text-sm text-gray-700">{item}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 异常提醒 */}
                <div>
                  <div className="flex items-center gap-2 mb-3">
                    <div className="w-8 h-8 bg-amber-50 rounded-lg flex items-center justify-center">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                    </div>
                    <h3 className="text-base font-semibold text-gray-900">异常提醒</h3>
                  </div>
                  <div className="ml-10 space-y-2">
                    {data.alerts.map((item, index) => (
                      <div key={index} className="flex items-start gap-2">
                        <div className="w-1.5 h-1.5 bg-amber-500 rounded-full mt-2"></div>
                        <p className="text-sm text-gray-700">{item}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Footer */}
              <div className="p-4 border-t border-gray-100 bg-gray-50">
                <button
                  onClick={onClose}
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-xl transition-colors"
                >
                  知道了
                </button>
              </div>
            </motion.div>
          </div>
        </>
      )}
    </AnimatePresence>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/AIReportModal.tsx
git commit -m "feat(market): add AIReportModal component"
```

---

## Task 6: 创建KPICards组件

**Files:**
- Create: `app/src/components/voc/market/KPICards.tsx`

**Step 1: 创建KPICards.tsx**

```typescript
import { motion, useMotionValue, useTransform, animate } from 'framer-motion';
import { useEffect } from 'react';
import { TrendingUp, TrendingDown, Volume2, Target, MessageCircle, Heart, Users, AlertCircle } from 'lucide-react';
import { KPIData } from './types';

interface KPICardsProps {
  data: KPIData[];
}

const icons = {
  volume: Volume2,
  index: Target,
  interaction: MessageCircle,
  nps: Heart,
  kol: Users,
  negative: AlertCircle,
};

function AnimatedNumber({ value, suffix = '' }: { value: number; suffix?: string }) {
  const count = useMotionValue(0);
  const rounded = useTransform(count, (latest) => {
    if (value >= 10000) {
      return (latest / 10000).toFixed(1) + '万';
    }
    return Math.round(latest).toLocaleString();
  });

  useEffect(() => {
    const controls = animate(count, value, {
      duration: 1,
      ease: 'easeOut',
    });
    return controls.stop;
  }, [count, value]);

  return <motion.span>{rounded}</motion.span>;
}

export default function KPICards({ data }: KPICardsProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
      {data.map((item, index) => {
        const Icon = icons[item.type];
        const isPositive = item.change >= 0;

        return (
          <motion.div
            key={item.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            whileHover={{ y: -2, boxShadow: '0 8px 25px rgba(0, 0, 0, 0.1)' }}
            className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 transition-shadow duration-200"
          >
            <div className="flex items-start justify-between mb-3">
              <span className="text-xs font-medium text-gray-600">{item.title}</span>
              <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center">
                <Icon className="w-4 h-4 text-blue-600" />
              </div>
            </div>

            <div className="flex items-baseline gap-2 mb-2">
              <h3 className="text-2xl font-bold text-gray-900">
                <AnimatedNumber value={typeof item.value === 'number' ? item.value : 0} />
                {item.suffix && <span className="text-sm">{item.suffix}</span>}
              </h3>
              <div
                className={`flex items-center gap-0.5 px-1.5 py-0.5 rounded-full text-xs font-medium ${
                  isPositive
                    ? 'bg-emerald-100 text-emerald-700'
                    : 'bg-red-100 text-red-700'
                }`}
              >
                {isPositive ? (
                  <TrendingUp className="w-2.5 h-2.5" />
                ) : (
                  <TrendingDown className="w-2.5 h-2.5" />
                )}
                <span>{isPositive ? '+' : ''}{item.change}%</span>
              </div>
            </div>

            <p className="text-xs text-gray-500">{item.comparison}</p>
          </motion.div>
        );
      })}
    </div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/KPICards.tsx
git commit -m "feat(market): add KPICards component"
```

---

## Task 7: 创建VolumeTrendChart组件

**Files:**
- Create: `app/src/components/voc/market/charts/VolumeTrendChart.tsx`

**Step 1: 创建VolumeTrendChart.tsx**

```typescript
import { motion } from 'framer-motion';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  Cell,
} from 'recharts';
import { VolumeTrendData } from '../types';

interface VolumeTrendChartProps {
  data: VolumeTrendData[];
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-xs text-gray-600 mb-2">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm font-semibold" style={{ color: entry.color }}>
            {entry.name}: {entry.value.toLocaleString()}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function VolumeTrendChart({ data }: VolumeTrendChartProps) {
  const milestoneData = data.filter(d => d.milestone);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-base font-semibold text-gray-900">声量趋势与竞品对比</h3>
      </div>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
            <XAxis
              dataKey="date"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis
              yAxisId="left"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '12px' }}
              iconType="circle"
            />

            {/* 营销节点参考线 */}
            {milestoneData.map((d, i) => (
              <ReferenceLine
                key={i}
                x={d.date}
                stroke="#F59E0B"
                strokeDasharray="3 3"
                label={{
                  value: d.milestone || '',
                  position: 'top',
                  fontSize: 11,
                  fill: '#F59E0B',
                }}
              />
            ))}

            <Bar yAxisId="left" dataKey="myVolume" name="我方声量" fill="#2563EB" radius={[4, 4, 0, 0]} animationDuration={800}>
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.milestone ? '#3B82F6' : '#2563EB'} />
              ))}
            </Bar>
            <Line yAxisId="right" type="monotone" dataKey="interaction" name="互动量" stroke="#1E40AF" strokeWidth={2} dot={{ r: 3 }} animationDuration={800} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/VolumeTrendChart.tsx
git commit -m "feat(market): add VolumeTrendChart component"
```

---

## Task 8: 创建PlatformPieChart组件

**Files:**
- Create: `app/src/components/voc/market/charts/PlatformPieChart.tsx`

**Step 1: 创建PlatformPieChart.tsx**

```typescript
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { PlatformData } from '../types';

interface PlatformPieChartProps {
  data: PlatformData[];
}

const COLORS = {
  '垂直平台': '#1E40AF',
  '泛类平台': '#60A5FA',
  '抖音': '#8B5CF6',
  '微博': '#F97316',
  '小红书': '#EC4899',
  '其他': '#9CA3AF',
  '汽车之家': '#2563EB',
  '懂车帝': '#059669',
};

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">{data.name}</p>
        <p className="text-xs text-gray-600 mt-1">
          {data.value.toLocaleString()}条 ({data.percent.toFixed(1)}%)
        </p>
      </div>
    );
  }
  return null;
};

export default function PlatformPieChart({ data }: PlatformPieChartProps) {
  // 计算破圈指数
  const totalVolume = data.reduce((sum, d) => sum + d.volume, 0);
  const generalVolume = data.filter(d => d.category === 'general').reduce((sum, d) => sum + d.volume, 0);
  const breakoutIndex = ((generalVolume / totalVolume) * 100).toFixed(0);

  // 准备饼图数据 - 先分两大类
  const categoryData = [
    { name: '垂直平台', value: data.filter(d => d.category === 'vertical').reduce((sum, d) => sum + d.volume, 0) },
    { name: '泛类平台', value: data.filter(d => d.category === 'general').reduce((sum, d) => sum + d.volume, 0) },
  ];

  // 泛类平台细分数据
  const generalPlatformData = data.filter(d => d.category === 'general').map(d => ({
    name: d.platform,
    value: d.volume,
  }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-base font-semibold text-gray-900">破圈指数与平台声量占比</h3>
      </div>

      <div className="flex items-center gap-6">
        {/* 饼图 */}
        <div className="flex-1">
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={70}
                paddingAngle={2}
                dataKey="value"
              >
                <Cell fill={COLORS['垂直平台']} />
                <Cell fill={COLORS['泛类平台']} />
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </Pie>
          </ResponsiveContainer>
        </div>

        {/* 中心数字 */}
        <div className="absolute left-[30%] top-[55%] transform -translate-x-1/2 -translate-y-1/2 text-center">
          <div className="text-3xl font-bold text-blue-600">{breakoutIndex}%</div>
          <div className="text-xs text-gray-500">破圈指数</div>
        </div>

        {/* 图例和细分 */}
        <div className="flex-1 space-y-3">
          {/* 大类图例 */}
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#1E40AF]"></div>
            <span className="text-xs text-gray-600">垂直平台</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#60A5FA]"></div>
            <span className="text-xs text-gray-600">泛类平台</span>
          </div>

          {/* 泛类平台细分 */}
          <div className="border-t border-gray-100 pt-3 space-y-2">
            {generalPlatformData.map((item) => (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: COLORS[item.name as keyof typeof COLORS] || '#9CA3AF' }}></div>
                  <span className="text-xs text-gray-600">{item.name}</span>
                </div>
                <span className="text-xs font-medium text-gray-900">{((item.value / totalVolume) * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/PlatformPieChart.tsx
git commit -m "feat(market): add PlatformPieChart component"
```

---

## Task 9: 创建KeywordWordCloud组件

**Files:**
- Create: `app/src/components/voc/market/charts/KeywordWordCloud.tsx`

**Step 1: 创建KeywordWordCloud.tsx**

```typescript
import { motion } from 'framer-motion';
import { WordCloud } from 'react-wordcloud';
import { KeywordData } from '../types';

interface KeywordWordCloudProps {
  data: KeywordData[];
}

const getSentimentColor = (sentiment: number, intensity: number) => {
  const alpha = 0.4 + (intensity * 0.6); // 基于强度调整透明度
  if (sentiment > 0.2) {
    return `rgba(16, 185, 129, ${alpha})`; // 绿色
  } else if (sentiment < -0.2) {
    return `rgba(239, 68, 68, ${alpha})`; // 红色
  }
  return `rgba(156, 163, 175, ${alpha})`; // 灰色
};

export default function KeywordWordCloud({ data }: KeywordWordCloudProps) {
  const words = data.map(d => ({
    text: d.text,
    value: d.frequency * d.sentimentIntensity,
    sentiment: d.sentiment,
  }));

  const callbacks = {
    getWordColor: (word: any) => getSentimentColor(word.sentiment, Math.random()),
    onWordClick: () => {},
  };

  const options = {
    rotations: 0,
    rotationAngles: [0],
    fontSizes: [14, 40],
    scale: 'sqrt' as const,
    spiral: 'archimedean' as const,
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">心智关键词词云</h3>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
            <span className="text-gray-600">正面</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-gray-400"></div>
            <span className="text-gray-600">中性</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full bg-red-500"></div>
            <span className="text-gray-600">负面</span>
          </div>
        </div>
      </div>

      <div className="h-[200px] flex items-center justify-center">
        <div className="w-full h-full">
          <WordCloud words={words} callbacks={callbacks} options={options} />
        </div>
      </div>

      {/* 关键洞察 */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="grid grid-cols-3 gap-3 text-xs">
          <div className="bg-emerald-50 p-2 rounded-lg">
            <div className="text-emerald-700 font-medium">TOP3正面</div>
            <div className="text-gray-600 mt-1">科技感、智能、设计</div>
          </div>
          <div className="bg-red-50 p-2 rounded-lg">
            <div className="text-red-700 font-medium">TOP1负面</div>
            <div className="text-gray-600 mt-1">价格贵、卡顿</div>
          </div>
          <div className="bg-amber-50 p-2 rounded-lg">
            <div className="text-amber-700 font-medium">新晋关键词</div>
            <div className="text-gray-600 mt-1">噪音 (+2.1%)</div>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/KeywordWordCloud.tsx
git commit -m "feat(market): add KeywordWordCloud component"
```

---

## Task 10: 创建ChannelQuadrantChart组件

**Files:**
- Create: `app/src/components/voc/market/charts/ChannelQuadrantChart.tsx`

**Step 1: 创建ChannelQuadrantChart.tsx**

```typescript
import { motion } from 'framer-motion';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { ChannelQuadrantData } from '../types';

interface ChannelQuadrantChartProps {
  data: ChannelQuadrantData[];
}

const channelColors: Record<string, string> = {
  douyin: '#8B5CF6',
  qichezhijia: '#2563EB',
  dongchidi: '#059669',
  xiaohongshu: '#EC4899',
  weibo: '#F97316',
  other: '#9CA3AF',
};

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">{data.channel}</p>
        <p className="text-xs text-gray-600 mt-1">
          声量占比: {data.volumeShare}%
        </p>
        <p className="text-xs text-gray-600">
          互动率: {data.interactionRate}%
        </p>
        <p className="text-xs text-gray-600">
          正面占比: {data.positiveRatio}%
        </p>
      </div>
    );
  }
  return null;
};

export default function ChannelQuadrantChart({ data }: ChannelQuadrantChartProps) {
  const medianVolumeShare = 5;
  const medianInteractionRate = 4;

  // 计算气泡大小（基于正面占比）
  const maxPositiveRatio = Math.max(...data.map(d => d.positiveRatio));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">渠道效果四象限</h3>
      </div>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis
              type="number"
              dataKey="volumeShare"
              name="声量占比"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              label={{ value: '声量占比 (%)', position: 'insideBottom', offset: -5, fontSize: 11, fill: '#9CA3AF' }}
            />
            <YAxis
              type="number"
              dataKey="interactionRate"
              name="互动率"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              label={{ value: '互动率 (%)', angle: -90, position: 'insideLeft', offset: 5, fontSize: 11, fill: '#9CA3AF' }}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />

            {/* 象限分割线 */}
            <ReferenceLine x={medianVolumeShare} stroke="#E5E7EB" strokeDasharray="3 3" />
            <ReferenceLine y={medianInteractionRate} stroke="#E5E7EB" strokeDasharray="3 3" />

            {/* 气泡 */}
            <Scatter data={data.map((d, index) => ({
              ...d,
              z: (d.positiveRatio / maxPositiveRatio) * 300 + 100,
            }))}>
              {data.map((entry, index) => (
                <circle
                  key={`circle-${index}`}
                  cx="0"
                  cy="0"
                  r={Math.sqrt((entry.positiveRatio / maxPositiveRatio) * 400 + 50)}
                  fill={channelColors[entry.category] || '#9CA3AF'}
                  fillOpacity={0.7}
                  stroke={channelColors[entry.category] || '#9CA3AF'}
                  strokeWidth={2}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* 象限说明 */}
      <div className="grid grid-cols-2 gap-4 mt-4 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
          <span className="text-gray-600">核心渠道（高声量+高互动）</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-blue-500"></div>
          <span className="text-gray-600">潜力渠道（低声量+高互动）</span>
        </div>
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/ChannelQuadrantChart.tsx
git commit -m "feat(market): add ChannelQuadrantChart component"
```

---

## Task 11: 创建ContentRankList组件

**Files:**
- Create: `app/src/components/voc/market/charts/ContentRankList.tsx`

**Step 1: 创建ContentRankList.tsx**

```typescript
import { motion } from 'framer-motion';
import { ContentRankData } from '../types';

interface ContentRankListProps {
  data: ContentRankData[];
}

const getRankIcon = (index: number) => {
  if (index === 0) return '🥇';
  if (index === 1) return '🥈';
  if (index === 2) return '🥉';
  return `${index + 1}`;
};

const getSentimentIcon = (ratio: number) => {
  if (ratio > 60) return '😊';
  if (ratio >= 40) return '😐';
  return '☹️';
};

const getSentimentClass = (ratio: number) => {
  if (ratio > 60) return 'bg-emerald-100 text-emerald-700';
  if (ratio >= 40) return 'bg-amber-100 text-amber-700';
  return 'bg-red-100 text-red-700';
};

export default function ContentRankList({ data }: ContentRankListProps) {
  const maxInteraction = Math.max(...data.map(d => d.avgInteraction));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">热门内容类型TOP5</h3>
      </div>

      <div className="space-y-3">
        {data.map((item, index) => (
          <motion.div
            key={item.type}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.05 }}
            className="flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 transition-colors"
          >
            {/* 排名 */}
            <div className="w-8 h-8 flex items-center justify-center">
              <span className="text-lg font-bold">{getRankIcon(index)}</span>
            </div>

            {/* 内容图标和名称 */}
            <div className="flex items-center gap-2 flex-1">
              <span className="text-xl">{item.icon}</span>
              <span className="text-sm font-medium text-gray-900">{item.type}</span>
            </div>

            {/* 互动量条 */}
            <div className="flex-1">
              <div className="relative h-2 bg-gray-100 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.avgInteraction / maxInteraction) * 100}%` }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  className="absolute left-0 top-0 h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-full"
                />
              </div>
            </div>

            {/* 互动量数值 */}
            <div className="w-16 text-right">
              <span className="text-sm font-semibold text-gray-900">
                {item.avgInteraction >= 10000
                  ? `${(item.avgInteraction / 10000).toFixed(1)}万`
                  : item.avgInteraction.toLocaleString()}
              </span>
            </div>

            {/* 情感标识 */}
            <div className={`px-2 py-1 rounded-lg text-xs font-medium ${getSentimentClass(item.positiveRatio)}`}>
              {getSentimentIcon(item.positiveRatio)} {item.positiveRatio}%
            </div>

            {/* 发布数 */}
            <div className="w-12 text-center">
              <span className="text-xs text-gray-500">{item.count}篇</span>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/ContentRankList.tsx
git commit -m "feat(market): add ContentRankList component"
```

---

## Task 12: 创建NegativeWordCloud组件

**Files:**
- Create: `app/src/components/voc/market/charts/NegativeWordCloud.tsx`

**Step 1: 创建NegativeWordCloud.tsx**

```typescript
import { motion } from 'framer-motion';
import { WordCloud } from 'react-wordcloud';
import { KeywordData } from '../types';

interface NegativeWordCloudProps {
  data: KeywordData[];
}

const getNegativeColor = (intensity: number) => {
  const alpha = 0.5 + (intensity * 0.5);
  const redValue = Math.floor(180 - (intensity * 80));
  return `rgba(${redValue}, ${Math.floor(50 - intensity * 20)}, ${Math.floor(50 - intensity * 20)}, ${alpha})`;
};

export default function NegativeWordCloud({ data }: NegativeWordCloudProps) {
  const negativeData = data.filter(d => d.sentiment < 0);

  const words = negativeData.map(d => ({
    text: d.text,
    value: d.frequency * d.sentimentIntensity,
    intensity: d.sentimentIntensity,
  }));

  const callbacks = {
    getWordColor: (word: any) => getNegativeColor(word.intensity),
    onWordClick: () => {},
  };

  const options = {
    rotations: 0,
    rotationAngles: [0],
    fontSizes: [14, 40],
    scale: 'sqrt' as const,
    spiral: 'archimedean' as const,
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">用户反感内容词云</h3>
        <span className="text-xs text-red-500 font-medium">仅展示负面关键词</span>
      </div>

      <div className="h-[200px] flex items-center justify-center">
        <div className="w-full h-full">
          <WordCloud words={words} callbacks={callbacks} options={options} />
        </div>
      </div>

      {/* 负面洞察 */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="bg-red-50 p-3 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-red-600 font-semibold text-sm">TOP3反感词</span>
            <span className="text-xs text-red-500 bg-red-100 px-2 py-0.5 rounded-full">风险等级: 中</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-700">
            <span>1. 价格贵</span>
            <span className="text-gray-400">|</span>
            <span>2. 卡顿</span>
            <span className="text-gray-400">|</span>
            <span>3. 性价比低</span>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            建议：增加价格价值沟通内容，优先解决车机流畅度问题
          </div>
        </div>
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/NegativeWordCloud.tsx
git commit -m "feat(market): add NegativeWordCloud component"
```

---

## Task 13: 创建KOLQuadrantChart组件

**Files:**
- Create: `app/src/components/voc/market/charts/KOLQuadrantChart.tsx`

**Step 1: 创建KOLQuadrantChart.tsx**

```typescript
import { motion } from 'framer-motion';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Label,
} from 'recharts';
import { KOLInfluenceData } from '../types';

interface KOLQuadrantChartProps {
  data: KOLInfluenceData[];
}

const categoryColors: Record<string, string> = {
  pro: '#2563EB',
  tech: '#059669',
  fashion: '#EC4899',
  koc: '#F59E0B',
};

const categoryLabels: Record<string, string> = {
  pro: '专业车评',
  tech: '科技博主',
  fashion: '生活时尚',
  koc: '真实车主KOC',
};

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">{data.name}</p>
        <p className="text-xs text-gray-600 mt-1">
          类型: {categoryLabels[data.category]}
        </p>
        <p className="text-xs text-gray-600">
          互动率: {data.interactionRate}%
        </p>
        <p className="text-xs text-gray-600">
          信任度: {data.trustLevel}%
        </p>
        <p className="text-xs text-gray-600">
          粉丝: {(data.fans / 10000).toFixed(1)}万
        </p>
      </div>
    );
  }
  return null;
};

export default function KOLQuadrantChart({ data }: KOLQuadrantChartProps) {
  const trustThreshold = 60;
  const interactionThreshold = 4;

  // 计算气泡大小（基于粉丝数）
  const maxFans = Math.max(...data.map(d => d.fans));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">KOL影响力矩阵</h3>
      </div>

      <div className="h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 20, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis
              type="number"
              dataKey="interactionRate"
              name="互动率"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            >
              <Label value="互动率 (%)" position="insideBottom" offset={-5} fontSize={11} fill="#9CA3AF" />
            </XAxis>
            <YAxis
              type="number"
              dataKey="trustLevel"
              name="信任度"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            >
              <Label value="信任度 (%)" angle={-90} position="insideLeft" offset={5} fontSize={11} fill="#9CA3AF" />
            </YAxis>
            <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />

            {/* 象限分割线 */}
            <ReferenceLine x={interactionThreshold} stroke="#E5E7EB" strokeDasharray="3 3" />
            <ReferenceLine y={trustThreshold} stroke="#E5E7EB" strokeDasharray="3 3" />

            {/* 气泡 */}
            <Scatter data={data.map(d => ({ ...d, z: d.fans }))}>
              {data.map((entry, index) => (
                <circle
                  key={`circle-${index}`}
                  cx="0"
                  cy="0"
                  r={Math.sqrt((entry.fans / maxFans) * 500 + 50)}
                  fill={categoryColors[entry.category] || '#9CA3AF'}
                  fillOpacity={0.7}
                  stroke={categoryColors[entry.category] || '#9CA3AF'}
                  strokeWidth={2}
                />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* 图例和象限说明 */}
      <div className="grid grid-cols-2 gap-4 mt-4">
        {/* 类型图例 */}
        <div className="flex flex-wrap gap-2 text-xs">
          {Object.entries(categoryLabels).map(([key, label]) => (
            <div key={key} className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: categoryColors[key] }}></div>
              <span className="text-gray-600">{label}</span>
            </div>
          ))}
        </div>

        {/* 象限说明 */}
        <div className="flex items-center gap-3 text-xs text-gray-600">
          <span>右上: 核心合作</span>
          <span>左上: 专家型</span>
        </div>
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/KOLQuadrantChart.tsx
git commit -m "feat(market): add KOLQuadrantChart component"
```

---

## Task 14: 创建KOLRadarChart组件

**Files:**
- Create: `app/src/components/voc/market/charts/KOLRadarChart.tsx`

**Step 1: 创建KOLRadarChart.tsx**

```typescript
import { motion } from 'framer-motion';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { RadarData } from '../types';

interface KOLRadarChartProps {
  data: RadarData[];
}

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: any[] }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-sm font-semibold text-gray-900">{payload[0].payload.dimension}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-xs text-gray-600" style={{ color: entry.color }}>
            {entry.name}: {entry.value}%
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function KOLRadarChart({ data }: KOLRadarChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">KOL vs 真实车主口碑对比</h3>
      </div>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={data} margin={{ top: 20, right: 20, left: 20, bottom: 20 }}>
            <PolarGrid stroke="#E5E7EB" />
            <PolarAngleAxis
              dataKey="dimension"
              tick={{ fill: '#6B7280', fontSize: 11 }}
            />
            <PolarRadiusAxis
              angle={90}
              domain={[0, 100]}
              tick={{ fill: '#9CA3AF', fontSize: 10 }}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{ fontSize: '12px' }}
              iconType="circle"
            />
            <Radar
              name="KOL"
              dataKey="kolRatio"
              stroke="#2563EB"
              fill="#2563EB"
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Radar
              name="车主"
              dataKey="ownerRatio"
              stroke="#10B981"
              fill="#10B981"
              fillOpacity={0.3}
              strokeWidth={2}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* 洞察 */}
      <div className="bg-blue-50 p-3 rounded-lg">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-blue-700 font-semibold text-sm">最大差异</span>
        </div>
        <div className="text-xs text-gray-700">
          <span className="font-medium">智能维度:</span> KOL 92% vs 车主 65% (差距27分)
          <span className="text-gray-500 mx-2">|</span>
          <span className="text-red-600">KOL存在过度渲染</span>
        </div>
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/KOLRadarChart.tsx
git commit -m "feat(market): add KOLRadarChart component"
```

---

## Task 15: 创建KOLTrendChart组件

**Files:**
- Create: `app/src/components/voc/market/charts/KOLTrendChart.tsx`

**Step 1: 创建KOLTrendChart.tsx**

```typescript
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { KOLTrendData } from '../types';

interface KOLTrendChartProps {
  data: KOLTrendData[];
}

const CustomTooltip = ({ active, payload, label }: { active?: boolean; payload?: any[]; label?: string }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-100">
        <p className="text-xs text-gray-600 mb-2">{label}</p>
        {payload.map((entry: any, index: number) => (
          <p key={index} className="text-sm font-semibold" style={{ color: entry.color }}>
            {entry.name}: {entry.value > 0 ? '+' : ''}{(entry.value * 100).toFixed(0)}%
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const kolColors: Record<string, string> = {
  'XX车评': '#2563EB',
  '科技博主A': '#059669',
  '时尚达人B': '#EC4899',
};

export default function KOLTrendChart({ data }: KOLTrendChartProps) {
  const kolNames = Object.keys(data[0]).filter(key => key !== 'week');

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
    >
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-base font-semibold text-gray-900">KOL立场变化趋势</h3>
      </div>

      <div className="h-[240px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 20, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" vertical={false} />
            <XAxis
              dataKey="week"
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
            />
            <YAxis
              domain={[-1, 1]}
              axisLine={false}
              tickLine={false}
              tick={{ fill: '#9CA3AF', fontSize: 11 }}
              tickFormatter={(value) => {
                if (value > 0) return `+${(value * 100).toFixed(0)}%`;
                return `${(value * 100).toFixed(0)}%`;
              }}
            />
            <Tooltip content={<CustomTooltip />} />

            {/* 零线参考 */}
            <ReferenceLine y={0} stroke="#E5E7EB" strokeDasharray="3 3" />

            {kolNames.map((kolName, index) => (
              <Line
                key={kolName}
                type="monotone"
                dataKey={kolName}
                stroke={kolColors[kolName] || '#9CA3AF'}
                strokeWidth={2}
                dot={{ r: 4 }}
                activeDot={{ r: 6 }}
                animationDuration={800}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* 洞察 */}
      <div className="flex gap-3 mt-4 text-xs">
        <div className="flex items-center gap-2 bg-emerald-50 px-3 py-2 rounded-lg">
          <span className="text-emerald-700 font-medium">立场转暖</span>
          <span className="text-gray-600">XX车评 (W-1 → W0: +13%)</span>
        </div>
        <div className="flex items-center gap-2 bg-red-50 px-3 py-2 rounded-lg">
          <span className="text-red-700 font-medium">立场转冷</span>
          <span className="text-gray-600">时尚达人B (W0 → W+1: -13%)</span>
        </div>
      </div>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/charts/KOLTrendChart.tsx
git commit -m "feat(market): add KOLTrendChart component"
```

---

## Task 16: 创建MarketDashboard主容器组件

**Files:**
- Create: `app/src/components/voc/market/MarketDashboard.tsx`

**Step 1: 创建MarketDashboard.tsx**

```typescript
import { motion } from 'framer-motion';
import KPICards from './KPICards';
import VolumeTrendChart from './charts/VolumeTrendChart';
import PlatformPieChart from './charts/PlatformPieChart';
import KeywordWordCloud from './charts/KeywordWordCloud';
import ChannelQuadrantChart from './charts/ChannelQuadrantChart';
import ContentRankList from './charts/ContentRankList';
import NegativeWordCloud from './charts/NegativeWordCloud';
import KOLQuadrantChart from './charts/KOLQuadrantChart';
import KOLRadarChart from './charts/KOLRadarChart';
import KOLTrendChart from './charts/KOLTrendChart';
import {
  marketKPIData,
  volumeTrendData,
  platformData,
  keywordData,
  channelQuadrantData,
  contentRankData,
  kolInfluenceData,
  radarData,
  kolTrendData,
} from './data/marketChartData';

export default function MarketDashboard() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4 }}
      className="space-y-6"
    >
      {/* 核心指标卡片 */}
      <section>
        <KPICards data={marketKPIData} />
      </section>

      {/* 传播效果分析组 */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1 h-5 bg-blue-600 rounded-full"></div>
          <h2 className="text-lg font-semibold text-gray-900">传播效果分析</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <VolumeTrendChart data={volumeTrendData} />
          </div>
          <div>
            <PlatformPieChart data={platformData} />
          </div>
        </div>
        <div className="mt-6">
          <KeywordWordCloud data={keywordData} />
        </div>
      </section>

      {/* 渠道效果分析组 */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1 h-5 bg-purple-600 rounded-full"></div>
          <h2 className="text-lg font-semibold text-gray-900">渠道效果分析</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ChannelQuadrantChart data={channelQuadrantData} />
          </div>
          <div>
            <ContentRankList data={contentRankData} />
          </div>
        </div>
        <div className="mt-6">
          <NegativeWordCloud data={keywordData} />
        </div>
      </section>

      {/* KOL效果评估组 */}
      <section>
        <div className="flex items-center gap-2 mb-4">
          <div className="w-1 h-5 bg-emerald-600 rounded-full"></div>
          <h2 className="text-lg font-semibold text-gray-900">KOL效果评估</h2>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <KOLQuadrantChart data={kolInfluenceData} />
          </div>
          <div>
            <KOLRadarChart data={radarData} />
          </div>
        </div>
        <div className="mt-6">
          <KOLTrendChart data={kolTrendData} />
        </div>
      </section>
    </motion.div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/market/MarketDashboard.tsx
git commit -m "feat(market): add MarketDashboard main container"
```

---

## Task 17: 修改VocViewPage集成新组件

**Files:**
- Modify: `app/src/components/voc/VocViewPage.tsx`

**Step 1: 修改VocViewPage.tsx**

```typescript
import { useState } from 'react';
import { motion } from 'framer-motion';
import { BookOpen } from 'lucide-react';
import ControlKnob from './ControlKnob';
import StoryLineList from './StoryLineList';
import DepartmentCharts from './DepartmentCharts';
import AIReportButton from './market/AIReportButton';
import AIReportModal from './market/AIReportModal';
import MarketDashboard from './market/MarketDashboard';
import { aiReportData } from './market/data/marketChartData';

export default function VocViewPage() {
  const [selectedDepartment, setSelectedDepartment] = useState(0);
  const [isAIReportOpen, setIsAIReportOpen] = useState(false);

  const isMarketDepartment = selectedDepartment === 0; // 假设市场部是第一个部门

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 页面标题 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="bg-white border-b border-gray-200"
      >
        <div className="px-6 py-5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">VOC看事件</h1>
              <p className="text-sm text-gray-500 mt-0.5">基于用户声音的业务洞察</p>
            </div>
          </div>
          {isMarketDepartment && (
            <AIReportButton onClick={() => setIsAIReportOpen(true)} />
          )}
        </div>
      </motion.div>

      {/* AI摘要模态弹窗 */}
      <AIReportModal
        isOpen={isAIReportOpen}
        onClose={() => setIsAIReportOpen(false)}
        data={aiReportData}
      />

      {/* 主内容区 */}
      <main className="p-6 max-w-7xl mx-auto">
        {/* 部门切换旋钮 */}
        <ControlKnob
          selectedIndex={selectedDepartment}
          onSelect={setSelectedDepartment}
        />

        {/* 市场部新仪表板 */}
        {isMarketDepartment ? (
          <>
            {/* 故事线列表 */}
            <StoryLineList selectedIndex={selectedDepartment} />

            {/* 市场部BI图表 */}
            <MarketDashboard />
          </>
        ) : (
          <>
            {/* 其他部门保持原有实现 */}
            <StoryLineList selectedIndex={selectedDepartment} />
            <DepartmentCharts selectedIndex={selectedDepartment} />
          </>
        )}
      </main>
    </div>
  );
}
```

**Step 2: 提交**

```bash
git add app/src/components/voc/VocViewPage.tsx
git commit -m "feat(voc): integrate MarketDashboard into VocViewPage"
```

---

## Task 18: 验证页面功能

**Files:**
- None

**Step 1: 启动开发服务器**

```bash
cd app && npm run dev
```

**Step 2: 验证检查项**

手动验证以下功能：
1. [ ] 页面加载正常，无控制台错误
2. [ ] AI摘要按钮显示在标题右侧，有脉冲动画
3. [ ] 点击AI按钮打开模态弹窗，内容正确显示
4. [ ] 6个核心指标卡片正确显示，数字有动画
5. [ ] 声量趋势图正确渲染，营销节点显示
6. [ ] 破圈指数饼图正确显示
7. [ ] 关键词词云正确渲染
8. [ ] 渠道四象限图正确显示
9. [ ] 内容排行榜正确显示
10. [ ] 负面词云正确显示
11. [ ] KOL影响力矩阵正确显示
12. [ ] KOL vs 车主雷达图正确显示
13. [ ] KOL立场趋势图正确显示
14. [ ] 所有图表样式与管理工作台一致
15. [ ] 响应式布局在不同屏幕尺寸下正常工作

**Step 3: 如果验证通过，标记完成**

如果所有检查项通过，继续下一步。

---

## Task 19: 最终提交

**Files:**
- None

**Step 1: 提交所有未提交的更改**

```bash
git add -A
git commit -m "feat(voc): complete market dashboard BI charts implementation

- Add AI summary button and modal with time-line layout
- Implement 6 KPI cards with animated numbers
- Add 9 data visualization charts:
  - Volume trend with competitor comparison
  - Platform share pie chart with breakout index
  - Keyword word cloud with sentiment colors
  - Channel quadrant analysis
  - Content type ranking list
  - Negative sentiment word cloud
  - KOL influence matrix
  - KOL vs owner radar comparison
  - KOL sentiment trend chart
- Maintain design consistency with management dashboard
- Support responsive layout with grid system"
```

**Step 2: 可选：创建标签**

```bash
git tag -a v1.0.0-market-dashboard -m "Implement VOC market dashboard BI charts"
```

---

## 实现完成

恭喜！VOC市场部BI图表页面重构已完成。

**实现内容总结：**
- 19个任务，涵盖从依赖安装到最终验证的完整流程
- 新增18个组件文件
- 1个主要页面修改
- 完整的模拟数据和类型定义
- 与管理工作台保持一致的样式规范

**下一步建议：**
1. 运行应用进行全面测试
2. 根据实际数据API替换模拟数据
3. 考虑添加单元测试
4. 根据用户反馈进行优化调整
