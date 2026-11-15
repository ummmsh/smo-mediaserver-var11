from __future__ import annotations

import heapq

from smo.events.event import Event


class EventCalendar:
    def __init__(self) -> None:
        self._events: list[Event] = []
        self._current_time = 0.0

    def schedule(self, event: Event) -> None:
        heapq.heappush(self._events, event)

    def next(self) -> Event:
        event = heapq.heappop(self._events)
        self._current_time = event.time
        return event

    def is_empty(self) -> bool:
        return not self._events

    @property
    def current_time(self) -> float:
        return self._current_time

    def snapshot(self) -> list[Event]:
        return sorted(self._events)
