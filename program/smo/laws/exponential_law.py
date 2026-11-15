from __future__ import annotations

import random

from smo.laws.random_law import RandomLaw


class ExponentialLaw(RandomLaw):
    def __init__(self, lam: float) -> None:
        self._lambda = lam

    def next(self) -> float:
        return random.expovariate(self._lambda)
