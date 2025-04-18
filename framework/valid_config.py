"""Логика проверки конфигурационного файла на корректность и его считывание"""

import configparser
import os
import uuid
from utils.utils import is_int


class ConfigValidator:
    """
    Класс для проверки конфигурационного файла на корректность."""

    def __init__(self, path: str):
        """Инициализация класса ConfigValidator."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Конфигурационный файл не найден: {path}")
        self.config = configparser.ConfigParser()
        self.config.read(path)

    def get(self, section: str, parameter: str) -> str:
        if section not in self.config:
            raise ValueError(f"Секция не найдена: {section}")
        if parameter not in self.config[section]:
            raise ValueError(f"Параметр не найден: {parameter} в секции {section}")
        return self.config.get(section, parameter)

    def safe_get(self, section: str, parameter: str) -> tuple[bool, str]:
        """
        Пытается получить значение параметра.
        Возвращает (False, сообщение об ошибке) если параметра нет,
        или (True, значение) если всё хорошо.
        """
        try:
            value = self.get(section, parameter)
            return True, value
        except ValueError as e:
            return False, str(e)

    def validate_int_in_range(
        self, section: str, parameter: str, min_value: int, max_value: int
    ) -> tuple[bool, str]:
        """
        Проверяет, что параметр существует, его значение — целое число,
        и оно лежит в заданном диапазоне [min_value, max_value].
        """
        ok, value = self.safe_get(section, parameter)
        if not ok:
            return False, f"Ошибка: {value}"

        if not is_int(value):
            return False, f"{parameter} должно быть целым числом, сейчас: '{value}'"

        value = int(value)

        if not min_value <= value <= max_value:
            return (
                False,
                f"{parameter}={value} вне допустимого диапазона [{min_value}-{max_value}]",
            )

        return True, f"{parameter} корректно"

    def validate_enum(
        self, section: str, parameter: str, valid_values: list[str]
    ) -> tuple[bool, str]:
        """
        Проверяет, что параметр существует
        и его значение входит в список допустимых значений (без учёта регистра).
        """
        ok, value = self.safe_get(section, parameter)
        if not ok:
            return False, f"Ошибка: {value}"

        if value.lower() not in [v.lower() for v in valid_values]:
            return (
                False,
                f"{parameter} должно быть одним из {valid_values}, сейчас: '{value}'",
            )

        return True, f"{parameter} корректно"

    def is_valid_ScanMemoryLimit(self) -> tuple[bool, str]:
        """Проверяет, что ScanMemoryLimit целое число в диапазоне [1024-8192]."""
        return self.validate_int_in_range("General", "ScanMemoryLimit", 1024, 8192)

    def is_valid_PackageType(self) -> tuple[bool, str]:
        """Проверяет, что PackageType равен 'rpm' или 'deb' (регистр не учитывается)."""
        return self.validate_enum("General", "PackageType", ["rpm", "deb"])

    def is_valid_ExecArgMax(self) -> tuple[bool, str]:
        """Проверяет, что ExecArgMax целое число в интервале [10-100]."""
        return self.validate_int_in_range("General", "ExecArgMax", 10, 100)

    def is_valid_AdditionalDNSLookup(self) -> tuple[bool, str]:
        """Проверяет, что AdditionalDNSLookup true/false/yes/no в любом регистре"""
        return self.validate_enum(
            "General", "AdditionalDNSLookup", ["true", "false", "yes", "no"]
        )

    # def is_valid_machine_id(self):
    #     """Проверяет, что MachineId является корректным UUID."""
    #     value = self.get("General", "MachineId").strip()
    #     try:
    #         uuid.UUID(value)
    #         return True
    #     except ValueError:
    #         return False
