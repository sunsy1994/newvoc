export interface CalcTaskNode {
  id: string;
  name: string;
  group: 'source' | 'task' | 'output';
  description: string;
  status: 'idle' | 'running' | 'success' | 'failed';
}

export interface CalcTaskEdge {
  source: string;
  target: string;
}

export interface CalcTaskRun {
  runId: string;
  taskId: string;
  status: 'queued' | 'running' | 'success' | 'failed';
  triggerType: 'manual' | 'batch' | 'schedule';
  startedAt: string;
  finishedAt?: string;
  durationMs?: number;
  processedRows: number;
  outputRows: number;
  errorMessage?: string;
  logPath?: string;
}

export interface CalcTask {
  taskId: string;
  taskName: string;
  taskGroup: string;
  taskDesc: string;
  scriptPath: string;
  entryFunc: string;
  inputTables: string[];
  outputTables: string[];
  runMode: 'manual' | 'batch' | 'schedule';
  isEnabled: boolean;
  status: 'idle' | 'running' | 'success' | 'failed';
  lastRunAt?: string;
  latestRun?: CalcTaskRun;
}

export interface CalcGraphResponse {
  nodes: CalcTaskNode[];
  edges: CalcTaskEdge[];
}

export interface CalcTaskDetail extends CalcTask {
  scriptContent: string;
  recentRuns: CalcTaskRun[];
}
