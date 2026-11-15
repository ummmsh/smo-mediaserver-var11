from __future__ import annotations

from smo.dispatchers.placement_dispatcher import PlacementDispatcher
from smo.dispatchers.selection_dispatcher import SelectionDispatcher
from smo.events.event import Event
from smo.events.event_calendar import EventCalendar
from smo.events.event_type import EventType
from smo.laws.exponential_law import ExponentialLaw
from smo.laws.uniform_law import UniformLaw
from smo.model.buffer import Buffer
from smo.model.device import Device
from smo.model.source import Source
from smo.simulation.system_state import SystemState
from smo.statistics.statistics import Statistics
from smo.statistics.summary_table import SummaryTable


class SimulationController:
    def __init__(
        self,
        sources: int,
        devices: int,
        buffer_size: int,
        lam: float,
        a: float,
        b: float,
        max_requests: int,
    ) -> None:
        self._calendar = EventCalendar()
        self._statistics = Statistics(sources)
        self._buffer = Buffer(buffer_size)
        self._devices: list[Device] = []
        self._selection = SelectionDispatcher(
            self._buffer, self._devices, self._statistics, self._calendar
        )
        self._placement = PlacementDispatcher(
            self._buffer, self._selection, self._statistics
        )
        for i in range(1, devices + 1):
            self._devices.append(
                Device(
                    i,
                    UniformLaw(a, b),
                    self._calendar,
                    self._selection,
                    self._statistics,
                )
            )
        self._sources = [
            Source(
                k,
                ExponentialLaw(lam),
                self._calendar,
                self._placement,
                self._statistics,
            )
            for k in range(1, sources + 1)
        ]
        self._max_requests = max_requests
        for source in self._sources:
            source.schedule_next(0.0)

    def step(self) -> SystemState | None:
        if self._calendar.is_empty():
            return None
        event = self._calendar.next()
        self._dispatch(event)
        return self._build_state(event)

    def run_auto(self, n_requests: int) -> SummaryTable:
        self._max_requests = n_requests
        while not self._calendar.is_empty():
            self._dispatch(self._calendar.next())
        return self._statistics.build_summary_table(
            self._devices, self._calendar.current_time
        )

    def _dispatch(self, event: Event) -> None:
        if event.type is EventType.END_SERVICE:
            event.device.on_service_end(event.time)
        elif self._max_requests > 0:
            self._max_requests -= 1
            event.source.on_generate(event.time)

    def _build_state(self, event: Event) -> SystemState:
        devices = [device.current for device in self._devices]
        arrived = None
        if event.type is EventType.GENERATE:
            for request in self._buffer.cells + devices:
                if request and request.arrival_time == event.time:
                    arrived = request
        return SystemState(
            time=event.time,
            last_event=event,
            last_arrived=arrived,
            last_evicted=self._statistics.last_evicted,
            buffer_cells=self._buffer.cells,
            devices=devices,
            reject_rate=self._statistics.reject_rate,
            calendar=self._calendar.snapshot(),
        )
