import type { StructuredReport } from "@/types/vocMarket";

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

type ReportAssetDetailBase = {
  report_type: "event_report" | "competitor_report";
  report_run_id: number;
  subject_name: string;
  generated_at: string;
};

export type ReportAssetDetail =
  | (ReportAssetDetailBase & {
      report_type: "event_report";
      view_kind: "structured";
      structured_report: StructuredReport;
    })
  | (ReportAssetDetailBase & {
      report_type: "competitor_report";
      view_kind: "html";
      html: string;
    });
