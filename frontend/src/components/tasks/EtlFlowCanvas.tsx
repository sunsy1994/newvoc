"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowDownToLine,
  Boxes,
  CheckCircle2,
  Database,
  FileInput,
  GitBranch,
  Layers3,
  RefreshCw,
  Route,
  SearchCheck,
} from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import type { EtlFlowNode, EtlFlowPayload } from "@/types/etlFlow";
import type { ImportTask } from "@/types/tasks";

type NodeLayout = {
  id: string;
  col: number;
  row: number;
  tone: "purple" | "blue" | "teal" | "yellow" | "green";
  icon: React.ReactNode;
};

const nodeLayouts: NodeLayout[] = [
  { id: "upload", col: 1, row: 1, tone: "purple", icon: <FileInput className="h-4 w-4" /> },
  { id: "ods", col: 2, row: 1, tone: "blue", icon: <Layers3 className="h-4 w-4" /> },
  { id: "validate", col: 3, row: 1, tone: "yellow", icon: <SearchCheck className="h-4 w-4" /> },
  { id: "standardize_event", col: 4, row: 1, tone: "teal", icon: <CheckCircle2 className="h-4 w-4" /> },
  { id: "standardize_content_author", col: 4, row: 2, tone: "teal", icon: <Boxes className="h-4 w-4" /> },
  { id: "standardize_comment", col: 4, row: 3, tone: "teal", icon: <GitBranch className="h-4 w-4" /> },
  { id: "ads", col: 5, row: 2, tone: "green", icon: <Route className="h-4 w-4" /> },
  { id: "postgres_load", col: 6, row: 2, tone: "purple", icon: <Database className="h-4 w-4" /> },
];

const edges = [
  ["upload", "ods"],
  ["ods", "validate"],
  ["validate", "standardize_event"],
  ["validate", "standardize_content_author"],
  ["standardize_event", "standardize_content_author"],
  ["standardize_content_author", "standardize_comment"],
  ["standardize_event", "ads"],
  ["standardize_content_author", "ads"],
  ["standardize_comment", "ads"],
  ["ads", "postgres_load"],
];

const toneClass = {
  purple: "bg-[#f0efff] text-[#5347CE]",
  blue: "bg-[#eef6ff] text-[#4896FE]",
  teal: "bg-[#eafafa] text-[#16C8C7]",
  yellow: "bg-[#fff8e5] text-[#c89516]",
  green: "bg-[#ecfbf1] text-[#2aa365]",
};

function buildApiUrl(endpoint: string, params?: URLSearchParams) {
  const query = params?.toString();
  return `${apiBaseUrl}${endpoint}${query ? `?${query}` : ""}`;
}

function tableShortName(table: string) {
  return table.replace("data_asset.", "").replace(".xlsx/csv", "");
}

function FlowNodeCard({ node, layout }: { node: EtlFlowNode; layout: NodeLayout }) {
  const metricEntries = Object.entries(node.metrics ?? {});

  return (
    <article
      className="relative z-10 min-h-52 w-64 rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_16px_34px_rgba(26,32,44,0.08)]"
      style={{ gridColumn: layout.col, gridRow: layout.row }}
    >
      <div className="mb-3 flex items-start gap-3">
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${toneClass[layout.tone]}`}>{layout.icon}</div>
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-wide text-[#8b92a1]">
            Step {String(node.order).padStart(2, "0")} / {node.function_name}
          </p>
          <h2 className="mt-1 text-sm font-semibold text-[#151720]">{node.title}</h2>
        </div>
      </div>
      <p className="line-clamp-2 text-xs leading-5 text-[#7b8190]">{node.desc}</p>

      <div className="mt-4 space-y-3">
        <div>
          <p className="mb-1 text-[11px] font-semibold text-[#8b92a1]">输出表</p>
          <div className="flex flex-wrap gap-1.5">
            {node.output_tables.slice(0, 4).map((table) => (
              <span key={table} className="rounded-lg bg-[#f7f9fc] px-2 py-1 text-[11px] font-medium text-[#596070]">
                {tableShortName(table)}
              </span>
            ))}
          </div>
        </div>

        <div>
          <p className="mb-1 text-[11px] font-semibold text-[#8b92a1]">批次指标</p>
          {metricEntries.length ? (
            <div className="grid grid-cols-2 gap-1.5">
              {metricEntries.slice(0, 4).map(([key, value]) => (
                <span key={key} className="rounded-lg bg-[#f0efff] px-2 py-1 text-[11px] font-semibold text-[#5347CE]">
                  {tableShortName(key)}: {value.toLocaleString("zh-CN")}
                </span>
              ))}
            </div>
          ) : (
            <span className="rounded-lg bg-[#f7f9fc] px-2 py-1 text-[11px] text-[#a3a9b5]">暂无批次指标</span>
          )}
        </div>
      </div>
    </article>
  );
}

function FlowLines() {
  const positions = Object.fromEntries(
    nodeLayouts.map((node) => [node.id, { x: (node.col - 1) * 304 + 128, y: (node.row - 1) * 248 + 104 }]),
  ) as Record<string, { x: number; y: number }>;

  return (
    <svg className="pointer-events-none absolute inset-0 z-0 h-[744px] w-[1776px]" aria-hidden="true">
      <defs>
        <marker id="flow-arrow" markerHeight="8" markerWidth="8" orient="auto" refX="6" refY="3">
          <path d="M0,0 L0,6 L6,3 z" fill="#9aa3b5" />
        </marker>
      </defs>
      {edges.map(([source, target]) => {
        const start = positions[source];
        const end = positions[target];
        const midX = start.x + (end.x - start.x) / 2;
        return (
          <path
            key={`${source}-${target}`}
            d={`M ${start.x + 128} ${start.y} C ${midX} ${start.y}, ${midX} ${end.y}, ${end.x - 128} ${end.y}`}
            fill="none"
            markerEnd="url(#flow-arrow)"
            stroke="#c7cfdd"
            strokeDasharray={source === "standardize_event" || source === "standardize_content_author" ? "5 5" : undefined}
            strokeWidth="1.6"
          />
        );
      })}
    </svg>
  );
}

export function EtlFlowCanvas() {
  const [tasks, setTasks] = useState<ImportTask[]>([]);
  const [selectedBatchId, setSelectedBatchId] = useState("");
  const [nodes, setNodes] = useState<EtlFlowNode[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  const nodeMap = useMemo(() => new Map(nodes.map((node) => [node.id, node])), [nodes]);
  const metricCount = nodes.reduce((count, node) => count + Object.keys(node.metrics ?? {}).length, 0);

  const loadTasks = useCallback(async () => {
    const response = await fetch(buildApiUrl("/tasks"), { cache: "no-store" });
    if (!response.ok) return;
    const nextTasks = (await response.json()) as ImportTask[];
    setTasks(nextTasks);
    if (!selectedBatchId && nextTasks[0]?.batch_id) setSelectedBatchId(nextTasks[0].batch_id);
  }, [selectedBatchId]);

  const loadFlow = useCallback(async () => {
    setMessage("正在加载流程...");
    const params = selectedBatchId ? new URLSearchParams({ batch_id: selectedBatchId }) : undefined;
    try {
      const response = await fetch(buildApiUrl("/etl/flow", params), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const payload = (await response.json()) as EtlFlowPayload;
      setNodes(payload.nodes ?? []);
      setMessage(null);
    } catch {
      setNodes([]);
      setMessage("流程加载失败，请检查后端服务。");
    }
  }, [selectedBatchId]);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  useEffect(() => {
    loadFlow();
  }, [loadFlow]);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">Task Management</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">ETL清理流程</h1>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={selectedBatchId}
            onChange={(event) => setSelectedBatchId(event.target.value)}
            className="h-10 min-w-72 rounded-lg border border-[#e8ecf3] bg-white px-3 text-sm text-[#596070] outline-none focus:border-[#5347CE]"
          >
            <option value="">不选择批次</option>
            {tasks.map((task) => (
              <option key={task.batch_id} value={task.batch_id}>
                {task.batch_id} / {task.status}
              </option>
            ))}
          </select>
          <button
            type="button"
            onClick={() => {
              loadTasks();
              loadFlow();
            }}
            className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#151720] px-4 text-sm font-semibold text-white"
          >
            <RefreshCw className="h-4 w-4" />
            刷新
          </button>
        </div>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <p className="text-xs text-[#8b92a1]">流程节点</p>
          <p className="mt-1 text-2xl font-semibold text-[#151720]">{nodes.length}</p>
        </div>
        <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <p className="text-xs text-[#8b92a1]">关系连线</p>
          <p className="mt-1 text-2xl font-semibold text-[#151720]">{edges.length}</p>
        </div>
        <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <p className="text-xs text-[#8b92a1]">批次指标</p>
          <p className="mt-1 text-2xl font-semibold text-[#151720]">{metricCount}</p>
        </div>
        <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <p className="text-xs text-[#8b92a1]">当前批次</p>
          <p className="mt-1 truncate text-sm font-semibold text-[#151720]">{selectedBatchId || "通用流程"}</p>
        </div>
      </section>

      <section className="rounded-2xl border border-[#e8ecf3] bg-white p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-[#151720]">ODS → DWD → ADS → PostgreSQL</h2>
            <p className="mt-1 text-xs leading-5 text-[#8b92a1]">用节点和连线呈现上传、校验、标准化、指标聚合和落库关系。</p>
          </div>
          {message ? <span className="rounded-lg bg-[#f7f9fc] px-3 py-2 text-xs text-[#8b92a1]">{message}</span> : null}
        </div>

        <div className="overflow-x-auto rounded-2xl bg-[#f5f7fb] p-6">
          <div className="relative grid h-[744px] w-[1776px] grid-cols-[repeat(6,256px)] grid-rows-[repeat(3,208px)] gap-x-12 gap-y-10">
            <FlowLines />
            {nodeLayouts.map((layout) => {
              const node = nodeMap.get(layout.id);
              return node ? <FlowNodeCard key={layout.id} layout={layout} node={node} /> : null;
            })}
          </div>
        </div>
      </section>
    </div>
  );
}
