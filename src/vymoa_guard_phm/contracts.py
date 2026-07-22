"""Stable data contracts shared by validation, models, policy, UI, and reports."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from hmac import compare_digest
from typing import Any, Literal

ValidationStatus = Literal["PASS", "WARN", "FAIL"]
AssessmentStatus = Literal["SCORED", "INSUFFICIENT_DATA"]
TriageStatus = Literal["GREEN", "AMBER", "RED", "INSUFFICIENT_DATA"]


@dataclass
class ValidationFinding:
    status: ValidationStatus
    code: str
    severity: Literal["info", "warning", "error"]
    message: str
    field: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InputWindow:
    scenario_id: str
    orbit_event: dict[str, Any]
    telemetry: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "InputWindow":
        return cls(
            scenario_id=str(payload.get("scenario_id", "unknown")),
            orbit_event=dict(payload.get("orbit_event") or {}),
            telemetry=list(payload.get("telemetry") or []),
            metadata=dict(payload.get("metadata") or {}),
        )


@dataclass
class OrbitAssessment:
    status: AssessmentStatus
    score_type: str
    score: float | None
    risk_class: str
    model_version: str
    threshold_version: str
    top_features: list[dict[str, Any]] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    raw_value: float | None = None
    raw_value_unit: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TelemetryAssessment:
    status: AssessmentStatus
    score_type: str
    score: float | None
    affected_channels: list[str] = field(default_factory=list)
    anomaly_window: dict[str, Any] | None = None
    model_version: str = "telemetry-baseline-0.1.0"
    threshold_version: str = "policy-0.1.0"
    evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DecisionAssessment:
    status: TriageStatus
    review_action: str
    reason_codes: list[str] = field(default_factory=list)
    rule_trace: list[dict[str, Any]] = field(default_factory=list)
    abstained: bool = False
    policy_version: str = "policy-0.1.0"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MissionAssessment:
    run_id: str
    scenario_id: str
    created_at: str
    input_manifest: dict[str, Any]
    quality_findings: list[ValidationFinding]
    orbit: OrbitAssessment
    telemetry: TelemetryAssessment
    decision: DecisionAssessment
    versions: dict[str, str]
    limitations: list[str] = field(default_factory=list)
    evidence_schema_version: str = "evidence-0.1.0"
    evidence_hash: str = ""

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["quality_findings"] = [finding.to_dict() for finding in self.quality_findings]
        return payload

    def compute_evidence_hash(self) -> str:
        payload = self.to_dict()
        payload["evidence_hash"] = ""
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def verify_evidence_hash(self) -> bool:
        return bool(self.evidence_hash) and compare_digest(self.evidence_hash, self.compute_evidence_hash())
