from pathlib import Path

from .config import BASE_DIR


TASKS = [
    {
        "task_id": "customer_touchpoint_standardize",
        "task_name": "用户旅程触点标准化",
        "task_group": "用户旅程",
        "task_desc": "将公网评论和已导入业务触点统一到 dwd_customer_touchpoint。",
        "script_path": "backend/app/tasks/customer_touchpoint_standardize.py",
        "module_path": "backend.app.tasks.customer_touchpoint_standardize",
        "entry_func": "run",
        "input_tables": ["dwd_comment", "rel_event_content", "dwd_event", "dwd_customer_touchpoint"],
        "output_tables": ["dwd_customer_touchpoint"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "journey_stage_summary",
        "task_name": "用户旅程阶段汇总",
        "task_group": "用户旅程",
        "task_desc": "按品牌、车型和旅程阶段聚合触点量、渠道数、负向占比和代表样本。",
        "script_path": "backend/app/tasks/journey_stage_summary.py",
        "module_path": "backend.app.tasks.journey_stage_summary",
        "entry_func": "run",
        "input_tables": ["dwd_customer_touchpoint"],
        "output_tables": ["ads_journey_stage_summary"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "journey_channel_matrix",
        "task_name": "用户旅程渠道矩阵",
        "task_group": "用户旅程",
        "task_desc": "按渠道和旅程阶段聚合触点量、负向占比、问题和意图标签。",
        "script_path": "backend/app/tasks/journey_channel_matrix.py",
        "module_path": "backend.app.tasks.journey_channel_matrix",
        "entry_func": "run",
        "input_tables": ["dwd_customer_touchpoint"],
        "output_tables": ["ads_journey_channel_matrix"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "journey_painpoint_summary",
        "task_name": "用户旅程痛点汇总",
        "task_group": "用户旅程",
        "task_desc": "按旅程阶段和问题标签聚合痛点，并生成部门负责人和动作建议。",
        "script_path": "backend/app/tasks/journey_painpoint_summary.py",
        "module_path": "backend.app.tasks.journey_painpoint_summary",
        "entry_func": "run",
        "input_tables": ["dwd_customer_touchpoint"],
        "output_tables": ["ads_journey_painpoint_summary"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "event_asset_overview",
        "task_name": "事件资产概览计算",
        "task_group": "汇总指标",
        "task_desc": "按事件聚合内容数、评论数、作者数、KOL数，输出事件库概览表。",
        "script_path": "backend/app/tasks/event_asset_overview.py",
        "module_path": "backend.app.tasks.event_asset_overview",
        "entry_func": "run",
        "input_tables": ["dwd_event", "dwd_content", "dwd_comment", "rel_event_content"],
        "output_tables": ["ads_event_asset_overview"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "author_event_summary",
        "task_name": "作者事件汇总计算",
        "task_group": "汇总指标",
        "task_desc": "按作者和事件聚合发文数、互动量、评论触发量，供作者库展示。",
        "script_path": "backend/app/tasks/author_event_summary.py",
        "module_path": "backend.app.tasks.author_event_summary",
        "entry_func": "run",
        "input_tables": [
            "dwd_content",
            "dwd_comment",
            "dwd_account",
            "rel_event_content",
            "fact_content_comment_profile_di",
            "ads_content_value_summary",
        ],
        "output_tables": ["ads_author_event_summary"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "event_trend_daily",
        "task_name": "事件趋势日表计算",
        "task_group": "趋势指标",
        "task_desc": "按事件与日期聚合内容数、评论数、互动量和负向评论数，供事件详情趋势图查询。",
        "script_path": "backend/app/tasks/event_trend_daily.py",
        "module_path": "backend.app.tasks.event_trend_daily",
        "entry_func": "run",
        "input_tables": ["dwd_content", "dwd_comment", "rel_event_content"],
        "output_tables": ["ads_event_trend_daily"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "content_comment_profile",
        "task_name": "内容评论结构计算",
        "task_group": "评论画像",
        "task_desc": "按内容聚合评论数、高置信评论占比、阶段分布和态度分布等评论结构信息。",
        "script_path": "backend/app/tasks/content_comment_profile.py",
        "module_path": "backend.app.tasks.content_comment_profile",
        "entry_func": "run",
        "input_tables": ["dwd_comment", "rel_event_content"],
        "output_tables": ["fact_content_comment_profile_di"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "content_value_summary",
        "task_name": "内容价值汇总计算",
        "task_group": "内容价值",
        "task_desc": "结合内容基础表现和评论结构，计算内容角色、价值等级、价值标记与代表性评论。",
        "script_path": "backend/app/tasks/content_value_summary.py",
        "module_path": "backend.app.tasks.content_value_summary",
        "entry_func": "run",
        "input_tables": ["dwd_content", "dwd_comment", "rel_event_content", "fact_content_comment_profile_di"],
        "output_tables": ["ads_content_value_summary"],
        "run_mode": "manual",
        "is_enabled": True,
    },
    {
        "task_id": "kol_event_summary",
        "task_name": "KOL事件汇总计算",
        "task_group": "KOL画像",
        "task_desc": "按KOL与事件聚合发文数、总互动、篇均互动和高置信评论占比。",
        "script_path": "backend/app/tasks/kol_event_summary.py",
        "module_path": "backend.app.tasks.kol_event_summary",
        "entry_func": "run",
        "input_tables": [
            "dwd_account",
            "dwd_content",
            "dwd_comment",
            "rel_event_content",
            "fact_content_comment_profile_di",
        ],
        "output_tables": ["ads_kol_event_summary"],
        "run_mode": "manual",
        "is_enabled": True,
    },
]


def list_calc_tasks() -> list[dict]:
    return [dict(item) for item in TASKS]


def get_calc_task(task_id: str) -> dict | None:
    return next((dict(item) for item in TASKS if item["task_id"] == task_id), None)


def read_script_content(task: dict) -> str:
    script_path = (BASE_DIR.parent / task["script_path"]).resolve()
    if not script_path.exists():
        return "# script file not found\n"
    return script_path.read_text(encoding="utf-8")
