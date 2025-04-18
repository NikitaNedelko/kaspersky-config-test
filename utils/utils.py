def is_int(value: str | None) -> bool:
    """Проверяет, что значение является целым числом."""
    if value is None:
        return False
    try:
        int_value = int(value)
        return float(int_value) == float(value)
    except (ValueError, TypeError):
        return False
