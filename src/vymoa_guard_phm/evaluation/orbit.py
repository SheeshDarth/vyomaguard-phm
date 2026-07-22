"""Reproducible ESA orbit holdout evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from time import perf_counter
from typing import Any

from vymoa_guard_phm.config import AssessmentConfig
from vymoa_guard_phm.data.adapters import load_zip_csv_records
from vymoa_guard_phm.data.manifest import DatasetManifest, sha256_file
from vymoa_guard_phm.data.orbit_target import select_final_cdm_rows
from vymoa_guard_phm.data.splits import group_temporal_split
from vymoa_guard_phm.evaluation.metrics import bootstrap_metric_ci, regression_ranking_metrics
from vymoa_guard_phm.models.orbit import OrbitRiskEngine


def evaluate_esa_orbit_holdout(
    archive_path: str | Path,
    *,
    manifest_path: str | Path = "data/manifests/esa_collision_avoidance.yaml",
    config: AssessmentConfig | None = None,
    test_fraction: float = 0.2,
    review_fraction: float = 0.1,
) -> dict[str, Any]:
    """Run a manifest-verified event-temporal Ridge baseline on local data."""

    started = perf_counter()
    manifest = DatasetManifest.from_path(manifest_path)
    findings = manifest.audit()
    if any(finding.status != "PASS" for finding in findings):
        raise ValueError("Manifest is not ready: " + ", ".join(finding.code for finding in findings))
    if not manifest.entity_fields:
        raise ValueError("Orbit manifest must declare an event/group field.")
    actual_checksum = sha256_file(archive_path)
    if actual_checksum.lower() != manifest.checksum.lower():
        raise ValueError(f"Artifact checksum mismatch: expected {manifest.checksum}, got {actual_checksum}.")

    raw_rows = load_zip_csv_records(archive_path)
    final_rows = [item.row for item in select_final_cdm_rows(raw_rows)]
    train_rows, test_rows = group_temporal_split(
        final_rows,
        group_key=manifest.entity_fields[0],
        time_key=manifest.time_field,
        test_fraction=test_fraction,
    )
    engine = OrbitRiskEngine(config).fit(train_rows, feature_allowlist=list(manifest.feature_fields))
    if not engine.fitted:
        raise ValueError("Orbit baseline could not fit the manifest-approved continuous target.")

    predictions: list[float] = []
    labels: list[float] = []
    for row in test_rows:
        assessment = engine.score(row)
        if assessment.raw_value is None:
            raise ValueError("Orbit baseline returned no raw continuous prediction.")
        labels.append(float(row["risk"]))
        predictions.append(assessment.raw_value)
    metrics = regression_ranking_metrics(labels, predictions, review_fraction=review_fraction)
    train_labels = [float(row["risk"]) for row in train_rows]
    constant_predictions = [sum(train_labels) / len(train_labels)] * len(labels)
    constant_metrics = regression_ranking_metrics(labels, constant_predictions, review_fraction=review_fraction)
    split_groups = {
        "train": sorted(str(row[manifest.entity_fields[0]]) for row in train_rows),
        "test": sorted(str(row[manifest.entity_fields[0]]) for row in test_rows),
    }
    predictions_hash = _payload_hash([round(value, 12) for value in predictions])
    split_hash = _payload_hash(split_groups)
    feature_allowlist_hash = _payload_hash(list(manifest.feature_fields))
    config = config or AssessmentConfig()
    config_hash = _payload_hash(config.to_dict())
    model_artifact = _model_artifact(engine)
    model_artifact_hash = _payload_hash(model_artifact)
    code_commit = _git_commit(Path(manifest_path).resolve().parents[2])
    run_identity = {
        "dataset_checksum": manifest.checksum.lower(),
        "manifest_schema": manifest.schema_version,
        "split_hash": split_hash,
        "feature_allowlist_hash": feature_allowlist_hash,
        "config_hash": config_hash,
        "model_artifact_hash": model_artifact_hash,
        "predictions_hash": predictions_hash,
        "code_commit": code_commit,
    }
    run_id = _payload_hash(run_identity)[:16]
    metrics["baseline_constant"] = constant_metrics
    metrics["uncertainty"] = {
        "spearman_95": bootstrap_metric_ci(labels, predictions, metric="spearman", review_fraction=review_fraction),
        "top_risk_recall_95": bootstrap_metric_ci(labels, predictions, metric="top_risk_recall", review_fraction=review_fraction),
    }
    metrics.update(
        {
            "dataset_id": manifest.dataset_id,
            "model_version": engine.config.orbit_model_version,
            "target_semantics": "base10_log_risk",
            "target_row_rule": "last_occurrence_by_event_id_in_source_order",
            "split_strategy": manifest.split_strategy,
            "time_order_field": manifest.time_field,
            "time_order_semantics": "proxy_only_until_decision-time_audit",
            "train_event_groups": float(len({row[manifest.entity_fields[0]] for row in train_rows})),
            "test_event_groups": float(len({row[manifest.entity_fields[0]] for row in test_rows})),
            "runtime_seconds": float(perf_counter() - started),
            "run_id": run_id,
            "code_commit": code_commit,
            "artifact_checksum": manifest.checksum.lower(),
            "feature_allowlist_hash": feature_allowlist_hash,
            "split_hash": split_hash,
            "predictions_hash": predictions_hash,
            "config_hash": config_hash,
            "model_artifact_hash": model_artifact_hash,
            "review_fraction": review_fraction,
            "review_count": float(max(1, int(math.ceil(len(labels) * review_fraction)))),
            "availability_contract_status": "BLOCKED_UNTIL_SIGNOFF",
            "model_artifact": model_artifact,
        }
    )
    return metrics


def _payload_hash(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _git_commit(repo_root: Path) -> str:
    configured = os.getenv("VYMOA_GUARD_PHM_COMMIT")
    if configured:
        return configured
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_root, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return "unknown"
    return result.stdout.strip() or "unknown"


def _model_artifact(engine: OrbitRiskEngine) -> dict[str, Any]:
    scaler = engine.model.named_steps["standardscaler"]
    ridge = engine.model.named_steps["ridge"]
    return {
        "type": "standard_scaler_ridge",
        "feature_names": engine.feature_names,
        "target_min": engine.target_min,
        "target_max": engine.target_max,
        "scaler_mean": [float(value) for value in scaler.mean_],
        "scaler_scale": [float(value) for value in scaler.scale_],
        "coefficients": [float(value) for value in ridge.coef_],
        "intercept": float(ridge.intercept_),
    }


def write_run_bundle(metrics: dict[str, Any], output_path: str | Path, *, model_artifact: dict[str, Any] | None = None) -> Path:
    """Persist a local ignored run bundle for independent replay review."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    bundle = {"metrics": metrics, "model_artifact": model_artifact or metrics.get("model_artifact", {})}
    path.write_text(json.dumps(_json_safe(bundle), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    return path


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate the VymoaGaurd PHM ESA orbit regression/ranking baseline.")
    parser.add_argument("--archive", required=True, help="Path to the ignored local ESA train_data.zip artifact.")
    parser.add_argument("--manifest", default="data/manifests/esa_collision_avoidance.yaml")
    parser.add_argument("--test-fraction", type=float, default=0.2)
    parser.add_argument("--review-fraction", type=float, default=0.1)
    parser.add_argument("--output", help="Optional local JSON run-bundle path; keep generated bundles out of Git.")
    args = parser.parse_args(argv)
    metrics = evaluate_esa_orbit_holdout(
        args.archive,
        manifest_path=args.manifest,
        test_fraction=args.test_fraction,
        review_fraction=args.review_fraction,
    )
    model_artifact = metrics.pop("model_artifact", {})
    if args.output:
        write_run_bundle(metrics, args.output, model_artifact=model_artifact)
    print(json.dumps(_json_safe(metrics), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
