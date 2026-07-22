# Decision Log — VymoaGaurd PHM

## DL-001 — Use evidence-first scope

**Decision:** Make the product a reproducible evidence cockpit, not a model showcase.  
**Rationale:** The source brief’s differentiation is the combination of aerospace datasets, explainability, deterministic policy, dashboard, and exportable report. The council found that validation and traceability create more credibility than mandatory deep learning.

## DL-002 — Make conjunction risk primary

**Decision:** The orbit-risk pipeline is the primary validated capability; telemetry is secondary and bounded.  
**Rationale:** This gives the six-week build a clear completion line and avoids presenting two equally deep research projects.

## DL-003 — Deep learning is optional

**Decision:** LSTM/Transformer/autoencoder experiments may run only after baseline gates pass.  
**Rationale:** Deep learning is not allowed to determine whether the MVP ships.

## DL-004 — Use deterministic triage, not maneuver advice

**Decision:** Emit `GREEN`, `AMBER`, `RED`, or `INSUFFICIENT_DATA` with a rule trace.  
**Rationale:** The prototype must not imply flight authority, autonomous action, or a combined probability unsupported by the data.

## DL-005 — Freeze the acceptance matrix first

**Decision:** Week 1 must finalize label semantics, temporal splits, leakage checks, abstention behavior, runtime budget, and quantitative model gates.  
**Rationale:** All five council advisors missed this initially; all peer reviewers identified it as the key blind spot.

## DL-006 — Probability language is conditional

**Decision:** Use calibrated probability only after label validity and calibration evidence are established. Otherwise use ranking/triage language.  
**Rationale:** A public dataset label may not support a physical collision-probability claim.

## DL-007 — Local MVP

**Decision:** Use local Parquet/SQLite and Streamlit with CPU-compatible inference.  
**Rationale:** This matches the solo-build and RTX 4050 constraints and keeps deployment scope bounded.

## DL-008 - Freeze audited dataset choices and target semantics

**Decision:** Use the ESA Collision Avoidance Challenge archive for a continuous final-risk regression/ranking task and OPSSAT-AD v2 `segments.csv` for supervised telemetry anomaly detection with segment-level grouping.

**Rationale:** The ESA source defines `risk` as a continuous base-10 log value at the final CDM, not a binary collision outcome. OPSSAT-AD supplies binary anomaly labels, timestamped raw segments, and a documented train split. The decision prevents unsupported probability claims and preserves telemetry window evidence.

## DL-009 - Separate frozen data provenance from the modeling contract

**Decision:** Freeze source URIs, artifact hashes, label definitions, and grouping metadata now, but keep feature availability, split assignments, evaluation thresholds, and public model claims provisional until Phase 3 independently reproduces them.

**Rationale:** The Phase 2 architecture review found that dataset identity alone does not prove decision-time availability or leakage-free modeling. The repository now has machine-readable target contracts, source-order final-CDM selection with explicit tie handling, canonical `group_temporal` manifests, and a transparent continuous regression/ranking slice. Phase 3 must add runtime artifact verification, manifest-driven feature allowlists, pre-registered metrics, and replay evidence before any model claim is frozen.
