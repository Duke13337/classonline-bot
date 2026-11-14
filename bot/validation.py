"""Проверка данных, которые вводит пользователь."""

from __future__ import annotations

import re

USERNAME_RE = re.compile(r"^@[A-Za-z0-9_]{5,32}$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-zА-Яа-я]{2,}$")
PHONE_RE = re.compile(r"^[+]?[\d\s()\-]{10,20}$")


class ValidationError(ValueError):
    """Введённые данные не проходят проверку."""


def normalize(value: str) -> str:
    """Убирает лишние пробелы и переводы строк."""
    return " ".join(value.split())


def validate_name(raw: str) -> str:
    value = normalize(raw)
    if len(value) < 2:
        raise ValidationError("Имя слишком короткое — укажите имя и фамилию.")
    if len(value) > 100:
        raise ValidationError("Слишком длинное имя — не более 100 символов.")
    if not any(char.isalpha() for char in value):
        raise ValidationError("Имя должно содержать буквы.")
    return value


def validate_contact(raw: str) -> str:
    value = normalize(raw)
    if len(value) < 5:
        raise ValidationError("Контакт слишком короткий — укажите телефон, e-mail или @username.")
    if len(value) > 100:
        raise ValidationError("Слишком длинный контакт — не более 100 символов.")
    if value.startswith("@"):
        if not USERNAME_RE.match(value):
            raise ValidationError(
                "Telegram-username: от 5 до 32 символов, латиница, цифры и «_»."
            )
        return value
    if EMAIL_RE.match(value):
        return value
    if PHONE_RE.match(value) and len(re.sub(r"\D", "", value)) >= 10:
        return value
    raise ValidationError("Не похоже на контакт. Укажите телефон, e-mail или @username.")


def validate_message(raw: str, *, min_length: int = 5, max_length: int = 1000) -> str:
    value = raw.strip()
    if len(value) < min_length:
        raise ValidationError(f"Слишком короткое сообщение — минимум {min_length} символов.")
    if len(value) > max_length:
        raise ValidationError(f"Слишком длинное сообщение — максимум {max_length} символов.")
    return value
