"""Модели данных приложения."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Application:
    """Заявка, сохранённая в базе данных."""

    id: int
    created_at: str
    user_id: int
    username: str | None
    full_name: str
    contact: str
    type_label: str
    message: str
    status: str = "new"


@dataclass(frozen=True, slots=True)
class ApplicationStats:
    """Сводка по заявкам для команды /stats."""

    total: int
    new: int
    week: int
    by_type: dict[str, int]
