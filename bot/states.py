"""Состояния диалога заполнения заявки."""

from aiogram.fsm.state import State, StatesGroup


class ApplicationForm(StatesGroup):
    name = State()
    contact = State()
    message = State()
    confirm = State()
