from pathlib import Path

from app.services.script_manager import ScriptManager


def test_read_script_returns_metadata(tmp_path: Path) -> None:
    script = tmp_path / "etl.py"
    script.write_text("def run_etl():\n    pass\n", encoding="utf-8")
    manager = ScriptManager(script, tmp_path / "backups")

    payload = manager.read_script()

    assert payload["path"] == str(script)
    assert payload["content"].startswith("def run_etl")
    assert payload["size"] > 0
    assert payload["backups"] == []


def test_save_script_creates_backup_before_writing(tmp_path: Path) -> None:
    script = tmp_path / "etl.py"
    script.write_text("old content", encoding="utf-8")
    manager = ScriptManager(script, tmp_path / "backups")

    payload = manager.save_script("new content")

    assert script.read_text(encoding="utf-8") == "new content"
    backups = list((tmp_path / "backups").glob("etl_*.py"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "old content"
    assert payload["content"] == "new content"
    assert payload["backups"][0]["name"] == backups[0].name
