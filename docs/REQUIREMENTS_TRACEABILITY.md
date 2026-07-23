# Requirements Traceability — VymoaGaurd PHM

The source brief is the authoritative product input. This table maps its major statements to planned artifacts and verification evidence.

| ID | Source requirement | Design artifact | Verification |
|---|---|---|---|
| BR-01 | Explainable space mission-assurance dashboard | [PRD](PRD.md), [Architecture](ARCHITECTURE.md) | End-to-end replay, canonical assessment, and dashboard smoke test |
| BR-02 | CDM conjunction/collision-risk module | [TRD](TRD.md), [Data and Labels](DATA_AND_LABELS.md) | Label audit, temporal holdout, metrics |
| BR-03 | ESA Collision Avoidance Challenge dataset | [Data and Labels](DATA_AND_LABELS.md) | Dataset manifest and checksum |
| BR-04 | Baseline and advanced orbit models | [TRD](TRD.md), [Evaluation](EVALUATION_AND_ACCEPTANCE.md) | Baseline gate and optional comparison |
| BR-05 | SHAP explanations | [TRD](TRD.md), [Safety](SAFETY_AND_LIMITATIONS.md) | Attribution presence/stability check |
| BR-06 | Telemetry anomaly module | [PRD](PRD.md), [Architecture](ARCHITECTURE.md) | Labeled/injected-fault evaluation |
| BR-07 | OPSSAT-AD or SMAP/MSL options | [Data and Labels](DATA_AND_LABELS.md) | Week 1 dataset decision record |
| BR-08 | Affected channels and anomaly windows | [TRD](TRD.md), [PRD](PRD.md) | Channel/window output tests |
| BR-09 | Mission decision layer | [Decision Policy](DECISION_POLICY.md) | Rule-table, precedence, invalid-output, disagreement, and abstention tests |
| BR-10 | Deterministic policy preferred over LLM dependency | [Architecture](ARCHITECTURE.md), [Safety](SAFETY_AND_LIMITATIONS.md) | No LLM in decision path |
| BR-11 | Streamlit screens | [PRD](PRD.md), [Roadmap](ROADMAP.md) | `tests/integration/test_dashboard.py` and replay |
| BR-12 | Markdown/PDF/JSON report export | [TRD](TRD.md), [PRD](PRD.md) | Strict JSON/Markdown parity; PDF deferred |
| BR-13 | Solo build / RTX 4050 | [TRD](TRD.md), [Roadmap](ROADMAP.md) | Runtime/memory benchmark and CPU fallback |
| BR-14 | Avoid out-of-scope features | [PRD](PRD.md), [Safety](SAFETY_AND_LIMITATIONS.md) | Scope review before merge |
| BR-15 | Six-week plan | [Roadmap](ROADMAP.md) | Weekly exit gates |
| BR-16 | Portfolio/internship positioning | [Overview](OVERVIEW.md), `README.md` | Demo and resume wording review |

## Evidence status

Rows BR-01, BR-09, BR-11, BR-12, and the related foundation/replay rows now have implementation evidence in the repository test suite. Remaining rows are design-level traceability until their corresponding data, model, or hardening gates are completed.
