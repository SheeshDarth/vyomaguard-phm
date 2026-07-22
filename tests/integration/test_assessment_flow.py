import json
from vymoa_guard_phm.replay import load_scenario, run_assessment
from vymoa_guard_phm.reports.render import to_json, to_markdown, write_reports


EXPECTED_STATUS = {
    "nominal": "GREEN",
    "conjunction_risk": "RED",
    "telemetry_anomaly": "AMBER",
    "bad_input": "INSUFFICIENT_DATA",
}


def test_all_fixture_scenarios_cross_the_canonical_flow():
    for scenario_id, expected_status in EXPECTED_STATUS.items():
        assessment = run_assessment(load_scenario(scenario_id))
        payload = assessment.to_dict()

        assert assessment.decision.status == expected_status
        assert payload["input_manifest"]["fixture_version"] == "0.1.0"
        assert payload["versions"]["policy"]
        assert payload["versions"]["policy_hash"]
        assert payload["input_manifest"]["input_hash"]
        assert payload["input_manifest"]["config_hash"]
        assert assessment.verify_evidence_hash()
        assert payload["limitations"]
        assert payload["decision"]["rule_trace"]


def test_reports_preserve_the_canonical_assessment(tmp_path):
    assessment = run_assessment(load_scenario("conjunction_risk"))
    json_path, markdown_path = write_reports(assessment, tmp_path)

    assert json.loads(json_path.read_text(encoding="utf-8")) == assessment.to_dict()
    markdown = markdown_path.read_text(encoding="utf-8")
    assert assessment.run_id in markdown
    assert f"**{assessment.decision.status}**" in markdown
    assert "Decision rule trace" in markdown
    assert to_json(assessment) == json_path.read_text(encoding="utf-8")
    assert to_markdown(assessment) == markdown


def test_evidence_hash_detects_mutation():
    assessment = run_assessment(load_scenario("nominal"))
    assert assessment.verify_evidence_hash()
    assessment.decision.reason_codes.append("TAMPERED")
    assert not assessment.verify_evidence_hash()
