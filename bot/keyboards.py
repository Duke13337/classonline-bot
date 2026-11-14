"""Инлайн-клавиатуры бота."""

from __future__ import annotations

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Запись на занятие", callback_data="type:lesson")
    builder.button(text="❓ Вопрос по курсу", callback_data="type:question")
    builder.button(text="💬 Прочее", callback_data="type:other")
    builder.button(text="ℹ️ Помощь", callback_data="menu:help")
    builder.adjust(1)
    return builder.as_markup()


def cancel_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✖️ Отмена", callback_data="form:cancel")
    return builder.as_markup()


def confirm_menu() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Отправить", callback_data="form:confirm")
    builder.button(text="✏️ Заполнить заново", callback_data="form:edit")
    builder.button(text="✖️ Отмена", callback_data="form:cancel")
    builder.adjust(1)
    return builder.as_markup()
