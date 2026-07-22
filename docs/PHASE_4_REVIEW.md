# Phase 4 Deep Review - VymoaGaurd PHM

## Review outcome

**Repository/engineering acceptance: PASS.** The Phase 4 increment is reproducible, lint-clean, test-covered, bounded to the audited OPSSAT-AD contract, and safe to publish as research software.

**Operational/model-validity acceptance: EXPLORATORY.** The frozen holdout false-alarm rate is 0.8281 for the selected robust score and 0.9263 for the Isolation Forest comparison. The current result does not support a validated detector, mission-assurance claim, failure probability, diagnosis, or alerting policy.

## Architecture review

### Strengths

- The evaluator is separated from the model and uses explicit manifest/checksum validation.
- Whole segments are split chronologically, and nominal training rows are used for baseline fitting.
- The canonical output retains anomaly-score semantics, affected channels, windows, model versions, threshold version, and limitations.
- Isolation Forest is computed as a comparison path and is not silently fused into the operator-facing score.
- The bounded nine-channel implementation runs within the existing 30-second complete-replay target; the latest local run took 11.46 seconds.
- Refit clears prior per-channel models, preventing stale model state from crossing datasets.

### Risks retained intentionally

- Labels are segment-level while channel/window evidence is row-level. Localization is therefore evidence for review, not a validated ground-truth explanation.
- Threshold `0.65` is a fixed configuration value and is explicitly not selected on the locked holdout. It is not an operational threshold.
- The current alert policy aggregates one score per segment and has no persistence, debounce, hysteresis, or detection-delay semantics.
- Missing/irregular sampling, timestamp disorder, stuck channels, warm-up behavior, and distribution drift need dedicated failure-mode tests.

## Council review

Five advisors, five anonymous peer reviews, and a chairman converged on the same decision: push the increment as an exploratory research snapshot; keep robust rolling statistics canonical; retain Isolation Forest as a comparison; and block operational claims until threshold provenance, alert burden, latency, score/label alignment, and failure-mode behavior are formalized.

## Required next gate

Define a pre-registered segment-level cost-sensitive acceptance contract on a temporal validation subset, including maximum nominal alarm burden, minimum recall, maximum delay, localization scope, and persistence behavior. Then rerun the untouched holdout and keep the current exploratory result for comparison.
