from pathlib import Path


def test_upload_form_reference_is_captured_before_async_request() -> None:
    script = Path("app/static/app.js").read_text(encoding="utf-8")

    assert "const uploadForm = event.currentTarget;" in script
    assert "new FormData(uploadForm)" in script
    assert "uploadForm.reset();" in script
    assert "event.currentTarget.reset()" not in script
