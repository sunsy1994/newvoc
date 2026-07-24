from app.services.system_settings import mask_api_key


def test_mask_api_key_hides_sensitive_middle() -> None:
    assert mask_api_key("sk-1234567890abcdef") == "sk-****cdef"
    assert mask_api_key("short") == "****"
    assert mask_api_key("") == ""


def test_department_default_prompts_use_v2_fixed_narrative_contracts() -> None:
    from app.services import system_settings

    cases = (
        (
            system_settings.MARKET_REPORT_PROMPT_SCENE,
            "market_report_summary_v2",
            ("market_rhythm", "market_topics", "market_platforms", "market_feedback"),
        ),
        (
            system_settings.PRODUCT_REPORT_PROMPT_SCENE,
            "product_report_summary_v2",
            ("product_focus", "product_sentiment", "product_opportunity", "product_pko_relationships", "product_pko_results"),
        ),
        (
            system_settings.SALES_REPORT_PROMPT_SCENE,
            "sales_report_summary_v2",
            ("sales_funnel", "sales_signals", "sales_intents", "sales_sources"),
        ),
    )

    for scene, expected_version, section_codes in cases:
        _, version, prompt = system_settings._default_prompt_payload(scene)
        assert version == expected_version
        assert '"headline"' in prompt
        assert '"executive_summary"' in prompt
        assert '"section_insights"' in prompt
        assert '"data_notes"' in prompt
        assert "report_markdown" not in prompt
        assert "图表类型和数值由系统固定" in prompt
        assert "输入缺失时不得推断" in prompt
        for code in section_codes:
            assert f'"{code}"' in prompt
