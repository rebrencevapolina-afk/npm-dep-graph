"""Клиент для работы с npm registry.

Содержит класс NpmClientError для ошибок клиента и функцию
fetch_direct_dependencies, которая возвращает список прямых
зависимостей пакета из npm registry.
"""

import requests


# Константа: таймаут HTTP-запроса в секундах
HTTP_TIMEOUT_SECONDS = 10

# Константа: имя последней версии пакета по умолчанию
LATEST_VERSION = "latest"


class NpmClientError(Exception):
    """Ошибка при работе с npm registry."""


def _build_package_url(repo_url: str, package_name: str,
                       version: str) -> str:
    """Собирает URL к конкретному пакету в npm registry.

    Args:
        repo_url: базовый URL реестра (например, https://registry.npmjs.org).
        package_name: имя пакета (например, express).
        version: версия пакета (например, 4.18.2 или latest).

    Returns:
        Полный URL к JSON-описанию пакета.
    """
    base = repo_url.rstrip("/")
    return f"{base}/{package_name}/{version}"


def _extract_dependencies(data: dict) -> dict:
    """Извлекает словарь прямых зависимостей из JSON-описания пакета.

    Args:
        data: JSON-описание пакета из npm registry.

    Returns:
        Словарь {имя зависимости: версия}.
    """
    dependencies = data.get("dependencies", {})
    if not isinstance(dependencies, dict):
        return {}
    return dependencies


def fetch_direct_dependencies(repo_url: str, package_name: str,
                              version: str = LATEST_VERSION) -> dict:
    """Запрашивает прямые зависимости пакета из npm registry.

    Args:
        repo_url: базовый URL реестра.
        package_name: имя пакета.
        version: версия пакета (по умолчанию 'latest').

    Returns:
        Словарь {имя зависимости: версия}.

    Raises:
        NpmClientError: если пакет не найден, сеть недоступна или
            ответ содержит некорректный JSON.
    """
    url = _build_package_url(repo_url, package_name, version)

    try:
        response = requests.get(url, timeout=HTTP_TIMEOUT_SECONDS)
    except requests.RequestException as exc:
        raise NpmClientError(
            f"Ошибка сети при запросе к npm registry: {exc}"
        ) from exc

    if response.status_code == 404:
        raise NpmClientError(
            f"Пакет '{package_name}' версии '{version}' не найден"
        )
    if response.status_code != 200:
        raise NpmClientError(
            f"npm registry вернул код {response.status_code}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise NpmClientError(
            "Ответ npm registry не является корректным JSON"
        ) from exc

    return _extract_dependencies(data)