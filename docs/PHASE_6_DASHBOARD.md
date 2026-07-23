# Phase 6 Dashboard and Reporting — VymoaGaurd PHM

## Gate status

Phase 6 is complete for the MVP dashboard and JSON/Markdown reporting gate. PDF generation remains intentionally deferred until the existing formats have stable parity and a visual verification workflow.

## Implemented surface

The Streamlit app at `src/vymoa_guard_phm/app.py` has four screens:

1. **Mission Overview** — triage status, review action, quality findings, evidence integrity, and reason codes.
2. **Orbit Risk** — ranking score semantics, risk class, model/threshold versions, feature evidence, and model notes.
3. **Telemetry Health** — anomaly score semantics, affected channels, anomaly window, model notes, and an explicit no-diagnosis boundary.
4. **Decision Report** — reason codes, rule trace, evidence-chain hashes, limitations, and report downloads.

The scenario selector uses fixed local fixtures only. The default replay visibly identifies the orbit path as a heuristic fixture baseline and telemetry as a robust-statistics baseline. No live mission data, credentials, maneuver command, diagnosis, or unsupported probability claim is introduced by the UI.

## Canonical data flow

```text
fixed fixture
  -> load_scenario
  -> run_assessment
  -> MissionAssessment
  -> dashboard tabs + JSON export + Markdown export
```

The dashboard imports the replay and report layers. It does not duplicate scoring, threshold, precedence, validation, or policy logic. The report renderer exposes the same input, configuration, policy, and evidence fingerprints shown in the Decision Report screen.

## Accessibility and usability checks

- Triage panels include visible status text and review action; status is not communicated by color alone.
- Ranking/anomaly score disclaimers are visible beside their metrics and do not depend on hover tooltips.
- The scenario selector has a visible label and help text.
- Tables expose column headers for quality findings, feature evidence, and rule traces.
- Download controls have a minimum 44px height.
- Text and border colors use a high-contrast navy/slate semantic palette.
- A reduced-motion media rule disables transitions and animation where requested by the user agent.
- The sidebar states that the dashboard is a deterministic local replay and includes the safety boundary.
- Native Streamlit tabs retain keyboard semantics and the app adds horizontal overflow and focus styling for narrower viewports.

## Verification

```text
python -m ruff check src tests --no-cache
python -m pytest -q -p no:cacheprovider
```

The integration smoke test verifies that the app starts without an exception, exposes the four screen labels, keeps the replay selector visible, and renders the canonical JSON evidence payloads. Regression tests also cover malformed input abstention, evidence-integrity export blocking, fixture provenance, heuristic semantics, Markdown audit parity, and path-safe report names. The full suite currently passes locally.
