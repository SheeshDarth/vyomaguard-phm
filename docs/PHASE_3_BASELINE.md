# Phase 3 Orbit Baseline - VymoaGaurd PHM

## Gate status

**Narrow engineering gate: PASS.** The checksum-verified local replay, source-order target selector, group-temporal split, train-only StandardScaler + Ridge pipeline, run bundle, and synthetic integration tests are working.

**Model-validity gate: BLOCKED.** The current result is retrospective research evidence only. Decision-time feature availability, post-decision leakage, target/censoring validity, and signed acceptance thresholds remain unresolved.

## Reproduction

```text
python -m vymoa_guard_phm.evaluation.orbit --archive data/downloads/esa-collision-avoidance/train_data.zip --output reports/generated/esa-orbit-phase3-run.json
```

The archive is ignored and must not be committed. The evaluator verifies the manifest SHA-256 before reading `train_data.csv` from the ZIP.

## Initial local holdout result

| Measure | Baseline result |
|---|---:|
| Dataset | ESA Collision Avoidance Challenge |
| Target | `risk`, continuous `base10_log_risk` |
| Split | `group_temporal`; 10,523 train events / 2,631 test events |
| Review population | 2,631 held-out event groups |
| Review load | 10% = 264 events |
| MAE | 6.7165 log-risk units |
| RMSE | 8.8937 log-risk units |
| Spearman ranking | 0.4484; bootstrap 95% interval 0.4071–0.4737 |
| Top-risk recall | 0.1477; bootstrap 95% interval 0.1136–0.1933 |
| Constant-target top-risk recall | 0.1439 |
| Runtime | 6.89 seconds on the local machine |

The score is a normalized `ranking_score`; it is not a probability, confidence, collision likelihood, maneuver recommendation, or flight-safety assessment. The baseline’s small improvement over the constant comparator is not an acceptance result.

## Required next gates

- field-level decision-time feature and write-time provenance audit;
- post-decision, target-proxy, duplicate, same-asset, and same-scenario leakage tests;
- explicit target/censoring validity review for source-order final-row selection;
- constant and naive temporal comparators with pre-registered practical thresholds;
- slice analysis and confidence intervals across time/order, data quality, and event regimes;
- clean-environment replay of the run bundle, including model artifact and split/prediction hashes.

No stronger model, probability terminology, telemetry fusion, deployment claim, or autonomous action path is authorized by this result.
