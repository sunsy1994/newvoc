from __future__ import annotations


def test_lineage_seeds_cover_business_generation_types() -> None:
    from app.services.data_lineage import LINEAGE_NODE_SEEDS

    assert {item["generation_type"] for item in LINEAGE_NODE_SEEDS} >= {
        "raw_fact",
        "direct_aggregation",
        "derived_metric",
        "rule_judgement",
        "llm_label",
        "llm_summary",
        "consumer_only",
    }


def test_lineage_seed_codes_are_unique_and_cover_four_agents() -> None:
    from app.services.data_lineage import LINEAGE_NODE_SEEDS

    codes = [item["lineage_code"] for item in LINEAGE_NODE_SEEDS]

    assert len(codes) == len(set(codes))
    assert {
        "agent.data_question.output",
        "agent.qa.output",
        "agent.report.output",
        "agent.insight.output",
    }.issubset(codes)


def test_lineage_seed_edges_only_reference_existing_nodes_and_are_unique() -> None:
    from app.services.data_lineage import LINEAGE_EDGE_SEEDS, LINEAGE_NODE_SEEDS

    codes = {item["lineage_code"] for item in LINEAGE_NODE_SEEDS}
    keys = [
        (item["upstream_code"], item["downstream_code"], item["relation_type"])
        for item in LINEAGE_EDGE_SEEDS
    ]

    assert all(upstream in codes and downstream in codes for upstream, downstream, _ in keys)
    assert len(keys) == len(set(keys))
    assert all(upstream != downstream for upstream, downstream, _ in keys)


def test_competitor_report_lineage_traces_deterministic_and_llm_stages() -> None:
    from app.services.data_lineage import LINEAGE_EDGE_SEEDS, LINEAGE_NODE_SEEDS

    nodes = {item["lineage_code"]: item for item in LINEAGE_NODE_SEEDS}

    assert {
        code: (nodes[code]["node_kind"], nodes[code]["generation_type"])
        for code in (
            "source.competitor.work_facts",
            "source.competitor.insight_markdown",
            "metric.competitor.total_engagement",
            "rule.competitor.top3",
            "summary.competitor.report_prose",
            "agent.competitor_report.output",
        )
    } == {
        "source.competitor.work_facts": ("source_field", "raw_fact"),
        "source.competitor.insight_markdown": ("source_field", "raw_fact"),
        "metric.competitor.total_engagement": ("metric", "derived_metric"),
        "rule.competitor.top3": ("rule", "rule_judgement"),
        "summary.competitor.report_prose": ("ai_summary", "llm_summary"),
        "agent.competitor_report.output": ("agent_output", "consumer_only"),
    }
    assert nodes["source.competitor.insight_markdown"]["implementation_ref"] == (
        "data_asset.competitor_work_insight.insight_markdown"
    )

    edges = {
        (item["upstream_code"], item["downstream_code"], item["relation_type"])
        for item in LINEAGE_EDGE_SEEDS
    }
    assert {
        ("source.competitor.work_facts", "metric.competitor.total_engagement", "calculates_to"),
        ("source.competitor.work_facts", "rule.competitor.top3", "rules_to"),
        ("metric.competitor.total_engagement", "rule.competitor.top3", "rules_to"),
        ("rule.competitor.top3", "summary.competitor.report_prose", "summarized_by"),
        ("source.competitor.insight_markdown", "summary.competitor.report_prose", "summarized_by"),
        ("summary.competitor.report_prose", "agent.competitor_report.output", "consumed_by"),
    }.issubset(edges)


def test_build_lineage_summary_counts_business_types_and_missing_definitions() -> None:
    from app.services.data_lineage import build_lineage_summary

    summary = build_lineage_summary(
        [
            {"node_kind": "metric", "generation_type": "direct_aggregation", "business_definition": "帖子去重计数"},
            {"node_kind": "rule", "generation_type": "rule_judgement", "business_definition": ""},
            {"node_kind": "llm_label", "generation_type": "llm_label", "business_definition": "评论情绪分类"},
            {"node_kind": "ai_summary", "generation_type": "llm_summary", "business_definition": None},
        ]
    )

    assert summary == {
        "node_count": 4,
        "metric_count": 1,
        "rule_count": 1,
        "llm_label_count": 1,
        "ai_summary_count": 1,
        "incomplete_definition_count": 2,
    }


def test_public_lineage_node_marks_llm_generation_types() -> None:
    from app.services.data_lineage import public_lineage_node

    assert public_lineage_node({"generation_type": "llm_label"})["uses_llm"] is True
    assert public_lineage_node({"generation_type": "llm_summary"})["uses_llm"] is True
    assert public_lineage_node({"generation_type": "derived_metric"})["uses_llm"] is False


def test_system_node_update_only_accepts_business_fields() -> None:
    from app.services.data_lineage import validate_node_update

    assert validate_node_update(
        {"business_definition": "新的业务口径", "owner": "产品部", "status": "active"},
        is_system=True,
    ) == {"business_definition": "新的业务口径", "owner": "产品部", "status": "active"}

    try:
        validate_node_update({"calculation_logic": "COUNT(*)"}, is_system=True)
    except ValueError as exc:
        assert "系统节点" in str(exc)
    else:
        raise AssertionError("system technical fields must be protected")


def test_custom_node_payload_requires_valid_enums_and_code() -> None:
    from app.services.data_lineage import validate_node_payload

    valid = validate_node_payload(
        {
            "lineage_code": "metric.custom_conversion",
            "lineage_name": "自定义转化率",
            "node_kind": "metric",
            "generation_type": "derived_metric",
            "business_domain": "sales",
        }
    )
    assert valid["status"] == "draft"
    assert valid["is_system"] is False

    for field, value in (("node_kind", "unknown"), ("generation_type", "manual"), ("business_domain", "finance")):
        payload = dict(valid)
        payload[field] = value
        try:
            validate_node_payload(payload)
        except ValueError as exc:
            assert field in str(exc)
        else:
            raise AssertionError(f"invalid {field} must be rejected")


def test_lineage_edge_rejects_self_reference_and_invalid_relation() -> None:
    from app.services.data_lineage import validate_edge_payload

    try:
        validate_edge_payload(
            {"upstream_code": "metric.a", "downstream_code": "metric.a", "relation_type": "depends_on"}
        )
    except ValueError as exc:
        assert "自身" in str(exc)
    else:
        raise AssertionError("self-referencing edge must be rejected")

    try:
        validate_edge_payload(
            {"upstream_code": "metric.a", "downstream_code": "metric.b", "relation_type": "unknown"}
        )
    except ValueError as exc:
        assert "relation_type" in str(exc)
    else:
        raise AssertionError("invalid relation type must be rejected")
