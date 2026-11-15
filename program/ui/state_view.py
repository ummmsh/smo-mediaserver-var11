from __future__ import annotations

from smo.events.event import Event
from smo.events.event_type import EventType
from smo.model.request import Request
from smo.simulation.system_state import SystemState


def render_state(
    state: SystemState,
    previous: SystemState | None,
    step_no: int,
    sources: int,
) -> str:
    return "\n".join(
        [
            "",
            "=" * 70,
            f"Шаг {step_no}",
            "=" * 70,
            "Формализованная схема модели:",
            _render_scheme(state, sources),
            "",
            "Действия на шаге:",
            *(f"  - {action}" for action in _actions(state, previous)),
            "",
            "Текущее состояние:",
            _render_current_state(state),
        ]
    )


def _render_scheme(state: SystemState, sources: int) -> str:
    times = {_owner(event): event.time for event in state.calendar}
    current = _owner(state.last_event)

    source_texts = []
    for k in range(1, sources + 1):
        name = f"И{k}"
        mark = "*" if name == current else " "
        source_texts.append(f"{mark}{name} [{_time(times.get(name))}]")

    cell_texts = [
        f"[{i}: {_label(cell):>5}]"
        for i, cell in enumerate(state.buffer_cells, start=1)
    ]

    device_texts = []
    for i, request in enumerate(state.devices, start=1):
        name = f"П{i}"
        mark = "*" if name == current else " "
        if request is None:
            device_texts.append(f"{mark}{name} [свободен]")
        else:
            end = _time(times.get(name))
            device_texts.append(f"{mark}{name} [{_label(request)} до {end}]")

    source_width = max(len(text) for text in source_texts)
    cell_width = max(len(text) for text in cell_texts)
    rows = max(len(source_texts), len(cell_texts), len(device_texts))

    lines = []
    for r in range(rows):
        if r < len(source_texts):
            line = source_texts[r].ljust(source_width) + " ─"
        else:
            line = " " * (source_width + 2)
        line += _junction(r, len(source_texts), "|", "|", "|")
        line += "- ДП - БП   " if r == 0 else "   |        "
        cell = cell_texts[r] if r < len(cell_texts) else ""
        line += cell.ljust(cell_width)
        line += " - ДВ ─ " if r == 0 else " " * 8
        line += _junction(r, len(device_texts), "|", "|", "|")
        if r < len(device_texts):
            line += "─ " + device_texts[r]
        lines.append(line.rstrip())

    evicted = _label(state.last_evicted)
    lines.append(
        " " * (source_width + 6) + f"|_ отказ (последний): {evicted}"
    )
    lines.append("")
    lines.append(
        "И - момент генерации следующей заявки, БП - номера заявок "
        "в местах буфера,"
    )
    lines.append(
        "П - заявка на приборе и момент окончания обслуживания, "
        "* - особое событие шага"
    )
    return "\n".join(lines)


def _junction(r: int, count: int, first: str, middle: str, last: str) -> str:
    if r >= count:
        return " "
    if count == 1:
        return "─"
    if r == 0:
        return first
    if r == count - 1:
        return last
    return middle


def _actions(state: SystemState, previous: SystemState | None) -> list[str]:
    event = state.last_event
    if event.type is EventType.END_SERVICE:
        return _service_end_actions(state, previous)

    arrived = state.last_arrived
    if arrived is None:
        return [f"создано N заявок, {_owner(event)} больше не генерирует"]

    actions = [f"{_owner(event)} сгенерировал заявку {_label(arrived)} (ИЗ1)"]
    previous_evicted = previous.last_evicted if previous else None
    if state.last_evicted is not previous_evicted:
        place = state.buffer_cells.index(arrived) + 1
        actions.append(
            f"БП переполнена: выбита самая старая заявка "
            f"{_label(state.last_evicted)}, отказ (Д1ОО3)"
        )
        actions.append(f"заявка {_label(arrived)} записана на место {place}")
    else:
        if previous:
            place = previous.buffer_cells.index(None) + 1
        else:
            place = 1
        actions.append(
            f"заявка {_label(arrived)} записана на первое свободное место "
            f"{place} БП (Д1ОЗ3)"
        )

    if arrived in state.devices:
        device = state.devices.index(arrived) + 1
        actions.append(
            f"ДВ выбрал из БП последнюю поступившую заявку "
            f"{_label(arrived)} (Д2Б2)"
        )
        actions.append(
            f"заявка {_label(arrived)} отправлена на первый свободный "
            f"прибор П{device} (Д2П1)"
        )
    else:
        actions.append("все приборы заняты, заявка ожидает в БП")
    return actions


def _service_end_actions(
    state: SystemState,
    previous: SystemState | None,
) -> list[str]:
    i = state.last_event.device.id
    done = previous.devices[i - 1] if previous else None
    actions = [f"прибор П{i} закончил обработку заявки {_label(done)} (ПЗ2)"]
    taken = state.devices[i - 1]
    if taken is None:
        actions.append(f"БП пуст, прибор П{i} простаивает")
    else:
        actions.append(
            f"ДВ выбрал из БП последнюю поступившую заявку "
            f"{_label(taken)} (Д2Б2)"
        )
        actions.append(f"заявка {_label(taken)} отправлена на прибор П{i}")
    return actions


def _render_current_state(state: SystemState) -> str:
    calendar = ", ".join(
        f"{_owner(event)} {event.time:.3f}" for event in state.calendar
    )
    arrived = state.last_arrived
    if arrived is None:
        arrived_text = "-"
    else:
        arrived_text = f"{_label(arrived)} (Tвх = {arrived.arrival_time:.3f})"
    return "\n".join(
        [
            f"Модельное время t:          {state.time:.3f}",
            f"Особое событие:             {_event_name(state)}",
            f"Поступившая заявка:         {arrived_text}",
            f"Последняя выбитая заявка:   {_label(state.last_evicted)}",
            f"pотк:                       {state.reject_rate:.4f}",
            f"Календарь событий:          {calendar or 'пуст'}",
        ]
    )


def _event_name(state: SystemState) -> str:
    event = state.last_event
    if event.type is EventType.END_SERVICE:
        return f"освобождение прибора {_owner(event)}"
    if state.last_arrived is None:
        return f"окончание генерации заявок {_owner(event)}"
    return f"поступление заявки от {_owner(event)}"


def _owner(event: Event) -> str:
    if event.type is EventType.GENERATE:
        return str(event.source)
    return f"П{event.device.id}"


def _label(request: Request | None) -> str:
    if request is None:
        return "-"
    return f"{request.source_id}.{request.frame_no}"


def _time(time: float | None) -> str:
    if time is None:
        return "-"
    return f"{time:.3f}"
