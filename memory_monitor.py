from __future__ import annotations

from datetime import datetime
from pathlib import Path
import csv
import time

import psutil


OUTPUT = Path("logs/memory.csv")
INTERVAL = 10


def bytes_to_gb(value: int) -> float:
    return value / (1024 ** 3)


OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

with OUTPUT.open(
    "w",
    newline="",
) as file:

    writer = csv.writer(file)

    writer.writerow(
        [
            "timestamp",
            "memory_used_gb",
            "memory_available_gb",
            "memory_percent",
            "swap_used_gb",
            "swap_percent",
            "python_processes",
            "python_rss_gb",
            "largest_python_gb",
            "largest_python_pid",
            "cpu_percent",
        ]
    )

    print(
        f"Gravando em {OUTPUT}"
    )

    while True:

        vm = psutil.virtual_memory()

        swap = psutil.swap_memory()

        python_processes = 0
        python_rss = 0
        largest_python = 0
        largest_pid = ""

        for process in psutil.process_iter(
            [
                "pid",
                "name",
                "memory_info",
            ]
        ):

            try:

                name = (
                    process.info["name"] or ""
                ).lower()

                if "python" not in name:
                    continue

                rss = (
                    process.info["memory_info"]
                    .rss
                )

                python_processes += 1

                python_rss += rss

                if rss > largest_python:

                    largest_python = rss
                    largest_pid = process.pid

            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
            ):

                pass

        writer.writerow(
            [
                datetime.now().isoformat(
                    timespec="seconds"
                ),
                round(
                    bytes_to_gb(vm.used),
                    2,
                ),
                round(
                    bytes_to_gb(vm.available),
                    2,
                ),
                vm.percent,
                round(
                    bytes_to_gb(swap.used),
                    2,
                ),
                swap.percent,
                python_processes,
                round(
                    bytes_to_gb(
                        python_rss
                    ),
                    2,
                ),
                round(
                    bytes_to_gb(
                        largest_python
                    ),
                    2,
                ),
                largest_pid,
                psutil.cpu_percent(),
            ]
        )

        file.flush()

        print(
            f"{datetime.now():%H:%M:%S} | "
            f"RAM {vm.percent:5.1f}% | "
            f"Python {python_processes:2d} | "
            f"RSS {bytes_to_gb(python_rss):6.1f} GB | "
            f"Maior {bytes_to_gb(largest_python):5.1f} GB"
        )

        time.sleep(INTERVAL)