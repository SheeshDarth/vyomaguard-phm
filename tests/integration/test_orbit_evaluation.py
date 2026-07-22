import csv
import io
import zipfile

from vymoa_guard_phm.evaluation.orbit import evaluate_esa_orbit_holdout, write_run_bundle


def test_esa_holdout_evaluation_verifies_manifest_and_replays_from_zip(tmp_path):
    rows = []
    for index in range(10):
        event_id = f"event-{index:02d}"
        base = float(index + 1)
        rows.extend(
            [
                {"event_id": event_id, "mission_id": "m", "time_to_tca": str(base + 0.5), "miss_distance": "100", "risk": "99"},
                {"event_id": event_id, "mission_id": "m", "time_to_tca": str(base), "miss_distance": str(base), "risk": str(-30 + index * 3)},
            ]
        )
    archive_path = tmp_path / "train_data.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        with archive.open("train_data.csv", "w") as raw_handle:
            with io.TextIOWrapper(raw_handle, encoding="utf-8", newline="") as text_stream:
                text_handle = csv.DictWriter(text_stream, fieldnames=list(rows[0]))
                text_handle.writeheader()
                text_handle.writerows(rows)

    manifest_path = tmp_path / "manifest.yaml"
    manifest_path.write_text(
        "\n".join(
            [
                "dataset_id: fixture-esa",
                "source_name: synthetic ESA",
                "source_snapshot: fixture-train_data.csv",
                "source_uri: https://example.invalid/train_data.zip",
                "acquired_at: 2026-07-22",
                "checksum: " + __import__("hashlib").sha256(archive_path.read_bytes()).hexdigest(),
                "license_note: synthetic",
                "schema_version: fixture-5-columns",
                "label_definition: continuous base10 log risk",
                "time_field: time_to_tca",
                "entity_fields: [event_id, mission_id]",
                "feature_fields: [time_to_tca, miss_distance]",
                "excluded_fields: [risk, event_id, mission_id]",
                "split_strategy: group_temporal",
                "status: FROZEN",
            ]
        ),
        encoding="utf-8",
    )

    result = evaluate_esa_orbit_holdout(archive_path, manifest_path=manifest_path, test_fraction=0.3)

    assert result["dataset_id"] == "fixture-esa"
    assert result["target_semantics"] == "base10_log_risk"
    assert result["split_strategy"] == "group_temporal"
    assert result["train_event_groups"] == 7.0
    assert result["test_event_groups"] == 3.0
    assert result["n"] == 3.0
    assert result["availability_contract_status"] == "BLOCKED_UNTIL_SIGNOFF"
    bundle_path = write_run_bundle(result, tmp_path / "run_bundle.json")
    assert bundle_path.exists()
