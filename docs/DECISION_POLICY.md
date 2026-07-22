# Mission Decision Policy — VymoaGaurd PHM

## 1. Purpose

The decision layer translates model evidence into a review state. It is deterministic, versioned, and inspectable. It does not issue commands, choose a maneuver, or create a combined probability of mission failure.

## 2. Inputs

- Orbit risk output: score semantics, class, calibration/evaluation status, top feature attributions.
- Telemetry output: anomaly score, threshold, affected channels, anomaly windows, evaluation status.
- Data quality: missingness, freshness, contradictions, unsupported ranges, out-of-distribution indicators if implemented.
- Policy configuration: thresholds, freshness limits, supported dataset/model versions, and precedence rules.
- Model agreement/disagreement and abstention flags.

## 3. Output contract

```json
{
  "status": "GREEN|AMBER|RED|INSUFFICIENT_DATA",
  "review_action": "NO_ALERT|MONITOR|SUBSYSTEM_INVESTIGATION|CONJUNCTION_REVIEW|MISSION_CRITICAL_REVIEW|REQUEST_DATA",
  "reason_codes": ["string"],
  "rule_trace": [
    {"rule_id": "POL-001", "result": "true", "evidence": "string"}
  ],
  "abstained": false,
  "policy_version": "string"
}
```

`review_action` is a human review suggestion, not an autonomous operational command.

## 4. Precedence rules

Rules are evaluated in this order:

1. **Data-quality gate:** mandatory failure, stale/contradictory input beyond policy, unsupported schema, or missing required evidence → `INSUFFICIENT_DATA` / `REQUEST_DATA`.
2. **Evidence availability:** a model that is unavailable, uncalibrated where calibration is required, or outside its supported manifest → `INSUFFICIENT_DATA`.
3. **High conjunction risk:** a validated high-risk orbit output → at least `RED` / `CONJUNCTION_REVIEW`.
4. **High telemetry anomaly:** a validated high-severity telemetry output with channel/window evidence → at least `AMBER` / `SUBSYSTEM_INVESTIGATION`.
5. **Compound evidence:** high orbit risk plus high telemetry anomaly → `RED` / `MISSION_CRITICAL_REVIEW`, with both evidence streams shown separately.
6. **Low/normal evidence:** complete, fresh inputs with no thresholds crossed → `GREEN` / `NO_ALERT`.
7. **Uncertainty/disagreement:** conflicting models, edge-of-threshold values, or insufficient evaluation support → conservative `AMBER` / `MONITOR` unless the data-quality gate requires abstention.

The exact numeric thresholds are configuration, not hard-coded in the UI. They are frozen and versioned after evaluation.

### Implemented Phase 5 guards

The implementation adds these deterministic gates before threshold-based triage:

- `POL-001`: any validation failure abstains;
- `POL-002`: policy thresholds must be finite, bounded, and ordered;
- `POL-003`: orbit output must be a finite `[0, 1]` `ranking_score`;
- `POL-004`: required telemetry must be a finite `[0, 1]` `anomaly_score`; optional telemetry may be unavailable;
- `POL-007`: a high telemetry score must include affected channels and a start/end anomaly window;
- `POL-008`: score-derived orbit class disagreement produces conservative monitoring;
- `POL-100`: every return path records a terminal rule-trace outcome.

## 5. State semantics

| Status | Meaning | What it does not mean |
|---|---|---|
| `GREEN` | No configured review trigger was crossed and required evidence is present. | It does not mean the spacecraft is guaranteed safe. |
| `AMBER` | Review/monitoring is warranted due to an anomaly, uncertainty, disagreement, or borderline evidence. | It does not diagnose a subsystem failure. |
| `RED` | High-priority human review is warranted because a configured high-risk or compound condition is present. | It does not authorize a maneuver or certify a collision. |
| `INSUFFICIENT_DATA` | The system cannot responsibly score or interpret the inputs. | It does not mean the mission is safe or unsafe. |

## 6. Reason codes

Suggested stable codes:

- `DATA_MISSING_REQUIRED`
- `DATA_STALE`
- `DATA_CONTRADICTORY`
- `DATA_UNSUPPORTED_RANGE`
- `MODEL_UNAVAILABLE`
- `MODEL_UNCALIBRATED`
- `ORBIT_HIGH_RISK`
- `ORBIT_BORDERLINE`
- `TELEMETRY_ANOMALY_HIGH`
- `TELEMETRY_CHANNEL_AFFECTED`
- `MODEL_DISAGREEMENT`
- `NO_REVIEW_TRIGGER`
- `COMPOUND_EVIDENCE`
- `MODEL_SCORE_SEMANTICS_INVALID`
- `MODEL_SCORE_MISSING`
- `MODEL_SCORE_INVALID`
- `MODEL_SCORE_OUT_OF_RANGE`
- `POLICY_CONFIGURATION_INVALID`
- `TELEMETRY_EVIDENCE_MISSING`
- `TELEMETRY_UNAVAILABLE_OPTIONAL`

## 7. Safety rules

- Never display “maneuver now,” a maneuver vector, or a command.
- Never merge an anomaly score and orbit score into an unvalidated probability.
- Always show the data-quality panel before the headline state.
- Always include the rule trace in exports.
- Always include the non-certification disclaimer in dashboard and report views.
