# Six-Week Roadmap — VymoaGaurd PHM

## Delivery strategy

The roadmap prioritizes one validated replayable path. The baseline system is the completion line; optional deep learning and PDF packaging are cut first when the schedule is under pressure.

## Week 1 — Contract, data, and acceptance gates

**Deliverables**

- dataset manifests and checksums;
- label audit for CDM and selected telemetry dataset;
- normalized schemas and validation fixtures;
- chronological/group split strategy;
- leakage tests;
- operator decision contract;
- quantitative acceptance matrix;
- first fixed-fixture assessment schema.

**Exit gate:** a valid fixture can be validated and serialized. If labels do not support calibrated probability claims, update the product language to ranking/triage before modeling.

## Week 2 — Orbit baseline

**Deliverables**

- engineered CDM feature pipeline;
- transparent regression/ranking baseline for the audited continuous target;
- temporal holdout evaluation;
- initial threshold and class mapping;
- failure-case table.

**Exit gate:** the reproducible engineering path runs end-to-end; stronger model claims remain blocked until decision-time availability, leakage, baselines, uncertainty, and acceptance-threshold gates pass.

## Week 3 — Telemetry baseline and evaluation

**Deliverables**

- bounded telemetry channel selection;
- robust rolling statistics;
- Isolation Forest baseline;
- audited/injected-fault evaluation;
- anomaly window and channel localization;
- false-alarm and detection-delay analysis.

**Exit gate:** telemetry is either a validated secondary engine or explicitly labeled exploratory if the data cannot support stronger claims.

**Current result:** the frozen OPSSAT-AD v2 group-temporal holdout has 425 test segments. The robust baseline reaches ROC-AUC 0.6096, PR-AUC 0.3889, recall 0.9643, F1 0.5284, and false-alarm rate 0.8281 at the fixed exploratory threshold. Isolation Forest comparison reaches ROC-AUC 0.5502 and false-alarm rate 0.9263, so it is not fused into the canonical score. Threshold selection is explicitly not tuned on the locked holdout; alert workload, delay, and localization semantics remain unresolved. The telemetry capability remains explicitly exploratory; see [Phase 4 Telemetry Baseline](PHASE_4_TELEMETRY_BASELINE.md).

## Week 4 — Calibration, explanations, and policy

**Deliverables**

- probability calibration if supported;
- SHAP/feature attribution for orbit model;
- telemetry evidence rendering;
- deterministic policy implementation;
- abstention and contradictory-input behavior;
- rule-trace tests.

**Exit gate:** one JSON assessment contains both engine outputs, quality findings, policy state, and traceable evidence.

## Week 5 — Dashboard and exports

**Deliverables**

- Mission Overview screen;
- Orbit Risk screen;
- Telemetry Health screen;
- Decision Report screen;
- scenario selector and replay button;
- JSON/Markdown export;
- PDF only if low risk after core parity is proven.

**Exit gate:** dashboard and exports are generated from the same canonical assessment object.

**Phase 5 completion note:** the deterministic policy and evidence fingerprint are complete. Phase 6 must consume these fields without reimplementing policy logic or recasting review statuses as health or safety judgments.

## Week 6 — Hardening and presentation

**Deliverables**

- unit, data-contract, integration, leakage, and adversarial tests;
- golden replay artifacts;
- README and architecture diagram;
- screenshots and short demo script;
- limitations and failure-case documentation;
- optional model comparison if all gates already pass.

**Exit gate:** a clean-machine replay can be demonstrated without hidden manual steps.

## Scope fallback ladder

Cut in this order:

1. PDF packaging.
2. Optional autoencoder/LSTM/Transformer.
3. Compound scenario polish beyond one fixture.
4. Telemetry breadth; keep one bounded dataset/channel subset.
5. Boosted orbit model; keep the transparent continuous regression/ranking baseline.

Do not cut validation, abstention, provenance, policy trace, or deterministic JSON replay.

## Post-MVP options

- A contained sequence-model experiment with a pre-registered comparison.
- More telemetry channels/datasets after a data contract exists.
- Better operator usability testing.
- Additional report formats.
- Deployment hardening only after a new threat/reliability review.
