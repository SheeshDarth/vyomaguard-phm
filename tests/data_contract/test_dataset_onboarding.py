import pytest

from vymoa_guard_phm.data.label_audit import audit_binary_labels
from vymoa_guard_phm.data.splits import assert_no_overlap, temporal_split


def test_label_audit_reports_binary_support_without_inference():
    result = audit_binary_labels(
        [
            {"event_id": "a", "label": 0},
            {"event_id": "b", "label": 1},
            {"event_id": "c", "label": 1},
        ]
    )

    assert result["status"] == "PASS"
    assert result["supports_binary_training"] is True
    assert result["label_counts"] == {"0": 1, "1": 2}


def test_temporal_split_orders_rows_and_rejects_entity_overlap():
    rows = [
        {"timestamp": "2026-01-03", "event_id": "c"},
        {"timestamp": "2026-01-01", "event_id": "a"},
        {"timestamp": "2026-01-02", "event_id": "b"},
        {"timestamp": "2026-01-04", "event_id": "d"},
    ]

    train, test = temporal_split(rows, test_fraction=0.5)

    assert [row["event_id"] for row in train] == ["a", "b"]
    assert [row["event_id"] for row in test] == ["c", "d"]
    assert_no_overlap(train, test, "event_id")

    with pytest.raises(ValueError, match="Leakage detected"):
        assert_no_overlap(train, [{"timestamp": "2026-01-05", "event_id": "b"}], "event_id")
