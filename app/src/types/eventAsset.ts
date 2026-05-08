export type EventStatus = '进行中' | '已结束' | '归档';
export type EventRiskLevel = '高' | '中' | '低';

export interface EventLibraryItem {
  id: string;
  name: string;
  description: string;
  type: string;
  brand: string;
  model: string;
  keywords: string[];
  startDate: string;
  endDate: string;
  status: EventStatus;
  platforms: string[];
  contentCount: number;
  commentCount: number;
  authorCount: number;
  kolCount: number;
  heat: number;
  growth: number;
  riskLevel: EventRiskLevel;
  updatedAt: string;
  topics: string[];
  targetAudience?: string;
  businessOwner?: string;
  storyGoal?: string;
}

export interface EventAssetDetail extends EventLibraryItem {
  totalEngagement: number;
  negativeCommentCount: number;
  negativeRatio: number;
  recentHeat: number;
  previousHeat: number;
}

export interface EventAssetTrendPoint {
  statDate: string;
  contentCount: number;
  commentCount: number;
  engagementCount: number;
  negativeCommentCount: number;
  heat: number;
}

export interface EventAssetListResponse {
  total: number;
  items: EventLibraryItem[];
}

export interface GetEventLibraryParams {
  keyword?: string;
  eventType?: string;
  eventStatus?: string;
  brandName?: string;
  platform?: string;
  dateFrom?: string;
  dateTo?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  page?: number;
  pageSize?: number;
}
