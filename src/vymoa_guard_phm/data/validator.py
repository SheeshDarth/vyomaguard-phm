"""Pre-scoring data-quality checks."""

from __future__ import annotations

from math import isfinite

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.contracts import InputWindow, ValidationFinding


def _finding(status: str, code: str, severity: str, message: str, field: str | None = None) -> ValidationFinding:
    return ValidationFinding(status=status, code=code, severity=severity, message=message, field=field)  # type: ignore[arg-type]


def validate_input(window: InputWindow, config: AssessmentConfig) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []
    event = window.orbit_event
    if not event:
        findings.append(_finding("FAIL", "DATA_MISSING_ORBIT_EVENT", "error", "An orbit event is required.", "orbit_event"))
    else:
        for required in ("event_id", "timestamp"):
            if required not in event:
                findings.append(_finding("FAIL", "DATA_MISSING_REQUIRED", "error", f"Missing orbit field: {required}.", f"orbit_event.{required}"))
        if not isinstance(event.get("features"), dict) or not event.get("features"):
            findings.append(_finding("FAIL", "DATA_MISSING_FEATURES", "error", "Orbit event requires a non-empty features mapping.", "orbit_event.features"))
        else:
            for name, value in event["features"].items():
                try:
                    if not isfinite(float(value)):
                        raise ValueError
                except (TypeError, ValueError):
                    findings.append(_finding("FAIL", "DATA_INVALID_FEATURE", "error", f"Orbit feature {name!r} must be finite numeric data.", f"orbit_event.features.{name}"))
            if "risk_score_hint" in event:
                try:
                    if not isfinite(float(event["risk_score_hint"])):
                        raise ValueError
                except (TypeError, ValueError):
                    findings.append(_finding("FAIL", "DATA_INVALID_FEATURE", "error", "Orbit risk_score_hint must be finite numeric data.", "orbit_event.risk_score_hint"))

    if window.metadata.get("contradictory"):
        findings.append(_finding("FAIL", "DATA_CONTRADICTORY", "error", "Input metadata marks the window as contradictory."))
    if window.metadata.get("stale"):
        findings.append(_finding("FAIL", "DATA_STALE", "error", "Input metadata marks the window as stale."))
    freshness = window.metadata.get("freshness_minutes")
    if freshness is not None:
        try:
            if float(freshness) > config.freshness_limit_minutes:
                findings.append(_finding("FAIL", "DATA_STALE", "error", f"Input freshness exceeds {config.freshness_limit_minutes} minutes.", "metadata.freshness_minutes"))
        except (TypeError, ValueError):
            findings.append(_finding("FAIL", "DATA_INVALID_FRESHNESS", "error", "Freshness must be numeric.", "metadata.freshness_minutes"))

    if config.required_telemetry and not window.telemetry:
        findings.append(_finding("FAIL", "DATA_MISSING_TELEMETRY", "error", "Telemetry is required for a complete mission assessment.", "telemetry"))
    seen_channels: set[str] = set()
    for index, row in enumerate(window.telemetry):
        for required in ("timestamp", "channel", "value"):
            if required not in row:
                findings.append(_finding("FAIL", "DATA_MISSING_REQUIRED", "error", f"Missing telemetry field: {required}.", f"telemetry[{index}].{required}"))
        channel = row.get("channel")
        if channel is not None:
            seen_channels.add(str(channel))
        try:
            if not isfinite(float(row.get("value"))):
                raise ValueError
        except (TypeError, ValueError):
            findings.append(_finding("FAIL", "DATA_INVALID_VALUE", "error", "Telemetry value must be numeric.", f"telemetry[{index}].value"))

    missing_channels = set(config.required_channels) - seen_channels
    if missing_channels:
        findings.append(_finding("FAIL", "DATA_MISSING_CHANNEL", "error", f"Missing required channels: {sorted(missing_channels)}.", "telemetry"))

    if not findings:
        findings.append(_finding("PASS", "DATA_VALID", "info", "Input schema and quality gates passed."))
    return findings


def has_failure(findings: list[ValidationFinding]) -> bool:
    return any(finding.status == "FAIL" for finding in findings)
