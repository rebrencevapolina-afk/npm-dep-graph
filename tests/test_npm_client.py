"""Тесты для клиента npm (без реальных сетевых запросов)."""

from unittest.mock import Mock, patch

import pytest
import requests

from src.npm_client import (
    NpmClientError,
    _build_package_url,
    _extract_dependencies,
    fetch_direct_dependencies,
)


def test_build_package_url():
    """Правильно собирает URL к пакету."""
    url = _build_package_url(
        "https://registry.npmjs.org", "express", "latest"
    )
    assert url == "https://registry.npmjs.org/express/latest"


def test_build_package_url_strips_slash():
    """Убирает лишний слэш в конце базового URL."""
    url = _build_package_url(
        "https://registry.npmjs.org/", "express", "latest"
    )
    assert url == "https://registry.npmjs.org/express/latest"


def test_extract_dependencies_empty():
    """Если dependencies нет — возвращает пустой словарь."""
    assert _extract_dependencies({}) == {}


def test_extract_dependencies_present():
    """Возвращает словарь зависимостей."""
    data = {"dependencies": {"a": "1.0.0", "b": "2.0.0"}}
    assert _extract_dependencies(data) == {"a": "1.0.0", "b": "2.0.0"}


@patch("src.npm_client.requests.get")
def test_fetch_dependencies_success(mock_get):
    """Успешный запрос возвращает словарь зависимостей."""
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "dependencies": {"accepts": "~1.3.8"}
    }
    mock_get.return_value = response

    result = fetch_direct_dependencies(
        "https://registry.npmjs.org", "express", "latest"
    )
    assert result == {"accepts": "~1.3.8"}


@patch("src.npm_client.requests.get")
def test_fetch_dependencies_404(mock_get):
    """404 вызывает NpmClientError."""
    response = Mock()
    response.status_code = 404
    mock_get.return_value = response

    with pytest.raises(NpmClientError, match="не найден"):
        fetch_direct_dependencies(
            "https://registry.npmjs.org", "nonexistent", "latest"
        )


@patch("src.npm_client.requests.get")
def test_fetch_dependencies_network_error(mock_get):
    """Ошибка сети вызывает NpmClientError."""
    mock_get.side_effect = requests.RequestException("boom")

    with pytest.raises(NpmClientError, match="Ошибка сети"):
        fetch_direct_dependencies(
            "https://registry.npmjs.org", "express", "latest"
        )