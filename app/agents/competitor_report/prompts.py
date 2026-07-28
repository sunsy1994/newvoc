from __future__ import annotations

import json
from typing import Any


PROMPT_VERSION = "competitor_report_agent_v1"


def render_competitor_summary_prompt(dataset: dict[str, Any]) -> str:
    evidence = {
        key: dataset.get(key)
        for key in (
            "overview",
            "daily_trend",
            "account_contribution",
            "topic_distribution",
            "top_works",
            "data_notes",
        )
    }
    return f"""你是 AutoVOC 竞品动态报告摘要助手。请只基于给定结构化证据提炼结论。

输出必须是以下 JSON 对象：
{{
  "executive_summary": ["3至5条有数字或案例支撑的结论"],
  "top_work_findings": [{{"work_id": "作品ID", "why_it_matters": "基于输入证据的判断"}}],
  "account_summary": "账号贡献结论",
  "rhythm_summary": "发布与互动节奏结论",
  "dealer_summary": "经销商表现；证据不足时明确不足"
}}

要求：
1. 只能引用输入证据，不得编造任何外部事实或缺失信息。
2. 不得编造缺失的作品描述、情感、评论和回复；没有证据时明确写“证据不足”。
3. 热门作品判断必须使用输入中的作品 ID，并由互动数据或已有作品解读支撑。
4. 不输出行动建议，不输出数据字段名、系统路径、工具或实现细节。

结构化证据：
{json.dumps(evidence, ensure_ascii=False, indent=2, default=str)}
"""
