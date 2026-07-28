from __future__ import annotations

import re
from html import escape
from pathlib import Path
from typing import Any


TEMPLATE_PATH = Path(__file__).with_name("templates") / "long_report.html"
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z_]+)\}\}")
INSIGHT_SECTIONS = (
    "视频介绍",
    "要点总结",
    "评论情绪",
    "评论关键词",
    "典型评论",
    "作者回复",
)
INSIGHT_HEADING_RE = re.compile(
    rf"^\s{{0,3}}#{{1,6}}\s*(?P<title>{'|'.join(map(re.escape, INSIGHT_SECTIONS))})\s*#*\s*$"
)


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


def _multiline_text(value: Any, default: str = "无") -> str:
    rendered = "\n".join(str(value).splitlines()).strip() if value is not None else ""
    return escape(rendered or default, quote=True).replace("\n", "<br>")


def _parse_insight_markdown(value: Any) -> dict[str, str]:
    parsed = {section: [] for section in INSIGHT_SECTIONS}
    source = str(value or "").strip()
    if not source or source == "无":
        return {section: "" for section in INSIGHT_SECTIONS}

    current: str | None = None
    has_heading = False
    for line in source.splitlines():
        match = INSIGHT_HEADING_RE.match(line)
        if match:
            current = match.group("title")
            has_heading = True
        elif current is not None:
            parsed[current].append(line)

    result = {section: "\n".join(lines).strip() for section, lines in parsed.items()}
    if not has_heading:
        result["视频介绍"] = source
    return result


def _records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _official_status(value: Any) -> str:
    if value is None or value == "":
        return "无"
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "是"}:
            return "是"
        if normalized in {"false", "0", "no", "否"}:
            return "否"
    return "是" if bool(value) else "否"


def _video_link(value: Any) -> str:
    url = str(value).strip() if value is not None else ""
    if not re.match(r"https?://", url, flags=re.IGNORECASE):
        return "无"
    safe_url = escape(url, quote=True)
    return f'<a href="{safe_url}" target="_blank" rel="noopener noreferrer">查看原视频</a>'


def _summary_items(summary: dict[str, Any]) -> str:
    items = summary.get("executive_summary")
    if not isinstance(items, list) or not items:
        items = ["无"]
    return "".join(f'<li class="finding">{_text(item)}</li>' for item in items)


def _daily_trend_rows(dataset: dict[str, Any]) -> str:
    rows = _records(dataset.get("daily_trend"))
    if not rows:
        return '<tr><td colspan="3">无</td></tr>'
    return "".join(
        "<tr>"
        f'<td>{_text(row.get("publish_date"))}</td>'
        f'<td>{_number(row.get("work_count"))}</td>'
        f'<td>{_number(row.get("total_engagement"))}</td>'
        "</tr>"
        for row in rows
    )


def _account_contribution_rows(dataset: dict[str, Any]) -> str:
    rows = _records(dataset.get("account_contribution"))
    if not rows:
        return '<tr><td colspan="5">无</td></tr>'
    return "".join(
        "<tr>"
        f'<td>{_text(row.get("author_name"))}</td>'
        f'<td>{_text(row.get("account_type"))}</td>'
        f'<td>{_official_status(row.get("is_official"))}</td>'
        f'<td>{_number(row.get("work_count"))}</td>'
        f'<td>{_number(row.get("total_engagement"))}</td>'
        "</tr>"
        for row in rows
    )


def _topic_distribution_rows(dataset: dict[str, Any]) -> str:
    rows = _records(dataset.get("topic_distribution"))
    if not rows:
        return '<tr><td colspan="3">无</td></tr>'
    return "".join(
        "<tr>"
        f'<td>{_text(row.get("topic"))}</td>'
        f'<td>{_number(row.get("work_count"))}</td>'
        f'<td>{_number(row.get("total_engagement"))}</td>'
        "</tr>"
        for row in rows
    )


def _data_note_items(dataset: dict[str, Any]) -> str:
    notes = dataset.get("data_notes")
    if not isinstance(notes, list) or not notes:
        notes = ["无"]
    return "".join(f"<li>{_multiline_text(note)}</li>" for note in notes)


def _top_work_cards(dataset: dict[str, Any], summary: dict[str, Any]) -> str:
    findings = {
        str(item.get("work_id")): item.get("why_it_matters")
        for item in summary.get("top_work_findings") or []
        if isinstance(item, dict) and item.get("work_id")
    }
    cards: list[str] = []
    for rank, work in enumerate(_records(dataset.get("top_works"))[:3], start=1):
        work_id = str(work.get("work_id") or "")
        insight = _parse_insight_markdown(work.get("insight_markdown"))
        brand_name = work.get("brand_name") or dataset.get("brand_name")
        cards.append(
            f"""
            <article class="work-card">
              <div class="rank">0{rank}</div>
              <div class="work-main">
                <div class="work-meta"><span>{_text(work_id)}</span><span>{_text(work.get("published_at"))[:10]}</span></div>
                <h3>{_text(work.get("title"))}</h3>
                <div class="metric-row">
                  <span>总互动 <strong>{_number(work.get("total_engagement"))}</strong></span>
                  <span>点赞 {_number(work.get("interaction_like_cnt"))}</span>
                  <span>评论 {_number(work.get("comment_cnt"))}</span>
                  <span>收藏 {_number(work.get("favorite_cnt"))}</span>
                  <span>分享 {_number(work.get("share_cnt"))}</span>
                </div>
                <div class="work-analysis">
                  <h4>视频基本信息</h4>
                  <dl class="detail-list">
                    <dt>标题</dt><dd>{_text(work.get("title"))}</dd>
                    <dt>作者</dt><dd>{_text(work.get("author_name"))}</dd>
                    <dt>品牌</dt><dd>{_text(brand_name)}</dd>
                    <dt>账号类型</dt><dd>{_text(work.get("account_type"))}</dd>
                    <dt>官方账号</dt><dd>{_official_status(work.get("is_official"))}</dd>
                    <dt>发布时间</dt><dd>{_text(work.get("published_at"))}</dd>
                    <dt>主题</dt><dd>{_text(work.get("topic_tags"))}</dd>
                    <dt>视频链接</dt><dd>{_video_link(work.get("video_url"))}</dd>
                  </dl>
                  <h4>视频内容解析</h4>
                  <dl class="detail-list">
                    <dt>视频介绍</dt><dd>{_multiline_text(insight["视频介绍"])}</dd>
                    <dt>要点总结</dt><dd>{_multiline_text(insight["要点总结"])}</dd>
                  </dl>
                  <h4>评论解析</h4>
                  <dl class="detail-list">
                    <dt>评论情绪</dt><dd>{_multiline_text(insight["评论情绪"])}</dd>
                    <dt>评论关键词</dt><dd>{_multiline_text(insight["评论关键词"])}</dd>
                    <dt>典型评论</dt><dd>{_multiline_text(insight["典型评论"])}</dd>
                    <dt>作者回复</dt><dd>{_multiline_text(insight["作者回复"])}</dd>
                  </dl>
                  <p class="selection-reason"><b>入选判断</b><span>{_text(findings.get(work_id))}</span></p>
                </div>
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
        "ACCOUNT_CONTRIBUTION_ROWS": _account_contribution_rows(dataset),
        "DAILY_TREND_ROWS": _daily_trend_rows(dataset),
        "TOPIC_DISTRIBUTION_ROWS": _topic_distribution_rows(dataset),
        "DATA_NOTES": _data_note_items(dataset),
    }
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    return PLACEHOLDER_RE.sub(lambda match: replacements[match.group(1)], template)
