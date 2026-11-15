from __future__ import annotations

from typing import TYPE_CHECKING

from smo.model.request import Request
from smo.statistics.summary_table import SummaryTable

if TYPE_CHECKING:
    from smo.model.device import Device


class Statistics:
    def __init__(self, sources: int) -> None:
        self._generated = [0] * sources
        self._rejected = [0] * sources
        self._processed = [0] * sources
        self._sum_wait = [0.0] * sources
        self._sum_wait2 = [0.0] * sources
        self._sum_service = [0.0] * sources
        self._sum_service2 = [0.0] * sources
        self._sum_in_system = [0.0] * sources
        self._last_evicted: Request | None = None

    def register_generated(self, request: Request) -> None:
        self._generated[request.source_id - 1] += 1

    def register_rejected(self, request: Request) -> None:
        self._rejected[request.source_id - 1] += 1
        self._last_evicted = request

    def register_waiting(self, request: Request, wait: float) -> None:
        k = request.source_id - 1
        self._sum_wait[k] += wait
        self._sum_wait2[k] += wait**2

    def register_processed(self, request: Request) -> None:
        k = request.source_id - 1
        service = request.service_end_time - request.service_start_time
        self._processed[k] += 1
        self._sum_service[k] += service
        self._sum_service2[k] += service**2
        self._sum_in_system[k] += (
            request.service_end_time - request.arrival_time
        )

    @property
    def reject_rate(self) -> float:
        generated = sum(self._generated)
        return sum(self._rejected) / generated if generated else 0.0

    @property
    def last_evicted(self) -> Request | None:
        return self._last_evicted

    def build_summary_table(
        self,
        devices: list[Device],
        time: float,
    ) -> SummaryTable:
        per_source = []
        for k, generated in enumerate(self._generated):
            processed = self._processed[k]
            reject_rate = self._rejected[k] / generated if generated else 0.0
            if processed == 0:
                per_source.append((generated, reject_rate, 0, 0, 0, 0, 0))
                continue
            in_system = self._sum_in_system[k] / processed
            wait = self._sum_wait[k] / processed
            service = self._sum_service[k] / processed
            wait_var = self._sum_wait2[k] / processed - wait**2
            service_var = self._sum_service2[k] / processed - service**2
            per_source.append(
                (
                    generated,
                    reject_rate,
                    in_system,
                    wait,
                    service,
                    max(wait_var, 0.0),
                    max(service_var, 0.0),
                )
            )
        per_device = [
            device.busy_time / time if time else 0.0 for device in devices
        ]
        return SummaryTable(per_source, per_device)
