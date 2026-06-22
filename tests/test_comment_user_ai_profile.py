from pathlib import Path

import pytest

from app.services.profile_library import build_comment_user_id


def test_render_comment_user_profile_prompt_replaces_input_section() -> None:
    from app.services.comment_user_ai_profile import render_comment_user_profile_prompt

    template = """你是一名汽车行业 VOC 用户画像语义证据抽取专家。

====================
三、输入格式
====================

用户ID：{{user_id}}

评论列表：
1. {{comment_1}}
2. {{comment_2}}
...

====================
四、输出格式
====================

请严格输出 JSON。
"""
    comments = [
        {"comment_id": "c1", "comment_text": "外观很好看，价格再优惠点就好了"},
        {"comment_id": "c2", "comment_text": "更关心后排空间"},
    ]

    prompt = render_comment_user_profile_prompt(template, "comment_user_001", comments)

    assert "用户ID：comment_user_001" in prompt
    assert "1. [comment_id=c1] 外观很好看，价格再优惠点就好了" in prompt
    assert "2. [comment_id=c2] 更关心后排空间" in prompt
    assert "{{comment_1}}" not in prompt
    assert "四、输出格式" in prompt


def test_build_openai_chat_payload_uses_json_response_format() -> None:
    from app.services.comment_user_ai_profile import build_openai_chat_payload

    payload = build_openai_chat_payload("profile-model", "rendered prompt")

    assert payload["model"] == "profile-model"
    assert payload["messages"] == [{"role": "user", "content": "rendered prompt"}]
    assert payload["response_format"] == {"type": "json_object"}
    assert payload["temperature"] == 0


def test_parse_openai_json_response_requires_json_object() -> None:
    from app.services.comment_user_ai_profile import parse_openai_json_response

    payload = {
        "choices": [
            {
                "message": {
                    "content": '{"user_id": "comment_user_001", "total_comments": 1, "comment_evidence_results": []}'
                }
            }
        ]
    }

    parsed = parse_openai_json_response(payload)

    assert parsed["user_id"] == "comment_user_001"


def test_parse_openai_json_response_rejects_non_json() -> None:
    from app.services.comment_user_ai_profile import parse_openai_json_response

    with pytest.raises(ValueError, match="JSON"):
        parse_openai_json_response({"choices": [{"message": {"content": "not json"}}]})


def test_filter_global_comment_rows_matches_system_comment_user_id() -> None:
    from app.services.comment_user_ai_profile import filter_comment_rows_by_user_id

    target_id = build_comment_user_id("抖音", "九月九的酒", "上海")
    rows = [
        {"platform": "抖音", "comment_author_name": "九月九的酒", "location": "上海", "comment_id": "c1"},
        {"platform": "小红书", "comment_author_name": "其他用户", "location": "北京", "comment_id": "c2"},
        {"platform": "抖音", "comment_author_name": "九月九的酒", "location": "上海", "comment_id": "c3"},
    ]

    matched = filter_comment_rows_by_user_id(rows, target_id)

    assert [row["comment_id"] for row in matched] == ["c1", "c3"]
    assert all(row["comment_user_id"] == target_id for row in matched)


def test_fetch_global_comment_rows_executes_query_before_fetch(monkeypatch) -> None:
    from app.services import comment_user_ai_profile

    calls = []

    class FakeCursor:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def execute(self, query):
            calls.append(("execute", "FROM data_asset.dwd_comment" in query))

        def fetchall(self):
            calls.append(("fetchall", None))
            return [
                {
                    "comment_id": "c1",
                    "content_id": "content_1",
                    "content_title": "post",
                    "source_url": "https://example.test",
                    "platform": "抖音",
                    "location": "上海",
                    "comment_author_name": "九月九的酒",
                    "comment_text": "空间不错",
                    "published_at": None,
                    "like_cnt": 0,
                    "reply_cnt": 0,
                    "interaction_cnt": 0,
                }
            ]

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def cursor(self):
            return FakeCursor()

    monkeypatch.setattr(comment_user_ai_profile.psycopg, "connect", lambda *args, **kwargs: FakeConnection())

    rows = comment_user_ai_profile.fetch_global_comment_rows("postgresql://example")

    assert calls[:2] == [("execute", True), ("fetchall", None)]
    assert rows[0]["comment_id"] == "c1"


def test_run_comment_user_ai_profile_uses_prompt_and_loader(tmp_path: Path, monkeypatch) -> None:
    from app.services import comment_user_ai_profile

    prompt_path = tmp_path / "画像提示词.txt"
    prompt_path.write_text(
        """说明

====================
三、输入格式
====================

用户ID：{{user_id}}

评论列表：
1. {{comment_1}}
...

====================
四、输出格式
====================

请严格输出 JSON。
""",
        encoding="utf-8",
    )
    comment_user_id = build_comment_user_id("抖音", "九月九的酒", "上海")
    comments = [
        {
            "platform": "抖音",
            "comment_author_name": "九月九的酒",
            "location": "上海",
            "comment_id": "c1",
            "comment_text": "我主要看价格和空间",
        }
    ]
    captured = {}

    monkeypatch.setattr(comment_user_ai_profile, "fetch_global_comment_rows", lambda database_url=None: comments)

    def fake_call(prompt, *, base_url, api_key, model, timeout_seconds):
        captured["prompt"] = prompt
        captured["base_url"] = base_url
        captured["model"] = model
        return {
            "user_id": comment_user_id,
            "total_comments": 1,
            "valid_comments": 1,
            "comment_evidence_results": [],
        }

    monkeypatch.setattr(comment_user_ai_profile, "call_openai_compatible_json", fake_call)

    def fake_loader(records, database_url=None):
        captured["records"] = records
        return {"raw_loaded": 1, "profiles_loaded": 1, "label_scores_loaded": 0}

    monkeypatch.setattr(comment_user_ai_profile, "load_comment_user_profile_records", fake_loader)

    result = comment_user_ai_profile.run_comment_user_ai_profile(
        comment_user_id,
        profile_batch="batch_ai",
        prompt_version="comment_user_profile_v1",
        prompt_path=prompt_path,
        base_url="https://llm.example/v1",
        api_key="secret",
        model="profile-model",
    )

    assert result["comment_count"] == 1
    assert result["db_loaded"]["profiles_loaded"] == 1
    assert "1. [comment_id=c1] 我主要看价格和空间" in captured["prompt"]
    assert captured["records"][0]["comment_user_id"] == comment_user_id
    assert captured["records"][0]["llm_result_json"]["total_comments"] == 1


def test_run_comment_user_ai_profile_uses_managed_config_and_prompt_when_no_file(monkeypatch) -> None:
    from app.services import comment_user_ai_profile

    comment_user_id = build_comment_user_id("抖音", "九月九的酒", "上海")
    comments = [
        {
            "platform": "抖音",
            "comment_author_name": "九月九的酒",
            "location": "上海",
            "comment_id": "c1",
            "comment_text": "我主要看价格和空间",
        }
    ]
    captured = {}

    monkeypatch.setattr(comment_user_ai_profile, "fetch_global_comment_rows", lambda database_url=None: comments)
    monkeypatch.setattr(
        comment_user_ai_profile,
        "get_runtime_ai_config",
        lambda database_url=None: {
            "base_url": "https://managed.example/v1",
            "api_key": "managed-secret",
            "model_name": "managed-model",
            "timeout_seconds": 88,
            "is_enabled": True,
        },
    )
    monkeypatch.setattr(
        comment_user_ai_profile,
        "get_default_prompt_template",
        lambda scene, database_url=None: {
            "prompt_version": "managed_prompt_v1",
            "prompt_content": "固定提示词\n\n用户ID：{{user_id}}\n\n评论列表：\n1. {{comment_1}}\n",
        },
    )

    def fake_call(prompt, *, base_url, api_key, model, timeout_seconds):
        captured.update(
            {
                "prompt": prompt,
                "base_url": base_url,
                "api_key": api_key,
                "model": model,
                "timeout_seconds": timeout_seconds,
            }
        )
        return {"total_comments": 1, "valid_comments": 1, "comment_evidence_results": []}

    monkeypatch.setattr(comment_user_ai_profile, "call_openai_compatible_json", fake_call)

    def fake_loader(records, database_url=None):
        captured["records"] = records
        return {"raw_loaded": 1, "profiles_loaded": 1, "label_scores_loaded": 0}

    monkeypatch.setattr(comment_user_ai_profile, "load_comment_user_profile_records", fake_loader)

    result = comment_user_ai_profile.run_comment_user_ai_profile(comment_user_id, profile_batch="batch_ai", prompt_path=None)

    assert result["prompt_version"] == "managed_prompt_v1"
    assert captured["base_url"] == "https://managed.example/v1"
    assert captured["api_key"] == "managed-secret"
    assert captured["model"] == "managed-model"
    assert captured["timeout_seconds"] == 88
    assert "1. [comment_id=c1] 我主要看价格和空间" in captured["prompt"]
    assert captured["records"][0]["source_file_name"] == "system_prompt:managed_prompt_v1"
