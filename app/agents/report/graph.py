from __future__ import annotations

import json
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.report import builder
from app.agents.report.state import EventReportState
from app.services.event_voc_insights import get_voc_event_market_dashboard, get_voc_event_product_dashboard, get_voc_event_sales_dashboard
from app.services.report_agent import build_market_report_context, build_product_report_context, build_sales_report_context, resolve_runtime_config
from app.services.comment_user_ai_profile import call_openai_compatible_json
from app.config import DATABASE_URL
from app.agents.qa.tools import infer_event_context_from_question
from app.agents.report.storage import save_event_report_agent_result


PROMPT_VERSION = "event_report_agent_v1"


def _render_prompt(state: EventReportState) -> str:
    context = {
        "market": state.get("market_context") or {},
        "product": state.get("product_context") or {},
        "sales": state.get("sales_context") or {},
    }
    return f"""你是 AutoVOC 事件综合报告 Agent。请只基于给定结构化数据生成事件综合报告摘要。

输出必须是 JSON：
{{
  "executive_summary": ["3-5条最关键结论，按结论先行写，每条不超过45字"],
  "recommendations": ["保留为空数组；本版本报告不输出行动建议"],
  "sections": [
    {{"title": "章节标题", "summary": "章节结论", "evidence": ["证据摘要"]}}
  ]
}}

要求：
1. 只能使用输入数据，不要编造外部事实。
2. 必须覆盖市场传播、产品反馈、销售线索三个视角，但不要给行动建议。
3. 产品视角只判断机会点、风险点、惊喜点，并解释计算口径。
4. 报告前端固定渲染为：01事件总判断、02市场传播判断、03产品机会与风险、04销售转化判断、05证据与计算口径；你只负责提供可填入模板的短结论。
5. 证据和计算方式由系统结构化字段承载，正文中不要伪造引用。

结构化数据：
{json.dumps(context, ensure_ascii=False, indent=2, default=str)}
"""


def collect_data_node(state: EventReportState) -> EventReportState:
    event_id = str(state.get("event_id") or "").strip()
    if not event_id:
        history_text = "\n".join(item.get("content") or "" for item in state.get("history") or [])
        inferred_event = infer_event_context_from_question(f"{state.get('message') or ''}\n{history_text}")
        event_id = str((inferred_event or {}).get("event_id") or "")
        if event_id:
            state["event_id"] = event_id
    if not event_id:
        raise ValueError("生成事件综合报告必须提供 event_id。")
    market_dashboard = get_voc_event_market_dashboard(event_id)
    product_dashboard = get_voc_event_product_dashboard(event_id)
    sales_dashboard = get_voc_event_sales_dashboard(event_id)
    if not market_dashboard.get("event"):
        raise ValueError("未找到事件市场看板数据，无法生成综合报告。")
    state["market_context"] = build_market_report_context(market_dashboard)
    state["product_context"] = build_product_report_context(product_dashboard)
    state["sales_context"] = build_sales_report_context(sales_dashboard)
    return state


def summarize_node(state: EventReportState) -> EventReportState:
    prompt = _render_prompt(state)
    base_url, api_key, model, timeout_seconds = resolve_runtime_config(DATABASE_URL, None, None, None, None)
    state["rendered_prompt"] = prompt
    state["llm_summary"] = call_openai_compatible_json(
        prompt,
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )
    return state


def build_report_node(state: EventReportState) -> EventReportState:
    result = builder.build_event_report_payload(
        event_id=str(state.get("event_id") or ""),
        market_context=state.get("market_context") or {},
        product_context=state.get("product_context") or {},
        sales_context=state.get("sales_context") or {},
        llm_summary=state.get("llm_summary") or {},
        prompt_version=PROMPT_VERSION,
        rendered_prompt=state.get("rendered_prompt") or "",
    )
    state["result"] = save_event_report_agent_result(result)
    return state


def build_event_report_graph():
    graph = StateGraph(EventReportState)
    graph.add_node("collect_data", collect_data_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("build_report", build_report_node)
    graph.set_entry_point("collect_data")
    graph.add_edge("collect_data", "summarize")
    graph.add_edge("summarize", "build_report")
    graph.add_edge("build_report", END)
    return graph.compile()


def run_event_report_agent(message: str, event_id: str | None = None, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    result = build_event_report_graph().invoke({"message": message, "event_id": event_id, "history": history or []})
    return result["result"]
