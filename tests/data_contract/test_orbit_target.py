import pytest

from vymoa_guard_phm.data.orbit_target import extract_final_risk_targets, select_final_cdm_rows


def test_final_row_selection_preserves_source_order_for_non_monotonic_events():
    rows = [
        {"event_id": "a", "time_to_tca": "2", "risk": "-10"},
        {"event_id": "b", "time_to_tca": "1", "risk": "-8"},
        {"event_id": "a", "time_to_tca": "1", "risk": "-20"},
        {"event_id": "b", "time_to_tca": "0", "risk": "-9"},
    ]

    selected = select_final_cdm_rows(rows)

    assert [(item.event_id, item.source_row_index) for item in selected] == [("a", 2), ("b", 3)]
    assert [item.row["risk"] for item in selected] == ["-20", "-9"]


def test_risk_target_extraction_is_finite_and_replayable():
    rows = [
        {"event_id": "a", "risk": "-30"},
        {"event_id": "a", "risk": "-25"},
        {"event_id": "b", "risk": "-5"},
    ]

    first = extract_final_risk_targets(rows)
    second = extract_final_risk_targets(rows)

    assert first == second
    assert [(item.event_id, item.source_row_index, item.value) for item in first] == [("a", 1, -25.0), ("b", 2, -5.0)]


@pytest.mark.parametrize(
    "rows, message",
    [
        ([{"risk": "-2"}], "Missing 'event_id'"),
        ([{"event_id": "a", "risk": "not-a-number"}], "Invalid 'risk'"),
        ([{"event_id": "a", "risk": "nan"}], "Non-finite 'risk'"),
    ],
)
def test_target_contract_rejects_ambiguous_rows(rows, message):
    with pytest.raises(ValueError, match=message):
        extract_final_risk_targets(rows)
