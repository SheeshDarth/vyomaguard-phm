"""Telemetry anomaly baseline using robust statistics and optional Isolation Forest."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import TelemetryAssessment
from vymoa_guard_phm.features.telemetry import _baseline, robust_channel_scores

try:
    from sklearn.ensemble import IsolationForest
except ImportError:  # pragma: no cover - robust statistics remain available.
    IsolationForest = None  # type: ignore[assignment,misc]


class TelemetryAnomalyEngine:
    def __init__(self, config: AssessmentConfig | None = None) -> None:
        self.config = config or AssessmentConfig()
        self.model_version = self.config.telemetry_model_version
        self.models: dict[str, Any] = {}
        self.model_bounds: dict[str, tuple[float, float]] = {}
        self.baselines: dict[str, tuple[float, float]] = {}
        self.fitted = False

    @staticmethod
    def _is_nominal(row: dict[str, Any]) -> bool:
        raw_label = row.get("anomaly")
        if raw_label is None:
            return True
        try:
            return float(raw_label) == 0.0
        except (TypeError, ValueError):
            return str(raw_label).strip().lower() in {"false", "nominal", "normal", "0"}

    def fit(self, rows: list[dict[str, Any]]) -> "TelemetryAnomalyEngine":
        self.models = {}
        self.model_bounds = {}
        nominal_rows = [row for row in rows if self._is_nominal(row)]
        grouped: dict[str, list[float]] = defaultdict(list)
        for row in nominal_rows:
            try:
                grouped[str(row["channel"])].append(float(row["value"]))
            except (KeyError, TypeError, ValueError):
                continue
        self.baselines = {channel: _baseline(values) for channel, values in grouped.items() if values}
        if IsolationForest is None:
            self.fitted = bool(self.baselines)
            return self
        for channel, values in grouped.items():
            if len(values) < 8:
                continue
            model = IsolationForest(
                random_state=self.config.random_seed,
                contamination="auto",
                n_estimators=self.config.telemetry_iforest_estimators,
                n_jobs=1,
            )
            model.fit(np.asarray(values, dtype=float).reshape(-1, 1))
            raw_nominal = -model.decision_function(np.asarray(values, dtype=float).reshape(-1, 1))
            lower, upper = (float(value) for value in np.percentile(raw_nominal, [5.0, 95.0]))
            self.models[channel] = model
            self.model_bounds[channel] = (lower, max(upper, lower + 1e-6))
        self.fitted = bool(self.baselines)
        return self

    def score(self, rows: list[dict[str, Any]], *, use_iforest: bool | None = None) -> TelemetryAssessment:
        if not rows:
            return TelemetryAssessment("INSUFFICIENT_DATA", "anomaly_score", None, model_version=self.model_version, threshold_version=self.config.policy_version)
        iforest_is_primary = self.config.telemetry_iforest_primary if use_iforest is None else use_iforest
        score, affected, window, evidence = robust_channel_scores(
            rows,
            baselines=self.baselines or None,
            window_size=self.config.telemetry_rolling_window,
        )
        model_channel_scores: dict[str, float] = {}
        model_high_rows: list[dict[str, Any]] = []
        for channel, model in self.models.items():
            channel_rows = [row for row in rows if str(row.get("channel")) == channel]
            numeric_rows: list[dict[str, Any]] = []
            values: list[float] = []
            for row in channel_rows:
                try:
                    numeric_rows.append(row)
                    values.append(float(row["value"]))
                except (KeyError, TypeError, ValueError):
                    continue
            if not values:
                continue
            raw_scores = -model.decision_function(np.asarray(values, dtype=float).reshape(-1, 1))
            lower, upper = self.model_bounds[channel]
            normalized = np.clip((raw_scores - lower) / (upper - lower), 0.0, 1.0)
            channel_score = float(np.max(normalized))
            model_channel_scores[channel] = channel_score
            model_high_rows.extend(row for row, value in zip(numeric_rows, normalized) if value >= self.config.telemetry_anomaly_threshold)
            evidence.append(f"{channel}: Isolation Forest anomaly score {channel_score:.3f}")
        if model_channel_scores:
            model_affected = {channel for channel, value in model_channel_scores.items() if value >= self.config.telemetry_anomaly_threshold}
            if iforest_is_primary:
                score = max(score, max(model_channel_scores.values()))
                affected = sorted(set(affected) | model_affected)
                evidence.append("Isolation Forest was included in the anomaly score because the caller explicitly selected it as primary.")
            else:
                evidence.append("Isolation Forest was evaluated as a comparison only and was not fused into the canonical score.")
            evidence.append("Isolation Forest output remains an anomaly score, not a failure probability.")
        if window is None and (model_high_rows if iforest_is_primary else affected):
            window_rows = (model_high_rows if iforest_is_primary else []) or [row for row in rows if str(row.get("channel")) in affected]
            timestamps = [str(row.get("timestamp")) for row in window_rows]
            if timestamps:
                window = {"start": min(timestamps), "end": max(timestamps), "channels": affected}
        evidence.append("Telemetry output is an anomaly score, not a failure probability.")
        return TelemetryAssessment("SCORED", "anomaly_score", round(float(score), 6), affected, window, self.model_version, self.config.policy_version, evidence)
