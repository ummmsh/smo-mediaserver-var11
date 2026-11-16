from __future__ import annotations

from smo.events.event import Event
from smo.events.event_type import EventType
from smo.model.request import Request
from smo.simulation.simulation_controller import SimulationController
from smo.simulation.system_state import SystemState
from ui.summary_view import print_summary


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
        _print_state(state, previous, step_no, sources)
        if input("> ").strip().lower() == "q":
            break
        step_no += 1
        previous, state = state, controller.step()
    while controller.step() is not None:
        pass
    print()
    print_summary(controller.run_auto(0))


def _print_state(
    state: SystemState,
    previous: SystemState | None,
    step_no: int,
    sources: int,
) -> None:
    times = {_owner(event): f"{event.time:.3f}" for event in state.calendar}
    current = _owner(state.last_event)

    source_line = "  ".join(
        f"{'*' if name == current else ''}{name} [{times.get(name, '-')}]"
        for name in (f"И{k}" for k in range(1, sources + 1))
    )
    buffer_line = " ".join(
        f"[{i}: {_label(cell)}]"
        for i, cell in enumerate(state.buffer_cells, start=1)
    )
    device_line = "  ".join(
        f"{'*' if f'П{i}' == current else ''}П{i} "
        + (f"[{_label(request)} до {times[f'П{i}']}]" if request else "[-]")
        for i, request in enumerate(state.devices, start=1)
    )
    calendar = ", ".join(
        f"{_owner(event)} {event.time:.3f}" for event in state.calendar
    )

    print()
    print("=" * 70)
    print(f"Шаг {step_no}, t = {state.time:.3f}, событие у {current}")
    print("=" * 70)
    print("Формализованная схема модели:")
    print(f"  И:  {source_line}")
    print("   |")
    print(f"  ДП ---> отказ (последний): {_label(state.last_evicted)}")
    print("   |")
    print(f"  БП: {buffer_line}")
    print("   |")
    print("  ДВ")
    print("   |")
    print(f"  П:  {device_line}")
    print()
    print("Действия на шаге:")
    for action in _actions(state, previous):
        print(f"  - {action}")
    print()
    print("Текущее состояние:")
    print(f"  pотк = {state.reject_rate:.4f}")
    print(f"  Календарь событий: {calendar or 'пуст'}")


def _actions(state: SystemState, previous: SystemState | None) -> list[str]:
    event = state.last_event
    if event.type is EventType.END_SERVICE:
        i = event.device.id
        done = previous.devices[i - 1] if previous else None
        taken = state.devices[i - 1]
        actions = [f"П{i} закончил обработку заявки {_label(done)} (ПЗ2)"]
        if taken is None:
            actions.append(f"БП пуст, П{i} простаивает")
        else:
            actions.append(
                f"ДВ выбрал из БП последнюю поступившую заявку "
                f"{_label(taken)} (Д2Б2) и отправил на П{i}"
            )
        return actions

    arrived = state.last_arrived
    if arrived is None:
        return [f"создано N заявок, {_owner(event)} больше не генерирует"]

    actions = [f"{_owner(event)} сгенерировал заявку {_label(arrived)} (ИЗ1)"]
    if previous and state.last_evicted is not previous.last_evicted:
        actions.append(
            f"БП переполнена, выбита самая старая заявка "
            f"{_label(state.last_evicted)} - отказ (Д1ОО3)"
        )
    else:
        actions.append(
            f"заявка {_label(arrived)} записана на первое свободное "
            f"место БП (Д1ОЗ3)"
        )
    if arrived in state.devices:
        i = state.devices.index(arrived) + 1
        actions.append(
            f"ДВ выбрал заявку {_label(arrived)} (Д2Б2) и отправил "
            f"на первый свободный прибор П{i} (Д2П1)"
        )
    else:
        actions.append("все приборы заняты, заявка ожидает в БП")
    return actions


def _owner(event: Event) -> str:
    if event.type is EventType.GENERATE:
        return str(event.source)
    return f"П{event.device.id}"


def _label(request: Request | None) -> str:
    if request is None:
        return "-"
    return f"{request.source_id}.{request.frame_no}"
