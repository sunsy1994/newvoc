from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from .config import settings
from .author_asset_service import AuthorAssetError, list_author_assets
from .comment_asset_service import CommentAssetError, list_comment_assets
from .content_asset_service import ContentAssetError, list_content_assets
from .event_asset_service import (
    EventAssetError,
    get_event_asset_detail,
    get_event_asset_trend,
    list_event_assets,
)
from .kol_asset_service import KOLAssetError, list_kol_assets
from .journey_service import (
    JourneyError,
    get_journey_matrix,
    get_journey_overview,
    list_journey_painpoints,
    list_journey_touchpoints,
)
from .import_service import ImportValidationError, process_import
from .job_store import list_jobs
from .schemas import (
    DataAccessOverviewResponse,
    ContentAssetListResponse,
    CommentAssetListResponse,
    DataSourceStatus,
    EventAssetDetail,
    EventAssetListResponse,
    EventTrendPoint,
    AuthorAssetListResponse,
    JourneyMatrixCell,
    JourneyOverviewResponse,
    JourneyPainpointItem,
    JourneyTouchpointListResponse,
    KOLAssetListResponse,
    OverviewCard,
    PostgresInfo,
)
from .task_service import build_graph, get_task_detail, list_tasks_with_state, run_task, TaskExecutionError
from .template_registry import get_template, list_templates


router = APIRouter()


@router.get("/data-access/overview", response_model=DataAccessOverviewResponse)
def get_overview():
    templates = list_templates()
    jobs = list_jobs()
    sources = [
        DataSourceStatus(
            id=f"src-{item['source_key']}",
            name=f"{item['source_name']}接入源",
            type="text" if "txt" in item["formats"] else "excel",
            owner="本地维护",
            status="ready" if item["exists"] else "pending",
            last_sync_at=jobs[0].updated_at.strftime("%Y-%m-%d %H:%M") if jobs else "-",
            record_count=max((job.inserted_rows for job in jobs if job.source_key == item["source_key"]), default=0),
            template_id=item["id"],
            target_table=item["target_table"],
        )
        for item in templates
    ]
    summary = [
        OverviewCard(id="sources", label="数据源", value=str(len(sources)), hint="Excel / 文本统一进站", tone="blue"),
        OverviewCard(id="templates", label="导入模板", value=str(len(templates)), hint="一类数据源一个模板", tone="emerald"),
        OverviewCard(id="jobs", label="导入任务", value=str(len(jobs)), hint="记录校验和入库状态", tone="amber"),
        OverviewCard(id="targets", label="目标主表", value="8", hint="PostgreSQL 标准化落库", tone="slate"),
    ]
    postgres = PostgresInfo(
        schema_name="data_asset",
        current_database=settings.database_url or "not-configured",
        tables=[
            "dwd_event",
            "dwd_content",
            "dwd_comment",
            "dwd_account",
            "rel_event_content",
            "fact_content_tag",
            "fact_comment_tag",
            "ads_event_asset_overview",
        ],
        key_interfaces=[
            "GET /api/data-access/overview",
            "GET /api/data-import/templates",
            "GET /api/data-import/jobs",
            "POST /api/data-import/jobs",
            "GET /api/data-import/templates/:templateId/download",
        ],
    )
    return DataAccessOverviewResponse(
        summary=summary,
        sources=sources,
        templates=templates,
        jobs=jobs,
        postgres=postgres,
    )


@router.get("/data-import/templates")
def get_templates():
    return list_templates()


@router.get("/data-import/templates/{template_id}/download")
def download_template(template_id: str):
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    path = Path(settings.template_dir) / template["file_name"]
    if not path.exists():
        raise HTTPException(status_code=404, detail="Template file not found")
    media_type = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        if path.suffix.lower() == ".xlsx"
        else "text/csv"
    )
    return FileResponse(path, filename=template["file_name"], media_type=media_type)


@router.get("/data-import/jobs")
def get_jobs():
    return list_jobs()


@router.post("/data-import/jobs")
async def create_job(
    source_key: str = Form(...),
    template_id: str = Form(...),
    operator: str = Form(...),
    file: UploadFile = File(...),
):
    try:
        return await process_import(
            source_key=source_key,
            template_id=template_id,
            operator=operator,
            upload_file=file,
        )
    except ImportValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/data-calc/graph")
def get_calc_graph():
    return build_graph()


@router.get("/data-calc/tasks")
def get_calc_tasks():
    return list_tasks_with_state()


@router.get("/data-calc/tasks/{task_id}")
def get_calc_task(task_id: str):
    try:
        return get_task_detail(task_id)
    except TaskExecutionError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/data-calc/tasks/{task_id}/run")
def post_calc_task_run(task_id: str):
    try:
        return run_task(task_id)
    except TaskExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/journey/overview", response_model=JourneyOverviewResponse)
def get_journey_overview_api(brand_name: str | None = None, model_name: str | None = None):
    try:
        return get_journey_overview(brand_name=brand_name, model_name=model_name)
    except JourneyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/journey/matrix", response_model=list[JourneyMatrixCell])
def get_journey_matrix_api(brand_name: str | None = None, model_name: str | None = None):
    try:
        return get_journey_matrix(brand_name=brand_name, model_name=model_name)
    except JourneyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/journey/touchpoints", response_model=JourneyTouchpointListResponse)
def get_journey_touchpoints_api(
    stage: str | None = None,
    channel: str | None = None,
    brand_name: str | None = None,
    model_name: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    try:
        return list_journey_touchpoints(
            stage=stage,
            channel=channel,
            brand_name=brand_name,
            model_name=model_name,
            page=page,
            page_size=page_size,
        )
    except JourneyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/journey/painpoints", response_model=list[JourneyPainpointItem])
def get_journey_painpoints_api(brand_name: str | None = None, model_name: str | None = None):
    try:
        return list_journey_painpoints(brand_name=brand_name, model_name=model_name)
    except JourneyError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/assets/events", response_model=EventAssetListResponse)
def get_event_assets(
    keyword: str | None = None,
    event_type: str | None = None,
    event_status: str | None = None,
    brand_name: str | None = None,
    platform: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = "updatedAt",
    sort_order: str = "desc",
    page: int = 1,
    page_size: int = 50,
):
    try:
        return list_event_assets(
            keyword=keyword,
            event_type=event_type,
            event_status=event_status,
            brand_name=brand_name,
            platform=platform,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            page_size=page_size,
        )
    except EventAssetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/assets/events/{event_id}", response_model=EventAssetDetail)
def get_event_asset(event_id: str):
    try:
        return get_event_asset_detail(event_id)
    except EventAssetError as exc:
        status = 404 if "not found" in str(exc).lower() else 503
        raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.get("/assets/events/{event_id}/trend", response_model=list[EventTrendPoint])
def get_event_asset_daily_trend(event_id: str):
    try:
        return get_event_asset_trend(event_id)
    except EventAssetError as exc:
        status = 404 if "not found" in str(exc).lower() else 503
        raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.get("/assets/contents", response_model=ContentAssetListResponse)
def get_content_assets(event_id: str | None = None):
    try:
        return list_content_assets(event_id=event_id)
    except ContentAssetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/assets/comments", response_model=CommentAssetListResponse)
def get_comment_assets(event_id: str | None = None):
    try:
        return list_comment_assets(event_id=event_id)
    except CommentAssetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/assets/authors", response_model=AuthorAssetListResponse)
def get_author_assets(event_id: str | None = None, include_kol: bool = True):
    try:
        return list_author_assets(event_id=event_id, include_kol=include_kol)
    except AuthorAssetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/assets/kols", response_model=KOLAssetListResponse)
def get_kol_assets(event_id: str | None = None):
    try:
        return list_kol_assets(event_id=event_id)
    except KOLAssetError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
