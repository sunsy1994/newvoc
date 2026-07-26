export type ReportTemplateId =
  | "F3"
  | "F4"
  | "F5"
  | "F6"
  | "F7"
  | "F8"
  | "L6"
  | "L12"
  | "L13"
  | "L14"
  | "L15";

export type ReportVisualChart = {
  chart_id: string;
  template_id: ReportTemplateId;
  title: string;
  subtitle: string;
  insight: string;
  source_label: string;
  data: Array<Record<string, unknown>>;
  meta: {
    displayed_count?: number;
    total_count?: number;
    unit?: string;
    empty_reason?: string;
  };
};
