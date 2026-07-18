from __future__ import annotations

import re
from collections.abc import Sequence
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
NATURAL_BRAND_REQUEST_PREFIX = re.compile(
    r"(?:(?:请)?(?:输出|生成)(?:一份)?|我想看(?:一份)?|帮我看看(?:一份)?)"
)


def _has_only_request_prefix(surface: str, brand: str) -> bool:
    if not surface.endswith(brand):
        return False
    prefix = surface[: -len(brand)]
    return not prefix or NATURAL_BRAND_REQUEST_PREFIX.fullmatch(prefix) is not None


def _resolve_brand(message: str, known_brands: Sequence[str] | None) -> tuple[str, bool]:
    labeled = BRAND_AFTER_LABEL.search(message)
    if labeled:
        return labeled.group("brand"), False

    candidates = sorted(
        {brand.strip() for brand in known_brands or () if brand.strip()},
        key=lambda brand: (-len(brand), brand),
    )
    for brand in candidates:
        for marker in (f"{brand}品牌", f"{brand}的竞品动态报告", f"{brand}的竞品报告"):
            marker_start = message.find(marker)
            while marker_start >= 0:
                surface = message[: marker_start + len(brand)]
                if _has_only_request_prefix(surface, brand):
                    return brand, False
                marker_start = message.find(marker, marker_start + 1)
    return DEFAULT_BRAND, True


def resolve_competitor_report_scope(
    message: str,
    today: date | None = None,
    *,
    known_brands: Sequence[str] | None = None,
) -> dict[str, str | bool]:
    anchor = today or datetime.now(SHANGHAI_TZ).date()
    if isinstance(anchor, datetime):
        anchor = anchor.date()
    asked_at = datetime.combine(anchor, time.min, tzinfo=SHANGHAI_TZ)
    time_scope = resolve_time_scope(message, asked_at=asked_at)
    brand_name, brand_defaulted = _resolve_brand(message, known_brands)
    return {
        "brand_name": brand_name,
        "brand_defaulted": brand_defaulted,
        "start_date": time_scope["start_date"],
        "end_date": time_scope["end_date"],
        "time_defaulted": time_scope["mode"] == "default_30_days",
    }
