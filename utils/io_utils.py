from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, Any


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(dict(row), ensure_ascii=False, default=str) + "\n")


def append_jsonl(path: Path, row: Mapping[str, Any]) -> None:
    ensure_dir(path.parent)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(dict(row), ensure_ascii=False, default=str) + "\n")


def write_json(path: Path, data: Mapping[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(dict(data), ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))
