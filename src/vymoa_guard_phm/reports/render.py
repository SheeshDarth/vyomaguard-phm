"""Render the canonical MissionAssessment without duplicating business logic."""

from __future__ import annotations

import json
from pathlib import Path
import re

from vymoa_guard_phm.contracts import MissionAssessment


class EvidenceIntegrityError(ValueError):
    """Raised when an assessment cannot be proven internally consistent."""


def _require_verified(assessment: MissionAssessment) -> None:
    if not assessment.verify_evidence_hash():
        raise EvidenceIntegrityError("Assessment evidence hash is missing or invalid; export is blocked.")


def safe_report_stem(value: str) -> str:
    """Return a path-safe, bounded report filename stem."""

    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", str(value)).strip("._-")[:64] or "assessment"
    if stem.upper() in {"CON", "PRN", "AUX", "NUL", "COM1", "LPT1"}:
        stem = f"assessment_{stem}"
    return stem


def to_json(assessment: MissionAssessment) -> str:
    _require_verified(assessment)
    return json.dumps(assessment.to_dict(), allow_nan=False, indent=2, sort_keys=True) + "\n"


def to_markdown(assessment: MissionAssessment) -> str:
    _require_verified(assessment)
    data = assessment.to_dict()
    orbit = data["orbit"]
    telemetry = data["telemetry"]
    decision = data["decision"]
    findings = data["quality_findings"]
    lines = [
        f"# VymoaGaurd PHM Mission Assessment — {assessment.scenario_id}",
        "",
        "> Prototype decision-support output. Research/demo only; not flight-certified software and not an autonomous maneuver recommendation.",
        "",
        f"- **Run ID:** `{assessment.run_id}`",
        f"- **Evidence hash:** `{assessment.evidence_hash}`",
        f"- **Evidence schema:** `{assessment.evidence_schema_version}`",
        f"- **Created:** `{assessment.created_at}`",
        f"- **Decision:** **{decision['status']}** — {decision['review_action']}",
        f"- **Abstained:** `{decision['abstained']}`",
        f"- **Reason codes:** `{', '.join(decision['reason_codes']) or 'none'}`",
        "",
        "## Data quality",
        "",
    ]
    lines.extend(f"- `{item['status']}` `{item['code']}` `{item['severity']}` — {item['message']}" for item in findings)
    lines.extend([
        "",
        "## Provenance and evidence chain",
        "",
        f"- Source: `{assessment.input_manifest.get('source')}`",
        f"- Fixture version: `{assessment.input_manifest.get('fixture_version')}`",
        f"- Fixture SHA-256: `{assessment.input_manifest.get('fixture_sha256')}`",
        f"- Input hash: `{assessment.input_manifest.get('input_hash')}`",
        f"- Configuration hash: `{assessment.input_manifest.get('config_hash')}`",
        f"- Policy hash: `{assessment.versions.get('policy_hash')}`",
        f"- Canonical object hash verified: `{assessment.verify_evidence_hash()}`",
        "- Versions:",
    ])
    lines.extend(f"  - `{key}` = `{value}`" for key, value in sorted(assessment.versions.items()))
    lines.extend([
        "",
        "## Orbit risk",
        "",
        f"- Score type: `{orbit['score_type']}`; this is a ranking score, not a probability.",
        f"- Score: `{orbit['score']}`",
        f"- Class: `{orbit['risk_class']}`; this is not a safety determination.",
        f"- Model version: `{orbit['model_version']}`",
        f"- Threshold version: `{orbit['threshold_version']}`",
        "- Top feature evidence:",
    ])
    lines.extend(
        f"  - `{item['name']}` = `{item['value']}`; evidence type `{item.get('evidence_type', 'model_attribution')}`; attribution `{item.get('attribution')}`"
        for item in orbit["top_features"]
    )
    lines.append("- Orbit evidence:")
    lines.extend(f"  - {item}" for item in orbit["evidence"])
    lines.extend([
        "",
        "## Telemetry health",
        "",
        f"- Score type: `{telemetry['score_type']}`; this is an anomaly score, not a failure probability.",
        f"- Score: `{telemetry['score']}`",
        f"- Model version: `{telemetry['model_version']}`",
        f"- Threshold version: `{telemetry['threshold_version']}`",
        f"- Affected channels: `{', '.join(telemetry['affected_channels']) or 'none'}`",
        f"- Anomaly window: `{telemetry['anomaly_window']}`",
        "- Telemetry evidence:",
    ])
    lines.extend(f"  - {item}" for item in telemetry["evidence"])
    lines.extend([
        "",
        "## Decision rule trace",
        "",
    ])
    lines.extend(f"- `{item['rule_id']}` → `{item['result']}` — {item['evidence']}" for item in decision["rule_trace"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in assessment.limitations)
    return "\n".join(lines) + "\n"


def write_reports(assessment: MissionAssessment, output_dir: str | Path) -> tuple[Path, Path]:
    _require_verified(assessment)
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    resolved_directory = directory.resolve()
    stem = safe_report_stem(assessment.scenario_id)
    json_path = (resolved_directory / f"{stem}.json").resolve()
    markdown_path = (resolved_directory / f"{stem}.md").resolve()
    for path in (json_path, markdown_path):
        try:
            path.relative_to(resolved_directory)
        except ValueError as exc:
            raise ValueError("Report path escaped the requested output directory.") from exc
    json_path.write_text(to_json(assessment), encoding="utf-8")
    markdown_path.write_text(to_markdown(assessment), encoding="utf-8")
    return json_path, markdown_path
