"""hello.py — минимальный пример скрипта для репозитория.

Демонстрирует рекомендуемую структуру: докстринг, функция main(),
аннотации типов и блок `if __name__ == "__main__"`.

Запуск:
    python scripts/hello.py
    python scripts/hello.py --name Мир
"""

from __future__ import annotations

import argparse


def build_greeting(name: str) -> str:
    """Возвращает приветствие для указанного имени."""
    return f"Привет, {name}!"


def main() -> None:
    parser = argparse.ArgumentParser(description="Пример приветственного скрипта.")
    parser.add_argument("--name", default="мир", help="имя для приветствия")
    args = parser.parse_args()

    print(build_greeting(args.name))


if __name__ == "__main__":
    main()
