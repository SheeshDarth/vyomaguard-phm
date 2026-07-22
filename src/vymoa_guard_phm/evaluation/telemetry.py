"""Reproducible OPSSAT-AD telemetry anomaly evaluation."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.data.adapters import load_csv_records
from vymoa_guard_phm.data.manifest import DatasetManifest, sha256_file
from vymoa_guard_phm.data.splits import group_temporal_split
from vymoa_guard_phm.evaluation.metrics import anomaly_detection_metrics
from vymoa_guard_phm.models.telemetry import TelemetryAnomalyEngine

TELEMETRY_TARGET_FIELD = "anomaly"
TELEMETRY_CONTRACT_ID = "esa-opssat-telemetry-v1"
DESCRIPTIVE_THRESHOLD_GRID = (0.25, 0.50, 0.65, 0.75, 0.90)


def _binary_segment_label(rows: list[dict[str, Any]], target_field: str) -> int:
    labels: set[int] = set()
    for row in rows:
        raw_label = row.get(target_field)
        if raw_label is None or str(raw_label).strip() == "":
            raise ValueError(f"Missing target field {target_field!r} in segment.")
        try:
            label = int(float(raw_label))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Target field {target_field!r} must be binary numeric data.") from exc
        if label not in {0, 1}:
            raise ValueError(f"Target field {target_field!r} must contain only 0 or 1; got {label}.")
        labels.add(label)
    if len(labels) != 1:
        raise ValueError(f"Contradictory labels found within one segment: {sorted(labels)}.")
    return labels.pop()


def _group_by_segment(rows: list[dict[str, Any]], segment_field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        segment = str(row.get(segment_field, "")).strip()
        if not segment:
            raise ValueError(f"Missing segment field {segment_field!r}.")
        grouped.setdefault(segment, []).append(row)
    return grouped


def _validate_manifest(manifest: DatasetManifest, segments_path: Path) -> None:
    findings = manifest.audit()
    failures = [finding.message for finding in findings if finding.status == "FAIL"]
    if failures:
        raise ValueError("Manifest audit failed: " + " | ".join(failures))
    if manifest.status.upper() != "FROZEN":
        raise ValueError("Telemetry evaluation requires a frozen dataset manifest.")
    if manifest.split_strategy != "group_temporal":
        raise ValueError("OPSSAT evaluation requires the manifest split strategy 'group_temporal'.")
    if sha256_file(segments_path) != manifest.checksum:
        raise ValueError(f"Checksum mismatch for {segments_path}; refresh the manifest before evaluation.")
    declared_fields = {manifest.time_field, *manifest.entity_fields, *manifest.feature_fields}
    missing_fields = {manifest.time_field, "segment", "channel", "value"} - declared_fields
    if missing_fields:
        raise ValueError(f"Telemetry manifest is missing declared fields: {sorted(missing_fields)}.")


def evaluate_opssat_holdout(
    segments_path: str | Path,
    manifest_path: str | Path = "data/manifests/esa_opssat_ad.yaml",
    *,
    config: AssessmentConfig | None = None,
    test_fraction: float = 0.2,
) -> dict[str, Any]:
    """Fit on chronological nominal segments and score a disjoint holdout."""

    started = time.perf_counter()
    path = Path(segments_path)
    manifest = DatasetManifest.from_path(manifest_path)
    _validate_manifest(manifest, path)
    rows = load_csv_records(path)
    if not rows:
        raise ValueError("OPSSAT segments file is empty.")
    segment_field = manifest.entity_fields[0] if manifest.entity_fields else "segment"
    train_rows, test_rows = group_temporal_split(
        rows,
        group_key=segment_field,
        time_key=manifest.time_field,
        test_fraction=test_fraction,
    )
    train_segments = _group_by_segment(train_rows, segment_field)
    test_segments = _group_by_segment(test_rows, segment_field)
    for segment_rows in train_segments.values():
        _binary_segment_label(segment_rows, TELEMETRY_TARGET_FIELD)
    engine = TelemetryAnomalyEngine(config or AssessmentConfig()).fit(train_rows)

    labels: list[int] = []
    scores: list[float] = []
    iforest_scores: list[float] = []
    scored_segments = 0
    for segment in sorted(test_segments):
        segment_rows = test_segments[segment]
        labels.append(_binary_segment_label(segment_rows, TELEMETRY_TARGET_FIELD))
        assessment = engine.score(segment_rows)
        iforest_assessment = engine.score(segment_rows, use_iforest=True)
        if assessment.score is None:
            continue
        scores.append(float(assessment.score))
        if iforest_assessment.score is None:
            raise ValueError("Isolation Forest comparison abstained on a labeled holdout segment.")
        iforest_scores.append(float(iforest_assessment.score))
        scored_segments += 1
    if scored_segments != len(labels):
        raise ValueError("Telemetry engine abstained on one or more labeled holdout segments.")

    selected_config = config or AssessmentConfig()
    runtime_seconds = time.perf_counter() - started
    return {
        "dataset_id": manifest.dataset_id,
        "contract_id": TELEMETRY_CONTRACT_ID,
        "source_snapshot": manifest.source_snapshot,
        "manifest_checksum": manifest.checksum,
        "evaluation_unit": "segment",
        "evidence_unit": "row/channel/window; localization is not label-validated",
        "target_semantics": "audited binary anomaly label",
        "target_field": TELEMETRY_TARGET_FIELD,
        "score_type": "anomaly_score",
        "probability_claim": False,
        "fit_scope": "nominal rows from chronological training segments only",
        "alert_policy": "one aggregated score per segment; no persistence, debounce, or hysteresis",
        "split_strategy": manifest.split_strategy,
        "test_fraction": float(test_fraction),
        "train_segments": len(train_segments),
        "test_segments": len(test_segments),
        "train_rows": len(train_rows),
        "test_rows": len(test_rows),
        "model_version": engine.model_version,
        "selected_baseline": "robust_rolling_statistics",
        "selection_note": "Isolation Forest is reported as a comparison and is not fused because this holdout is exploratory and the comparison increases false alarms.",
        "threshold": selected_config.telemetry_anomaly_threshold,
        "threshold_selection": "fixed configuration; not selected or tuned on the locked holdout",
        "threshold_sweep_is_descriptive": True,
        "runtime_seconds": round(runtime_seconds, 6),
        "metrics": anomaly_detection_metrics(
            labels,
            scores,
            threshold=selected_config.telemetry_anomaly_threshold,
        ),
        "iforest_comparison_metrics": anomaly_detection_metrics(
            labels,
            iforest_scores,
            threshold=selected_config.telemetry_anomaly_threshold,
        ),
        "threshold_sweep": [
            {
                "threshold": threshold,
                "metrics": anomaly_detection_metrics(labels, scores, threshold=threshold),
            }
            for threshold in DESCRIPTIVE_THRESHOLD_GRID
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the VymoaGaurd PHM telemetry anomaly baseline.")
    parser.add_argument("--segments", default="data/downloads/opssat-ad/segments.csv")
    parser.add_argument("--manifest", default="data/manifests/esa_opssat_ad.yaml")
    parser.add_argument("--output", help="Optional JSON output path.")
    parser.add_argument("--test-fraction", type=float, default=0.2)
    args = parser.parse_args(argv)
    report = evaluate_opssat_holdout(args.segments, args.manifest, test_fraction=args.test_fraction)
    payload = json.dumps(report, indent=2, sort_keys=True, allow_nan=False)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
