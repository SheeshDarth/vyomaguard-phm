"""Render the canonical MissionAssessment without duplicating business logic."""

from __future__ import annotations

import json
from pathlib import Path

from vymoa_guard_phm.contracts import MissionAssessment


def to_json(assessment: MissionAssessment) -> str:
    return json.dumps(assessment.to_dict(), indent=2, sort_keys=True) + "\n"


def to_markdown(assessment: MissionAssessment) -> str:
    data = assessment.to_dict()
    orbit = data["orbit"]
    telemetry = data["telemetry"]
    decision = data["decision"]
    findings = data["quality_findings"]
    lines = [
        f"# VymoaGaurd PHM Mission Assessment — {assessment.scenario_id}",
        "",
        "> Prototype decision-support output. Not flight-certified software and not an autonomous maneuver recommendation.",
        "",
        f"- **Run ID:** `{assessment.run_id}`",
        f"- **Created:** `{assessment.created_at}`",
        f"- **Decision:** **{decision['status']}** — {decision['review_action']}",
        f"- **Abstained:** `{decision['abstained']}`",
        "",
        "## Data quality",
        "",
    ]
    lines.extend(f"- `{item['status']}` `{item['code']}` — {item['message']}" for item in findings)
    lines.extend([
        "",
        "## Orbit risk",
        "",
        f"- Score type: `{orbit['score_type']}`",
        f"- Score: `{orbit['score']}`",
        f"- Class: `{orbit['risk_class']}`",
        "- Top feature evidence:",
    ])
    lines.extend(f"  - `{item['name']}` = `{item['value']}`; attribution `{item['attribution']}`" for item in orbit["top_features"])
    lines.extend([
        "",
        "## Telemetry health",
        "",
        f"- Score type: `{telemetry['score_type']}`",
        f"- Score: `{telemetry['score']}`",
        f"- Affected channels: `{', '.join(telemetry['affected_channels']) or 'none'}`",
        f"- Anomaly window: `{telemetry['anomaly_window']}`",
        "",
        "## Decision rule trace",
        "",
    ])
    lines.extend(f"- `{item['rule_id']}` → `{item['result']}` — {item['evidence']}" for item in decision["rule_trace"])
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {limitation}" for limitation in assessment.limitations)
    return "\n".join(lines) + "\n"


def write_reports(assessment: MissionAssessment, output_dir: str | Path) -> tuple[Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    json_path = directory / f"{assessment.scenario_id}.json"
    markdown_path = directory / f"{assessment.scenario_id}.md"
    json_path.write_text(to_json(assessment), encoding="utf-8")
    markdown_path.write_text(to_markdown(assessment), encoding="utf-8")
    return json_path, markdown_path

