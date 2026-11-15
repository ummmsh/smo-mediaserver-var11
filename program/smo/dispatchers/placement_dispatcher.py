from __future__ import annotations

from smo.dispatchers.selection_dispatcher import SelectionDispatcher
from smo.model.buffer import Buffer
from smo.model.put_status import PutStatus
from smo.model.request import Request
from smo.statistics.statistics import Statistics


class PlacementDispatcher:
    def __init__(
        self,
        buffer: Buffer,
        selection_dispatcher: SelectionDispatcher,
        statistics: Statistics,
    ) -> None:
        self._buffer = buffer
        self._selection_dispatcher = selection_dispatcher
        self._statistics = statistics

    def put(self, request: Request) -> None:
        result = self._buffer.put(request)
        if result.status is PutStatus.EVICTED:
            self._statistics.register_rejected(result.evicted)
        self._selection_dispatcher.on_buffer_changed()
