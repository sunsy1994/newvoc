from __future__ import annotations

import re
from html import escape
from pathlib import Path
from typing import Any


TEMPLATE_PATH = Path(__file__).with_name("templates") / "long_report.html"
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_]+)\}\}")


def _text(value: Any, default: str = "无") -> str:
    rendered = str(value).strip() if value is not None else ""
    return escape(rendered or default, quote=True)


def _number(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:,.1f}"
    try:
        return f"{int(value or 0):,}"
    except (TypeError, ValueError):
        return _text(value, "0")


def _summary_items(summary: dict[str, Any]) -> str:
    items = summary.get("executive_summary")
    if not isinstance(items, list) or not items:
        items = ["无"]
    return "".join(f'<li class="finding">{_text(item)}</li>' for item in items)


def _top_work_cards(dataset: dict[str, Any], summary: dict[str, Any]) -> str:
    findings = {
        str(item.get("work_id")): item.get("why_it_matters")
        for item in summary.get("top_work_findings") or []
        if isinstance(item, dict) and item.get("work_id")
    }
    cards: list[str] = []
    for rank, work in enumerate((dataset.get("top_works") or [])[:3], start=1):
        work_id = str(work.get("work_id") or "")
        insight = work.get("insight_markdown")
        cards.append(
            f"""
            <article class="work-card">
              <div class="rank">0{rank}</div>
              <div class="work-main">
                <div class="work-meta"><span>{_text(work_id)}</span><span>{_text(work.get("published_at"))[:10]}</span></div>
                <h3>{_text(work.get("title"))}</h3>
                <p class="muted">{_text(work.get("author_name"))} · {_text(work.get("account_type"))}</p>
                <div class="metric-row">
                  <span>总互动 <strong>{_number(work.get("total_engagement"))}</strong></span>
                  <span>点赞 {_number(work.get("interaction_like_cnt"))}</span>
                  <span>评论 {_number(work.get("comment_cnt"))}</span>
                  <span>收藏 {_number(work.get("favorite_cnt"))}</span>
                  <span>分享 {_number(work.get("share_cnt"))}</span>
                </div>
                <p><b>作品解读</b><span>{_text(insight)}</span></p>
                <p><b>入选判断</b><span>{_text(findings.get(work_id))}</span></p>
              </div>
            </article>
            """
        )
    return "".join(cards) or '<p class="empty">无</p>'


def render_competitor_report_html(dataset: dict[str, Any], summary: dict[str, Any]) -> str:
    overview = dataset.get("overview") or {}
    replacements = {
        "BRAND_NAME": _text(dataset.get("brand_name")),
        "START_DATE": _text(dataset.get("start_date")),
        "END_DATE": _text(dataset.get("end_date")),
        "WORK_COUNT": _number(overview.get("work_count")),
        "ACCOUNT_COUNT": _number(overview.get("account_count")),
        "TOTAL_ENGAGEMENT": _number(overview.get("total_engagement")),
        "AVERAGE_ENGAGEMENT": _number(overview.get("average_engagement")),
        "EXECUTIVE_SUMMARY": _summary_items(summary),
        "ACCOUNT_SUMMARY": _text(summary.get("account_summary")),
        "RHYTHM_SUMMARY": _text(summary.get("rhythm_summary")),
        "DEALER_SUMMARY": _text(summary.get("dealer_summary")),
        "TOP_WORKS": _top_work_cards(dataset, summary),
    }
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return PLACEHOLDER_RE.sub(lambda match: replacements[match.group(1)], template)
