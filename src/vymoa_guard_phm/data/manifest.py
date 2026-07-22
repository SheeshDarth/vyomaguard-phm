"""Dataset manifest contracts and pre-training audit gates.

The MVP never downloads data implicitly. A manifest must be completed and
frozen before a dataset can be used for training or probability claims.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Literal

ManifestStatus = Literal["PASS", "WARN", "FAIL"]
ALLOWED_SPLITS = {"temporal", "group_temporal"}
PLACEHOLDER_MARKER = "UNCONFIRMED"


def _parse_value(raw_value: str) -> Any:
    value = raw_value.strip()
    if not value:
        return ""
    if value.startswith("[") or value.startswith("{"):
        try:
            return ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            if value.startswith("[") and value.endswith("]"):
                return [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
            raise ValueError(f"Unsupported manifest value: {value!r}") from exc
    if value.lower() in {"null", "none"}:
        return None
    return value.strip("\"'")


def _read_simple_yaml(path: Path) -> dict[str, Any]:
    """Read the flat YAML subset used by repository manifests.

    Keeping this parser in the standard library avoids making PyYAML a
    runtime requirement for the small, auditable manifest format.
    """

    values: dict[str, Any] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"Invalid manifest line {line_number} in {path}: {raw_line!r}")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"Manifest line {line_number} has an empty key: {path}")
        values[key] = _parse_value(raw_value)
    return values


@dataclass(frozen=True)
class ManifestFinding:
    status: ManifestStatus
    code: str
    severity: Literal["info", "warning", "error"]
    message: str
    field: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    source_name: str
    source_snapshot: str
    source_uri: str
    acquired_at: str
    checksum: str
    license_note: str
    schema_version: str
    label_definition: str
    time_field: str
    entity_fields: tuple[str, ...]
    feature_fields: tuple[str, ...]
    excluded_fields: tuple[str, ...]
    split_strategy: str
    status: str
    notes: str = ""
    artifact_checksums: tuple[str, ...] = ()

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "DatasetManifest":
        def text(key: str) -> str:
            value = payload.get(key)
            return "" if value is None else str(value)

        def fields(key: str) -> tuple[str, ...]:
            value = payload.get(key) or []
            if isinstance(value, str):
                value = [value]
            if not isinstance(value, (list, tuple)):
                raise ValueError(f"Manifest field {key!r} must be a list.")
            return tuple(str(item) for item in value)

        return cls(
            dataset_id=text("dataset_id"),
            source_name=text("source_name"),
            source_snapshot=text("source_snapshot"),
            source_uri=text("source_uri"),
            acquired_at=text("acquired_at"),
            checksum=text("checksum"),
            license_note=text("license_note"),
            schema_version=text("schema_version"),
            label_definition=text("label_definition"),
            time_field=text("time_field"),
            entity_fields=fields("entity_fields"),
            feature_fields=fields("feature_fields"),
            excluded_fields=fields("excluded_fields"),
            split_strategy=text("split_strategy"),
            status=text("status"),
            notes=text("notes"),
            artifact_checksums=fields("artifact_checksums"),
        )

    @classmethod
    def from_path(cls, path: str | Path) -> "DatasetManifest":
        manifest_path = Path(path)
        return cls.from_mapping(_read_simple_yaml(manifest_path))

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in ("entity_fields", "feature_fields", "excluded_fields", "artifact_checksums"):
            payload[key] = list(payload[key])
        return payload

    def audit(self) -> list[ManifestFinding]:
        findings: list[ManifestFinding] = []
        required = (
            "dataset_id",
            "source_name",
            "source_snapshot",
            "source_uri",
            "acquired_at",
            "checksum",
            "license_note",
            "schema_version",
            "label_definition",
            "time_field",
            "split_strategy",
            "status",
        )
        for field in required:
            if not getattr(self, field):
                findings.append(ManifestFinding("FAIL", "MANIFEST_MISSING_FIELD", "error", f"Manifest field {field!r} is required.", field))

        for field in required:
            value = getattr(self, field)
            if PLACEHOLDER_MARKER in value.upper():
                findings.append(ManifestFinding("WARN", "MANIFEST_UNCONFIRMED", "warning", f"Manifest field {field!r} still contains an unconfirmed placeholder.", field))

        if self.status.upper() != "FROZEN":
            findings.append(ManifestFinding("WARN", "MANIFEST_NOT_FROZEN", "warning", "Training is blocked until the manifest is frozen.", "status"))
        if self.split_strategy not in ALLOWED_SPLITS:
            findings.append(ManifestFinding("FAIL", "MANIFEST_INVALID_SPLIT", "error", f"Unsupported split strategy: {self.split_strategy!r}.", "split_strategy"))
        if self.checksum and PLACEHOLDER_MARKER not in self.checksum.upper() and not re.fullmatch(r"[0-9a-fA-F]{64}", self.checksum):
            findings.append(ManifestFinding("FAIL", "MANIFEST_INVALID_CHECKSUM", "error", "Checksum must be a 64-character SHA-256 hex digest.", "checksum"))
        if not self.feature_fields:
            findings.append(ManifestFinding("WARN", "MANIFEST_FEATURES_UNCONFIRMED", "warning", "Feature fields must be confirmed from the source schema before training.", "feature_fields"))
        for artifact in self.artifact_checksums:
            if "=" not in artifact:
                findings.append(ManifestFinding("FAIL", "MANIFEST_INVALID_ARTIFACT_CHECKSUM", "error", "Artifact checksums must use the form filename=sha256.", "artifact_checksums"))
                continue
            filename, digest = artifact.split("=", 1)
            if not filename or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
                findings.append(ManifestFinding("FAIL", "MANIFEST_INVALID_ARTIFACT_CHECKSUM", "error", "Artifact checksum entries must contain a filename and 64-character SHA-256 digest.", "artifact_checksums"))
        if "risk" in self.feature_fields:
            findings.append(ManifestFinding("FAIL", "MANIFEST_TARGET_LEAKAGE", "error", "The continuous risk target cannot be used as an input feature.", "feature_fields"))
        overlapping_keys = sorted(set(self.entity_fields) & set(self.feature_fields))
        if overlapping_keys:
            findings.append(ManifestFinding("FAIL", "MANIFEST_GROUP_FEATURE_OVERLAP", "error", f"Entity/group fields cannot also be predictors: {overlapping_keys}.", "feature_fields"))

        if not any(finding.status != "PASS" for finding in findings):
            findings.append(ManifestFinding("PASS", "MANIFEST_READY", "info", "Manifest is complete and frozen for controlled use."))
        return findings


def sha256_file(path: str | Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifests(manifest_dir: str | Path) -> list[tuple[Path, DatasetManifest]]:
    directory = Path(manifest_dir)
    paths = sorted((*directory.glob("*.yaml"), *directory.glob("*.yml")))
    return [(path, DatasetManifest.from_path(path)) for path in paths]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit VymoaGaurd PHM dataset manifests before training.")
    parser.add_argument("--manifest-dir", default="data/manifests", help="Directory containing flat YAML manifests.")
    parser.add_argument("--dataset-id", action="append", dest="dataset_ids", help="Audit only this dataset ID; repeat for multiple selected datasets.")
    parser.add_argument("--strict", action="store_true", help="Return exit code 1 when any manifest is not ready.")
    args = parser.parse_args(argv)

    reports = []
    exit_code = 0
    for path, manifest in load_manifests(args.manifest_dir):
        if args.dataset_ids and manifest.dataset_id not in args.dataset_ids:
            continue
        findings = manifest.audit()
        reports.append({"path": str(path), "manifest": manifest.to_dict(), "findings": [finding.to_dict() for finding in findings]})
        if args.strict and any(finding.status != "PASS" for finding in findings):
            exit_code = 1
    print(json.dumps(reports, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
