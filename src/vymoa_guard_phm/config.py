"""Runtime configuration with explicit, versioned thresholds."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class AssessmentConfig:
    orbit_monitor_threshold: float = 0.50
    orbit_review_threshold: float = 0.65
    orbit_red_threshold: float = 0.85
    telemetry_anomaly_threshold: float = 0.65
    freshness_limit_minutes: float = 60.0
    policy_version: str = "policy-0.1.0"
    orbit_model_version: str = "orbit-regression-ranking-baseline-0.1.0"
    telemetry_model_version: str = "telemetry-robust-iforest-0.1.0"
    random_seed: int = 42
    required_telemetry: bool = True
    required_channels: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "AssessmentConfig":
        values = asdict(cls())
        values.update(payload)
        return cls(**values)
