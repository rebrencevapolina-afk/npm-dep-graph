"""Тесты для модуля визуализации."""

import os
import tempfile

import pytest

from src.visualizer import (
    VisualizerError,
    generate_d2,
    save_d2,
)


def test_generate_d2_simple():
    """Простой граф корректно преобразуется в D2."""
    graph = {"A": ["B"], "B": []}
    d2 = generate_d2(graph)
    assert '"A" -> "B"' in d2
    assert '"B"' in d2


def test_generate_d2_cycle():
    """Цикл корректно преобразуется в D2."""
    graph = {"A": ["B"], "B": ["A"]}
    d2 = generate_d2(graph)
    assert '"A" -> "B"' in d2
    assert '"B" -> "A"' in d2


def test_generate_d2_empty():
    """Пустой граф даёт пустую строку."""
    assert generate_d2({}) == ""


def test_save_d2_success():
    """Файл .d2 создаётся без ошибок."""
    graph = {"A": ["B"], "B": []}
    fd, path = tempfile.mkstemp(suffix=".d2")
    os.close(fd)
    try:
        save_d2(graph, path)
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        assert '"A" -> "B"' in content
    finally:
        os.unlink(path)


def test_save_d2_bad_path():
    """Невалидный путь вызывает VisualizerError."""
    with pytest.raises(VisualizerError):
        save_d2({"A": []}, "/nonexistent/dir/file.d2")