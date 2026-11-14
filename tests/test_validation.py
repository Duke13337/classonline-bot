"""Тесты проверки пользовательского ввода."""

import pytest

from bot.validation import (
    ValidationError,
    validate_contact,
    validate_message,
    validate_name,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("  Данил   Зеленов ", "Данил Зеленов"),
        ("Анна-Мария Петрова", "Анна-Мария Петрова"),
        ("John Smith", "John Smith"),
    ],
)
def test_validate_name_accepts(raw: str, expected: str) -> None:
    assert validate_name(raw) == expected


@pytest.mark.parametrize("raw", ["", "   ", "12345", "a", "х" * 101])
def test_validate_name_rejects(raw: str) -> None:
    with pytest.raises(ValidationError):
        validate_name(raw)


@pytest.mark.parametrize(
    "raw",
    [
        "+7 900 123-45-67",
        "8 (900) 123-45-67",
        "student@example.com",
        "danil.zelenov@mail.ru",
        "@class_online",
    ],
)
def test_validate_contact_accepts(raw: str) -> None:
    assert validate_contact(raw) == raw


@pytest.mark.parametrize(
    "raw",
    ["", "123", "почта", "@ab", "user@site", "abc def", "@user-name"],
)
def test_validate_contact_rejects(raw: str) -> None:
    with pytest.raises(ValidationError):
        validate_contact(raw)


def test_validate_message_strips_spaces() -> None:
    assert validate_message("  Хочу на математику  ") == "Хочу на математику"


@pytest.mark.parametrize("raw", ["", "  hi  ", "x" * 1001])
def test_validate_message_rejects(raw: str) -> None:
    with pytest.raises(ValidationError):
        validate_message(raw)
