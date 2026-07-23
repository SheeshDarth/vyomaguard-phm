"""Stable data contracts shared by validation, models, policy, UI, and reports."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from hmac import compare_digest
from collections.abc import Mapping
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
    shape_errors: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: object) -> "InputWindow":
        shape_errors: list[str] = []
        if not isinstance(payload, Mapping):
            return cls("unknown", {}, [], {}, ["input must be an object"])

        orbit_value = payload.get("orbit_event")
        if orbit_value is None:
            orbit_event: dict[str, Any] = {}
        elif isinstance(orbit_value, Mapping):
            orbit_event = dict(orbit_value)
        else:
            shape_errors.append("orbit_event must be an object")
            orbit_event = {}

        telemetry_value = payload.get("telemetry")
        if telemetry_value is None:
            telemetry: list[dict[str, Any]] = []
        elif isinstance(telemetry_value, list):
            telemetry = []
            for index, row in enumerate(telemetry_value):
                if isinstance(row, Mapping):
                    telemetry.append(dict(row))
                else:
                    shape_errors.append(f"telemetry[{index}] must be an object")
        else:
            shape_errors.append("telemetry must be an array")
            telemetry = []

        metadata_value = payload.get("metadata")
        if metadata_value is None:
            metadata: dict[str, Any] = {}
        elif isinstance(metadata_value, Mapping):
            metadata = dict(metadata_value)
        else:
            shape_errors.append("metadata must be an object")
            metadata = {}

        return cls(
            scenario_id=str(payload.get("scenario_id", "unknown")),
            orbit_event=orbit_event,
            telemetry=telemetry,
            metadata=metadata,
            shape_errors=shape_errors,
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
