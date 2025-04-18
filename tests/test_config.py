"""Тесты для проверки конфигурационного файла"""

import os
import pytest
from framework.valid_config import ConfigValidator


@pytest.fixture(scope="module")
def config():
    """Фикстура для создания объекта ConfigValidator с корректным ini файлом"""
    path = os.environ.get("CONFIG_PATH", "/var/opt/kaspersky/config.ini")
    return ConfigValidator(path)


@pytest.fixture(
    params=[
        ("example/valid_config.ini", True),
        ("example/out_of_range_config.ini", False),
        ("example/invalid_str_config.ini", False),
        ("example/invalid_int_or_float_config.ini", False),
        ("example/empty_config.ini", False),
    ]
)
def config_with_expected(request: pytest.FixtureRequest):
    """Параметризированная фикстура возвращает: ConfigValidator с ожидаемым результатом."""
    path, expected = request.param
    return ConfigValidator(path), expected


def test_init_file_not_found():
    """Проверяет, что при отсутствии файла выбрасывается FileNotFoundError"""
    with pytest.raises(FileNotFoundError):
        ConfigValidator("/path/does/not/exist.ini")


def test_get_invalid_section(config: ConfigValidator):
    """Проверяет, что при отсутствии секции выбрасывается ValueError"""
    with pytest.raises(ValueError, match="Секция не найдена: WatchDogs"):
        config.get("WatchDogs", "PackageType")


def test_get_invalid_parameter(config: ConfigValidator):
    """Проверяет, что при отсутствии параметра выбрасывается ValueError"""
    with pytest.raises(
        ValueError, match="Параметр не найден: WrongParam в секции General"
    ):
        config.get("General", "WrongParam")


def test_ScanMemoryLimit(config_with_expected: tuple[ConfigValidator, bool]):
    """Проверка корректности значения ScanMemoryLimit"""
    config, expected = config_with_expected
    is_valid, msg = config.is_valid_ScanMemoryLimit()
    assert (
        is_valid == expected
    ), f"Результат: {is_valid}, Ожидалось: {expected}. Детали: {msg}"


# def test_

# def test_package_type(config: ConfigValidator):
#     """Проверка корректности значения PackageType"""
#     assert config.is_valid_package_type(), "Ошибка: PackageType должен быть rpm или deb"


# def test_machine_id(config: ConfigValidator):
#     assert config.is_valid_machine_id(), "Ошибка: MachineId не является UUID"


# def test_scan_memory_limit(config:ConfigValidator):
#     assert config.is_valid_ScanMemoryLimit(), "Ошибка: ScanMemoryLimit вне допустимого диапазона"

"""
pytest --cov=. --cov-report=html tests/
"""
