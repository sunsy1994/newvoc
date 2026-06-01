from decimal import Decimal

from app.services.asset_library import ASSET_DEFINITIONS, build_like_pattern, normalize_row


def test_asset_definitions_expose_only_business_columns() -> None:
    forbidden = {"event_id", "content_id", "author_id", "comment_id", "event_key", "content_key", "author_key", "ingest_batch_id", "raw_source_key"}

    for definition in ASSET_DEFINITIONS.values():
        keys = {column["key"] for column in definition.columns}
        assert keys
        assert not keys.intersection(forbidden)


def test_event_asset_columns_are_business_facing() -> None:
    labels = [column["label"] for column in ASSET_DEFINITIONS["events"].columns]

    assert labels == [
        "事件名称",
        "事件类型",
        "品牌",
        "车型",
        "开始时间",
        "结束时间",
        "状态",
        "内容数",
        "评论数",
        "作者数",
        "KOL内容数",
        "总互动量",
    ]


def test_author_and_kol_assets_are_separate() -> None:
    assert ASSET_DEFINITIONS["authors"].label == "作者资产"
    assert ASSET_DEFINITIONS["kols"].label == "KOL资产"
    assert "(a.is_kol = false OR a.is_kol IS NULL)" in ASSET_DEFINITIONS["authors"].base_where
    assert "a.is_kol = true" in ASSET_DEFINITIONS["kols"].base_where

    author_columns = {column["key"] for column in ASSET_DEFINITIONS["authors"].columns}
    kol_columns = {column["key"] for column in ASSET_DEFINITIONS["kols"].columns}
    assert "is_kol" not in author_columns
    assert {"content_cnt", "received_comment_cnt", "total_engagement"}.issubset(author_columns)
    assert {"content_cnt", "received_comment_cnt", "total_engagement"}.issubset(kol_columns)


def test_comment_user_asset_is_aggregated_from_comments() -> None:
    definition = ASSET_DEFINITIONS["comment_users"]

    assert definition.label == "评论用户资产"
    assert [column["key"] for column in definition.columns] == [
        "platform",
        "comment_author_name",
        "location",
        "comment_cnt",
        "participated_content_cnt",
        "participated_event_cnt",
        "like_cnt",
        "reply_cnt",
        "latest_comment_at",
    ]


def test_build_like_pattern_escapes_search_text() -> None:
    assert build_like_pattern("  ID_100%  ") == "%ID\\_100\\%%"


def test_normalize_row_converts_decimal_values() -> None:
    assert normalize_row({"total_engagement": Decimal("12"), "rate": Decimal("1.5")}) == {
        "total_engagement": 12,
        "rate": 1.5,
    }
