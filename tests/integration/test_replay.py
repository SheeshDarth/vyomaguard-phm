from vymoa_guard_phm.replay import load_scenario, run_assessment
from vymoa_guard_phm.contracts import InputWindow
from vymoa_guard_phm.reports.render import to_json


def test_nominal_replay_is_deterministic():
    first = run_assessment(load_scenario("nominal"))
    second = run_assessment(load_scenario("nominal"))
    assert first.to_dict() == second.to_dict()
    assert first.decision.status == "GREEN"


def test_risk_replay_is_red_without_maneuver_command():
    assessment = run_assessment(load_scenario("conjunction_risk"))
    assert assessment.decision.status == "RED"
    assert "maneuver" not in assessment.decision.review_action.lower()


def test_bad_replay_abstains():
    assessment = run_assessment(load_scenario("bad_input"))
    assert assessment.decision.status == "INSUFFICIENT_DATA"
    assert assessment.decision.abstained is True


def test_nonfinite_input_abstains_with_strict_evidence_record():
    window = InputWindow(
        scenario_id="nonfinite",
        orbit_event={"event_id": "bad", "timestamp": "2026-01-01T00:00:00Z", "features": {"x": float("nan")}},
        telemetry=[{"timestamp": "2026-01-01T00:00:00Z", "channel": "power_bus", "value": float("inf")}],
    )
    assessment = run_assessment(window)
    assert assessment.decision.status == "INSUFFICIENT_DATA"
    assert assessment.verify_evidence_hash()
    assert "NaN" not in to_json(assessment)
