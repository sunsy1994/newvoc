from pathlib import Path

import pandas as pd

import pytest

from app.services.profile_library import KOL_PROFILE_COLUMNS, load_kol_profiles, prepare_kol_profile_upload


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
