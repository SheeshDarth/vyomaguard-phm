"""Transparent continuous orbit-risk regression/ranking baseline."""

from __future__ import annotations

from typing import Any

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import OrbitAssessment
from vymoa_guard_phm.features.orbit import feature_vector, numeric_features
from vymoa_guard_phm.data.orbit_target import select_final_cdm_rows

try:
    from sklearn.linear_model import Ridge
except ImportError:  # pragma: no cover - the heuristic path remains usable.
    Ridge = None  # type: ignore[assignment,misc]


class OrbitRiskEngine:
    def __init__(self, config: AssessmentConfig | None = None) -> None:
        self.config = config or AssessmentConfig()
        self.model: Any = None
        self.feature_names: list[str] = []
        self.fitted = False
        self.target_min: float | None = None
        self.target_max: float | None = None

    def fit(self, rows: list[dict[str, Any]]) -> "OrbitRiskEngine":
        if Ridge is None or len(rows) < 4:
            return self
        source_rows = list(rows)
        if any("event_id" in row for row in source_rows):
            source_rows = [item.row for item in select_final_cdm_rows(source_rows)]
        labeled_rows: list[tuple[dict[str, Any], float]] = []
        for row in source_rows:
            try:
                target = float(row["risk"])
            except (KeyError, TypeError, ValueError):
                continue
            if not (-float("inf") < target < float("inf")):
                continue
            labeled_rows.append((dict(row.get("event", row)), target))
        if len(labeled_rows) < 4 or len({target for _, target in labeled_rows}) < 2:
            return self
        all_names = sorted({name for event, _ in labeled_rows for name in numeric_features(event).keys()})
        if not all_names:
            return self
        matrix = [feature_vector(event, all_names)[1] for event, _ in labeled_rows]
        targets = [target for _, target in labeled_rows]
        model = Ridge(alpha=1.0)
        model.fit(matrix, targets)
        self.model = model
        self.feature_names = all_names
        self.target_min = min(targets)
        self.target_max = max(targets)
        self.fitted = True
        return self

    def _ranking_score(self, raw_value: float) -> float:
        if self.target_min is None or self.target_max is None or self.target_max == self.target_min:
            return 0.5
        normalized = (raw_value - self.target_min) / (self.target_max - self.target_min)
        return max(0.0, min(1.0, normalized))

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
        raw_value: float | None = None
        if self.fitted:
            _, vector = feature_vector(event, self.feature_names)
            raw_value = float(self.model.predict([vector])[0])
            score = self._ranking_score(raw_value)
            coefficients = self.model.coef_
            contributions = [(name, coefficient * value, value) for name, coefficient, value in zip(self.feature_names, coefficients, vector)]
            contributions.sort(key=lambda item: abs(item[1]), reverse=True)
            top_features = [{"name": name, "value": value, "attribution": contribution, "direction": "raises" if contribution >= 0 else "lowers"} for name, contribution, value in contributions[:5]]
            evidence = ["Regression output is normalized to a ranking score using the training-target range.", "The raw target is source-defined base-10 log risk, not a collision probability."]
        else:
            score = self._heuristic_score(event)
            values = numeric_features(event)
            top_features = [{"name": name, "value": value, "attribution": value, "direction": "raises" if value >= 0 else "lowers"} for name, value in sorted(values.items(), key=lambda item: abs(item[1]), reverse=True)[:5]]
            evidence = ["Heuristic output is a fixture-only ranking score; no probability claim is permitted."]
        if score >= self.config.orbit_red_threshold:
            risk_class = "REVIEW"
        elif score >= self.config.orbit_monitor_threshold:
            risk_class = "MONITOR"
        else:
            risk_class = "SAFE"
        return OrbitAssessment("SCORED", "ranking_score", round(score, 6), risk_class, self.config.orbit_model_version, self.config.policy_version, top_features, evidence + ["Feature attribution describes model evidence; it is not causal explanation."], raw_value, "base10_log_risk" if raw_value is not None else None)
