export interface DataLineage {
  tables: string[];
  formula: string;
}

export interface JourneyStageSummaryItem {
  stage: string;
  touchpointCount: number;
  channelCount: number;
  negativeRatio: number;
  intentTop: Array<{ label: string; value: number }>;
  issueTop: Array<{ label: string; value: number }>;
  channelDistribution: Array<{ label: string; value: number }>;
  representativeTouchpoints: Array<{ touchpointId: string; channel: string; text: string; time: string }>;
  dataLineage: DataLineage;
}

export interface JourneyOverviewResponse {
  brandName: string;
  modelName: string;
  stages: JourneyStageSummaryItem[];
  dataLineage: DataLineage;
}

export interface JourneyMatrixCell {
  sourceChannel: string;
  journeyStage: string;
  touchpointCount: number;
  negativeRatio: number;
  issueTop: Array<{ label: string; value: number }>;
  intentTop: Array<{ label: string; value: number }>;
  dataLineage: DataLineage;
}

export interface JourneyTouchpointItem {
  id: string;
  sourceChannel: string;
  sourceSystem: string;
  userDisplayName: string;
  text: string;
  touchpointTime: string;
  brandName: string;
  modelName: string;
  cityName: string;
  storeName: string;
  journeyStage: string;
  stageReason: string;
  intentTag: string;
  issueTag: string;
  sentimentTag: string;
}

export interface JourneyTouchpointListResponse {
  total: number;
  items: JourneyTouchpointItem[];
  dataLineage: DataLineage;
}

export interface JourneyPainpointItem {
  journeyStage: string;
  issueTag: string;
  touchpointCount: number;
  negativeRatio: number;
  sourceChannels: Array<{ label: string; value: number }>;
  sampleTexts: Array<{ touchpointId: string; channel: string; text: string; time: string }>;
  suggestedOwner: string;
  suggestedAction: string;
  dataLineage: DataLineage;
}
