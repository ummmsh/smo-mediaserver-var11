from __future__ import annotations

from smo.statistics.summary_table import SummaryTable

SOURCE_COLUMNS = ("pотк", "Tпреб", "TБП", "Tобсл", "ДБП", "Добсл")


def render_summary(table: SummaryTable) -> str:
    lines = [
        "Таблица 1. Характеристики источников ВС",
        f"{'№ источника':<13}{'Кол-во заявок':>14}"
        + "".join(f"{column:>9}" for column in SOURCE_COLUMNS),
    ]
    for k, (generated, *values) in enumerate(table.per_source, start=1):
        lines.append(
            f"{f'И{k}':<13}{generated:>14}"
            + "".join(f"{value:>9.4f}" for value in values)
        )
    lines.append("")
    lines.append("Таблица 2. Характеристики приборов ВС")
    lines.append(f"{'№ прибора':<13}{'Kисп':>14}")
    for i, usage in enumerate(table.per_device, start=1):
        lines.append(f"{f'П{i}':<13}{usage:>14.4f}")
    lines.append("")
    lines.append(f"pотк системы = {total_reject_rate(table):.4f}")
    return "\n".join(lines)


def total_reject_rate(table: SummaryTable) -> float:
    generated = sum(row[0] for row in table.per_source)
    rejected = sum(row[0] * row[1] for row in table.per_source)
    if generated == 0:
        return 0.0
    return rejected / generated
