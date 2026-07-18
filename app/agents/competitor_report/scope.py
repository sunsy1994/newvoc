from __future__ import annotations

import re
from datetime import date, datetime, time

from app.agents.qa.time_scope_resolver import SHANGHAI_TZ, resolve_time_scope


DEFAULT_BRAND = "上汽大众"
BRAND_CHARS = r"[A-Za-z0-9\u4e00-\u9fff·-]"
TIME_BOUNDARY = (
    r"\d{4}-\d{2}-\d{2}\s*(?:到|至|~|—|–)\s*\d{4}-\d{2}-\d{2}"
    r"|(?:最近|近)[一二三四五六七八九十两俩\d]*(?:天|日|周|个月|月|年)"
    r"|(?:今天|今日|昨天|昨日|本周|这周|上周|本月|这个月|上月|上个月)"
)
BRAND_AFTER_LABEL = re.compile(
    rf"品牌\s*(?:是|为|[:：])\s*(?P<brand>{BRAND_CHARS}{{2,20}}?)"
    rf"(?={TIME_BOUNDARY}|(?:的)?竞品(?:动态)?报告|[，,。；;：:\s]|$)"
)
BRAND_SUFFIX = re.compile(
    rf"^(?P<brand>{BRAND_CHARS}{{2,20}})品牌"
    rf"(?={TIME_BOUNDARY}|(?:的)?竞品(?:动态)?报告|[，,。；;：:\s]|$)"
)
BRAND_POSSESSIVE_REPORT = re.compile(
    rf"^(?!(?:{TIME_BOUNDARY})的竞品)(?P<brand>{BRAND_CHARS}{{3,20}})的竞品(?:动态)?报告"
)
REPORT_REQUEST_OPENING = re.compile(r"^(?:[^，,。；;：:\s]{0,20}?一份|生成)")


def _resolve_brand(message: str) -> tuple[str, bool]:
    labeled = BRAND_AFTER_LABEL.search(message)
    if labeled:
        return labeled.group("brand"), False

    report_request = REPORT_REQUEST_OPENING.sub("", message, count=1).strip()
    for pattern in (BRAND_SUFFIX, BRAND_POSSESSIVE_REPORT):
        match = pattern.match(report_request)
        if match:
            return match.group("brand"), False
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
