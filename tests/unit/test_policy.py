from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import OrbitAssessment, TelemetryAssessment, ValidationFinding
from vymoa_guard_phm.policy.rules import evaluate_policy


def _orbit(score: float) -> OrbitAssessment:
    return OrbitAssessment("SCORED", "ranking_score", score, "REVIEW", "orbit", "policy")


def _telemetry(score: float) -> TelemetryAssessment:
    return TelemetryAssessment("SCORED", "anomaly_score", score)


def test_high_orbit_and_telemetry_produce_red_compound_review():
    result = evaluate_policy(_orbit(0.9), _telemetry(0.9), [ValidationFinding("PASS", "OK", "info", "ok")], AssessmentConfig())
    assert result.status == "RED"
    assert result.review_action == "MISSION_CRITICAL_REVIEW"
    assert "COMPOUND_EVIDENCE" in result.reason_codes


def test_failed_quality_gate_abstains():
    result = evaluate_policy(_orbit(0.1), _telemetry(0.1), [ValidationFinding("FAIL", "BAD", "error", "bad")], AssessmentConfig())
    assert result.status == "INSUFFICIENT_DATA"
    assert result.abstained is True

