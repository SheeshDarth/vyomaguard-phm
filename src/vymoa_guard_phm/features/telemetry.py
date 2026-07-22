"""Robust telemetry statistics and bounded anomaly scoring."""

from __future__ import annotations

from collections import defaultdict
from statistics import median
from typing import Any


def grouped_values(rows: list[dict[str, Any]]) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        try:
            grouped[str(row["channel"])].append(float(row["value"]))
        except (KeyError, TypeError, ValueError):
            continue
    return dict(grouped)


def _baseline(values: list[float]) -> tuple[float, float]:
    center = median(values)
    deviations = [abs(value - center) for value in values]
    return center, median(deviations) or 1e-6


def robust_channel_scores(
    rows: list[dict[str, Any]],
    *,
    baselines: dict[str, tuple[float, float]] | None = None,
    window_size: int = 24,
) -> tuple[float, list[str], dict[str, Any] | None, list[str]]:
    """Score channel deviations using train-fitted robust rolling baselines."""

    grouped_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        try:
            grouped_rows[str(row["channel"])].append(row)
        except (KeyError, TypeError):
            continue
    if not grouped_rows:
        return 0.0, [], None, []
    channel_scores: dict[str, float] = {}
    high_rows: list[dict[str, Any]] = []
    evidence: list[str] = []
    for channel, channel_rows in grouped_rows.items():
        ordered_rows = sorted(channel_rows, key=lambda row: str(row.get("timestamp", "")))
        numeric_rows: list[dict[str, Any]] = []
        values: list[float] = []
        for row in ordered_rows:
            try:
                numeric_rows.append(row)
                values.append(float(row["value"]))
            except (KeyError, TypeError, ValueError):
                continue
        if not values:
            continue
        center, mad = (baselines or {}).get(channel, _baseline(values))
        point_scores: list[float] = []
        for index, (row, value) in enumerate(zip(numeric_rows, values)):
            history = values[max(0, index - window_size):index]
            rolling_center, rolling_mad = _baseline(history) if len(history) >= 3 else (center, mad)
            deviation = abs(value - rolling_center) / (1.4826 * rolling_mad)
            point_score = min(1.0, deviation / 8.0)
            point_scores.append(point_score)
            if point_score >= 0.65:
                high_rows.append(row)
        channel_scores[channel] = max(point_scores, default=0.0)
        evidence.append(f"{channel}: robust deviation score {channel_scores[channel]:.3f}")
    if not channel_scores:
        return 0.0, [], None, evidence
    score = max(channel_scores.values())
    affected = sorted(channel for channel, value in channel_scores.items() if value >= 0.65)
    if not affected and score >= 0.5:
        affected = [max(channel_scores, key=channel_scores.get)]
    window = None
    if high_rows:
        timestamps = [str(row.get("timestamp")) for row in high_rows]
        window = {"start": min(timestamps), "end": max(timestamps), "channels": affected}
    return score, affected, window, evidence
