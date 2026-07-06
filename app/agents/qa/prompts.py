from __future__ import annotations

import json

from app.agents.qa.state import QaAgentState
from app.agents.qa.tools import ALLOWED_TOOLS


def build_decision_prompt(state: QaAgentState) -> str:
    return f"""你是 AutoVOC 事件问答 Agent 的 ReAct 决策器。
问题：{state.get('question', '')}
当前事件：{json.dumps(state.get('event') or {}, ensure_ascii=False, default=str)}
统计区间：{json.dumps(state.get('time_scope') or {}, ensure_ascii=False)}
上一轮草稿：{state.get('draft_answer') or '尚无草稿'}
已有观察：{json.dumps(state.get('observations') or [], ensure_ascii=False, default=str)}
当前轮次：{state.get('round_count', 0)} / 3

只能选择以下工具：{', '.join(sorted(ALLOWED_TOOLS))}。
如果信息不足但缺少事件，设置 needs_clarification=true。
如果已有证据足够，设置 finish=true；否则每轮只选择一个工具。
仅返回 JSON：
{{"tool_name":"工具名","arguments":{{}},"finish":false,"needs_clarification":false,"clarification_question":""}}
禁止输出 SQL，禁止编造工具和参数。"""


def build_revision_prompt(state: QaAgentState) -> str:
    return f"""你是 AutoVOC 事件问答 Agent 的答案修订器。
用户问题：{state.get('question', '')}
上一轮回答：{state.get('draft_answer') or '尚无回答'}
事件：{json.dumps(state.get('event') or {}, ensure_ascii=False, default=str)}
统计区间：{json.dumps(state.get('time_scope') or {}, ensure_ascii=False)}
全部工具观察：{json.dumps(state.get('observations') or [], ensure_ascii=False, default=str)}

请基于全部工具观察修订上一轮回答。只能使用观察中存在的事实和数字；不要暴露工具名、字段名或执行轨迹。
仅返回 JSON：
{{"answer":"修订后的回答","sufficient":true,"missing_evidence":"","suggested_questions":["可继续追问"]}}
如果证据不足，sufficient=false，并准确说明还缺什么。"""
