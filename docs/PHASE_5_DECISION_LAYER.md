# Phase 5 Decision Layer - VymoaGaurd PHM

## Gate status

**Engineering gate: PASS.** The policy is a pure deterministic function with explicit precedence, bounded score semantics, optional-telemetry behavior, conservative disagreement handling, stable reason codes, and a terminal rule trace on every return path.

**Operational safety gate: PASS for abstention behavior; not a flight-authority claim.** Invalid, unavailable, stale, contradictory, or unsupported evidence cannot silently become `GREEN`. The policy produces human review actions only and does not calculate a joint probability or issue maneuver commands.

## Canonical flow

```text
quality failure
  -> INSUFFICIENT_DATA / REQUEST_DATA
valid configuration
  -> score type, finite value, and [0, 1] checks
required telemetry available
  -> high telemetry requires channels + start/end window
orbit class agrees with score
  -> compound/high orbit/high telemetry/borderline/disagreement/green precedence
every path
  -> reason codes + POL-100 terminal rule trace + policy version
```

## Verified cases

| Case | Result |
|---|---|
| Nominal fixture | `GREEN` / `NO_ALERT` |
| Conjunction-risk fixture | `RED` / `CONJUNCTION_REVIEW` |
| Telemetry-anomaly fixture | `AMBER` / `SUBSYSTEM_INVESTIGATION` |
| Malformed/stale/contradictory fixture | `INSUFFICIENT_DATA` / `REQUEST_DATA` |
| High telemetry without channel/window evidence | `INSUFFICIENT_DATA` |
| Non-finite or out-of-range score | `INSUFFICIENT_DATA` |
| Invalid threshold ordering | `INSUFFICIENT_DATA` |
| Optional telemetry unavailable with high orbit | `RED` / `CONJUNCTION_REVIEW`, with `TELEMETRY_UNAVAILABLE_OPTIONAL` |
| Optional telemetry unavailable with low orbit | `AMBER` / `MONITOR`; `GREEN` is not permitted |
| Orbit score/class disagreement | `AMBER` / `MONITOR` |

The policy remains deterministic and evidence-first. `GREEN` means no configured trigger was crossed with required evidence present; it does not mean the spacecraft is safe.

## Remaining scope

- Phase 6 must render the canonical `MissionAssessment` without duplicating policy logic in Streamlit.
- Phase 7 must add golden rule-trace fixtures, dashboard smoke tests, and clean-machine replay.
- No policy output is a collision probability, failure diagnosis, certification, or maneuver command.
