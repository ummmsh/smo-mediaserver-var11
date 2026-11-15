from __future__ import annotations

from typing import TYPE_CHECKING

from smo.events.event_type import EventType

if TYPE_CHECKING:
    from smo.model.device import Device
    from smo.model.source import Source


class Event:
    def __init__(
        self,
        time: float,
        event_type: EventType,
        source: Source | None = None,
        device: Device | None = None,
    ) -> None:
        self._time = time
        self._type = event_type
        self._source = source
        self._device = device

    @property
    def time(self) -> float:
        return self._time

    @property
    def type(self) -> EventType:
        return self._type

    @property
    def source(self) -> Source | None:
        return self._source

    @property
    def device(self) -> Device | None:
        return self._device

    def __lt__(self, other: Event) -> bool:
        return self._time < other.time
