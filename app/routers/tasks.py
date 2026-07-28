from __future__ import annotations

from io import BytesIO
import shutil
import tempfile
from pathlib import Path
from typing import Annotated, Literal
from urllib.parse import quote

import psycopg
import pandas as pd
import httpx
from pydantic import BaseModel, Field
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse

from app.config import TEMPLATE_DIR
from app.config import PROJECT_ROOT
from app.services.comment_user_ai_flow import build_comment_user_ai_flow
from app.services.comment_user_ai_profile import DEFAULT_PROMPT_FILE, run_comment_user_ai_profile
from app.services.data_lineage import (
    create_lineage_edge,
    create_lineage_node,
    delete_lineage_edge,
    get_lineage_detail,
    list_lineage_nodes,
    update_lineage_node,
)
from app.agents.core import AgentCapability, AgentCapabilityUnavailableError, dispatch_agent
from app.services.agent_error_log import AgentErrorLog
from app.services.asset_library import get_report_asset, list_assets
from app.services.competitor_library import (
    get_competitor_work_insight,
    get_competitor_options,
    list_competitor_accounts,
    list_competitor_works,
    save_competitor_work_insight,
)
from app.services.etl_flow import build_flow_nodes
from app.services.etl_runner import EtlRunner
from app.services.emoji_dictionary import list_emoji_mappings, save_emoji_mapping
from app.services.event_voc_insights import (
    get_voc_author_detail,
    get_voc_event_discussion_point_comments,
    get_voc_event_comment_user_insight_profile,
    get_voc_event_content_detail,
    get_voc_event_detail,
    get_voc_event_market_dashboard,
    get_voc_event_product_dashboard,
    get_voc_event_sales_dashboard,
    list_voc_events,
)
from app.services.home_dashboard import get_auto_voc_home
from app.services.profile_library import (
    export_comment_user_profile_samples,
    export_kol_profile_samples,
    get_comment_user_profile_batches,
    get_kol_profile_batches,
    list_comment_user_profiles,
    list_kol_profiles,
    load_comment_user_profiles,
    load_kol_profiles,
)
from app.services.report_agent import (
    get_latest_market_report_agent_result,
    get_latest_product_report_agent_result,
    get_latest_sales_report_agent_result,
    run_market_report_agent,
    run_product_report_agent,
    run_sales_report_agent,
)
from app.services.script_manager import ScriptManager
from app.services.system_settings import (
    get_default_ai_config,
    list_prompt_templates,
    save_default_ai_config,
    save_prompt_template,
)
from app.services.task_store import TaskStore


ALLOWED_TABLES = {
    "ods_event_upload",
    "ods_content_upload",
    "ods_comment_upload",
    "dwd_event",
    "dwd_content",
    "dwd_author",
    "dwd_comment",
    "rel_event_content",
    "rel_author_content",
    "ads_event_overview",
    "ads_event_trend_daily",
    "ads_event_content_rank",
    "ads_event_location_distribution",
    "rejected_content",
    "rejected_comment",
}

ALLOWED_TEMPLATES = {
    "event_upload_template.csv",
    "event_upload_template.xlsx",
    "content_upload_template.csv",
    "content_upload_template.xlsx",
    "comment_upload_template.csv",
    "comment_upload_template.xlsx",
}


router = APIRouter()

EXPORT_LIMIT = 100_000


class ScriptSaveRequest(BaseModel):
    content: str


class ScriptTestRunRequest(BaseModel):
    batch_id: str


class CompetitorWorkInsightSaveRequest(BaseModel):
    insight_markdown: str = ""
    updated_by: str | None = None


class CommentUserAiProfileRunRequest(BaseModel):
    profile_batch: str = "ai_profile"
    prompt_version: str = "comment_user_profile_v1"
    prompt_file: str | None = None


class AiConfigSaveRequest(BaseModel):
    base_url: str
    api_key: str | None = None
    model_name: str
    timeout_seconds: int = 60
    is_enabled: bool = True


class DataQuestionHistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class DataQuestionAgentRunRequest(BaseModel):
    question: str
    event_id: str | None = None
    history: list[DataQuestionHistoryItem] = Field(default_factory=list)


class AgentRunRequest(BaseModel):
    capability: AgentCapability
    message: str = Field(min_length=1)
    event_id: str | None = None
    history: list[DataQuestionHistoryItem] = Field(default_factory=list)


class PromptTemplateSaveRequest(BaseModel):
    prompt_name: str
    prompt_scene: str
    prompt_version: str
    prompt_content: str
    is_default: bool = False
    is_enabled: bool = True


class EmojiMappingSaveRequest(BaseModel):
    emoji_code: str
    emoji_type: str = "emoji"
    emoji_value: str
    display_name: str | None = None
    is_enabled: bool = True


class LineageNodeCreateRequest(BaseModel):
    lineage_code: str = ""
    lineage_name: str = ""
    node_kind: str = ""
    generation_type: str = ""
    business_domain: str = ""
    business_definition: str = ""
    calculation_logic: str = ""
    implementation_ref: str = ""
    prompt_scene: str = ""
    owner: str = ""
    status: str = "draft"


class LineageNodeUpdateRequest(BaseModel):
    lineage_name: str | None = None
    node_kind: str | None = None
    generation_type: str | None = None
    business_domain: str | None = None
    business_definition: str | None = None
    calculation_logic: str | None = None
    implementation_ref: str | None = None
    prompt_scene: str | None = None
    owner: str | None = None
    status: str | None = None


class LineageEdgeCreateRequest(BaseModel):
    upstream_code: str = ""
    downstream_code: str = ""
    relation_type: str = ""
    relation_description: str = ""


def get_store(request: Request) -> TaskStore:
    return request.app.state.task_store


def get_script_manager(request: Request) -> ScriptManager:
    return request.app.state.script_manager


def get_agent_error_log(request: Request) -> AgentErrorLog:
    return request.app.state.agent_error_log


@router.get("/api/system/data-lineage")
def get_system_data_lineage(
    q: str | None = None,
    node_kind: str | None = None,
    business_domain: str | None = None,
    generation_type: str | None = None,
    status: str | None = None,
) -> dict:
    try:
        return list_lineage_nodes(
            q=q,
            node_kind=node_kind,
            business_domain=business_domain,
            generation_type=generation_type,
            status=status,
        )
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/system/data-lineage/{lineage_code}")
def get_system_data_lineage_detail(lineage_code: str) -> dict:
    try:
        result = get_lineage_detail(lineage_code)
        if result is None:
            raise HTTPException(status_code=404, detail="血缘节点不存在")
        return result
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.post("/api/system/data-lineage/nodes")
def create_system_data_lineage_node(payload: LineageNodeCreateRequest) -> dict:
    try:
        return create_lineage_node(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="血缘编码已存在")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.put("/api/system/data-lineage/nodes/{lineage_code}")
def update_system_data_lineage_node(lineage_code: str, payload: LineageNodeUpdateRequest) -> dict:
    try:
        result = update_lineage_node(lineage_code, payload.model_dump(exclude_unset=True))
        if result is None:
            raise HTTPException(status_code=404, detail="血缘节点不存在")
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.post("/api/system/data-lineage/edges")
def create_system_data_lineage_edge(payload: LineageEdgeCreateRequest) -> dict:
    try:
        return create_lineage_edge(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=400, detail="血缘关系已存在")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.delete("/api/system/data-lineage/edges/{edge_id}")
def delete_system_data_lineage_edge(edge_id: int) -> dict:
    try:
        if not delete_lineage_edge(edge_id):
            raise HTTPException(status_code=404, detail="关系不存在或属于受保护的系统关系")
        return {"deleted": True, "edge_id": edge_id}
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/system/ai-config")
def get_system_ai_config() -> dict:
    try:
        return get_default_ai_config()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.put("/api/system/ai-config")
def save_system_ai_config(payload: AiConfigSaveRequest) -> dict:
    try:
        return save_default_ai_config(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/system/prompts")
def get_system_prompts(scene: str | None = None) -> dict:
    try:
        return list_prompt_templates(scene=scene)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.post("/api/system/prompts")
def save_system_prompt(payload: PromptTemplateSaveRequest) -> dict:
    try:
        return save_prompt_template(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/system/emojis")
def get_system_emojis(enabled_only: bool = False) -> dict:
    try:
        return list_emoji_mappings(enabled_only=enabled_only)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.post("/api/system/emojis")
def save_system_emoji(payload: EmojiMappingSaveRequest) -> dict:
    try:
        return save_emoji_mapping(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


def upload_suffix(upload_file: UploadFile) -> str:
    suffix = Path(upload_file.filename or "").suffix.lower()
    return suffix if suffix in {".xlsx", ".csv"} else ".xlsx"


def save_upload(upload_file: UploadFile, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as output:
        shutil.copyfileobj(upload_file.file, output)


def excel_response(dataframe: pd.DataFrame, filename: str) -> StreamingResponse:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        dataframe.to_excel(writer, sheet_name="data", index=False)
    buffer.seek(0)
    encoded_filename = quote(filename)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


def payload_to_dataframe(payload: dict) -> pd.DataFrame:
    column_labels = {column["key"]: column["label"] for column in payload.get("columns", [])}
    rows = payload.get("rows", [])
    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        return pd.DataFrame(columns=list(column_labels.values()))
    ordered_keys = [column["key"] for column in payload.get("columns", []) if column["key"] in dataframe.columns]
    dataframe = dataframe[ordered_keys]
    return dataframe.rename(columns=column_labels)


def save_temp_upload(upload_file: UploadFile) -> Path:
    suffix = Path(upload_file.filename or "").suffix.lower()
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix or ".xlsx") as temp_file:
        shutil.copyfileobj(upload_file.file, temp_file)
        return Path(temp_file.name)


def resolve_project_prompt_path(prompt_file: str | None) -> Path:
    if not prompt_file:
        return DEFAULT_PROMPT_FILE
    prompt_path = (PROJECT_ROOT / prompt_file).resolve()
    project_root = PROJECT_ROOT.resolve()
    if not prompt_path.is_relative_to(project_root):
        raise ValueError("prompt_file must stay inside project root")
    return prompt_path


@router.get("/api/tasks")
def list_tasks(request: Request) -> list[dict]:
    return get_store(request).list_tasks()


@router.get("/api/auto-voc/home")
def get_auto_voc_home_api(days: int = 30) -> dict:
    try:
        return get_auto_voc_home(days=days)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


def has_insufficient_data_support(question: str, answer: object) -> bool:
    if not isinstance(answer, str):
        return False
    insufficient_terms = (
        "缺少",
        "没有提供",
        "未提供",
        "无法直接获取",
        "无法获得",
        "无法直接评估",
        "无法判断",
        "无法评估",
        "当前没有数据支撑",
    )
    data_terms = ("数据", "画像", "证据", "信息", "样本")
    if any(term in answer for term in insufficient_terms) and any(term in answer for term in data_terms):
        return True
    profile_overlap_question = "KOL" in question and "粉丝画像" in question and "目标用户" in question
    return profile_overlap_question and "无法" in answer and ("粉丝" in answer or "画像" in answer)


def execute_agent_request(
    capability: AgentCapability,
    message: str,
    event_id: str | None,
    history_items: list[DataQuestionHistoryItem],
    error_log: AgentErrorLog | None = None,
) -> dict:
    history = [item.model_dump() for item in history_items[-10:]]

    def fallback_response(error_reason: str) -> dict:
        if error_log:
            error_log.append(
                capability=str(capability),
                question=message,
                error_reason=error_reason,
                history=history,
            )
        if capability == "competitor_report":
            return {
                "status": "failed",
                "retryable": True,
                "answer": "竞品动态报告生成失败，请重试。",
                "report_type": "competitor_report",
                "brand_name": "",
                "time_scope": {},
                "scope_notice": [],
                "report_asset": None,
            }
        return {
            "status": "answered",
            "answer": "当前没有数据支撑，暂时无法反馈当前问题。这个问题已记录到系统管理的异常问题记录中，后续可用于补充数据或能力。",
            "suggested_questions": [],
            "requires_clarification": False,
            "event_name": "未确定",
            "time_scope": {},
            "data_scope": "当前可用数据不足",
            "react_rounds": 0,
        }

    try:
        result = dispatch_agent(capability, message, event_id=event_id, history=history)
        if error_log and has_insufficient_data_support(message, result.get("answer")):
            error_log.append(
                capability=str(capability),
                question=message,
                error_reason="insufficient data support",
                history=history,
            )
        return result
    except AgentCapabilityUnavailableError as exc:
        raise HTTPException(status_code=501, detail=str(exc))
    except ValueError as exc:
        return fallback_response(str(exc))
    except httpx.HTTPError as exc:
        return fallback_response(f"AI service request failed: {exc}")
    except psycopg.Error as exc:
        return fallback_response(f"PostgreSQL connection/query failed: {exc}")
    except Exception as exc:
        return fallback_response(str(exc))


@router.post("/api/agents/run")
def run_agent_api(payload: AgentRunRequest, request: Request) -> dict:
    return execute_agent_request(
        payload.capability,
        payload.message,
        None if payload.capability == "competitor_report" else payload.event_id,
        payload.history,
        get_agent_error_log(request),
    )


@router.post("/api/agents/data-question/run")
def run_data_question_agent_api(payload: DataQuestionAgentRunRequest, request: Request) -> dict:
    return execute_agent_request(
        "data_question",
        payload.question,
        payload.event_id,
        payload.history,
        get_agent_error_log(request),
    )


@router.get("/api/system/agent-error-questions")
def get_agent_error_questions(request: Request, limit: int = 100) -> dict:
    return get_agent_error_log(request).list(limit=limit)


@router.get("/api/assets/{asset_key}/export")
def export_assets(asset_key: str, q: str | None = None) -> StreamingResponse:
    try:
        payload = list_assets(asset_key, q=q, limit=EXPORT_LIMIT, offset=0, max_limit=EXPORT_LIMIT)
    except KeyError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    return excel_response(payload_to_dataframe(payload), f"{payload['label']}.xlsx")


@router.get("/api/assets/{asset_key}")
def get_assets(asset_key: str, q: str | None = None, limit: int = 50, offset: int = 0) -> dict:
    try:
        return list_assets(asset_key, q=q, limit=limit, offset=offset)
    except KeyError:
        raise HTTPException(status_code=404, detail="Asset not found")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/voc/events")
def get_voc_events(q: str | None = None, limit: int = 20) -> dict:
    try:
        return list_voc_events(q=q, limit=limit)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/voc/events/{event_id}/market-dashboard")
def get_voc_event_market_dashboard_api(event_id: str) -> dict:
    try:
        payload = get_voc_event_market_dashboard(event_id)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if not payload.get("event"):
        raise HTTPException(status_code=404, detail="Event not found")
    return payload


@router.get("/api/voc/events/{event_id}/product-dashboard")
def get_voc_event_product_dashboard_api(event_id: str) -> dict:
    try:
        payload = get_voc_event_product_dashboard(event_id)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if not payload.get("event"):
        raise HTTPException(status_code=404, detail="Event not found")
    return payload


@router.get("/api/voc/events/{event_id}/sales-dashboard")
def get_voc_event_sales_dashboard_api(event_id: str) -> dict:
    try:
        payload = get_voc_event_sales_dashboard(event_id)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if not payload.get("event"):
        raise HTTPException(status_code=404, detail="Event not found")
    return payload


@router.get("/api/voc/events/{event_id}/contents/{content_id}/detail")
def get_voc_event_content_detail_api(
    event_id: str,
    content_id: str,
    sort: str = "interaction",
    limit: int = 10,
    offset: int = 0,
) -> dict:
    try:
        payload = get_voc_event_content_detail(event_id, content_id, sort=sort, limit=limit, offset=offset)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if not payload.get("content"):
        raise HTTPException(status_code=404, detail="Content not found")
    return payload


@router.get("/api/voc/events/{event_id}/discussion-points/{aspect}/comments")
def get_voc_event_discussion_point_comments_api(
    event_id: str,
    aspect: str,
    limit: int = 20,
    offset: int = 0,
) -> dict:
    try:
        return get_voc_event_discussion_point_comments(event_id, aspect, limit=limit, offset=offset)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/voc/events/{event_id}/comment-users/{comment_user_id}/insight-profile")
def get_voc_event_comment_user_insight_profile_api(event_id: str, comment_user_id: str) -> dict:
    try:
        payload = get_voc_event_comment_user_insight_profile(event_id, comment_user_id)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if not payload.get("comments") and not payload.get("profile_summary", {}).get("main_label"):
        raise HTTPException(status_code=404, detail="Comment user not found")
    return payload


@router.get("/api/voc/authors/{author_id}/detail")
def get_voc_author_detail_api(author_id: str) -> dict:
    try:
        payload = get_voc_author_detail(author_id)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if not payload.get("author"):
        raise HTTPException(status_code=404, detail="Author not found")
    return payload


@router.get("/api/voc/events/{event_id}")
def get_voc_event(event_id: str) -> dict:
    try:
        payload = get_voc_event_detail(event_id)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if not payload.get("overview"):
        raise HTTPException(status_code=404, detail="Event not found")
    return payload


@router.get("/api/competitors/accounts/export")
def export_competitor_accounts(q: str | None = None) -> StreamingResponse:
    try:
        payload = list_competitor_accounts(q=q, limit=EXPORT_LIMIT, offset=0, max_limit=EXPORT_LIMIT)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    return excel_response(payload_to_dataframe(payload), "竞品账号库.xlsx")


@router.get("/api/competitors/accounts")
def get_competitor_accounts(q: str | None = None, limit: int = 50, offset: int = 0) -> dict:
    try:
        return list_competitor_accounts(q=q, limit=limit, offset=offset)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/competitors/works/export")
def export_competitor_works(
    q: str | None = None,
    brand_name: str | None = None,
    account_name: str | None = None,
    account_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
) -> StreamingResponse:
    try:
        payload = list_competitor_works(
            q=q,
            brand_name=brand_name,
            account_name=account_name,
            account_type=account_type,
            start_date=start_date,
            end_date=end_date,
            limit=EXPORT_LIMIT,
            offset=0,
            max_limit=EXPORT_LIMIT,
        )
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    return excel_response(payload_to_dataframe(payload), "竞品作品库.xlsx")


@router.get("/api/competitors/works")
def get_competitor_works(
    q: str | None = None,
    brand_name: str | None = None,
    account_name: str | None = None,
    account_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    try:
        return list_competitor_works(
            q=q,
            brand_name=brand_name,
            account_name=account_name,
            account_type=account_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/assets/reports/{report_type}/{report_run_id}")
def get_report_asset_api(report_type: str, report_run_id: int) -> dict:
    if report_type not in {"event_report", "competitor_report"} or report_run_id <= 0:
        raise HTTPException(status_code=404, detail="Report not found")
    try:
        report = get_report_asset(report_type, report_run_id)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/api/competitors/works/{work_id}/insight")
def get_competitor_work_insight_api(work_id: str) -> dict:
    try:
        return get_competitor_work_insight(work_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.put("/api/competitors/works/{work_id}/insight")
def save_competitor_work_insight_api(work_id: str, payload: CompetitorWorkInsightSaveRequest) -> dict:
    try:
        return save_competitor_work_insight(work_id, payload.insight_markdown, payload.updated_by)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.delete("/api/competitors/works/{work_id}/insight")
def clear_competitor_work_insight_api(work_id: str) -> dict:
    try:
        return save_competitor_work_insight(work_id, "")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/competitors/options")
def get_competitor_filter_options() -> dict:
    try:
        return get_competitor_options()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/profiles/kols/samples/export")
def export_kol_samples(days: int = 7) -> StreamingResponse:
    try:
        dataframe = export_kol_profile_samples(days=days)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    return excel_response(dataframe, f"KOL近{days}日发帖样本.xlsx")


@router.post("/api/profiles/kols/upload")
def upload_kol_profiles(profile_file: Annotated[UploadFile, File()]) -> dict:
    temp_path = save_temp_upload(profile_file)
    try:
        return load_kol_profiles(temp_path, source_file_name=profile_file.filename or "kol_profile.xlsx")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI画像调用超时，请调大 PROFILE_AI_TIMEOUT_SECONDS 或稍后重试。")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"AI画像服务返回异常：{exc.response.status_code} {exc.response.text[:300]}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"AI画像服务调用失败：{exc}")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    finally:
        temp_path.unlink(missing_ok=True)


@router.get("/api/profiles/kols")
def get_kol_profiles(q: str | None = None, profile_batch: str | None = None, limit: int = 50, offset: int = 0) -> dict:
    try:
        return list_kol_profiles(q=q, profile_batch=profile_batch, limit=limit, offset=offset)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/profiles/kols/batches")
def get_kol_batches() -> dict:
    try:
        return {"batches": get_kol_profile_batches()}
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/profiles/comment-users/samples/export")
def export_comment_user_samples() -> StreamingResponse:
    try:
        dataframe = export_comment_user_profile_samples()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    return excel_response(dataframe, "评论用户画像样本.xlsx")


@router.post("/api/profiles/comment-users/upload")
def upload_comment_user_profiles(profile_file: Annotated[UploadFile, File()]) -> dict:
    temp_path = save_temp_upload(profile_file)
    try:
        return load_comment_user_profiles(temp_path, source_file_name=profile_file.filename or "comment_user_profile.xlsx")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI画像调用超时，请调大 PROFILE_AI_TIMEOUT_SECONDS 或稍后重试。")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"AI画像服务返回异常：{exc.response.status_code} {exc.response.text[:300]}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"AI画像服务调用失败：{exc}")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")
    finally:
        temp_path.unlink(missing_ok=True)


@router.post("/api/profiles/comment-users/{comment_user_id}/ai-run")
def run_comment_user_ai_profile_api(comment_user_id: str, payload: CommentUserAiProfileRunRequest) -> dict:
    try:
        return run_comment_user_ai_profile(
            comment_user_id,
            profile_batch=payload.profile_batch,
            prompt_version=payload.prompt_version,
            prompt_path=resolve_project_prompt_path(payload.prompt_file) if payload.prompt_file else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI画像调用超时，请调大 PROFILE_AI_TIMEOUT_SECONDS 或稍后重试。")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"AI画像服务返回异常：{exc.response.status_code} {exc.response.text[:300]}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"AI画像服务调用失败：{exc}")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.post("/api/voc/events/{event_id}/market/report-agent/run")
def run_market_report_agent_api(event_id: str) -> dict:
    try:
        return run_market_report_agent(event_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI市场摘要调用超时，请检查模型服务或稍后重试。")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"AI市场摘要服务返回异常：{exc.response.status_code} {exc.response.text[:300]}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"AI市场摘要服务调用失败：{exc}")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/voc/events/{event_id}/market/report-agent/latest")
def get_latest_market_report_agent_api(event_id: str) -> dict:
    try:
        latest = get_latest_market_report_agent_result(event_id)
        if latest is None:
            raise HTTPException(status_code=404, detail="No cached market report found.")
        return latest
    except HTTPException:
        raise
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.post("/api/voc/events/{event_id}/product/report-agent/run")
def run_product_report_agent_api(event_id: str) -> dict:
    try:
        return run_product_report_agent(event_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI product report request timed out.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"AI product report service returned error: {exc.response.status_code} {exc.response.text[:300]}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"AI product report request failed: {exc}")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/voc/events/{event_id}/product/report-agent/latest")
def get_latest_product_report_agent_api(event_id: str) -> dict:
    try:
        latest = get_latest_product_report_agent_result(event_id)
        if latest is None:
            raise HTTPException(status_code=404, detail="No cached product report found.")
        return latest
    except HTTPException:
        raise
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.post("/api/voc/events/{event_id}/sales/report-agent/run")
def run_sales_report_agent_api(event_id: str) -> dict:
    try:
        return run_sales_report_agent(event_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI sales report request timed out.")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail=f"AI sales report service returned error: {exc.response.status_code} {exc.response.text[:300]}")
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"AI sales report request failed: {exc}")
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/voc/events/{event_id}/sales/report-agent/latest")
def get_latest_sales_report_agent_api(event_id: str) -> dict:
    try:
        latest = get_latest_sales_report_agent_result(event_id)
        if latest is None:
            raise HTTPException(status_code=404, detail="No cached sales report found.")
        return latest
    except HTTPException:
        raise
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/profiles/comment-users/ai-flow")
def get_comment_user_ai_profile_flow_api() -> dict:
    try:
        return build_comment_user_ai_flow()
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/profiles/comment-users")
def get_comment_user_profiles(
    q: str | None = None,
    profile_batch: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    try:
        return list_comment_user_profiles(q=q, profile_batch=profile_batch, limit=limit, offset=offset)
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/profiles/comment-users/batches")
def get_comment_user_batches() -> dict:
    try:
        return {"batches": get_comment_user_profile_batches()}
    except psycopg.Error as exc:
        raise HTTPException(status_code=503, detail=f"PostgreSQL connection/query failed: {exc}")


@router.get("/api/etl/flow")
def get_etl_flow(request: Request, batch_id: str | None = None) -> dict:
    summary = None
    if batch_id:
        try:
            summary = get_store(request).get_task(batch_id).get("summary", {})
        except KeyError:
            raise HTTPException(status_code=404, detail="Task not found")
    return {"nodes": build_flow_nodes(summary)}


@router.get("/api/etl/script")
def get_etl_script(request: Request) -> dict:
    return get_script_manager(request).read_script()


@router.put("/api/etl/script")
def save_etl_script(request: Request, payload: ScriptSaveRequest) -> dict:
    return get_script_manager(request).save_script(payload.content)


@router.post("/api/etl/script/test-run")
def test_run_etl_script(request: Request, payload: ScriptTestRunRequest) -> dict:
    try:
        get_store(request).get_task(payload.batch_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")
    return EtlRunner(get_store(request), get_script_manager(request).script_path).run_task(payload.batch_id)


@router.post("/api/tasks/upload")
def upload_task(
    request: Request,
    event_file: Annotated[UploadFile, File()],
    content_file: Annotated[UploadFile, File()],
    comment_file: Annotated[UploadFile, File()],
) -> dict:
    store = get_store(request)
    task = store.create_task(
        input_files={
            "event_upload": event_file.filename or "event_upload.xlsx",
            "content_upload": content_file.filename or "content_upload.xlsx",
            "comment_upload": comment_file.filename or "comment_upload.xlsx",
        }
    )
    input_dir = store.input_dir(task["batch_id"])
    save_upload(event_file, input_dir / f"event_upload{upload_suffix(event_file)}")
    save_upload(content_file, input_dir / f"content_upload{upload_suffix(content_file)}")
    save_upload(comment_file, input_dir / f"comment_upload{upload_suffix(comment_file)}")
    return task


@router.post("/api/tasks/{batch_id}/run")
def run_task(request: Request, batch_id: str) -> dict:
    try:
        return EtlRunner(get_store(request), get_script_manager(request).script_path).run_task(batch_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/api/tasks/{batch_id}")
def get_task(request: Request, batch_id: str) -> dict:
    try:
        return get_store(request).get_task(batch_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get("/api/tasks/{batch_id}/tables")
def list_task_tables(request: Request, batch_id: str) -> dict:
    store = get_store(request)
    output_dir = store.output_dir(batch_id)
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Task output not found")
    tables = sorted(path.stem for path in output_dir.glob("*.csv") if path.stem in ALLOWED_TABLES)
    return {"batch_id": batch_id, "tables": tables}


@router.get("/api/tasks/{batch_id}/tables/{table_name}")
def preview_task_table(request: Request, batch_id: str, table_name: str, limit: int = 50, offset: int = 0) -> dict:
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail="Table not found")
    table_path = get_store(request).output_dir(batch_id) / f"{table_name}.csv"
    if not table_path.exists():
        raise HTTPException(status_code=404, detail="Table not found")
    dataframe = pd.read_csv(table_path, encoding="utf-8-sig")
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    page = dataframe.iloc[offset : offset + limit].fillna("")
    return {
        "batch_id": batch_id,
        "table": table_name,
        "total": int(len(dataframe)),
        "columns": dataframe.columns.tolist(),
        "rows": page.to_dict(orient="records"),
    }


@router.get("/api/tasks/{batch_id}/tables/{table_name}/export")
def export_task_table(request: Request, batch_id: str, table_name: str) -> StreamingResponse:
    if table_name not in ALLOWED_TABLES:
        raise HTTPException(status_code=404, detail="Table not found")
    table_path = get_store(request).output_dir(batch_id) / f"{table_name}.csv"
    if not table_path.exists():
        raise HTTPException(status_code=404, detail="Table not found")
    dataframe = pd.read_csv(table_path, encoding="utf-8-sig").fillna("")
    return excel_response(dataframe, f"{batch_id}_{table_name}.xlsx")


@router.get("/api/templates/{template_name}")
def download_template(template_name: str) -> FileResponse:
    if template_name not in ALLOWED_TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template not found")
    return FileResponse(template_path, filename=template_name)
