"""Machine-testable target construction for the ESA orbit dataset.

The ESA training archive is an ordered event stream.  The source-defined
target is the risk value on the last observed row for each event, so this
module deliberately never sorts by ``time_to_tca``.  The source row index is
the deterministic tie-breaker for repeated event rows.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class FinalCdmRow:
    event_id: str
    source_row_index: int
    row: dict[str, Any]


@dataclass(frozen=True)
class OrbitRiskTarget:
    event_id: str
    source_row_index: int
    value: float


def select_final_cdm_rows(
    rows: Iterable[Mapping[str, Any]], *, event_key: str = "event_id"
) -> list[FinalCdmRow]:
    """Select the last source-order row for each event.

    The result is ordered by each event's first appearance in the source.
    Missing or blank event identifiers are rejected because silently grouping
    them would make target provenance ambiguous.
    """

    selected: dict[str, FinalCdmRow] = {}
    event_order: list[str] = []
    for source_row_index, raw_row in enumerate(rows):
        event_id = str(raw_row.get(event_key, "")).strip()
        if not event_id:
            raise ValueError(f"Missing {event_key!r} at source row {source_row_index}.")
        if event_id not in selected:
            event_order.append(event_id)
        selected[event_id] = FinalCdmRow(event_id, source_row_index, dict(raw_row))
    return [selected[event_id] for event_id in event_order]


def extract_final_risk_targets(
    rows: Iterable[Mapping[str, Any]], *, event_key: str = "event_id", target_key: str = "risk"
) -> list[OrbitRiskTarget]:
    """Extract finite continuous log-risk values from final CDM rows."""

    targets: list[OrbitRiskTarget] = []
    for final_row in select_final_cdm_rows(rows, event_key=event_key):
        raw_value = final_row.row.get(target_key)
        try:
            value = float(raw_value)
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"Invalid {target_key!r} for event {final_row.event_id!r} "
                f"at source row {final_row.source_row_index}."
            ) from exc
        if not math.isfinite(value):
            raise ValueError(
                f"Non-finite {target_key!r} for event {final_row.event_id!r} "
                f"at source row {final_row.source_row_index}."
            )
        targets.append(OrbitRiskTarget(final_row.event_id, final_row.source_row_index, value))
    return targets
