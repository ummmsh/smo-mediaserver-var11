from __future__ import annotations

from ui.auto_mode import run_auto_mode
from ui.step_mode import run_step_mode

SOURCES = 3
DEVICES = 3
BUFFER_SIZE = 3
LAMBDA = 0.5
A = 1.0
B = 3.0
N_REQUESTS = 100


def main() -> None:
    mode = input("Режим: 1 - пошаговый, 2 - автоматический: ").strip()
    if mode == "1":
        run_step_mode(SOURCES, DEVICES, BUFFER_SIZE, LAMBDA, A, B, N_REQUESTS)
    else:
        run_auto_mode(SOURCES, DEVICES, BUFFER_SIZE, LAMBDA, A, B, N_REQUESTS)


if __name__ == "__main__":
    main()
