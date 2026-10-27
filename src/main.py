"""Точка входа приложения для визуализации графов зависимостей npm.

Загружает конфигурацию из YAML, валидирует её и выводит все
параметры в формате ключ-значение. Служит заготовкой для
последующих этапов: сбор данных, построение графа, визуализация.
"""

import argparse
import sys

from src.config import Config, ConfigError, load_config


CONFIG_PATH_DEFAULT = "config.yaml"


def parse_args(argv=None) -> argparse.Namespace:
    """Разбирает аргументы командной строки.

    Args:
        argv: список аргументов; если None — берётся sys.argv[1:].

    Returns:
        Пространство имён с аргументами CLI.
    """
    parser = argparse.ArgumentParser(
        description="Инструмент визуализации графов зависимостей npm",
    )
    parser.add_argument(
        "--config",
        default=CONFIG_PATH_DEFAULT,
        help="Путь к YAML-файлу конфигурации",
    )
    return parser.parse_args(argv)


def print_config(config: Config) -> None:
    """Печатает все параметры конфигурации в формате ключ-значение."""
    print("=" * 40)
    print("Параметры конфигурации:")
    print("=" * 40)
    print(f"package_name = {config.package_name}")
    print(f"repo_url     = {config.repo_url}")
    print(f"test_mode    = {config.test_mode}")
    print(f"max_depth    = {config.max_depth}")
    print("=" * 40)


def main(argv=None) -> int:
    """Точка входа: разбирает аргументы, загружает конфиг, выводит его.

    Returns:
        Код возврата: 0 при успехе, 1 при ошибке конфигурации.
    """
    args = parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1

    print_config(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())