# Technical Requirements Document — VymoaGaurd PHM

## 1. Technical objective

Implement a local Python system whose deterministic core can be invoked from a CLI replay and surfaced through Streamlit. The core must remain usable without the UI so that data, models, policy, and reporting can be tested independently.

## 2. Proposed stack

| Concern | Proposed technology | Decision status |
|---|---|---|
| Language | Python | Source-backed |
| Tabular/data processing | Pandas, NumPy | Source-backed |
| Baseline ML | scikit-learn | Source-backed |
| Candidate boosted model | XGBoost or LightGBM | Source-backed; select after baseline gates |
| Optional sequence model | PyTorch | Source-backed; non-blocking experiment |
| Feature attribution | SHAP | Source-backed; label as attribution |
| Charts | Plotly | Source-backed |
| UI | Streamlit | Source-backed |
| Local storage | SQLite or Parquet | Source-backed; use both only if justified |
| Reports | JSON, Markdown; PDF after core | PRD decision |

## 3. Component requirements

### 3.1 Dataset adapters

- Accept explicit dataset manifests rather than hidden downloads.
- Record source name, version/snapshot, source URI, acquisition date, license/usage note, primary and artifact-level checksums, and schema revision.
- Separate raw immutable files from normalized feature tables.
- Fail with a typed validation error when the input is not supported.

### 3.2 Validation and quality gates

Validation shall run before feature engineering and produce structured findings:

```json
{
  "status": "PASS|WARN|FAIL",
  "code": "MISSING_REQUIRED_FIELD",
  "severity": "info|warning|error",
  "field": "string|null",
  "message": "human-readable explanation"
}
```

Required checks: schema, nulls, timestamp order, duplicate event IDs, stale timestamps, unsupported ranges, contradictory values, and train/test overlap.

### 3.3 Feature pipeline

- Fit transformations only on the training partition.
- Persist the feature schema and transformation version.
- Keep raw field names alongside human-readable display labels.
- Record missing-value imputation and scaling decisions.
- Prevent target-derived or future-window fields from entering training features.

Feature names are dataset-dependent. The data contract must not assume a field exists just because it is common in aerospace data; the label audit must confirm availability first.

### 3.4 Orbit risk engine

The audited ESA target is continuous base-10 log risk, so the baseline shall be a transparent regression/ranking model. A classifier is permitted only if a separate binary target and threshold are pre-registered from the label audit. A gradient-boosted model may replace the baseline only if it passes the same frozen group-temporal holdout gates and improves the agreed objective without unacceptable explanation regressions.

Required output:

```json
{
  "score_type": "calibrated_probability|ranking_score",
  "score": 0.0,
  "risk_class": "SAFE|MONITOR|REVIEW",
  "threshold_version": "string",
  "top_features": [
    {"name": "string", "value": 0.0, "attribution": 0.0, "direction": "raises|lowers|unknown"}
  ],
  "model_version": "string",
  "evaluation_reference": "string"
}
```

If the label audit does not support calibration, the field must use `ranking_score` and the UI/report must not call it probability or confidence.

### 3.5 Telemetry anomaly engine

The baseline shall combine robust rolling statistics with Isolation Forest over a bounded channel subset. It shall return anomaly score, affected channels, contiguous anomaly windows, threshold version, and evaluation reference. An autoencoder is permitted only as a non-blocking comparison after the baseline is evaluated on held-out/injected faults.

### 3.6 Mission decision policy

The policy shall be a pure function of orbit output, telemetry output, data-quality findings, freshness, and policy configuration. It shall emit status, reason codes, human-readable rule trace, and policy version. It shall not calculate a combined probability in the MVP.

### 3.7 Report generator

Reports shall be generated from the same `MissionAssessment` object rendered by the dashboard. This prevents dashboard/report divergence. JSON is canonical; Markdown is a human-readable projection; PDF is a packaging layer.

### 3.8 Dashboard

The Streamlit app shall call the domain pipeline through a thin adapter. UI code shall not contain model thresholds or business rules. A scenario selector and “replay assessment” action are required for the demo.

## 4. Data model

Core records:

| Record | Purpose |
|---|---|
| `DatasetManifest` | Dataset identity, source URI, primary/artifact checksums, license note, schema/version, acquisition metadata. |
| `InputWindow` | Validated CDM or telemetry slice used for one assessment. |
| `FeatureSnapshot` | Model-ready features and transformation metadata. |
| `OrbitAssessment` | Orbit score/class, attribution, model and threshold versions. |
| `TelemetryAssessment` | Anomaly score, channels/windows, threshold and evaluation metadata. |
| `DecisionAssessment` | Status, reason codes, rule trace, abstention state, policy version. |
| `MissionAssessment` | Immutable envelope joining the above with run and provenance metadata. |

Every record must carry or inherit `run_id`, `created_at`, `source_manifest_id`, `model_version`, and `policy_version`.

## 5. Integration contracts

The seams are:

```text
DatasetAdapter -> Validator -> FeatureBuilder
FeatureBuilder -> OrbitRiskEngine
FeatureBuilder -> TelemetryAnomalyEngine
OrbitRiskEngine + TelemetryAnomalyEngine + QualityFindings -> DecisionPolicy
MissionAssessment -> ReportRenderer
MissionAssessment -> StreamlitViewModel
```

No component should import Streamlit. No model should call the policy layer to mutate thresholds. Configuration is read-only during assessment.

## 6. Reliability and performance targets

These are proposed starting targets, not source-backed facts; finalize them after the Week 1 dataset/label audit:

- deterministic replay: identical fixture/config produces identical status, rule trace, and stable numeric output within documented tolerance;
- data-quality safety: 100% of malformed/stale/contradictory fixture cases produce the expected validation status and abstention;
- local inference: target interactive response for a single assessment and a complete replay within 30 seconds;
- memory: target operation within the RTX 4050 machine’s available memory without requiring GPU-only features;
- report parity: exported JSON and dashboard values are generated from the same assessment object;
- graceful degradation: if an optional model is unavailable, the validated baseline remains runnable.

## 7. Test strategy

- Unit tests for feature transforms, thresholding, policy precedence, abstention, and report serialization.
- Data-contract tests for each adapter and fixture.
- Leakage tests for temporal/group overlap and fit-on-train-only transforms.
- Model tests for deterministic seeds, calibration artifact presence, and schema compatibility.
- Integration tests for end-to-end replay and dashboard-to-domain parity.
- Adversarial fixtures for missing, stale, contradictory, out-of-range, and model-disagreement inputs.
- Golden-file tests for canonical JSON and Markdown report shape.

## 8. Technical tradeoffs

| Decision | Chosen direction | Alternative | Why |
|---|---|---|---|
| Model ambition | Baseline first | Mandatory LSTM/Transformer | Protects validation and schedule. |
| Cross-domain combination | Rule-based evidence policy | Probability fusion | Avoids unvalidated statistical claims. |
| Storage | Local Parquet/SQLite | Cloud database | Fits solo, offline demo scope. |
| UI coupling | Thin Streamlit adapter | Rules in UI callbacks | Keeps domain logic testable. |
| PDF | Post-core packaging | Required from day one | Avoids spending time on document layout before correctness. |
