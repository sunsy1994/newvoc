from __future__ import annotations

from typing import Any

import psycopg
from psycopg.rows import dict_row

from app.config import DATABASE_URL
from app.services.asset_library import normalize_row


NODE_KINDS = {"source_field", "metric", "rule", "llm_label", "ai_summary", "dashboard", "agent_tool", "agent_output"}
GENERATION_TYPES = {
    "raw_fact",
    "direct_aggregation",
    "derived_metric",
    "rule_judgement",
    "llm_label",
    "llm_summary",
    "consumer_only",
}
BUSINESS_DOMAINS = {"market", "product", "sales", "shared"}
NODE_STATUSES = {"draft", "active", "deprecated"}
RELATION_TYPES = {"depends_on", "aggregates_to", "calculates_to", "rules_to", "labels_to", "consumed_by", "summarized_by"}
LLM_GENERATION_TYPES = {"llm_label", "llm_summary"}
SYSTEM_EDITABLE_FIELDS = {"business_definition", "owner", "status"}
CUSTOM_EDITABLE_FIELDS = {
    "lineage_name",
    "node_kind",
    "generation_type",
    "business_domain",
    "business_definition",
    "calculation_logic",
    "implementation_ref",
    "prompt_scene",
    "owner",
    "status",
}


def _node(
    code: str,
    name: str,
    kind: str,
    generation: str,
    domain: str,
    definition: str,
    logic: str,
    implementation: str,
    prompt_scene: str = "",
) -> dict[str, Any]:
    return {
        "lineage_code": code,
        "lineage_name": name,
        "node_kind": kind,
        "generation_type": generation,
        "business_domain": domain,
        "business_definition": definition,
        "calculation_logic": logic,
        "implementation_ref": implementation,
        "prompt_scene": prompt_scene,
        "owner": "",
        "status": "active",
        "is_system": True,
    }


LINEAGE_NODE_SEEDS = [
    _node("source.event.event_id", "事件ID", "source_field", "raw_fact", "shared", "事件资产唯一标识。", "上传或ETL标准化后直接保存。", "data_asset.dwd_event.event_id"),
    _node("source.content.content_id", "内容ID", "source_field", "raw_fact", "market", "帖子或主内容唯一标识。", "上传或ETL标准化后直接保存。", "data_asset.dwd_content.content_id"),
    _node("source.content.published_at", "内容发布时间", "source_field", "raw_fact", "market", "内容公开发布时间。", "上传或ETL标准化后直接保存。", "data_asset.dwd_content.published_at"),
    _node("source.content.engagement_total", "内容互动量", "source_field", "raw_fact", "market", "单条内容的点赞、评论、转发和收藏等互动汇总。", "数据导入字段或ETL汇总字段。", "data_asset.dwd_content.engagement_total"),
    _node("source.comment.comment_id", "评论ID", "source_field", "raw_fact", "shared", "评论资产唯一标识。", "上传或ETL标准化后直接保存。", "data_asset.dwd_comment.comment_id"),
    _node("source.comment.comment_text", "评论正文", "source_field", "raw_fact", "shared", "用户公开评论原文。", "上传或ETL标准化后直接保存。", "data_asset.dwd_comment.comment_text"),
    _node("source.author.is_kol", "KOL标识", "source_field", "raw_fact", "market", "作者是否属于KOL。", "作者资产维护或ETL识别结果。", "data_asset.dwd_author.is_kol"),
    _node("metric.content_count", "帖子数", "metric", "direct_aggregation", "market", "事件范围内去重内容数量。", "COUNT(DISTINCT content_id)", "event_voc_insights.fetch_event_overview"),
    _node("metric.comment_count", "评论数", "metric", "direct_aggregation", "shared", "事件范围内去重评论数量。", "COUNT(DISTINCT comment_id)", "event_voc_insights.fetch_event_overview"),
    _node("metric.total_volume", "总声量", "metric", "derived_metric", "market", "事件内容数与评论数之和。", "content_count + comment_count", "event_voc_insights.build_market_overview_metrics"),
    _node("metric.total_engagement", "总互动量", "metric", "direct_aggregation", "market", "事件内容互动量汇总。", "SUM(engagement_total)", "event_voc_insights.fetch_event_overview"),
    _node("label.comment_sentiment", "评论情绪标签", "llm_label", "llm_label", "shared", "LLM对评论表达情绪的结构化分类。", "从评论正文生成正向、中性、负向等标签。", "dwd_comment.comment_label_json.comment_sentiment", "comment_labeling"),
    _node("label.purchase_signal", "购买信号标签", "llm_label", "llm_label", "sales", "LLM识别评论中的购买意向强度。", "从评论正文生成无、弱、中、强标签。", "dwd_comment.comment_label_json.purchase_signal", "comment_labeling"),
    _node("label.product_aspect", "产品关注点标签", "llm_label", "llm_label", "product", "LLM识别评论讨论的产品维度。", "从评论正文提取外观、价格、配置等关注点。", "dwd_comment.comment_label_json.aspect", "comment_labeling"),
    _node("metric.positive_rate", "正向率", "metric", "derived_metric", "shared", "已标注评论中正向评论的占比。", "positive_count / labeled_comment_count × 100%", "event_voc_insights.fetch_comment_quality"),
    _node("metric.negative_rate", "负向率", "metric", "derived_metric", "shared", "已标注评论中负向评论的占比。", "negative_count / labeled_comment_count × 100%", "event_voc_insights.fetch_comment_quality"),
    _node("metric.purchase_signal_rate", "中高购买信号率", "metric", "derived_metric", "sales", "已标注评论中购买信号为中或强的占比。", "mid_high_purchase_signal_count / labeled_comment_count × 100%", "event_voc_insights.fetch_comment_quality"),
    _node("metric.peak_contribution_rate", "峰值贡献率", "metric", "derived_metric", "market", "事件峰值日声量占总声量的比例。", "peak_volume / total_volume × 100%", "event_voc_insights.build_volume_rhythm_story"),
    _node("rule.burst_event", "集中爆发", "rule", "rule_judgement", "market", "事件声量是否集中在峰值日爆发。", "峰值贡献率达到规则阈值时判断为集中爆发。", "event_voc_insights.build_volume_rhythm_story"),
    _node("rule.kol_driven", "KOL带动", "rule", "rule_judgement", "market", "事件互动是否主要由KOL内容贡献。", "根据KOL互动贡献率进行规则判断。", "event_voc_insights.build_subject_story"),
    _node("rule.product_opportunity", "产品机会点", "rule", "rule_judgement", "product", "高提及且具有中高购买信号的产品关注点。", "提及率 × 中高购买信号率。", "event_voc_insights.build_product_opportunity_story"),
    _node("rule.product_risk", "产品风险点", "rule", "rule_judgement", "product", "高提及且负向反馈集中的产品关注点。", "提及率 × 负向率。", "event_voc_insights.build_product_opportunity_story"),
    _node("rule.product_surprise", "产品惊喜点", "rule", "rule_judgement", "product", "高提及且正向反馈集中的产品关注点。", "提及率 × 正向率。", "event_voc_insights.build_product_opportunity_story"),
    _node("dashboard.market", "市场看板", "dashboard", "consumer_only", "market", "消费传播规模、节奏、主体和反馈质量。", "只消费已定义指标和规则。", "frontend.voc.events.market"),
    _node("dashboard.product", "产品看板", "dashboard", "consumer_only", "product", "消费产品关注点、机会风险和PKO证据。", "只消费已定义指标、标签和规则。", "frontend.voc.events.product"),
    _node("dashboard.sales", "销售看板", "dashboard", "consumer_only", "sales", "消费购买信号、用户画像和线索来源。", "只消费已定义指标和标签。", "frontend.voc.events.sales"),
    _node("tool.data_question.metric", "问数指标工具", "agent_tool", "consumer_only", "shared", "为问数Agent提供白名单指标查询。", "按事件和指标编码执行确定性查询。", "app.agents.data_question.tools"),
    _node("tool.qa.story", "问答故事工具", "agent_tool", "consumer_only", "shared", "为问答Agent提供市场、产品、销售和评论证据。", "调用现有看板和时间切片服务。", "app.agents.qa.tools"),
    _node("tool.insight.evidence", "洞察证据工具", "agent_tool", "consumer_only", "shared", "为洞察Agent检索相似事件及真实评论证据。", "规则召回、关注点过滤和证据门槛。", "app.agents.insight.tools"),
    _node("agent.data_question.output", "问数回答", "agent_output", "llm_summary", "shared", "基于确定性指标查询结果组织的回答。", "LLM只组织Tool返回的数据。", "app.agents.data_question.graph", "data_question_agent"),
    _node("agent.qa.output", "问答回答", "agent_output", "llm_summary", "shared", "基于事件工具证据生成的聚焦回答。", "最多三轮受限ReAct。", "app.agents.qa.graph", "qa_agent"),
    _node("agent.report.output", "事件综合报告", "agent_output", "llm_summary", "shared", "消费三部门看板上下文生成的固定模板报告。", "LLM短结论加系统模板和证据。", "app.agents.report.graph", "event_report_agent_v1"),
    _node("agent.insight.output", "用户反应推演", "agent_output", "llm_summary", "shared", "基于相似事件和真实评论证据生成的用户反应推演。", "证据门槛通过后推演并复核。", "app.agents.insight.graph", "insight_agent"),
    _node("source.competitor.work_facts", "竞品作品事实", "source_field", "raw_fact", "market", "竞品作品的品牌、作者、发布时间、主题和互动分项等原始事实。", "竞品库导入并按作品原样保存。", "data_asset.competitor_work"),
    _node("source.competitor.insight_markdown", "竞品作品人工解读", "source_field", "raw_fact", "market", "用户按作品维护的视频与评论 Markdown 解读。", "按 work_id 人工维护；未维护时为空。", "data_asset.competitor_work_insight.insight_markdown"),
    _node("metric.competitor.total_engagement", "竞品作品总互动量", "metric", "derived_metric", "market", "单条竞品作品的点赞、评论、收藏和分享之和。", "interaction_like_cnt + comment_cnt + favorite_cnt + share_cnt", "app.agents.competitor_report.tools.TOTAL_ENGAGEMENT_SQL"),
    _node("rule.competitor.top3", "竞品热门作品Top3", "rule", "rule_judgement", "market", "指定品牌和时间范围内按统一互动口径选出的前三条作品。", "先按品牌和时间过滤，再按总互动量降序、互动点赞数降序、评论数降序、发布时间降序、work_id 升序取前三。", "app.agents.competitor_report.tools.collect_competitor_report_dataset"),
    _node("summary.competitor.report_prose", "竞品报告AI结论", "ai_summary", "llm_summary", "market", "基于确定性指标、Top3 事实和人工解读生成的报告结论文案。", "LLM只组织结构化数据与人工维护资料，不计算指标或选择Top3。", "app.agents.competitor_report.graph", "competitor_report_agent_v1"),
    _node("agent.competitor_report.output", "竞品动态报告", "agent_output", "consumer_only", "market", "固定模板渲染的竞品动态 HTML 报告。", "系统模板组合范围、指标、Top3、人工解读和AI结论。", "app.agents.competitor_report.renderer"),
]


def _edge(upstream: str, downstream: str, relation: str, description: str) -> dict[str, Any]:
    return {
        "upstream_code": upstream,
        "downstream_code": downstream,
        "relation_type": relation,
        "relation_description": description,
        "is_system": True,
    }


LINEAGE_EDGE_SEEDS = [
    _edge("source.content.content_id", "metric.content_count", "aggregates_to", "按事件去重统计内容。"),
    _edge("source.comment.comment_id", "metric.comment_count", "aggregates_to", "按事件去重统计评论。"),
    _edge("metric.content_count", "metric.total_volume", "calculates_to", "内容数参与总声量计算。"),
    _edge("metric.comment_count", "metric.total_volume", "calculates_to", "评论数参与总声量计算。"),
    _edge("source.content.engagement_total", "metric.total_engagement", "aggregates_to", "汇总内容互动。"),
    _edge("source.comment.comment_text", "label.comment_sentiment", "labels_to", "LLM从评论原文识别情绪。"),
    _edge("source.comment.comment_text", "label.purchase_signal", "labels_to", "LLM从评论原文识别购买信号。"),
    _edge("source.comment.comment_text", "label.product_aspect", "labels_to", "LLM从评论原文识别产品关注点。"),
    _edge("label.comment_sentiment", "metric.positive_rate", "calculates_to", "正向标签用于计算正向率。"),
    _edge("label.comment_sentiment", "metric.negative_rate", "calculates_to", "负向标签用于计算负向率。"),
    _edge("label.purchase_signal", "metric.purchase_signal_rate", "calculates_to", "中强标签用于计算购买信号率。"),
    _edge("source.content.published_at", "metric.peak_contribution_rate", "calculates_to", "按日聚合形成传播峰值。"),
    _edge("metric.total_volume", "metric.peak_contribution_rate", "calculates_to", "总声量作为峰值贡献率分母。"),
    _edge("metric.peak_contribution_rate", "rule.burst_event", "rules_to", "峰值贡献率触发集中爆发规则。"),
    _edge("source.author.is_kol", "rule.kol_driven", "rules_to", "KOL身份参与互动贡献规则。"),
    _edge("metric.total_engagement", "rule.kol_driven", "rules_to", "互动量参与KOL贡献判断。"),
    _edge("label.product_aspect", "rule.product_opportunity", "rules_to", "关注点为机会判断提供维度。"),
    _edge("metric.purchase_signal_rate", "rule.product_opportunity", "rules_to", "购买信号率参与机会判断。"),
    _edge("label.product_aspect", "rule.product_risk", "rules_to", "关注点为风险判断提供维度。"),
    _edge("metric.negative_rate", "rule.product_risk", "rules_to", "负向率参与风险判断。"),
    _edge("label.product_aspect", "rule.product_surprise", "rules_to", "关注点为惊喜判断提供维度。"),
    _edge("metric.positive_rate", "rule.product_surprise", "rules_to", "正向率参与惊喜判断。"),
    _edge("metric.total_volume", "dashboard.market", "consumed_by", "市场看板展示事件规模。"),
    _edge("rule.burst_event", "dashboard.market", "consumed_by", "市场看板展示传播节奏判断。"),
    _edge("rule.kol_driven", "dashboard.market", "consumed_by", "市场看板展示传播主体判断。"),
    _edge("rule.product_opportunity", "dashboard.product", "consumed_by", "产品看板展示机会点。"),
    _edge("rule.product_risk", "dashboard.product", "consumed_by", "产品看板展示风险点。"),
    _edge("rule.product_surprise", "dashboard.product", "consumed_by", "产品看板展示惊喜点。"),
    _edge("metric.purchase_signal_rate", "dashboard.sales", "consumed_by", "销售看板展示线索质量。"),
    _edge("metric.content_count", "tool.data_question.metric", "consumed_by", "问数工具查询帖子数。"),
    _edge("metric.comment_count", "tool.data_question.metric", "consumed_by", "问数工具查询评论数。"),
    _edge("metric.total_volume", "tool.data_question.metric", "consumed_by", "问数工具查询总声量。"),
    _edge("tool.data_question.metric", "agent.data_question.output", "summarized_by", "查询结果组织为问数回答。"),
    _edge("dashboard.market", "tool.qa.story", "consumed_by", "问答工具读取市场故事。"),
    _edge("dashboard.product", "tool.qa.story", "consumed_by", "问答工具读取产品故事。"),
    _edge("dashboard.sales", "tool.qa.story", "consumed_by", "问答工具读取销售故事。"),
    _edge("tool.qa.story", "agent.qa.output", "summarized_by", "工具证据组织为问答回答。"),
    _edge("dashboard.market", "agent.report.output", "summarized_by", "市场上下文进入报告。"),
    _edge("dashboard.product", "agent.report.output", "summarized_by", "产品上下文进入报告。"),
    _edge("dashboard.sales", "agent.report.output", "summarized_by", "销售上下文进入报告。"),
    _edge("source.comment.comment_text", "tool.insight.evidence", "consumed_by", "洞察工具检索真实评论。"),
    _edge("label.product_aspect", "tool.insight.evidence", "consumed_by", "关注点限制洞察证据范围。"),
    _edge("tool.insight.evidence", "agent.insight.output", "summarized_by", "相似事件证据进入用户反应推演。"),
    _edge("source.competitor.work_facts", "metric.competitor.total_engagement", "calculates_to", "四项互动事实用于计算作品总互动量。"),
    _edge("source.competitor.work_facts", "rule.competitor.top3", "rules_to", "品牌、时间和稳定排序字段参与Top3筛选。"),
    _edge("metric.competitor.total_engagement", "rule.competitor.top3", "rules_to", "总互动量作为Top3主排序依据。"),
    _edge("source.competitor.work_facts", "summary.competitor.report_prose", "summarized_by", "LLM消费overview、daily、account、topic和Top3原始字段生成结论。"),
    _edge("metric.competitor.total_engagement", "summary.competitor.report_prose", "summarized_by", "确定性互动指标进入AI结论。"),
    _edge("rule.competitor.top3", "summary.competitor.report_prose", "summarized_by", "确定性Top3事实进入AI结论。"),
    _edge("source.competitor.insight_markdown", "summary.competitor.report_prose", "summarized_by", "人工维护解读为AI结论提供证据。"),
    _edge("source.competitor.work_facts", "agent.competitor_report.output", "consumed_by", "报告固定区块展示作品与范围事实。"),
    _edge("metric.competitor.total_engagement", "agent.competitor_report.output", "consumed_by", "报告固定区块展示互动指标。"),
    _edge("rule.competitor.top3", "agent.competitor_report.output", "consumed_by", "报告固定区块展示热门作品Top3。"),
    _edge("source.competitor.insight_markdown", "agent.competitor_report.output", "consumed_by", "报告Top3区块展示人工维护解读。"),
    _edge("summary.competitor.report_prose", "agent.competitor_report.output", "consumed_by", "固定模板组合AI结论形成最终报告。"),
]


SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS data_asset;
CREATE TABLE IF NOT EXISTS data_asset.system_lineage_node (
    lineage_id BIGSERIAL PRIMARY KEY,
    lineage_code TEXT NOT NULL UNIQUE,
    lineage_name TEXT NOT NULL,
    node_kind TEXT NOT NULL CHECK (node_kind IN ('source_field','metric','rule','llm_label','ai_summary','dashboard','agent_tool','agent_output')),
    generation_type TEXT NOT NULL CHECK (generation_type IN ('raw_fact','direct_aggregation','derived_metric','rule_judgement','llm_label','llm_summary','consumer_only')),
    business_domain TEXT NOT NULL CHECK (business_domain IN ('market','product','sales','shared')),
    business_definition TEXT NOT NULL DEFAULT '',
    calculation_logic TEXT NOT NULL DEFAULT '',
    implementation_ref TEXT NOT NULL DEFAULT '',
    prompt_scene TEXT NOT NULL DEFAULT '',
    owner TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('draft','active','deprecated')),
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    created_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS data_asset.system_lineage_edge (
    edge_id BIGSERIAL PRIMARY KEY,
    upstream_code TEXT NOT NULL REFERENCES data_asset.system_lineage_node(lineage_code) ON DELETE RESTRICT,
    downstream_code TEXT NOT NULL REFERENCES data_asset.system_lineage_node(lineage_code) ON DELETE RESTRICT,
    relation_type TEXT NOT NULL CHECK (relation_type IN ('depends_on','aggregates_to','calculates_to','rules_to','labels_to','consumed_by','summarized_by')),
    relation_description TEXT NOT NULL DEFAULT '',
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    created_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT system_lineage_edge_not_self CHECK (upstream_code <> downstream_code),
    CONSTRAINT system_lineage_edge_unique UNIQUE (upstream_code, downstream_code, relation_type)
);
"""


def public_lineage_node(node: dict[str, Any]) -> dict[str, Any]:
    result = normalize_row(dict(node))
    result["uses_llm"] = result.get("generation_type") in LLM_GENERATION_TYPES
    result["upstream_count"] = int(result.get("upstream_count") or 0)
    result["downstream_count"] = int(result.get("downstream_count") or 0)
    return result


def build_lineage_summary(nodes: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "node_count": len(nodes),
        "metric_count": sum(item.get("node_kind") == "metric" for item in nodes),
        "rule_count": sum(item.get("node_kind") == "rule" for item in nodes),
        "llm_label_count": sum(item.get("node_kind") == "llm_label" for item in nodes),
        "ai_summary_count": sum(item.get("generation_type") == "llm_summary" for item in nodes),
        "incomplete_definition_count": sum(not str(item.get("business_definition") or "").strip() for item in nodes),
    }


def _required_text(payload: dict[str, Any], field: str) -> str:
    value = str(payload.get(field) or "").strip()
    if not value:
        raise ValueError(f"{field} 不能为空")
    return value


def _enum_value(payload: dict[str, Any], field: str, allowed: set[str]) -> str:
    value = _required_text(payload, field)
    if value not in allowed:
        raise ValueError(f"{field} 不合法")
    return value


def validate_node_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "lineage_code": _required_text(payload, "lineage_code"),
        "lineage_name": _required_text(payload, "lineage_name"),
        "node_kind": _enum_value(payload, "node_kind", NODE_KINDS),
        "generation_type": _enum_value(payload, "generation_type", GENERATION_TYPES),
        "business_domain": _enum_value(payload, "business_domain", BUSINESS_DOMAINS),
        "business_definition": str(payload.get("business_definition") or "").strip(),
        "calculation_logic": str(payload.get("calculation_logic") or "").strip(),
        "implementation_ref": str(payload.get("implementation_ref") or "").strip(),
        "prompt_scene": str(payload.get("prompt_scene") or "").strip(),
        "owner": str(payload.get("owner") or "").strip(),
        "status": _enum_value({"status": payload.get("status", "draft")}, "status", NODE_STATUSES),
        "is_system": False,
    }


def validate_node_update(payload: dict[str, Any], *, is_system: bool) -> dict[str, Any]:
    allowed = SYSTEM_EDITABLE_FIELDS if is_system else CUSTOM_EDITABLE_FIELDS
    unknown = set(payload) - allowed
    if unknown:
        scope = "系统节点" if is_system else "自定义节点"
        raise ValueError(f"{scope}不允许修改字段：{', '.join(sorted(unknown))}")
    if not payload:
        raise ValueError("至少提供一个需要修改的字段")
    result = {key: str(value or "").strip() for key, value in payload.items()}
    for field, allowed_values in (
        ("node_kind", NODE_KINDS),
        ("generation_type", GENERATION_TYPES),
        ("business_domain", BUSINESS_DOMAINS),
        ("status", NODE_STATUSES),
    ):
        if field in result and result[field] not in allowed_values:
            raise ValueError(f"{field} 不合法")
    if "lineage_name" in result and not result["lineage_name"]:
        raise ValueError("lineage_name 不能为空")
    return result


def validate_edge_payload(payload: dict[str, Any]) -> dict[str, Any]:
    upstream = _required_text(payload, "upstream_code")
    downstream = _required_text(payload, "downstream_code")
    if upstream == downstream:
        raise ValueError("血缘关系不能指向自身")
    return {
        "upstream_code": upstream,
        "downstream_code": downstream,
        "relation_type": _enum_value(payload, "relation_type", RELATION_TYPES),
        "relation_description": str(payload.get("relation_description") or "").strip(),
        "is_system": False,
    }


def ensure_lineage_catalog(database_url: str = DATABASE_URL) -> None:
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(SCHEMA_SQL)
            cur.executemany(
                """
                INSERT INTO data_asset.system_lineage_node
                  (lineage_code, lineage_name, node_kind, generation_type, business_domain,
                   business_definition, calculation_logic, implementation_ref, prompt_scene, owner, status, is_system)
                VALUES (%(lineage_code)s, %(lineage_name)s, %(node_kind)s, %(generation_type)s, %(business_domain)s,
                        %(business_definition)s, %(calculation_logic)s, %(implementation_ref)s, %(prompt_scene)s,
                        %(owner)s, %(status)s, TRUE)
                ON CONFLICT (lineage_code) DO UPDATE
                SET lineage_name = EXCLUDED.lineage_name,
                    node_kind = EXCLUDED.node_kind,
                    generation_type = EXCLUDED.generation_type,
                    business_domain = EXCLUDED.business_domain,
                    calculation_logic = EXCLUDED.calculation_logic,
                    implementation_ref = EXCLUDED.implementation_ref,
                    prompt_scene = EXCLUDED.prompt_scene,
                    is_system = TRUE,
                    updated_time = CURRENT_TIMESTAMP
                """,
                LINEAGE_NODE_SEEDS,
            )
            cur.executemany(
                """
                INSERT INTO data_asset.system_lineage_edge
                  (upstream_code, downstream_code, relation_type, relation_description, is_system)
                VALUES (%(upstream_code)s, %(downstream_code)s, %(relation_type)s, %(relation_description)s, TRUE)
                ON CONFLICT (upstream_code, downstream_code, relation_type) DO UPDATE
                SET relation_description = EXCLUDED.relation_description,
                    is_system = TRUE,
                    updated_time = CURRENT_TIMESTAMP
                """,
                LINEAGE_EDGE_SEEDS,
            )
        conn.commit()


def list_lineage_nodes(
    q: str | None = None,
    node_kind: str | None = None,
    business_domain: str | None = None,
    generation_type: str | None = None,
    status: str | None = None,
    database_url: str = DATABASE_URL,
) -> dict[str, Any]:
    ensure_lineage_catalog(database_url)
    query = """
        SELECT n.*,
               count(DISTINCT incoming.edge_id)::bigint AS upstream_count,
               count(DISTINCT outgoing.edge_id)::bigint AS downstream_count
        FROM data_asset.system_lineage_node n
        LEFT JOIN data_asset.system_lineage_edge incoming ON incoming.downstream_code = n.lineage_code
        LEFT JOIN data_asset.system_lineage_edge outgoing ON outgoing.upstream_code = n.lineage_code
        WHERE (%s::text IS NULL OR n.lineage_name ILIKE %s OR n.lineage_code ILIKE %s)
          AND (%s::text IS NULL OR n.node_kind = %s)
          AND (%s::text IS NULL OR n.business_domain = %s)
          AND (%s::text IS NULL OR n.generation_type = %s)
          AND (%s::text IS NULL OR n.status = %s)
        GROUP BY n.lineage_id
        ORDER BY n.status = 'deprecated', n.business_domain, n.node_kind, n.lineage_name
    """
    keyword = f"%{str(q or '').strip()}%" if str(q or "").strip() else None
    params = (keyword, keyword, keyword, node_kind, node_kind, business_domain, business_domain, generation_type, generation_type, status, status)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            nodes = [public_lineage_node(dict(row)) for row in cur.fetchall()]
    return {"summary": build_lineage_summary(nodes), "nodes": nodes}


def get_lineage_detail(lineage_code: str, database_url: str = DATABASE_URL) -> dict[str, Any] | None:
    ensure_lineage_catalog(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM data_asset.system_lineage_node WHERE lineage_code = %s", (lineage_code,))
            row = cur.fetchone()
            if row is None:
                return None
            node = public_lineage_node(dict(row))
            cur.execute(
                """
                SELECT e.*, n.lineage_name, n.node_kind, n.generation_type, n.business_domain, n.status
                FROM data_asset.system_lineage_edge e
                JOIN data_asset.system_lineage_node n ON n.lineage_code = e.upstream_code
                WHERE e.downstream_code = %s ORDER BY n.lineage_name
                """,
                (lineage_code,),
            )
            upstream = [normalize_row(dict(item)) for item in cur.fetchall()]
            cur.execute(
                """
                SELECT e.*, n.lineage_name, n.node_kind, n.generation_type, n.business_domain, n.status
                FROM data_asset.system_lineage_edge e
                JOIN data_asset.system_lineage_node n ON n.lineage_code = e.downstream_code
                WHERE e.upstream_code = %s ORDER BY n.lineage_name
                """,
                (lineage_code,),
            )
            downstream = [normalize_row(dict(item)) for item in cur.fetchall()]
            cur.execute(
                "SELECT lineage_code, lineage_name, node_kind, business_domain FROM data_asset.system_lineage_node WHERE lineage_code <> %s ORDER BY lineage_name",
                (lineage_code,),
            )
            available_nodes = [normalize_row(dict(item)) for item in cur.fetchall()]
    edges = [{key: item.get(key) for key in ("edge_id", "upstream_code", "downstream_code", "relation_type", "relation_description", "is_system")} for item in upstream + downstream]
    return {"node": node, "upstream": upstream, "downstream": downstream, "edges": edges, "available_nodes": available_nodes}


def create_lineage_node(payload: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    ensure_lineage_catalog(database_url)
    values = validate_node_payload(payload)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO data_asset.system_lineage_node
                  (lineage_code, lineage_name, node_kind, generation_type, business_domain,
                   business_definition, calculation_logic, implementation_ref, prompt_scene, owner, status, is_system)
                VALUES (%(lineage_code)s, %(lineage_name)s, %(node_kind)s, %(generation_type)s, %(business_domain)s,
                        %(business_definition)s, %(calculation_logic)s, %(implementation_ref)s, %(prompt_scene)s,
                        %(owner)s, %(status)s, FALSE)
                RETURNING *
                """,
                values,
            )
            row = cur.fetchone()
        conn.commit()
    return public_lineage_node(dict(row))


def update_lineage_node(lineage_code: str, payload: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any] | None:
    ensure_lineage_catalog(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT is_system FROM data_asset.system_lineage_node WHERE lineage_code = %s",
                (lineage_code,),
            )
            existing = cur.fetchone()
            if existing is None:
                return None
            values = validate_node_update(payload, is_system=bool(existing["is_system"]))
            assignments = ", ".join(f"{field} = %({field})s" for field in values)
            values["lineage_code"] = lineage_code
            cur.execute(
                f"UPDATE data_asset.system_lineage_node SET {assignments}, updated_time = CURRENT_TIMESTAMP "
                "WHERE lineage_code = %(lineage_code)s RETURNING *",
                values,
            )
            row = cur.fetchone()
        conn.commit()
    return public_lineage_node(dict(row))


def create_lineage_edge(payload: dict[str, Any], database_url: str = DATABASE_URL) -> dict[str, Any]:
    ensure_lineage_catalog(database_url)
    values = validate_edge_payload(payload)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT lineage_code FROM data_asset.system_lineage_node WHERE lineage_code IN (%s, %s)",
                (values["upstream_code"], values["downstream_code"]),
            )
            if len(cur.fetchall()) != 2:
                raise ValueError("上游或下游节点不存在")
            cur.execute(
                """
                INSERT INTO data_asset.system_lineage_edge
                  (upstream_code, downstream_code, relation_type, relation_description, is_system)
                VALUES (%(upstream_code)s, %(downstream_code)s, %(relation_type)s, %(relation_description)s, FALSE)
                RETURNING *
                """,
                values,
            )
            row = cur.fetchone()
        conn.commit()
    return normalize_row(dict(row))


def delete_lineage_edge(edge_id: int, database_url: str = DATABASE_URL) -> bool:
    ensure_lineage_catalog(database_url)
    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM data_asset.system_lineage_edge WHERE edge_id = %s AND is_system = FALSE RETURNING edge_id",
                (edge_id,),
            )
            deleted = cur.fetchone() is not None
        conn.commit()
    return deleted
