# VymoaGaurd PHM — Project Overview

## 1. Executive summary

VymoaGaurd PHM is a local, explainable mission-assurance prototype for satellite operators. It combines:

- **External orbital risk:** a conjunction-data model estimates the risk class of a potential close approach.
- **Internal spacecraft health:** a telemetry model identifies abnormal channel behavior and affected time windows.
- **Operator decision support:** a deterministic policy converts evidence into a triage state and explains why.

The project is designed as a credible solo build on an RTX 4050, not as production flight software. The strongest demonstration is a replayable chain from fixed input data to model evidence, decision rules, and an exportable report.

## 2. Product identity

**Name:** VymoaGaurd PHM  
**Positioning:** A solo-built space mission-assurance prototype for explainable conjunction-risk classification, telemetry anomaly detection, and operator triage.  
**Primary audience:** reviewers, internship interviewers, and technically curious mission-operations stakeholders.  
**Secondary audience:** developers who want to inspect the data, model, policy, and evidence chain.

The product should feel like a compact operations evidence cockpit rather than a collection of unrelated notebooks.

## 3. Core operator question

> What requires attention now, why does it require attention, and what is the next safe review step?

The system must answer that question with evidence and uncertainty. It must not pretend to replace a flight dynamics team, flight rulebook, or certified mission-control system.

## 4. User journey

1. The user selects a fixed replay scenario or loads a validated CDM and telemetry window.
2. Input validation reports freshness, missingness, schema errors, and contradictions.
3. The orbit engine returns a risk score/class and feature attributions.
4. The telemetry engine returns an anomaly score, affected channels, and an anomaly window.
5. The decision layer applies explicit rules and returns a triage state plus rule trace.
6. The user inspects the timeline, evidence, explanations, provenance, and limitations.
7. The user exports the same assessment as JSON, Markdown, or optional PDF.

## 5. Scope at a glance

| Area | MVP commitment | Deliberately deferred |
|---|---|---|
| Orbit | CDM feature pipeline and one validated classifier | 3D visualization, autonomous maneuver planning |
| Telemetry | One public dataset, bounded channels, baseline anomaly detector | Broad fleet monitoring, many spacecraft at once |
| Decision support | Deterministic triage and evidence trace | Learned policy, LLM-generated safety advice |
| Explainability | Feature attribution and rule trace | Causal claims, natural-language rationale without evidence |
| Dashboard | Four screens and replay flow | Multi-user operations, cloud deployment |
| Reporting | JSON and Markdown required; PDF after core | Certified operational record system |
| Modeling | Baselines first; deep model only if it passes gates | Model zoo or mandatory Transformer/LSTM |

## 6. Key concepts

- **Conjunction risk:** a model output about a CDM event under the dataset’s label definition. It is not a physical guarantee.
- **Telemetry anomaly:** a score indicating unusual behavior relative to the selected training/reference data. It is not automatically a failure probability.
- **Evidence:** input values, feature values, attributions, anomaly channels/windows, thresholds, data-quality findings, and provenance.
- **Triage:** a deterministic review state: `GREEN`, `AMBER`, `RED`, or `INSUFFICIENT_DATA`.
- **Abstention:** refusing to make a substantive assessment when inputs are missing, stale, contradictory, outside supported bounds, or too uncertain.

## 7. Proposed implementation sequence

The original brief sequences data, models, dashboard, and polish across six weeks. This design inserts a label audit, acceptance matrix, and replay artifact before UI work. See [Roadmap](ROADMAP.md).

## 8. Source and assumptions

Everything directly stated about the product comes from `VymoaGaurd_PHM_Project_Brief.md`. The following are design assumptions proposed for implementation and must be confirmed during Week 1:

- the selected CDM dataset contains a defensible target or supports a defensible ranking/triage framing;
- one telemetry dataset can supply labels or support injected-fault evaluation;
- data can be stored locally as immutable raw inputs plus normalized Parquet/SQLite tables;
- the app is single-user and local for the MVP;
- proposed performance and model gates are achievable on the available RTX 4050 and CPU fallback.
