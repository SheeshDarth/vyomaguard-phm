"""Transparent orbit-risk baseline with optional sklearn fitting."""

from __future__ import annotations

import math
from typing import Any

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import OrbitAssessment
from vymoa_guard_phm.features.orbit import feature_vector, numeric_features

try:
    from sklearn.linear_model import LogisticRegression
except ImportError:  # pragma: no cover - the heuristic path remains usable.
    LogisticRegression = None  # type: ignore[assignment,misc]


class OrbitRiskEngine:
    def __init__(self, config: AssessmentConfig | None = None) -> None:
        self.config = config or AssessmentConfig()
        self.model: Any = None
        self.feature_names: list[str] = []
        self.fitted = False

    def fit(self, rows: list[dict[str, Any]]) -> "OrbitRiskEngine":
        if LogisticRegression is None or len(rows) < 4:
            return self
        labels = [int(row["label"]) for row in rows if "label" in row]
        if len(labels) != len(rows) or len(set(labels)) < 2:
            return self
        all_names = sorted({name for row in rows for name in numeric_features(row.get("event", row)).keys()})
        if not all_names:
            return self
        matrix = [feature_vector(row.get("event", row), all_names)[1] for row in rows]
        model = LogisticRegression(random_state=self.config.random_seed, max_iter=500)
        model.fit(matrix, labels)
        self.model = model
        self.feature_names = all_names
        self.fitted = True
        return self

    def _heuristic_score(self, event: dict[str, Any]) -> float:
        if event.get("risk_score_hint") is not None:
            return max(0.0, min(1.0, float(event["risk_score_hint"])))
        values = numeric_features(event)
        if not values:
            return 0.0
        # A deterministic fallback for fixtures before a dataset-trained model exists.
        return max(0.0, min(1.0, sum(abs(value) for value in values.values()) / (len(values) * 10.0)))

    def score(self, event: dict[str, Any]) -> OrbitAssessment:
        if not event:
            return OrbitAssessment("INSUFFICIENT_DATA", "ranking_score", None, "INSUFFICIENT_DATA", self.config.orbit_model_version, self.config.policy_version)
        if self.fitted:
            _, vector = feature_vector(event, self.feature_names)
            score = float(self.model.predict_proba([vector])[0][1])
            coefficients = self.model.coef_[0]
            contributions = [(name, coefficient * value, value) for name, coefficient, value in zip(self.feature_names, coefficients, vector)]
            contributions.sort(key=lambda item: abs(item[1]), reverse=True)
            top_features = [{"name": name, "value": value, "attribution": contribution, "direction": "raises" if contribution >= 0 else "lowers"} for name, contribution, value in contributions[:5]]
            score_type = "ranking_score"
        else:
            score = self._heuristic_score(event)
            values = numeric_features(event)
            top_features = [{"name": name, "value": value, "attribution": value, "direction": "raises" if value >= 0 else "lowers"} for name, value in sorted(values.items(), key=lambda item: abs(item[1]), reverse=True)[:5]]
            score_type = "ranking_score"
        if score >= self.config.orbit_red_threshold:
            risk_class = "REVIEW"
        elif score >= self.config.orbit_monitor_threshold:
            risk_class = "MONITOR"
        else:
            risk_class = "SAFE"
        return OrbitAssessment("SCORED", score_type, round(score, 6), risk_class, self.config.orbit_model_version, self.config.policy_version, top_features, ["Feature attribution describes model evidence; it is not causal explanation."])

