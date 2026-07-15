export type AssetColumn = {
  key: string;
  label: string;
};

export type AssetListPayload = {
  asset: string;
  label: string;
  total: number;
  columns: AssetColumn[];
  rows: Record<string, unknown>[];
};

export type AssetKey = "events" | "contents" | "comments" | "authors" | "kols" | "comment_users" | "reports";

export type AssetPageConfig = {
  assetKey: AssetKey;
  title: string;
  eyebrow: string;
  listTitle: string;
  listMeta: string;
  searchPlaceholder: string;
};
