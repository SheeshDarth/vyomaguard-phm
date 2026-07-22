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

