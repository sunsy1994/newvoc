from pathlib import Path

import pandas as pd

import pytest

from app.services.profile_library import (
    COMMENT_USER_PROFILE_COLUMNS,
    build_comment_user_id,
    load_kol_profiles,
    prepare_comment_user_llm_upload,
    prepare_kol_profile_upload,
    summarize_comment_user_profile,
    KOL_PROFILE_COLUMNS,
)


def test_kol_profile_columns_match_prompt_output() -> None:
    keys = [column["key"] for column in KOL_PROFILE_COLUMNS]

    assert keys == [
        "author_id",
        "platform",
        "author_name",
        "author_home_url",
        "kol_main_type",
        "content_tendency",
        "car_focus",
        "remark",
        "profile_batch",
        "source_file_name",
        "updated_time",
    ]


def test_prepare_kol_profile_upload_uses_author_id_and_prompt_fields(tmp_path: Path) -> None:
    upload_path = tmp_path / "kol_profile.xlsx"
    pd.DataFrame(
        [
            {
                "author_id": "author_001",
                "kol_main_type": "车型实测测评KOL",
                "content_tendency": "偏客观实测",
                "car_focus": "燃油车专注",
                "remark": "近7日测评内容占比最高",
                "profile_batch": "prompt_v1",
            }
        ]
    ).to_excel(upload_path, index=False)

    dataframe = prepare_kol_profile_upload(upload_path)

    assert dataframe.loc[0, "author_id"] == "author_001"
    assert dataframe.loc[0, "profile_batch"] == "prompt_v1"
    assert dataframe.loc[0, "kol_main_type"] == "车型实测测评KOL"


def test_prepare_kol_profile_upload_accepts_chinese_headers(tmp_path: Path) -> None:
    upload_path = tmp_path / "kol_profile_cn.xlsx"
    pd.DataFrame(
        [
            {
                "作者ID": "author_001",
                "KOL主类型": "车型实测测评KOL",
                "内容倾向": "偏客观实测",
                "车型关注": "燃油车专注",
                "判定依据": "近7日测评内容占比最高",
                "画像批次": "prompt_v1",
            }
        ]
    ).to_excel(upload_path, index=False)

    dataframe = prepare_kol_profile_upload(upload_path)

    assert dataframe.loc[0, "author_id"] == "author_001"
    assert dataframe.loc[0, "profile_batch"] == "prompt_v1"


def test_load_kol_profiles_rejects_upload_without_author_id(tmp_path: Path) -> None:
    upload_path = tmp_path / "kol_profile_missing_id.xlsx"
    pd.DataFrame([{"kol_main_type": "车型实测测评KOL"}]).to_excel(upload_path, index=False)

    with pytest.raises(ValueError, match="author_id"):
        load_kol_profiles(upload_path, "kol_profile_missing_id.xlsx")


def test_comment_user_profile_columns_show_label_and_reason_fields() -> None:
    keys = [column["key"] for column in COMMENT_USER_PROFILE_COLUMNS]

    assert keys == [
        "comment_user_id",
        "platform",
        "comment_author_name",
        "location",
        "main_dimension",
        "main_label",
        "main_score",
        "total_comments",
        "valid_comments",
        "profile_batch",
        "prompt_version",
        "source_file_name",
        "updated_time",
    ]


def test_build_comment_user_id_is_stable_from_platform_name_and_location() -> None:
    first_id = build_comment_user_id("douyin", "driver_a", "beijing")
    second_id = build_comment_user_id("douyin", " driver_a ", "beijing")

    assert first_id == second_id
    assert first_id.startswith("comment_user_")


def test_prepare_comment_user_llm_upload_parses_json_and_keeps_batch(tmp_path: Path) -> None:
    upload_path = tmp_path / "comment_user_profile.xlsx"
    pd.DataFrame(
        [
            {
                "comment_user_id": "comment_user_001",
                "profile_batch": "prompt_v1",
                "prompt_version": "user_profile_v1",
                "llm_result_json": '{"total_comments": 1, "valid_comments": 1, "comment_evidence_results": []}',
            }
        ]
    ).to_excel(upload_path, index=False)

    dataframe = prepare_comment_user_llm_upload(upload_path, "comment_user_profile.xlsx")

    assert dataframe.loc[0, "comment_user_id"] == "comment_user_001"
    assert dataframe.loc[0, "profile_batch"] == "prompt_v1"
    assert dataframe.loc[0, "prompt_version"] == "user_profile_v1"
    assert dataframe.loc[0, "llm_result_json"]["total_comments"] == 1
    assert dataframe.loc[0, "source_file_name"] == "comment_user_profile.xlsx"


def test_prepare_comment_user_llm_upload_rejects_invalid_json(tmp_path: Path) -> None:
    upload_path = tmp_path / "comment_user_profile_bad.xlsx"
    pd.DataFrame([{"comment_user_id": "comment_user_001", "llm_result_json": "{bad json"}]).to_excel(
        upload_path,
        index=False,
    )

    with pytest.raises(ValueError, match="llm_result_json"):
        prepare_comment_user_llm_upload(upload_path, "comment_user_profile_bad.xlsx")


def test_summarize_comment_user_profile_returns_main_label_and_evidence_reason() -> None:
    llm_result = {
        "total_comments": 2,
        "valid_comments": 2,
        "comment_evidence_results": [
            {
                "comment_id": "c1",
                "comment_text": "price is important",
                "is_valid": True,
                "comment_quality_score": 0.9,
                "emotion": {"emotion_level": "low"},
                "evidence_list": [
                    {
                        "dimension": "purchase_need",
                        "label": "price_sensitive",
                        "evidence_score": 0.9,
                        "evidence_text": "price is important",
                        "reason": "focuses on cost",
                    }
                ],
            }
        ],
    }

    profile = summarize_comment_user_profile("comment_user_001", llm_result)

    assert profile["comment_user_id"] == "comment_user_001"
    assert profile["main_dimension"] == "purchase_need"
    assert profile["main_label"] == "price_sensitive"
    assert profile["label_scores"][0]["evidence_details"][0]["reason"] == "focuses on cost"
