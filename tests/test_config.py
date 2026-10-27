"""Тесты для модуля загрузки конфигурации."""

import os
import tempfile

import pytest

from src.config import ConfigError, load_config


def _write_yaml(content: str) -> str:
    """Создаёт временный YAML-файл и возвращает путь к нему."""
    fd, path = tempfile.mkstemp(suffix=".yaml")
    with os.fdopen(fd, "w", encoding="utf-8") as file:
        file.write(content)
    return path


def test_load_valid_config():
    """Корректная конфигурация загружается без ошибок."""
    content = (
        "package_name: express\n"
        "repo_url: https://registry.npmjs.org\n"
        "test_mode: false\n"
        "max_depth: 3\n"
    )
    path = _write_yaml(content)
    try:
        config = load_config(path)
        assert config.package_name == "express"
        assert config.max_depth == 3
    finally:
        os.unlink(path)


def test_missing_file_raises():
    """Отсутствующий файл вызывает ConfigError."""
    with pytest.raises(ConfigError):
        load_config("/nonexistent/path.yaml")


def test_invalid_max_depth_raises():
    """Неверный тип max_depth вызывает ConfigError."""
    content = (
        "package_name: express\n"
        "repo_url: https://registry.npmjs.org\n"
        "test_mode: false\n"
        "max_depth: 'abc'\n"
    )
    path = _write_yaml(content)
    try:
        with pytest.raises(ConfigError):
            load_config(path)
    finally:
        os.unlink(path)