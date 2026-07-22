from vymoa_guard_phm.replay import load_scenario, run_assessment


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

