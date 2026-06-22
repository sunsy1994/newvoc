from __future__ import annotations

from typing import Any


FLOW_NODES = [
    {
        "id": "upload",
        "title": "原始上传文件",
        "desc": "使用者上传事件、内容、评论三张原始文件。",
        "input_tables": ["event_upload.xlsx/csv", "content_upload.xlsx/csv", "comment_upload.xlsx/csv"],
        "output_tables": ["ods_event_upload", "ods_content_upload", "ods_comment_upload"],
        "rules": ["保留原始字段", "缺失的可选字段置空", "按模板字段映射为英文列名"],
        "function_name": "read_upload",
        "metric_keys": ["ods_event_upload", "ods_content_upload", "ods_comment_upload"],
    },
    {
        "id": "ods",
        "title": "ODS 原始层",
        "desc": "将上传文件转成可追溯的原始数据层。",
        "input_tables": ["上传文件"],
        "output_tables": ["ods_event_upload", "ods_content_upload", "ods_comment_upload"],
        "rules": ["记录导入批次", "记录来源文件", "保留原始行号"],
        "function_name": "read_upload",
        "metric_keys": ["ods_event_upload", "ods_content_upload", "ods_comment_upload"],
    },
    {
        "id": "validate",
        "title": "字段校验",
        "desc": "检查必填字段是否具备，提前暴露模板和清洗问题。",
        "input_tables": ["ods_event_upload", "ods_content_upload", "ods_comment_upload"],
        "output_tables": ["校验错误信息"],
        "rules": ["事件名、事件类型必填", "内容链接、标题、发布时间必填", "评论正文、评论时间必填"],
        "function_name": "validate_required",
        "metric_keys": ["rejected_content", "rejected_comment"],
    },
    {
        "id": "standardize_event",
        "title": "事件标准化",
        "desc": "把原始事件整理为稳定事件主表。",
        "input_tables": ["ods_event_upload"],
        "output_tables": ["dwd_event"],
        "rules": ["优先沿用 raw_event_id", "缺失时按事件自然字段生成 event_id", "统一事件状态和时间字段"],
        "function_name": "standardize_events",
        "metric_keys": ["dwd_event"],
    },
    {
        "id": "standardize_content_author",
        "title": "内容与作者标准化",
        "desc": "把帖子和作者拆成内容资产与作者资产。",
        "input_tables": ["ods_content_upload", "dwd_event"],
        "output_tables": ["dwd_content", "dwd_author", "rel_event_content", "rel_author_content"],
        "rules": ["内容按 platform + source_url 去重", "作者按主页或平台昵称去重", "互动量由点赞、评论、分享、收藏生成"],
        "function_name": "standardize_content",
        "metric_keys": ["dwd_content", "dwd_author", "rel_event_content", "rel_author_content", "rejected_content"],
    },
    {
        "id": "standardize_comment",
        "title": "评论标准化",
        "desc": "把评论挂到内容上，形成 VOC 原声明细。",
        "input_tables": ["ods_comment_upload", "dwd_content"],
        "output_tables": ["dwd_comment"],
        "rules": [
            "优先用 content_source_url 匹配内容",
            "评论 ID 缺失时生成稳定 ID",
            "位置字段原样保留用于分布统计",
            "comment_label_json 原样保留用于评论质量分析",
        ],
        "function_name": "standardize_comments",
        "metric_keys": ["dwd_comment", "rejected_comment"],
    },
    {
        "id": "ads",
        "title": "ADS 指标聚合",
        "desc": "生成事件总览、趋势、排行和位置分布。",
        "input_tables": ["dwd_event", "dwd_content", "dwd_author", "dwd_comment"],
        "output_tables": ["ads_event_overview", "ads_event_trend_daily", "ads_event_content_rank", "ads_event_location_distribution"],
        "rules": ["按事件聚合内容数和评论数", "按日期聚合趋势", "按互动和评论量生成排行", "按评论位置生成分布"],
        "function_name": "build_ads",
        "metric_keys": ["ads_event_overview", "ads_event_trend_daily", "ads_event_content_rank", "ads_event_location_distribution"],
    },
    {
        "id": "postgres_load",
        "title": "PostgreSQL 落库",
        "desc": "把本批次 ETL 输出写入 data_asset schema。",
        "input_tables": ["ETL CSV 输出"],
        "output_tables": ["data_asset.*"],
        "rules": ["ODS 按批次写入", "DWD/REL/ADS 按主键 upsert", "rejected 行以 JSONB 保留"],
        "function_name": "load_etl_outputs",
        "metric_keys": ["dwd_event", "dwd_content", "dwd_comment", "ads_event_overview"],
    },
]


def build_flow_nodes(summary: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    summary = summary or {}
    nodes = []
    for index, node in enumerate(FLOW_NODES, start=1):
        metrics = {key: summary[key] for key in node["metric_keys"] if key in summary}
        nodes.append({**node, "order": index, "metrics": metrics})
    return nodes
