from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryTable:
    per_source: list[tuple[int, float, float, float, float, float, float]]
    per_device: list[float]
