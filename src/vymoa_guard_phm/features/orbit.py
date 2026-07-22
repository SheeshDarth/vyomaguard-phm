"""Dataset-agnostic numeric CDM feature extraction."""

from __future__ import annotations

from typing import Any


def numeric_features(event: dict[str, Any]) -> dict[str, float]:
    features = event.get("features")
    if features is None:
        excluded = {"event_id", "mission_id", "risk", "label", "source_row_index"}
        features = {key: value for key, value in event.items() if key not in excluded}
    output: dict[str, float] = {}
    for key, value in features.items():
        try:
            output[str(key)] = float(value)
        except (TypeError, ValueError):
            continue
    return dict(sorted(output.items()))


def feature_vector(event: dict[str, Any], feature_names: list[str] | None = None) -> tuple[list[str], list[float]]:
    values = numeric_features(event)
    names = feature_names or list(values)
    return names, [values.get(name, 0.0) for name in names]
