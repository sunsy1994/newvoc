from app.services.competitor_library import (
    ACCOUNT_COLUMNS,
    WORK_COLUMNS,
    build_work_filters,
)


def test_competitor_column_definitions_are_business_facing() -> None:
    account_keys = [column["key"] for column in ACCOUNT_COLUMNS]
    work_keys = [column["key"] for column in WORK_COLUMNS]

    assert account_keys == [
        "account_name",
        "brand_name",
        "account_type",
        "is_official",
        "is_enabled",
        "account_home_url",
        "remark",
    ]
    assert "work_id" in work_keys
    assert "published_at" in work_keys
    assert "video_url" in work_keys


def test_build_work_filters_supports_published_date_range_and_query() -> None:
    where_sql, params = build_work_filters(
        q="途观",
        brand_name="上汽大众",
        account_type="经销商",
        start_date="2026-05-01",
        end_date="2026-05-31",
    )

    assert "w.published_at >= %s" in where_sql
    assert "w.published_at < (%s::date + INTERVAL '1 day')" in where_sql
    assert "w.brand_name = %s" in where_sql
    assert "w.account_type = %s" in where_sql
    assert params == ["上汽大众", "经销商", "2026-05-01", "2026-05-31", "%途观%", "%途观%", "%途观%"]
