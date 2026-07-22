"""Pure, auditable policy rules; no model-probability fusion or commands."""

from __future__ import annotations

from math import isfinite

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import DecisionAssessment, OrbitAssessment, TelemetryAssessment, ValidationFinding
from vymoa_guard_phm.data.validator import has_failure


def _trace(rule_id: str, result: bool, evidence: str) -> dict[str, object]:
    return {"rule_id": rule_id, "result": result, "evidence": evidence}


def _finish(
    status: str,
    review_action: str,
    reasons: list[str],
    trace: list[dict[str, object]],
    abstained: bool,
    config: AssessmentConfig,
    evidence: str,
) -> DecisionAssessment:
    trace.append(_trace("POL-100", True, evidence))
    return DecisionAssessment(status, review_action, list(dict.fromkeys(reasons)), trace, abstained, config.policy_version)  # type: ignore[arg-type]


def _configuration_is_valid(config: AssessmentConfig) -> bool:
    thresholds = (
        config.orbit_monitor_threshold,
        config.orbit_review_threshold,
        config.orbit_red_threshold,
        config.telemetry_anomaly_threshold,
    )
    return (
        all(isfinite(float(value)) and 0.0 <= float(value) <= 1.0 for value in thresholds)
        and config.orbit_monitor_threshold <= config.orbit_review_threshold <= config.orbit_red_threshold
    )


def _score_issue(assessment: OrbitAssessment | TelemetryAssessment, expected_score_type: str) -> str | None:
    if assessment.status != "SCORED":
        return "MODEL_UNAVAILABLE"
    if assessment.score_type != expected_score_type:
        return "MODEL_SCORE_SEMANTICS_INVALID"
    if assessment.score is None:
        return "MODEL_SCORE_MISSING"
    try:
        score = float(assessment.score)
    except (TypeError, ValueError):
        return "MODEL_SCORE_INVALID"
    if not isfinite(score) or not 0.0 <= score <= 1.0:
        return "MODEL_SCORE_OUT_OF_RANGE"
    return None


def _telemetry_evidence_is_present(telemetry: TelemetryAssessment) -> bool:
    window = telemetry.anomaly_window or {}
    channels = window.get("channels")
    return bool(telemetry.affected_channels and window.get("start") and window.get("end") and channels)


def evaluate_policy(
    orbit: OrbitAssessment,
    telemetry: TelemetryAssessment,
    findings: list[ValidationFinding],
    config: AssessmentConfig,
) -> DecisionAssessment:
    trace: list[dict[str, object]] = []
    reasons: list[str] = []
    if has_failure(findings):
        trace.append(_trace("POL-001", True, "At least one input-quality gate failed."))
        reasons.append("DATA_QUALITY_FAILURE")
        return _finish("INSUFFICIENT_DATA", "REQUEST_DATA", reasons, trace, True, config, "Policy abstained because input quality has precedence.")
    trace.append(_trace("POL-001", False, "Input-quality gates passed."))

    if not _configuration_is_valid(config):
        trace.append(_trace("POL-002", True, "Policy thresholds are non-finite, out of range, or incorrectly ordered."))
        return _finish("INSUFFICIENT_DATA", "REQUEST_DATA", ["POLICY_CONFIGURATION_INVALID"], trace, True, config, "Policy abstained because its versioned configuration is invalid.")
    trace.append(_trace("POL-002", False, "Versioned policy thresholds are finite, bounded, and ordered."))

    orbit_issue = _score_issue(orbit, "ranking_score")
    if orbit_issue:
        trace.append(_trace("POL-003", True, f"Orbit assessment rejected: {orbit_issue}."))
        return _finish("INSUFFICIENT_DATA", "REQUEST_DATA", [orbit_issue], trace, True, config, "Policy abstained because orbit evidence is unavailable or semantically invalid.")
    trace.append(_trace("POL-003", False, "Orbit ranking score is present, finite, and bounded."))
    orbit_score = float(orbit.score)

    telemetry_score: float | None = None
    telemetry_available = telemetry.status == "SCORED"
    if not telemetry_available and config.required_telemetry:
        trace.append(_trace("POL-004", True, "Required telemetry assessment is unavailable."))
        return _finish("INSUFFICIENT_DATA", "REQUEST_DATA", ["MODEL_UNAVAILABLE"], trace, True, config, "Policy abstained because required telemetry evidence is unavailable.")
    if not telemetry_available:
        trace.append(_trace("POL-004", False, "Telemetry assessment is unavailable but configured as optional."))
        reasons.append("TELEMETRY_UNAVAILABLE_OPTIONAL")
    else:
        telemetry_issue = _score_issue(telemetry, "anomaly_score")
        if telemetry_issue:
            trace.append(_trace("POL-004", True, f"Telemetry assessment rejected: {telemetry_issue}."))
            return _finish("INSUFFICIENT_DATA", "REQUEST_DATA", [telemetry_issue], trace, True, config, "Policy abstained because telemetry evidence is unavailable or semantically invalid.")
        telemetry_score = float(telemetry.score)
        trace.append(_trace("POL-004", False, "Telemetry anomaly score is present, finite, and bounded."))

    orbit_red = orbit_score >= config.orbit_red_threshold
    orbit_review = orbit_score >= config.orbit_review_threshold
    telemetry_high = telemetry_score is not None and telemetry_score >= config.telemetry_anomaly_threshold
    trace.append(_trace("POL-005", orbit_red, f"Orbit score {orbit_score:.3f} >= red threshold {config.orbit_red_threshold:.3f}."))
    trace.append(_trace("POL-006", telemetry_high, f"Telemetry score {telemetry_score if telemetry_score is not None else 0.0:.3f} >= anomaly threshold {config.telemetry_anomaly_threshold:.3f}."))

    if telemetry_high and not _telemetry_evidence_is_present(telemetry):
        trace.append(_trace("POL-007", True, "High telemetry score has no affected-channel and anomaly-window evidence."))
        return _finish("INSUFFICIENT_DATA", "REQUEST_DATA", ["TELEMETRY_EVIDENCE_MISSING"], trace, True, config, "Policy abstained rather than emitting a high-severity telemetry state without evidence.")
    trace.append(_trace("POL-007", False, "Telemetry evidence is sufficient for the configured score state."))

    expected_class = "REVIEW" if orbit_red else "MONITOR" if orbit_review else "SAFE"
    model_disagreement = str(orbit.risk_class).upper() != expected_class
    trace.append(_trace("POL-008", model_disagreement, f"Orbit risk class {orbit.risk_class!r} agrees with score-derived class {expected_class!r}: {not model_disagreement}."))
    if model_disagreement:
        reasons.append("MODEL_DISAGREEMENT")

    compound = orbit_red and telemetry_high
    trace.append(_trace("POL-009", compound, "Both orbit and telemetry thresholds are crossed."))
    if model_disagreement:
        if orbit_red:
            reasons.append("ORBIT_HIGH_RISK")
        if telemetry_high:
            reasons.extend(["TELEMETRY_ANOMALY_HIGH", "TELEMETRY_CHANNEL_AFFECTED"])
        return _finish("AMBER", "MONITOR", reasons, trace, False, config, "Model evidence disagrees; conservative monitoring takes precedence over severity thresholds.")
    if orbit_red and telemetry_high:
        reasons.extend(["ORBIT_HIGH_RISK", "TELEMETRY_ANOMALY_HIGH", "COMPOUND_EVIDENCE"])
        return _finish("RED", "MISSION_CRITICAL_REVIEW", reasons, trace, False, config, "Compound evidence requires mission-critical human review.")
    if orbit_red:
        reasons.append("ORBIT_HIGH_RISK")
        return _finish("RED", "CONJUNCTION_REVIEW", reasons, trace, False, config, "High orbit ranking score requires conjunction review.")
    if telemetry_high:
        reasons.extend(["TELEMETRY_ANOMALY_HIGH", "TELEMETRY_CHANNEL_AFFECTED"])
        return _finish("AMBER", "SUBSYSTEM_INVESTIGATION", reasons, trace, False, config, "High telemetry anomaly score with channel/window evidence requires subsystem investigation.")
    if orbit_review:
        reasons.append("ORBIT_BORDERLINE")
        return _finish("AMBER", "MONITOR", reasons, trace, False, config, "Borderline orbit ranking score requires monitoring.")
    if not telemetry_available:
        return _finish("AMBER", "MONITOR", reasons, trace, False, config, "Optional telemetry is unavailable; monitoring is required and GREEN is not permitted.")
    reasons.append("NO_REVIEW_TRIGGER")
    return _finish("GREEN", "NO_ALERT", reasons, trace, False, config, "No configured review trigger was crossed and required evidence is present.")
