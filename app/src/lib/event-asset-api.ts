import { eventLibraryData } from '@/components/assets/data/eventLibraryData';
import type {
  EventAssetDetail,
  EventAssetListResponse,
  EventAssetTrendPoint,
  EventLibraryItem,
  GetEventLibraryParams,
} from '@/types/eventAsset';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

function apiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

async function safeJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function normalizeEventItem(item: any): EventLibraryItem {
  return {
    id: item.id,
    name: item.name,
    description: item.description ?? '',
    type: item.type,
    brand: item.brand ?? '',
    model: item.model ?? '',
    keywords: item.keywords ?? [],
    startDate: item.startDate ?? item.start_date ?? '',
    endDate: item.endDate ?? item.end_date ?? '',
    status: item.status,
    platforms: item.platforms ?? [],
    contentCount: item.contentCount ?? item.content_count ?? 0,
    commentCount: item.commentCount ?? item.comment_count ?? 0,
    authorCount: item.authorCount ?? item.author_count ?? 0,
    kolCount: item.kolCount ?? item.kol_count ?? 0,
    heat: item.heat ?? 0,
    growth: item.growth ?? 0,
    riskLevel: item.riskLevel ?? item.risk_level ?? '低',
    updatedAt: item.updatedAt ?? item.updated_at ?? '',
    topics: item.topics ?? [],
  };
}

function normalizeEventDetail(item: any): EventAssetDetail {
  return {
    ...normalizeEventItem(item),
    totalEngagement: item.totalEngagement ?? item.total_engagement ?? 0,
    negativeCommentCount: item.negativeCommentCount ?? item.negative_comment_count ?? 0,
    negativeRatio: item.negativeRatio ?? item.negative_ratio ?? 0,
    recentHeat: item.recentHeat ?? item.recent_heat ?? 0,
    previousHeat: item.previousHeat ?? item.previous_heat ?? item.prev_heat ?? 0,
  };
}

function normalizeTrendPoint(item: any): EventAssetTrendPoint {
  return {
    statDate: item.statDate ?? item.stat_date ?? '',
    contentCount: item.contentCount ?? item.content_count ?? 0,
    commentCount: item.commentCount ?? item.comment_count ?? 0,
    engagementCount: item.engagementCount ?? item.engagement_count ?? 0,
    negativeCommentCount: item.negativeCommentCount ?? item.negative_comment_count ?? 0,
    heat: item.heat ?? 0,
  };
}

function buildQuery(params: GetEventLibraryParams = {}) {
  const search = new URLSearchParams();
  if (params.keyword) search.set('keyword', params.keyword);
  if (params.eventType && params.eventType !== '全部') search.set('event_type', params.eventType);
  if (params.eventStatus && params.eventStatus !== '全部') search.set('event_status', params.eventStatus);
  if (params.brandName && params.brandName !== '全部品牌') search.set('brand_name', params.brandName);
  if (params.platform && params.platform !== '全部平台') search.set('platform', params.platform);
  if (params.dateFrom) search.set('date_from', params.dateFrom);
  if (params.dateTo) search.set('date_to', params.dateTo);
  if (params.sortBy) search.set('sort_by', params.sortBy);
  if (params.sortOrder) search.set('sort_order', params.sortOrder);
  if (params.page) search.set('page', String(params.page));
  if (params.pageSize) search.set('page_size', String(params.pageSize));
  return search.toString();
}

export async function getEventLibrary(params: GetEventLibraryParams = {}): Promise<EventAssetListResponse> {
  try {
    const query = buildQuery(params);
    const payload = await safeJson<any>(apiUrl(`/api/assets/events${query ? `?${query}` : ''}`));
    return {
      total: payload.total ?? 0,
      items: (payload.items ?? []).map(normalizeEventItem),
    };
  } catch {
    return {
      total: eventLibraryData.length,
      items: eventLibraryData,
    };
  }
}

export async function getEventDetail(eventId: string): Promise<EventAssetDetail> {
  try {
    const payload = await safeJson<any>(apiUrl(`/api/assets/events/${eventId}`));
    return normalizeEventDetail(payload);
  } catch {
    const fallback = eventLibraryData.find((item) => item.id === eventId) ?? eventLibraryData[0];
    return {
      ...fallback,
      totalEngagement: 0,
      negativeCommentCount: 0,
      negativeRatio: 0,
      recentHeat: fallback?.heat ?? 0,
      previousHeat: 0,
    };
  }
}

export async function getEventTrend(eventId: string): Promise<EventAssetTrendPoint[]> {
  try {
    const payload = await safeJson<any[]>(apiUrl(`/api/assets/events/${eventId}/trend`));
    return payload.map(normalizeTrendPoint);
  } catch {
    return [];
  }
}
