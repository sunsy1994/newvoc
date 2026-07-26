import pytest

from app.services.report_visuals import (
    build_event_report_charts,
    build_market_report_charts,
    build_product_report_charts,
    build_sales_report_charts,
    has_renderable_data,
    normalize_report_chart_meta,
    normalize_report_chart_data,
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
    from app.services.report_visuals import REPORT_TEMPLATE_IDS

    charts = build_product_report_charts(
        {
            "product_focus": {"aspects": []},
            "product_opportunity": {"surprise_points": [], "pain_points": [], "conversion_points": []},
            "pko": {"evidence_comments": [], "dimension_result_matrix": []},
        }
    )
    assert [(item["chart_id"], item["template_id"]) for item in charts] == [
        ("product-focus", "F5"),
        ("product-sentiment", "L15"),
        ("product-opportunity", "F5"),
        ("product-pko-evidence", "L6"),
        ("product-pko-matrix", "F7"),
    ]
    assert {"L6", "L15", "F6", "L12"} <= REPORT_TEMPLATE_IDS


def test_l6_keeps_only_real_dimension_target_evidence_rows():
    rows = [
        {
            "comment_id": "c1",
            "comment_text": "外观比竞品更协调",
            "dimension": "外观",
            "target": "竞品A",
            "result_bucket": "advantage",
        },
        {
            "comment_id": "c2",
            "comment_text": "空间对比",
            "dimension": "",
            "target": "竞品B",
            "result_bucket": "neutral",
        },
        {
            "comment_id": "c3",
            "comment_text": "缺少车系",
            "dimension": "空间",
            "target": None,
            "result_bucket": "neutral",
        },
    ]

    assert normalize_report_chart_data("L6", rows) == [rows[0]]


def test_l15_requires_named_aspect_and_two_finite_rates():
    rows = [
        {"aspect": "外观", "positive_rate": 70, "negative_rate": 20},
        {"aspect": "空间", "positive_rate": 55, "negative_rate": None},
        {"aspect": "", "positive_rate": 40, "negative_rate": 30},
        {"aspect": "价格", "positive_rate": float("inf"), "negative_rate": 30},
    ]

    assert normalize_report_chart_data("L15", rows) == [
        {
            "aspect": "外观",
            "positive_rate": 70.0,
            "neutral_rate": 10.0,
            "negative_rate": 20.0,
        }
    ]


def test_l15_normalizes_sentiment_rates_deterministically():
    from app.services import report_visuals

    assert report_visuals.normalize_sentiment_rates(70, 20) == {
        "positive_rate": 70.0,
        "neutral_rate": 10.0,
        "negative_rate": 20.0,
    }
    assert report_visuals.normalize_sentiment_rates(80, 40) == {
        "positive_rate": 66.67,
        "neutral_rate": 0.0,
        "negative_rate": 33.33,
    }
    assert report_visuals.normalize_sentiment_rates(150, 20) == {
        "positive_rate": 83.33,
        "neutral_rate": 0.0,
        "negative_rate": 16.67,
    }


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


def test_l6_keeps_real_records_and_caps_at_fifty():
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


def test_l6_uses_comment_id_as_stable_tie_breaker():
    rows = [
        {
            "comment_id": comment_id,
            "target": "竞品A",
            "dimension": "空间",
            "result": "优势",
            "comment_text": f"原声 {comment_id}",
            "interaction_cnt": 10,
            "published_at": "2026-07-24T10:00:00",
        }
        for comment_id in ["c-003", "c-001", "c-002"]
    ]

    chart = build_product_report_charts({"pko": {"evidence_comments": rows}})[3]

    assert [row["comment_id"] for row in chart["data"]] == [
        "c-001",
        "c-002",
        "c-003",
    ]


def test_missing_data_stays_empty():
    charts = build_market_report_charts({})
    assert all(chart["data"] == [] for chart in charts)
    assert all(chart["meta"]["empty_reason"] for chart in charts)


def test_l6_excludes_incomplete_evidence_from_data_and_counts():
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

    assert chart["data"] == []
    assert chart["meta"] == {
        "displayed_count": 0,
        "total_count": 0,
        "unit": "条对比评论",
        "empty_reason": "暂无可用数据",
    }


def test_l6_rejects_non_string_dimensions_and_targets():
    chart = build_product_report_charts(
        {
            "pko": {
                "evidence_comments": [
                    {
                        "comment_id": "one",
                        "comment_text": "first",
                        "target": {"bad": "value"},
                        "dimension": ["bad"],
                        "result": "优势",
                        "interaction_cnt": "bad",
                    }
                ]
            }
        }
    )[3]

    assert chart["data"] == []
    assert chart["meta"] == {
        "displayed_count": 0,
        "total_count": 0,
        "unit": "条对比评论",
        "empty_reason": "暂无可用数据",
    }


def test_event_report_uses_the_four_cross_department_charts_in_fixed_order():
    charts = build_event_report_charts(
        {"volume_trend": [{"date": "2026-07-01"}]},
        {"product_focus": {"aspects": [{"aspect": "外观"}]}},
        {"lead_quality": {"summary": {"labeled_comment_count": 1}}},
    )
    assert [item["template_id"] for item in charts] == ["F3", "L14", "F6", "L13"]


@pytest.mark.parametrize(
    ("template_id", "data"),
    [
        ("F3", []),
        ("F4", []),
        ("F5", [{"topic": "外观"}]),
        ("F6", [{"aspect": "外观", "positive_rate": 70}]),
        ("F7", [{"dimension": "空间", "total_count": 8}]),
        ("F8", [{"platform": "抖音", "total_volume": 20}]),
        (
            "L12",
            [
                {
                    "comment_id": "c-1",
                    "target": "竞品A",
                    "dimension": "空间",
                    "result": "advantage",
                }
            ],
        ),
        (
            "L6",
            [
                {
                    "comment_id": "c-1",
                    "target": "竞品A",
                    "dimension": "空间",
                    "result_bucket": "advantage",
                }
            ],
        ),
        (
            "L13",
            [
                {"stage": "已打标评论", "count": 100},
                {"stage": "车相关评论", "count": 80},
                {"stage": "销售相关意图", "count": 30},
            ],
        ),
        (
            "L13",
            [
                {"stage": "已打标评论", "count": 100},
                {"stage": "车相关评论", "count": 80},
                {"stage": "销售相关意图", "count": 90},
                {"stage": "中/强购买信号", "count": 20},
            ],
        ),
        ("L14", [{"label": "正向", "rate": 70}, {"label": "负向", "rate": 20}]),
    ],
)
def test_report_chart_renderability_matches_svg_input_contracts(template_id, data):
    assert normalize_report_chart_data(template_id, data) == []
    assert has_renderable_data({"template_id": template_id, "data": data}) is False


@pytest.mark.parametrize(
    ("template_id", "data"),
    [
        ("F3", [{"date": "2026-07-01", "total_volume": 12}]),
        ("F4", [{"label": "强信号", "count": 4}]),
        ("F5", [{"topic": "外观", "comment_count": 8}]),
        ("F6", [{"aspect": "外观", "positive_rate": 70, "negative_rate": 10}]),
        (
            "F7",
            [{"dimension": "空间", "advantage_count": 4, "disadvantage_count": 2}],
        ),
        (
            "F8",
            [{"platform": "抖音", "total_volume": 20, "engagement_per_content": 6}],
        ),
        (
            "L12",
            [
                {
                    "comment_id": "c-1",
                    "target": "竞品A",
                    "dimension": "空间",
                    "result": "advantage",
                    "comment_text": "空间更宽敞",
                }
            ],
        ),
        (
            "L6",
            [
                {
                    "comment_id": "c-1",
                    "target": "竞品A",
                    "dimension": "空间",
                    "result_bucket": "advantage",
                    "comment_text": "空间更宽敞",
                }
            ],
        ),
        (
            "L15",
            [
                {
                    "aspect": "外观",
                    "positive_rate": 70.0,
                    "neutral_rate": 10.0,
                    "negative_rate": 20.0,
                }
            ],
        ),
        (
            "L13",
            [
                {"stage": "已打标评论", "count": 100},
                {"stage": "车相关评论", "count": 80},
                {"stage": "销售相关意图", "count": 30},
                {"stage": "中/强购买信号", "count": 20},
            ],
        ),
        ("L14", [{"label": "正向", "rate": 70}, {"label": "负向", "rate": 30}]),
    ],
)
def test_report_chart_renderability_accepts_complete_svg_inputs(template_id, data):
    assert normalize_report_chart_data(template_id, data) == data
    assert has_renderable_data({"template_id": template_id, "data": data}) is True


def test_builders_drop_rows_that_cannot_render_and_expose_empty_reason():
    market = build_market_report_charts(
        {
            "platform": {
                "platform_efficiency": [
                    {"platform": "抖音", "total_volume": 20},
                ]
            },
            "feedback_quality": {
                "sentiment_distribution": [
                    {"label": "正向", "rate": 70},
                    {"label": "负向", "rate": 20},
                ]
            },
        }
    )
    sales = build_sales_report_charts(
        {
            "lead_quality": {
                "summary": {
                    "labeled_comment_count": 100,
                    "vehicle_related_count": 80,
                    "sales_intent_comment_count": 90,
                    "mid_high_purchase_signal_count": 20,
                }
            }
        }
    )

    for chart in (market[2], market[3], sales[0]):
        assert chart["data"] == []
        assert chart["meta"]["empty_reason"] == "暂无可用数据"


@pytest.mark.parametrize(
    "template_id",
    ["F3", "F4", "F5", "F6", "F7", "F8", "L13", "L14", "L15"],
)
def test_non_l12_cache_meta_allows_only_fixed_safe_shapes(template_id):
    assert normalize_report_chart_meta(template_id, [{}], {}) == {}
    assert normalize_report_chart_meta(
        template_id,
        [],
        {"empty_reason": "暂无可用数据"},
    ) == {"empty_reason": "暂无可用数据"}
    assert normalize_report_chart_meta(template_id, [{}], {"unexpected": []}) is None
    assert normalize_report_chart_meta(
        template_id,
        [],
        {"empty_reason": {"unsafe": True}},
    ) is None
    assert normalize_report_chart_meta(
        template_id,
        [],
        {"empty_reason": "其他空态"},
    ) is None


def test_cache_meta_rejects_unknown_template():
    assert normalize_report_chart_meta("UNKNOWN", [], {}) is None


@pytest.mark.parametrize("template_id", ["L6", "L12"])
def test_l6_and_l12_cache_meta_keep_real_total_larger_than_displayed_data(template_id):
    data = [
        {
            "comment_id": f"c-{index:03d}",
            "target": "竞品A",
            "dimension": "空间",
            "result_bucket": "advantage",
            "comment_text": f"原声 {index}",
        }
        for index in range(50)
    ]
    meta = {"displayed_count": 50, "total_count": 60, "unit": "条对比评论"}

    assert normalize_report_chart_meta(template_id, data, meta) == meta
    assert normalize_report_chart_meta(
        template_id,
        data,
        {"displayed_count": 50, "total_count": 49, "unit": "条对比评论"},
    ) is None
