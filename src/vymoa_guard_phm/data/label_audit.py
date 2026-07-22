"""Small, explicit label-audit primitives for dataset onboarding."""

from __future__ import annotations

from collections import Counter
from typing import Any


def audit_binary_labels(rows: list[dict[str, Any]], label_key: str = "label") -> dict[str, Any]:
    labels = [row.get(label_key) for row in rows if row.get(label_key) is not None]
    counts = Counter(labels)
    return {
        "rows": len(rows),
        "labeled_rows": len(labels),
        "unique_labels": sorted(str(label) for label in counts),
        "label_counts": {str(label): count for label, count in counts.items()},
        "supports_binary_training": len(counts) == 2,
        "status": "PASS" if len(counts) == 2 else "REVIEW_REQUIRED",
    }

