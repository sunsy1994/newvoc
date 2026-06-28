from __future__ import annotations

import json

from app.agents.data_question.state import DataQuestionState, METRIC_CATALOG


def build_action_prompt(state: DataQuestionState) -> str:
    history_json = json.dumps(state.get("history") or [], ensure_ascii=False)
    page_context = {"current_event_id": state.get("event_id")}
    return f"""你是汽车行业VOC问数助手。请把用户问题转换为一个受控工具动作，只输出JSON对象。

可用动作：
1. list_events：查询近期事件，参数 days（默认30）和可选 brand。
2. resolve_event：根据名称查找事件，参数 event_name。
3. get_event_metric：查询单个事件指标，参数 metric，可选 event_name。页面已有事件时可省略 event_name。
4. rank_events：比较近期事件，参数 days（默认30）和 metric。

metric只能是：{', '.join(METRIC_CATALOG)}。
“近期”默认30天。只有无法确定事件或指标且会影响结果时才追问。
如果上一轮正在追问事件或指标，当前回答应继承上一轮未完成的查询意图。
不要生成SQL，不要生成接口路径，不要回答数据本身。

输出格式：
{{"action":"list_events","arguments":{{"days":30}},"needs_clarification":false,"clarification_question":""}}

页面上下文：{json.dumps(page_context, ensure_ascii=False)}
最近会话：{history_json}
当前问题：{state['question']}
"""


def build_answer_prompt(state: DataQuestionState) -> str:
    return f"""你是汽车行业VOC数据助手。请只基于下面的工具结果回答用户问题。

要求：
1. 使用自然、简洁的中文，像业务助手而不是接口日志。
2. 不得提及或输出event_id、接口路径、数据库字段、工具名和执行轨迹。
3. 不得补充工具结果之外的数字或事实。
4. 如果用户使用“近期”，自然说明本次采用的时间范围。
5. suggested_questions给出0到3个可继续追问的问题。
6. 建议问题必须能由现有问数工具回答，只能围绕事件列表、声量、帖子、评论、KOL和互动量，不要建议话题、情感或竞品分析。

输出JSON：{{"answer":"","suggested_questions":[]}}

用户问题：{state['question']}
工具结果：{json.dumps(state['tool_result'], ensure_ascii=False, default=str)}
"""
