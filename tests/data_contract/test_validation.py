import json
from pathlib import Path

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import InputWindow
from vymoa_guard_phm.data.validator import validate_input


def test_bad_fixture_fails_quality_gates():
    fixture = json.loads(Path("data/fixtures/scenarios.json").read_text())
    findings = validate_input(InputWindow.from_dict(fixture["bad_input"]), AssessmentConfig())
    assert any(item.code == "DATA_CONTRADICTORY" for item in findings)
    assert any(item.code == "DATA_MISSING_TELEMETRY" for item in findings)


def test_malformed_nested_shapes_are_reported_without_crashing():
    window = InputWindow.from_dict({"scenario_id": "malformed", "orbit_event": [], "telemetry": [None, "row"], "metadata": "bad"})

    findings = validate_input(window, AssessmentConfig())

    assert any(item.code == "DATA_INVALID_SHAPE" for item in findings)


def test_nonfinite_or_negative_freshness_fails_quality_gate():
    fixture = json.loads(Path("data/fixtures/scenarios.json").read_text())
    window = InputWindow.from_dict(fixture["nominal"])
    window.metadata["freshness_minutes"] = float("nan")

    findings = validate_input(window, AssessmentConfig())

    assert any(item.code == "DATA_INVALID_FRESHNESS" for item in findings)
