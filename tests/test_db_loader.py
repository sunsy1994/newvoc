from pathlib import Path

import pandas as pd

from app.services.db_loader import (
    TABLE_PRIMARY_KEYS,
    normalize_db_value,
    prepare_dataframe_for_table,
    resolve_load_tables,
)


def test_prepare_ods_adds_batch_metadata() -> None:
    dataframe = pd.DataFrame([{"raw_event_id": "EVT-001", "event_name": "上市事件"}])

    prepared = prepare_dataframe_for_table("ods_event_upload", dataframe, "batch_001")

    assert prepared.loc[0, "ingest_batch_id"] == "batch_001"
    assert prepared.loc[0, "source_file_name"] == "ods_event_upload.csv"
    assert prepared.loc[0, "raw_row_no"] == 2


def test_prepare_dwd_content_drops_generated_column() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "content_id": "CONTENT-001",
                "content_key": "key",
                "event_id": "EVT-001",
                "platform": "抖音",
                "source_url": "https://example.com/a",
                "title": "标题",
                "published_at": "2026-05-01",
                "engagement_total": 100,
            }
        ]
    )

    prepared = prepare_dataframe_for_table("dwd_content", dataframe, "batch_001")

    assert "engagement_total" not in prepared.columns
    assert prepared.loc[0, "content_id"] == "CONTENT-001"


def test_resolve_load_tables_only_returns_existing_known_outputs(tmp_path: Path) -> None:
    (tmp_path / "dwd_event.csv").write_text("event_id\nEVT-001\n", encoding="utf-8")
    (tmp_path / "unknown.csv").write_text("x\n1\n", encoding="utf-8")

    tables = resolve_load_tables(tmp_path)

    assert tables == [("dwd_event", tmp_path / "dwd_event.csv")]
    assert TABLE_PRIMARY_KEYS["dwd_event"] == ["event_id"]


def test_normalize_boolean_chinese_values() -> None:
    assert normalize_db_value("是", "is_kol") is True
    assert normalize_db_value("否", "is_kol") is False


def test_normalize_numeric_placeholders_to_none() -> None:
    assert normalize_db_value("--", "reply_cnt") is None
    assert normalize_db_value("-", "favorite_cnt") is None
    assert normalize_db_value("1,234", "like_cnt") == 1234
