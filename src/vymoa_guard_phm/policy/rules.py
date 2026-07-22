"""Pure, auditable policy rules; no model-probability fusion or commands."""

from __future__ import annotations

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import DecisionAssessment, OrbitAssessment, TelemetryAssessment, ValidationFinding
from vymoa_guard_phm.data.validator import has_failure


def _trace(rule_id: str, result: bool, evidence: str) -> dict[str, object]:
    return {"rule_id": rule_id, "result": result, "evidence": evidence}


def evaluate_policy(orbit: OrbitAssessment, telemetry: TelemetryAssessment, findings: list[ValidationFinding], config: AssessmentConfig) -> DecisionAssessment:
    trace: list[dict[str, object]] = []
    reasons: list[str] = []
    if has_failure(findings):
        trace.append(_trace("POL-001", True, "At least one input-quality gate failed."))
        reasons.append("DATA_QUALITY_FAILURE")
        return DecisionAssessment("INSUFFICIENT_DATA", "REQUEST_DATA", reasons, trace, True, config.policy_version)
    trace.append(_trace("POL-001", False, "Input-quality gates passed."))
    if orbit.status != "SCORED" or telemetry.status != "SCORED":
        trace.append(_trace("POL-002", True, "A required assessment is unavailable."))
        reasons.append("MODEL_UNAVAILABLE")
        return DecisionAssessment("INSUFFICIENT_DATA", "REQUEST_DATA", reasons, trace, True, config.policy_version)
    orbit_score = float(orbit.score or 0.0)
    telemetry_score = float(telemetry.score or 0.0)
    orbit_red = orbit_score >= config.orbit_red_threshold
    orbit_review = orbit_score >= config.orbit_review_threshold
    telemetry_high = telemetry_score >= config.telemetry_anomaly_threshold
    trace.append(_trace("POL-003", orbit_red, f"Orbit score {orbit_score:.3f} >= red threshold {config.orbit_red_threshold:.3f}."))
    trace.append(_trace("POL-004", telemetry_high, f"Telemetry score {telemetry_score:.3f} >= anomaly threshold {config.telemetry_anomaly_threshold:.3f}."))
    if orbit_red and telemetry_high:
        reasons.extend(["ORBIT_HIGH_RISK", "TELEMETRY_ANOMALY_HIGH", "COMPOUND_EVIDENCE"])
        return DecisionAssessment("RED", "MISSION_CRITICAL_REVIEW", reasons, trace, False, config.policy_version)
    if orbit_red:
        reasons.append("ORBIT_HIGH_RISK")
        return DecisionAssessment("RED", "CONJUNCTION_REVIEW", reasons, trace, False, config.policy_version)
    if telemetry_high:
        reasons.extend(["TELEMETRY_ANOMALY_HIGH", "TELEMETRY_CHANNEL_AFFECTED"])
        return DecisionAssessment("AMBER", "SUBSYSTEM_INVESTIGATION", reasons, trace, False, config.policy_version)
    if orbit_review:
        reasons.append("ORBIT_BORDERLINE")
        return DecisionAssessment("AMBER", "MONITOR", reasons, trace, False, config.policy_version)
    reasons.append("NO_REVIEW_TRIGGER")
    return DecisionAssessment("GREEN", "NO_ALERT", reasons, trace, False, config.policy_version)

