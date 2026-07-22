# VymoaGaurd PHM

## Subtitle

Space Mission Assurance Digital Twin for Collision Risk, Satellite Telemetry Anomaly Detection, and Operator Decision Support

## One-Line Pitch

VymoaGaurd PHM predicts spacecraft collision risk, detects satellite telemetry anomalies, and converts both into explainable mission-operator recommendations.

## Why This Project

India's private space ecosystem is moving fast across space situational awareness, satellite operations, Earth observation, and mission assurance. A strong student project in this area should not be another generic machine learning notebook. It should look like a compact prototype of a real space-operations tool.

VymoaGaurd PHM is designed to show that capability. It combines two high-value aerospace problems:

1. Spacecraft conjunction and collision-risk prediction.
2. Satellite telemetry anomaly detection and subsystem health monitoring.

The project is scoped for a solo build on an RTX 4050 while still looking serious enough for NASA, ISRO, DRDO, Digantara, Dhruva Space, Airbus Defence, Boeing Space, Lockheed Martin, and satellite-operations startups.

## Core Problem Statement

Satellite operators must continuously monitor two major mission risks:

1. External orbital risk: another object may pass dangerously close to the spacecraft.
2. Internal spacecraft risk: telemetry may indicate abnormal subsystem behavior.

VymoaGaurd PHM builds an explainable AI dashboard that helps operators answer:

- Is this satellite currently safe?
- Is there a collision-risk event that needs maneuver review?
- Is any telemetry channel behaving abnormally?
- Which subsystem or feature is driving the risk?
- What action should the operator take next?

## MVP Scope

### Module 1: Orbit Risk Engine

Purpose:
Predict final conjunction/collision risk from time-series Conjunction Data Messages.

Dataset:
ESA Collision Avoidance Challenge dataset.

Models:
- Baseline: Logistic Regression, Random Forest, XGBoost or LightGBM.
- Advanced: LSTM or Temporal Transformer over CDM sequences.

Outputs:
- Collision-risk score.
- Risk class: safe, monitor, maneuver review.
- Confidence estimate.
- Top contributing CDM features using SHAP.

Metrics:
- ROC-AUC.
- PR-AUC.
- F1 score for high-risk events.
- False-negative rate.
- Calibration error.

### Module 2: Telemetry Anomaly Engine

Purpose:
Detect abnormal spacecraft telemetry behavior and identify affected channels.

Dataset Options:
- ESA OPSSAT-AD.
- NASA SMAP/MSL anomaly detection dataset.

Models:
- Baseline: Isolation Forest, One-Class SVM.
- Advanced: LSTM Autoencoder or Transformer Autoencoder.

Outputs:
- Anomaly score.
- Affected telemetry channels.
- Time-window of anomaly.
- Mission-readiness status.

Metrics:
- Precision.
- Recall.
- F1 score.
- False alarm rate.
- Detection delay.

### Module 3: Mission Decision Layer

Purpose:
Convert model outputs into operator-facing recommendations.

Decision Classes:
- Safe.
- Monitor.
- Investigate.
- Maneuver review.
- Safe-mode risk.

Approach:
Use a deterministic rule-based policy first. This is better than making the project LLM-dependent because safety-critical recommendations should be explainable and repeatable.

Example:

If collision risk is high and telemetry is normal:
Recommend maneuver review.

If telemetry anomaly is high but collision risk is low:
Recommend subsystem investigation.

If both collision risk and telemetry anomaly are high:
Recommend mission-critical review.

### Module 4: Dashboard

Recommended Stack:
- Streamlit for fastest solo build.
- Python backend with scikit-learn, XGBoost or LightGBM, PyTorch, SHAP.
- SQLite or Parquet for local storage.

Screens:

1. Mission Overview
   - Satellite status.
   - Current risk level.
   - Latest anomaly.
   - Recommended action.

2. Orbit Risk
   - CDM event timeline.
   - Predicted collision probability.
   - Risk class.
   - Explainability panel.

3. Telemetry Health
   - Sensor/channel plots.
   - Highlighted anomaly windows.
   - Affected subsystem estimate.

4. Decision Report
   - Risk summary.
   - Evidence.
   - Confidence.
   - Recommended action.
   - Export as Markdown/PDF/JSON.

## What To Avoid

- Do not add SAR, hyperspectral, or Earth-observation image generation into the MVP.
- Do not make it a huge multi-agent local LLM project.
- Do not start with 3D orbit visualization.
- Do not overclaim that it is production-ready or certified.
- Do not frame it as a military targeting system.

## Differentiation

Most student projects stop at model training. VymoaGaurd PHM should stand out because it includes:

- Real aerospace datasets.
- Two mission-risk channels: orbit risk and telemetry health.
- Explainable model outputs.
- Operator-facing decision policy.
- Dashboard and exportable report.
- Clear aerospace product framing.

## Resume Bullet

Built VymoaGaurd PHM, a space mission-assurance dashboard that combines spacecraft conjunction-risk prediction and satellite telemetry anomaly detection, using ESA/NASA datasets, explainable ML, and rule-based operator decision support.

## GitHub README Hook

VymoaGaurd PHM is an explainable mission-assurance prototype for satellite operators. It predicts spacecraft collision risk from conjunction data, detects anomalies in satellite telemetry, and recommends operator actions through a mission-control dashboard.

## Suggested Repository Name

vyomaguard-phm

## Suggested Tech Stack

- Python
- scikit-learn
- XGBoost or LightGBM
- PyTorch
- SHAP
- Streamlit
- Pandas
- NumPy
- Plotly
- SQLite or Parquet

## Six-Week Solo Build Plan

### Week 1: Research and Data Pipeline

- Download ESA Collision Avoidance Challenge data.
- Download OPSSAT-AD or NASA SMAP/MSL telemetry data.
- Write data loaders.
- Create exploratory notebooks.
- Define target labels and evaluation metrics.

### Week 2: Orbit Risk Baseline

- Train tabular baseline models.
- Evaluate with ROC-AUC, PR-AUC, and F1.
- Add risk classes.
- Add SHAP explanations.

### Week 3: Telemetry Anomaly Baseline

- Train Isolation Forest or One-Class SVM.
- Build anomaly scoring pipeline.
- Plot anomaly windows.
- Evaluate precision, recall, F1, and false alarm rate.

### Week 4: Deep Learning Upgrade

- Add LSTM Autoencoder for telemetry.
- Optionally add sequence model for CDM risk prediction.
- Compare baseline vs advanced models.

### Week 5: Dashboard

- Build Streamlit interface.
- Add mission overview screen.
- Add orbit-risk and telemetry-health screens.
- Add decision report export.

### Week 6: Polish

- Write README.
- Add architecture diagram.
- Add screenshots.
- Record demo video.
- Add limitations and future work.

## Final Positioning

VymoaGaurd PHM should be presented as:

"A solo-built space mission-assurance prototype for explainable collision-risk prediction, spacecraft telemetry anomaly detection, and operator decision support."

This is specific, aerospace-relevant, and differentiated enough to help an internship profile stand out.
