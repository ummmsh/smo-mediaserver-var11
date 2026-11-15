from __future__ import annotations

from abc import ABC, abstractmethod


class RandomLaw(ABC):
    @abstractmethod
    def next(self) -> float:
        pass
