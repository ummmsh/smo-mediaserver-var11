from __future__ import annotations

import math

from smo.simulation.simulation_controller import SimulationController
from ui.summary_view import print_summary, reject_rate

T_ALPHA = 1.643
DELTA = 0.1
MAX_ITERATIONS = 10


def run_auto_mode(
    sources: int,
    devices: int,
    buffer_size: int,
    lam: float,
    a: float,
    b: float,
    n_requests: int,
) -> None:
    n = n_requests
    p0 = 0.0
    for _ in range(MAX_ITERATIONS):
        controller = SimulationController(
            sources, devices, buffer_size, lam, a, b, n
        )
        table = controller.run_auto(n)
        accepted = n
        p1 = reject_rate(table)
        print(f"N = {n}, pотк = {p1:.4f}")
        if p0 > 0 and abs(p0 - p1) / p0 < DELTA:
            break
        p0 = p1
        if p1 > 0:
            n = math.ceil(T_ALPHA**2 * (1 - p1) / (p1 * DELTA**2))
        else:
            n *= 2
    print(f"Принято N = {accepted}")
    print()
    print_summary(table)
