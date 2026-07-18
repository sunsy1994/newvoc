"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ArrowDownToLine,
  ArrowUpFromLine,
  Bot,
  Calculator,
  ChevronRight,
  CirclePlus,
  Database,
  GitBranch,
  RefreshCw,
  Save,
  Search,
  ShieldCheck,
  Trash2,
  X,
} from "lucide-react";

import { apiBaseUrl } from "@/config/navigation";
import { DataPagination } from "@/components/shared/DataPagination";
import type { LineageDetailPayload, LineageListPayload, LineageNode, LineageSummary } from "@/types/system";

const emptySummary: LineageSummary = {
  node_count: 0,
  metric_count: 0,
  rule_count: 0,
  llm_label_count: 0,
  ai_summary_count: 0,
  incomplete_definition_count: 0,
};

const kindLabels: Record<string, string> = {
  source_field: "原始字段",
  metric: "指标",
  rule: "规则判断",
  llm_label: "LLM 标签",
  ai_summary: "AI 总结",
  dashboard: "业务看板",
  agent_tool: "Agent 工具",
  agent_output: "Agent 产出",
};

const generationLabels: Record<string, string> = {
  raw_fact: "原始事实",
  direct_aggregation: "直接聚合",
  derived_metric: "逻辑计算",
  rule_judgement: "规则判断",
  llm_label: "LLM 打标",
  llm_summary: "LLM 总结",
  consumer_only: "仅消费",
};

const domainLabels: Record<string, string> = { market: "市场", product: "产品", sales: "销售", shared: "通用" };
const relationLabels: Record<string, string> = {
  depends_on: "依赖",
  aggregates_to: "聚合为",
  calculates_to: "计算为",
  rules_to: "判断为",
  labels_to: "标注为",
  consumed_by: "被消费",
  summarized_by: "被总结",
};

const blankNodeForm = {
  lineage_code: "",
  lineage_name: "",
  node_kind: "metric",
  generation_type: "derived_metric",
  business_domain: "shared",
  business_definition: "",
  calculation_logic: "",
  implementation_ref: "",
  prompt_scene: "",
  owner: "",
  status: "draft",
};

function badgeTone(value: string) {
  if (["llm_label", "llm_summary"].includes(value)) return "border-violet-200 bg-violet-50 text-violet-700";
  if (["rule", "rule_judgement"].includes(value)) return "border-amber-200 bg-amber-50 text-amber-700";
  if (["metric", "direct_aggregation", "derived_metric"].includes(value)) return "border-sky-200 bg-sky-50 text-sky-700";
  return "border-[var(--sys-input-border)] bg-[var(--sys-panel-bg)] text-[var(--sys-body)]";
}

function LineageBadge({ value, labels }: { value: string; labels: Record<string, string> }) {
  return <span className={`inline-flex rounded-full border px-2.5 py-1 text-[11px] font-semibold ${badgeTone(value)}`}>{labels[value] ?? value}</span>;
}

function RelationCard({ name, code, relation }: { name: string; code: string; relation: string }) {
  return (
    <div className="rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-3">
      <p className="truncate text-sm font-semibold text-[var(--sys-title)]">{name}</p>
      <p className="mt-1 truncate font-mono text-[10px] text-[var(--sys-muted)]">{code}</p>
      <p className="mt-2 text-[11px] font-medium text-[#5347CE]">{relationLabels[relation] ?? relation}</p>
    </div>
  );
}

export function DataLineagePage() {
  const [payload, setPayload] = useState<LineageListPayload>({ summary: emptySummary, nodes: [] });
  const [detail, setDetail] = useState<LineageDetailPayload | null>(null);
  const [query, setQuery] = useState("");
  const [kind, setKind] = useState("");
  const [domain, setDomain] = useState("");
  const [generation, setGeneration] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);
  const [offset, setOffset] = useState(0);
  const [pageSize, setPageSize] = useState(10);
  const [createOpen, setCreateOpen] = useState(false);
  const [createForm, setCreateForm] = useState(blankNodeForm);
  const [form, setForm] = useState({ ...blankNodeForm, status: "active" });
  const [edgeForm, setEdgeForm] = useState({ direction: "upstream", other_code: "", relation_type: "depends_on", relation_description: "" });

  const loadNodes = useCallback(async () => {
    setLoading(true);
    setError("");
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (kind) params.set("node_kind", kind);
    if (domain) params.set("business_domain", domain);
    if (generation) params.set("generation_type", generation);
    try {
      const response = await fetch(`${apiBaseUrl}/system/data-lineage?${params}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      setPayload((await response.json()) as LineageListPayload);
    } catch {
      setError("数据血缘目录加载失败，请确认后端和 PostgreSQL 已启动。");
    } finally {
      setLoading(false);
    }
  }, [domain, generation, kind, query]);

  useEffect(() => {
    const timer = window.setTimeout(loadNodes, 220);
    return () => window.clearTimeout(timer);
  }, [loadNodes]);

  useEffect(() => {
    setOffset(0);
  }, [domain, generation, kind, query]);

  useEffect(() => {
    if (offset < payload.nodes.length || offset === 0) return;
    setOffset(Math.max(0, (Math.ceil(payload.nodes.length / pageSize) - 1) * pageSize));
  }, [offset, pageSize, payload.nodes.length]);

  const openDetail = useCallback(async (lineageCode: string) => {
    setError("");
    try {
      const response = await fetch(`${apiBaseUrl}/system/data-lineage/${encodeURIComponent(lineageCode)}`, { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const next = (await response.json()) as LineageDetailPayload;
      setDetail(next);
      setForm({
        lineage_code: next.node.lineage_code,
        lineage_name: next.node.lineage_name,
        node_kind: next.node.node_kind,
        generation_type: next.node.generation_type,
        business_domain: next.node.business_domain,
        business_definition: next.node.business_definition ?? "",
        calculation_logic: next.node.calculation_logic ?? "",
        implementation_ref: next.node.implementation_ref ?? "",
        prompt_scene: next.node.prompt_scene ?? "",
        owner: next.node.owner ?? "",
        status: next.node.status ?? "active",
      });
      setEdgeForm({ direction: "upstream", other_code: "", relation_type: "depends_on", relation_description: "" });
    } catch {
      setError("节点详情加载失败。");
    }
  }, []);

  async function saveNode() {
    if (!detail) return;
    setSaving(true);
    try {
      const body = detail.node.is_system
        ? { business_definition: form.business_definition, owner: form.owner, status: form.status }
        : Object.fromEntries(Object.entries(form).filter(([key]) => key !== "lineage_code"));
      const response = await fetch(`${apiBaseUrl}/system/data-lineage/nodes/${encodeURIComponent(detail.node.lineage_code)}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) throw new Error((await response.json()).detail ?? `HTTP ${response.status}`);
      await Promise.all([openDetail(detail.node.lineage_code), loadNodes()]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "节点保存失败。");
    } finally {
      setSaving(false);
    }
  }

  async function createNode() {
    setSaving(true);
    setError("");
    try {
      const response = await fetch(`${apiBaseUrl}/system/data-lineage/nodes`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(createForm),
      });
      if (!response.ok) throw new Error((await response.json()).detail ?? `HTTP ${response.status}`);
      const created = (await response.json()) as LineageNode;
      setCreateOpen(false);
      setCreateForm(blankNodeForm);
      await loadNodes();
      await openDetail(created.lineage_code);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "人工节点创建失败。");
    } finally {
      setSaving(false);
    }
  }

  async function addEdge() {
    if (!detail || !edgeForm.other_code) return;
    setSaving(true);
    const current = detail.node.lineage_code;
    const body = {
      upstream_code: edgeForm.direction === "upstream" ? edgeForm.other_code : current,
      downstream_code: edgeForm.direction === "upstream" ? current : edgeForm.other_code,
      relation_type: edgeForm.relation_type,
      relation_description: edgeForm.relation_description,
    };
    try {
      const response = await fetch(`${apiBaseUrl}/system/data-lineage/edges`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) throw new Error((await response.json()).detail ?? `HTTP ${response.status}`);
      await Promise.all([openDetail(current), loadNodes()]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "关系保存失败。");
    } finally {
      setSaving(false);
    }
  }

  async function removeEdge(edgeId: number) {
    if (!detail) return;
    const response = await fetch(`${apiBaseUrl}/system/data-lineage/edges/${edgeId}`, { method: "DELETE" });
    if (response.ok) await openDetail(detail.node.lineage_code);
    else setError((await response.json()).detail ?? "系统关系不可删除。");
  }

  const summaryCards = useMemo(
    () => [
      { label: "业务输出", value: payload.summary.node_count, icon: Database },
      { label: "计算指标", value: payload.summary.metric_count, icon: Calculator },
      { label: "规则判断", value: payload.summary.rule_count, icon: GitBranch },
      { label: "LLM 参与", value: payload.summary.llm_label_count + payload.summary.ai_summary_count, icon: Bot },
      { label: "待补定义", value: payload.summary.incomplete_definition_count, icon: ShieldCheck },
    ],
    [payload.summary],
  );
  const visibleNodes = useMemo(() => payload.nodes.slice(offset, offset + pageSize), [offset, pageSize, payload.nodes]);

  return (
    <div className="space-y-5">
      <header className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-[11px] font-medium uppercase tracking-[0.08em] text-[var(--sys-subtle)]">Data Governance / Lineage</p>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight text-[var(--sys-title)]">数据血缘维护</h1>
          <p className="mt-2 max-w-3xl text-sm text-[var(--sys-body)]">追踪业务指标从哪里来、如何计算、是否经过 LLM，以及最终被哪个看板、工具或 Agent 消费。</p>
        </div>
        <div className="flex gap-2"><button type="button" onClick={() => setCreateOpen(true)} className="inline-flex h-10 items-center gap-2 rounded-xl bg-[#5347CE] px-4 text-sm font-semibold text-white active:translate-y-px"><CirclePlus className="h-4 w-4" />新增人工节点</button><button type="button" onClick={loadNodes} className="inline-flex h-10 items-center gap-2 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-4 text-sm font-semibold text-[var(--sys-body)] shadow-[var(--sys-card-shadow)] active:translate-y-px"><RefreshCw className="h-4 w-4" />刷新目录</button></div>
      </header>

      <section className="grid grid-cols-2 gap-3 lg:grid-cols-5">
        {summaryCards.map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-2xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-4 shadow-[var(--sys-card-shadow)]">
            <div className="flex items-center justify-between text-[var(--sys-muted)]"><span className="text-xs font-medium">{label}</span><Icon className="h-4 w-4" /></div>
            <p className="mt-3 text-2xl font-semibold tracking-tight text-[var(--sys-title)]">{value}</p>
          </div>
        ))}
      </section>

      <section className="overflow-hidden rounded-[20px] border border-[var(--sys-input-border)] bg-[var(--sys-card)] shadow-[var(--sys-card-shadow)]">
        <div className="flex flex-wrap gap-3 border-b border-[var(--sys-input-border)] p-4">
          <label className="flex min-w-[240px] flex-1 items-center gap-2 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-panel-bg)] px-3">
            <Search className="h-4 w-4 text-[var(--sys-muted)]" />
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索名称或血缘编码" className="h-10 min-w-0 flex-1 bg-transparent text-sm text-[var(--sys-title)] outline-none" />
          </label>
          <select value={kind} onChange={(event) => setKind(event.target.value)} className="h-10 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm text-[var(--sys-body)]">
            <option value="">全部节点类型</option>{Object.entries(kindLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
          <select value={generation} onChange={(event) => setGeneration(event.target.value)} className="h-10 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm text-[var(--sys-body)]">
            <option value="">全部生成方式</option>{Object.entries(generationLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
          <select value={domain} onChange={(event) => setDomain(event.target.value)} className="h-10 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm text-[var(--sys-body)]">
            <option value="">全部业务域</option>{Object.entries(domainLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </div>

        {error ? <div className="border-b border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div> : null}
        <div className="overflow-x-auto">
          <table className="w-full min-w-[980px] text-left text-sm">
            <thead className="bg-[var(--sys-panel-bg)] text-[11px] font-semibold uppercase tracking-[0.04em] text-[var(--sys-muted)]">
              <tr><th className="px-4 py-3">业务输出</th><th className="px-4 py-3">节点类型</th><th className="px-4 py-3">生成方式</th><th className="px-4 py-3">业务域</th><th className="px-4 py-3">上下游</th><th className="px-4 py-3">负责人</th><th className="px-4 py-3">状态</th><th className="w-12" /></tr>
            </thead>
            <tbody className="divide-y divide-[var(--sys-input-border)]">
              {visibleNodes.map((node) => (
                <tr key={node.lineage_code} onClick={() => openDetail(node.lineage_code)} className="cursor-pointer bg-[var(--sys-card)] transition-colors hover:bg-[var(--sys-panel-bg)]">
                  <td className="px-4 py-3"><p className="font-semibold text-[var(--sys-title)]">{node.lineage_name}</p><p className="mt-1 font-mono text-[10px] text-[var(--sys-muted)]">{node.lineage_code}</p></td>
                  <td className="px-4 py-3"><LineageBadge value={node.node_kind} labels={kindLabels} /></td>
                  <td className="px-4 py-3"><LineageBadge value={node.generation_type} labels={generationLabels} /></td>
                  <td className="px-4 py-3 text-[var(--sys-body)]">{domainLabels[node.business_domain] ?? node.business_domain}</td>
                  <td className="px-4 py-3 text-xs text-[var(--sys-body)]"><span className="mr-3">↑ {node.upstream_count}</span><span>↓ {node.downstream_count}</span></td>
                  <td className="px-4 py-3 text-[var(--sys-body)]">{node.owner || "待维护"}</td>
                  <td className="px-4 py-3"><span className={`inline-flex items-center gap-1.5 text-xs ${node.status === "active" ? "text-emerald-700" : "text-[var(--sys-muted)]"}`}><span className="h-1.5 w-1.5 rounded-full bg-current" />{node.status}</span></td>
                  <td className="pr-4 text-right"><ChevronRight className="inline h-4 w-4 text-[var(--sys-muted)]" /></td>
                </tr>
              ))}
              {!payload.nodes.length ? <tr><td colSpan={8} className="px-4 py-12 text-center text-sm text-[var(--sys-muted)]">{loading ? "正在加载血缘目录..." : "没有匹配的血缘节点"}</td></tr> : null}
            </tbody>
          </table>
        </div>
        <div className="px-4 pb-4">
          <DataPagination total={payload.nodes.length} offset={offset} pageSize={pageSize} onOffsetChange={setOffset} onPageSizeChange={setPageSize} />
        </div>
      </section>

      {createOpen ? (
        <div className="data-lineage-overlay fixed inset-0 z-50 grid place-items-center p-4" onMouseDown={(event) => event.target === event.currentTarget && setCreateOpen(false)}>
          <section className="data-lineage-modal-surface w-full max-w-2xl rounded-[20px] border border-[var(--sys-input-border)] p-5 shadow-[0_24px_80px_rgba(28,36,34,0.24)]">
            <div className="flex items-start justify-between"><div><h2 className="text-lg font-semibold text-[var(--sys-title)]">新增人工节点</h2><p className="mt-1 text-xs text-[var(--sys-muted)]">用于登记尚未代码绑定、但需要进入治理范围的业务口径。</p></div><button type="button" aria-label="关闭" onClick={() => setCreateOpen(false)} className="p-2 text-[var(--sys-muted)]"><X className="h-5 w-5" /></button></div>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <label className="text-xs text-[var(--sys-muted)]">血缘编码<input value={createForm.lineage_code} onChange={(event) => setCreateForm({ ...createForm, lineage_code: event.target.value })} placeholder="metric.custom_name" className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 font-mono text-sm outline-none" /></label>
              <label className="text-xs text-[var(--sys-muted)]">业务名称<input value={createForm.lineage_name} onChange={(event) => setCreateForm({ ...createForm, lineage_name: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm outline-none" /></label>
              <label className="text-xs text-[var(--sys-muted)]">节点类型<select value={createForm.node_kind} onChange={(event) => setCreateForm({ ...createForm, node_kind: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm">{Object.entries(kindLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
              <label className="text-xs text-[var(--sys-muted)]">生成方式<select value={createForm.generation_type} onChange={(event) => setCreateForm({ ...createForm, generation_type: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm">{Object.entries(generationLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
              <label className="text-xs text-[var(--sys-muted)]">业务域<select value={createForm.business_domain} onChange={(event) => setCreateForm({ ...createForm, business_domain: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm">{Object.entries(domainLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
              <label className="text-xs text-[var(--sys-muted)]">负责人<input value={createForm.owner} onChange={(event) => setCreateForm({ ...createForm, owner: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm outline-none" /></label>
              <label className="text-xs text-[var(--sys-muted)] sm:col-span-2">业务定义<textarea value={createForm.business_definition} onChange={(event) => setCreateForm({ ...createForm, business_definition: event.target.value })} rows={2} className="mt-1.5 w-full rounded-xl border border-[var(--sys-input-border)] p-3 text-sm outline-none" /></label>
              <label className="text-xs text-[var(--sys-muted)] sm:col-span-2">计算 / 判断口径<textarea value={createForm.calculation_logic} onChange={(event) => setCreateForm({ ...createForm, calculation_logic: event.target.value })} rows={2} className="mt-1.5 w-full rounded-xl border border-[var(--sys-input-border)] p-3 text-sm outline-none" /></label>
            </div>
            <div className="mt-5 flex justify-end gap-2"><button type="button" onClick={() => setCreateOpen(false)} className="h-10 rounded-xl border border-[var(--sys-input-border)] px-4 text-sm text-[var(--sys-body)]">取消</button><button type="button" disabled={saving || !createForm.lineage_code.trim() || !createForm.lineage_name.trim()} onClick={createNode} className="h-10 rounded-xl bg-[#5347CE] px-4 text-sm font-semibold text-white disabled:opacity-40">创建节点</button></div>
          </section>
        </div>
      ) : null}

      {detail ? (
        <div className="data-lineage-overlay fixed inset-0 z-50 flex justify-end" onMouseDown={(event) => event.target === event.currentTarget && setDetail(null)}>
          <aside className="data-lineage-drawer-surface h-full w-full max-w-[760px] overflow-y-auto border-l border-[var(--sys-input-border)] p-5 shadow-[-24px_0_60px_rgba(28,36,34,0.2)]">
            <div className="flex items-start justify-between gap-4">
              <div><div className="flex items-center gap-2"><LineageBadge value={detail.node.generation_type} labels={generationLabels} />{detail.node.is_system ? <span className="inline-flex items-center gap-1 text-[11px] text-emerald-700"><ShieldCheck className="h-3.5 w-3.5" />代码绑定</span> : null}</div><h2 className="mt-3 text-xl font-semibold text-[var(--sys-title)]">{detail.node.lineage_name}</h2><p className="mt-1 font-mono text-xs text-[var(--sys-muted)]">{detail.node.lineage_code}</p></div>
              <button type="button" aria-label="关闭" onClick={() => setDetail(null)} className="rounded-lg p-2 text-[var(--sys-muted)] hover:bg-[var(--sys-panel-bg)]"><X className="h-5 w-5" /></button>
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-[1fr_180px_1fr]">
              <div><p className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-[var(--sys-muted)]"><ArrowDownToLine className="h-3.5 w-3.5" />上游输入</p><div className="space-y-2">{detail.upstream.map((item) => <RelationCard key={item.edge_id} name={item.lineage_name} code={item.upstream_code} relation={item.relation_type} />)}{!detail.upstream.length ? <p className="rounded-xl border border-dashed border-[var(--sys-input-border)] p-4 text-center text-xs text-[var(--sys-muted)]">源头节点</p> : null}</div></div>
              <div className="self-start rounded-2xl border border-[#5347CE]/25 bg-[#5347CE]/[0.06] p-4 text-center"><GitBranch className="mx-auto h-5 w-5 text-[#5347CE]" /><p className="mt-2 text-sm font-semibold text-[var(--sys-title)]">{detail.node.lineage_name}</p><p className="mt-2 text-[11px] text-[var(--sys-muted)]">{kindLabels[detail.node.node_kind]}</p></div>
              <div><p className="mb-2 flex items-center gap-1.5 text-xs font-semibold text-[var(--sys-muted)]"><ArrowUpFromLine className="h-3.5 w-3.5" />下游消费</p><div className="space-y-2">{detail.downstream.map((item) => <RelationCard key={item.edge_id} name={item.lineage_name} code={item.downstream_code} relation={item.relation_type} />)}{!detail.downstream.length ? <p className="rounded-xl border border-dashed border-[var(--sys-input-border)] p-4 text-center text-xs text-[var(--sys-muted)]">暂无下游</p> : null}</div></div>
            </div>

            <section className="mt-6 rounded-2xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-4">
              <h3 className="text-sm font-semibold text-[var(--sys-title)]">业务定义</h3>
              {!detail.node.is_system ? <div className="mt-3 grid gap-3 sm:grid-cols-2"><label className="text-xs text-[var(--sys-muted)]">业务名称<input value={form.lineage_name} onChange={(event) => setForm({ ...form, lineage_name: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm outline-none" /></label><label className="text-xs text-[var(--sys-muted)]">业务域<select value={form.business_domain} onChange={(event) => setForm({ ...form, business_domain: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm">{Object.entries(domainLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label className="text-xs text-[var(--sys-muted)]">节点类型<select value={form.node_kind} onChange={(event) => setForm({ ...form, node_kind: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm">{Object.entries(kindLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label><label className="text-xs text-[var(--sys-muted)]">生成方式<select value={form.generation_type} onChange={(event) => setForm({ ...form, generation_type: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] px-3 text-sm">{Object.entries(generationLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label></div> : null}
              <textarea value={form.business_definition} onChange={(event) => setForm({ ...form, business_definition: event.target.value })} rows={3} className="mt-3 w-full rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-panel-bg)] p-3 text-sm text-[var(--sys-title)] outline-none focus:border-[#5347CE]" />
              {!detail.node.is_system ? <label className="mt-3 block text-xs text-[var(--sys-muted)]">计算 / 判断口径<textarea value={form.calculation_logic} onChange={(event) => setForm({ ...form, calculation_logic: event.target.value })} rows={2} className="mt-1.5 w-full rounded-xl border border-[var(--sys-input-border)] p-3 text-sm text-[var(--sys-title)] outline-none" /></label> : null}
              <div className="mt-3 grid gap-3 sm:grid-cols-2"><label className="text-xs text-[var(--sys-muted)]">负责人<input value={form.owner} onChange={(event) => setForm({ ...form, owner: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm text-[var(--sys-title)] outline-none" /></label><label className="text-xs text-[var(--sys-muted)]">状态<select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value })} className="mt-1.5 h-10 w-full rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm text-[var(--sys-title)]"><option value="draft">draft</option><option value="active">active</option><option value="deprecated">deprecated</option></select></label></div>
              <div className="mt-4 grid gap-3 border-t border-[var(--sys-input-border)] pt-4 sm:grid-cols-2"><div><p className="text-[11px] font-semibold text-[var(--sys-muted)]">计算 / 判断口径</p><p className="mt-1.5 text-xs leading-5 text-[var(--sys-body)]">{detail.node.calculation_logic || "未记录"}</p></div><div><p className="text-[11px] font-semibold text-[var(--sys-muted)]">代码位置 / Prompt 场景</p><p className="mt-1.5 break-all font-mono text-[10px] leading-5 text-[var(--sys-body)]">{detail.node.implementation_ref || "-"}<br />{detail.node.prompt_scene || "-"}</p></div></div>
              <button type="button" disabled={saving} onClick={saveNode} className="mt-4 inline-flex h-10 items-center gap-2 rounded-xl bg-[#5347CE] px-4 text-sm font-semibold text-white disabled:opacity-50 active:translate-y-px"><Save className="h-4 w-4" />保存业务信息</button>
            </section>

            <section className="mt-4 rounded-2xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] p-4">
              <h3 className="flex items-center gap-2 text-sm font-semibold text-[var(--sys-title)]"><CirclePlus className="h-4 w-4" />补充人工血缘关系</h3>
              <div className="mt-3 grid gap-2 sm:grid-cols-2"><select value={edgeForm.direction} onChange={(event) => setEdgeForm({ ...edgeForm, direction: event.target.value })} className="h-10 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm"><option value="upstream">选择上游输入</option><option value="downstream">选择下游消费</option></select><select value={edgeForm.other_code} onChange={(event) => setEdgeForm({ ...edgeForm, other_code: event.target.value })} className="h-10 min-w-0 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm"><option value="">请选择节点</option>{detail.available_nodes.map((node) => <option key={node.lineage_code} value={node.lineage_code}>{node.lineage_name}</option>)}</select><select value={edgeForm.relation_type} onChange={(event) => setEdgeForm({ ...edgeForm, relation_type: event.target.value })} className="h-10 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm">{Object.entries(relationLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><input value={edgeForm.relation_description} onChange={(event) => setEdgeForm({ ...edgeForm, relation_description: event.target.value })} placeholder="关系说明（选填）" className="h-10 rounded-xl border border-[var(--sys-input-border)] bg-[var(--sys-card)] px-3 text-sm outline-none" /></div>
              <button type="button" disabled={saving || !edgeForm.other_code} onClick={addEdge} className="mt-3 inline-flex h-9 items-center gap-2 rounded-xl border border-[#5347CE]/30 px-3 text-xs font-semibold text-[#5347CE] disabled:opacity-40"><CirclePlus className="h-3.5 w-3.5" />添加关系</button>
              {detail.upstream.concat(detail.downstream).some((item) => !item.is_system) ? <div className="mt-4 border-t border-[var(--sys-input-border)] pt-3">{detail.upstream.concat(detail.downstream).filter((item) => !item.is_system).map((item) => <div key={item.edge_id} className="flex items-center justify-between py-1 text-xs text-[var(--sys-body)]"><span>{item.upstream_code} → {item.downstream_code}</span><button type="button" onClick={() => removeEdge(item.edge_id)} aria-label="删除关系" className="p-1 text-rose-600"><Trash2 className="h-3.5 w-3.5" /></button></div>)}</div> : null}
            </section>
          </aside>
        </div>
      ) : null}
    </div>
  );
}
