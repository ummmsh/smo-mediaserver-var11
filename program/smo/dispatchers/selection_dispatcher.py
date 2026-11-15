from __future__ import annotations

from typing import TYPE_CHECKING

from smo.events.event_calendar import EventCalendar
from smo.model.buffer import Buffer
from smo.statistics.statistics import Statistics

if TYPE_CHECKING:
    from smo.model.device import Device


class SelectionDispatcher:
    def __init__(
        self,
        buffer: Buffer,
        devices: list[Device],
        statistics: Statistics,
        calendar: EventCalendar,
    ) -> None:
        self._buffer = buffer
        self._devices = devices
        self._statistics = statistics
        self._calendar = calendar

    def on_buffer_changed(self) -> None:
        device = self._find_free_device()
        if device is not None:
            self._start_from_buffer(device)

    def on_device_released(self, device: Device) -> None:
        if not self._buffer.is_empty():
            self._start_from_buffer(device)

    def _find_free_device(self) -> Device | None:
        for device in self._devices:
            if not device.is_busy():
                return device
        return None

    def _start_from_buffer(self, device: Device) -> None:
        t = self._calendar.current_time
        request = self._buffer.take_latest()
        self._statistics.register_waiting(request, t - request.arrival_time)
        device.start_service(request, t)
