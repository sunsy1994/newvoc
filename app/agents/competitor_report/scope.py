from __future__ import annotations

import re
from datetime import date, datetime, time

from app.agents.qa.time_scope_resolver import SHANGHAI_TZ, resolve_time_scope


DEFAULT_BRAND = "上汽大众"
BRAND_CHARS = r"[A-Za-z0-9\u4e00-\u9fff·-]"
BRAND_WITHOUT_DE = r"(?:(?!的)[A-Za-z0-9\u4e00-\u9fff·-])"
TIME_BOUNDARY = (
    r"\d{4}-\d{2}-\d{2}\s*(?:到|至|~|—|–)\s*\d{4}-\d{2}-\d{2}"
    r"|(?:最近|近)[一二三四五六七八九十两俩\d]*(?:天|日|周|个月|月|年)"
    r"|(?:今天|今日|昨天|昨日|本周|这周|上周|本月|这个月|上月|上个月)"
)
BRAND_AFTER_LABEL = re.compile(
    rf"品牌\s*(?:是|为|[:：])\s*(?P<brand>{BRAND_CHARS}{{2,20}}?)"
    rf"(?={TIME_BOUNDARY}|(?:的)?竞品(?:动态)?报告|[，,。；;：:\s]|$)"
)
BRAND_BEFORE_LABEL = re.compile(rf"^(?P<brand>{BRAND_CHARS}{{2,20}})品牌")
BRAND_BEFORE_REPORT = re.compile(rf"^(?P<brand>{BRAND_WITHOUT_DE}{{2,20}})竞品(?:动态)?报告")
REQUEST_PREFIX = re.compile(
    r"^(?:(?:请|麻烦)?(?:帮我|帮忙|给我)(?:做|输出|生成|制作|出|查看|看看|分析)?"
    r"|(?:请|麻烦)?(?:做|输出|生成|制作|出|查看|看看|分析)"
    r"|我想(?:看|要)|想(?:看|要)|需要|关于|来)"
    r"(?:一份|一下|一个|个)?"
)


def _resolve_brand(message: str) -> tuple[str, bool]:
    labeled = BRAND_AFTER_LABEL.search(message)
    if labeled:
        return labeled.group("brand"), False

    report_request = REQUEST_PREFIX.sub("", message, count=1).strip()
    for pattern in (BRAND_BEFORE_LABEL, BRAND_BEFORE_REPORT):
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
