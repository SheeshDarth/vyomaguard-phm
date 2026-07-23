"""Streamlit presentation layer over the deterministic assessment pipeline."""

from __future__ import annotations

from html import escape
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
from vymoa_guard_phm.reports.render import safe_report_stem, to_json, to_markdown


STATUS_STYLES = {
    "GREEN": "green",
    "AMBER": "amber",
    "RED": "red",
    "INSUFFICIENT_DATA": "insufficient",
}


def _status_panel(status: str, action: str) -> str:
    tone = STATUS_STYLES.get(status, "insufficient")
    return (
        f'<div class="status-panel {tone}" role="status" aria-live="polite">'
        f'<span class="status-label">Triage status</span>'
        f'<strong>{escape(status)}</strong>'
        f'<span>{escape(action)}</span>'
        "</div>"
    )


def _apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root { --vg-navy:#0b132b; --vg-ink:#14213d; --vg-muted:#4b5563; --vg-border:#cbd5e1; --vg-surface:#f8fafc; }
        .block-container { max-width: 1180px; padding-top: 2.2rem; padding-bottom: 3rem; }
        h1, h2, h3 { color: var(--vg-navy); letter-spacing: -0.02em; }
        p, li, label, [data-testid="stMetricLabel"] { color: var(--vg-ink); }
        .status-panel { display:flex; align-items:center; gap:1rem; border:1px solid var(--vg-border); border-left:8px solid var(--vg-navy); border-radius:12px; background:var(--vg-surface); padding:1rem 1.25rem; margin:0.5rem 0 1.25rem; }
        .status-panel strong { font-size:1.35rem; color:var(--vg-navy); }
        .status-panel span { color:var(--vg-muted); }
        .status-panel .status-label { font-weight:700; color:var(--vg-ink); }
        .status-panel.green { border-left-color:#0f766e; }
        .status-panel.amber { border-left-color:#b45309; }
        .status-panel.red { border-left-color:#b42318; }
        .status-panel.insufficient { border-left-color:#475569; }
        [data-testid="stSidebar"] { background:#f1f5f9; }
        [data-testid="stDownloadButton"] button { min-height:44px; }
        div[data-baseweb="tab-list"] { overflow-x:auto; scrollbar-width:thin; }
        div[data-baseweb="tab"] { color:#334155 !important; }
        div[data-baseweb="tab"][aria-selected="true"] { color:#0b3d62 !important; }
        div[data-testid="stDataFrame"] button { min-width:44px; min-height:44px; }
        button:focus-visible, [role="tab"]:focus-visible { outline:3px solid #0f766e !important; outline-offset:2px; }
        @media (max-width: 720px) {
          .block-container { padding-left:1rem; padding-right:1rem; }
          .status-panel { align-items:flex-start; flex-direction:column; gap:0.25rem; }
        }
        @media (prefers-reduced-motion: reduce) {
          *, *::before, *::after { scroll-behavior:auto !important; transition:none !important; animation:none !important; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _quality_rows(assessment) -> list[dict[str, str]]:
    return [
        {"Status": finding.status, "Code": finding.code, "Severity": finding.severity, "Message": finding.message}
        for finding in assessment.quality_findings
    ]


def _feature_rows(assessment) -> list[dict[str, object]]:
    return [
        {
            "Feature": item["name"],
            "Value": item["value"],
            "Evidence type": item.get("evidence_type", "model_attribution"),
            "Attribution": item.get("attribution") if item.get("attribution") is not None else "Not available",
            "Direction": item.get("direction", "unknown"),
        }
        for item in assessment.orbit.top_features
    ]


def _evidence_rows(assessment) -> list[dict[str, str]]:
    return [
        {"Rule": item["rule_id"], "Result": str(item["result"]), "Evidence": str(item["evidence"])}
        for item in assessment.decision.rule_trace
    ]


def render() -> None:
    if st is None:
        raise RuntimeError("Install the project dependencies to run the Streamlit dashboard.")
    st.set_page_config(page_title="VymoaGaurd PHM", layout="wide")
    _apply_theme()
    st.title("VymoaGaurd PHM")
    st.caption("Evidence-first mission-assurance prototype · research software, not flight-certified software")
    scenarios = list(json.loads(DEFAULT_FIXTURE.read_text(encoding="utf-8")))
    st.sidebar.markdown("### Scenario replay")
    scenario = st.sidebar.selectbox("Replay scenario", scenarios, help="Select a fixed deterministic fixture.")
    st.sidebar.caption("The dashboard replays local fixtures only. No live mission data is connected.")
    st.sidebar.info("Review suggestions only. No probability, diagnosis, certification, or maneuver command is produced.")
    assessment = run_assessment(load_scenario(scenario))
    decision = assessment.decision
    integrity_ok = assessment.verify_evidence_hash()
    if not integrity_ok:
        st.error("Canonical object hash verification failed. Interpretation and exports are blocked.")
        st.stop()
    st.markdown(_status_panel(decision.status, decision.review_action), unsafe_allow_html=True)

    tab_overview, tab_orbit, tab_telemetry, tab_report = st.tabs(
        ["Mission Overview", "Orbit Risk", "Telemetry Health", "Decision Report"]
    )
    with tab_overview:
        st.header("Mission Overview")
        left, middle, right, integrity = st.columns(4)
        left.metric("Triage status", decision.status)
        middle.metric("Review action", decision.review_action)
        right.metric("Quality findings", len(assessment.quality_findings))
        integrity.metric("Canonical object hash", "Verified")
        st.caption(f"Scenario: `{assessment.scenario_id}` · Run ID: `{assessment.run_id}` · Evidence schema: `{assessment.evidence_schema_version}`")
        st.subheader("Data quality")
        st.dataframe(_quality_rows(assessment), hide_index=True, use_container_width=True)
        st.subheader("Decision reasons")
        st.write(" · ".join(f"`{reason}`" for reason in decision.reason_codes) or "No reason codes recorded.")
        st.info("Research/demo only: GREEN means no configured review trigger crossed with required evidence present. It does not mean the spacecraft is safe or flight-ready.")

    with tab_orbit:
        st.header("Orbit Risk")
        st.info("The orbit output is an uncalibrated ranking score, not a collision probability or safety determination. LOW_RANKING means only that the configured monitor threshold was not crossed.")
        orbit = assessment.orbit
        score, orbit_class, raw_value = st.columns(3)
        score.metric("Ranking score", orbit.score if orbit.score is not None else "Unavailable")
        orbit_class.metric("Risk class", orbit.risk_class)
        raw_value.metric("Raw target", orbit.raw_value if orbit.raw_value is not None else "Unavailable")
        st.caption(f"Score semantics: `{orbit.score_type}` · Model path: `{orbit.model_version}` · Thresholds: `{orbit.threshold_version}`")
        st.subheader("Feature evidence")
        st.dataframe(_feature_rows(assessment), hide_index=True, use_container_width=True)
        st.subheader("Model evidence")
        for item in orbit.evidence:
            st.write(f"• {item}")

    with tab_telemetry:
        st.header("Telemetry Health")
        st.info("The telemetry output is an anomaly score from a robust rolling baseline, not a failure probability, diagnosis, or health percentage.")
        telemetry = assessment.telemetry
        score, channels, window = st.columns(3)
        score.metric("Anomaly score", telemetry.score if telemetry.score is not None else "Unavailable")
        channels.metric("Affected channels", len(telemetry.affected_channels))
        window.metric("Anomaly window", "Available" if telemetry.anomaly_window else "Unavailable")
        st.caption(f"Score semantics: `{telemetry.score_type}` · Model path: `{telemetry.model_version}` · Thresholds: `{telemetry.threshold_version}`")
        st.subheader("Affected channels")
        if telemetry.affected_channels:
            st.dataframe([{"Channel": channel} for channel in telemetry.affected_channels], hide_index=True, use_container_width=True)
        else:
            st.info("No affected channels were reported.")
        st.subheader("Anomaly window")
        st.json(telemetry.anomaly_window or {"status": "No anomaly window reported"})
        st.subheader("Telemetry evidence")
        for item in telemetry.evidence:
            st.write(f"• {item}")

    with tab_report:
        st.header("Decision Report")
        st.subheader("Decision status")
        st.write(f"`{decision.status}` · `{decision.review_action}` · abstained=`{decision.abstained}`")
        st.subheader("Reason codes")
        st.write(" · ".join(f"`{reason}`" for reason in decision.reason_codes) or "No reason codes recorded.")
        st.subheader("Rule trace")
        st.dataframe(_evidence_rows(assessment), hide_index=True, use_container_width=True)
        st.subheader("Evidence chain")
        st.json(
            {
                "source": assessment.input_manifest.get("source"),
                "fixture_sha256": assessment.input_manifest.get("fixture_sha256"),
                "input_hash": assessment.input_manifest.get("input_hash"),
                "config_hash": assessment.input_manifest.get("config_hash"),
                "policy_hash": assessment.versions.get("policy_hash"),
                "evidence_schema_version": assessment.evidence_schema_version,
                "evidence_hash": assessment.evidence_hash,
                "canonical_object_hash_verified": integrity_ok,
                "note": "Integrity fingerprint only; not an authenticity or provenance signature.",
            }
        )
        report_stem = safe_report_stem(scenario)
        st.download_button("Download canonical JSON", to_json(assessment), file_name=f"{report_stem}.json", mime="application/json", key="download-json")
        st.download_button("Download Markdown report", to_markdown(assessment), file_name=f"{report_stem}.md", mime="text/markdown", key="download-markdown")
        with st.expander("Limitations and safety boundary"):
            for limitation in assessment.limitations:
                st.write(f"• {limitation}")
            st.caption("All displayed evidence is derived from the canonical MissionAssessment object.")


if __name__ == "__main__":  # pragma: no cover
    render()
