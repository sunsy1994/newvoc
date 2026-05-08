import {
  dataAccessOverview,
  dataSourceTemplates,
  importJobs,
} from '@/components/data-access/data/dataAccessMock';
import type {
  CreateImportJobPayload,
  DataAccessOverview,
  DataSourceTemplate,
  ImportJob,
} from '@/types/dataAccess';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

function apiUrl(path: string) {
  return `${API_BASE_URL}${path}`;
}

function normalizeTemplate(template: any): DataSourceTemplate {
  return {
    id: template.id,
    sourceKey: template.sourceKey ?? template.source_key,
    sourceName: template.sourceName ?? template.source_name,
    fileName: template.fileName ?? template.file_name,
    formats: template.formats,
    description: template.description,
    requiredFields: template.requiredFields ?? template.required_fields,
    optionalFields: template.optionalFields ?? template.optional_fields,
    targetTable: template.targetTable ?? template.target_table,
    downloadPath: template.downloadPath ?? template.download_path,
  };
}

function normalizeJob(job: any): ImportJob {
  return {
    id: job.id ?? job.job_id,
    sourceName: job.sourceName ?? job.source_name,
    templateName: job.templateName ?? job.template_name,
    fileName: job.fileName ?? job.file_name,
    status: job.status,
    createdAt: job.createdAt ?? job.created_at,
    createdBy: job.createdBy ?? job.operator ?? job.created_by,
    insertedRows: job.insertedRows ?? job.inserted_rows ?? 0,
    rejectedRows: job.rejectedRows ?? job.rejected_rows ?? 0,
    message: job.message ?? '',
  };
}

function normalizeOverview(payload: any): DataAccessOverview {
  return {
    summary: payload.summary,
    sources: (payload.sources ?? []).map((source: any) => ({
      id: source.id,
      name: source.name,
      type: source.type,
      owner: source.owner,
      status: source.status,
      lastSyncAt: source.lastSyncAt ?? source.last_sync_at,
      recordCount: source.recordCount ?? source.record_count,
      templateId: source.templateId ?? source.template_id,
      targetTable: source.targetTable ?? source.target_table,
    })),
    templates: (payload.templates ?? []).map(normalizeTemplate),
    jobs: (payload.jobs ?? []).map(normalizeJob),
    postgres: {
      schemaName: payload.postgres.schemaName ?? payload.postgres.schema_name,
      currentDatabase: payload.postgres.currentDatabase ?? payload.postgres.current_database,
      tables: payload.postgres.tables,
      keyInterfaces: payload.postgres.keyInterfaces ?? payload.postgres.key_interfaces,
    },
  };
}

async function safeJson<T>(input: RequestInfo | URL, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export async function getDataAccessOverview(): Promise<DataAccessOverview> {
  try {
    const payload = await safeJson<any>(apiUrl('/api/data-access/overview'));
    return normalizeOverview(payload);
  } catch {
    return dataAccessOverview;
  }
}

export async function getImportTemplates(): Promise<DataSourceTemplate[]> {
  try {
    const payload = await safeJson<any[]>(apiUrl('/api/data-import/templates'));
    return payload.map(normalizeTemplate);
  } catch {
    return dataSourceTemplates;
  }
}

export async function getImportJobs(): Promise<ImportJob[]> {
  try {
    const payload = await safeJson<any[]>(apiUrl('/api/data-import/jobs'));
    return payload.map(normalizeJob);
  } catch {
    return importJobs;
  }
}

export async function createImportJob(
  payload: CreateImportJobPayload
): Promise<{ jobId: string; accepted: boolean; message: string }> {
  try {
    const formData = new FormData();
    formData.append('source_key', payload.sourceKey);
    formData.append('template_id', payload.templateId);
    formData.append('operator', payload.operator);
    formData.append('file', payload.file);

    return await safeJson(apiUrl('/api/data-import/jobs'), {
      method: 'POST',
      body: formData,
    });
  } catch {
    return {
      jobId: `mock-${payload.sourceKey}-${Date.now()}`,
      accepted: true,
      message: `已按 ${payload.templateId} 接收 ${payload.file.name}，当前为前端 mock 流程。`,
    };
  }
}
