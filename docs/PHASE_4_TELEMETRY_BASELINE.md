# Phase 4 Telemetry Baseline - VymoaGaurd PHM

## Gate status

**Engineering gate: PASS.** The evaluator verifies the frozen OPSSAT-AD v2 `segments.csv` checksum, splits whole segments chronologically, fits channel baselines using nominal training rows only, scores a disjoint holdout, and emits strict JSON metrics.

**Model-validity gate: EXPLORATORY.** The result is useful for inspecting the data and the evidence path, but the false-alarm rate is too high for an operational triage claim. Telemetry scores remain anomaly scores; they are not failure probabilities, diagnoses, health percentages, or maneuver inputs.

## Reproduction

```text
python -m vymoa_guard_phm.evaluation.telemetry --segments data/downloads/opssat-ad/segments.csv --manifest data/manifests/esa_opssat_ad.yaml --output reports/generated/opssat-phase4-run.json
```

The CSV is downloaded locally and ignored by Git. The evaluator fails closed if the checksum or frozen manifest contract does not match.

## Frozen holdout result

| Measure | Robust rolling baseline | Isolation Forest comparison |
| --- | ---: | ---: |
| Dataset | OPSSAT-AD v2 | OPSSAT-AD v2 |
| Evaluation unit | 425 segments | 425 segments |
| Split | `group_temporal`; 1,698 train / 425 test segments | same holdout |
| Fit scope | nominal training rows only | nominal training rows only |
| Score type | `anomaly_score` | `anomaly_score` |
| ROC-AUC | 0.6096 | 0.5502 |
| PR-AUC | 0.3889 | 0.3546 |
| Recall at threshold 0.65 | 0.9643 | 0.9714 |
| F1 at threshold 0.65 | 0.5284 | 0.5037 |
| False-alarm rate | 0.8281 | 0.9263 |
| Runtime | 11.46 seconds | included in same run |

The robust baseline is selected because it has better held-out ranking and fewer false alarms. The threshold is still exploratory and is not an operational acceptance threshold.

### Descriptive threshold sweep

The sweep is descriptive only; no threshold was selected using the locked holdout.

| Threshold | Recall | F1 | False-alarm rate |
| ---: | ---: | ---: | ---: |
| 0.25 | 1.0000 | 0.4956 | 1.0000 |
| 0.50 | 0.9929 | 0.5027 | 0.9614 |
| 0.65 | 0.9643 | 0.5284 | 0.8281 |
| 0.75 | 0.9500 | 0.5407 | 0.7684 |
| 0.90 | 0.9000 | 0.5431 | 0.6947 |

## Evidence contract

Each scored telemetry assessment contains:

- `score_type: anomaly_score`;
- affected channel identifiers when evidence crosses the configured threshold;
- an anomaly window with start/end timestamps when evidence is localizable;
- robust-deviation and Isolation Forest comparison evidence;
- model and policy versions;
- an explicit statement that the output is not a failure probability.

The evaluation unit is a segment. Channel/window evidence is an explanation surface, not a validated fault-localization label. The current alert policy is one aggregate score per segment; it has no persistence, debounce, hysteresis, or detection-delay calculation.

## Review conclusions and next gates

- Keep the canonical score robust-statistics-only until channel-specific false-alarm controls, delay analysis, and slice stability are established.
- Retain Isolation Forest as a comparison path; do not promote it to the primary score without a new frozen evaluation.
- Add channel normalization and per-channel threshold selection only with a pre-registered holdout protocol.
- Add documented injected-fault tests if a labeled operational fault set is unavailable.
- Do not add an autoencoder in Phase 4; the current baseline has not cleared the practical false-alarm gate.
