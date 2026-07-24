from app.services.report_visuals import (
    build_event_report_charts,
    build_market_report_charts,
    build_product_report_charts,
    build_sales_report_charts,
)


def test_market_report_chart_order_is_fixed():
    charts = build_market_report_charts(
        {
            "volume_trend": [{"date": "2026-07-01", "total_volume": 12, "content_count": 2, "comment_count": 10}],
            "hot_topics": {"topics": [{"topic": "外观", "comment_count": 8, "content_count": 2}]},
            "platform": {"platform_efficiency": []},
            "feedback_quality": {"sentiment_distribution": [{"label": "正向", "count": 7, "rate": 70}]},
        }
    )
    assert [item["template_id"] for item in charts] == ["F3", "F5", "F8", "L14"]


def test_product_report_chart_order_is_fixed():
    charts = build_product_report_charts(
        {
            "product_focus": {"aspects": []},
            "product_opportunity": {"surprise_points": [], "pain_points": [], "conversion_points": []},
            "pko": {"evidence_comments": [], "dimension_result_matrix": []},
        }
    )
    assert [item["template_id"] for item in charts] == ["F5", "F6", "F5", "L12", "F7"]


def test_sales_report_chart_order_is_fixed():
    charts = build_sales_report_charts(
        {
            "lead_quality": {"summary": {}, "purchase_signal_distribution": [], "intent_distribution": []},
            "lead_source": {"platform_efficiency": []},
        }
    )
    assert [item["template_id"] for item in charts] == ["L13", "F4", "F5", "F6"]


def test_sales_funnel_uses_the_real_mid_high_purchase_signal_field():
    chart = build_sales_report_charts(
        {
            "lead_quality": {
                "summary": {
                    "labeled_comment_count": 120,
                    "vehicle_related_count": 100,
                    "sales_intent_comment_count": 40,
                    "mid_high_purchase_signal_count": 12,
                }
            }
        }
    )[0]

    assert [row["count"] for row in chart["data"]] == [120, 100, 40, 12]


def test_l12_keeps_real_records_and_caps_at_fifty():
    rows = [
        {
            "comment_id": f"c-{index:03d}",
            "target": "竞品A",
            "dimension": "空间",
            "result": "优势",
            "comment_text": f"原声 {index}",
            "interaction_cnt": 100 - index,
            "published_at": f"2026-07-{(index % 28) + 1:02d}",
        }
        for index in range(60)
    ]
    chart = build_product_report_charts(
        {
            "product_focus": {"aspects": []},
            "product_opportunity": {"surprise_points": [], "pain_points": [], "conversion_points": []},
            "pko": {"evidence_comments": rows, "dimension_result_matrix": []},
        }
    )[3]
    assert len(chart["data"]) == 50
    assert chart["meta"] == {"displayed_count": 50, "total_count": 60, "unit": "条对比评论"}
    assert chart["data"][0]["comment_id"] == "c-000"


def test_missing_data_stays_empty():
    charts = build_market_report_charts({})
    assert all(chart["data"] == [] for chart in charts)
    assert all(chart["meta"]["empty_reason"] for chart in charts)


def test_l12_excludes_unrenderable_records_from_data_and_counts():
    chart = build_product_report_charts(
        {
            "pko": {
                "evidence_comments": [
                    {"comment_id": "one", "comment_text": "first"},
                    {"comment_id": "missing-copy"},
                    {"comment_id": "blank-copy", "comment_text": "  "},
                    {"comment_text": "missing id"},
                    {"comment_id": "two", "comment_text": "second"},
                ]
            }
        }
    )[3]

    assert [row["comment_id"] for row in chart["data"]] == ["one", "two"]
    assert chart["meta"]["displayed_count"] == 2
    assert chart["meta"]["total_count"] == 2


def test_event_report_uses_the_four_cross_department_charts_in_fixed_order():
    charts = build_event_report_charts(
        {"volume_trend": [{"date": "2026-07-01"}]},
        {"product_focus": {"aspects": [{"aspect": "外观"}]}},
        {"lead_quality": {"summary": {"labeled_comment_count": 1}}},
    )
    assert [item["template_id"] for item in charts] == ["F3", "L14", "F6", "L13"]
