from app.services.system_settings import mask_api_key


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


def test_builtin_product_v2_prompt_is_registered_for_v3_upgrade() -> None:
    from app.services import system_settings

    assert (
        system_settings.PRODUCT_REPORT_PROMPT_SCENE,
        "product_report_summary_v2",
    ) in system_settings.LEGACY_REPORT_PROMPT_HASHES


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
