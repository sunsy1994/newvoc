import type { ProductStorylineMetric, ProductStorylineView } from "./productStorylineData";
import type { ReportVisualChart } from "../report-visuals/types";

const CHAPTER_IDS = ["output", "needs", "sources", "follow_up"] as const;
const txt=(v:unknown)=>typeof v==="string"&&v.trim()?v.trim():undefined;
const num=(v:unknown)=>typeof v==="number"&&Number.isFinite(v)&&v>=0?v:undefined;
const rows=(charts:ReportVisualChart[],id:string)=>charts.find(c=>c.chart_id===id)?.data??[];
const fmt=(v:number)=>new Intl.NumberFormat("zh-CN").format(v);
const isRecord=(v:unknown):v is Record<string,unknown>=>typeof v==="object"&&v!==null&&!Array.isArray(v);

function metrics(charts:ReportVisualChart[],chapter:string):ProductStorylineMetric[]{
  if(chapter==="output") return rows(charts,"sales-lead-output").slice(-2).flatMap(r=>txt(r.stage)&&num(r.count)!==undefined?[{label:txt(r.stage)!,value:`${fmt(num(r.count)!)} 条`}]:[]);
  if(chapter==="needs") return rows(charts,"sales-user-needs").filter(r=>r.row_type==="intent").sort((a,b)=>(num(b.count)??0)-(num(a.count)??0)).slice(0,3).flatMap(r=>txt(r.label)&&num(r.count)!==undefined?[{label:txt(r.label)!,value:`${fmt(num(r.count)!)} 条`}]:[]);
  if(chapter==="sources") return rows(charts,"sales-content-sources").sort((a,b)=>(num(b.high_intent_comment_count)??0)-(num(a.high_intent_comment_count)??0)).slice(0,3).flatMap(r=>(txt(r.title)||txt(r.platform))&&num(r.high_intent_comment_count)!==undefined?[{label:(txt(r.title)||txt(r.platform))!,value:`${fmt(num(r.high_intent_comment_count)!)} 条中高意向`}]:[]);
  const users=rows(charts,"sales-follow-up-pool"); return ["强","中"].map(signal=>({label:`${signal}信号用户`,value:`${users.filter(r=>r.purchase_signal===signal||(signal==="强"?r.purchase_signal==="strong":r.purchase_signal==="medium")).length} 位`}));
}

export function isSalesStoryline(value:unknown){return isRecord(value)&&Boolean(txt(value.headline))&&Boolean(txt(value.lead))&&Array.isArray(value.chapters)&&value.chapters.length===4&&value.chapters.every((c,i)=>isRecord(c)&&c.chapter_id===CHAPTER_IDS[i]&&Boolean(txt(c.title))&&Boolean(txt(c.conclusion))&&typeof c.body==="string"&&Array.isArray(c.metric_refs));}

export function buildSalesStorylineView(value:unknown,charts:ReportVisualChart[],eventName?:string):ProductStorylineView|null{
  if(!isSalesStoryline(value))return null;
  const story=value as {headline:string;lead:string;chapters:Array<{chapter_id:typeof CHAPTER_IDS[number];title:string;conclusion:string;body:string}>};
  const chapters=story.chapters.map(c=>({chapterId:c.chapter_id,title:c.title,conclusion:c.conclusion,body:c.body,metrics:metrics(charts,c.chapter_id).slice(0,3),evidence:[]}));
  if(!chapters.some(c=>c.metrics.length))return null;
  return {...(txt(eventName)?{eventName:txt(eventName)}:{}),headline:story.headline,lead:story.lead,heroMetrics:[...metrics(charts,"output").slice(-1),...metrics(charts,"follow_up").slice(0,2)],chapters};
}

export function formatSalesStorylineCopyText(view:ProductStorylineView){return [view.eventName?`${view.eventName} · 销售线索复盘`:"销售线索复盘",view.headline,view.lead,...view.chapters.map((c,i)=>[`${String(i+1).padStart(2,"0")} ${c.title}`,`结论：${c.conclusion}`,c.body,...c.metrics.map(m=>`- ${m.label}：${m.value}`)].filter(Boolean).join("\n"))].filter(Boolean).join("\n\n");}
