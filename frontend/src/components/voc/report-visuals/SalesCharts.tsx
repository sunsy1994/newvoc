import { ReportVisualShell } from "./ReportVisualShell";
import type { ReportVisualChart } from "./types";

type Props = { chart: ReportVisualChart };
const num = (v: unknown) => typeof v === "number" && Number.isFinite(v) ? Math.max(0, v) : 0;
const txt = (v: unknown) => typeof v === "string" ? v.trim() : "";
const fmt = (v: number) => new Intl.NumberFormat("zh-CN").format(v);

export function S1LeadOutputFunnel({ chart }: Props) {
  const rows = chart.data;
  const first = num(rows[0]?.count) || 1;
  return <ReportVisualShell chart={chart} hasData={rows.length > 0}><div aria-label="线索产出图" role="img" className="space-y-4">{rows.map((row, i) => { const count=num(row.count); const previous=i ? num(rows[i-1].count) : count; return <div key={`${txt(row.stage)}-${i}`} className="grid grid-cols-[120px_1fr_110px] items-center gap-3"><span className="text-sm font-medium text-[var(--theme-ink)]">{txt(row.stage)}</span><div className="h-9 rounded-xl bg-[var(--theme-selected-bg)]"><div className="flex h-full items-center rounded-xl bg-[var(--theme-primary)] px-3 text-xs font-semibold text-white" style={{width:`${Math.max(8,count/first*100)}%`,opacity:1-i*.13}}>{fmt(count)}</div></div><span className="text-right text-xs text-[var(--theme-muted)]">{i ? `${previous ? Math.round(count/previous*1000)/10 : 0}% 阶段转化` : "分析基数"}</span></div>;})}</div></ReportVisualShell>;
}

export function S2UserNeeds({ chart }: Props) {
  const intents=chart.data.filter(r=>r.row_type==="intent").sort((a,b)=>num(b.count)-num(a.count)).slice(0,8);
  const signals=chart.data.filter(r=>r.row_type==="signal");
  const max=Math.max(...intents.map(r=>num(r.count)),1); const signalTotal=signals.reduce((s,r)=>s+num(r.count),0)||1;
  return <ReportVisualShell chart={chart} hasData={chart.data.length>0}><div aria-label="用户需求图" role="img" className="space-y-5"><div className="space-y-3">{intents.map((row,i)=>{const muted=["无效","玩梗"].includes(txt(row.label));return <div key={`${txt(row.label)}-${i}`} className="grid grid-cols-[100px_1fr_72px] items-center gap-3"><span className="truncate text-sm text-[var(--theme-ink)]">{txt(row.label)}</span><div className="h-3 rounded-full bg-[var(--theme-selected-bg)]"><div className="h-full rounded-full bg-[var(--theme-primary)]" style={{width:`${Math.max(3,num(row.count)/max*100)}%`,opacity:muted?.28:.85}} /></div><span className="text-right text-xs text-[var(--theme-muted)]">{num(row.rate)}%</span></div>;})}</div><div><p className="mb-2 text-xs font-semibold text-[var(--theme-muted)]">购买信号结构</p><div className="flex h-4 overflow-hidden rounded-full bg-[var(--theme-selected-bg)]">{signals.map((row,i)=><div key={`${txt(row.label)}-${i}`} title={`${txt(row.label)} ${num(row.rate)}%`} className="bg-[var(--theme-primary)]" style={{width:`${num(row.count)/signalTotal*100}%`,opacity:.95-i*.18}} />)}</div></div></div></ReportVisualShell>;
}

export function S3ContentSources({ chart }: Props) {
  const rows=[...chart.data].sort((a,b)=>num(b.high_intent_comment_count)-num(a.high_intent_comment_count)||num(b.strong_signal_comment_count)-num(a.strong_signal_comment_count)).slice(0,8); const max=Math.max(...rows.map(r=>num(r.high_intent_comment_count)),1);
  return <ReportVisualShell chart={chart} hasData={rows.length>0}><div aria-label="内容线索来源图" role="img" className="space-y-4">{rows.map((row,i)=>{const high=num(row.high_intent_comment_count),strong=num(row.strong_signal_comment_count);return <div key={`${txt(row.content_id)||txt(row.platform)}-${i}`}><div className="mb-1.5 flex items-end justify-between gap-3"><div className="min-w-0"><p className="truncate text-sm font-medium text-[var(--theme-ink)]">{txt(row.title)||`${txt(row.platform)} · 平台级数据`}</p><p className="text-xs text-[var(--theme-muted)]">{[txt(row.platform),txt(row.author_name)].filter(Boolean).join(" · ")}</p></div><span className="shrink-0 text-xs text-[var(--theme-muted)]">{high} 中高意向 · {strong} 强信号 · {num(row.comment_count)} 评论</span></div><div className="relative h-3 rounded-full bg-[var(--theme-selected-bg)]"><div className="absolute inset-y-0 left-0 rounded-full bg-[var(--theme-primary)] opacity-45" style={{width:`${Math.max(3,high/max*100)}%`}}/><div className="absolute inset-y-0 left-0 rounded-full bg-[var(--theme-primary)]" style={{width:`${Math.max(0,strong/max*100)}%`}}/></div></div>;})}</div></ReportVisualShell>;
}

export function S4FollowUpPool({ chart }: Props) {
  const groups=[{key:"强",title:"强信号用户"},{key:"中",title:"中信号用户"}];
  return <ReportVisualShell chart={chart} hasData={chart.data.length>0}><div aria-label="承接对象图" role="img" className="grid gap-4 lg:grid-cols-2">{groups.map(group=>{const allUsers=chart.data.filter(r=>r.purchase_signal===group.key||r.purchase_signal===(group.key==="强"?"strong":"medium"));const users=allUsers.slice(0,5);return <section key={group.key} className="rounded-2xl bg-[var(--theme-soft-panel)] p-4"><div className="mb-3 flex items-center justify-between"><h4 className="font-semibold text-[var(--theme-ink)]">{group.title}</h4><span className="text-xs text-[var(--theme-primary)]">{allUsers.length} 位</span></div><div className="space-y-2">{users.map((user,i)=><article key={`${txt(user.comment_user_id)}-${i}`} className="rounded-xl border border-[var(--theme-border)] bg-[var(--theme-white)] p-3"><div className="flex justify-between gap-3"><span className="text-sm font-medium text-[var(--theme-ink)]">{txt(user.nickname)||"匿名用户"}</span><span className="text-xs text-[var(--theme-muted)]">{txt(user.platform)}</span></div><p className="mt-1 text-xs text-[var(--theme-primary)]">{txt(user.segment_label)||txt(user.profile_status)||"未画像用户"}</p>{txt(user.representative_comment)?<p className="mt-2 line-clamp-2 text-xs leading-5 text-[var(--theme-body)]">“{txt(user.representative_comment)}”</p>:null}</article>)}</div></section>;})}</div></ReportVisualShell>;
}
