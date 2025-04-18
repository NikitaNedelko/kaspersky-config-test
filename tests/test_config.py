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
        "is_valid_CoreDumpsPath",
        "is_valid_MachineId",
        "is_valid_locale",
        "is_valid_ConnectTimeout",
        "is_valid_MaxVirtualMemory",
        "is_valid_MaxMemory",
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


@pytest.mark.parametrize(
    "section, parameter, valid_values",
    [
        ("General", "AdditionalDNSLookup", ["true", "false", "yes", "no"]),
        ("General", "CoreDumps", ["true", "false", "yes", "no"]),
        ("General", "RevealSensitiveInfoInTraces", ["true", "false", "yes", "no"]),
        ("General", "UseFanotify", ["true", "false", "yes", "no"]),
        ("General", "KsvlaMode", ["true", "false", "yes", "no"]),
        ("General", "StartupTraces", ["true", "false", "yes", "no"]),
        ("General", "PackageType", ["rpm", "deb"]),
    ],
)
def test_boolean_parameter(
    config_with_expected: tuple[ConfigValidator, bool],
    section: str,
    parameter: str,
    valid_values: list[str],
):
    """Проверяет, что параметр принимает true/false/yes/no в любом регистре."""
    config, expected = config_with_expected
    is_valid, msg = config.validate_enum(section, parameter, valid_values)
    assert (
        is_valid == expected
    ), f"[{parameter}] Результат: {is_valid}, Ожидалось: {expected}. Детали: {msg}"


@pytest.mark.parametrize(
    "section, parameter, min_value, max_value",
    [
        ("General", "ScanMemoryLimit", 1024, 8192),
        ("General", "ExecArgMax", 10, 100),
        ("General", "ExecEnvMax", 10, 100),
        ("General", "MaxInotifyWatches", 1000, 1000000),
        ("General", "MaxInotifyInstances", 1024, 8192),
        ("Watchdog", "PingInterval", 100, 10000),
    ],
)
def test_integer_range_parameters(
    config_with_expected: tuple[ConfigValidator, bool],
    section: str,
    parameter: str,
    min_value: int,
    max_value: int,
):
    """Проверяет, что параметр является целым числом в заданном диапазоне."""
    config, expected = config_with_expected
    is_valid, msg = config.validate_int_in_range(
        section, parameter, min_value, max_value
    )
    assert (
        is_valid == expected
    ), f"[{parameter}] Результат: {is_valid}, Ожидалось: {expected}. Детали: {msg}"
