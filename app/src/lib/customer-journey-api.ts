import type {
  DataLineage,
  JourneyMatrixCell,
  JourneyOverviewResponse,
  JourneyPainpointItem,
  JourneyTouchpointItem,
  JourneyTouchpointListResponse,
} from '@/types/customerJourney';

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

function lineage(item: any): DataLineage {
  const raw = item?.dataLineage ?? item?.data_lineage ?? {};
  return {
    tables: raw.tables ?? [],
    formula: raw.formula ?? '',
  };
}

function normalizeStage(item: any): JourneyOverviewResponse['stages'][number] {
  return {
    stage: item.stage ?? '',
    touchpointCount: item.touchpointCount ?? item.touchpoint_count ?? 0,
    channelCount: item.channelCount ?? item.channel_count ?? 0,
    negativeRatio: item.negativeRatio ?? item.negative_ratio ?? 0,
    intentTop: item.intentTop ?? item.intent_top ?? [],
    issueTop: item.issueTop ?? item.issue_top ?? [],
    channelDistribution: item.channelDistribution ?? item.channel_distribution ?? [],
    representativeTouchpoints: item.representativeTouchpoints ?? item.representative_touchpoints ?? [],
    dataLineage: lineage(item),
  };
}

function normalizeMatrix(item: any): JourneyMatrixCell {
  return {
    sourceChannel: item.sourceChannel ?? item.source_channel ?? '',
    journeyStage: item.journeyStage ?? item.journey_stage ?? '',
    touchpointCount: item.touchpointCount ?? item.touchpoint_count ?? 0,
    negativeRatio: item.negativeRatio ?? item.negative_ratio ?? 0,
    issueTop: item.issueTop ?? item.issue_top ?? [],
    intentTop: item.intentTop ?? item.intent_top ?? [],
    dataLineage: lineage(item),
  };
}

function normalizeTouchpoint(item: any): JourneyTouchpointItem {
  return {
    id: item.id ?? '',
    sourceChannel: item.sourceChannel ?? item.source_channel ?? '',
    sourceSystem: item.sourceSystem ?? item.source_system ?? '',
    userDisplayName: item.userDisplayName ?? item.user_display_name ?? '',
    text: item.text ?? '',
    touchpointTime: item.touchpointTime ?? item.touchpoint_time ?? '',
    brandName: item.brandName ?? item.brand_name ?? '',
    modelName: item.modelName ?? item.model_name ?? '',
    cityName: item.cityName ?? item.city_name ?? '',
    storeName: item.storeName ?? item.store_name ?? '',
    journeyStage: item.journeyStage ?? item.journey_stage ?? '',
    stageReason: item.stageReason ?? item.stage_reason ?? '',
    intentTag: item.intentTag ?? item.intent_tag ?? '',
    issueTag: item.issueTag ?? item.issue_tag ?? '',
    sentimentTag: item.sentimentTag ?? item.sentiment_tag ?? '',
  };
}

function normalizePainpoint(item: any): JourneyPainpointItem {
  return {
    journeyStage: item.journeyStage ?? item.journey_stage ?? '',
    issueTag: item.issueTag ?? item.issue_tag ?? '',
    touchpointCount: item.touchpointCount ?? item.touchpoint_count ?? 0,
    negativeRatio: item.negativeRatio ?? item.negative_ratio ?? 0,
    sourceChannels: item.sourceChannels ?? item.source_channels ?? [],
    sampleTexts: item.sampleTexts ?? item.sample_texts ?? [],
    suggestedOwner: item.suggestedOwner ?? item.suggested_owner ?? '',
    suggestedAction: item.suggestedAction ?? item.suggested_action ?? '',
    dataLineage: lineage(item),
  };
}

function buildQuery(params: Record<string, string | number | undefined> = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : '';
}

export async function getJourneyOverview(params: { brandName?: string; modelName?: string } = {}): Promise<JourneyOverviewResponse> {
  const payload = await safeJson<any>(
    apiUrl(`/api/journey/overview${buildQuery({ brand_name: params.brandName, model_name: params.modelName })}`),
  );
  return {
    brandName: payload.brandName ?? payload.brand_name ?? '',
    modelName: payload.modelName ?? payload.model_name ?? '',
    stages: (payload.stages ?? []).map(normalizeStage),
    dataLineage: lineage(payload),
  };
}

export async function getJourneyMatrix(params: { brandName?: string; modelName?: string } = {}): Promise<JourneyMatrixCell[]> {
  const payload = await safeJson<any[]>(
    apiUrl(`/api/journey/matrix${buildQuery({ brand_name: params.brandName, model_name: params.modelName })}`),
  );
  return payload.map(normalizeMatrix);
}

export async function getJourneyTouchpoints(params: {
  stage?: string;
  channel?: string;
  brandName?: string;
  modelName?: string;
  page?: number;
  pageSize?: number;
} = {}): Promise<JourneyTouchpointListResponse> {
  const payload = await safeJson<any>(
    apiUrl(`/api/journey/touchpoints${buildQuery({
      stage: params.stage,
      channel: params.channel,
      brand_name: params.brandName,
      model_name: params.modelName,
      page: params.page,
      page_size: params.pageSize,
    })}`),
  );
  return {
    total: payload.total ?? 0,
    items: (payload.items ?? []).map(normalizeTouchpoint),
    dataLineage: lineage(payload),
  };
}

export async function getJourneyPainpoints(params: { brandName?: string; modelName?: string } = {}): Promise<JourneyPainpointItem[]> {
  const payload = await safeJson<any[]>(
    apiUrl(`/api/journey/painpoints${buildQuery({ brand_name: params.brandName, model_name: params.modelName })}`),
  );
  return payload.map(normalizePainpoint);
}
