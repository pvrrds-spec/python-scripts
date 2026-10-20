#!/usr/bin/env python3
"""Оценка состояния оперативной памяти компьютера.

Показывает:
- объём и использование RAM (общая, доступная, занято, %)
- использование swap / файла подкачки
- топ процессов по потреблению памяти

Кроссплатформенно: Windows / Linux / macOS.

Использование:
    python scripts/memory_check.py            # краткий отчёт
    python scripts/memory_check.py --verbose  # подробный отчёт с топом процессов
    python scripts/memory_check.py --watch 5  # обновлять каждые 5 секунд
"""

from __future__ import annotations

import argparse
import platform
import sys
import time
from dataclasses import dataclass

try:
    import psutil
except ImportError:
    sys.exit(
        "Модуль psutil не найден. Установите его командой:\n"
        "    pip install psutil"
    )


def human_bytes(n: float) -> str:
    """Преобразовать число байт в человекочитаемый формат."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024.0 or unit == "TB":
            return f"{n:.2f} {unit}"
        n /= 1024.0
    return f"{n:.2f} TB"  # недостижимо, но для строгой типизации


@dataclass
class MemoryReport:
    """Снимок состояния памяти."""

    total: int
    available: int
    used: int
    percent: float
    swap_total: int
    swap_used: int
    swap_percent: float

    @property
    def status(self) -> str:
        """Текстовая оценка по порогам использования."""
        if self.percent < 60:
            return "ХОРОШО — памяти достаточно"
        if self.percent < 80:
            return "НОРМАЛЬНО — следите за нагрузкой"
        if self.percent < 90:
            return "ВНИМАНИЕ — память почти заполнена"
        return "КРИТИЧНО — нехватка памяти, возможны зависания"


def collect_memory_report() -> MemoryReport:
    """Собрать текущие метрики памяти системы."""
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    return MemoryReport(
        total=vm.total,
        available=vm.available,
        used=vm.used,
        percent=vm.percent,
        swap_total=sw.total,
        swap_used=sw.used,
        swap_percent=sw.percent,
    )


def top_memory_processes(limit: int = 10) -> list[tuple[str, int, float]]:
    """Вернуть список процессов (имя, RSS в байтах, % памяти), отсортированный по памяти."""
    result: list[tuple[str, int, float]] = []
    for proc in psutil.process_iter(["name", "memory_info", "memory_percent"]):
        try:
            info = proc.info
            mem = info["memory_info"]
            if mem is None:
                continue
            result.append((info["name"] or "?", mem.rss, info["memory_percent"] or 0.0))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    result.sort(key=lambda x: x[1], reverse=True)
    return result[:limit]


def print_report(report: MemoryReport, verbose: bool, top_n: int) -> None:
    """Вывести отчёт в консоль."""
    bar_len = 30
    filled = int(bar_len * report.percent / 100)
    bar = "#" * filled + "-" * (bar_len - filled)

    print("=" * 56)
    print("ОЦЕНКА ОПЕРАТИВНОЙ ПАМЯТИ")
    print(f"Система: {platform.system()} {platform.release()} ({platform.machine()})")
    print("=" * 56)
    print(f"RAM всего:      {human_bytes(report.total):>14}")
    print(f"Занято:         {human_bytes(report.used):>14}")
    print(f"Свободно:       {human_bytes(report.available):>14}")
    print(f"Использовано:   [{bar}] {report.percent:.1f}%")
    print(f"Swap/подкачка:  {human_bytes(report.swap_used)} / {human_bytes(report.swap_total)} ({report.swap_percent:.1f}%)")
    print("-" * 56)
    print(f"Оценка: {report.status}")

    if verbose:
        print("-" * 56)
        print(f"ТОП-{top_n} процессов по памяти:")
        rows = top_memory_processes(top_n)
        if not rows:
            print("  (недостаточно прав для чтения информации о процессах)")
        for name, rss, pct in rows:
            short_name = name if len(name) <= 30 else name[:27] + "..."
            print(f"  {short_name:<32} {human_bytes(rss):>12}  {pct:5.1f}%")
    print("=" * 56)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Оценка оперативной памяти ноутбука.")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="показать топ процессов по памяти",
    )
    parser.add_argument(
        "-n", "--top", type=int, default=10, metavar="N",
        help="сколько процессов показать в режиме --verbose (по умолчанию 10)",
    )
    parser.add_argument(
        "-w", "--watch", type=int, default=0, metavar="SEC",
        help="обновлять отчёт каждые SEC секунд (Ctrl+C для выхода)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        while True:
            report = collect_memory_report()
            print_report(report, verbose=args.verbose, top_n=args.top)
            if args.watch <= 0:
                break
            time.sleep(args.watch)
    except KeyboardInterrupt:
        print("\nОстановлено пользователем.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
