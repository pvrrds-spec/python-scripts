"""Тесты для scripts/hello.py."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from hello import build_greeting  # noqa: E402


def test_build_greeting_default() -> None:
    assert build_greeting("мир") == "Привет, мир!"


def test_build_greeting_custom_name() -> None:
    assert build_greeting("Алиса") == "Привет, Алиса!"
