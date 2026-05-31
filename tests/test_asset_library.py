from app.services.asset_library import ASSET_DEFINITIONS, build_like_pattern


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


def test_build_like_pattern_escapes_search_text() -> None:
    assert build_like_pattern("  ID_100%  ") == "%ID\\_100\\%%"
