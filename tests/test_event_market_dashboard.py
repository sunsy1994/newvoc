from app.services import event_voc_insights


def test_build_volume_rhythm_story_identifies_peak_and_pattern() -> None:
    trend = [
        {"date": "2026-05-14", "content_count": 4, "comment_count": 8, "total_volume": 12},
        {"date": "2026-05-15", "content_count": 12, "comment_count": 88, "total_volume": 100},
        {"date": "2026-05-16", "content_count": 5, "comment_count": 13, "total_volume": 18},
    ]

    rhythm = event_voc_insights.build_volume_rhythm_story(trend)

    assert rhythm["summary"]["total_volume"] == 130
    assert rhythm["summary"]["rhythm_type"] == "集中爆发"
    assert rhythm["summary"]["peak_date"] == "2026-05-15"
    assert rhythm["summary"]["peak_volume"] == 100
    assert rhythm["summary"]["peak_volume_rate"] == 76.9
    assert "集中爆发" in rhythm["summary"]["rule_based_conclusion"]


def test_build_subject_story_identifies_kol_driven_pattern() -> None:
    subject_rows = [
        {"subject_type": "KOL", "content_count": 6, "comment_count": 90, "total_engagement": 900},
        {"subject_type": "普通用户", "content_count": 4, "comment_count": 20, "total_engagement": 100},
    ]
    kol_type_rows = [
        {"kol_main_type": "车型实测测评KOL", "kol_count": 2, "content_count": 4, "total_engagement": 700},
        {"kol_main_type": "新车资讯爆料KOL", "kol_count": 1, "content_count": 2, "total_engagement": 200},
    ]
    top_authors = [
        {"author_name": "车圈老张", "subject_type": "KOL", "content_count": 3, "comment_count": 60, "total_engagement": 600}
    ]

    story = event_voc_insights.build_subject_story(subject_rows, kol_type_rows, top_authors)

    assert story["summary"]["dominant_subject_type"] == "KOL"
    assert story["summary"]["dominant_subject_engagement_rate"] == 90.0
    assert story["summary"]["top_kol_type"] == "车型实测测评KOL"
    assert "KOL带动" in story["summary"]["rule_based_conclusion"]
    assert story["subject_distribution"][0]["rate"] == 90.0


def test_build_platform_story_identifies_core_platform_and_quality() -> None:
    platform_rows = [
        {
            "platform": "抖音",
            "content_count": 10,
            "comment_count": 90,
            "total_volume": 100,
            "total_engagement": 1000,
            "labeled_comment_count": 80,
            "vehicle_related_count": 64,
            "mid_high_purchase_signal_count": 20,
        },
        {
            "platform": "小红书",
            "content_count": 5,
            "comment_count": 10,
            "total_volume": 15,
            "total_engagement": 250,
            "labeled_comment_count": 10,
            "vehicle_related_count": 9,
            "mid_high_purchase_signal_count": 1,
        },
    ]

    story = event_voc_insights.build_platform_story(platform_rows)

    assert story["summary"]["core_platform"] == "抖音"
    assert story["summary"]["core_platform_volume_rate"] == 87.0
    assert story["summary"]["core_platform_effective_comment_rate"] == 80.0
    assert story["summary"]["core_platform_purchase_signal_rate"] == 25.0
    assert "抖音" in story["summary"]["rule_based_conclusion"]
    assert story["platform_efficiency"][0]["engagement_per_content"] == 100.0


def test_build_regional_response_story_uses_comment_location_only() -> None:
    rows = [
        {
            "location": "Shanghai",
            "comment_count": 12,
            "labeled_comment_count": 10,
            "vehicle_related_count": 8,
            "positive_count": 5,
            "negative_count": 1,
            "mid_high_purchase_signal_count": 3,
        },
        {
            "location": "Beijing",
            "comment_count": 8,
            "labeled_comment_count": 8,
            "vehicle_related_count": 4,
            "positive_count": 2,
            "negative_count": 2,
            "mid_high_purchase_signal_count": 1,
        },
    ]
    top_contents = [
        {
            "location": "Shanghai",
            "content_id": "c1",
            "title": "Launch video",
            "platform": "Douyin",
            "comment_count": 7,
            "vehicle_related_count": 5,
        }
    ]

    story = event_voc_insights.build_regional_response_story(rows, top_contents)

    assert story["summary"]["top_location"] == "Shanghai"
    assert story["summary"]["top_location_comment_rate"] == 60.0
    assert story["summary"]["top_location_effective_comment_rate"] == 80.0
    assert story["summary"]["top_location_purchase_signal_rate"] == 30.0
    assert story["locations"][0]["positive_rate"] == 50.0
    assert story["top_contents"][0]["title"] == "Launch video"
    assert story["summary"]["data_scope"] == "comment_location_only"


def test_build_topic_spread_story_parses_hash_topics_from_content_text() -> None:
    content_rows = [
        {
            "content_id": "c1",
            "title": "#SmartCabin launch",
            "content_text": "This week #SmartCabin #FamilyTrip",
            "platform": "Douyin",
            "total_engagement": 100,
            "comment_count": 10,
            "labeled_comment_count": 8,
            "vehicle_related_count": 6,
            "positive_count": 4,
            "mid_high_purchase_signal_count": 2,
        },
        {
            "content_id": "c2",
            "title": "Test drive #SmartCabin",
            "content_text": "",
            "platform": "XHS",
            "total_engagement": 50,
            "comment_count": 5,
            "labeled_comment_count": 5,
            "vehicle_related_count": 3,
            "positive_count": 1,
            "mid_high_purchase_signal_count": 1,
        },
        {
            "content_id": "c3",
            "title": "Owner story #SmartCabin",
            "content_text": "",
            "platform": "Douyin",
            "total_engagement": 40,
            "comment_count": 4,
            "labeled_comment_count": 4,
            "vehicle_related_count": 3,
            "positive_count": 2,
            "mid_high_purchase_signal_count": 0,
        },
        {
            "content_id": "c4",
            "title": "Dealer live #SmartCabin",
            "content_text": "",
            "platform": "Kuaishou",
            "total_engagement": 30,
            "comment_count": 3,
            "labeled_comment_count": 3,
            "vehicle_related_count": 2,
            "positive_count": 1,
            "mid_high_purchase_signal_count": 0,
        },
    ]

    story = event_voc_insights.build_topic_spread_story(content_rows)

    assert story["summary"]["top_topic"] == "SmartCabin"
    assert story["summary"]["topic_count"] == 2
    assert story["summary"]["top_topic_content_count"] == 4
    assert story["summary"]["top_topic_comment_count"] == 22
    assert story["topics"][0]["topic"] == "SmartCabin"
    assert story["topics"][0]["effective_comment_rate"] == 70.0
    assert len(story["topics"][0]["top_contents"]) == 4
    assert story["topics"][0]["top_contents"][0]["content_id"] == "c1"


def test_build_content_comment_timeline_groups_comments_by_publish_lifecycle() -> None:
    published_at = "2026-05-18T10:00:00"
    rows = [
        {"published_at": "2026-05-18T10:05:00", "interaction_cnt": 3},
        {"published_at": "2026-05-18T12:45:00", "interaction_cnt": 5},
        {"published_at": "2026-05-18T13:20:00", "interaction_cnt": 2},
        {"published_at": "2026-05-20T12:10:00", "interaction_cnt": 9},
    ]

    timeline = event_voc_insights.build_content_comment_timeline(rows, published_at)

    assert [point["relative_bucket"] for point in timeline] == ["0-3h", "3-6h", "6-9h", "9-12h", "12-24h", "24-48h", "48h+"]
    assert timeline[0] == {"time_bucket": "0-3h", "relative_bucket": "0-3h", "comment_count": 2, "interaction_count": 8}
    assert timeline[1] == {"time_bucket": "3-6h", "relative_bucket": "3-6h", "comment_count": 1, "interaction_count": 2}
    assert timeline[2] == {"time_bucket": "6-9h", "relative_bucket": "6-9h", "comment_count": 0, "interaction_count": 0}
    assert timeline[-1] == {"time_bucket": "48h+", "relative_bucket": "48h+", "comment_count": 1, "interaction_count": 9}


def test_describe_comment_peak_bucket_prefers_highest_comment_bucket() -> None:
    timeline = [
        {"relative_bucket": "0-3h", "comment_count": 2, "interaction_count": 8},
        {"relative_bucket": "3-6h", "comment_count": 5, "interaction_count": 4},
        {"relative_bucket": "6-9h", "comment_count": 0, "interaction_count": 0},
    ]

    assert event_voc_insights.describe_comment_peak_bucket(timeline) == "3-6h"


def test_build_author_profile_sankey_groups_event_to_user_profile() -> None:
    rows = [
        {"event_id": "event_1", "event_name": "上市发布", "comment_user_id": "user_1", "comment_count": 3},
        {"event_id": "event_1", "event_name": "上市发布", "comment_user_id": "user_2", "comment_count": 2},
        {"event_id": "event_2", "event_name": "试驾传播", "comment_user_id": "user_1", "comment_count": 1},
    ]
    profile_map = {"user_1": "价格敏感", "user_2": "外观关注"}

    sankey = event_voc_insights.build_author_profile_sankey("author_1", "车圈老张", rows, profile_map)

    assert {"id": "author:author_1", "label": "车圈老张", "layer": 0} in sankey["nodes"]
    assert {"id": "event:event_1", "label": "上市发布", "layer": 1} in sankey["nodes"]
    assert {"id": "profile:价格敏感", "label": "价格敏感", "layer": 2} in sankey["nodes"]
    assert {"source": "author:author_1", "target": "event:event_1", "value": 5} in sankey["links"]
    assert {"source": "event:event_1", "target": "profile:价格敏感", "value": 3} in sankey["links"]
    assert {"source": "event:event_1", "target": "profile:外观关注", "value": 2} in sankey["links"]


def test_build_product_focus_story_identifies_top_aspect_and_sentiment() -> None:
    rows = [
        {"aspect": "空间", "comment_count": 12, "positive_count": 8, "negative_count": 1, "purchase_signal_count": 3},
        {"aspect": "价格", "comment_count": 10, "positive_count": 2, "negative_count": 6, "purchase_signal_count": 1},
        {"aspect": "智能化", "comment_count": 5, "positive_count": 3, "negative_count": 1, "purchase_signal_count": 2},
    ]

    story = event_voc_insights.build_product_focus_story(rows)

    assert story["summary"]["top_aspect"] == "空间"
    assert story["summary"]["aspect_count"] == 3
    assert story["summary"]["total_mentions"] == 27
    assert story["aspects"][0]["positive_rate"] == 66.7
    assert story["aspects"][1]["negative_rate"] == 60.0
    assert "空间" in story["summary"]["rule_based_conclusion"]


def test_build_product_opportunity_story_ranks_surprise_pain_and_conversion_points() -> None:
    aspects = [
        {
            "aspect": "space",
            "comment_count": 20,
            "mention_rate": 50.0,
            "positive_count": 16,
            "positive_rate": 80.0,
            "negative_count": 2,
            "negative_rate": 10.0,
            "purchase_signal_count": 4,
            "purchase_signal_rate": 20.0,
            "evidence_comments": [{"comment_text": "space is excellent", "interaction_cnt": 9}],
        },
        {
            "aspect": "price",
            "comment_count": 12,
            "mention_rate": 30.0,
            "positive_count": 1,
            "positive_rate": 8.3,
            "negative_count": 8,
            "negative_rate": 66.7,
            "purchase_signal_count": 1,
            "purchase_signal_rate": 8.3,
        },
        {
            "aspect": "smart cockpit",
            "comment_count": 8,
            "mention_rate": 20.0,
            "positive_count": 4,
            "positive_rate": 50.0,
            "negative_count": 1,
            "negative_rate": 12.5,
            "purchase_signal_count": 5,
            "purchase_signal_rate": 62.5,
        },
    ]

    story = event_voc_insights.build_product_opportunity_story(aspects)

    assert story["summary"]["surprise_point"] == "space"
    assert story["summary"]["pain_point"] == "price"
    assert story["summary"]["conversion_point"] == "smart cockpit"
    assert story["surprise_points"][0]["opportunity_score"] == 40.0
    assert story["surprise_points"][0]["reason"] == "提及率 50.0% × 惊喜率 80.0%"
    assert story["surprise_points"][0]["evidence_comments"][0]["comment_text"] == "space is excellent"
    assert story["pain_points"][0]["opportunity_score"] == 20.0
    assert story["pain_points"][0]["reason"] == "提及率 30.0% × 风险率 66.7%"
    assert story["conversion_points"][0]["opportunity_score"] == 12.5
    assert story["conversion_points"][0]["reason"] == "提及率 20.0% × 转化率 62.5%"
    assert story["summary"]["rule_based_conclusion"]


def test_build_product_pko_story_summarizes_target_dimension_and_result() -> None:
    rows = [
        {
            "target": "BYD Qin L",
            "dimension": "price",
            "result": "本车劣势",
            "reason": "same price has more configuration",
            "comment_text": "BYD Qin L is cheaper with more options",
            "interaction_cnt": 9,
        },
        {
            "target": "BYD Qin L",
            "dimension": "appearance",
            "result": "本车优势",
            "reason": "design looks better",
            "comment_text": "this design looks better than Qin L",
            "interaction_cnt": 5,
        },
        {
            "target": "Tesla Model 3",
            "dimension": "brand",
            "result": "中性对比",
            "reason": "brand discussion",
            "comment_text": "brand is a different choice",
            "interaction_cnt": 2,
        },
    ]

    story = event_voc_insights.build_product_pko_story(rows)

    assert story["summary"]["pko_comment_count"] == 3
    assert story["summary"]["top_target"] == "BYD Qin L"
    assert story["summary"]["top_dimension"] == "price"
    assert story["summary"]["advantage_dimension"] == "appearance"
    assert story["summary"]["disadvantage_dimension"] == "price"
    assert story["target_distribution"][0] == {"label": "BYD Qin L", "count": 2, "rate": 66.7}
    assert story["result_distribution"][0]["label"] == "本车劣势"
    assert story["evidence_comments"][0]["comment_text"] == "BYD Qin L is cheaper with more options"


def test_build_product_pko_story_separates_generic_other_from_explicit_targets() -> None:
    rows = [
        {
            "target": "其他",
            "dimension": "品牌",
            "result": "中性对比",
            "comment_text": "和其他国产新能源都差不多",
            "interaction_cnt": 12,
        },
        {
            "target": "其他",
            "dimension": "价格",
            "result": "本车劣势",
            "comment_text": "其他车价格更有优势",
            "interaction_cnt": 6,
        },
        {
            "target": "比亚迪",
            "dimension": "价格",
            "result": "本车劣势",
            "comment_text": "比亚迪价格更低",
            "interaction_cnt": 9,
        },
        {
            "target": "比亚迪",
            "dimension": "品牌",
            "result": "中性对比",
            "comment_text": "品牌各有优势",
            "interaction_cnt": 3,
        },
        {
            "target": "理想",
            "dimension": "空间",
            "result": "本车优势",
            "comment_text": "比理想更灵活",
            "interaction_cnt": 4,
        },
    ]

    story = event_voc_insights.build_product_pko_story(rows)

    assert story["summary"]["pko_comment_count"] == 5
    assert story["summary"]["generic_target_count"] == 2
    assert story["summary"]["explicit_target_count"] == 3
    assert story["summary"]["explicit_target_rate"] == 60.0
    assert story["summary"]["top_explicit_target"] == "比亚迪"
    assert story["explicit_target_distribution"][0] == {"label": "比亚迪", "count": 2, "rate": 40.0}
    assert all(item["label"] != "其他" for item in story["explicit_target_distribution"])
    assert story["generic_target_summary"] == {"label": "其他对象", "count": 2, "rate": 40.0}
    price_row = next(row for row in story["dimension_result_matrix"] if row["dimension"] == "价格")
    assert price_row["disadvantage_count"] == 2
    assert price_row["top_target"] == "比亚迪"


def test_build_product_pko_story_keeps_evidence_for_each_explicit_target() -> None:
    rows = [
        {"target": "国产新能源", "dimension": "品牌", "result": "中性对比", "comment_text": "国产新能源 comment", "interaction_cnt": 10},
        {"target": "BYD", "dimension": "价格", "result": "中性对比", "comment_text": "BYD comment", "interaction_cnt": 9},
        {"target": "油车", "dimension": "其他", "result": "中性对比", "comment_text": "oil car comment", "interaction_cnt": 8},
        {"target": "其他", "dimension": "其他", "result": "中性对比", "comment_text": "other 1", "interaction_cnt": 7},
        {"target": "其他", "dimension": "其他", "result": "中性对比", "comment_text": "other 2", "interaction_cnt": 6},
        {"target": "其他", "dimension": "其他", "result": "中性对比", "comment_text": "other 3", "interaction_cnt": 5},
        {"target": "上汽大众", "dimension": "品牌", "result": "中性对比", "comment_text": "saic vw comment", "interaction_cnt": 4},
        {"target": "ID.4", "dimension": "智能化", "result": "本车劣势", "comment_text": "id4 evidence comment", "interaction_cnt": 0},
    ]

    story = event_voc_insights.build_product_pko_story(rows)

    evidence_targets = {item["target"] for item in story["evidence_comments"]}
    assert {item["label"] for item in story["explicit_target_distribution"]}.issubset(evidence_targets)
    assert any(item["target"] == "ID.4" and item["comment_text"] == "id4 evidence comment" for item in story["evidence_comments"])


def test_build_sales_lead_quality_story_summarizes_purchase_intent() -> None:
    rows = [
        {
            "is_vehicle_related": "是",
            "comment_intent": "询价",
            "purchase_signal": "强",
            "comment_user_id": "u1",
            "main_label": "价格敏感",
            "content_id": "c1",
            "comment_text": "How much is the top trim?",
            "interaction_cnt": 10,
        },
        {
            "is_vehicle_related": "是",
            "comment_intent": "对比",
            "purchase_signal": "中",
            "comment_user_id": "u2",
            "main_label": "竞品对比",
            "content_id": "c2",
            "comment_text": "Compare with Qin L before buying",
            "interaction_cnt": 6,
        },
        {
            "is_vehicle_related": "否",
            "comment_intent": "闲聊",
            "purchase_signal": "无",
            "comment_user_id": "u3",
            "main_label": "未画像用户",
            "content_id": "c2",
            "comment_text": "just passing by",
            "interaction_cnt": 1,
        },
    ]

    story = event_voc_insights.build_sales_lead_quality_story(rows)

    assert story["summary"]["labeled_comment_count"] == 3
    assert story["summary"]["vehicle_related_rate"] == 66.7
    assert story["summary"]["mid_high_purchase_signal_count"] == 2
    assert story["summary"]["mid_high_purchase_signal_rate"] == 66.7
    assert story["summary"]["strong_purchase_signal_count"] == 1
    assert story["intent_distribution"][0] == {"label": "询价", "count": 1, "rate": 33.3}
    assert story["purchase_signal_distribution"][0]["label"] == "强"
    assert story["evidence_comments"][0]["comment_text"] == "How much is the top trim?"
    assert story["summary"]["sales_intent_comment_count"] == 2
    assert story["summary"]["sales_intent_rate"] == 66.7
    assert story["sankey"]["nodes"][0] == {"id": "all", "label": "全部已打标评论", "layer": 0}
    assert {"source": "all", "target": "vehicle_related", "value": 2} in story["sankey"]["links"]
    assert {"source": "vehicle_related", "target": "sales_intent", "value": 2} in story["sankey"]["links"]
    assert {"source": "sales_intent", "target": "signal_strong", "value": 1} in story["sankey"]["links"]
    all_segment = next(item for item in story["profile_segments"] if item["segment_id"] == "all")
    strong_segment = next(item for item in story["profile_segments"] if item["segment_id"] == "signal_strong")
    assert all_segment["summary"]["user_count"] == 3
    assert all_segment["profile_distribution"][0] == {"main_label": "价格敏感", "user_count": 1, "rate": 33.3}
    assert strong_segment["summary"]["user_count"] == 1
    assert strong_segment["users"][0]["comment_user_id"] == "u1"
    assert strong_segment["users"][0]["purchase_signal"] == "强"
    assert strong_segment["users"][0]["representative_comment"] == "How much is the top trim?"
    mid_segment = next(item for item in story["profile_segments"] if item["segment_id"] == "signal_mid")
    assert mid_segment["summary"]["user_count"] == 1
    assert mid_segment["users"][0]["comment_user_id"] == "u2"
    assert mid_segment["users"][0]["purchase_signal"] == "中"


def test_build_comment_user_insight_profile_uses_label_scores_as_radar_and_evidence() -> None:
    profile = {
        "comment_user_id": "douyin:tester:shanghai",
        "comment_author_name": "tester",
        "platform": "douyin",
        "location": "shanghai",
        "main_label": "price sensitive",
        "main_dimension": "decision style",
        "main_score": 82.0,
        "total_comments": 3,
        "valid_comments": 2,
        "profile_batch": "v1",
    }
    label_scores = [
        {
            "dimension": "decision style",
            "label": "price sensitive",
            "final_score": 82.0,
            "support_count": 2,
            "evidence_examples_json": [
                {"comment_id": "cm1", "evidence_text": "asks for discount", "comment_text": "any discount?"}
            ],
            "evidence_details_json": [
                {"comment_id": "cm1", "evidence_text": "asks for discount", "reason": "explicit price question"}
            ],
        },
        {
            "dimension": "core concern",
            "label": "configuration",
            "final_score": 61.0,
            "support_count": 1,
            "evidence_examples_json": [],
            "evidence_details_json": [],
        },
    ]
    comments = [
        {
            "comment_id": "cm1",
            "comment_text": "any discount?",
            "published_at": "2026-05-18T10:00:00",
            "platform": "douyin",
            "comment_intent": "inquiry",
            "purchase_signal": "strong",
        },
        {
            "comment_id": "cm2",
            "comment_text": "configuration looks good",
            "published_at": "2026-05-19T10:00:00",
            "platform": "douyin",
            "comment_intent": "comparison",
            "purchase_signal": "mid",
        },
    ]

    payload = event_voc_insights.build_comment_user_insight_profile(profile, label_scores, comments)

    assert payload["user"]["comment_user_id"] == "douyin:tester:shanghai"
    assert payload["profile_summary"]["main_label"] == "price sensitive"
    assert payload["profile_summary"]["main_score"] == 82.0
    assert payload["radar_labels"][0] == {
        "dimension": "decision style",
        "label": "price sensitive",
        "score": 82.0,
        "support_count": 2,
    }
    assert payload["key_evidence"][0]["evidence_text"] == "asks for discount"
    assert payload["key_evidence"][0]["reason"] == "explicit price question"
    assert payload["comments"][0]["comment_text"] == "configuration looks good"
    assert payload["comments"][0]["purchase_signal"] == "mid"
    assert payload["comments"][1]["comment_text"] == "any discount?"


def test_build_sales_lead_source_efficiency_groups_platform_content_and_comments() -> None:
    rows = [
        {
            "platform": "抖音",
            "content_id": "c1",
            "title": "上市试驾",
            "source_url": "https://example.com/c1",
            "author_name": "车评A",
            "comment_intent": "询价",
            "purchase_signal": "强",
            "comment_text": "落地多少钱",
            "interaction_cnt": 8,
        },
        {
            "platform": "抖音",
            "content_id": "c1",
            "title": "上市试驾",
            "source_url": "https://example.com/c1",
            "author_name": "车评A",
            "comment_intent": "购买意向",
            "purchase_signal": "中",
            "comment_text": "这个价位可以考虑",
            "interaction_cnt": 4,
        },
        {
            "platform": "小红书",
            "content_id": "c2",
            "title": "静态体验",
            "source_url": "https://example.com/c2",
            "author_name": "车评B",
            "comment_intent": "闲聊",
            "purchase_signal": "无",
            "comment_text": "路过看看",
            "interaction_cnt": 1,
        },
        {
            "platform": "小红书",
            "content_id": "c2",
            "title": "静态体验",
            "source_url": "https://example.com/c2",
            "author_name": "车评B",
            "comment_intent": "购买意向",
            "purchase_signal": "弱",
            "comment_text": "再看看价格",
            "interaction_cnt": 2,
        },
    ]

    story = event_voc_insights.build_sales_lead_source_efficiency(rows)

    assert story["summary"]["high_intent_comment_count"] == 2
    assert story["summary"]["strong_signal_comment_count"] == 1
    assert story["summary"]["inquiry_comment_count"] == 1
    assert story["summary"]["source_platform_count"] == 1
    assert story["platform_efficiency"][0]["platform"] == "抖音"
    assert story["platform_efficiency"][0]["high_intent_rate"] == 100.0
    assert story["platform_efficiency"][0]["mid_signal_comment_count"] == 1
    assert story["platform_efficiency"][0]["low_signal_comment_count"] == 0
    assert story["platform_efficiency"][1]["platform"] == "小红书"
    assert story["platform_efficiency"][1]["low_signal_comment_count"] == 1
    assert story["content_leads"][0]["content_id"] == "c1"
    assert story["content_leads"][0]["high_intent_comment_count"] == 2
    assert story["content_leads"][0]["dominant_intent"] == "询价"
    assert story["lead_comments"][0]["comment_text"] == "落地多少钱"


def test_market_dashboard_payload_uses_real_sections(monkeypatch) -> None:
    def fake_overview(conn, event_id):
        return {
            "event_id": event_id,
            "event_name": "IDT6上市",
            "brand_name": "一汽大众",
            "model_name": "ID.AURA T6",
            "event_type": "新品上市",
            "event_status": "进行中",
            "start_time": "2026-05-14T00:00:00",
            "end_time": "2026-05-20T00:00:00",
            "content_cnt": 25,
            "comment_cnt": 19,
            "kol_content_cnt": 6,
            "total_engagement": 65692,
        }

    monkeypatch.setattr(event_voc_insights, "fetch_event_overview", fake_overview)
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_volume_trend",
        lambda conn, event_id: [{"date": "2026-05-14", "content_count": 2, "comment_count": 3, "total_volume": 5}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_channel_distribution",
        lambda conn, event_id: [{"channel": "抖音", "content_count": 10, "comment_count": 8, "total_volume": 18}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_kol_type_distribution",
        lambda conn, event_id: [{"kol_main_type": "车型实测测评KOL", "kol_count": 2, "content_count": 4, "total_engagement": 1200}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_hot_posts",
        lambda conn, event_id: [{"content_id": "c1", "title": "试驾体验", "total_engagement": 999}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_latest_comment_user_profiles",
        lambda conn, event_id: [{"main_label": "价格敏感"}, {"main_label": "价格敏感"}, {"main_label": "空间关注"}],
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_comment_quality",
        lambda conn, event_id: {"summary": {"labeled_comment_count": 19}},
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_subject_story",
        lambda conn, event_id, kol_type_distribution: {"summary": {"dominant_subject_type": "KOL"}},
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_platform_story",
        lambda conn, event_id: {"summary": {"core_platform": "抖音"}},
    )

    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_regional_response_story",
        lambda conn, event_id: {"summary": {"top_location": "Shanghai", "data_scope": "comment_location_only"}},
    )
    monkeypatch.setattr(
        event_voc_insights,
        "fetch_event_topic_spread_story",
        lambda conn, event_id: {"summary": {"top_topic": "SmartCabin"}},
    )

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(event_voc_insights.psycopg, "connect", lambda *args, **kwargs: FakeConnection())

    payload = event_voc_insights.get_voc_event_market_dashboard("event_001")

    assert payload["event"]["event_id"] == "event_001"
    assert payload["overview_metrics"] == {
        "total_volume": 44,
        "content_count": 25,
        "comment_count": 19,
        "kol_count": 2,
        "kol_content_count": 6,
        "total_engagement": 65692,
    }
    assert payload["volume_trend"][0]["total_volume"] == 5
    assert payload["volume_rhythm"]["summary"]["peak_volume"] == 5
    assert payload["channel_distribution"][0]["channel"] == "抖音"
    assert payload["kol_type_distribution"][0]["kol_main_type"] == "车型实测测评KOL"
    assert payload["user_profile_distribution"][0] == {"main_label": "价格敏感", "user_cnt": 2}
    assert payload["comment_quality"]["summary"]["labeled_comment_count"] == 19
    assert payload["subject_story"]["summary"]["dominant_subject_type"] == "KOL"
    assert payload["platform_story"]["summary"]["core_platform"] == "抖音"
    assert payload["hot_posts"][0]["title"] == "试驾体验"
