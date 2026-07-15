from __future__ import annotations

import json
from typing import Any

from app.config import DATABASE_URL
from app.services.comment_user_ai_profile import call_openai_compatible_json
from app.services.report_agent import resolve_runtime_config


def _runtime() -> tuple[str, str, str, int]:
    return resolve_runtime_config(DATABASE_URL, None, None, None, None)


def parse_and_rank(
    question: str,
    candidates: list[dict[str, Any]],
    history: list[dict[str, str]],
) -> dict[str, Any]:
    prompt = f"""你是 AutoVOC 洞察推演 Agent 的场景解析与历史事件重排节点。

请同时完成两件事：
1. 把用户假设解析成结构化场景；
2. 只从给定候选事件中判断相似度并排序。

输出 JSON：
{{
  "status": "ready 或 needs_clarification",
  "clarification_question": "缺少关键条件时只问一个问题，否则为空",
  "scenario": {{
    "action_type": "企业动作类型",
    "affected_aspects": ["受到影响的配置或产品关注点"],
    "compensation": ["调价或权益补偿"],
    "target": "动作对象",
    "brand_name": "明确提到的品牌，否则为空",
    "model_name": "明确提到的车型，否则为空",
    "expected_scope": "希望推演的用户反应范围"
  }},
  "ranked_events": [
    {{
      "event_id": "只能来自候选事件",
      "similarity": "strong、medium、irrelevant 三选一",
      "similarities": ["相似点"],
      "differences": ["关键差异"]
    }}
  ]
}}

规则：
- 配置增加或减少场景必须明确具体配置；缺少关键条件时返回 needs_clarification。
- 不得新增候选列表以外的事件。
- strong 表示企业动作和核心产品关注点都相似；medium 表示只覆盖部分场景；其余为 irrelevant。
- 不生成用户反应结论。

用户问题：{question}
最近对话：{json.dumps(history[-10:], ensure_ascii=False, default=str)}
候选事件：{json.dumps(candidates, ensure_ascii=False, default=str)}
"""
    base_url, api_key, model, timeout_seconds = _runtime()
    return call_openai_compatible_json(
        prompt,
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )

def simulate_reactions(scenario: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    prompt = f"""你是 AutoVOC 证据驱动的用户反应推演节点。只能依据输入的历史事件和真实评论证据推演。

输出 JSON：
{{
  "reaction_cards": [{{"reaction": "支持、观望或反对", "strength": "主要或次要", "summary": "可能反应", "audiences": ["有证据的用户群"], "reasons": ["证据支持的原因"], "evidence_event_ids": ["事件ID"]}}],
  "audience_cards": [{{"audience": "用户群", "reaction": "可能反应", "concerns": ["关注点"], "evidence_event_ids": ["事件ID"]}}],
  "impact_cards": [{{"dimension": "口碑、产品关注点、购买信号或传播风险", "direction": "方向", "summary": "证据支持的影响", "evidence_event_ids": ["事件ID"]}}],
  "expression_themes": ["归纳后的表达主题，不得伪装成真实引语"],
  "limitations": ["当前证据不能覆盖的范围"]
}}

硬性要求：
- 每个主要判断必须引用输入中的 event_id。
- 不得伪造评论原话；真实评论由系统另行展示。
- 不得生成精确反应百分比。
- 跨品牌事件只能支持可能性判断，必须保留其证据边界。
- 不输出产品、营销或销售建议。
- 使用“可能、倾向、证据显示”，不得使用“必然、一定”。

目标场景：{json.dumps(scenario, ensure_ascii=False, default=str)}
已通过门槛的历史证据：{json.dumps(events, ensure_ascii=False, default=str)}
"""
    base_url, api_key, model, timeout_seconds = _runtime()
    return call_openai_compatible_json(
        prompt,
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )


def revise_simulation(
    scenario: dict[str, Any],
    events: list[dict[str, Any]],
    draft: dict[str, Any],
    issues: list[str],
) -> dict[str, Any]:
    prompt = f"""请修正 AutoVOC 用户反应推演 JSON。只能删除或改写不合格结论，不得增加新的事件、评论或百分比。

检查问题：{json.dumps(issues, ensure_ascii=False)}
目标场景：{json.dumps(scenario, ensure_ascii=False, default=str)}
允许使用的历史证据：{json.dumps(events, ensure_ascii=False, default=str)}
待修正 JSON：{json.dumps(draft, ensure_ascii=False, default=str)}

保持 reaction_cards、audience_cards、impact_cards、expression_themes、limitations 五个字段。
"""
    base_url, api_key, model, timeout_seconds = _runtime()
    return call_openai_compatible_json(
        prompt,
        base_url=base_url,
        api_key=api_key,
        model=model,
        timeout_seconds=timeout_seconds,
    )
