from __future__ import annotations

import random

from smo.laws.random_law import RandomLaw


class UniformLaw(RandomLaw):
    def __init__(self, a: float, b: float) -> None:
        self._a = a
        self._b = b

    def next(self) -> float:
        return random.uniform(self._a, self._b)
