# VymoaGaurd PHM — Knowledge Graph Audit

## Corpus

- **Input:** `VymoaGaurd_PHM_Project_Brief.md`
- **Files:** 1 Markdown document
- **Words:** approximately 990
- **Nodes:** 30
- **Edges:** 33
- **Communities:** 5
- **Extraction:** manual evidence extraction from the complete brief
- **Token cost:** 0 input / 0 output tokens; no graphify package or semantic subagent was available in the workspace

The graph is intentionally honest: edges explicitly stated in the brief are `EXTRACTED`; cross-module relationships inferred from the product flow are `INFERRED` and carry a lower confidence score.

## Communities

1. **Product Mission Assurance** — product identity, mission-assurance framing, and the four top-level modules.
2. **Orbit Risk Engine** — CDMs, the ESA dataset, risk scores/classes, metrics, and SHAP attribution.
3. **Telemetry Health** — candidate telemetry datasets, anomaly score, affected channels, and anomaly windows.
4. **Policy Dashboard Reporting** — deterministic decision policy, decision classes, dashboard screens, and exports.
5. **Validation Delivery Constraints** — solo six-week plan, RTX 4050 constraint, evaluation, explainability, data quality, and exclusions.

## God Nodes

These nodes connect multiple communities and are the best starting points for understanding the project:

- **VymoaGaurd PHM** — connects product identity to both model engines, the decision layer, and dashboard.
- **Mission Decision Layer** — the bridge between orbit risk, telemetry health, operator triage, and explainability.
- **Streamlit Dashboard** — turns the model/policy graph into the user-facing product.
- **Orbit Risk Engine** — the strongest primary capability and the source of the orbit-risk evidence chain.
- **Six-Week Solo Build Plan** — constrains model ambition, dashboard timing, and RTX 4050 usage.

## Surprising Connections

- The brief’s strongest differentiator is not a model node; it is the path **CDM/telemetry → decision layer → dashboard/report**. The product value is cross-domain traceability.
- The **deterministic policy** node is the safety bridge: it connects two uncertain model outputs without requiring an unvalidated joint probability.
- **SHAP feature attribution** connects the orbit model to the product’s explainability claim, but the graph does not support a causal-explanation claim.
- The **six-week plan** is structurally coupled to the dashboard and model choices: the planned deep-learning upgrade is the most likely scope-pressure point.

## Suggested Questions

- How should a rule-based decision layer combine orbit risk and telemetry anomalies without creating an unsupported joint probability?
- Which dataset and label definition can support a calibrated risk claim rather than only ranking or triage?
- What acceptance thresholds prove that the telemetry anomaly engine is useful rather than merely visually interesting?
- Which features are actually present in the selected CDM dataset and safe from temporal leakage?
- What is the smallest replay scenario that demonstrates the complete evidence chain?

## Audit notes

- The original brief is a product concept and six-week build plan, not an implementation specification.
- It names model families and metrics but does not define label semantics, split logic, thresholds, data freshness rules, or numerical acceptance gates.
- It names “mission-readiness status” but does not define its operational meaning; downstream design narrows this to explicit triage states and abstention.
- `Aerospace Predictive Maintenance Report - Google Docs.pdf` was not included in this graph because the requested source was the Markdown brief.
