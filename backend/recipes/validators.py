import re
from django.core.exceptions import ValidationError


def username_validator(value):
    """Валидатор для username."""
    regex = r"^[\w.@+-]+\Z"
    if not re.fullmatch(regex, value):
        invalid_characters = sorted(set(re.findall(r"[^\w.@+-]", value)))
        raise ValidationError(
            f"Недопустимые символы {', '.join(invalid_characters)} в username. "
            f"username может содержать только буквы, цифры и "
            f"знаки @, ., +, -, _.",
        )

    if value.lower() == "me":
        raise ValidationError(
            "Использовать имя 'me' в качестве username запрещено."
        )


def color_validator(value):
    """Валидатор для HEX-кода цвета."""
    regex = r"^#([A-Fa-f0-9]{6})$"
    if not re.fullmatch(regex, value):
        raise ValidationError(
            f"Значение '{value}' не является корректным HEX-кодом цвета. "
            "Убедитесь, что цвет указан в формате #RRGGBB."
        )
