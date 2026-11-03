"""Точка входа приложения: граф, обратные зависимости, визуализация."""

import argparse
import sys

from src.config import Config, ConfigError, load_config
from src.graph_builder import (
    GraphBuilderError,
    build_graph,
    find_reverse_dependencies,
    load_test_repo,
    print_graph,
    print_reverse_dependencies,
)
from src.npm_client import NpmClientError, fetch_direct_dependencies
from src.visualizer import (
    VisualizerError,
    render_svg,
    save_d2,
)


CONFIG_PATH_DEFAULT = "config.yaml"
D2_PATH_DEFAULT = "graph.d2"
SVG_PATH_DEFAULT = "graph.svg"


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
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Сгенерировать D2 и SVG-изображение графа",
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
    """Печатает список прямых зависимостей пакета."""
    print("=" * 40)
    print(f"Прямые зависимости ({len(dependencies)}):")
    print("=" * 40)
    if not dependencies:
        print("(нет прямых зависимостей)")
        return
    for name, version in sorted(dependencies.items()):
        print(f"  {name} {version}")
    print("=" * 40)


def _visualize(graph: dict) -> int:
    """Генерирует .d2 и .svg для графа. Возвращает код возврата."""
    try:
        save_d2(graph, D2_PATH_DEFAULT)
        print(f"D2-файл сохранён: {D2_PATH_DEFAULT}")
        render_svg(D2_PATH_DEFAULT, SVG_PATH_DEFAULT)
        print(f"SVG-изображение сохранено: {SVG_PATH_DEFAULT}")
    except VisualizerError as exc:
        print(f"Ошибка визуализации: {exc}", file=sys.stderr)
        return 1
    return 0


def _run_real_mode(config: Config, visualize: bool) -> int:
    """Режим работы с реальным npm registry."""
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


def _run_test_mode(config: Config, visualize: bool) -> int:
    """Режим работы с локальным файлом (Этапы 3 и 4)."""
    try:
        repo = load_test_repo(config.repo_url)
        graph = build_graph(
            config.package_name,
            repo,
            max_depth=config.max_depth,
        )
        reverse = find_reverse_dependencies(graph, config.package_name)
    except GraphBuilderError as exc:
        print(f"Ошибка построения графа: {exc}", file=sys.stderr)
        return 1

    print_graph(graph)
    print_reverse_dependencies(config.package_name, reverse)

    if visualize:
        return _visualize(graph)
    return 0


def main(argv=None) -> int:
    """Точка входа."""
    args = parse_args(argv)

    try:
        config = load_config(args.config)
    except ConfigError as exc:
        print(f"Ошибка конфигурации: {exc}", file=sys.stderr)
        return 1

    print_config(config)

    if config.test_mode:
        return _run_test_mode(config, args.visualize)
    return _run_real_mode(config, args.visualize)


if __name__ == "__main__":
    sys.exit(main())