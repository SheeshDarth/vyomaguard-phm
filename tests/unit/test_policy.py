from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import OrbitAssessment, TelemetryAssessment, ValidationFinding
from vymoa_guard_phm.policy.rules import evaluate_policy


def _orbit(score: float, risk_class: str | None = None) -> OrbitAssessment:
    if risk_class is None:
        risk_class = "REVIEW" if score >= 0.85 else "MONITOR" if score >= 0.65 else "LOW_RANKING"
    return OrbitAssessment("SCORED", "ranking_score", score, risk_class, "orbit", "policy")


def _telemetry(score: float, *, evidence: bool = True) -> TelemetryAssessment:
    if not evidence:
        return TelemetryAssessment("SCORED", "anomaly_score", score)
    return TelemetryAssessment(
        "SCORED",
        "anomaly_score",
        score,
        ["power_bus"],
        {"start": "2026-01-01T00:00:00Z", "end": "2026-01-01T00:01:00Z", "channels": ["power_bus"]},
    )


def test_high_orbit_and_telemetry_produce_red_compound_review():
    result = evaluate_policy(_orbit(0.9), _telemetry(0.9), [ValidationFinding("PASS", "OK", "info", "ok")], AssessmentConfig())
    assert result.status == "RED"
    assert result.review_action == "MISSION_CRITICAL_REVIEW"
    assert "COMPOUND_EVIDENCE" in result.reason_codes


def test_failed_quality_gate_abstains():
    result = evaluate_policy(_orbit(0.1), _telemetry(0.1), [ValidationFinding("FAIL", "BAD", "error", "bad")], AssessmentConfig())
    assert result.status == "INSUFFICIENT_DATA"
    assert result.abstained is True


def test_high_telemetry_without_channel_window_evidence_abstains():
    result = evaluate_policy(_orbit(0.1), _telemetry(0.9, evidence=False), [ValidationFinding("PASS", "OK", "info", "ok")], AssessmentConfig())
    assert result.status == "INSUFFICIENT_DATA"
    assert "TELEMETRY_EVIDENCE_MISSING" in result.reason_codes
    assert result.rule_trace[-1]["rule_id"] == "POL-100"


def test_optional_telemetry_does_not_block_high_orbit_review():
    result = evaluate_policy(
        _orbit(0.9),
        TelemetryAssessment("INSUFFICIENT_DATA", "anomaly_score", None),
        [ValidationFinding("PASS", "OK", "info", "ok")],
        AssessmentConfig(required_telemetry=False),
    )
    assert result.status == "RED"
    assert result.review_action == "CONJUNCTION_REVIEW"
    assert "TELEMETRY_UNAVAILABLE_OPTIONAL" in result.reason_codes


def test_optional_telemetry_unavailable_cannot_be_green():
    result = evaluate_policy(
        _orbit(0.1),
        TelemetryAssessment("INSUFFICIENT_DATA", "anomaly_score", None),
        [ValidationFinding("PASS", "OK", "info", "ok")],
        AssessmentConfig(required_telemetry=False),
    )
    assert result.status == "AMBER"
    assert result.review_action == "MONITOR"
    assert "TELEMETRY_UNAVAILABLE_OPTIONAL" in result.reason_codes


def test_non_finite_orbit_score_abstains_instead_of_becoming_green():
    result = evaluate_policy(_orbit(float("nan")), _telemetry(0.1), [ValidationFinding("PASS", "OK", "info", "ok")], AssessmentConfig())
    assert result.status == "INSUFFICIENT_DATA"
    assert "MODEL_SCORE_OUT_OF_RANGE" in result.reason_codes


def test_score_class_disagreement_requires_monitoring():
    result = evaluate_policy(_orbit(0.2, "REVIEW"), _telemetry(0.1), [ValidationFinding("PASS", "OK", "info", "ok")], AssessmentConfig())
    assert result.status == "AMBER"
    assert result.review_action == "MONITOR"
    assert "MODEL_DISAGREEMENT" in result.reason_codes


def test_score_class_disagreement_overrides_red_threshold():
    result = evaluate_policy(_orbit(0.95, "LOW_RANKING"), _telemetry(0.1), [ValidationFinding("PASS", "OK", "info", "ok")], AssessmentConfig())
    assert result.status == "AMBER"
    assert result.review_action == "MONITOR"
    assert result.rule_trace[-1]["rule_id"] == "POL-100"


def test_invalid_threshold_configuration_abstains():
    result = evaluate_policy(
        _orbit(0.2),
        _telemetry(0.1),
        [ValidationFinding("PASS", "OK", "info", "ok")],
        AssessmentConfig(orbit_review_threshold=0.9, orbit_red_threshold=0.8),
    )
    assert result.status == "INSUFFICIENT_DATA"
    assert "POLICY_CONFIGURATION_INVALID" in result.reason_codes
