"""Тесты для модуля построения графа зависимостей."""

import os
import tempfile

import pytest

from src.graph_builder import (
    GraphBuilderError,
    build_graph,
    find_reverse_dependencies,
    load_test_repo,
)   

EXPECTED_CYCLE_SIZE = 3

def _write_yaml(content: str) -> str:
    """Создаёт временный YAML-файл и возвращает путь."""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write(content)
    return path


def test_load_test_repo_success():
    """Корректный YAML загружается без ошибок."""
    content = "A:\n  dependencies: [B, C]\nB:\n  dependencies: []\n"
    path = _write_yaml(content)
    try:
        repo = load_test_repo(path)
        assert repo == {"A": ["B", "C"], "B": []}
    finally:
        os.unlink(path)


def test_load_test_repo_missing_file():
    """Отсутствующий файл вызывает ошибку."""
    with pytest.raises(GraphBuilderError, match="не найден"):
        load_test_repo("/nonexistent/file.yaml")


def test_build_graph_simple():
    """Простой граф без циклов."""
    repo = {"A": ["B"], "B": ["C"], "C": []}
    graph = build_graph("A", repo, max_depth=5)
    assert set(graph.keys()) == {"A", "B", "C"}


def test_build_graph_depth_limit():
    """Глубина ограничивает обход."""
    repo = {"A": ["B"], "B": ["C"], "C": ["D"], "D": []}
    graph = build_graph("A", repo, max_depth=2)
    assert set(graph.keys()) == {"A", "B", "C"}
    assert "D" not in graph


def test_build_graph_cycle():
    """Циклическая зависимость не зацикливает обход."""
    repo = {"A": ["B"], "B": ["C"], "C": ["A"]}
    graph = build_graph("A", repo, max_depth=10)
    assert len(graph) == EXPECTED_CYCLE_SIZE
    assert set(graph.keys()) == {"A", "B", "C"}


def test_build_graph_root_missing():
    """Отсутствующий корень вызывает ошибку."""
    repo = {"A": ["B"]}
    with pytest.raises(GraphBuilderError, match="не найден"):
        build_graph("Z", repo, max_depth=3)

def test_find_reverse_dependencies_simple():
    """Находит пакет, который зависит от target."""
    graph = {"A": ["B"], "B": ["C"], "C": []}
    reverse = find_reverse_dependencies(graph, "B")
    assert reverse == ["A"]


def test_find_reverse_dependencies_multiple():
    """Находит несколько пакетов, зависящих от target."""
    graph = {"A": ["C"], "B": ["C"], "C": []}
    reverse = find_reverse_dependencies(graph, "C")
    assert reverse == ["A", "B"]


def test_find_reverse_dependencies_none():
    """Нет пакетов, зависящих от target."""
    graph = {"A": ["B"], "B": []}
    reverse = find_reverse_dependencies(graph, "A")
    assert reverse == []


def test_find_reverse_dependencies_cycle():
    """Цикл не ломает поиск обратных зависимостей."""
    graph = {"A": ["B"], "B": ["A"]}
    reverse = find_reverse_dependencies(graph, "A")
    assert reverse == ["B"]


def test_find_reverse_dependencies_target_missing():
    """Отсутствующий target вызывает ошибку."""
    graph = {"A": ["B"]}
    with pytest.raises(GraphBuilderError, match="не найден"):
        find_reverse_dependencies(graph, "Z")