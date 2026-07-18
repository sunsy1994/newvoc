from __future__ import annotations

import re
from datetime import date, datetime, time

from app.agents.qa.time_scope_resolver import SHANGHAI_TZ, resolve_time_scope


DEFAULT_BRAND = "上汽大众"
BRAND_AFTER_LABEL = re.compile(r"品牌\s*(?:是|为|[:：])\s*(?P<brand>[A-Za-z0-9\u4e00-\u9fff·-]{2,20})")
BRAND_BEFORE_LABEL = re.compile(r"(?P<brand>[A-Za-z0-9\u4e00-\u9fff·-]{2,20})品牌")
BRAND_BEFORE_REPORT = re.compile(r"(?P<brand>[^，,。；;：:\s]{2,30}?)(?:的)?竞品(?:动态)?报告")
TIME_TEXT = re.compile(
    r"\d{4}-\d{2}-\d{2}\s*(?:到|至|~|—|–)\s*\d{4}-\d{2}-\d{2}"
    r"|(?:最近|近)[一二三四五六七八九十两俩\d]*(?:天|日|周|个月|月|年)"
    r"|(?:今天|今日|昨天|昨日|本周|这周|上周|本月|这个月|上月|上个月)"
)
LEADING_REQUEST = re.compile(
    r"^(?:我想看|我想要|请|帮我|帮忙|给我|生成|制作|出|查看|看看|分析|想看|想要|需要|关于|来)"
    r"(?:一份|一下|一个|个)?"
)
GENERIC_REPORT_MODIFIERS = {"详细", "完整", "最新", "近期", "本期", "这个", "相关", "动态", "竞品", "报告"}


def _clean_brand_candidate(value: str) -> str:
    candidate = TIME_TEXT.sub("", value)
    candidate = re.split(r"(?:的)?(?:竞品|报告)", candidate, maxsplit=1)[0].strip("，,。；;：: 的")
    while True:
        cleaned = LEADING_REQUEST.sub("", candidate).strip("，,。；;：: 的")
        if cleaned == candidate:
            break
        candidate = cleaned
    return candidate


def _resolve_brand(message: str) -> tuple[str, bool]:
    for pattern in (BRAND_AFTER_LABEL, BRAND_BEFORE_LABEL):
        match = pattern.search(message)
        if not match:
            continue
        candidate = _clean_brand_candidate(match.group("brand"))
        if candidate:
            return candidate, False
    match = BRAND_BEFORE_REPORT.search(message)
    if match:
        candidate = _clean_brand_candidate(match.group("brand"))
        if candidate and candidate not in GENERIC_REPORT_MODIFIERS:
            return candidate, False
    return DEFAULT_BRAND, True


def resolve_competitor_report_scope(message: str, today: date | None = None) -> dict[str, str | bool]:
    anchor = today or datetime.now(SHANGHAI_TZ).date()
    if isinstance(anchor, datetime):
        anchor = anchor.date()
    asked_at = datetime.combine(anchor, time.min, tzinfo=SHANGHAI_TZ)
    time_scope = resolve_time_scope(message, asked_at=asked_at)
    brand_name, brand_defaulted = _resolve_brand(message)
    return {
        "brand_name": brand_name,
        "brand_defaulted": brand_defaulted,
        "start_date": time_scope["start_date"],
        "end_date": time_scope["end_date"],
        "time_defaulted": time_scope["mode"] == "default_30_days",
    }
