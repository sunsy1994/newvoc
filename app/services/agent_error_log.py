from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class AgentErrorLog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def append(
        self,
        *,
        capability: str,
        question: str,
        error_reason: str,
        history: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        record = {
            "record_id": uuid4().hex,
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "capability": capability,
            "question": question,
            "error_reason": error_reason,
            "history_size": len(history or []),
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def list(self, limit: int = 100) -> dict[str, list[dict[str, Any]]]:
        safe_limit = max(1, min(int(limit or 100), 500))
        if not self.path.exists():
            return {"records": []}
        records: list[dict[str, Any]] = []
        with self.path.open("r", encoding="utf-8") as file:
            for line in file:
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    records.append(payload)
        records.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        return {"records": records[:safe_limit]}
