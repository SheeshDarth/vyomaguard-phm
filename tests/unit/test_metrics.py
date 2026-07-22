import pytest

from vymoa_guard_phm.evaluation.metrics import bootstrap_metric_ci, regression_ranking_metrics


def test_regression_ranking_metrics_report_continuous_target_quality():
    result = regression_ranking_metrics([-30.0, -20.0, -10.0, -2.0], [-29.0, -21.0, -11.0, -3.0])

    assert result["mae"] == pytest.approx(1.0)
    assert result["rmse"] == pytest.approx(1.0)
    assert result["spearman"] == pytest.approx(1.0)
    assert result["top_risk_recall"] == 1.0


def test_regression_ranking_metrics_reject_bad_review_fraction():
    with pytest.raises(ValueError, match="review_fraction"):
        regression_ranking_metrics([1.0], [1.0], review_fraction=0.0)


def test_bootstrap_metric_ci_is_deterministic():
    values = bootstrap_metric_ci([-3.0, -2.0, -1.0, 0.0], [-2.9, -2.1, -1.1, -0.1], metric="spearman", iterations=20)

    assert values == bootstrap_metric_ci([-3.0, -2.0, -1.0, 0.0], [-2.9, -2.1, -1.1, -0.1], metric="spearman", iterations=20)
    assert values["lower"] <= values["upper"]
