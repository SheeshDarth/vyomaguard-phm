"""Leakage-aware chronological split helpers."""

from __future__ import annotations

from typing import Any


def temporal_split(rows: list[dict[str, Any]], time_key: str = "timestamp", test_fraction: float = 0.2) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not rows:
        return [], []
    ordered = sorted(rows, key=lambda row: str(row.get(time_key, "")))
    cut = max(1, min(len(ordered) - 1, int(round(len(ordered) * (1 - test_fraction))))) if len(ordered) > 1 else len(ordered)
    return ordered[:cut], ordered[cut:]


def group_temporal_split(
    rows: list[dict[str, Any]],
    *,
    group_key: str,
    time_key: str,
    test_fraction: float = 0.2,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Split whole groups in deterministic time order.

    The function is intentionally generic. For ESA orbit data, callers pass
    one source-order-selected final CDM row per event, so the time field is a
    declared temporal ordering proxy rather than an implicit row sort.
    """

    if not rows:
        return [], []
    grouped: dict[str, list[dict[str, Any]]] = {}
    group_time: dict[str, float | str] = {}
    for row in rows:
        group = str(row.get(group_key, "")).strip()
        if not group:
            raise ValueError(f"Missing group key {group_key!r}.")
        raw_time = row.get(time_key)
        if raw_time is None or str(raw_time).strip() == "":
            raise ValueError(f"Missing time key {time_key!r} for group {group!r}.")
        try:
            parsed_time: float | str = float(raw_time)
        except (TypeError, ValueError):
            parsed_time = str(raw_time)
        grouped.setdefault(group, []).append(row)
        if group not in group_time or parsed_time < group_time[group]:
            group_time[group] = parsed_time
    ordered_groups = sorted(grouped, key=lambda group: group_time[group])
    cut = max(1, min(len(ordered_groups) - 1, int(round(len(ordered_groups) * (1 - test_fraction))))) if len(ordered_groups) > 1 else len(ordered_groups)
    train = [row for group in ordered_groups[:cut] for row in grouped[group]]
    test = [row for group in ordered_groups[cut:] for row in grouped[group]]
    assert_no_overlap(train, test, group_key)
    return train, test


def assert_no_overlap(train: list[dict[str, Any]], test: list[dict[str, Any]], key: str) -> None:
    train_keys = {row.get(key) for row in train}
    test_keys = {row.get(key) for row in test}
    overlap = train_keys & test_keys
    if overlap:
        raise ValueError(f"Leakage detected for {key}: {sorted(str(item) for item in overlap)}")
