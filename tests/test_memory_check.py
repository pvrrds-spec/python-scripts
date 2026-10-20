"""Тесты для scripts/memory_check.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from memory_check import (  # noqa: E402
    MemoryReport,
    collect_memory_report,
    human_bytes,
    top_memory_processes,
)


def make_report(percent: float) -> MemoryReport:
    return MemoryReport(
        total=16 * 1024**3,
        available=int(16 * 1024**3 * (1 - percent / 100)),
        used=int(16 * 1024**3 * percent / 100),
        percent=percent,
        swap_total=8 * 1024**3,
        swap_used=1024**3,
        swap_percent=12.5,
    )


def test_human_bytes() -> None:
    assert human_bytes(512) == "512.00 B"
    assert human_bytes(1024) == "1.00 KB"
    assert human_bytes(5 * 1024**3) == "5.00 GB"
    assert human_bytes(2 * 1024**4) == "2.00 TB"


def test_status_thresholds() -> None:
    assert "ХОРОШО" in make_report(50).status
    assert "НОРМАЛЬНО" in make_report(70).status
    assert "ВНИМАНИЕ" in make_report(85).status
    assert "КРИТИЧНО" in make_report(95).status


def test_collect_memory_report() -> None:
    report = collect_memory_report()
    assert report.total > 0
    assert 0 <= report.percent <= 100
    assert report.used <= report.total


def test_top_processes_returns_sorted_list() -> None:
    rows = top_memory_processes(limit=5)
    assert len(rows) <= 5
    sizes = [rss for _, rss, _ in rows]
    assert sizes == sorted(sizes, reverse=True)
