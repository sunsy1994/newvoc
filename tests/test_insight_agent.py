from __future__ import annotations


def evidence_comments(count: int) -> list[dict[str, str]]:
    return [{"comment_id": f"comment_{index}", "comment_text": f"用户评论 {index}"} for index in range(count)]


def test_evidence_gate_accepts_one_strong_match_with_ten_comments() -> None:
    from app.agents.insight.tools import evaluate_evidence_gate

    result = evaluate_evidence_gate(
        [{"event_id": "event_1", "similarity": "strong", "evidence_comments": evidence_comments(10)}]
    )

    assert result == {
        "status": "completed",
        "strong_count": 1,
        "medium_count": 0,
        "comment_count": 10,
    }


def test_evidence_gate_accepts_two_medium_matches_with_ten_comments() -> None:
    from app.agents.insight.tools import evaluate_evidence_gate

    result = evaluate_evidence_gate(
        [
            {"event_id": "event_1", "similarity": "medium", "evidence_comments": evidence_comments(5)},
            {"event_id": "event_2", "similarity": "medium", "evidence_comments": evidence_comments(5)},
        ]
    )

    assert result["status"] == "completed"
    assert result["medium_count"] == 2
    assert result["comment_count"] == 10


def test_evidence_gate_returns_partial_for_related_but_incomplete_matches() -> None:
    from app.agents.insight.tools import evaluate_evidence_gate

    result = evaluate_evidence_gate(
        [{"event_id": "event_1", "similarity": "medium", "evidence_comments": evidence_comments(10)}]
    )

    assert result["status"] == "partial"


def test_evidence_gate_rejects_missing_or_insufficient_comments() -> None:
    from app.agents.insight.tools import evaluate_evidence_gate

    assert evaluate_evidence_gate([])["status"] == "insufficient_data"
    result = evaluate_evidence_gate(
        [{"event_id": "event_1", "similarity": "strong", "evidence_comments": evidence_comments(9)}]
    )
    assert result["status"] == "insufficient_data"
    assert result["comment_count"] == 9


def test_list_candidate_events_prioritizes_model_brand_then_cross_brand(monkeypatch) -> None:
    from app.agents.insight import tools

    monkeypatch.setattr(
        tools,
        "list_voc_events",
        lambda limit=100: {
            "events": [
                {"event_id": "cross", "event_name": "竞品配置调整", "brand_name": "竞品", "model_name": "C车"},
                {"event_id": "brand", "event_name": "品牌价格权益", "brand_name": "品牌A", "model_name": "B车"},
                {"event_id": "model", "event_name": "A车改款上市", "brand_name": "品牌A", "model_name": "A车"},
            ]
        },
    )

    result = tools.list_candidate_events(
        {"action_type": "配置减少", "affected_aspects": ["座椅通风"], "brand_name": "品牌A", "model_name": "A车"}
    )

    assert [item["event_id"] for item in result] == ["model", "brand", "cross"]
    assert [item["relation_type"] for item in result] == ["same_model", "same_brand", "cross_brand"]


def test_list_candidate_events_prioritizes_matching_action_within_relation(monkeypatch) -> None:
    from app.agents.insight import tools

    monkeypatch.setattr(
        tools,
        "list_voc_events",
        lambda limit=100: {
            "events": [
                {"event_id": "unrelated", "event_name": "品牌传播活动", "event_type": "品牌传播"},
                {"event_id": "matched", "event_name": "新款配置调整", "event_type": "产品质量"},
            ]
        },
    )

    result = tools.list_candidate_events({"action_type": "配置减少", "affected_aspects": ["座椅通风"]})

    assert [item["event_id"] for item in result] == ["matched", "unrelated"]


def test_get_event_reaction_evidence_combines_real_product_and_sales_comments(monkeypatch) -> None:
    from app.agents.insight import tools

    monkeypatch.setattr(tools, "get_voc_event_market_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "get_voc_event_product_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "get_voc_event_sales_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "build_market_report_context", lambda payload: {"feedback_quality": {"positive_rate": 40}})
    monkeypatch.setattr(
        tools,
        "build_product_report_context",
        lambda payload: {
            "product_focus": {"aspects": [{"aspect": "配置", "comment_count": 12}]},
            "evidence_comments": [
                {"comment_id": "comment_1", "comment_text": "减配后价格也要降", "platform": "抖音"},
            ],
        },
    )
    monkeypatch.setattr(
        tools,
        "build_sales_report_context",
        lambda payload: {
            "lead_source": {
                "lead_comments": [
                    {"comment_id": "comment_2", "comment_text": "价格合适可以考虑", "purchase_signal": "中"},
                ]
            }
        },
    )

    result = tools.get_event_reaction_evidence(
        {"event_id": "event_1", "event_name": "配置调整", "relation_type": "cross_brand"}
    )

    assert result["event"]["relation_type"] == "cross_brand"
    assert [item["comment_id"] for item in result["evidence_comments"]] == ["comment_1", "comment_2"]
    assert result["market"]["feedback_quality"]["positive_rate"] == 40


def test_get_event_reaction_evidence_uses_scenario_aspects_for_relevant_comments(monkeypatch) -> None:
    from app.agents.insight import tools

    monkeypatch.setattr(tools, "get_voc_event_market_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "get_voc_event_product_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "get_voc_event_sales_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "build_market_report_context", lambda payload: {})
    monkeypatch.setattr(tools, "build_product_report_context", lambda payload: {"evidence_comments": []})
    monkeypatch.setattr(tools, "build_sales_report_context", lambda payload: {"lead_source": {"lead_comments": []}})
    captured = []

    def fake_comments(event_id: str, aspect: str, limit: int = 20) -> dict:
        captured.append((event_id, aspect, limit))
        return {"comments": [{"comment_id": "relevant_1", "comment_text": "座椅通风不能减"}]}

    monkeypatch.setattr(tools, "get_voc_event_discussion_point_comments", fake_comments)

    result = tools.get_event_reaction_evidence(
        candidate_event(),
        {"affected_aspects": ["座椅通风"]},
    )

    assert captured == [("event_1", "座椅通风", 20)]
    assert result["evidence_comments"][0]["comment_id"] == "relevant_1"


def test_get_event_reaction_evidence_excludes_unrelated_fallback_comments(monkeypatch) -> None:
    from app.agents.insight import tools

    monkeypatch.setattr(tools, "get_voc_event_market_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "get_voc_event_product_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "get_voc_event_sales_dashboard", lambda event_id: {"event": {"event_id": event_id}})
    monkeypatch.setattr(tools, "build_market_report_context", lambda payload: {})
    monkeypatch.setattr(
        tools,
        "build_product_report_context",
        lambda payload: {"evidence_comments": [{"comment_id": "appearance", "aspect": "外观", "comment_text": "外观很好看"}]},
    )
    monkeypatch.setattr(
        tools,
        "build_sales_report_context",
        lambda payload: {"lead_source": {"lead_comments": [{"comment_id": "price", "comment_text": "价格合适可以考虑"}]}},
    )
    monkeypatch.setattr(
        tools,
        "get_voc_event_discussion_point_comments",
        lambda event_id, aspect, limit=20: {"comments": []},
    )

    result = tools.get_event_reaction_evidence(candidate_event(), {"affected_aspects": ["座椅通风"]})

    assert result["evidence_comments"] == []


def candidate_event(event_id: str = "event_1", relation_type: str = "cross_brand") -> dict[str, str]:
    return {
        "event_id": event_id,
        "event_name": "竞品配置调整",
        "brand_name": "竞品品牌",
        "model_name": "竞品车型",
        "relation_type": relation_type,
    }


def ranked_scenario(similarity: str = "strong") -> dict:
    return {
        "status": "ready",
        "clarification_question": "",
        "scenario": {
            "action_type": "配置减少",
            "affected_aspects": ["座椅通风"],
            "compensation": ["价格降低1万元"],
            "target": "新款车型",
            "brand_name": "品牌A",
            "model_name": "A车",
            "expected_scope": "上市后用户反应",
        },
        "ranked_events": [
            {"event_id": "event_1", "similarity": similarity, "similarities": ["配置调整"], "differences": ["跨品牌"]}
        ],
    }


def completed_simulation() -> dict:
    return {
        "reaction_cards": [
            {
                "reaction": "反对",
                "strength": "主要",
                "summary": "配置关注用户可能质疑价值感。",
                "audiences": ["配置关注用户"],
                "reasons": ["历史配置调整事件中相关质疑集中"],
                "evidence_event_ids": ["event_1"],
            }
        ],
        "audience_cards": [],
        "impact_cards": [],
        "expression_themes": ["质疑减配后的产品价值"],
        "limitations": ["缺少同车型历史事件"],
    }


def patch_completed_insight_dependencies(monkeypatch, *, similarity: str = "strong", comment_count: int = 10) -> None:
    from app.agents.insight import graph

    monkeypatch.setattr(graph.tools, "list_candidate_events", lambda scenario, event_id=None, limit=30: [candidate_event()])
    monkeypatch.setattr(graph.parser, "parse_and_rank", lambda question, candidates, history: ranked_scenario(similarity))
    monkeypatch.setattr(
        graph.tools,
        "get_event_reaction_evidence",
        lambda candidate, scenario=None: {
            "event": candidate,
            "market": {},
            "product": {},
            "sales": {},
            "evidence_comments": evidence_comments(comment_count),
        },
    )


def test_insight_agent_returns_clarification_before_evidence_collection(monkeypatch) -> None:
    from app.agents.insight import graph

    monkeypatch.setattr(graph.tools, "list_candidate_events", lambda scenario, event_id=None, limit=30: [candidate_event()])
    monkeypatch.setattr(
        graph.parser,
        "parse_and_rank",
        lambda question, candidates, history: {
            "status": "needs_clarification",
            "scenario": {"action_type": "配置减少", "affected_aspects": []},
            "clarification_question": "你准备减少哪项配置？",
            "ranked_events": [],
        },
    )
    monkeypatch.setattr(
        graph.tools,
        "get_event_reaction_evidence",
        lambda candidate: (_ for _ in ()).throw(AssertionError("澄清前不应获取证据")),
    )

    result = graph.run_insight_agent("我准备减配")

    assert result["status"] == "needs_clarification"
    assert result["answer"] == "你准备减少哪项配置？"
    assert result["requires_clarification"] is True


def test_insight_agent_does_not_simulate_when_comments_are_insufficient(monkeypatch) -> None:
    from app.agents.insight import graph

    patch_completed_insight_dependencies(monkeypatch, comment_count=9)
    monkeypatch.setattr(
        graph.parser,
        "simulate_reactions",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("证据不足时不应推演")),
    )

    result = graph.run_insight_agent("如果取消座椅通风但降价1万元，用户会怎么说？")

    assert result["status"] == "insufficient_data"
    assert "暂无此类数据推演" in result["answer"]
    assert result["insight_result"]["reaction_cards"] == []


def test_insight_agent_returns_partial_without_full_reaction_cards(monkeypatch) -> None:
    from app.agents.insight import graph

    patch_completed_insight_dependencies(monkeypatch, similarity="medium", comment_count=10)
    monkeypatch.setattr(
        graph.parser,
        "simulate_reactions",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("部分匹配时不应形成完整推演")),
    )

    result = graph.run_insight_agent("如果取消座椅通风但降价1万元，用户会怎么说？")

    assert result["status"] == "partial"
    assert result["insight_result"]["status"] == "partial"
    assert result["insight_result"]["reaction_cards"] == []
    assert result["insight_result"]["similar_events"][0]["relation_type"] == "cross_brand"


def test_insight_agent_returns_completed_cards_with_system_evidence(monkeypatch) -> None:
    from app.agents.insight import graph

    patch_completed_insight_dependencies(monkeypatch)
    monkeypatch.setattr(graph.parser, "simulate_reactions", lambda scenario, events: completed_simulation())
    monkeypatch.setattr(graph.parser, "revise_simulation", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("合格结果不应修正")))

    result = graph.run_insight_agent("如果取消座椅通风但降价1万元，用户会怎么说？")

    assert result["status"] == "completed"
    assert result["react_rounds"] == 2
    assert result["insight_result"]["reaction_cards"][0]["reaction"] == "反对"
    assert len(result["insight_result"]["evidence_comments"]) == 10
    assert result["insight_result"]["similar_events"][0]["relation_type"] == "cross_brand"
    assert all("%" not in str(card) for card in result["insight_result"]["reaction_cards"])


def test_parse_and_rank_prompt_combines_scenario_and_candidate_judgement(monkeypatch) -> None:
    from app.agents.insight import parser

    captured = {}
    monkeypatch.setattr(parser, "resolve_runtime_config", lambda *args: ("http://llm", "key", "model", 30))

    def fake_call(prompt: str, **kwargs) -> dict:
        captured["prompt"] = prompt
        return ranked_scenario()

    monkeypatch.setattr(parser, "call_openai_compatible_json", fake_call)

    result = parser.parse_and_rank("取消座椅通风并降价", [candidate_event()], [])

    assert result["scenario"]["affected_aspects"] == ["座椅通风"]
    assert "候选事件" in captured["prompt"]
    assert "strong、medium、irrelevant" in captured["prompt"]
    assert "缺少关键条件" in captured["prompt"]


def test_review_simulation_flags_percentages_and_unknown_evidence_ids() -> None:
    from app.agents.insight.graph import review_simulation

    issues = review_simulation(
        {
            "reaction_cards": [
                {
                    "summary": "预计60%的用户会反对。",
                    "evidence_event_ids": ["unknown_event"],
                }
            ]
        },
        accepted_event_ids={"event_1"},
    )

    assert "不得生成精确反应百分比" in issues
    assert "结论引用了未通过证据门槛的事件" in issues
