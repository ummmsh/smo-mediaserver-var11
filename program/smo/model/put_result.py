from __future__ import annotations

from dataclasses import dataclass

from smo.model.put_status import PutStatus
from smo.model.request import Request


@dataclass(frozen=True)
class PutResult:
    status: PutStatus
    cell_index: int
    evicted: Request | None
