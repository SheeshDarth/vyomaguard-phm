# Safety, Responsible Framing, and Limitations

## 1. System classification

VymoaGaurd PHM is a research/portfolio prototype for mission-assurance decision support. It is not flight software, a certified collision-avoidance system, a spacecraft health monitor, or an autonomous operations tool.

## 2. Prohibited claims

Do not claim that the system:

- guarantees collision avoidance or spacecraft safety;
- predicts a physical collision without a validated target definition;
- diagnoses a subsystem failure from an anomaly score;
- produces a probability of failure by combining two unrelated model scores;
- recommends or executes a maneuver;
- is flight-certified, operationally qualified, or suitable for real mission decisions;
- supports military targeting or weapons decisions.

## 3. Required language

Prefer:

- “calibrated conjunction-risk classification under the selected dataset’s label definition”;
- “telemetry anomaly score”;
- “feature attribution” rather than “causal explanation”;
- “human review state” or “triage” rather than “command”;
- “insufficient data” rather than forcing a prediction.

## 4. Known limitations

- Public datasets may not represent current operational missions, sensor configurations, or data latency.
- A challenge-provided label may not mean physical collision probability.
- Anomaly datasets may have incomplete or synthetic fault coverage.
- Thresholds are design choices tied to data, prevalence, and review capacity.
- SHAP or other attributions describe model behavior; they do not establish causality.
- Rule-based compound states are not statistically calibrated joint risk.
- The dashboard cannot replace flight dynamics analysis, telemetry expertise, or approved flight rules.

## 5. Misuse controls

- Use public, synthetic, or de-identified fixtures only.
- Keep scoring local by default; do not add network ingestion without a new security review.
- Keep export banners and report disclaimers intact.
- Do not place secrets or real mission telemetry in notebooks, fixtures, screenshots, or version control.
- Require a user to inspect evidence and rule trace before export.
- Make `INSUFFICIENT_DATA` a normal visible outcome, not an exception hidden from the user.

## 6. Failure response

If validation fails, a dataset is not label-valid, or a model fails a gate:

1. preserve the failed run and its evidence;
2. mark the metric/claim as failed or unsupported;
3. fall back to the simpler validated path;
4. update the report and documentation;
5. do not tune thresholds only to make the dashboard look better.
