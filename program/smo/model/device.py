from __future__ import annotations

from typing import TYPE_CHECKING

from smo.events.event import Event
from smo.events.event_calendar import EventCalendar
from smo.events.event_type import EventType
from smo.laws.random_law import RandomLaw
from smo.model.request import Request
from smo.statistics.statistics import Statistics

if TYPE_CHECKING:
    from smo.dispatchers.selection_dispatcher import SelectionDispatcher


class Device:
    def __init__(
        self,
        device_id: int,
        law: RandomLaw,
        calendar: EventCalendar,
        dispatcher: SelectionDispatcher,
        statistics: Statistics,
    ) -> None:
        self._id = device_id
        self._current: Request | None = None
        self._busy_time = 0.0
        self._law = law
        self._calendar = calendar
        self._dispatcher = dispatcher
        self._statistics = statistics

    def start_service(self, request: Request, t: float) -> None:
        self._current = request
        request.set_service_start(t, self._id)
        time = t + self._law.next()
        event = Event(time, EventType.END_SERVICE, device=self)
        self._calendar.schedule(event)

    def on_service_end(self, t: float) -> None:
        request = self._current
        request.set_service_end(t)
        self._busy_time += t - request.service_start_time
        self._current = None
        self._statistics.register_processed(request)
        self._dispatcher.on_device_released(self)

    def is_busy(self) -> bool:
        return self._current is not None

    @property
    def id(self) -> int:
        return self._id

    @property
    def current(self) -> Request | None:
        return self._current

    @property
    def busy_time(self) -> float:
        return self._busy_time
