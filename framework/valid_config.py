"""Логика проверки конфигурационного файла на корректность и его считывание"""

import configparser
import os
import uuid
import re
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

    def is_valid_CoreDumpsPath(self) -> tuple[bool, str]:
        """Проверяет, что CoreDumpsPath существует и является абсолютным путём."""
        ok, value = self.safe_get("General", "CoreDumpsPath")
        if not ok:
            return False, f"Ошибка: {value}"

        if not os.path.isabs(value):
            return (
                False,
                f"CoreDumpsPath должен быть абсолютным путём, сейчас: '{value}'",
            )

        if not os.path.isdir(value):
            return (
                False,
                f"CoreDumpsPath не существует или не является директорией: '{value}'",
            )

        return True, "CoreDumpsPath корректно"

    def is_valid_MachineId(self) -> tuple[bool, str]:
        """Проверяет, что MachineId является корректным UUID."""
        ok, value = self.safe_get("General", "MachineId")
        if not ok:
            return False, f"Ошибка: {value}"

        try:
            uuid.UUID(value.strip())
            return True, "MachineId корректно"
        except ValueError:
            return False, f"MachineId невалидный UUID: '{value}'"

    def is_valid_locale(self) -> tuple[bool, str]:
        """Проверяет, что Locale имеет корректный формат."""
        ok, value = self.safe_get("General", "Locale")
        if not ok:
            return False, f"Ошибка: {value}"

        pattern = r"^[a-zA-Z]{2}([-_][a-zA-Z]{2})?(\.UTF-8)?$"
        if not re.fullmatch(pattern, value.strip()):
            return False, f"Locale имеет неверный формат: '{value}'"

        return True, "Locale корректно"
