# VymoaGaurd PHM Build Phases

This is the working delivery sequence for VymoaGaurd PHM. Each phase has one primary engineering skill and one explicit exit gate. The skills support the work; the repository tests and acceptance criteria remain authoritative.

## Phase 0 - Repository and documentation baseline

Primary skills: `codebase-orientation`, `github:github`.

Deliverables:

- repository naming, license, contribution, security, and CI files;
- authoritative project brief and linked product/technical documentation;
- a clean public-repository boundary with no datasets, secrets, checkpoints, or reports committed.

Exit gate: the repository can be cloned and its documentation can be read without private mission data.

## Phase 1 - Foundation and contracts (current)

Primary skills: `codebase-orientation`, `integration-test-planner`, `unit-test-starter`.

Deliverables:

- typed assessment contracts and versioned configuration;
- deterministic fixtures and replay;
- data-quality findings and abstention behavior;
- integration scenarios covering validation, model outputs, policy, and report parity;
- dataset label-audit and temporal-split primitives.

Exit gate: `python -m pytest` passes and every fixture produces a deterministic canonical assessment.

## Phase 2 - Dataset acquisition and label audit

Primary skills: `security-quick-scan` for data-boundary review and `integration-test-planner` for ingestion tests.

Deliverables:

- frozen dataset manifests, checksums, and download instructions;
- documented label semantics and entity/time grouping;
- chronological/group splits and leakage tests;
- an explicit decision on probability versus ranking/anomaly terminology.

Exit gate: a frozen, auditable dataset snapshot passes the label and leakage acceptance matrix.

## Phase 3 - Orbit risk engine

Primary skills: `unit-test-starter` for feature/model edge cases and `performance-budgeting` for runtime constraints.

Deliverables:

- CDM adapter and feature pipeline;
- logistic-regression baseline and temporal holdout evaluation;
- threshold metrics, failure-case analysis, and feature attribution;
- optional XGBoost comparison only after baseline gates pass.

Exit gate: reproducible holdout metrics are recorded without temporal or entity leakage.

## Phase 4 - Telemetry anomaly engine

Primary skills: `integration-test-planner` and `performance-budgeting`.

Deliverables:

- bounded channel schema and robust rolling features;
- Isolation Forest baseline;
- affected-channel and anomaly-window evidence;
- audited-label or documented injected-fault evaluation;
- optional autoencoder only if it improves held-out results materially.

Exit gate: telemetry output is validated as an anomaly score, or explicitly marked exploratory.

## Phase 5 - Decision layer and evidence chain

Primary skills: `unit-test-starter`, `security-quick-scan`.

Deliverables:

- pure deterministic policy rules;
- precedence, contradiction, freshness, missingness, and disagreement handling;
- reason codes, review action, policy version, and rule trace;
- canonical JSON contract consumed by every downstream surface.

Exit gate: malformed, stale, and contradictory inputs abstain correctly and every non-green result has evidence.

## Phase 6 - Dashboard and reporting

Primary skills: `ui-ux-pro-max`, `accessibility-basic-check`, and `readme-polish`.

Deliverables:

- Mission Overview, Orbit Risk, Telemetry Health, and Decision Report screens;
- scenario replay and evidence navigation;
- JSON and Markdown exports, followed by PDF only after parity is stable;
- dashboard smoke tests and accessible status presentation.

Exit gate: the dashboard and exports render from the same `MissionAssessment` object.

## Phase 7 - Hardening and demo

Primary skills: `security-quick-scan`, `performance-budgeting`, `pr-reviewer`, and `readme-polish`.

Deliverables:

- clean-machine replay;
- golden JSON/Markdown reports;
- runtime and memory benchmarks;
- security, dependency, and public-repository review;
- screenshots, demo script, limitations, and release notes.

Exit gate: the fixed-data path is demonstrable end to end and the safety boundary is visible in code and documentation.

## Scope fallback

Cut PDF generation, deep-learning experiments, extra telemetry channels, dashboard polish, and model upgrades in that order. Preserve validation, provenance, abstention, deterministic policy, rule traces, and replayability.
