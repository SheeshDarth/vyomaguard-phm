"""Metrics used by the acceptance matrix."""

from __future__ import annotations

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

