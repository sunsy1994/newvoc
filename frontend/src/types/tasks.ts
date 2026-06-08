export type TaskStatus = "uploaded" | "running" | "success" | "failed" | string;

export type ImportTask = {
  batch_id: string;
  status: TaskStatus;
  created_at: string;
  updated_at?: string;
  started_at?: string | null;
  finished_at?: string | null;
  input_files?: Record<string, string>;
  summary?: Record<string, number>;
  db_loaded?: Record<string, number>;
  error_message?: string | null;
};

export type TaskTablesPayload = {
  batch_id: string;
  tables: string[];
};

export type TaskTablePayload = {
  batch_id: string;
  table: string;
  total: number;
  columns: string[];
  rows: Record<string, unknown>[];
};
