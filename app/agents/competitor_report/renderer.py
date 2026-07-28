from __future__ import annotations

from html import escape
from typing import Any

from app.agents.competitor_report.skill_generator import generate_html_from_records


def _records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _full_scope_records(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ('records', 'works'):
        if key in dataset and isinstance(dataset[key], list):
            return _records(dataset[key])
    top_works = _records(dataset.get('top_works'))
    work_count = int((dataset.get('overview') or {}).get('work_count') or 0)
    if work_count == len(top_works):
        return top_works
    raise ValueError('full-scope competitor report records are required; Top3 is not a full dataset')


def _summary_text(value: Any) -> str:
    return escape(str(value), quote=True)


def _inject_visible_summary(html: str, dataset: dict[str, Any], summary: dict[str, Any]) -> str:
    executive = summary.get('executive_summary')
    if isinstance(executive, list):
        content = ''.join(f'<div class="insight">{_summary_text(item)}</div>' for item in executive)
        html = html.replace('<div class="insight-list">', f'<div class="insight-list">{content}', 1)

    module_summaries = (
        ('账号互动贡献', summary.get('account_summary')),
        ('发布时间与互动走势', summary.get('rhythm_summary')),
        ('重点经销商承接效果', summary.get('dealer_summary')),
    )
    for heading, value in module_summaries:
        if value is not None and str(value).strip():
            needle = f'<h2>{heading}</h2>'
            html = html.replace(
                needle,
                f'{needle}<p class="meta">{_summary_text(value)}</p>',
                1,
            )

    notes = dataset.get('data_notes')
    if isinstance(notes, list) and notes:
        items = ''.join(f'<li>{_summary_text(note)}</li>' for note in notes)
        section = (
            '<section class="section"><h2>数据口径和证据说明</h2>'
            f'<ul class="comment-list">{items}</ul></section>'
        )
        html = html.replace('<div class="footer">', f'{section}<div class="footer">', 1)
    return html


def render_competitor_report_html(dataset: dict, summary: dict) -> str:
    records = _full_scope_records(dataset)
    findings = {
        str(item.get('work_id')): str(item.get('why_it_matters') or '无')
        for item in summary.get('top_work_findings') or []
        if isinstance(item, dict) and item.get('work_id')
    }
    render_records = [
        {
            **record,
            'selection_reason': findings.get(str(record.get('work_id') or ''), ''),
        }
        for record in records
    ]
    video_insights = {
        str(record.get('work_id') or ''): str(record.get('insight_markdown') or '')
        for record in render_records
    }
    html = generate_html_from_records(
        render_records,
        brand_name=str(dataset.get('brand_name') or '未标注品牌'),
        output_name=(
            f"{dataset.get('start_date') or '未知日期'} 至 "
            f"{dataset.get('end_date') or '未知日期'}"
        ),
        video_insights_by_work_id=video_insights,
    )
    return _inject_visible_summary(html, dataset, summary)
