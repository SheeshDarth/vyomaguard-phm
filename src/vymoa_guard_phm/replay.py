"""Deterministic end-to-end assessment replay."""

from __future__ import annotations

import argparse
import hashlib
import json
from math import isfinite
from pathlib import Path

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import InputWindow, MissionAssessment
from vymoa_guard_phm.data.validator import has_failure, validate_input
from vymoa_guard_phm.models.orbit import OrbitRiskEngine
from vymoa_guard_phm.models.telemetry import TelemetryAnomalyEngine
from vymoa_guard_phm.policy.rules import evaluate_policy
from vymoa_guard_phm.reports.render import write_reports

DEFAULT_FIXTURE = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "scenarios.json"


def load_scenario(scenario_id: str, fixture_path: str | Path = DEFAULT_FIXTURE) -> InputWindow:
    fixture = Path(fixture_path)
    payload = json.loads(fixture.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Scenario fixture must contain an object keyed by scenario ID.")
    try:
        window = InputWindow.from_dict(payload[scenario_id])
    except KeyError as exc:
        raise ValueError(f"Unknown scenario {scenario_id!r}. Available: {sorted(payload)}") from exc
    window.metadata["_fixture_source"] = fixture.name
    window.metadata["_fixture_sha256"] = hashlib.sha256(fixture.read_bytes()).hexdigest()
    return window


def _run_id(window: InputWindow, config: AssessmentConfig) -> str:
    content = json.dumps({"window": window.__dict__, "config": config.to_dict()}, sort_keys=True).encode("utf-8")
    return hashlib.sha256(content).hexdigest()[:16]


def _hash_payload(payload: object) -> str:
    def safe(value: object) -> object:
        if isinstance(value, float) and not isfinite(value):
            return f"nonfinite:{value!r}"
        if isinstance(value, dict):
            return {str(key): safe(item) for key, item in value.items()}
        if isinstance(value, list):
            return [safe(item) for item in value]
        return value

    canonical = json.dumps(safe(payload), sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def run_assessment(window: InputWindow, config: AssessmentConfig | None = None) -> MissionAssessment:
    config = config or AssessmentConfig()
    findings = validate_input(window, config)
    if has_failure(findings):
        orbit = OrbitRiskEngine(config).score({})
        telemetry = TelemetryAnomalyEngine(config).score([])
    else:
        orbit = OrbitRiskEngine(config).score(window.orbit_event)
        telemetry = TelemetryAnomalyEngine(config).score(window.telemetry)
    decision = evaluate_policy(orbit, telemetry, findings, config)
    input_hash = _hash_payload(window.__dict__)
    config_hash = _hash_payload(config.to_dict())
    policy_hash = _hash_payload({"policy_version": config.policy_version, "thresholds": {"orbit_monitor": config.orbit_monitor_threshold, "orbit_review": config.orbit_review_threshold, "orbit_red": config.orbit_red_threshold, "telemetry_anomaly": config.telemetry_anomaly_threshold}})
    assessment = MissionAssessment(
        run_id=_run_id(window, config),
        scenario_id=window.scenario_id,
        created_at="2026-01-01T00:00:00+00:00",
        input_manifest={"scenario_id": window.scenario_id, "source": window.metadata.get("_fixture_source", "in-memory input"), "fixture_sha256": window.metadata.get("_fixture_sha256"), "fixture_version": window.metadata.get("fixture_version", "unknown"), "input_hash": input_hash, "config_hash": config_hash},
        quality_findings=findings,
        orbit=orbit,
        telemetry=telemetry,
        decision=decision,
        versions={"package": "0.1.0", "policy": config.policy_version, "policy_hash": policy_hash, "orbit_model": orbit.model_version, "telemetry_model": telemetry.model_version},
        limitations=[
            "This replay uses deterministic demo fixtures, not live mission data.",
            "Orbit score is a ranking-oriented baseline until dataset labels support calibration.",
            "Telemetry score indicates unusual behavior; it is not a subsystem-failure probability.",
            "Feature attribution is model evidence, not causal explanation.",
            "Evidence hash is an integrity fingerprint, not an authenticity signature.",
        ],
    )
    assessment.evidence_hash = assessment.compute_evidence_hash()
    return assessment


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Replay a VymoaGaurd PHM mission-assurance scenario.")
    parser.add_argument("--scenario", default="nominal", help="Scenario ID from the fixture manifest.")
    parser.add_argument("--fixture", default=str(DEFAULT_FIXTURE), help="Path to a scenario JSON fixture.")
    parser.add_argument("--output", default="reports/generated", help="Output directory for JSON and Markdown reports.")
    args = parser.parse_args(argv)
    assessment = run_assessment(load_scenario(args.scenario, args.fixture))
    json_path, markdown_path = write_reports(assessment, args.output)
    print(json.dumps({"status": assessment.decision.status, "json": str(json_path), "markdown": str(markdown_path)}, indent=2))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
