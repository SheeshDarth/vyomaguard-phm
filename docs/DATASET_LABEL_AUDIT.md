# Dataset and Label Audit - VymoaGaurd PHM

**Audit date:** 2026-07-22
**Phase:** 2 - Dataset acquisition and label audit
**Repository rule:** downloaded artifacts remain in ignored `data/downloads/` and are not committed.

## Decision summary

- **Orbit:** use the ESA Collision Avoidance Challenge training archive for a continuous final-risk regression/ranking task. Do not call the target a binary collision label or calibrated collision probability.
- **Telemetry:** use OPSSAT-AD v2 as the primary telemetry dataset. Use `segments.csv` for timestamped channel/window evidence and `dataset.csv` only as a companion segment-level feature table.
- **Fallback:** NASA SMAP/MSL is not acquired because OPSSAT-AD provides a public, satellite-specific binary anomaly label and raw temporal segments.

## Orbit dataset audit

Source: [ESA Collision Avoidance Challenge data page](https://kelvins.esa.int/collision-avoidance-challenge/data/) and [challenge description](https://kelvins.esa.int/collision-avoidance-challenge/challenge/).

| Item | Audited value |
|---|---|
| Artifact | `train_data.zip` containing `train_data.csv` |
| Local size | 87,718,091 bytes |
| SHA-256 | `68362fe5629cc80f17291f2d73f733bf4e922675e37b91a8ee79afadb46f3edc` |
| Rows / columns | 162,634 / 103 |
| Group key | `event_id` |
| Event groups | 13,154 |
| Rows per event | 1 to 23; mean 12.36 |
| Temporal field | `time_to_tca`, ranging from -0.1498 to 6.9938 days |
| Target | `risk`, a continuous base-10 log risk value |
| Final target semantics | source-defined risk in the final row of each event time series |
| Ordering finding | 12,929 groups are monotonically decreasing in `time_to_tca`; 225 are increasing. Preserve source row order and test ordering assumptions rather than silently sorting every group. |

The challenge page describes the `risk` column as a self-computed value at each CDM epoch and asks competitors to predict the final risk for an event. Therefore, binary-classification wording is not supported by the audited target. Phase 3 must use the machine-readable [ESA orbit target contract](../data/ESA_ORBIT_TARGET_CONTRACT.yaml) and a regression/ranking baseline; a classifier would require a separately documented binary ground truth and pre-registered threshold.

The feature manifest excludes `risk`, `event_id`, and `mission_id` from predictors. `event_id` and `mission_id` remain grouping/provenance fields.

## Telemetry dataset audit

Source: [OPSSAT-AD v2 on Zenodo](https://zenodo.org/records/15108715), DOI `10.5281/zenodo.15108715`.

The Zenodo record identifies the dataset as an AI-ready benchmark built from OPS-SAT telemetry, provides `segments.csv` and `dataset.csv`, and lists a CC BY 4.0 license.

| Item | `segments.csv` | `dataset.csv` |
|---|---:|---:|
| Size | 18,987,091 bytes | 507,550 bytes |
| SHA-256 | `d5201e9e751eb2a53a0ff7c11567dc4239f594ea4b479b2aa66fe67ddcbcb9ba` | `b524177da6f516d5c9f63c7acbc385341f0ad42046ef20c1bed2d25e51b98f02` |
| Rows / columns | 303,493 / 8 | 2,123 / 23 |
| Group key | `segment` + `channel` | `segment` |
| Label | binary `anomaly` field | binary `anomaly` field |
| Time field | `timestamp` | not present |
| Channels | 9 | 9 |

Additional findings:

- `anomaly` has 203,229 nominal rows and 100,264 anomaly rows.
- There are 2,123 segments and no segment mixes the provided `train` flag or `anomaly` label.
- `label` is a constant category string (`anomaly`) and is excluded from predictors and targets.
- `segments.csv` is required for anomaly-window evidence; the derived feature table alone cannot satisfy the telemetry time-window requirement.
- Split at the segment level before fitting transforms or evaluating row-level alerts; the manifest and [OPSSAT telemetry contract](../data/OPSSAT_TELEMETRY_CONTRACT.yaml) therefore use `group_temporal`.

## Phase 2 gate

**PASS for local dataset onboarding:** both selected artifacts are downloaded, checksummed, schema-audited, and represented by frozen manifests.
**Not yet a model gate:** Phase 3 must implement the orbit continuous-target decision and the telemetry segment-level split/evaluation before training claims are made.

No real mission data, credentials, or downloaded artifacts are committed to the public repository.
