from __future__ import annotations

from datetime import datetime
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.competitor_report.prompts import PROMPT_VERSION, render_competitor_summary_prompt
from app.agents.competitor_report.renderer import render_competitor_report_html
from app.agents.competitor_report.scope import resolve_competitor_report_scope
from app.agents.competitor_report.state import CompetitorReportState
from app.agents.competitor_report.storage import save_competitor_report_agent_result
from app.agents.competitor_report.tools import collect_competitor_report_dataset
from app.agents.qa.time_scope_resolver import SHANGHAI_TZ
from app.config import DATABASE_URL
from app.services.comment_user_ai_profile import call_openai_compatible_json
from app.services.competitor_library import get_competitor_options
from app.services.report_agent import resolve_runtime_config


def _validate_llm_summary(summary: Any, dataset: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(summary, dict):
        raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约。")
    executive_summary = summary.get("executive_summary")
    if (
        not isinstance(executive_summary, list)
        or not 3 <= len(executive_summary) <= 5
        or any(not isinstance(item, str) or not item.strip() for item in executive_summary)
    ):
        raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：executive_summary 必须为3至5条非空结论。")
    top_work_findings = summary.get("top_work_findings")
    if not isinstance(top_work_findings, list) or not top_work_findings:
        raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：top_work_findings 必须为非空数组。")
    known_work_ids = {str(work.get("work_id")) for work in dataset.get("top_works") or [] if work.get("work_id")}
    seen_work_ids: set[str] = set()
    for finding in top_work_findings:
        if not isinstance(finding, dict):
            raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：热门作品结论格式错误。")
        work_id = finding.get("work_id")
        why_it_matters = finding.get("why_it_matters")
        if (
            not isinstance(work_id, str)
            or work_id not in known_work_ids
            or work_id in seen_work_ids
            or not isinstance(why_it_matters, str)
            or not why_it_matters.strip()
        ):
            raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：热门作品结论必须引用输入作品 ID。")
        seen_work_ids.add(work_id)
    for key in ("account_summary", "rhythm_summary", "dealer_summary"):
        if not isinstance(summary.get(key), str) or not summary[key].strip():
            raise ValueError(f"LLM 返回结果不符合竞品报告 JSON 契约：{key} 必须为非空文本。")
    return summary


def resolve_scope_node(state: CompetitorReportState) -> CompetitorReportState:
    options = get_competitor_options()
    scope = resolve_competitor_report_scope(
        state.get("message") or "",
        known_brands=options.get("brands") or [],
    )
    state.update(scope)  # type: ignore[arg-type]
    notices: list[str] = []
    if scope["brand_defaulted"]:
        notices.append(f"未指定品牌，默认使用{scope['brand_name']}。")
    if scope["time_defaulted"]:
        notices.append("未指定时间，默认使用最近30天。")
    state["scope_notice"] = notices
    return state


def collect_data_node(state: CompetitorReportState) -> CompetitorReportState:
    dataset = collect_competitor_report_dataset(
        state["brand_name"],
        state["start_date"],
        state["end_date"],
    )
    if int((dataset.get("overview") or {}).get("work_count") or 0) == 0:
        raise ValueError(
            f"{state['brand_name']}在{state['start_date']}至{state['end_date']}范围内没有作品，无法生成竞品报告。"
        )
    state["dataset"] = dataset
    return state


def summarize_node(state: CompetitorReportState) -> CompetitorReportState:
    prompt = render_competitor_summary_prompt(state["dataset"])
    base_url, api_key, model, timeout_seconds = resolve_runtime_config(
        DATABASE_URL,
        None,
        None,
        None,
        None,
    )
    state["rendered_prompt"] = prompt
    raw_summary = call_openai_compatible_json(
        prompt,
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )
    state["llm_summary"] = _validate_llm_summary(raw_summary, state["dataset"])
    return state


def render_report_node(state: CompetitorReportState) -> CompetitorReportState:
    state["report_html"] = render_competitor_report_html(state["dataset"], state["llm_summary"])
    return state


def save_report_node(state: CompetitorReportState) -> CompetitorReportState:
    asset = save_competitor_report_agent_result(
        {
            "brand_name": state["brand_name"],
            "start_date": state["start_date"],
            "end_date": state["end_date"],
            "generated_at": datetime.now(SHANGHAI_TZ),
            "prompt_version": PROMPT_VERSION,
            "html": state["report_html"],
            "summary": state["llm_summary"],
            "context": state["dataset"],
            "rendered_prompt": state["rendered_prompt"],
        }
    )
    notices = state.get("scope_notice") or []
    notice_text = f"（{'；'.join(item.rstrip('。') for item in notices)}）" if notices else ""
    state["report_asset"] = asset
    state["result"] = {
        "status": "generated",
        "answer": (
            f"已生成{state['brand_name']}竞品动态报告，统计范围为"
            f"{state['start_date']} 至 {state['end_date']}。{notice_text}"
        ),
        "report_type": "competitor",
        "brand_name": state["brand_name"],
        "time_scope": {"start_date": state["start_date"], "end_date": state["end_date"]},
        "scope_notice": notices,
        "summary": state["llm_summary"],
        "report_asset": asset,
    }
    return state


def build_competitor_report_graph():
    graph = StateGraph(CompetitorReportState)
    graph.add_node("resolve_scope", resolve_scope_node)
    graph.add_node("collect_data", collect_data_node)
    graph.add_node("summarize", summarize_node)
    graph.add_node("render_report", render_report_node)
    graph.add_node("save_report", save_report_node)
    graph.set_entry_point("resolve_scope")
    graph.add_edge("resolve_scope", "collect_data")
    graph.add_edge("collect_data", "summarize")
    graph.add_edge("summarize", "render_report")
    graph.add_edge("render_report", "save_report")
    graph.add_edge("save_report", END)
    return graph.compile()


def run_competitor_report_agent(
    message: str,
    event_id: str | None = None,
    history: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    state = build_competitor_report_graph().invoke(
        {"message": message, "event_id": event_id, "history": history or []}
    )
    return state["result"]
