from __future__ import annotations

from typing import TYPE_CHECKING

from smo.events.event import Event
from smo.events.event_calendar import EventCalendar
from smo.events.event_type import EventType
from smo.laws.random_law import RandomLaw
from smo.model.request import Request
from smo.statistics.statistics import Statistics

if TYPE_CHECKING:
    from smo.dispatchers.placement_dispatcher import PlacementDispatcher


class Source:
    def __init__(
        self,
        source_id: int,
        law: RandomLaw,
        calendar: EventCalendar,
        dispatcher: PlacementDispatcher,
        statistics: Statistics,
    ) -> None:
        self._id = source_id
        self._frame_counter = 0
        self._law = law
        self._calendar = calendar
        self._dispatcher = dispatcher
        self._statistics = statistics

    def schedule_next(self, t: float) -> None:
        time = t + self._law.next()
        self._calendar.schedule(Event(time, EventType.GENERATE, self))

    def on_generate(self, t: float) -> None:
        request = self._generate_request(t)
        self._statistics.register_generated(request)
        self.schedule_next(t)
        self._dispatcher.put(request)

    def _generate_request(self, t: float) -> Request:
        self._frame_counter += 1
        return Request(self._id, self._frame_counter, t)

    def __str__(self) -> str:
        return f"И{self._id}"
