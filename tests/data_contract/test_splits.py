import pytest

from vymoa_guard_phm.data.splits import group_temporal_split


def test_group_temporal_split_keeps_groups_disjoint_and_numeric_ordered():
    rows = [
        {"event_id": "late", "time_to_tca": "10"},
        {"event_id": "early", "time_to_tca": "2"},
        {"event_id": "middle", "time_to_tca": "5"},
        {"event_id": "middle", "time_to_tca": "4"},
    ]

    train, test = group_temporal_split(rows, group_key="event_id", time_key="time_to_tca", test_fraction=0.5)

    assert [row["event_id"] for row in train] == ["early", "middle", "middle"]
    assert [row["event_id"] for row in test] == ["late"]
    assert {row["event_id"] for row in train}.isdisjoint({row["event_id"] for row in test})


def test_group_temporal_split_rejects_missing_group_or_time():
    with pytest.raises(ValueError, match="Missing group key"):
        group_temporal_split([{"time_to_tca": "1"}], group_key="event_id", time_key="time_to_tca")
    with pytest.raises(ValueError, match="Missing time key"):
        group_temporal_split([{"event_id": "a"}], group_key="event_id", time_key="time_to_tca")
