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
