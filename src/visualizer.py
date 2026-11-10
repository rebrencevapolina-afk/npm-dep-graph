"""Модуль визуализации графа зависимостей на языке диаграмм D2.

Содержит класс VisualizerError для ошибок визуализации и функции
для генерации текстового представления графа в формате D2 и
конвертации его в SVG-изображение через утилиту d2.
"""

import os
import subprocess


D2_COMMAND = "d2"
D2_TIMEOUT_SECONDS = 30


class VisualizerError(Exception):
    """Ошибка при визуализации графа."""


def generate_d2(graph: dict) -> str:
    """Генерирует текстовое представление графа в формате D2.

    Args:
        graph: словарь {имя пакета: список его зависимостей}.

    Returns:
        Строка с описанием графа в синтаксисе D2.
    """
    lines = []
    for name in sorted(graph.keys()):
        deps = graph[name]
        if not deps:
            lines.append(f'"{name}"')
            continue
        for dep in deps:
            lines.append(f'"{name}" -> "{dep}"')
    return "\n".join(lines)


def save_d2(graph: dict, path: str) -> None:
    """Сохраняет текстовое представление графа в файл .d2.

    Args:
        graph: словарь {имя пакета: список его зависимостей}.
        path: путь к выходному файлу .d2.

    Raises:
        VisualizerError: если не удалось записать файл.
    """
    content = generate_d2(graph)
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
    except OSError as exc:
        raise VisualizerError(
            f"Не удалось записать D2-файл: {exc}"
        ) from exc


def render_svg(d2_path: str, svg_path: str) -> None:
    """Запускает D2 для конвертации .d2 в .svg.

    Args:
        d2_path: путь к входному файлу .d2.
        svg_path: путь к выходному файлу .svg.

    Raises:
        VisualizerError: если D2 не установлен, вернул ошибку
            или превысил таймаут.
    """
    try:
        result = subprocess.run(
            [D2_COMMAND, d2_path, svg_path],
            capture_output=True,
            text=True,
            timeout=D2_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as exc:
        raise VisualizerError(
            f"Утилита '{D2_COMMAND}' не найдена. "
            "Установите D2: https://d2lang.com/tour/install"
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise VisualizerError(
            f"D2 превысил таймаут {D2_TIMEOUT_SECONDS} секунд"
        ) from exc

    if result.returncode != 0:
        raise VisualizerError(
            f"D2 завершился с ошибкой (код {result.returncode}): "
            f"{result.stderr.strip()}"
        )