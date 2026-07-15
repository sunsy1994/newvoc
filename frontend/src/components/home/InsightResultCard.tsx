"use client";

import { AlertTriangle, CircleCheck, Eye, Lightbulb, MessageSquareQuote, ShieldAlert, UsersRound } from "lucide-react";

import type { InsightResult } from "@/types/vocMarket";


const relationLabels: Record<string, string> = {
  same_model: "同车型",
  same_brand: "同品牌",
  cross_brand: "跨品牌",
};

const reactionTones: Record<string, string> = {
  支持: "border-[#bde4d6] bg-[#f1faf6] text-[#177054]",
  观望: "border-[#ead9a7] bg-[#fffaf0] text-[#8a6515]",
  反对: "border-[#f0c6c3] bg-[#fff5f4] text-[#a2443e]",
};

function SectionTitle({ icon: Icon, title, subtitle }: { icon: typeof Lightbulb; title: string; subtitle?: string }) {
  return (
    <div className="mb-3 flex items-start gap-2.5">
      <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-[var(--theme-primary-soft)] text-[var(--sys-icon-fill)]">
        <Icon className="h-4 w-4" />
      </span>
      <div>
        <h4 className="text-sm font-semibold text-[var(--theme-ink)]">{title}</h4>
        {subtitle ? <p className="mt-0.5 text-[11px] leading-5 text-[var(--theme-muted)]">{subtitle}</p> : null}
      </div>
    </div>
  );
}

function ScenarioSummary({ result }: { result: InsightResult }) {
  const scenario = result.scenario;
  const parts = [
    scenario.action_type,
    ...(scenario.affected_aspects ?? []),
    ...(scenario.compensation ?? []),
    scenario.target,
  ].filter(Boolean);
  return (
    <header className="relative overflow-hidden rounded-[22px] border border-[var(--theme-border)] bg-[linear-gradient(135deg,#effaf6_0%,#ffffff_52%,#f3f2ff_100%)] p-4 sm:p-5">
      <div className="absolute -right-10 -top-12 h-32 w-32 rounded-full bg-[#8fded0]/20 blur-2xl" />
      <div className="relative flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--theme-muted)]">Evidence-grounded simulation</p>
          <h3 className="mt-1.5 text-lg font-semibold tracking-tight text-[var(--theme-ink)]">用户反应推演</h3>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-[var(--theme-body)]">{parts.join(" · ") || "待补充推演场景"}</p>
        </div>
        <div className="flex flex-wrap gap-2 text-[10px] font-semibold">
          <span className="rounded-full border border-white/80 bg-white/75 px-2.5 py-1 text-[var(--theme-body)] shadow-sm">置信度：{result.confidence}</span>
          <span className="rounded-full border border-white/80 bg-white/75 px-2.5 py-1 text-[var(--theme-body)] shadow-sm">
            {result.data_scope.similar_event_count ?? result.similar_events.length} 个相似事件
          </span>
          <span className="rounded-full border border-white/80 bg-white/75 px-2.5 py-1 text-[var(--theme-body)] shadow-sm">
            {result.data_scope.relevant_comment_count ?? result.evidence_comments.length} 条证据
          </span>
        </div>
      </div>
    </header>
  );
}

export function InsightResultCard({ result }: { result: InsightResult }) {
  const status = result.status ?? (result.reaction_cards.length ? "completed" : "insufficient_data");
  const isCompleted = status === "completed";

  if (!isCompleted) {
    const isClarification = status === "needs_clarification";
    return (
      <section className="mt-3 rounded-[22px] border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4 shadow-[0_16px_42px_rgba(31,43,39,0.05)] sm:p-5">
        <ScenarioSummary result={result} />
        <div className="mt-4 flex gap-3 rounded-2xl border border-dashed border-[var(--theme-border)] bg-white p-4">
          {isClarification ? <Lightbulb className="mt-0.5 h-5 w-5 shrink-0 text-[var(--sys-icon-fill)]" /> : <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[#a87422]" />}
          <div>
            <h4 className="text-sm font-semibold text-[var(--theme-ink)]">{isClarification ? "需要补充推演条件" : status === "partial" ? "当前仅能部分匹配" : "暂无此类数据推演"}</h4>
            <p className="mt-1 text-xs leading-6 text-[var(--theme-body)]">
              {status === "partial" ? "已找到相关历史事件，但证据不足以形成完整用户反应结论。" : "当前事件库未找到足够相似的历史事件，或相关评论未达到证据门槛。"}
            </p>
            {result.limitations.length ? (
              <ul className="mt-2 space-y-1 text-xs leading-5 text-[var(--theme-muted)]">
                {result.limitations.map((item) => <li key={item}>· {item}</li>)}
              </ul>
            ) : null}
          </div>
        </div>
        {status === "partial" && result.similar_events.length ? (
          <div className="mt-4 rounded-2xl border border-[var(--theme-border)] bg-white p-4">
            <h4 className="text-xs font-semibold text-[var(--theme-ink)]">部分匹配事件</h4>
            <div className="mt-2 space-y-2">
              {result.similar_events.map((event, index) => (
                <div key={event.event_id ?? index} className="flex items-center justify-between gap-3 rounded-xl bg-[var(--theme-soft-panel)] px-3 py-2 text-xs">
                  <span className="font-medium text-[var(--theme-body)]">{event.event_name || "历史事件"}</span>
                  <span className="shrink-0 text-[10px] font-semibold text-[var(--sys-icon-fill)]">{relationLabels[event.relation_type ?? ""] || event.relation_type} · {event.comment_count} 条证据</span>
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </section>
    );
  }

  return (
    <section className="mt-3 space-y-4 rounded-[24px] border border-[var(--theme-border)] bg-white p-4 shadow-[0_18px_50px_rgba(31,43,39,0.06)] sm:p-5">
      <ScenarioSummary result={result} />

      <div>
        <SectionTitle icon={CircleCheck} title="用户反应判断" subtitle="仅展示历史证据能够支持的定性方向" />
        <div className="grid gap-3 md:grid-cols-3">
          {result.reaction_cards.map((card, index) => (
            <article key={`${card.reaction}-${index}`} className={`rounded-2xl border p-4 ${reactionTones[card.reaction] ?? reactionTones.观望}`}>
              <div className="flex items-center justify-between gap-2">
                <span className="text-sm font-semibold">{card.reaction}</span>
                <span className="rounded-full bg-white/70 px-2 py-0.5 text-[10px] font-semibold">{card.strength}</span>
              </div>
              <p className="mt-2 text-xs leading-5 text-current/90">{card.summary}</p>
              {card.reasons.length ? <p className="mt-3 border-t border-current/10 pt-2 text-[11px] leading-5 text-current/75">{card.reasons.join("；")}</p> : null}
            </article>
          ))}
        </div>
      </div>

      {result.audience_cards.length ? (
        <div>
          <SectionTitle icon={UsersRound} title="受影响用户群" subtitle="没有用户群证据时不生成画像" />
          <div className="grid gap-3 sm:grid-cols-2">
            {result.audience_cards.map((card, index) => (
              <article key={`${card.audience}-${index}`} className="rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-4">
                <div className="flex items-center justify-between gap-3"><h5 className="text-sm font-semibold text-[var(--theme-ink)]">{card.audience}</h5><span className="text-[11px] font-semibold text-[var(--sys-icon-fill)]">{card.reaction}</span></div>
                <p className="mt-2 text-xs leading-5 text-[var(--theme-body)]">{card.concerns.join(" · ")}</p>
              </article>
            ))}
          </div>
        </div>
      ) : null}

      {result.impact_cards.length ? (
        <div>
          <SectionTitle icon={ShieldAlert} title="口碑与购买信号" subtitle="只描述影响方向，不给出行动建议" />
          <div className="grid gap-3 sm:grid-cols-2">
            {result.impact_cards.map((card, index) => (
              <article key={`${card.dimension}-${index}`} className="rounded-2xl border border-[var(--theme-border)] bg-white p-4 shadow-[0_8px_24px_rgba(31,43,39,0.035)]">
                <p className="text-[10px] font-semibold uppercase tracking-[0.12em] text-[var(--theme-muted)]">{card.dimension}</p>
                <h5 className="mt-1 text-sm font-semibold text-[var(--theme-ink)]">{card.direction}</h5>
                <p className="mt-2 text-xs leading-5 text-[var(--theme-body)]">{card.summary}</p>
              </article>
            ))}
          </div>
        </div>
      ) : null}

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-[20px] border border-[var(--theme-border)] bg-[#fbfaf6] p-4">
          <SectionTitle icon={MessageSquareQuote} title="表达主题" subtitle="Agent 归纳方向，不作为真实用户引语" />
          <div className="flex flex-wrap gap-2">
            {result.expression_themes.map((theme) => <span key={theme} className="rounded-full border border-[#e7dcc2] bg-white px-3 py-1.5 text-[11px] text-[#765d2f]">{theme}</span>)}
          </div>
        </div>
        <div className="rounded-[20px] border border-[var(--theme-border)] bg-[#f7faf9] p-4">
          <SectionTitle icon={Eye} title="真实证据原话" subtitle="来自已入库历史事件，可展开核对来源" />
          <div className="space-y-2">
            {result.evidence_comments.slice(0, 8).map((comment, index) => (
              <details key={comment.comment_id ?? `${comment.event_id}-${index}`} className="rounded-xl border border-[var(--theme-border)] bg-white px-3 py-2 text-xs">
                <summary className="cursor-pointer list-none font-medium leading-5 text-[var(--theme-body)]">“{comment.comment_text}”</summary>
                <p className="mt-2 text-[10px] text-[var(--theme-muted)]">{comment.event_name || "历史事件"} · {relationLabels[comment.relation_type ?? ""] || "关系未标注"} · {comment.platform || "平台未标注"}</p>
              </details>
            ))}
          </div>
        </div>
      </div>

      <div>
        <SectionTitle icon={Lightbulb} title="相似事件与推演边界" subtitle="同车型优先，其次同品牌，再其次跨品牌" />
        <div className="space-y-2">
          {result.similar_events.map((event, index) => (
            <article key={event.event_id ?? index} className="flex flex-col gap-2 rounded-2xl border border-[var(--theme-border)] bg-[var(--theme-soft-panel)] p-3 sm:flex-row sm:items-center sm:justify-between">
              <div><h5 className="text-xs font-semibold text-[var(--theme-ink)]">{event.event_name || "历史事件"}</h5><p className="mt-1 text-[10px] text-[var(--theme-muted)]">{event.similarities.join(" · ") || "相关场景"}</p></div>
              <div className="flex flex-wrap gap-2 text-[10px] font-semibold"><span className="rounded-full bg-white px-2 py-1 text-[var(--sys-icon-fill)]">{relationLabels[event.relation_type ?? ""] || event.relation_type}</span><span className="rounded-full bg-white px-2 py-1 text-[var(--theme-body)]">{event.comment_count} 条证据</span></div>
            </article>
          ))}
        </div>
        {result.limitations.length ? <p className="mt-3 rounded-xl bg-[#fff8ef] px-3 py-2 text-[11px] leading-5 text-[#81602e]">边界：{result.limitations.join("；")}</p> : null}
      </div>
    </section>
  );
}
