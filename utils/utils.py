def is_int(value: str | None) -> bool:
    """Проверяет, что значение является целым числом."""
    if value is None:
        return False
    try:
        int_value = int(value)
        return float(int_value) == float(value)
    except (ValueError, TypeError):
        return False


def is_float(value: str | None) -> bool:
    """Проверяет, что значение является числом с плавающей точкой."""
    if value is None:
        return False
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False
