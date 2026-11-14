"""Сценарий заполнения заявки."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot import keyboards, texts
from bot.config import Settings
from bot.database import ApplicationRepository
from bot.states import ApplicationForm
from bot.validation import (
    ValidationError,
    validate_contact,
    validate_message,
    validate_name,
)

logger = logging.getLogger(__name__)
router = Router(name="application")


@router.callback_query(F.data.startswith("type:"))
async def choose_type(callback: CallbackQuery, state: FSMContext) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    code = callback.data.partition(":")[2]
    info = texts.TYPES.get(code)
    if info is None:
        await callback.answer("Неизвестный тип обращения", show_alert=True)
        return

    await state.set_state(ApplicationForm.name)
    await state.update_data(type_code=info.code, type_label=info.label)
    await callback.message.edit_text(
        f"Вы выбрали: <b>{info.label}</b>\n\n{texts.NAME_PROMPT}",
        reply_markup=keyboards.cancel_menu(),
    )
    await callback.answer()


@router.message(ApplicationForm.name)
async def process_name(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(texts.TEXT_ONLY, reply_markup=keyboards.cancel_menu())
        return
    try:
        full_name = validate_name(message.text)
    except ValidationError as error:
        await message.answer(f"⚠️ {error}\n\nПопробуйте ещё раз.")
        return

    await state.update_data(full_name=full_name)
    await state.set_state(ApplicationForm.contact)
    await message.answer(texts.CONTACT_PROMPT, reply_markup=keyboards.cancel_menu())


@router.message(ApplicationForm.contact)
async def process_contact(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(texts.TEXT_ONLY, reply_markup=keyboards.cancel_menu())
        return
    try:
        contact = validate_contact(message.text)
    except ValidationError as error:
        await message.answer(f"⚠️ {error}\n\nПопробуйте ещё раз.")
        return

    data = await state.get_data()
    hint = texts.TYPES.get(data.get("type_code", ""), None)
    await state.update_data(contact=contact)
    await state.set_state(ApplicationForm.message)
    await message.answer(
        hint.hint if hint else "Опишите ваш вопрос или предложение.",
        reply_markup=keyboards.cancel_menu(),
    )


@router.message(ApplicationForm.message)
async def process_message(message: Message, state: FSMContext) -> None:
    if not message.text:
        await message.answer(texts.TEXT_ONLY, reply_markup=keyboards.cancel_menu())
        return
    try:
        text = validate_message(message.text)
    except ValidationError as error:
        await message.answer(f"⚠️ {error}\n\nПопробуйте ещё раз.")
        return

    await state.update_data(message=text)
    data = await state.get_data()
    await state.set_state(ApplicationForm.confirm)
    await message.answer(texts.summary_text(data), reply_markup=keyboards.confirm_menu())


@router.callback_query(ApplicationForm.confirm, F.data == "form:confirm")
async def submit_application(
    callback: CallbackQuery,
    state: FSMContext,
    repo: ApplicationRepository,
    settings: Settings,
) -> None:
    if callback.message is None or callback.from_user is None:
        await callback.answer()
        return

    data = await state.get_data()
    required = ("type_label", "full_name", "contact", "message")
    if any(not data.get(field) for field in required):
        await state.clear()
        await callback.answer("Не хватает данных — начните заново", show_alert=True)
        await callback.message.edit_text(
            "Что-то потерялось. Начните, пожалуйста, заново: /start",
            reply_markup=keyboards.main_menu(),
        )
        return

    application = await repo.add(
        user_id=callback.from_user.id,
        username=callback.from_user.username,
        full_name=str(data["full_name"]),
        contact=str(data["contact"]),
        type_label=str(data["type_label"]),
        message=str(data["message"]),
    )

    await state.clear()
    await callback.message.edit_text(texts.submitted_summary_text(data))
    await callback.message.answer(
        texts.success_text(application), reply_markup=keyboards.main_menu()
    )
    await callback.answer("Заявка отправлена")

    notification = texts.admin_notification(application)
    for admin_id in settings.admin_ids:
        try:
            await callback.bot.send_message(admin_id, notification)
        except TelegramAPIError:
            logger.warning("Не удалось отправить уведомление администратору %s", admin_id)


@router.callback_query(ApplicationForm.confirm, F.data == "form:edit")
async def restart_form(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ApplicationForm.name)
    await state.update_data(full_name=None, contact=None, message=None)
    await callback.answer()
    if callback.message is not None:
        await callback.message.edit_text(
            f"Хорошо, заполним заново.\n\n{texts.NAME_PROMPT}",
            reply_markup=keyboards.cancel_menu(),
        )
