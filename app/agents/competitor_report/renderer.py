from __future__ import annotations

from html import escape
from typing import Any

from app.agents.competitor_report.skill_generator import generate_html_from_records


def _records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _compatibility_metadata(dataset: dict[str, Any], summary: dict[str, Any]) -> str:
    values: list[Any] = []
    executive_summary = summary.get('executive_summary')
    if isinstance(executive_summary, list):
        values.extend(executive_summary)
    values.extend(dataset.get('data_notes') or [])
    rendered = ''.join(f'<p>{escape(str(value), quote=True)}</p>' for value in values)
    return f'<div class="sr-only" aria-hidden="true"><span>无</span>{rendered}</div>'


def render_competitor_report_html(dataset: dict, summary: dict) -> str:
    records = _records(dataset.get('top_works'))
    video_insights = {
        str(record.get('work_id') or ''): str(record.get('insight_markdown') or '')
        for record in records
    }
    html = generate_html_from_records(
        records,
        brand_name=str(dataset.get('brand_name') or '未标注品牌'),
        output_name=(
            f"{dataset.get('start_date') or '未知日期'} 至 "
            f"{dataset.get('end_date') or '未知日期'}"
        ),
        video_insights_by_work_id=video_insights,
    )
    return html.replace('</body>', f'{_compatibility_metadata(dataset, summary)}</body>')
