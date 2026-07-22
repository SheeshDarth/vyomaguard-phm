# Integration Test Plan

## Purpose

Verify that the canonical assessment flow preserves contracts and evidence across modules. The system under test is the complete in-process replay path; tests use small deterministic fixtures and avoid mocking the validator, model baselines, policy, or report renderer.

## Interfaces under test

| Boundary | Contract | Failure risk |
| --- | --- | --- |
| Fixture to input | `InputWindow.from_dict` | malformed or incomplete input is silently accepted |
| Input to validation | `validate_input(window, config)` | stale, missing, contradictory, or invalid data reaches scoring |
| Input to engines | `OrbitRiskEngine` and `TelemetryAnomalyEngine` | score type or evidence loses its semantics |
| Engines to policy | `evaluate_policy(...)` | precedence and abstention rules are bypassed |
| Policy to assessment | `MissionAssessment` | versions, provenance, or limitations are absent |
| Assessment to reports | `to_json` and `to_markdown` | UI/export drift or missing decision evidence |

## Scenarios

| Scenario | Expected result | Required assertions |
| --- | --- | --- |
| `nominal` | `GREEN` | deterministic assessment, scored engines, no abstention |
| `conjunction_risk` | `RED` | orbit evidence and rule trace exist; no maneuver command is generated |
| `telemetry_anomaly` | `AMBER` | anomaly score identifies affected channels and policy remains deterministic |
| `bad_input` | `INSUFFICIENT_DATA` | failed quality findings are preserved and assessment abstains |
| report round trip | unchanged | parsed JSON matches the canonical assessment and Markdown contains the same run/status |
| temporal split | safe split | train/test ordering is chronological and entity keys do not overlap |
| label audit | explicit status | binary support is reported instead of inferred silently |

## Test setup

- Python 3.11 or 3.12.
- Install the development extra with `python -m pip install -e ".[dev]"`.
- Run from the repository root with `python -m pytest`.
- Use `tmp_path` for generated reports; never use committed report directories.
- Keep downloaded datasets outside the repository and use manifest metadata when Phase 2 begins.

## Exit gate

The foundation phase is complete when all scenarios pass, replay is deterministic, failed quality gates abstain, labels and splits are explicitly audited, and JSON/Markdown exports preserve the canonical decision.
