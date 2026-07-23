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


def test_malformed_replay_abstains_instead_of_crashing():
    assessment = run_assessment(InputWindow.from_dict({"scenario_id": "malformed", "orbit_event": [], "telemetry": [None]}))

    assert assessment.decision.status == "INSUFFICIENT_DATA"
    assert assessment.decision.abstained is True
    assert any(item.code == "DATA_INVALID_SHAPE" for item in assessment.quality_findings)


def test_fixture_replay_records_actual_fixture_identity_and_heuristic_semantics():
    assessment = run_assessment(load_scenario("nominal"))

    assert assessment.input_manifest["source"] == "scenarios.json"
    assert assessment.input_manifest["fixture_sha256"]
    assert assessment.orbit.risk_class == "LOW_RANKING"
    assert assessment.orbit.model_version == "orbit-heuristic-fixture-0.1.0"
    assert all(item.get("attribution") is None for item in assessment.orbit.top_features)


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
