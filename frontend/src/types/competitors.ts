export type CompetitorColumn = {
  key: string;
  label: string;
};

export type CompetitorWorkInsight = {
  work_id: string;
  insight_markdown: string;
  updated_at?: string | null;
  updated_by?: string | null;
};

export type CompetitorListPayload = {
  asset: string;
  label: string;
  total: number;
  columns: CompetitorColumn[];
  rows: Record<string, unknown>[];
};

export type CompetitorOptionsPayload = {
  brands: string[];
  account_types: string[];
};

export type CompetitorMode = "accounts" | "works";

export type CompetitorPageConfig = {
  mode: CompetitorMode;
  title: string;
  eyebrow: string;
  listTitle: string;
  listMeta: string;
  searchPlaceholder: string;
  listEndpoint: string;
  exportEndpoint: string;
};
