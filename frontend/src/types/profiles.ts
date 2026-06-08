export type ProfileColumn = {
  key: string;
  label: string;
};

export type ProfileListPayload = {
  asset: string;
  label: string;
  total: number;
  columns: ProfileColumn[];
  rows: Record<string, unknown>[];
};

export type ProfileBatchesPayload = {
  batches: string[];
};

export type ProfileMode = "kols" | "comment-users";

export type ProfilePageConfig = {
  mode: ProfileMode;
  title: string;
  eyebrow: string;
  sampleTitle: string;
  sampleMeta: string;
  uploadTitle: string;
  uploadMeta: string;
  listTitle: string;
  searchPlaceholder: string;
  exportEndpoint: string;
  uploadEndpoint: string;
  listEndpoint: string;
  batchesEndpoint: string;
  sampleDays?: boolean;
};
