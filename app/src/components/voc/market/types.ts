export interface KPIData {
  title: string;
  value: number | string;
  change: number;
  comparison: string;
  type: 'volume' | 'index' | 'interaction' | 'nps' | 'kol' | 'negative';
  suffix?: string;
}

export interface VolumeTrendData {
  date: string;
  myVolume: number;
  competitorVolume?: number;
  interaction: number;
  milestone?: string;
}

export interface PlatformData {
  platform: string;
  volume: number;
  category: 'vertical' | 'general';
}

export interface KeywordData {
  text: string;
  frequency: number;
  sentiment: number;
  sentimentIntensity: number;
}

export interface ChannelQuadrantData {
  channel: string;
  volumeShare: number;
  interactionRate: number;
  positiveRatio: number;
  category: string;
}

export interface ContentRankData {
  type: string;
  avgInteraction: number;
  positiveRatio: number;
  count: number;
  icon: string;
}

export interface KOLInfluenceData {
  name: string;
  interactionRate: number;
  trustLevel: number;
  fans: number;
  category: string;
}

export interface RadarData {
  dimension: string;
  kolRatio: number;
  ownerRatio: number;
}

export interface KOLTrendData {
  week: string;
  [kolName: string]: number | string;
}

export interface AIReportData {
  eventProgress: string[];
  keyMetrics: string[];
  alerts: string[];
}
