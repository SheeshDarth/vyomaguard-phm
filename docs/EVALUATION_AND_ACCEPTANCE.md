# Evaluation and Acceptance Plan — VymoaGaurd PHM

## 1. Evaluation philosophy

Evaluation must measure whether the system supports cautious review, not whether it produces a compelling chart. Metrics are reported on frozen temporal holdouts and accompanied by prevalence, thresholds, failure cases, and data-quality behavior.

## 2. Acceptance matrix

The numeric targets below are proposed starting gates. Final values must be signed off after the Week 1 label audit; if the labels do not support a metric, the metric is marked not applicable and the product claim is reduced.

| Gate | Proposed initial target | Evidence |
|---|---:|---|
| Label validity | 100% of label-audit checklist complete; unresolved semantics block probability claims | Label-audit note and manifest |
| Leakage | 0 detected train/holdout overlap by event/group/time | Automated leakage test |
| Orbit regression | Report MAE/RMSE in source-defined base-10 log-risk units | Frozen event-temporal holdout report |
| Orbit ranking | Report Spearman/Kendall correlation and top-risk retrieval at the declared review load | Frozen event-temporal holdout report |
| Orbit probability calibration | Not applicable unless a separately audited binary target and probability claim are approved | Explicit claim decision and calibration artifact, if applicable |
| Telemetry detection | Provisional injected-fault/label recall ≥ 0.80 with false-alarm rate reported and capped by a Week 1 target | Fault manifest and holdout metrics |
| Detection delay | Report median and p95 delay; target must be agreed for the selected sampling/window semantics | Detection-delay table |
| Abstention safety | 100% of required malformed/stale/contradictory fixtures abstain as expected | Adversarial fixture tests |
| Replay reproducibility | Same fixture/config produces identical decision and stable numeric output within documented tolerance | Golden JSON comparison |
| Explanation presence | 100% of scored non-green assessments include feature/channel evidence and rule trace | Schema validation and UI test |
| Runtime | Provisional single assessment ≤ 1 s after model load; complete replay ≤ 30 s locally | Timed benchmark |
| Memory | No GPU-only dependency; target fits within available machine memory | Resource benchmark |
| Report parity | Dashboard and JSON derive from same canonical assessment object | Integration test |

The project does not pass by selectively reporting favorable metrics. Any failed gate must be visible in the report and triggers the fallback path in the roadmap.

## 3. Orbit risk metrics

- MAE and RMSE in source-defined base-10 log-risk units.
- Spearman/Kendall ranking correlation and top-k/tail retrieval at the declared review load.
- Error and ranking stability across temporal, event, missingness, and distribution-shift slices.
- Binary recall, confusion matrices, or calibration only after a separately audited binary target and threshold are approved.
- Slice analysis by time period, object/group, and missingness bucket where supported.

## 4. Telemetry metrics

- Precision, recall, and F1 on audited or injected fault windows.
- False-alarm rate on nominal windows.
- Detection delay from fault onset to first alert.
- Channel localization quality where ground truth identifies the affected channel.
- Alert duration/fragmentation so one fault does not become dozens of unhelpful alerts.

## 5. Failure analysis

Every validation run should retain examples of:

- false negatives at the high-risk threshold;
- false positives and their evidence;
- poorly calibrated probability bins;
- missed and delayed telemetry faults;
- noisy or intermittent channels;
- data-quality-triggered abstentions;
- model disagreement and threshold edge cases.

## 6. Model comparison rule

The model with the highest score is not automatically selected. The selected model must pass all mandatory gates, remain explainable, fit the runtime budget, and be reproducible. If a boosted or deep model does not clearly improve the agreed primary metric without regressions, keep the simpler baseline.

## 7. Verification checklist

Before the dashboard is considered demo-ready:

- [ ] Dataset manifests and checksums exist.
- [ ] Label semantics and supported claims are documented.
- [ ] Temporal/group splits are tested.
- [ ] Thresholds are frozen and versioned.
- [ ] Calibration is measured or explicitly not claimed.
- [ ] Telemetry labels/injections are documented.
- [ ] Adversarial input fixtures pass.
- [ ] Replay is deterministic.
- [ ] JSON/Markdown values match the UI.
- [ ] Limitations and non-certification notice are visible.
