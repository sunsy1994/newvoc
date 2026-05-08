import {
  type CompetitorAuthorType,
  type CompetitorContentItem,
  interactionRangeOptions,
  pinOptions,
  timeRangeOptions,
} from './data/competitorLibraryData';

export type CompetitorPlatformFilter = '全部平台' | CompetitorContentItem['platform'];
export type CompetitorAuthorFilter = '全部作者类型' | CompetitorAuthorType;
export type CompetitorTimeRange = (typeof timeRangeOptions)[number];
export type CompetitorPinFilter = (typeof pinOptions)[number];
export type CompetitorInteractionRange = (typeof interactionRangeOptions)[number];

export interface CompetitorFilterState {
  keyword: string;
  brand: string;
  model: string;
  platform: CompetitorPlatformFilter;
  authorType: CompetitorAuthorFilter;
  proposition: string;
  timeRange: CompetitorTimeRange;
  pinFilter: CompetitorPinFilter;
  interactionRange: CompetitorInteractionRange;
  onlyHotEvent: boolean;
  onlyHighInteraction: boolean;
}

export const HIGH_INTERACTION_THRESHOLD = 10000;

const numberFormatter = new Intl.NumberFormat('zh-CN');

export function formatNumber(value: number) {
  return numberFormatter.format(value);
}

export function getEngagement(item: CompetitorContentItem) {
  return item.likeCount + item.commentCount + item.favoriteCount + item.shareCount;
}

export function getInteractionThreshold(range: CompetitorInteractionRange) {
  if (range === '2,000+') return 2000;
  if (range === '5,000+') return 5000;
  if (range === '10,000+') return 10000;
  return 0;
}

export function getDateText(value: string) {
  return value.split(' ')[0];
}

export function getDaysDiff(dateText: string) {
  return Math.floor(
    (new Date('2026-03-09').getTime() - new Date(dateText.replace(' ', 'T')).getTime()) / (1000 * 60 * 60 * 24)
  );
}

export function filterCompetitorItems(
  items: CompetitorContentItem[],
  {
    keyword,
    brand,
    model,
    platform,
    authorType,
    proposition,
    timeRange,
    pinFilter,
    interactionRange,
    onlyHotEvent,
    onlyHighInteraction,
  }: CompetitorFilterState
) {
  const rangeDays = { 全部时间: Number.POSITIVE_INFINITY, 近7天: 7, 近30天: 30 }[timeRange];
  const minInteraction = Math.max(
    getInteractionThreshold(interactionRange),
    onlyHighInteraction ? HIGH_INTERACTION_THRESHOLD : 0
  );

  return items.filter((item) => {
    const q = keyword.trim().toLowerCase();
    const matchKeyword =
      q.length === 0 ||
      item.title.toLowerCase().includes(q) ||
      item.author.toLowerCase().includes(q) ||
      item.model.toLowerCase().includes(q) ||
      item.brand.toLowerCase().includes(q);

    const dayDiff = getDaysDiff(item.publishedAt);
    const matchRange = rangeDays === Number.POSITIVE_INFINITY || dayDiff <= rangeDays;
    const matchBrand = brand === '全部品牌' || item.brand === brand;
    const matchModel = model === '全部车型' || item.model === model;
    const matchPlatform = platform === '全部平台' || item.platform === platform;
    const matchAuthorType = authorType === '全部作者类型' || item.authorType === authorType;
    const matchPin = pinFilter === '全部' || item.isPinned;
    const matchInteraction = getEngagement(item) >= minInteraction;
    const matchHotEvent = !onlyHotEvent || Boolean(item.hotEvent);
    const matchProposition = proposition === '全部命题' || item.propositionTags.includes(proposition);

    return (
      matchKeyword &&
      matchRange &&
      matchBrand &&
      matchModel &&
      matchPlatform &&
      matchAuthorType &&
      matchPin &&
      matchInteraction &&
      matchHotEvent &&
      matchProposition
    );
  });
}
