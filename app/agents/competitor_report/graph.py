from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.competitor_report.prompts import PROMPT_VERSION, render_competitor_summary_prompt
from app.agents.competitor_report.renderer import render_competitor_report_html
from app.agents.competitor_report.scope import DEFAULT_BRAND, extract_competitor_report_scope, resolve_competitor_report_scope
from app.agents.competitor_report.state import CompetitorReportState
from app.agents.competitor_report.storage import save_competitor_report_agent_result
from app.agents.competitor_report.tools import collect_competitor_report_dataset
from app.agents.qa.time_scope_resolver import SHANGHAI_TZ
from app.config import DATABASE_URL
from app.services.comment_user_ai_profile import call_openai_compatible_json
from app.services.competitor_library import get_competitor_options
from app.services.report_agent import resolve_runtime_config


LLM_SUMMARY_KEYS = {
    "executive_summary",
    "top_work_findings",
    "account_summary",
    "rhythm_summary",
    "dealer_summary",
}
TOP_WORK_FINDING_KEYS = {"work_id", "why_it_matters"}
INTERNAL_SNAKE_CASE_TOKENS = (
    "competitor_work",
    "insight_markdown",
    "rendered_prompt",
    "total_engagement",
    "average_engagement",
    "work_count",
    "account_count",
    "brand_name",
    "start_date",
    "end_date",
    "daily_trend",
    "publish_date",
    "account_contribution",
    "author_name",
    "account_type",
    "is_official",
    "topic_distribution",
    "top_works",
    "work_id",
    "published_at",
    "topic_tags",
    "video_url",
    "interaction_like_cnt",
    "comment_cnt",
    "favorite_cnt",
    "share_cnt",
    "data_notes",
    "event_id",
    "brand_defaulted",
    "time_defaulted",
    "scope_notice",
    "llm_summary",
    "report_html",
    "report_asset",
    "report_run_id",
    "generated_at",
    "prompt_version",
    "summary_json",
    "context_json",
    "executive_summary",
    "top_work_findings",
    "why_it_matters",
    "account_summary",
    "rhythm_summary",
    "dealer_summary",
    "report_type",
    "time_scope",
    "database_url",
    "base_url",
    "api_key",
    "timeout_seconds",
    "known_brands",
    "get_competitor_options",
    "resolve_competitor_report_scope",
    "collect_competitor_report_dataset",
    "resolve_runtime_config",
    "call_openai_compatible_json",
    "render_competitor_summary_prompt",
    "render_competitor_report_html",
    "save_competitor_report_agent_result",
    "ensure_competitor_report_table",
    "normalize_competitor_report_row",
    "resolve_scope_node",
    "collect_data_node",
    "summarize_node",
    "render_report_node",
    "save_report_node",
    "build_competitor_report_graph",
    "run_competitor_report_agent",
)
INTERNAL_TOKEN_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:"
    + "|".join(re.escape(token) for token in INTERNAL_SNAKE_CASE_TOKENS)
    + r")(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
DATA_ASSET_RE = re.compile(r"(?<![A-Za-z0-9_])data_asset\.", re.IGNORECASE)
INTERNAL_LITERAL_RE = re.compile(
    r"(?<![A-Za-z0-9_])(?:skill\.md|app[./\\]agents|tool[\s_-]+name)(?![A-Za-z0-9_])",
    re.IGNORECASE,
)
TOOL_ASSIGNMENT_RE = re.compile(r"(?<![A-Za-z0-9_])tool\s*[:=]\s*\S+", re.IGNORECASE)
HTTP_URL_RE = re.compile(r"https?://[^\s<>\"'，。；：！？、（）【】\[\]{}]+", re.IGNORECASE)
WINDOWS_ABSOLUTE_PATH_RE = re.compile(r"(?<![A-Za-z0-9])(?:[A-Z]:[\\/]|\\\\[^\\/\s]+[\\/])", re.IGNORECASE)
SENSITIVE_UNIX_ROOTS = (
    "etc",
    "bin",
    "boot",
    "dev",
    "lib",
    "lib64",
    "proc",
    "run",
    "sbin",
    "sys",
    "tmp",
    "srv",
    "usr",
    "data",
    "home",
    "root",
    "opt",
    "var",
    "mnt",
    "Users",
    "workspace",
)
UNIX_ABSOLUTE_PATH_RE = re.compile(
    r"(?:"
    r"(?:^|(?<=[：:=（(【\[]))/(?!/)[^/\s<>\"'，。；：！？、（）【】()\[\]{}]+"
    r"|(?<=\s)/(?!/)[A-Za-z0-9._~+-]+"
    r")"
    r"(?:/[^/\s<>\"'，。；：！？、（）【】()\[\]{}]+)+"
)
UNIX_SINGLE_SEGMENT_PATH_RE = re.compile(
    r"(?:^|(?<=[\s：:=（(【\[]))/(?:"
    + "|".join(re.escape(root) for root in SENSITIVE_UNIX_ROOTS)
    + r")(?![A-Za-z0-9._~+\-/])",
    re.IGNORECASE,
)
RELATIVE_SKILL_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9_.-])(?:\.(?:codex|agents|claude)|skills)[\\/]",
    re.IGNORECASE,
)


class CompetitorReportExecutionError(RuntimeError):
    def __init__(
        self,
        stage: str,
        state: CompetitorReportState,
        cause: Exception,
        *,
        retryable: bool = True,
    ) -> None:
        super().__init__(str(cause))
        self.stage = stage
        self.brand_name = str(state.get("brand_name") or "")
        self.start_date = str(state.get("start_date") or "")
        self.end_date = str(state.get("end_date") or "")
        self.retryable = retryable
        self.cause = cause


class CompetitorReportNoDataError(CompetitorReportExecutionError):
    def __init__(self, state: CompetitorReportState) -> None:
        message = (
            f"{state['brand_name']}在{state['start_date']}至{state['end_date']}范围内暂无竞品数据。"
        )
        super().__init__("no_data", state, ValueError(message), retryable=False)


def _reject_internal_prose(value: str) -> None:
    path_scan_value = HTTP_URL_RE.sub("", value)
    if (
        any(pattern.search(value) for pattern in (INTERNAL_TOKEN_RE, DATA_ASSET_RE, INTERNAL_LITERAL_RE, TOOL_ASSIGNMENT_RE))
        or any(
            pattern.search(path_scan_value)
            for pattern in (
                WINDOWS_ABSOLUTE_PATH_RE,
                UNIX_ABSOLUTE_PATH_RE,
                UNIX_SINGLE_SEGMENT_PATH_RE,
                RELATIVE_SKILL_PATH_RE,
            )
        )
    ):
        raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：结论包含内部标识。")


def _validate_llm_summary(summary: Any, dataset: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(summary, dict):
        raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约。")
    if set(summary) != LLM_SUMMARY_KEYS:
        raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：顶层字段不匹配。")
    executive_summary = summary.get("executive_summary")
    if (
        not isinstance(executive_summary, list)
        or not 3 <= len(executive_summary) <= 5
        or any(not isinstance(item, str) or not item.strip() for item in executive_summary)
    ):
        raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：executive_summary 必须为3至5条非空结论。")
    for item in executive_summary:
        _reject_internal_prose(item)
    top_work_findings = summary.get("top_work_findings")
    if not isinstance(top_work_findings, list) or not top_work_findings:
        raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：top_work_findings 必须为非空数组。")
    known_work_ids = {str(work.get("work_id")) for work in dataset.get("top_works") or [] if work.get("work_id")}
    seen_work_ids: set[str] = set()
    for finding in top_work_findings:
        if not isinstance(finding, dict):
            raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：热门作品结论格式错误。")
        if set(finding) != TOP_WORK_FINDING_KEYS:
            raise ValueError("LLM 返回结果不符合竞品报告 JSON 契约：热门作品结论字段不匹配。")
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
        _reject_internal_prose(why_it_matters)
        seen_work_ids.add(work_id)
    if seen_work_ids != known_work_ids or len(top_work_findings) != len(known_work_ids):
        raise ValueError(
            "LLM 返回结果不符合竞品报告 JSON 契约：top_work_findings 必须精确覆盖全部热门作品。"
        )
    for key in ("account_summary", "rhythm_summary", "dealer_summary"):
        if not isinstance(summary.get(key), str) or not summary[key].strip():
            raise ValueError(f"LLM 返回结果不符合竞品报告 JSON 契约：{key} 必须为非空文本。")
        _reject_internal_prose(summary[key])
    return summary


def resolve_scope_node(state: CompetitorReportState) -> CompetitorReportState:
    try:
        options = get_competitor_options()
        state.update(
            resolve_competitor_report_scope(
                state.get("message") or "",
                known_brands=options.get("brands") or [],
            )
        )
        base_url, api_key, model, timeout_seconds = resolve_runtime_config(
            DATABASE_URL,
            None,
            None,
            None,
            None,
        )
        runtime = {
            "base_url": base_url,
            "api_key": api_key,
            "model": model,
            "timeout_seconds": timeout_seconds,
        }
        scope = extract_competitor_report_scope(
            state.get("message") or "",
            history=state.get("history") or [],
            known_brands=options.get("brands") or [],
            llm_json=lambda prompt: call_openai_compatible_json(prompt, **runtime),
        )
        state["ai_runtime"] = runtime
    except Exception as exc:
        raise CompetitorReportExecutionError("scope", state, exc) from exc
    state.update(scope)  # type: ignore[arg-type]
    notices: list[str] = []
    if scope["brand_defaulted"]:
        notices.append(f"未指定品牌，默认使用{scope['brand_name']}。")
    if scope["time_defaulted"]:
        notices.append("未指定时间，默认使用最近30天。")
    if scope.get("scope_source") == "deterministic_fallback":
        notices.append("智能范围解析暂不可用，已按明确表达确定范围。")
    state["scope_notice"] = notices
    return state


def collect_data_node(state: CompetitorReportState) -> CompetitorReportState:
    try:
        dataset = collect_competitor_report_dataset(
            state["brand_name"],
            state["start_date"],
            state["end_date"],
        )
    except Exception as exc:
        raise CompetitorReportExecutionError("database", state, exc) from exc
    if int((dataset.get("overview") or {}).get("work_count") or 0) == 0:
        raise CompetitorReportNoDataError(state)
    state["dataset"] = dataset
    return state


def summarize_node(state: CompetitorReportState) -> CompetitorReportState:
    prompt = render_competitor_summary_prompt(state["dataset"])
    state["rendered_prompt"] = prompt
    try:
        runtime = state["ai_runtime"]
        raw_summary = call_openai_compatible_json(prompt, **runtime)
        state["llm_summary"] = _validate_llm_summary(raw_summary, state["dataset"])
    except Exception as exc:
        raise CompetitorReportExecutionError("llm", state, exc) from exc
    return state


def render_report_node(state: CompetitorReportState) -> CompetitorReportState:
    try:
        state["report_html"] = render_competitor_report_html(state["dataset"], state["llm_summary"])
    except Exception as exc:
        raise CompetitorReportExecutionError("render", state, exc) from exc
    return state


def save_report_node(state: CompetitorReportState) -> CompetitorReportState:
    try:
        asset = save_competitor_report_agent_result(
            {
                "brand_name": state["brand_name"],
                "start_date": state["start_date"],
                "end_date": state["end_date"],
                "generated_at": datetime.now(SHANGHAI_TZ),
                "status": "completed",
                "error_message": None,
                "prompt_version": PROMPT_VERSION,
                "html": state["report_html"],
                "summary": state["llm_summary"],
                "context": state["dataset"],
                "rendered_prompt": state["rendered_prompt"],
            }
        )
    except Exception as exc:
        raise CompetitorReportExecutionError("storage", state, exc) from exc
    notices = state.get("scope_notice") or []
    notice_text = f"（{'；'.join(item.rstrip('。') for item in notices)}）" if notices else ""
    public_asset = {
        "report_run_id": asset["report_run_id"],
        "report_type": "competitor_report",
    }
    state["report_asset"] = public_asset
    state["result"] = {
        "status": "generated",
        "answer": (
            f"已生成{state['brand_name']}竞品动态报告，统计范围为"
            f"{state['start_date']} 至 {state['end_date']}。{notice_text}"
        ),
        "report_type": "competitor_report",
        "brand_name": state["brand_name"],
        "time_scope": {"start_date": state["start_date"], "end_date": state["end_date"]},
        "scope_notice": notices,
        "summary": state["llm_summary"],
        "report_asset": public_asset,
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
    anchor = datetime.now(SHANGHAI_TZ).date()
    initial_scope: dict[str, Any] = {
        "brand_name": DEFAULT_BRAND,
        "brand_defaulted": True,
        "start_date": (anchor - timedelta(days=29)).isoformat(),
        "end_date": anchor.isoformat(),
        "time_defaulted": True,
    }
    try:
        initial_scope = resolve_competitor_report_scope(message)
        state = build_competitor_report_graph().invoke(
            {
                "message": message,
                "event_id": event_id,
                "history": history or [],
                **initial_scope,
            }
        )
        return state["result"]
    except CompetitorReportExecutionError as exc:
        status = "no_data" if isinstance(exc, CompetitorReportNoDataError) else "failed"
        if exc.brand_name and exc.start_date and exc.end_date:
            try:
                save_competitor_report_agent_result(
                    {
                        "brand_name": exc.brand_name,
                        "start_date": exc.start_date,
                        "end_date": exc.end_date,
                        "generated_at": datetime.now(SHANGHAI_TZ),
                        "status": status,
                        "error_message": str(exc.cause),
                        "prompt_version": PROMPT_VERSION,
                        "html": "",
                        "summary": {},
                        "context": {},
                        "rendered_prompt": "",
                    }
                )
            except Exception:
                pass
        time_scope = (
            {"start_date": exc.start_date, "end_date": exc.end_date}
            if exc.start_date and exc.end_date
            else {}
        )
        if status == "no_data":
            answer = (
                f"{exc.brand_name}在{exc.start_date} 至 {exc.end_date}范围内暂无竞品数据，"
                "未生成报告资产。"
            )
        else:
            scope_text = (
                f"（{exc.brand_name}，{exc.start_date} 至 {exc.end_date}）"
                if exc.brand_name and exc.start_date and exc.end_date
                else ""
            )
            answer = f"竞品动态报告生成失败{scope_text}，请重试。"
        return {
            "status": status,
            "retryable": exc.retryable,
            "answer": answer,
            "report_type": "competitor_report",
            "brand_name": exc.brand_name,
            "time_scope": time_scope,
            "scope_notice": [],
            "report_asset": None,
        }
    except Exception as exc:
        try:
            save_competitor_report_agent_result(
                {
                    "brand_name": initial_scope["brand_name"],
                    "start_date": initial_scope["start_date"],
                    "end_date": initial_scope["end_date"],
                    "generated_at": datetime.now(SHANGHAI_TZ),
                    "status": "failed",
                    "error_message": str(exc),
                    "prompt_version": PROMPT_VERSION,
                    "html": "",
                    "summary": {},
                    "context": {},
                    "rendered_prompt": "",
                }
            )
        except Exception:
            pass
        return {
            "status": "failed",
            "retryable": True,
            "answer": "竞品动态报告生成失败，请重试。",
            "report_type": "competitor_report",
            "brand_name": initial_scope["brand_name"],
            "time_scope": {
                "start_date": initial_scope["start_date"],
                "end_date": initial_scope["end_date"],
            },
            "scope_notice": [],
            "report_asset": None,
        }
