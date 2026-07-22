"""Metrics used by the acceptance matrix."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np
from sklearn.metrics import average_precision_score, f1_score, precision_score, recall_score, roc_auc_score


def expected_calibration_error(y_true: Iterable[int], scores: Iterable[float], bins: int = 10) -> float:
    labels = np.asarray(list(y_true), dtype=float)
    probabilities = np.asarray(list(scores), dtype=float)
    if len(labels) == 0:
        return 0.0
    edges = np.linspace(0.0, 1.0, bins + 1)
    error = 0.0
    for lower, upper in zip(edges[:-1], edges[1:]):
        mask = (probabilities >= lower) & (probabilities < upper if upper < 1.0 else probabilities <= upper)
        if not mask.any():
            continue
        error += float(mask.mean()) * abs(float(labels[mask].mean()) - float(probabilities[mask].mean()))
    return float(error)


def binary_metrics(y_true: Iterable[int], scores: Iterable[float], threshold: float = 0.5) -> dict[str, float]:
    labels = np.asarray(list(y_true), dtype=int)
    probabilities = np.asarray(list(scores), dtype=float)
    predictions = (probabilities >= threshold).astype(int)
    result = {
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "false_negative_rate": float(1.0 - recall_score(labels, predictions, zero_division=0)),
        "expected_calibration_error": expected_calibration_error(labels, probabilities),
    }
    if len(np.unique(labels)) == 2:
        result["roc_auc"] = float(roc_auc_score(labels, probabilities))
        result["pr_auc"] = float(average_precision_score(labels, probabilities))
    else:
        result["roc_auc"] = float("nan")
        result["pr_auc"] = float("nan")
    return result


def anomaly_detection_metrics(
    y_true: Iterable[int], scores: Iterable[float], threshold: float = 0.65
) -> dict[str, float | int | None]:
    """Evaluate bounded anomaly scores without treating them as probabilities."""

    labels = np.asarray(list(y_true), dtype=int)
    anomaly_scores = np.asarray(list(scores), dtype=float)
    if len(labels) != len(anomaly_scores):
        raise ValueError("y_true and scores must have equal length.")
    if len(labels) == 0:
        return {
            "n": 0,
            "positive_count": 0,
            "threshold": float(threshold),
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "false_negative_rate": 0.0,
            "false_alarm_rate": None,
            "roc_auc": None,
            "pr_auc": None,
        }
    predictions = (anomaly_scores >= threshold).astype(int)
    negatives = int(np.sum(labels == 0))
    false_alarms = int(np.sum((labels == 0) & (predictions == 1)))
    result: dict[str, float | int | None] = {
        "n": int(len(labels)),
        "positive_count": int(np.sum(labels == 1)),
        "threshold": float(threshold),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "false_negative_rate": float(1.0 - recall_score(labels, predictions, zero_division=0)),
        "false_alarm_rate": float(false_alarms / negatives) if negatives else None,
        "roc_auc": None,
        "pr_auc": None,
    }
    if len(np.unique(labels)) == 2:
        result["roc_auc"] = float(roc_auc_score(labels, anomaly_scores))
        result["pr_auc"] = float(average_precision_score(labels, anomaly_scores))
    return result


def _ordinal_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(1, len(values) + 1, dtype=float)
    return ranks


def regression_ranking_metrics(
    y_true: Iterable[float], predictions: Iterable[float], *, review_fraction: float = 0.1
) -> dict[str, float]:
    """Evaluate source-defined continuous risk without probability language."""

    labels = np.asarray(list(y_true), dtype=float)
    scores = np.asarray(list(predictions), dtype=float)
    if len(labels) != len(scores):
        raise ValueError("y_true and predictions must have equal length.")
    if len(labels) == 0:
        return {"n": 0.0, "mae": 0.0, "rmse": 0.0, "spearman": float("nan"), "top_risk_recall": 0.0}
    if not 0.0 < review_fraction <= 1.0:
        raise ValueError("review_fraction must be in the interval (0, 1].")
    residuals = scores - labels
    top_n = max(1, math.ceil(len(labels) * review_fraction))
    actual_top = set(np.argsort(labels, kind="mergesort")[-top_n:])
    predicted_top = set(np.argsort(scores, kind="mergesort")[-top_n:])
    if len(np.unique(labels)) > 1 and len(np.unique(scores)) > 1:
        spearman = float(np.corrcoef(_ordinal_ranks(labels), _ordinal_ranks(scores))[0, 1])
    else:
        spearman = float("nan")
    return {
        "n": float(len(labels)),
        "mae": float(np.mean(np.abs(residuals))),
        "rmse": float(np.sqrt(np.mean(np.square(residuals)))),
        "spearman": spearman,
        "top_risk_recall": float(len(actual_top & predicted_top) / len(actual_top)),
    }


def bootstrap_metric_ci(
    y_true: Iterable[float],
    predictions: Iterable[float],
    *,
    metric: str,
    review_fraction: float = 0.1,
    iterations: int = 200,
    random_seed: int = 42,
) -> dict[str, float]:
    """Return deterministic percentile intervals for a ranking metric."""

    labels = np.asarray(list(y_true), dtype=float)
    scores = np.asarray(list(predictions), dtype=float)
    if len(labels) != len(scores):
        raise ValueError("y_true and predictions must have equal length.")
    if iterations < 1:
        raise ValueError("iterations must be positive.")
    if metric not in {"spearman", "top_risk_recall"}:
        raise ValueError(f"Unsupported bootstrap metric: {metric!r}.")
    if len(labels) == 0:
        return {"lower": float("nan"), "upper": float("nan")}
    rng = np.random.default_rng(random_seed)
    values: list[float] = []
    for _ in range(iterations):
        sample = rng.integers(0, len(labels), size=len(labels))
        value = regression_ranking_metrics(labels[sample], scores[sample], review_fraction=review_fraction)[metric]
        if math.isfinite(value):
            values.append(value)
    if not values:
        return {"lower": float("nan"), "upper": float("nan")}
    return {"lower": float(np.percentile(values, 2.5)), "upper": float(np.percentile(values, 97.5))}
