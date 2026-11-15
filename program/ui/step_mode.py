from __future__ import annotations

from smo.simulation.simulation_controller import SimulationController
from ui.state_view import render_state
from ui.summary_view import render_summary


def run_step_mode(
    sources: int,
    devices: int,
    buffer_size: int,
    lam: float,
    a: float,
    b: float,
    n_requests: int,
) -> None:
    controller = SimulationController(
        sources, devices, buffer_size, lam, a, b, n_requests
    )
    print("Enter - следующий шаг, q - досчитать до окончания моделирования")
    step_no = 1
    previous = None
    state = controller.step()
    while state is not None:
        print(render_state(state, previous, step_no, sources))
        if input("> ").strip().lower() == "q":
            break
        step_no += 1
        previous = state
        state = controller.step()
    while controller.step() is not None:
        pass
    print()
    print(render_summary(controller.run_auto(0)))
