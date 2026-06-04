from pathlib import Path

import pandas as pd

from app.services.profile_library import KOL_PROFILE_COLUMNS, prepare_kol_profile_upload


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
