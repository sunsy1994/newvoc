import type { KPIData, VolumeTrendData, PlatformData, KeywordData, ChannelQuadrantData, ContentRankData, KOLInfluenceData, RadarData, KOLTrendData, AIReportData } from '../types';

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
