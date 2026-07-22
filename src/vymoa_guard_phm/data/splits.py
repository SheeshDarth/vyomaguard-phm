"""Leakage-aware chronological split helpers."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def temporal_split(rows: list[dict[str, Any]], time_key: str = "timestamp", test_fraction: float = 0.2) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not rows:
        return [], []
    ordered = sorted(rows, key=lambda row: str(row.get(time_key, "")))
    cut = max(1, min(len(ordered) - 1, int(round(len(ordered) * (1 - test_fraction))))) if len(ordered) > 1 else len(ordered)
    return ordered[:cut], ordered[cut:]


def assert_no_overlap(train: list[dict[str, Any]], test: list[dict[str, Any]], key: str) -> None:
    train_keys = {row.get(key) for row in train}
    test_keys = {row.get(key) for row in test}
    overlap = train_keys & test_keys
    if overlap:
        raise ValueError(f"Leakage detected for {key}: {sorted(str(item) for item in overlap)}")

