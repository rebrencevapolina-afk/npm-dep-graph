"""Точка входа приложения для визуализации графов зависимостей npm."""

import argparse
import sys

from src.config import Config, ConfigError, load_config
from src.npm_client import NpmClientError, fetch_direct_dependencies


CONFIG_PATH_DEFAULT = "config.yaml"


def parse_args(argv=None) -> argparse.Namespace:
    """Разбирает аргументы командной строки."""
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
    """Печатает параметры конфигурации в формате ключ-значение."""
    print("=" * 40)
    print("Параметры конфигурации:")
    print("=" * 40)
    print(f"package_name = {config.package_name}")
    print(f"repo_url     = {config.repo_url}")
    print(f"test_mode    = {config.test_mode}")
    print(f"max_depth    = {config.max_depth}")
    print("=" * 40)


def print_dependencies(dependencies: dict) -> None:
    """Печатает список прямых зависимостей пакета.

    Args:
        dependencies: словарь {имя: версия}.
    """
    print("=" * 40)
    print(f"Прямые зависимости ({len(dependencies)}):")
    print("=" * 40)
    if not dependencies:
        print("(нет прямых зависимостей)")
        return
    for name, version in sorted(dependencies.items()):
        print(f"  {name} {version}")
    print("=" * 40)


def main(argv=None) -> int:
    """Точка входа."""
    args = parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1

    print_config(config)

    try:
        dependencies = fetch_direct_dependencies(
            repo_url=config.repo_url,
            package_name=config.package_name,
        )
    except NpmClientError as exc:
        print(f"Ошибка получения зависимостей: {exc}", file=sys.stderr)
        return 1

    print_dependencies(dependencies)
    return 0


if __name__ == "__main__":
    sys.exit(main())