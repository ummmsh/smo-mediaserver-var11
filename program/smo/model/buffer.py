from __future__ import annotations

from smo.model.put_result import PutResult
from smo.model.put_status import PutStatus
from smo.model.request import Request


class Buffer:
    def __init__(self, size: int) -> None:
        self._cells: list[Request | None] = [None] * size

    def put(self, request: Request) -> PutResult:
        index = self._find_first_free()
        if index is not None:
            self._cells[index] = request
            return PutResult(PutStatus.STORED, index, None)
        index = self._index_of_oldest()
        evicted = self._cells[index]
        self._cells[index] = request
        return PutResult(PutStatus.EVICTED, index, evicted)

    def take_latest(self) -> Request:
        index = self._index_of_latest()
        request = self._cells[index]
        self._cells[index] = None
        return request

    def is_empty(self) -> bool:
        return all(cell is None for cell in self._cells)

    @property
    def cells(self) -> list[Request | None]:
        return list(self._cells)

    def _find_first_free(self) -> int | None:
        for index, cell in enumerate(self._cells):
            if cell is None:
                return index
        return None

    def _index_of_oldest(self) -> int:
        occupied = [i for i, cell in enumerate(self._cells) if cell]
        return min(occupied, key=lambda i: self._cells[i].arrival_time)

    def _index_of_latest(self) -> int:
        occupied = [i for i, cell in enumerate(self._cells) if cell]
        return max(occupied, key=lambda i: self._cells[i].arrival_time)
