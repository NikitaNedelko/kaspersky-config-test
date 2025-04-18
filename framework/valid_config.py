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
            raise FileNotFoundError(f"Configuration file not found: {path}")
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

    def is_valid_ScanMemoryLimit(self) -> tuple[bool, str]:
        """Проверяет, что ScanMemoryLimit целое число в диапазоне 1024-8192."""
        clear, value = self.safe_get("General", "ScanMemoryLimit")
        if not clear:
            return False, f"Ошибка: {value}"
        if not is_int(value):
            return False, f"ScanMemoryLimit должно быть целым числом, сейчас: '{value}'"
        if not (1024 <= int(value) <= 8192):
            return False, f"ScanMemoryLimit={value} вне диапазона (1024-8192)"
        return True, "ScanMemoryLimit корректно"

    def is_valid_package_type(self):
        """Проверяет, что PackageType равен 'rpm' или 'deb' (регистр не учитывается)."""
        value = self.get("General", "PackageType")
        return value.lower() in ("rpm", "deb")

    def is_valid_machine_id(self):
        """Проверяет, что MachineId является корректным UUID."""
        value = self.get("General", "MachineId").strip()
        try:
            uuid.UUID(value)
            return True
        except ValueError:
            return False
