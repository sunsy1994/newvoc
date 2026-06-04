from pathlib import Path


def test_upload_form_reference_is_captured_before_async_request() -> None:
    script = Path("app/static/app.js").read_text(encoding="utf-8")

    assert "const uploadForm = event.currentTarget;" in script
    assert "new FormData(uploadForm)" in script
    assert "uploadForm.reset();" in script
    assert "event.currentTarget.reset()" not in script


def test_etl_transparency_ui_is_present() -> None:
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    script = Path("app/static/app.js").read_text(encoding="utf-8")

    assert "ETL 清理流程" in html
    assert "脚本维护" in html
    assert 'api("/api/etl/script"' in script
    assert "/api/etl/flow" in script


def test_task_management_uses_submenu_views() -> None:
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    script = Path("app/static/app.js").read_text(encoding="utf-8")

    assert 'data-view-target="import-view"' in html
    assert 'data-view-target="flow-view"' in html
    assert 'data-view-target="script-view"' in html
    assert 'class="workbench-view active" id="import-view"' in html
    assert "activateView" in script


def test_asset_library_ui_is_present() -> None:
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    script = Path("app/static/app.js").read_text(encoding="utf-8")

    assert "资产库" in html
    assert 'id="asset-library-view"' in html
    assert 'data-asset-key="events"' in html
    assert 'data-asset-key="contents"' in html
    assert 'data-asset-key="comments"' in html
    assert 'data-asset-key="authors"' in html
    assert 'data-asset-key="kols"' in html
    assert 'data-asset-key="comment_users"' in html
    assert "KOL资产" in html
    assert "评论用户资产" in html
    assert "/api/assets/" in script
    assert "资产库加载失败" in script


def test_competitor_activity_ui_is_present() -> None:
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    script = Path("app/static/app.js").read_text(encoding="utf-8")

    assert 'data-main-target="competitor-activity-view"' in html
    assert "竞品动态" in html
    assert 'data-competitor-target="competitor-accounts-view"' in html
    assert 'data-competitor-target="competitor-works-view"' in html
    assert 'id="competitor-start-date"' in html
    assert 'id="competitor-end-date"' in html
    assert "/api/competitors/works" in script


def test_profile_maintenance_ui_is_present() -> None:
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    script = Path("app/static/app.js").read_text(encoding="utf-8")

    assert 'data-main-target="profile-maintenance-view"' in html
    assert "用户画像维护" in html
    assert 'data-profile-target="kol-profile-view"' in html
    assert 'id="export-kol-samples"' in html
    assert 'id="kol-profile-upload-form"' in html
    assert "/api/profiles/kols" in script
    assert 'src="/static/app.js?v=' in html


def test_tables_have_pagination_and_export_controls() -> None:
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    script = Path("app/static/app.js").read_text(encoding="utf-8")

    for element_id in [
        "table-pager",
        "asset-pager",
        "competitor-account-pager",
        "competitor-work-pager",
        "export-table",
        "export-asset",
        "export-competitor-accounts",
        "export-competitor-works",
    ]:
        assert f'id="{element_id}"' in html

    assert "renderPager" in script
    assert "/export" in script


def test_competitor_work_filter_keeps_export_button_on_same_row() -> None:
    styles = Path("app/static/styles.css").read_text(encoding="utf-8")

    assert ".competitor-filters" in styles
    assert "repeat(4, minmax(112px, 130px)) auto auto" in styles


def test_asset_library_is_not_nested_inside_task_workbench() -> None:
    html = Path("app/static/index.html").read_text(encoding="utf-8")
    task_start = html.index('id="task-workbench-view"')
    asset_start = html.index('id="asset-library-view"')
    between = html[task_start:asset_start]

    assert '</section>\n\n    <section class="main-view" id="asset-library-view">' in html
    assert between.count('<section') == between.count('</section>')
