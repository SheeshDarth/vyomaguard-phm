# Data and Labels Plan — VymoaGaurd PHM

## 1. Purpose

This document prevents the model from making stronger claims than the data supports. Dataset choice, target semantics, split strategy, and provenance are implementation gates, not cleanup work.

The completed initial audit is recorded in [Dataset and Label Audit](DATASET_LABEL_AUDIT.md). The current selections are ESA Collision Avoidance Challenge for orbit risk and OPSSAT-AD v2 for telemetry.

## 2. Candidate datasets from the source brief

| Signal | Candidate | Required Week 1 decision |
|---|---|---|
| Conjunction/orbit risk | ESA Collision Avoidance Challenge dataset | Confirm event labels, time ordering, duplicate/event grouping, and usable features. |
| Telemetry anomaly | ESA OPSSAT-AD | Prefer if labels, channel metadata, and licensing/format support the evaluation plan. |
| Telemetry anomaly fallback | NASA SMAP/MSL anomaly detection dataset | Use if it gives clearer labels or a more reproducible anomaly protocol. |

The final dataset choice must be recorded in a manifest with source, version/snapshot, source URI, primary checksum, artifact-level checksums, license/usage note, acquisition date, schema version, and preprocessing revision. The current machine-readable target contracts are [ESA orbit target](../data/ESA_ORBIT_TARGET_CONTRACT.yaml) and [OPSSAT telemetry](../data/OPSSAT_TELEMETRY_CONTRACT.yaml).

## 3. Label audit

Before model training, produce a short label-audit note answering:

- What exactly is a positive orbit event?
- Is the target a physical outcome, a challenge-provided label, a ranking target, or a proxy?
- Is the target available before the prediction time?
- Are repeated CDMs from the same conjunction or object grouped?
- Does the telemetry dataset identify anomaly onset, duration, affected channel, or only an event label?
- Can injected faults be constructed without changing the evaluation semantics?
- Are labels consistent across time, object, subsystem, and data source?
- Does the data support calibrated probability, or only ranking/triage?

If the answer is unclear, the UI and reports must use `ranking_score` or `anomaly_score` and avoid probability/confidence language.

## 4. Canonical manifest

```yaml
dataset_id: string
source_name: string
source_snapshot: string
source_uri: string
acquired_at: timestamp
checksum: sha256
artifact_checksums: [filename=sha256]
license_note: string
schema_version: string
label_definition: string
time_field: string
entity_fields: [string]
feature_fields: [string]
excluded_fields: [string]
split_strategy: temporal|group_temporal|other
notes: string
```

## 5. Normalized input shapes

### CDM event/window

The normalized record should preserve the original source fields and add only derived metadata:

```text
event_id
primary_object_id
secondary_object_id (if present)
event_time / time_of_closest_approach (if present)
observation_time (if present)
source_row_id
raw_payload_reference
label (only if audited)
derived_feature_namespace
```

The exact aerospace feature names are dataset-dependent. A field must not be invented, aliased, or silently dropped without being listed in the feature manifest.

### Telemetry window

```text
window_id
spacecraft_or_source_id (if present)
channel_id
timestamp
value
source_row_id
anomaly_label (only if audited)
fault_window_reference (if injected)
```

## 6. Split strategy

- Use chronological splits by event/observation time.
- Group related CDMs or repeated conjunction observations so the same event does not cross train and holdout.
- Keep the final temporal holdout untouched until model and threshold selection are frozen.
- Fit imputers, scalers, encoders, and calibration transforms only on training data.
- Do not use future telemetry windows, post-event labels, or downstream decision fields as predictors.
- For ESA orbit data, select the last occurrence of each `event_id` in immutable source-row order. Do not sort by `time_to_tca`; the contract uses `source_row_index` as the tie-breaker.

## 7. Telemetry evaluation modes

Use the strongest evaluation mode the selected dataset supports:

1. **Ground-truth mode:** use audited anomaly labels with precision, recall, F1, false-alarm rate, and detection delay.
2. **Injected-fault mode:** inject documented faults into nominal windows, retain the untouched nominal data for false-alarm analysis, and report injection parameters.
3. **Exploratory mode:** if neither labels nor defensible injections are possible, call the feature exploratory anomaly visualization and do not claim validated anomaly detection.

## 8. Data quality behavior

| Finding | Required behavior |
|---|---|
| Missing required field | Fail validation; `INSUFFICIENT_DATA`. |
| Stale input | Warn or abstain according to configured freshness policy; show age. |
| Contradictory timestamps/identifiers | Abstain; preserve the contradiction in report. |
| Unsupported range/unit | Fail validation unless normalized with recorded conversion. |
| Unknown channel or object | Score only if the manifest explicitly permits it; otherwise abstain. |
| Model disagreement | Keep both outputs visible and use conservative policy state. |

## 9. Data security and reproducibility

Use public or synthetic fixtures only for the MVP. Never add real mission telemetry to the repository. Store checksums and manifests, avoid credentials in notebooks/config, and document any downloaded data outside version control.
