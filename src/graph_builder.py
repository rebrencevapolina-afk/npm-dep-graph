"""Модуль построения графа зависимостей (BFS с рекурсией).

Содержит класс GraphBuilderError для ошибок построения и функции
для загрузки тестового репозитория, а также для построения графа
методом BFS с рекурсией и учётом максимальной глубины.
"""

import os

import yaml


MAX_DEPTH_MIN = 1
MAX_DEPTH_MAX = 20


class GraphBuilderError(Exception):
    """Ошибка при построении графа зависимостей."""


def _validate_package(name, value) -> list:
    """Проверяет описание одного пакета и возвращает его зависимости.

    Args:
        name: имя пакета.
        value: значение из YAML (должно быть словарём).

    Returns:
        Список зависимостей пакета.

    Raises:
        GraphBuilderError: если данные некорректны.
    """
    if not isinstance(name, str):
        raise GraphBuilderError(
            f"Имя пакета должно быть строкой: {name}"
        )
    if not isinstance(value, dict):
        raise GraphBuilderError(
            f"Значение для пакета '{name}' должно быть словарём"
        )
    deps = value.get("dependencies", [])
    if not isinstance(deps, list):
        raise GraphBuilderError(
            f"Поле dependencies для '{name}' должно быть списком"
        )
    return [str(d) for d in deps]


def load_test_repo(path: str) -> dict:
    """Загружает тестовый репозиторий из YAML-файла.

    Формат файла:
        A:
          dependencies: [B, C]
        B:
          dependencies: [D]
        ...

    Args:
        path: путь к YAML-файлу тестового репозитория.

    Returns:
        Словарь {имя пакета: список прямых зависимостей}.

    Raises:
        GraphBuilderError: если файл не найден, не является YAML,
            или имеет неверный формат.
    """
    if not os.path.isfile(path):
        raise GraphBuilderError(
            f"Файл тестового репозитория не найден: {path}"
        )

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise GraphBuilderError(f"Неверный формат YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise GraphBuilderError(
            "Корневой элемент YAML должен быть словарём"
        )

    return {name: _validate_package(name, value)
            for name, value in data.items()}


def _check_max_depth(max_depth: int) -> None:
    """Проверяет корректность максимальной глубины."""
    if not isinstance(max_depth, int) or isinstance(max_depth, bool):
        raise GraphBuilderError("max_depth должен быть целым числом")
    if not (MAX_DEPTH_MIN <= max_depth <= MAX_DEPTH_MAX):
        raise GraphBuilderError(
            f"max_depth должен быть от {MAX_DEPTH_MIN} до {MAX_DEPTH_MAX}"
        )


def _visit(package: str, depth: int, repo: dict, max_depth: int,
           visited: set, graph: dict) -> None:
    """Рекурсивно обходит зависимости пакета (BFS с рекурсией).

    Args:
        package: текущий пакет.
        depth: текущая глубина.
        repo: словарь {имя: [зависимости]}.
        max_depth: максимальная глубина.
        visited: множество посещённых пакетов.
        graph: словарь для результатов.
    """
    if package in visited:
        return
    if depth > max_depth:
        return

    visited.add(package)
    deps = repo.get(package, [])
    graph[package] = list(deps)

    if depth == max_depth:
        return
    for dep in deps:
        if dep not in visited:
            _visit(dep, depth + 1, repo, max_depth, visited, graph)


def build_graph(root: str, repo: dict, max_depth: int) -> dict:
    """Строит граф зависимостей от пакета root до max_depth.

    Используется BFS с рекурсией. Циклы обрабатываются через
    множество visited.

    Args:
        root: имя корневого пакета.
        repo: словарь {имя пакета: список зависимостей}.
        max_depth: максимальная глубина анализа (>= 1).

    Returns:
        Словарь {имя пакета: список его зависимостей}.

    Raises:
        GraphBuilderError: если root отсутствует в repo или
            max_depth некорректен.
    """
    _check_max_depth(max_depth)
    if root not in repo:
        raise GraphBuilderError(f"Корневой пакет не найден: {root}")

    graph = {}
    visited = set()
    _visit(root, 0, repo, max_depth, visited, graph)
    return graph


def print_graph(graph: dict) -> None:
    """Печатает граф зависимостей в читаемом виде.

    Args:
        graph: словарь {имя пакета: список его зависимостей}.
    """
    print("=" * 40)
    print(f"Граф зависимостей ({len(graph)} пакетов):")
    print("=" * 40)
    if not graph:
        print("(пустой граф)")
        return
    for name in sorted(graph.keys()):
        deps = graph[name]
        if deps:
            print(f"  {name} -> {', '.join(deps)}")
        else:
            print(f"  {name} -> (нет зависимостей)")
    print("=" * 40)


def find_reverse_dependencies(graph: dict, target: str) -> list:
    """Находит пакеты, которые зависят от target (обратные зависимости).

    Обходит все пакеты в графе и проверяет, у кого target есть в
    списке прямых зависимостей.

    Args:
        graph: словарь {имя пакета: список его зависимостей}.
        target: имя пакета, для которого ищем обратные зависимости.

    Returns:
        Отсортированный список имён пакетов, которые зависят от target.

    Raises:
        GraphBuilderError: если target отсутствует в graph.
    """
    if target not in graph:
        raise GraphBuilderError(
            f"Пакет не найден в графе: {target}"
        )

    reverse = []
    for name, deps in graph.items():
        if target in deps and name != target:
            reverse.append(name)

    return sorted(reverse)


def print_reverse_dependencies(target: str, reverse: list) -> None:
    """Печатает обратные зависимости пакета target.

    Args:
        target: имя пакета.
        reverse: список пакетов, которые зависят от target.
    """
    print("=" * 40)
    print(f"Обратные зависимости для '{target}':")
    print("=" * 40)
    if not reverse:
        print("(нет пакетов, зависящих от данного)")
        return
    for name in reverse:
        print(f"  {name}")
    print("=" * 40)