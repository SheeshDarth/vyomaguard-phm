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
    selected = {manifest.dataset_id: manifest for _, manifest in manifests}
    assert [finding.status for finding in selected["esa-collision-avoidance-challenge"].audit()] == ["PASS"]
    assert [finding.status for finding in selected["esa-opssat-ad"].audit()] == ["PASS"]
    fallback_codes = {finding.code for finding in selected["nasa-smap-msl"].audit()}
    assert "MANIFEST_NOT_FROZEN" in fallback_codes
    assert "MANIFEST_UNCONFIRMED" in fallback_codes


def test_frozen_manifest_with_sha256_and_schema_is_ready(tmp_path):
    data_path = tmp_path / "records.json"
    data_path.write_text("[]\n", encoding="utf-8")
    manifest = DatasetManifest.from_mapping(
        {
            "dataset_id": "fixture",
            "source_name": "synthetic",
            "source_snapshot": "fixture-0.1.0",
            "source_uri": "https://example.invalid/fixture.json",
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


def test_manifest_rejects_malformed_companion_checksum():
    manifest = DatasetManifest.from_mapping(
        {
            "dataset_id": "bad-artifact",
            "source_name": "synthetic",
            "source_snapshot": "fixture",
            "source_uri": "https://example.invalid/fixture.json",
            "acquired_at": "2026-07-22",
            "checksum": "0" * 64,
            "artifact_checksums": ["dataset.csv=not-a-sha256"],
            "license_note": "synthetic",
            "schema_version": "1",
            "label_definition": "binary",
            "time_field": "timestamp",
            "entity_fields": ["event_id"],
            "feature_fields": ["miss_distance_km"],
            "excluded_fields": ["label"],
            "split_strategy": "group_temporal",
            "status": "FROZEN",
        }
    )

    assert "MANIFEST_INVALID_ARTIFACT_CHECKSUM" in {finding.code for finding in manifest.audit()}


def test_manifest_rejects_target_or_group_fields_as_predictors():
    manifest = DatasetManifest.from_mapping(
        {
            "dataset_id": "bad",
            "source_name": "synthetic",
            "source_snapshot": "fixture",
            "source_uri": "https://example.invalid/fixture.json",
            "acquired_at": "2026-07-22",
            "checksum": "0" * 64,
            "license_note": "synthetic",
            "schema_version": "1",
            "label_definition": "binary",
            "time_field": "timestamp",
            "entity_fields": ["event_id"],
            "feature_fields": ["event_id", "risk"],
            "excluded_fields": [],
            "split_strategy": "group_temporal",
            "status": "FROZEN",
        }
    )

    codes = {finding.code for finding in manifest.audit()}
    assert "MANIFEST_TARGET_LEAKAGE" in codes
    assert "MANIFEST_GROUP_FEATURE_OVERLAP" in codes
