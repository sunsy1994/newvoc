from __future__ import annotations


def resolve_product_report_prompt_for_test(monkeypatch):
    from app.services import report_agent

    monkeypatch.setattr(
        report_agent,
        "get_default_prompt_template",
        lambda scene, database_url=None: {
            "prompt_version": "custom_product_prompt",
            "prompt_content": "请在 headline、executive_summary 和 section_insights 中输出产品建议。",
        },
    )
    return report_agent.resolve_product_report_prompt("postgresql://unused")


def test_custom_product_prompt_appends_fixed_storyline_and_global_no_advice_rule(monkeypatch) -> None:
    from app.services import report_agent

    prompt, _ = resolve_product_report_prompt_for_test(monkeypatch)

    assert report_agent.DEFAULT_PRODUCT_REPORT_PROMPT_VERSION == "product_report_summary_v3"
    assert "storyline" in prompt
    assert '"chapter_id": "focus"' in prompt
    assert '"chapter_id": "attitude"' in prompt
    assert '"chapter_id": "comparison"' in prompt
    assert '"chapter_id": "evidence"' in prompt
    assert "不得复述 section_insights" in prompt
    assert "无论上述自定义要求如何，所有输出字段均不得包含产品建议" in prompt
    assert prompt.rfind("所有输出字段均不得包含产品建议") > prompt.find("输出产品建议")
    assert "metric_refs" in prompt and "comment_id" in prompt


def test_default_product_prompt_allows_real_comment_ids_for_evidence_refs() -> None:
    from app.services import report_agent

    assert "所有输出字段均不得包含产品建议" in report_agent.DEFAULT_PRODUCT_REPORT_PROMPT
    assert "target、dimension、result、reason、comment_text 和 comment_id" in (
        report_agent.DEFAULT_PRODUCT_REPORT_PROMPT
    )


def test_market_prompt_requires_storyline_and_sales_does_not(monkeypatch) -> None:
    from app.services import report_agent

    monkeypatch.setattr(
        report_agent,
        "get_default_prompt_template",
        lambda scene, database_url=None: {
            "prompt_version": f"custom_{scene}",
            "prompt_content": f"保留这段 {scene} 分析要求。",
        },
    )

    market_prompt, _ = report_agent.resolve_market_report_prompt("postgresql://unused")
    sales_prompt, _ = report_agent.resolve_sales_report_prompt("postgresql://unused")

    assert "storyline" in market_prompt
    assert "storyline" not in sales_prompt
