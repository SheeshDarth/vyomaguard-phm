"""Explicit local dataset adapters; downloads are intentionally out of scope."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def load_json_records(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    if isinstance(payload, dict) and isinstance(payload.get("records"), list):
        return [dict(item) for item in payload["records"]]
    raise ValueError("Expected a JSON list or an object containing a 'records' list.")


def load_csv_records(path: str | Path) -> list[dict[str, Any]]:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def load_records(path: str | Path) -> list[dict[str, Any]]:
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return load_json_records(path)
    if suffix == ".csv":
        return load_csv_records(path)
    raise ValueError(f"Unsupported dataset format: {suffix or '<none>'}. Use JSON or CSV.")


def manifest_for(path: str | Path, *, dataset_id: str, label_definition: str, split_strategy: str = "temporal") -> dict[str, Any]:
    file_path = Path(path)
    return {
        "dataset_id": dataset_id,
        "source_name": "local-file",
        "source_snapshot": file_path.name,
        "path": str(file_path),
        "label_definition": label_definition,
        "split_strategy": split_strategy,
        "status": "UNVERIFIED",
        "notes": "Complete the source, checksum, license, and schema fields before training.",
    }

