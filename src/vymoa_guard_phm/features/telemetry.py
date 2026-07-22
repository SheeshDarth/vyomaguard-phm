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


def robust_channel_scores(rows: list[dict[str, Any]]) -> tuple[float, list[str], dict[str, Any] | None, list[str]]:
    grouped = grouped_values(rows)
    if not grouped:
        return 0.0, [], None, []
    channel_scores: dict[str, float] = {}
    evidence: list[str] = []
    for channel, values in grouped.items():
        center = median(values)
        deviations = [abs(value - center) for value in values]
        mad = median(deviations) or 1e-6
        z = max(abs(value - center) / (1.4826 * mad) for value in values)
        channel_scores[channel] = min(1.0, z / 8.0)
        evidence.append(f"{channel}: robust deviation score {channel_scores[channel]:.3f}")
    score = max(channel_scores.values())
    affected = sorted(channel for channel, value in channel_scores.items() if value >= 0.65)
    if not affected and score >= 0.5:
        affected = [max(channel_scores, key=channel_scores.get)]
    window = None
    if affected:
        affected_rows = [row for row in rows if str(row.get("channel")) in affected]
        timestamps = [str(row.get("timestamp")) for row in affected_rows]
        window = {"start": min(timestamps), "end": max(timestamps), "channels": affected}
    return score, affected, window, evidence

