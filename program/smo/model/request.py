from __future__ import annotations


class Request:
    def __init__(
        self,
        source_id: int,
        frame_no: int,
        arrival_time: float,
    ) -> None:
        self._source_id = source_id
        self._frame_no = frame_no
        self._arrival_time = arrival_time
        self._service_start_time = 0.0
        self._service_end_time = 0.0
        self._device_id = 0

    @property
    def source_id(self) -> int:
        return self._source_id

    @property
    def frame_no(self) -> int:
        return self._frame_no

    @property
    def arrival_time(self) -> float:
        return self._arrival_time

    @property
    def service_start_time(self) -> float:
        return self._service_start_time

    @property
    def service_end_time(self) -> float:
        return self._service_end_time

    def set_service_start(self, t: float, device_id: int) -> None:
        self._service_start_time = t
        self._device_id = device_id

    def set_service_end(self, t: float) -> None:
        self._service_end_time = t
