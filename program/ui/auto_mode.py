from __future__ import annotations

import math

from smo.simulation.simulation_controller import SimulationController
from smo.statistics.summary_table import SummaryTable
from ui.summary_view import render_summary, total_reject_rate

T_ALPHA = 1.643
DELTA = 0.1
MAX_ITERATIONS = 30


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
    table = _simulate(sources, devices, buffer_size, lam, a, b, n)
    p0 = total_reject_rate(table)
    print(f"N = {n}, pотк = {p0:.4f}")
    for _ in range(MAX_ITERATIONS):
        n = _required_n(p0, n)
        table = _simulate(sources, devices, buffer_size, lam, a, b, n)
        p1 = total_reject_rate(table)
        print(f"N = {n}, pотк = {p1:.4f}")
        if p0 > 0 and abs(p0 - p1) / p0 < DELTA:
            break
        p0 = p1
    print(f"Принято N = {n}")
    print()
    print(render_summary(table))


def _required_n(p: float, n: int) -> int:
    if p == 0:
        return n * 2
    return math.ceil(T_ALPHA**2 * (1 - p) / (p * DELTA**2))


def _simulate(
    sources: int,
    devices: int,
    buffer_size: int,
    lam: float,
    a: float,
    b: float,
    n_requests: int,
) -> SummaryTable:
    controller = SimulationController(
        sources, devices, buffer_size, lam, a, b, n_requests
    )
    return controller.run_auto(n_requests)
