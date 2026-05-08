export type AssetPage =
  | 'dashboard'
  | 'voc'
  | 'customer-journey'
  | 'data-access'
  | 'data-import'
  | 'data-calc'
  | 'event-library'
  | 'content-library'
  | 'comment-library'
  | 'kol-library'
  | 'author-library'
  | 'competitor-library';

export interface AssetNavigationContext {
  eventId?: string;
  contentId?: string;
  authorId?: string;
  commentId?: string;
  kolId?: string;
  keyword?: string;
  includeKOL?: boolean;
}

export type AssetPageChangeHandler = (page: AssetPage, context?: AssetNavigationContext) => void;
