# Product Requirements Document — VymoaGaurd PHM

**Status:** Draft baseline for implementation  
**Source:** `VymoaGaurd_PHM_Project_Brief.md`  
**Product owner:** Solo builder  
**Target build window:** Six weeks  
**Deployment target:** Local development/demo machine, with CPU-compatible fallback

## 1. Problem statement

Satellite operators must monitor both external orbital risk and internal spacecraft behavior. The source brief identifies two recurring questions: whether a conjunction requires review and whether telemetry shows abnormal behavior. A model-only notebook does not give an operator a coherent, inspectable next step.

VymoaGaurd PHM provides a single evidence-oriented view that combines both signals without hiding uncertainty or implying autonomous authority.

## 2. Product goal

Deliver a replayable prototype that can:

- ingest validated CDM and telemetry data;
- score conjunction risk and telemetry abnormality;
- explain the evidence behind each score;
- apply deterministic triage rules;
- abstain safely when evidence is inadequate;
- display the result in a dashboard; and
- export a reproducible mission-assurance report.

## 3. Success definition

The MVP is successful when a reviewer can run one fixed scenario and trace:

`raw inputs → validation → features → model outputs → attributions → policy rule → triage → report`

The success criterion is traceability and validation quality, not the use of a particular neural architecture.

## 4. Personas and needs

### Mission-operations reviewer

Needs to see which evidence triggered attention, whether inputs are fresh and complete, and what review state is appropriate.

### Aerospace/ML interviewer or evaluator

Needs to verify dataset provenance, split discipline, metrics, failure analysis, reproducibility, and limitations.

### Developer/researcher

Needs stable data contracts, deterministic replay, separable components, model versioning, and machine-readable outputs.

## 5. User stories

| ID | User story | Priority |
|---|---|---|
| US-01 | As a reviewer, I can load a fixed scenario and see the overall triage state. | Must |
| US-02 | As a reviewer, I can inspect the CDM risk score, class, threshold, and top feature attributions. | Must |
| US-03 | As a reviewer, I can inspect telemetry anomaly score, affected channels, and anomaly time window. | Must |
| US-04 | As a reviewer, I can see the exact deterministic rule trace behind the triage state. | Must |
| US-05 | As a reviewer, I can see missing, stale, contradictory, or unsupported inputs and receive `INSUFFICIENT_DATA` when required. | Must |
| US-06 | As a reviewer, I can export the assessment as JSON and Markdown with provenance and limitations. | Must |
| US-07 | As a developer, I can replay the same fixture and obtain deterministic outputs. | Must |
| US-08 | As a developer, I can compare baseline and optional advanced models on a frozen temporal holdout. | Should |
| US-09 | As a reviewer, I can use a PDF version of the report if it can be generated without destabilizing the core workflow. | Could |
| US-10 | As a user, I can see a 3D orbit view or autonomous maneuver plan. | Won’t for MVP |

## 6. Functional requirements

### FR-01 — Input ingestion

The system shall ingest a CDM event/window and a telemetry window through versioned adapters. Raw inputs shall remain immutable and every assessment shall reference the input manifest.

### FR-02 — Data validation

The system shall validate schema, required fields, timestamp ordering, missingness, freshness, duplicate identifiers, and contradictory values before scoring.

### FR-03 — Orbit risk scoring

The system shall expose a primary CDM risk score/classifier selected from a transparent baseline family. The model output shall be accompanied by the training data version, model version, threshold, split description, and validation metrics.

### FR-04 — Telemetry anomaly scoring

The system shall expose an anomaly score for a bounded set of telemetry channels and identify the window/channels that contributed to the alert. The output shall be named an anomaly score, not a failure probability, unless separately validated.

### FR-05 — Explainability

The system shall show model feature attribution for the orbit model and channel/window evidence for telemetry. Explanations shall be labeled as attribution/evidence, not causal proof.

### FR-06 — Deterministic mission policy

The system shall map model outputs and input-quality findings to `GREEN`, `AMBER`, `RED`, or `INSUFFICIENT_DATA` through versioned, testable rules. No learned or LLM-generated policy is permitted in the MVP.

### FR-07 — Abstention

The system shall return `INSUFFICIENT_DATA` when mandatory data are missing, stale, contradictory, unsupported, or below the configured confidence/evidence requirements.

### FR-08 — Dashboard

The dashboard shall provide Mission Overview, Orbit Risk, Telemetry Health, and Decision Report screens, with a replayable scenario selector.

### FR-09 — Reporting

The system shall export JSON and Markdown. PDF export is optional after the core pipeline is stable. Reports shall contain inputs, timestamps, outputs, evidence, rule trace, provenance, limitations, and status.

### FR-10 — Reproducibility

Given the same fixture, configuration, model artifacts, and software version, the pipeline shall produce deterministic output within documented numerical tolerances.

## 7. Non-functional requirements

| Category | Requirement |
|---|---|
| Reproducibility | Fixed seeds, frozen manifests, versioned preprocessing/model/policy, deterministic replay. |
| Performance | Proposed target: a single assessment should feel interactive locally; exact budgets are finalized in Week 1. |
| Portability | CPU fallback for inference; RTX 4050 is an optimization, not a dependency for completion. |
| Explainability | Every non-green assessment exposes inputs, feature/channel evidence, threshold, and rule trace. |
| Safety | No autonomous command, maneuver vector, or flight-certification language. |
| Privacy | Use public/fixed/demo data only; do not require real mission telemetry. |
| Maintainability | Keep domain logic independent from Streamlit so it can be tested from the CLI. |
| Observability | Each run records run ID, input/model/policy versions, timestamps, status, and validation findings. |

## 8. MVP acceptance criteria

The MVP is accepted only when all Must requirements pass and the following are demonstrated:

- label audit completed for each selected dataset;
- no detected temporal/group leakage;
- fixed fixture replay is reproducible;
- missing/stale/contradictory inputs abstain correctly;
- orbit metrics include log-risk regression error, ranking correlation, tail retrieval, and calibration only if a separately audited probability target is approved;
- telemetry metrics include precision, recall, F1, false-alarm rate, and detection delay where labels or injected faults support them;
- every triage output has a deterministic rule trace;
- JSON and Markdown exports match the dashboard’s displayed assessment;
- limitations are visible in the UI and reports.

## 9. Explicit non-goals

- autonomous maneuver planning or execution;
- flight-certified collision avoidance or spacecraft health assessment;
- military targeting or weapons support;
- SAR, hyperspectral, Earth-observation image generation;
- a large multi-agent local LLM system;
- multi-user cloud operations, fleet-scale monitoring, or 3D orbit visualization;
- a mandatory LSTM, Transformer, or autoencoder.

## 10. Product risks

The highest risks are invalid labels, leakage, unsupported probability language, false alarms, misleading explanations, and scope drift. Each is addressed in [Evaluation and Acceptance](EVALUATION_AND_ACCEPTANCE.md), [Data and Labels](DATA_AND_LABELS.md), and [Safety and Limitations](SAFETY_AND_LIMITATIONS.md).
