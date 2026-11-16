from __future__ import annotations

from smo.statistics.summary_table import SummaryTable


def print_summary(table: SummaryTable) -> None:
    print("Таблица 1. Характеристики источников ВС")
    print(
        f"{'№ источника':<13}{'Кол-во заявок':>14}{'pотк':>9}{'Tпреб':>9}"
        f"{'TБП':>9}{'Tобсл':>9}{'ДБП':>9}{'Добсл':>9}"
    )
    for k, (count, *values) in enumerate(table.per_source, start=1):
        numbers = "".join(f"{value:>9.4f}" for value in values)
        print(f"{f'И{k}':<13}{count:>14}{numbers}")
    print()
    print("Таблица 2. Характеристики приборов ВС")
    print(f"{'№ прибора':<13}{'Kисп':>14}")
    for i, usage in enumerate(table.per_device, start=1):
        print(f"{f'П{i}':<13}{usage:>14.4f}")
    print()
    print(f"pотк системы = {reject_rate(table):.4f}")


def reject_rate(table: SummaryTable) -> float:
    generated = sum(row[0] for row in table.per_source)
    rejected = sum(row[0] * row[1] for row in table.per_source)
    return rejected / generated if generated else 0.0
