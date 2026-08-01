from app.services.system_settings import mask_api_key


HISTORICAL_PRODUCT_V2_PROMPT = """你是汽车行业 VOC 产品分析助手。请只基于给定的产品看板结构化数据生成固定字段的叙事文案。

约束：
1. 所有判断必须来自 product_context_json；输入缺失时不得推断、补齐竞品事实或编造外部信息。
2. 图表类型和数值由系统固定。不要生成图表、图型、排序、数据点或 structured_report，也不要修改输入数值。
3. PKO 只使用 pko 中已有的 target、dimension、result、reason 和 comment_text。
4. 只总结机会、风险、转化信号与 PKO 事实，不生成产品建议。
5. data_notes 只放真正影响判断的数据说明。
6. 输出必须是 JSON 对象，字段和 section_insights 的键不可增减，不要输出 Markdown。

严格输出：
{
  "headline": "",
  "executive_summary": "",
  "section_insights": {
    "product_focus": "",
    "product_sentiment": "",
    "product_opportunity": "",
    "product_pko_relationships": "",
    "product_pko_results": ""
  },
  "data_notes": []
}

产品看板结构化数据：
{{product_context_json}}
"""


def test_mask_api_key_hides_sensitive_middle() -> None:
    assert mask_api_key("sk-1234567890abcdef") == "sk-****cdef"
    assert mask_api_key("short") == "****"
    assert mask_api_key("") == ""


def test_department_default_prompts_use_fixed_narrative_contracts() -> None:
    from app.services import system_settings

    cases = (
        (
            system_settings.MARKET_REPORT_PROMPT_SCENE,
            "market_report_summary_v2",
            ("market_rhythm", "market_topics", "market_platforms", "market_feedback"),
        ),
        (
            system_settings.PRODUCT_REPORT_PROMPT_SCENE,
            "product_report_summary_v3",
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


def test_builtin_product_v2_prompt_is_upgraded_to_v3() -> None:
    from app.services import system_settings

    assert (
        system_settings._prompt_seed_action(
            {
                "prompt_scene": system_settings.PRODUCT_REPORT_PROMPT_SCENE,
                "prompt_version": "product_report_summary_v2",
                "prompt_content": HISTORICAL_PRODUCT_V2_PROMPT,
            }
        )
        == "upgrade"
    )


def test_prompt_seed_action_upgrades_only_exact_known_builtin_v1(monkeypatch) -> None:
    import hashlib

    from app.services import system_settings

    scene = system_settings.MARKET_REPORT_PROMPT_SCENE
    version = "market_report_summary_v1"
    legacy_content = "exact historical builtin"
    monkeypatch.setitem(
        system_settings.LEGACY_REPORT_PROMPT_HASHES,
        (scene, version),
        hashlib.sha256(legacy_content.encode("utf-8")).hexdigest(),
    )

    assert (
        system_settings._prompt_seed_action(
            {
                "prompt_scene": scene,
                "prompt_version": version,
                "prompt_content": legacy_content,
            }
        )
        == "upgrade"
    )
    assert (
        system_settings._prompt_seed_action(
            {
                "prompt_scene": scene,
                "prompt_version": version,
                "prompt_content": "administrator custom content",
            }
        )
        == "keep"
    )
    assert (
        system_settings._prompt_seed_action(
            {
                "prompt_scene": scene,
                "prompt_version": system_settings.MARKET_REPORT_PROMPT_VERSION,
                "prompt_content": system_settings.MARKET_REPORT_PROMPT_CONTENT,
            }
        )
        == "keep"
    )


def test_ensure_default_prompt_replaces_builtin_v1_but_keeps_custom(monkeypatch) -> None:
    from app.services import system_settings

    class FakeCursor:
        def __init__(self, statements):
            self.statements = statements

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def execute(self, statement, params):
            self.statements.append((" ".join(statement.split()), params))

    class FakeConnection:
        def __init__(self):
            self.statements = []

        def cursor(self):
            return FakeCursor(self.statements)

    builtin_v1 = {
        "prompt_scene": system_settings.MARKET_REPORT_PROMPT_SCENE,
        "prompt_version": "market_report_summary_v1",
        "prompt_content": "known builtin",
    }
    custom_v1 = {**builtin_v1, "prompt_content": "administrator custom"}
    seeded = []
    connection = FakeConnection()
    monkeypatch.setattr(
        system_settings,
        "_seed_default_prompt_template",
        lambda conn, scene: seeded.append(scene)
        or {
            "prompt_scene": scene,
            "prompt_version": system_settings.MARKET_REPORT_PROMPT_VERSION,
            "prompt_content": system_settings.MARKET_REPORT_PROMPT_CONTENT,
        },
    )
    monkeypatch.setattr(system_settings, "_prompt_seed_action", lambda row: "upgrade")
    monkeypatch.setattr(system_settings, "_get_enabled_default_prompt", lambda conn, scene: builtin_v1)
    monkeypatch.setattr(
        system_settings,
        "_get_prompt_by_version",
        lambda conn, scene, version: None,
    )

    upgraded = system_settings._ensure_default_prompt_template(
        connection,
        system_settings.MARKET_REPORT_PROMPT_SCENE,
    )

    assert upgraded["prompt_version"] == system_settings.MARKET_REPORT_PROMPT_VERSION
    assert seeded == [system_settings.MARKET_REPORT_PROMPT_SCENE]
    assert connection.statements == [
        (
            "UPDATE data_asset.system_prompt_template SET is_default = FALSE WHERE prompt_scene = %s",
            (system_settings.MARKET_REPORT_PROMPT_SCENE,),
        )
    ]

    monkeypatch.setattr(system_settings, "_prompt_seed_action", lambda row: "keep")
    monkeypatch.setattr(system_settings, "_get_enabled_default_prompt", lambda conn, scene: custom_v1)
    assert (
        system_settings._ensure_default_prompt_template(
            connection,
            system_settings.MARKET_REPORT_PROMPT_SCENE,
        )
        == custom_v1
    )
    assert seeded == [system_settings.MARKET_REPORT_PROMPT_SCENE]


def test_builtin_v1_upgrade_does_not_activate_conflicting_custom_v2(monkeypatch) -> None:
    from app.services import system_settings

    builtin_v1 = {
        "prompt_scene": system_settings.MARKET_REPORT_PROMPT_SCENE,
        "prompt_version": "market_report_summary_v1",
        "prompt_content": "known builtin v1",
        "is_default": True,
        "is_enabled": True,
    }
    custom_v2 = {
        "prompt_scene": system_settings.MARKET_REPORT_PROMPT_SCENE,
        "prompt_version": system_settings.MARKET_REPORT_PROMPT_VERSION,
        "prompt_content": "administrator disabled custom v2",
        "is_default": False,
        "is_enabled": False,
    }
    monkeypatch.setattr(
        system_settings,
        "_get_enabled_default_prompt",
        lambda conn, scene: builtin_v1,
    )
    monkeypatch.setattr(system_settings, "_prompt_seed_action", lambda row: "upgrade")
    monkeypatch.setattr(
        system_settings,
        "_get_prompt_by_version",
        lambda conn, scene, version: custom_v2,
        raising=False,
    )
    monkeypatch.setattr(
        system_settings,
        "_seed_default_prompt_template",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            AssertionError("custom v2 must not be seeded or activated")
        ),
    )

    assert (
        system_settings._ensure_default_prompt_template(
            object(),
            system_settings.MARKET_REPORT_PROMPT_SCENE,
        )
        == builtin_v1
    )
