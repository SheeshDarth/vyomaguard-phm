from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.evaluation.metrics import anomaly_detection_metrics
from vymoa_guard_phm.models.telemetry import TelemetryAnomalyEngine


def test_telemetry_engine_uses_nominal_fit_and_returns_evidence():
    train = [
        {"timestamp": str(index), "channel": "bus_a", "value": 1.0 + (index % 3) * 0.01, "anomaly": 0}
        for index in range(12)
    ]
    holdout = [
        {"timestamp": "20", "channel": "bus_a", "value": 1.01, "anomaly": 0},
        {"timestamp": "21", "channel": "bus_a", "value": 9.0, "anomaly": 1},
    ]
    assessment = TelemetryAnomalyEngine(AssessmentConfig(telemetry_iforest_estimators=10)).fit(train).score(holdout)
    assert assessment.status == "SCORED"
    assert assessment.score_type == "anomaly_score"
    assert assessment.score is not None
    assert any("not a failure probability" in item for item in assessment.evidence)


def test_anomaly_metrics_keep_single_class_auc_explicitly_unavailable():
    metrics = anomaly_detection_metrics([0, 0], [0.1, 0.2])
    assert metrics["roc_auc"] is None
    assert metrics["pr_auc"] is None
    assert metrics["false_alarm_rate"] == 0.0


def test_engine_refit_discards_previous_channel_models():
    rows = [
        {"timestamp": str(index), "channel": "bus_a", "value": 1.0, "anomaly": 0}
        for index in range(8)
    ]
    engine = TelemetryAnomalyEngine(AssessmentConfig(telemetry_iforest_estimators=10)).fit(rows)
    assert set(engine.baselines) == {"bus_a"}
    engine.fit([{**row, "channel": "bus_b"} for row in rows])
    assert set(engine.baselines) == {"bus_b"}
    assert set(engine.models) <= {"bus_b"}
