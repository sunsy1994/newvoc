from __future__ import annotations

import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ScriptManager:
    def __init__(self, script_path: Path, backup_dir: Path) -> None:
        self.script_path = Path(script_path)
        self.backup_dir = Path(backup_dir)

    def read_script(self) -> dict[str, Any]:
        stat = self.script_path.stat()
        return {
            "path": str(self.script_path),
            "content": self.script_path.read_text(encoding="utf-8"),
            "updated_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat().replace("+00:00", "Z"),
            "size": stat.st_size,
            "backups": self.list_backups(),
        }

    def save_script(self, content: str) -> dict[str, Any]:
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
        backup_path = self.backup_dir / f"{self.script_path.stem}_{timestamp}{self.script_path.suffix}"
        shutil.copy2(self.script_path, backup_path)
        self.script_path.write_text(content, encoding="utf-8")
        return self.read_script()

    def list_backups(self) -> list[dict[str, Any]]:
        if not self.backup_dir.exists():
            return []
        backups = []
        pattern = f"{self.script_path.stem}_*{self.script_path.suffix}"
        for path in sorted(self.backup_dir.glob(pattern), key=lambda item: item.stat().st_mtime, reverse=True):
            stat = path.stat()
            backups.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "created_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat().replace("+00:00", "Z"),
                    "size": stat.st_size,
                }
            )
        return backups[:10]
