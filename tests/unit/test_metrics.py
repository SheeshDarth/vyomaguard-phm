from vymoa_guard_phm.evaluation.metrics import binary_metrics


def test_binary_metrics_reports_discrimination_and_calibration_fields():
    metrics = binary_metrics([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9])
    assert metrics["roc_auc"] == 1.0
    assert metrics["pr_auc"] == 1.0
    assert metrics["recall"] == 1.0
    assert "expected_calibration_error" in metrics
