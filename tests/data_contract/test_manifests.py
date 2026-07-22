from pathlib import Path

from vymoa_guard_phm.data.manifest import DatasetManifest, load_manifests, sha256_file


MANIFEST_DIR = Path("data/manifests")


def test_candidate_manifests_are_parseable_and_explicitly_unverified():
    manifests = load_manifests(MANIFEST_DIR)

    assert {manifest.dataset_id for _, manifest in manifests} == {
        "esa-collision-avoidance-challenge",
        "esa-opssat-ad",
        "nasa-smap-msl",
    }
    for _, manifest in manifests:
        codes = {finding.code for finding in manifest.audit()}
        assert "MANIFEST_NOT_FROZEN" in codes
        assert "MANIFEST_UNCONFIRMED" in codes


def test_frozen_manifest_with_sha256_and_schema_is_ready(tmp_path):
    data_path = tmp_path / "records.json"
    data_path.write_text("[]\n", encoding="utf-8")
    manifest = DatasetManifest.from_mapping(
        {
            "dataset_id": "fixture",
            "source_name": "synthetic",
            "source_snapshot": "fixture-0.1.0",
            "acquired_at": "2026-07-22T00:00:00Z",
            "checksum": sha256_file(data_path),
            "license_note": "repository synthetic fixture",
            "schema_version": "fixture-0.1.0",
            "label_definition": "1 means reviewed risk event",
            "time_field": "timestamp",
            "entity_fields": ["event_id"],
            "feature_fields": ["miss_distance_km"],
            "excluded_fields": ["label"],
            "split_strategy": "group_temporal",
            "status": "FROZEN",
        }
    )

    assert [finding.status for finding in manifest.audit()] == ["PASS"]
