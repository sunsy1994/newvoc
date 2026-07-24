from __future__ import annotations


def sample_market_dashboard() -> dict:
    return {
        "event": {
            "event_id": "event_001",
            "event_name": "ID.AURA T6 launch",
            "brand_name": "FAW-Volkswagen",
            "model_name": "ID.AURA T6",
            "event_type": "new_launch",
            "event_status": "active",
            "start_time": "2026-05-10",
            "end_time": "2026-05-24",
        },
        "overview_metrics": {
            "total_volume": 273,
            "content_count": 20,
            "comment_count": 253,
            "kol_count": 3,
            "kol_content_count": 8,
            "total_engagement": 12000,
        },
        "volume_rhythm": {
            "summary": {
                "rhythm_type": "burst",
                "peak_date": "2026-05-17",
                "peak_volume": 211,
                "peak_volume_rate": 77.3,
                "has_secondary_peak": False,
                "rule_based_conclusion": "The event volume concentrated on one peak day.",
            }
        },
        "volume_trend": [
            {"date": "2026-05-16", "content_count": 2, "comment_count": 18, "total_volume": 20},
            {"date": "2026-05-17", "content_count": 8, "comment_count": 203, "total_volume": 211},
        ],
        "subject_story": {
            "summary": {
                "dominant_subject_type": "KOL",
                "kol_engagement_rate": 68.5,
                "top_kol_type": "vehicle review KOL",
                "rule_based_conclusion": "KOL content drove most of the engagement.",
            },
            "top_authors": [{"author_name": "Auto Reviewer A", "content_count": 3, "total_engagement": 6000}],
        },
        "platform_story": {
            "summary": {
                "core_platform": "Douyin",
                "core_platform_volume_rate": 82.1,
                "core_platform_effective_comment_rate": 84.3,
                "core_platform_purchase_signal_rate": 19.8,
                "rule_based_conclusion": "Douyin contributed the main event volume.",
            },
            "platform_efficiency": [{"platform": "Douyin", "total_volume": 220, "engagement_per_content": 1500.0}],
        },
        "comment_quality": {
            "summary": {
                "labeled_comment_count": 253,
                "vehicle_related_rate": 84.3,
                "top_aspect": "appearance",
                "top_intent": "purchase intention",
                "positive_rate": 52.4,
                "negative_rate": 12.8,
                "mid_high_purchase_signal_rate": 19.8,
                "rule_based_conclusion": "Users discussed appearance with visible purchase signals.",
            },
            "sentiment_distribution": [
                {"label": "positive", "count": 120, "rate": 52.4},
                {"label": "other", "count": 109, "rate": 47.6},
            ],
            "purchase_signal_distribution": [{"label": "strong", "count": 18, "rate": 7.1}],
        },
        "user_profile_distribution": [{"main_label": "family travel", "user_cnt": 51}],
        "regional_response_story": {"summary": {"top_location": "Shanghai", "top_location_comment_rate": 31.2}},
        "topic_spread_story": {
            "summary": {
                "top_topic": "#T6",
                "topic_count": 6,
                "top_topic_comment_count": 120,
                "rule_based_conclusion": "#T6 是讨论最集中的话题。",
            },
            "topics": [{"topic": "#T6", "content_count": 6, "comment_count": 120, "total_engagement": 9000}],
        },
        "hot_posts": [{"title": "T6 real experience", "total_engagement": 9000, "platform": "Douyin"}],
    }


def test_build_market_report_context_keeps_business_story_sections() -> None:
    from app.services.report_agent import build_market_report_context

    context = build_market_report_context(sample_market_dashboard())

    assert context["event_overview"]["event_name"] == "ID.AURA T6 launch"
    assert context["event_overview"]["start_time"] == "2026-05-10"
    assert context["scale"]["total_volume"] == 273
    assert context["rhythm"]["rhythm_type"] == "burst"
    assert context["volume_trend"][1]["date"] == "2026-05-17"
    assert context["volume_trend"][1]["content_count"] == 8
    assert context["volume_trend"][1]["comment_count"] == 203
    assert context["hot_topics"]["summary"]["top_topic"] == "#T6"
    assert context["kol_and_authors"]["summary"]["top_kol_type"] == "vehicle review KOL"
    assert context["audience"]["user_profile_distribution"][0]["main_label"] == "family travel"
    assert context["feedback_quality"]["summary"]["mid_high_purchase_signal_rate"] == 19.8
    assert context["evidence"]["hot_posts"][0]["title"] == "T6 real experience"


def test_render_market_report_prompt_injects_json_context() -> None:
    from app.services.report_agent import render_market_report_prompt

    prompt = render_market_report_prompt(
        "Summarize the market dashboard.\nInput:\n{{market_context_json}}",
        {"event_overview": {"event_name": "ID.AURA T6 launch"}},
    )

    assert "{{market_context_json}}" not in prompt
    assert '"event_name": "ID.AURA T6 launch"' in prompt
    assert "只使用给定信息" in prompt


def test_normalize_report_narrative_uses_fixed_fields_and_rule_based_fallbacks() -> None:
    from app.services.report_agent import normalize_report_narrative

    narrative = normalize_report_narrative(
        {
            "headline": "  测试标题  ",
            "executive_summary": "测试摘要",
            "section_insights": {
                "market_rhythm": " ",
                "market_topics": "话题判断",
                "unexpected": "不得透传",
            },
            "data_notes": [" 评论位置不代表用户真实所在地。 ", ""],
        },
        ("market_rhythm", "market_topics", "market_platforms", "market_feedback"),
        {
            "market_rhythm": "节奏规则结论",
            "market_platforms": "平台规则结论",
        },
    )

    assert narrative == {
        "headline": "测试标题",
        "executive_summary": "测试摘要",
        "section_insights": {
            "market_rhythm": "节奏规则结论",
            "market_topics": "话题判断",
            "market_platforms": "平台规则结论",
            "market_feedback": "",
        },
        "data_notes": ["评论位置不代表用户真实所在地。"],
    }


def test_run_market_report_agent_returns_fixed_narrative_and_builder_charts(monkeypatch) -> None:
    from app.services import report_agent

    captured = {}
    monkeypatch.setattr(report_agent, "get_voc_event_market_dashboard", lambda event_id, database_url=None: sample_market_dashboard())
    monkeypatch.setattr(
        report_agent,
        "get_runtime_ai_config",
        lambda database_url=None: {
            "base_url": "https://llm.example/v1",
            "api_key": "secret",
            "model_name": "report-model",
            "timeout_seconds": 30,
        },
    )
    monkeypatch.setattr(
        report_agent,
        "get_default_prompt_template",
        lambda scene, database_url=None: {
            "prompt_version": "market_report_v2",
            "prompt_content": (
                '{"headline":"","executive_summary":"","section_insights":'
                '{"market_rhythm":"","market_topics":"","market_platforms":"","market_feedback":""},'
                '"data_notes":[]}\n{{market_context_json}}'
            ),
        },
    )

    def fake_call(prompt, *, base_url, api_key, model, timeout_seconds):
        captured.update({"prompt": prompt, "base_url": base_url, "api_key": api_key, "model": model, "timeout_seconds": timeout_seconds})
        return {
            "headline": "测试标题",
            "executive_summary": "测试摘要",
            "section_insights": {
                "market_rhythm": "节奏判断",
                "market_topics": "话题判断",
                "market_platforms": "平台判断",
                "market_feedback": "反馈判断",
            },
            "data_notes": [],
            "structured_report": {
                "charts": [{"chart_id": "llm-chart", "template_id": "F4", "data": [{"value": 999}]}],
            },
        }

    monkeypatch.setattr(report_agent, "call_openai_compatible_json", fake_call)
    monkeypatch.setattr(report_agent, "save_market_report_agent_result", lambda result, database_url=None: result)

    result = report_agent.run_market_report_agent("event_001")

    assert result["event_id"] == "event_001"
    assert result["prompt_version"] == "market_report_v2"
    assert result["summary"]["report_narrative"] == {
        "headline": "测试标题",
        "executive_summary": "测试摘要",
        "section_insights": {
            "market_rhythm": "节奏判断",
            "market_topics": "话题判断",
            "market_platforms": "平台判断",
            "market_feedback": "反馈判断",
        },
        "data_notes": [],
    }
    charts = result["summary"]["structured_report"]["charts"]
    assert [chart["template_id"] for chart in charts] == ["F3", "F5", "F8", "L14"]
    assert [chart["insight"] for chart in charts] == ["节奏判断", "话题判断", "平台判断", "反馈判断"]
    assert charts[0]["data"] == result["context"]["volume_trend"]
    assert charts[2]["data"][0]["engagement_per_content"] == 1500.0
    assert all(chart["chart_id"] != "llm-chart" for chart in charts)
    assert result["context"]["event_overview"]["event_name"] == "ID.AURA T6 launch"
    assert result["rendered_prompt"] == captured["prompt"]
    assert "ID.AURA T6 launch" in result["rendered_prompt"]
    assert captured["base_url"] == "https://llm.example/v1"
    assert captured["model"] == "report-model"


def test_run_market_report_agent_falls_back_to_builtin_prompt(monkeypatch) -> None:
    from app.services import report_agent

    monkeypatch.setattr(report_agent, "get_voc_event_market_dashboard", lambda event_id, database_url=None: sample_market_dashboard())
    monkeypatch.setattr(
        report_agent,
        "get_runtime_ai_config",
        lambda database_url=None: {
            "base_url": "https://llm.example/v1",
            "api_key": "secret",
            "model_name": "report-model",
            "timeout_seconds": 30,
        },
    )
    monkeypatch.setattr(report_agent, "get_default_prompt_template", lambda scene, database_url=None: (_ for _ in ()).throw(ValueError("missing")))
    monkeypatch.setattr(report_agent, "call_openai_compatible_json", lambda *args, **kwargs: {})
    monkeypatch.setattr(report_agent, "save_market_report_agent_result", lambda result, database_url=None: result)

    result = report_agent.run_market_report_agent("event_001")

    assert result["prompt_version"] == report_agent.DEFAULT_MARKET_REPORT_PROMPT_VERSION
    assert report_agent.DEFAULT_MARKET_REPORT_PROMPT_VERSION == "market_report_summary_v2"
    assert result["summary"]["report_narrative"]["section_insights"]["market_rhythm"] == "The event volume concentrated on one peak day."
    charts = result["summary"]["structured_report"]["charts"]
    assert [chart["template_id"] for chart in charts] == ["F3", "F5", "F8", "L14"]
    assert [chart["insight"] for chart in charts] == [
        "The event volume concentrated on one peak day.",
        "#T6 是讨论最集中的话题。",
        "Douyin contributed the main event volume.",
        "Users discussed appearance with visible purchase signals.",
    ]


def test_resolve_market_report_prompt_preserves_custom_content_and_appends_v2_contract(monkeypatch) -> None:
    from app.services import report_agent

    monkeypatch.setattr(
        report_agent,
        "get_default_prompt_template",
        lambda scene, database_url=None: {
            "prompt_version": "custom_market_report_v1",
            "prompt_content": 'Return {"report_markdown": ""}',
        },
    )

    prompt, version = report_agent.resolve_market_report_prompt()

    assert version == "custom_market_report_v1"
    assert prompt.startswith('Return {"report_markdown": ""}')
    assert report_agent.REPORT_PROMPT_CONTRACT_MARKER in prompt
    assert '"headline"' in prompt
    assert '"executive_summary"' in prompt
    assert '"market_rhythm"' in prompt


def test_custom_prompt_cannot_bypass_fixed_contract_by_mentioning_all_fields(monkeypatch) -> None:
    from app.services import report_agent

    custom = (
        '{"headline":"","executive_summary":"","section_insights":'
        '{"market_rhythm":"","market_topics":"","market_platforms":"","market_feedback":""},'
        '"data_notes":[],"structured_report":{"charts":[]}}'
    )
    monkeypatch.setattr(
        report_agent,
        "get_default_prompt_template",
        lambda scene, database_url=None: {
            "prompt_version": "custom_market_v7",
            "prompt_content": custom,
        },
    )

    prompt, version = report_agent.resolve_market_report_prompt()

    assert version == "custom_market_v7"
    assert prompt.startswith(custom)
    assert report_agent.REPORT_PROMPT_CONTRACT_MARKER in prompt
    assert "不得输出 report_markdown、structured_report 或图表数据" in prompt


def test_build_report_summary_rejects_llm_insight_when_chart_data_is_empty() -> None:
    from app.services.report_agent import build_report_summary

    summary = build_report_summary(
        {
            "headline": "测试标题",
            "executive_summary": "测试摘要",
            "section_insights": {"market_rhythm": "虚构的增长趋势"},
            "data_notes": [],
        },
        [
            {
                "chart_id": "market-volume-trend",
                "template_id": "F3",
                "title": "传播规模与节奏",
                "subtitle": "按日声量变化",
                "insight": "",
                "source_label": "volume_trend",
                "data": [],
                "meta": {"empty_reason": "暂无可用数据"},
            }
        ],
        ("market_rhythm",),
        {"market_rhythm": ""},
        {"market-volume-trend": "market_rhythm"},
    )

    assert summary["report_narrative"]["section_insights"]["market_rhythm"] == ""
    assert summary["structured_report"]["charts"][0]["insight"] == ""
    assert summary["report_narrative"]["headline"] == "暂无可用报告数据"
    assert summary["report_narrative"]["executive_summary"] == "当前数据不足，无法生成可靠报告结论。"


def test_build_report_summary_rejects_all_llm_copy_when_nonempty_chart_cannot_render() -> None:
    from app.services.report_agent import build_report_summary

    summary = build_report_summary(
        {
            "headline": "虚构的平台优势",
            "executive_summary": "虚构的摘要",
            "section_insights": {"market_platforms": "虚构的效率判断"},
            "data_notes": [],
        },
        [
            {
                "chart_id": "market-platform-efficiency",
                "template_id": "F8",
                "title": "平台传播效率",
                "subtitle": "规模与反馈效率",
                "insight": "",
                "source_label": "platform.platform_efficiency",
                "data": [{"platform": "抖音", "total_volume": 20}],
                "meta": {},
            }
        ],
        ("market_platforms",),
        {"market_platforms": "平台数据不足。"},
        {"market-platform-efficiency": "market_platforms"},
    )

    assert summary["report_narrative"] == {
        "headline": "暂无可用报告数据",
        "executive_summary": "当前数据不足，无法生成可靠报告结论。",
        "section_insights": {"market_platforms": "平台数据不足。"},
        "data_notes": [],
    }
    assert summary["structured_report"]["charts"][0]["insight"] == "平台数据不足。"


def test_normalize_report_narrative_rejects_non_strings_and_caps_lengths() -> None:
    from app.services import report_agent

    narrative = report_agent.normalize_report_narrative(
        {
            "headline": {"claim": "不得字符串化"},
            "executive_summary": ["不得", "字符串化"],
            "section_insights": {
                "market_rhythm": {"claim": "不得字符串化"},
                "market_topics": "话" * (report_agent.MAX_REPORT_SECTION_INSIGHT_LENGTH + 20),
            },
            "data_notes": [
                {"note": "不得字符串化"},
                42,
                *[
                    f"说明{index}" + "长" * report_agent.MAX_REPORT_DATA_NOTE_LENGTH
                    for index in range(report_agent.MAX_REPORT_DATA_NOTES + 3)
                ],
            ],
        },
        ("market_rhythm", "market_topics"),
        {"market_rhythm": "规则结论"},
    )

    assert narrative["headline"] == ""
    assert narrative["executive_summary"] == ""
    assert narrative["section_insights"]["market_rhythm"] == "规则结论"
    assert len(narrative["section_insights"]["market_topics"]) == report_agent.MAX_REPORT_SECTION_INSIGHT_LENGTH
    assert len(narrative["data_notes"]) == report_agent.MAX_REPORT_DATA_NOTES
    assert all(isinstance(note, str) for note in narrative["data_notes"])
    assert all(len(note) <= report_agent.MAX_REPORT_DATA_NOTE_LENGTH for note in narrative["data_notes"])

    bounded = report_agent.normalize_report_narrative(
        {
            "headline": "标" * (report_agent.MAX_REPORT_HEADLINE_LENGTH + 20),
            "executive_summary": "摘"
            * (report_agent.MAX_REPORT_EXECUTIVE_SUMMARY_LENGTH + 20),
            "section_insights": {},
            "data_notes": [],
        },
        (),
        {},
    )
    assert len(bounded["headline"]) == report_agent.MAX_REPORT_HEADLINE_LENGTH
    assert (
        len(bounded["executive_summary"])
        == report_agent.MAX_REPORT_EXECUTIVE_SUMMARY_LENGTH
    )


def test_normalize_cached_v1_report_keeps_markdown_without_inventing_charts() -> None:
    from app.services.report_agent import normalize_cached_report_row

    result = normalize_cached_report_row(
        {
            "event_id": "event_001",
            "prompt_version": "market_report_summary_v1",
            "generated_at": "2026-06-22T10:00:00",
            "summary_json": {
                "report_markdown": "# Cached Market Report",
                "data_notes": ["历史数据说明"],
            },
            "context_json": {"event_overview": {"event_name": "ID.AURA T6 launch"}},
            "rendered_prompt": "Cached prompt",
        }
    )

    assert result["summary"] == {
        "report_markdown": "# Cached Market Report",
        "data_notes": ["历史数据说明"],
    }
    assert "structured_report" not in result["summary"]


def test_normalize_partial_cached_report_prefers_legacy_markdown_without_empty_chart_spec() -> None:
    from app.services.report_agent import normalize_cached_report_row

    result = normalize_cached_report_row(
        {
            "event_id": "event_001",
            "prompt_version": "market_report_summary_v1",
            "summary_json": {
                "report_markdown": "# Cached Market Report",
                "data_notes": [],
                "structured_report": {},
            },
            "context_json": {},
            "rendered_prompt": "Cached prompt",
        }
    )

    assert result["summary"] == {
        "report_markdown": "# Cached Market Report",
        "data_notes": [],
    }
    assert "structured_report" not in result["summary"]


def test_normalize_partial_v2_shaped_cache_does_not_hide_legacy_markdown() -> None:
    from app.services.report_agent import normalize_cached_report_row

    result = normalize_cached_report_row(
        {
            "event_id": "event_001",
            "prompt_version": "market_report_summary_v2",
            "summary_json": {
                "report_markdown": "# Cached Market Report",
                "data_notes": [],
                "report_narrative": {},
                "structured_report": {"charts": []},
            },
            "context_json": {},
            "rendered_prompt": "Cached prompt",
        }
    )

    assert result["summary"] == {
        "report_markdown": "# Cached Market Report",
        "data_notes": [],
    }


def test_normalize_cache_with_unknown_template_does_not_hide_legacy_markdown() -> None:
    from app.services.report_agent import normalize_cached_report_row

    result = normalize_cached_report_row(
        {
            "event_id": "event_001",
            "prompt_version": "market_report_summary_v2",
            "summary_json": {
                "report_markdown": "# Cached Market Report",
                "data_notes": [],
                "report_narrative": {
                    "headline": "历史标题",
                    "executive_summary": "历史摘要",
                    "section_insights": {
                        "market_rhythm": "节奏",
                        "market_topics": "话题",
                        "market_platforms": "平台",
                        "market_feedback": "反馈",
                    },
                    "data_notes": [],
                },
                "structured_report": {
                    "charts": [
                        {
                            "chart_id": "market-volume-trend",
                            "template_id": "UNKNOWN",
                            "title": "错误模板",
                            "subtitle": "",
                            "insight": "",
                            "source_label": "",
                            "data": [],
                            "meta": {"empty_reason": "暂无可用数据"},
                        },
                        {
                            "chart_id": "market-hot-topics",
                            "template_id": "F5",
                            "title": "热门话题结构",
                            "subtitle": "按讨论量展示",
                            "insight": "话题",
                            "source_label": "hot_topics.topics",
                            "data": [{"topic": "外观", "comment_count": 8}],
                            "meta": {},
                        },
                        {
                            "chart_id": "market-platform-efficiency",
                            "template_id": "F8",
                            "title": "平台传播效率",
                            "subtitle": "规模与反馈效率",
                            "insight": "平台",
                            "source_label": "platform.platform_efficiency",
                            "data": [
                                {
                                    "platform": "抖音",
                                    "total_volume": 20,
                                    "engagement_per_content": 6,
                                }
                            ],
                            "meta": {},
                        },
                        {
                            "chart_id": "market-feedback-sentiment",
                            "template_id": "L14",
                            "title": "用户反馈构成",
                            "subtitle": "情感分布",
                            "insight": "反馈",
                            "source_label": "feedback_quality.sentiment_distribution",
                            "data": [
                                {"label": "正向", "rate": 70},
                                {"label": "负向", "rate": 30},
                            ],
                            "meta": {},
                        },
                    ]
                },
            },
            "context_json": {},
            "rendered_prompt": "Cached prompt",
        }
    )

    assert result["summary"]["report_markdown"] == "# Cached Market Report"
    assert "structured_report" not in result["summary"]


def test_known_v2_prompt_version_cannot_restore_another_department_contract() -> None:
    from app.services.report_agent import normalize_cached_report_row
    from app.services.report_visuals import build_product_report_charts

    charts = build_product_report_charts(
        {
            "product_focus": {
                "aspects": [
                    {
                        "aspect": "外观",
                        "mention_rate": 50,
                        "positive_rate": 70,
                        "negative_rate": 10,
                    }
                ]
            },
            "product_opportunity": {
                "surprise_points": [
                    {"aspect": "外观", "opportunity_score": 20},
                ]
            },
            "pko": {
                "evidence_comments": [
                    {
                        "comment_id": "pko-1",
                        "target": "竞品A",
                        "dimension": "空间",
                        "result": "优势",
                        "comment_text": "空间更好",
                    }
                ],
                "dimension_result_matrix": [
                    {"dimension": "空间", "advantage_count": 1},
                ],
            },
        }
    )
    result = normalize_cached_report_row(
        {
            "event_id": "event_001",
            "prompt_version": "market_report_summary_v2",
            "summary_json": {
                "report_markdown": "# 保留市场部历史报告",
                "report_narrative": {
                    "headline": "产品标题",
                    "executive_summary": "产品摘要",
                    "section_insights": {
                        "product_focus": "关注点",
                        "product_sentiment": "情感",
                        "product_opportunity": "机会",
                        "product_pko_relationships": "关系",
                        "product_pko_results": "结果",
                    },
                    "data_notes": [],
                },
                "structured_report": {"charts": charts},
            },
        }
    )

    assert result["summary"]["report_markdown"] == "# 保留市场部历史报告"
    assert "structured_report" not in result["summary"]


def test_cached_chart_with_mixed_invalid_rows_falls_back_to_markdown() -> None:
    from app.services.report_agent import normalize_cached_report_row
    from app.services.report_visuals import build_market_report_charts

    charts = build_market_report_charts(
        {
            "volume_trend": [{"date": "2026-07-01", "total_volume": 12}],
            "hot_topics": {"topics": [{"topic": "外观", "comment_count": 8}]},
            "platform": {
                "platform_efficiency": [
                    {
                        "platform": "抖音",
                        "total_volume": 20,
                        "engagement_per_content": 6,
                    }
                ]
            },
            "feedback_quality": {
                "sentiment_distribution": [
                    {"label": "正向", "rate": 70},
                    {"label": "负向", "rate": 30},
                ]
            },
        }
    )
    charts[2]["data"].append({"platform": "缺少二维坐标"})
    result = normalize_cached_report_row(
        {
            "event_id": "event_001",
            "prompt_version": "market_report_summary_v2",
            "summary_json": {
                "report_markdown": "# 保留历史报告",
                "report_narrative": {
                    "headline": "历史标题",
                    "executive_summary": "历史摘要",
                    "section_insights": {
                        "market_rhythm": "节奏",
                        "market_topics": "话题",
                        "market_platforms": "平台",
                        "market_feedback": "反馈",
                    },
                    "data_notes": [],
                },
                "structured_report": {"charts": charts},
            },
        }
    )

    assert result["summary"]["report_markdown"] == "# 保留历史报告"
    assert "structured_report" not in result["summary"]


def test_cached_chart_requires_fixed_system_metadata() -> None:
    from app.services import report_agent
    from app.services.report_visuals import build_market_report_charts

    chart = build_market_report_charts(
        {"volume_trend": [{"date": "2026-07-01", "total_volume": 12}]}
    )[0]
    chart["title"] = ""

    assert (
        report_agent._valid_cached_chart(
            chart,
            *report_agent.MARKET_REPORT_CHART_CONTRACT[0],
        )
        is False
    )


def test_normalize_cached_v2_report_restores_saved_narrative_and_charts() -> None:
    from app.services.report_agent import normalize_cached_report_row

    summary = {
        "report_narrative": {
            "headline": "历史标题",
            "executive_summary": "历史摘要",
            "section_insights": {
                "market_rhythm": "历史节奏判断",
                "market_topics": "历史话题判断",
                "market_platforms": "历史平台判断",
                "market_feedback": "历史反馈判断",
            },
            "data_notes": [],
        },
        "structured_report": {
            "charts": [
                {
                    "chart_id": "market-volume-trend",
                    "template_id": "F3",
                    "title": "传播规模与节奏",
                    "subtitle": "按日声量变化",
                    "insight": "历史节奏判断",
                    "source_label": "volume_trend",
                    "data": [{"date": "2026-05-17", "total_volume": 211}],
                    "meta": {},
                },
                {
                    "chart_id": "market-hot-topics",
                    "template_id": "F5",
                    "title": "热门话题结构",
                    "subtitle": "按讨论量展示",
                    "insight": "历史话题判断",
                    "source_label": "hot_topics.topics",
                    "data": [{"topic": "外观", "comment_count": 8}],
                    "meta": {},
                },
                {
                    "chart_id": "market-platform-efficiency",
                    "template_id": "F8",
                    "title": "平台传播效率",
                    "subtitle": "规模与反馈效率",
                    "insight": "历史平台判断",
                    "source_label": "platform.platform_efficiency",
                    "data": [
                        {
                            "platform": "抖音",
                            "total_volume": 20,
                            "engagement_per_content": 6,
                        }
                    ],
                    "meta": {},
                },
                {
                    "chart_id": "market-feedback-sentiment",
                    "template_id": "L14",
                    "title": "用户反馈构成",
                    "subtitle": "情感分布",
                    "insight": "历史反馈判断",
                    "source_label": "feedback_quality.sentiment_distribution",
                    "data": [
                        {"label": "正向", "rate": 70},
                        {"label": "负向", "rate": 30},
                    ],
                    "meta": {},
                },
            ]
        },
    }

    result = normalize_cached_report_row(
        {
            "event_id": "event_001",
            "prompt_version": "market_report_summary_v2",
            "generated_at": "2026-06-22T10:00:00",
            "summary_json": summary,
            "context_json": {},
            "rendered_prompt": "Cached prompt",
        }
    )

    assert result["summary"] == summary


def test_market_report_agent_api_runs_summary(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    captured = {}

    def fake_run(event_id, **kwargs):
        captured["event_id"] = event_id
        return {
            "event_id": event_id,
            "prompt_version": "market_report_summary_v2",
            "summary": {
                "report_narrative": {
                    "headline": "市场部测试报告",
                    "executive_summary": "测试摘要",
                    "section_insights": {"market_rhythm": "节奏判断"},
                    "data_notes": [],
                },
                "structured_report": {
                    "charts": [{"chart_id": "market-volume-trend", "template_id": "F3", "data": []}],
                },
            },
            "context": {"event_overview": {"event_name": "ID.AURA T6 launch"}},
            "rendered_prompt": "Market report",
        }

    monkeypatch.setattr("app.routers.tasks.run_market_report_agent", fake_run)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.post("/api/voc/events/event_001/market/report-agent/run")

    assert response.status_code == 200
    assert response.json()["summary"]["report_narrative"]["headline"] == "市场部测试报告"
    assert response.json()["summary"]["structured_report"]["charts"][0]["template_id"] == "F3"
    assert response.json()["rendered_prompt"] == "Market report"
    assert captured["event_id"] == "event_001"


def test_market_report_agent_api_returns_latest_cached_summary(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    captured = {}

    def fake_latest(event_id, **kwargs):
        captured["event_id"] = event_id
        return {
            "event_id": event_id,
            "prompt_version": "market_report_v1",
            "generated_at": "2026-06-22T10:00:00",
            "summary": {
                "report_markdown": "# Cached Market Report\n\nThis is cached.",
                "data_notes": [],
            },
            "context": {"event_overview": {"event_name": "ID.AURA T6 launch"}},
            "rendered_prompt": "Cached prompt",
        }

    monkeypatch.setattr("app.routers.tasks.get_latest_market_report_agent_result", fake_latest)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.get("/api/voc/events/event_001/market/report-agent/latest")

    assert response.status_code == 200
    assert response.json()["summary"]["report_markdown"].startswith("# Cached Market Report")
    assert response.json()["rendered_prompt"] == "Cached prompt"
    assert captured["event_id"] == "event_001"


def test_market_report_agent_api_returns_404_without_cached_summary(tmp_path, monkeypatch) -> None:
    from fastapi.testclient import TestClient

    from app.main import create_app

    monkeypatch.setattr("app.routers.tasks.get_latest_market_report_agent_result", lambda event_id, **kwargs: None)
    client = TestClient(create_app(tasks_dir=tmp_path / "tasks"))

    response = client.get("/api/voc/events/event_001/market/report-agent/latest")

    assert response.status_code == 404
