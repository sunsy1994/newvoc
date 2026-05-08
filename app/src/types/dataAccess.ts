export interface DataSourceTemplate {
  id: string;
  sourceKey: string;
  sourceName: string;
  fileName: string;
  formats: Array<'csv' | 'xlsx' | 'txt'>;
  description: string;
  requiredFields: string[];
  optionalFields: string[];
  targetTable: string;
  downloadPath: string;
}

export interface DataSourceStatus {
  id: string;
  name: string;
  type: 'excel' | 'csv' | 'text' | 'api';
  owner: string;
  status: 'ready' | 'pending' | 'error';
  lastSyncAt: string;
  recordCount: number;
  templateId: string;
  targetTable: string;
}

export interface ImportJob {
  id: string;
  sourceName: string;
  templateName: string;
  fileName: string;
  status: 'queued' | 'running' | 'success' | 'failed';
  createdAt: string;
  createdBy: string;
  insertedRows: number;
  rejectedRows: number;
  message: string;
}

export interface DataAccessOverview {
  summary: Array<{
    id: string;
    label: string;
    value: string;
    hint: string;
    tone: 'blue' | 'emerald' | 'amber' | 'slate';
  }>;
  sources: DataSourceStatus[];
  templates: DataSourceTemplate[];
  jobs: ImportJob[];
  postgres: {
    schemaName: string;
    currentDatabase: string;
    tables: string[];
    keyInterfaces: string[];
  };
}

export interface CreateImportJobPayload {
  sourceKey: string;
  templateId: string;
  operator: string;
  file: File;
}
