# VymoaGaurd PHM

Space mission-assurance prototype for explainable conjunction-risk assessment, satellite telemetry anomaly detection, and deterministic operator triage.

> **Status:** Product and technical design baseline. The implementation has not started. This repository is a prototype plan, not flight software, a certified safety system, or an autonomous maneuver planner.

## What it does

VymoaGaurd PHM turns two evidence streams into one auditable mission-assurance assessment:

1. A CDM-based orbit-risk model classifies conjunction risk under documented assumptions.
2. A telemetry model detects abnormal behavior and localizes affected channels/windows.
3. A deterministic policy layer converts the two signals, data quality, freshness, and uncertainty into `GREEN`, `AMBER`, `RED`, or `INSUFFICIENT_DATA` triage.
4. A Streamlit dashboard and JSON/Markdown/PDF report expose the evidence, provenance, explanations, and limitations.

The product claim is intentionally narrow:

> Given validated inputs and fixed assumptions, VymoaGaurd PHM produces a reproducible, explainable conjunction-risk classification and deterministic operator triage.

## Documentation map

- [Overview](docs/OVERVIEW.md) — product brief, users, scope, terminology, and repository map.
- [PRD](docs/PRD.md) — product requirements, user stories, acceptance criteria, and non-goals.
- [TRD](docs/TRD.md) — technical requirements, interfaces, data contracts, quality attributes, and test strategy.
- [Architecture](docs/ARCHITECTURE.md) — components, data flow, deployment shape, and key decisions.
- [Data and Labels](docs/DATA_AND_LABELS.md) — dataset choice, schemas, label audit, splits, and leakage controls.
- [Evaluation and Acceptance](docs/EVALUATION_AND_ACCEPTANCE.md) — metrics and quantitative go/no-go gates.
- [Decision Policy](docs/DECISION_POLICY.md) — deterministic triage rules and abstention behavior.
- [Roadmap](docs/ROADMAP.md) — revised six-week solo-build plan and fallback cuts.
- [Safety and Limitations](docs/SAFETY_AND_LIMITATIONS.md) — safe framing, misuse boundaries, and known limitations.
- [Requirements Traceability](docs/REQUIREMENTS_TRACEABILITY.md) — source requirement to artifact and verification mapping.
- [Glossary](docs/GLOSSARY.md) — plain-language terms for reviewers and operators.
- [Council Decision Log](docs/DECISION_LOG.md) — scope decisions and rationale from the five-advisor review.
- [Knowledge Graph Audit](graphify-out/GRAPH_REPORT.md) — evidence-backed project graph, communities, and open questions.

## Intended MVP

- Primary: calibrated logistic regression or gradient-boosted CDM classifier, selected by acceptance gates.
- Secondary: robust rolling statistics plus Isolation Forest on one telemetry dataset and a deliberately bounded channel subset.
- Decision layer: deterministic policy with data-quality gates and explicit abstention.
- Dashboard: mission overview, orbit risk, telemetry health, and decision report screens.
- First end-to-end artifact: a versioned CLI replay that produces a JSON mission-assurance report from fixed fixtures.

Deep sequence models are optional experiments. They must not delay the baseline, change the acceptance protocol, or become the primary product claim.

## Proposed repository shape

```text
VymoaGaurd PHM/
├── VymoaGaurd_PHM_Project_Brief.md   # authoritative source brief
├── README.md
├── docs/                             # product and technical design
└── graphify-out/                     # evidence graph and audit artifacts
```

When implementation begins, add the Python package, tests, data manifests, model artifacts, and Streamlit entry point under the same documentation contracts.

## Non-negotiable boundaries

- No autonomous maneuver recommendation or command generation.
- No claim of flight readiness, collision certainty, or subsystem-failure probability from an anomaly score.
- No probability fusion across orbit and telemetry without a separately validated statistical model; the MVP uses rule-based evidence combination.
- Missing, stale, contradictory, or out-of-distribution inputs must be visible and can force `INSUFFICIENT_DATA`.
- Public datasets, fixed fixtures, and synthetic/injected faults must be identified in every report.

## Source basis

This design set is derived from the full contents of [VymoaGaurd_PHM_Project_Brief.md](VymoaGaurd_PHM_Project_Brief.md). The source brief defines the concept, MVP modules, candidate datasets/models, dashboard screens, exclusions, stack, and original six-week plan. This documentation tightens that plan with explicit assumptions, safety boundaries, traceability, and go/no-go gates.
