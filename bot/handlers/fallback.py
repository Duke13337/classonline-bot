"""Обработка сообщений, которые не подошли ни одному сценарию."""

from __future__ import annotations

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import texts

router = Router(name="fallback")


@router.message()
async def unknown_message(message: Message, state: FSMContext) -> None:
    in_form = await state.get_state() is not None
    await message.answer(texts.UNKNOWN_IN_FORM if in_form else texts.UNKNOWN)


@router.callback_query()
async def unknown_callback(callback: CallbackQuery) -> None:
    await callback.answer("Кнопка устарела. Откройте меню командой /start", show_alert=True)
