from __future__ import annotations


def sample_market_context() -> dict:
    return {
        "event_overview": {
            "event_id": "event_001",
            "event_name": "IDT6上市",
            "brand_name": "一汽大众",
            "model_name": "ID.AURA T6",
            "start_time": "2026-05-14",
            "end_time": "2026-05-20",
        },
        "scale": {"total_volume": 261, "content_count": 25, "comment_count": 236, "total_engagement": 65692},
        "volume_trend": [
            {"date": "2026-05-14", "content_count": 3, "comment_count": 21, "total_volume": 24},
            {"date": "2026-05-15", "content_count": 8, "comment_count": 92, "total_volume": 100},
        ],
        "feedback_quality": {
            "summary": {"positive_rate": 34.5, "negative_rate": 31.5, "mid_high_purchase_signal_rate": 19.8, "top_aspect": "外观"}
        },
        "evidence": {"hot_posts": [{"title": "IDT6实拍体验", "total_engagement": 12000, "platform": "抖音"}]},
    }


def sample_product_context() -> dict:
    return {
        "product_focus": {
            "summary": {"top_aspect": "外观", "aspect_count": 11, "total_mentions": 194},
            "aspects": [
                {"aspect": "外观", "comment_count": 67, "positive_rate": 79.1, "negative_rate": 3.0},
                {"aspect": "价格", "comment_count": 14, "positive_rate": 7.2, "negative_rate": 42.9},
            ],
        },
        "product_opportunity": {
            "surprise_points": [{"aspect": "外观", "opportunity_score": 27.3, "reason": "造型正向反馈集中"}],
            "pain_points": [{"aspect": "价格", "opportunity_score": 3.1, "reason": "价格负向反馈集中"}],
            "conversion_points": [{"aspect": "智能", "opportunity_score": 10.3, "reason": "购买信号相对集中"}],
        },
        "pko": {
            "summary": {"pko_comment_count": 8, "top_target": "国产新能源"},
            "target_distribution": [{"label": "国产新能源", "count": 5, "rate": 62.5}],
            "evidence_comments": [{"comment_text": "这个设计确实更有高级感", "target": "国产新能源", "dimension": "外观", "result": "优势"}],
        },
        "evidence_comments": [{"aspect": "外观", "comment_text": "美，不止一种姿态"}],
    }


def sample_sales_context() -> dict:
    return {
        "lead_quality": {
            "summary": {"mid_high_purchase_signal_count": 31, "mid_high_purchase_signal_rate": 13.1, "top_intent": "询价"},
            "purchase_signal_distribution": [{"label": "强", "count": 18, "rate": 7.6}],
        },
        "lead_source": {
            "summary": {"top_platform": "抖音", "high_intent_comment_count": 31},
            "platform_efficiency": [{"platform": "抖音", "comment_count": 120, "high_intent_rate": 20.6}],
            "lead_comments": [{"comment_text": "大灯选型绝了，预售啥时候？", "purchase_signal": "强"}],
        },
        "recommended_follow_up_users": [{"nickname": "Aurora", "purchase_signal": "强", "representative_comment": "预售啥时候？"}],
    }


def test_event_report_builder_requires_charts_evidence_and_calculations() -> None:
    from app.agents.report import builder

    report = builder.build_event_report_payload(
        event_id="event_001",
        market_context=sample_market_context(),
        product_context=sample_product_context(),
        sales_context=sample_sales_context(),
        llm_summary={
            "executive_summary": ["外观是最明确的机会点。"],
            "recommendations": ["围绕外观高级感做内容复用。"],
        },
    )

    structured = report["summary"]["structured_report"]
    assert report["status"] == "generated"
    assert "已生成" in report["message"]
    assert report["suggested_questions"] == []
    assert structured["title"] == "IDT6上市事件综合报告"
    assert [section["code"] for section in structured["template_sections"]] == ["01", "02", "03", "04", "05"]
    assert [section["title"] for section in structured["template_sections"]] == ["事件总判断", "市场传播判断", "产品机会与风险", "销售转化判断", "证据与计算口径"]
    product_section = structured["template_sections"][2]
    assert [card["title"] for card in product_section["cards"]] == ["机会点", "风险点", "惊喜点", "判断口径"]
    assert "路径：" not in str(structured["template_sections"])
    assert "product.evidence_comments" not in str(structured["template_sections"])
    assert all(section["cards"] for section in structured["template_sections"])
    assert {chart["chart_type"] for chart in structured["charts"]} >= {"metric_cards", "bar", "trend", "table"}
    trend_chart = next(chart for chart in structured["charts"] if chart["chart_id"] == "event_rhythm_summary")
    assert trend_chart["data"][0] == {"date": "2026-05-14", "content_count": 3, "comment_count": 21, "total_volume": 24}
    assert trend_chart["x_field"] == "date"
    assert trend_chart["series"] == ["content_count", "comment_count"]
    assert structured["evidence_references"]
    assert structured["calculation_notes"]
    assert all(item["source_path"] for item in structured["evidence_references"])
    assert "report_markdown" in report["summary"]


def test_report_agent_dispatcher_runs_event_report(monkeypatch) -> None:
    from app.agents.core import dispatcher

    monkeypatch.setattr(
        dispatcher,
        "AGENT_RUNNERS",
        {
            **dispatcher.AGENT_RUNNERS,
            "report": lambda message, event_id=None, history=None: {
            "status": "generated",
            "message": "已生成《IDT6上市事件综合报告》。",
            "event_id": event_id or "event_001",
            "summary": {"report_markdown": "# IDT6上市事件综合报告", "structured_report": {"charts": [], "evidence_references": [], "calculation_notes": []}},
            },
        },
    )

    result = dispatcher.dispatch_agent("report", "生成一份IDT6上市事件综合报告", event_id="event_001", history=[])

    assert result["status"] == "generated"
    assert result["event_id"] == "event_001"
    assert "已生成" in result["message"]
