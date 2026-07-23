# Glossary — VymoaGaurd PHM

| Term | Meaning in this project |
|---|---|
| CDM | Conjunction Data Message: the event data used by the orbit-risk module. |
| Conjunction | A close-approach event between tracked objects; this prototype scores the dataset’s defined event target. |
| Triage | A review state that prioritizes attention; it is not an operational command. |
| Risk class | A bucket such as safe/monitor/review derived from the orbit model threshold. |
| Calibrated probability | A score whose numeric interpretation is checked against observed outcomes; use only if labels support it. |
| Ranking score | A score useful for ordering cases when probability semantics are not defensible. |
| Anomaly score | A measure of unusual telemetry behavior relative to a reference population; not automatically a failure probability. |
| Feature attribution | A model-behavior explanation showing which inputs moved a prediction; not causal proof. |
| Low ranking tier | A ranking-score label below the configured monitor threshold; it is not a safety determination. |
| Data-quality gate | A pre-scoring rule that checks whether the system has adequate, valid evidence. |
| Abstention | Returning `INSUFFICIENT_DATA` instead of forcing a substantive prediction. |
| Temporal holdout | A test partition later in time than training data, used to reduce leakage and measure time generalization. |
| Injected fault | A documented synthetic fault added to nominal telemetry for controlled evaluation when real labels are incomplete. |
| Replay | Re-running a fixed scenario to verify deterministic behavior and demonstrate the product. |
| Mission-assurance prototype | A non-certified tool that organizes evidence and review signals around mission risk. |
