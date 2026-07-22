import pytest

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.models.orbit import OrbitRiskEngine


def test_orbit_engine_fits_continuous_target_and_preserves_units():
    pytest.importorskip("sklearn")
    rows = [
        {"event": {"features": {"miss_distance": 1.0, "relative_speed": 1.0}}, "risk": -30.0},
        {"event": {"features": {"miss_distance": 2.0, "relative_speed": 1.0}}, "risk": -20.0},
        {"event": {"features": {"miss_distance": 3.0, "relative_speed": 1.0}}, "risk": -10.0},
        {"event": {"features": {"miss_distance": 4.0, "relative_speed": 1.0}}, "risk": -2.0},
    ]

    engine = OrbitRiskEngine(AssessmentConfig()).fit(rows)
    assessment = engine.score({"features": {"miss_distance": 3.5, "relative_speed": 1.0}})

    assert engine.fitted is True
    assert assessment.score_type == "ranking_score"
    assert assessment.raw_value_unit == "base10_log_risk"
    assert assessment.raw_value is not None
    assert 0.0 <= assessment.score <= 1.0
    assert assessment.evidence[1].endswith("not a collision probability.")


def test_orbit_engine_does_not_fit_without_continuous_targets():
    engine = OrbitRiskEngine(AssessmentConfig()).fit(
        [{"event": {"features": {"miss_distance": 1.0}}, "label": 1}] * 4
    )

    assert engine.fitted is False


def test_orbit_engine_uses_source_order_final_rows_for_raw_cdm_rows():
    pytest.importorskip("sklearn")
    rows = []
    final_targets = [-30.0, -20.0, -10.0, -2.0]
    for index, target in enumerate(final_targets):
        rows.extend(
            [
                {"event_id": f"event-{index}", "miss_distance": 100.0, "risk": 99.0},
                {"event_id": f"event-{index}", "miss_distance": float(index + 1), "risk": target},
            ]
        )

    engine = OrbitRiskEngine(AssessmentConfig()).fit(rows)

    assert engine.fitted is True
    assert engine.target_min == -30.0
    assert engine.target_max == -2.0
