"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Bot, CheckCircle2, Code2, Database, FileJson, KeyRound, RefreshCw, Search, UserRound } from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import type { AiProfileFlowNode, AiProfileFlowPayload } from "@/types/aiProfileFlow";

type NodeLayout = {
  id: string;
  col: number;
  row: number;
  tone: "green" | "orange" | "blue" | "purple" | "teal" | "gray";
  icon: React.ReactNode;
};

const cardWidth = 292;
const colGap = 92;
const rowHeight = 260;
const canvasWidth = 7 * cardWidth + 6 * colGap;
const canvasHeight = 2 * rowHeight + 80;

const nodeLayouts: NodeLayout[] = [
  { id: "select_users", col: 1, row: 1, tone: "green", icon: <UserRound className="h-4 w-4" /> },
  { id: "extract_comments", col: 2, row: 1, tone: "orange", icon: <Search className="h-4 w-4" /> },
  { id: "render_prompt", col: 3, row: 1, tone: "blue", icon: <Code2 className="h-4 w-4" /> },
  { id: "call_llm", col: 4, row: 1, tone: "purple", icon: <Bot className="h-4 w-4" /> },
  { id: "normalize_json", col: 5, row: 1, tone: "teal", icon: <FileJson className="h-4 w-4" /> },
  { id: "write_profile_tables", col: 6, row: 1, tone: "green", icon: <Database className="h-4 w-4" /> },
  { id: "validate_result", col: 7, row: 1, tone: "gray", icon: <CheckCircle2 className="h-4 w-4" /> },
];

const edges = [
  ["select_users", "extract_comments"],
  ["extract_comments", "render_prompt"],
  ["render_prompt", "call_llm"],
  ["call_llm", "normalize_json"],
  ["normalize_json", "write_profile_tables"],
  ["write_profile_tables", "validate_result"],
];

const toneClass = {
  green: "bg-[#ecfbf1] text-[#2aa365]",
  orange: "bg-[#fff3e9] text-[#d98252]",
  blue: "bg-[var(--theme-soft-panel)] text-[var(--voc-chart-5)]",
  purple: "bg-[var(--sys-icon-bg)] text-[var(--sys-icon-fill)]",
  teal: "bg-[var(--theme-status-bg)] text-[var(--theme-status-text)]",
  gray: "bg-[#f1f3f7] text-[#7b8190]",
};

const statusLabel = {
  ready: "就绪",
  waiting: "等待结果",
  blocked: "需配置",
};

const statusClass = {
  ready: "bg-[#ecfbf1] text-[#2aa365]",
  waiting: "bg-[#fff8e5] text-[#c89516]",
  blocked: "bg-[#fff0f0] text-[#d15b5b]",
};

function buildApiUrl(endpoint: string) {
  return `${apiBaseUrl}${endpoint}`;
}

function metricLabel(key: string) {
  const labels: Record<string, string> = {
    comment_user_count: "用户数",
    comment_count: "评论数",
    enabled_prompt_count: "启用提示词",
    ai_config_count: "AI配置",
    raw_profile_count: "原始结果",
    profiled_user_count: "已画像用户",
    label_score_count: "标签得分",
  };
  return labels[key] ?? key;
}

function FlowLines() {
  const positions = Object.fromEntries(
    nodeLayouts.map((node) => [
      node.id,
      {
        x: (node.col - 1) * (cardWidth + colGap),
        y: (node.row - 1) * rowHeight,
      },
    ]),
  ) as Record<string, { x: number; y: number }>;

  return (
    <svg className="pointer-events-none absolute inset-0 z-0" width={canvasWidth} height={canvasHeight} aria-hidden="true">
      <defs>
        <marker id="ai-flow-arrow" markerHeight="8" markerWidth="8" orient="auto" refX="6" refY="3">
          <path d="M0,0 L0,6 L6,3 z" fill="#a7afbf" />
        </marker>
      </defs>
      {edges.map(([source, target]) => {
        const start = positions[source];
        const end = positions[target];
        const startX = start.x + cardWidth;
        const startY = start.y + 122;
        const endX = end.x;
        const endY = end.y + 122;
        const midX = startX + (endX - startX) / 2;
        return (
          <path
            key={`${source}-${target}`}
            d={`M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`}
            fill="none"
            markerEnd="url(#ai-flow-arrow)"
            stroke="#c7cfdd"
            strokeWidth="1.8"
          />
        );
      })}
    </svg>
  );
}

function FlowNodeCard({ node, layout }: { node: AiProfileFlowNode; layout: NodeLayout }) {
  const metricEntries = Object.entries(node.metrics ?? {});

  return (
    <article
      className="relative z-10 flex h-[244px] w-[292px] flex-col rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_16px_34px_rgba(26,32,44,0.08)]"
      style={{ gridColumn: layout.col, gridRow: layout.row }}
    >
      <div className="mb-3 flex items-start gap-3">
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${toneClass[layout.tone]}`}>{layout.icon}</div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2">
            <p className="truncate text-[11px] font-semibold uppercase tracking-wide text-[#8b92a1]">
              Step {String(node.order).padStart(2, "0")}
            </p>
            <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold ${statusClass[node.status]}`}>
              {statusLabel[node.status]}
            </span>
          </div>
          <h2 className="mt-1 line-clamp-1 text-sm font-semibold text-[#151720]" title={node.title}>
            {node.title}
          </h2>
        </div>
      </div>

      <p className="line-clamp-2 min-h-10 text-xs leading-5 text-[#7b8190]" title={node.desc}>
        {node.desc}
      </p>

      <div className="mt-3 grid grid-cols-2 gap-2">
        {metricEntries.map(([key, value]) => (
          <div key={key} className="rounded-xl bg-[#f7f9fc] px-3 py-2">
            <p className="text-[10px] text-[#8b92a1]">{metricLabel(key)}</p>
            <p className="mt-1 text-sm font-semibold text-[#151720]">{value.toLocaleString("zh-CN")}</p>
          </div>
        ))}
      </div>

      <div className="mt-auto flex items-center gap-1.5 text-[11px] text-[#8b92a1]">
        <KeyRound className="h-3.5 w-3.5" />
        <span className="truncate" title={node.function_name}>
          {node.function_name}
        </span>
      </div>
    </article>
  );
}

export function CommentUserAiProfileFlowCanvas() {
  const [payload, setPayload] = useState<AiProfileFlowPayload | null>(null);
  const [message, setMessage] = useState<string | null>("正在加载流程...");

  const nodes = payload?.nodes ?? [];
  const nodeMap = useMemo(() => new Map(nodes.map((node) => [node.id, node])), [nodes]);
  const summary = payload?.summary ?? {};

  const loadFlow = useCallback(async () => {
    setMessage("正在加载流程...");
    try {
      const response = await fetch(buildApiUrl("/profiles/comment-users/ai-flow"), { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setPayload((await response.json()) as AiProfileFlowPayload);
      setMessage(null);
    } catch {
      setPayload(null);
      setMessage("用户画像 AI 打标流程加载失败，请检查后端和 PostgreSQL。");
    }
  }, []);

  useEffect(() => {
    loadFlow();
  }, [loadFlow]);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-xs font-medium text-[#8b92a1]">Task Management</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[#151720]">用户画像AI打标流程</h1>
        </div>
        <button
          type="button"
          onClick={loadFlow}
          className="inline-flex h-10 items-center gap-2 rounded-lg bg-[#151720] px-4 text-sm font-semibold text-white"
        >
          <RefreshCw className="h-4 w-4" />
          刷新
        </button>
      </header>

      <section className="grid gap-3 md:grid-cols-4">
        <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <p className="text-xs text-[#8b92a1]">评论用户</p>
          <p className="mt-1 text-2xl font-semibold text-[#151720]">{(summary.comment_user_count ?? 0).toLocaleString("zh-CN")}</p>
        </div>
        <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <p className="text-xs text-[#8b92a1]">已画像用户</p>
          <p className="mt-1 text-2xl font-semibold text-[#151720]">{(summary.profiled_user_count ?? 0).toLocaleString("zh-CN")}</p>
        </div>
        <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <p className="text-xs text-[#8b92a1]">启用提示词</p>
          <p className="mt-1 text-2xl font-semibold text-[#151720]">{(summary.enabled_prompt_count ?? 0).toLocaleString("zh-CN")}</p>
        </div>
        <div className="rounded-2xl border border-[#e8ecf3] bg-white p-4 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
          <p className="text-xs text-[#8b92a1]">标签得分</p>
          <p className="mt-1 text-2xl font-semibold text-[#151720]">{(summary.label_score_count ?? 0).toLocaleString("zh-CN")}</p>
        </div>
      </section>

      <section className="rounded-2xl border border-[#e8ecf3] bg-[var(--theme-white)] p-5 shadow-[0_10px_28px_rgba(26,32,44,0.04)]">
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-[#151720]">选择用户范围 → 抽取全量评论 → 拼接提示词 → 调用 LLM → JSON 规范化解析 → 写入画像表 → 结果校验</h2>
            <p className="mt-1 text-xs leading-5 text-[#8b92a1]">
              这里展示用户画像 AI 打标的运行链路。参数和提示词在系统管理维护，画像结果进入用户画像维护和销售看板。
            </p>
          </div>
          {message ? <span className="rounded-lg bg-[#f7f9fc] px-3 py-2 text-xs text-[#8b92a1]">{message}</span> : null}
        </div>

        <div className="overflow-x-auto rounded-2xl bg-[var(--theme-page)] p-6">
          <div
            className="relative grid gap-x-24"
            style={{
              width: canvasWidth,
              height: canvasHeight,
              gridTemplateColumns: `repeat(7, ${cardWidth}px)`,
              gridTemplateRows: `repeat(2, ${rowHeight}px)`,
            }}
          >
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
