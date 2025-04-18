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
        ("example/empty_values_config.ini", False),
        ("example/no_parameters_config.ini", False),
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


@pytest.mark.parametrize(
    "validator_func_name",
    [
        "is_valid_ScanMemoryLimit",
        "is_valid_PackageType",
        "is_valid_ExecArgMax",
        "is_valid_AdditionalDNSLookup",
    ],
)
def test_parameter(
    config_with_expected: tuple[ConfigValidator, bool], validator_func_name: str
):
    """Универсальный тест для проверки параметров через имя функции."""
    config, expected = config_with_expected
    validator_func = getattr(config, validator_func_name)
    is_valid, msg = validator_func()
    assert (
        is_valid == expected
    ), f"[{validator_func_name}] Результат: {is_valid}, Ожидалось: {expected}. Детали: {msg}"


"""
pytest --cov=. --cov-report=html tests/
"""
