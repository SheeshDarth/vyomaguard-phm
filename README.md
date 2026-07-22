# VymoaGaurd PHM

[![CI](https://github.com/SheeshDarth/vyomaguard-phm/actions/workflows/ci.yml/badge.svg)](https://github.com/SheeshDarth/vyomaguard-phm/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Explainable space mission-assurance prototype for conjunction-risk ranking, satellite telemetry anomaly detection, and deterministic operator triage.

> **Safety boundary:** This is research/portfolio software. It is not flight-certified, does not issue maneuver commands, and does not replace flight-dynamics or mission-operations procedures.

## What it does

VymoaGaurd PHM turns two evidence streams into one auditable mission-assurance assessment:

1. A CDM-based orbit-risk baseline ranks conjunction scenarios against the audited continuous ESA log-risk target under documented assumptions.
2. A telemetry baseline detects unusual behavior and localizes affected channels/windows.
3. A deterministic policy layer converts risk, anomaly evidence, data quality, freshness, and uncertainty into `GREEN`, `AMBER`, `RED`, or `INSUFFICIENT_DATA`.
4. A Streamlit dashboard and JSON/Markdown reports expose the evidence, provenance, explanations, and limitations.

The product claim is intentionally narrow:

> Given validated inputs and fixed assumptions, VymoaGaurd PHM produces a reproducible, explainable conjunction-risk ranking/anomaly assessment and deterministic operator triage.

## Quick start

PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:PYTHONPATH = "src"
python -m pytest
python -m vymoa_guard_phm.replay --scenario nominal --output reports/generated
python -m vymoa_guard_phm.data.manifest --manifest-dir data/manifests
python -m vymoa_guard_phm.evaluation.telemetry --segments data/downloads/opssat-ad/segments.csv --manifest data/manifests/esa_opssat_ad.yaml
python -m streamlit run src/vymoa_guard_phm/app.py
```

Available deterministic fixtures:

- `nominal` → `GREEN`
- `conjunction_risk` → `RED`
- `telemetry_anomaly` → `AMBER`
- `bad_input` → `INSUFFICIENT_DATA`

## Current implementation

- Typed contracts for input windows, validation findings, model assessments, decisions, and reports.
- Data-quality validation with stale, contradictory, missing, and invalid-input abstention.
- Logistic Regression-compatible orbit baseline with deterministic heuristic fallback.
- Robust telemetry statistics with optional Isolation Forest comparison path.
- OPSSAT-AD segment-level holdout evaluator with anomaly-only metrics and no probability claims.
- Deterministic mission policy with reason codes and rule traces.
- Canonical JSON and Markdown report rendering.
- Streamlit dashboard with Mission Overview, Orbit Risk, Telemetry Health, Decision Report, and Data Quality views.
- Dataset adapters, manifests, label-audit helper, temporal split helper, and evaluation metrics.

## Documentation

- [Project Overview](docs/OVERVIEW.md)
- [Product Requirements](docs/PRD.md)
- [Technical Requirements](docs/TRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Data and Labels](docs/DATA_AND_LABELS.md)
  - [Dataset Label Audit](docs/DATASET_LABEL_AUDIT.md)
  - [Phase 3 Orbit Baseline](docs/PHASE_3_BASELINE.md)
  - [Phase 4 Telemetry Baseline](docs/PHASE_4_TELEMETRY_BASELINE.md)
  - [Phase 4 Deep Review](docs/PHASE_4_REVIEW.md)
- [Evaluation and Acceptance](docs/EVALUATION_AND_ACCEPTANCE.md)
- [Decision Policy](docs/DECISION_POLICY.md)
- [Six-Week Roadmap](docs/ROADMAP.md)
- [Build Phases and Skill Sequence](docs/BUILD_PHASES.md)
- [Integration Test Plan](docs/INTEGRATION_TEST_PLAN.md)
- [Safety and Limitations](docs/SAFETY_AND_LIMITATIONS.md)
- [Requirements Traceability](docs/REQUIREMENTS_TRACEABILITY.md)
- [GitHub Setup Options](docs/GITHUB_SETUP.md)
- [Knowledge Graph Audit](graphify-out/GRAPH_REPORT.md)

## Repository layout

```text
VymoaGaurd PHM/
├── VymoaGaurd_PHM_Project_Brief.md  # authoritative source brief
├── src/vymoa_guard_phm/             # domain package and Streamlit app
├── tests/                            # unit, contract, and integration tests
├── data/fixtures/                    # small deterministic fixtures only
├── data/manifests/                   # dataset provenance and label contracts
├── docs/                             # product, technical, safety, and GitHub docs
└── graphify-out/                     # project knowledge graph and audit
```

Downloaded datasets, real mission telemetry, secrets, model checkpoints, and generated reports are excluded from version control.

## Model and safety boundaries

- Primary orbit model: transparent regression/ranking baseline first; classification only after a validated binary target; XGBoost only after acceptance gates pass.
- Secondary telemetry model: robust rolling statistics plus Isolation Forest.
- Deep sequence models are optional experiments and never block the MVP.
- Cross-domain evidence is combined through deterministic rules, not an unvalidated joint probability.
- Feature attribution is model evidence, not causal explanation.
- `INSUFFICIENT_DATA` is a valid and visible outcome.
- No autonomous maneuver recommendation or command generation.

## License and contribution

This project is released under the [MIT License](LICENSE). See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.
