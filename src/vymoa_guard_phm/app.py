"""Streamlit presentation layer over the deterministic assessment pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Streamlit executes this file as a script. Add the src root so the app works
# from a fresh checkout even before an editable install is performed.
if __package__ in (None, ""):
    source_root = Path(__file__).resolve().parents[1]
    if str(source_root) not in sys.path:
        sys.path.insert(0, str(source_root))

try:
    import streamlit as st
except ImportError:  # pragma: no cover
    st = None  # type: ignore[assignment]

from vymoa_guard_phm.replay import DEFAULT_FIXTURE, load_scenario, run_assessment
from vymoa_guard_phm.reports.render import to_json, to_markdown


def render() -> None:
    if st is None:
        raise RuntimeError("Install the project dependencies to run the Streamlit dashboard.")
    st.set_page_config(page_title="VymoaGaurd PHM", layout="wide")
    st.title("VymoaGaurd PHM")
    st.caption("Explainable mission-assurance prototype — not flight-certified software.")
    scenarios = list(json.loads(DEFAULT_FIXTURE.read_text(encoding="utf-8")))
    scenario = st.sidebar.selectbox("Replay scenario", scenarios)
    assessment = run_assessment(load_scenario(scenario))
    decision = assessment.decision
    st.subheader(f"Mission Overview — {assessment.scenario_id}")
    left, right = st.columns(2)
    left.metric("Triage status", decision.status)
    right.metric("Review action", decision.review_action)
    if decision.status == "INSUFFICIENT_DATA":
        st.warning("The policy abstained because required evidence or data-quality gates failed.")
    elif decision.status == "RED":
        st.error("High-priority human review is warranted. No maneuver command is generated.")
    elif decision.status == "AMBER":
        st.warning("Monitoring or investigation is warranted.")
    else:
        st.success("No configured review trigger crossed the current thresholds.")
    tab1, tab2, tab3, tab4 = st.tabs(["Orbit Risk", "Telemetry Health", "Decision Report", "Data Quality"])
    with tab1:
        st.json(assessment.orbit.to_dict())
    with tab2:
        st.json(assessment.telemetry.to_dict())
    with tab3:
        st.json(assessment.decision.to_dict())
        st.download_button("Download JSON", to_json(assessment), file_name=f"{scenario}.json", mime="application/json")
        st.download_button("Download Markdown", to_markdown(assessment), file_name=f"{scenario}.md", mime="text/markdown")
    with tab4:
        st.json([finding.to_dict() for finding in assessment.quality_findings])
        st.caption("All evidence is derived from the canonical MissionAssessment object.")


if __name__ == "__main__":  # pragma: no cover
    render()
