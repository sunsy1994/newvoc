from __future__ import annotations

import calendar
import re
from datetime import date, datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from app.agents.qa import time_slice


SHANGHAI_TZ = ZoneInfo("Asia/Shanghai")
EXPLICIT_RANGE_PATTERN = re.compile(
    r"(?P<start>\d{4}-\d{2}-\d{2})\s*(?:到|至|~|—|–)\s*(?P<end>\d{4}-\d{2}-\d{2})"
)
RELATIVE_RANGE_PATTERN = re.compile(r"近(?P<count>[一二三四五六七八九十两俩\d]+)?(?P<unit>天|日|周|个月|月|年)")
NAMED_MONTH_PATTERN = re.compile(r"(?<!\d)(?P<month>1[0-2]|0?[1-9])月")
NAMED_MONTH_LAST_WEEK_PATTERN = re.compile(
    r"(?:(?P<year>\d{4})年)?(?P<month>1[0-2]|0?[1-9])月最后一(?:周|星期)"
)


def _date_text(value: Any) -> str:
    return str(value or "")[:10]


def _chinese_number(value: str | None) -> int:
    text = str(value or "一")
    if text.isdigit():
        return int(text)
    digits = {"一": 1, "二": 2, "两": 2, "俩": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
    if text == "十":
        return 10
    if text.startswith("十"):
        return 10 + digits.get(text[1:], 0)
    if "十" in text:
        left, right = text.split("十", 1)
        return digits.get(left, 0) * 10 + digits.get(right, 0)
    return digits.get(text, 1)


def _anchor_date(asked_at: datetime | None) -> date:
    anchor = asked_at or datetime.now(SHANGHAI_TZ)
    if anchor.tzinfo is None:
        anchor = anchor.replace(tzinfo=SHANGHAI_TZ)
    return anchor.astimezone(SHANGHAI_TZ).date()


def _scope(
    *,
    mode: str,
    start: date,
    end: date,
    label_suffix: str,
    source: str | None = None,
    anchor: date | None = None,
) -> dict[str, str]:
    payload = {
        "mode": mode,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "label": f"{start.isoformat()} 至 {end.isoformat()}（{label_suffix}）",
    }
    if source:
        payload["source"] = source
    if anchor:
        payload["anchor_date"] = anchor.isoformat()
    return payload


def _shift_months(value: date, months: int) -> date:
    month_index = value.year * 12 + value.month - 1 - months
    year = month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def _shift_years(value: date, years: int) -> date:
    year = value.year - years
    day = min(value.day, calendar.monthrange(year, value.month)[1])
    return date(year, value.month, day)


def _relative_scope(question: str, anchor: date) -> dict[str, str] | None:
    if "今天" in question or "今日" in question:
        return _scope(mode="relative", start=anchor, end=anchor, label_suffix="用户指定今天", source="user_relative_phrase", anchor=anchor)
    if "昨天" in question or "昨日" in question:
        day = anchor - timedelta(days=1)
        return _scope(mode="relative", start=day, end=day, label_suffix="用户指定昨天", source="user_relative_phrase", anchor=anchor)
    if "本周" in question or "这周" in question:
        start = anchor - timedelta(days=anchor.weekday())
        return _scope(mode="relative", start=start, end=anchor, label_suffix="用户指定本周，截至提问日", source="user_relative_phrase", anchor=anchor)
    if "上周" in question:
        this_week_start = anchor - timedelta(days=anchor.weekday())
        start = this_week_start - timedelta(days=7)
        return _scope(mode="relative", start=start, end=start + timedelta(days=6), label_suffix="用户指定上周", source="user_relative_phrase", anchor=anchor)
    if "本月" in question or "这个月" in question:
        return _scope(mode="relative", start=anchor.replace(day=1), end=anchor, label_suffix="用户指定本月，截至提问日", source="user_relative_phrase", anchor=anchor)
    if "上月" in question or "上个月" in question:
        first_day = anchor.replace(day=1)
        end = first_day - timedelta(days=1)
        return _scope(mode="relative", start=end.replace(day=1), end=end, label_suffix="用户指定上月", source="user_relative_phrase", anchor=anchor)

    relative = RELATIVE_RANGE_PATTERN.search(question)
    if not relative:
        return None
    count_text = relative.group("count")
    unit = relative.group("unit")
    count = max(1, min(_chinese_number(count_text), 365))
    if unit in {"天", "日"}:
        start = anchor - timedelta(days=count - 1)
        suffix = f"提问时点近{count_text or ''}{unit}"
    elif unit == "周":
        start = anchor - timedelta(days=count * 7 - 1)
        suffix = f"提问时点近{count_text or ''}{unit}"
    elif unit in {"个月", "月"}:
        start = _shift_months(anchor, min(count, 120))
        suffix = f"提问时点近{count_text or ''}{unit}，按自然月"
    else:
        start = _shift_years(anchor, min(count, 20))
        suffix = f"提问时点近{count_text or ''}{unit}"
    return _scope(mode="relative", start=start, end=anchor, label_suffix=suffix, source="user_relative_phrase", anchor=anchor)


def _named_month_scope(question: str, anchor: date) -> dict[str, str] | None:
    match = NAMED_MONTH_PATTERN.search(question)
    if not match:
        return None
    month = int(match.group("month"))
    year = anchor.year if month <= anchor.month else anchor.year - 1
    start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    if year == anchor.year and month == anchor.month:
        end = min(end, anchor)
    return _scope(mode="named_month", start=start, end=end, label_suffix=f"用户指定{month}月", source="user_month_phrase", anchor=anchor)


def _named_month_last_week_scope(question: str, anchor: date) -> dict[str, str] | None:
    match = NAMED_MONTH_LAST_WEEK_PATTERN.search(question)
    if not match:
        return None
    month = int(match.group("month"))
    year = int(match.group("year") or (anchor.year if month <= anchor.month else anchor.year - 1))
    month_start = date(year, month, 1)
    end = date(year, month, calendar.monthrange(year, month)[1])
    start = max(month_start, end - timedelta(days=end.weekday()))
    month_text = f"{year}年{month}月" if match.group("year") else f"{month}月"
    return _scope(
        mode="named_month_last_week",
        start=start,
        end=end,
        label_suffix=f"用户指定{month_text}最后一周",
        source="user_month_last_week_phrase",
        anchor=anchor,
    )


def resolve_time_scope(question: str, *, asked_at: datetime | None = None, event: dict[str, Any] | None = None) -> dict[str, str]:
    anchor = _anchor_date(asked_at)

    explicit = EXPLICIT_RANGE_PATTERN.search(question)
    if explicit:
        start_date = explicit.group("start")
        end_date = explicit.group("end")
        time_slice.date_bounds(start_date, end_date)
        return {
            "mode": "explicit",
            "start_date": start_date,
            "end_date": end_date,
            "label": f"{start_date} 至 {end_date}（用户指定）",
        }

    relative = _relative_scope(question, anchor)
    if relative:
        return relative

    named_month_last_week = _named_month_last_week_scope(question, anchor)
    if named_month_last_week:
        return named_month_last_week

    named_month = _named_month_scope(question, anchor)
    if named_month:
        return named_month

    if event:
        start_date = _date_text(event.get("start_time") or event.get("end_time"))
        end_date = _date_text(event.get("end_time") or event.get("start_time"))
        if start_date and end_date:
            return {
                "mode": "event_period",
                "start_date": start_date,
                "end_date": end_date,
                "label": f"{start_date} 至 {end_date}（事件完整周期）",
            }

    end = anchor
    start = end - timedelta(days=29)
    return {
        "mode": "default_30_days",
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "label": f"{start.isoformat()} 至 {end.isoformat()}（提问时点近30天）",
    }
