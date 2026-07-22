"""Telemetry anomaly baseline using robust statistics and optional Isolation Forest."""

from __future__ import annotations

from typing import Any

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import TelemetryAssessment
from vymoa_guard_phm.features.telemetry import robust_channel_scores

try:
    from sklearn.ensemble import IsolationForest
except ImportError:  # pragma: no cover - robust statistics remain available.
    IsolationForest = None  # type: ignore[assignment,misc]


class TelemetryAnomalyEngine:
    def __init__(self, config: AssessmentConfig | None = None) -> None:
        self.config = config or AssessmentConfig()
        self.model_version = self.config.telemetry_model_version
        self.model = None

    def fit(self, rows: list[dict[str, Any]]) -> "TelemetryAnomalyEngine":
        if IsolationForest is None or len(rows) < 8:
            return self
        values = []
        for row in rows:
            try:
                values.append([float(row["value"])])
            except (KeyError, TypeError, ValueError):
                continue
        if len(values) >= 8:
            self.model = IsolationForest(random_state=self.config.random_seed, contamination="auto", n_estimators=100)
            self.model.fit(values)
        return self

    def score(self, rows: list[dict[str, Any]]) -> TelemetryAssessment:
        if not rows:
            return TelemetryAssessment("INSUFFICIENT_DATA", "anomaly_score", None, model_version=self.model_version, threshold_version=self.config.policy_version)
        score, affected, window, evidence = robust_channel_scores(rows)
        if self.model is not None:
            values = [[float(row["value"])] for row in rows]
            raw = -self.model.decision_function(values)
            span = float(raw.max() - raw.min()) if len(raw) else 0.0
            model_score = float((raw.max() - raw.min()) / span) if span > 0 else 0.0
            score = max(score, min(1.0, model_score))
            evidence.append("Isolation Forest comparison path evaluated; robust statistics remain the primary evidence.")
        return TelemetryAssessment("SCORED", "anomaly_score", round(score, 6), affected, window, self.model_version, self.config.policy_version, evidence)
