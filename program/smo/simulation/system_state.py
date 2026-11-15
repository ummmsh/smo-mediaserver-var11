from __future__ import annotations

from dataclasses import dataclass

from smo.events.event import Event
from smo.model.request import Request


@dataclass(frozen=True)
class SystemState:
    time: float
    last_event: Event
    last_arrived: Request | None
    last_evicted: Request | None
    buffer_cells: list[Request | None]
    devices: list[Request | None]
    reject_rate: float
    calendar: list[Event]
