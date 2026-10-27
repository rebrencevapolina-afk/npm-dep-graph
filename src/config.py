"""Модуль загрузки и валидации YAML-конфигурации.

Содержит класс ConfigError для ошибок валидации и функцию
load_config, которая читает YAML-файл и проверяет все поля.
"""

import os
from dataclasses import dataclass

import yaml


# Константы для валидации
MAX_DEPTH_MIN = 1
MAX_DEPTH_MAX = 20
REQUIRED_FIELDS = ("package_name", "repo_url", "test_mode", "max_depth")


class ConfigError(Exception):
    """Ошибка валидации конфигурации."""


@dataclass
class Config:
    """Конфигурация приложения.

    Attributes:
        package_name: имя анализируемого npm-пакета.
        repo_url: URL репозитория или путь к тестовому файлу.
        test_mode: True, если используется тестовый режим.
        max_depth: максимальная глубина анализа зависимостей.
    """

    package_name: str
    repo_url: str
    test_mode: bool
    max_depth: int


def _check_required_fields(data: dict) -> None:
    """Проверяет наличие всех обязательных полей в словаре."""
    missing = [key for key in REQUIRED_FIELDS if key not in data]
    if missing:
        raise ConfigError(
            f"В конфигурации отсутствуют поля: {', '.join(missing)}"
        )


def _check_package_name(value) -> str:
    """Проверяет имя пакета."""
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("package_name должен быть непустой строкой")
    return value.strip()


def _check_repo_url(value) -> str:
    """Проверяет URL репозитория или путь к файлу."""
    if not isinstance(value, str) or not value.strip():
        raise ConfigError("repo_url должен быть непустой строкой")
    return value.strip()


def _check_test_mode(value) -> bool:
    """Проверяет флаг тестового режима."""
    if not isinstance(value, bool):
        raise ConfigError("test_mode должен быть true или false")
    return value


def _check_max_depth(value) -> int:
    """Проверяет максимальную глубину анализа."""
    if not isinstance(value, int) or isinstance(value, bool):
        raise ConfigError("max_depth должен быть целым числом")
    if not (MAX_DEPTH_MIN <= value <= MAX_DEPTH_MAX):
        raise ConfigError(
            f"max_depth должен быть от {MAX_DEPTH_MIN} до {MAX_DEPTH_MAX}"
        )
    return value


def load_config(path: str) -> Config:
    """Загружает и валидирует YAML-конфигурацию.

    Args:
        path: путь к YAML-файлу конфигурации.

    Returns:
        Объект Config с валидированными параметрами.

    Raises:
        ConfigError: если файл не найден, содержит неверный YAML
            или не проходит валидацию полей.
    """
    if not os.path.isfile(path):
        raise ConfigError(f"Файл конфигурации не найден: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
    except yaml.YAMLError as exc:
        raise ConfigError(f"Неверный формат YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Корневой элемент YAML должен быть словарём")

    _check_required_fields(data)

    return Config(
        package_name=_check_package_name(data["package_name"]),
        repo_url=_check_repo_url(data["repo_url"]),
        test_mode=_check_test_mode(data["test_mode"]),
        max_depth=_check_max_depth(data["max_depth"]),
    )