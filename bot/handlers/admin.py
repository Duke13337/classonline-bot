"""Команды администратора: статистика, список заявок, экспорт."""

from __future__ import annotations

from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, Message

from bot import texts
from bot.config import Settings
from bot.database import ApplicationRepository
from bot.services import applications_to_csv

router = Router(name="admin")

DEFAULT_LIMIT = 5
MAX_LIMIT = 20


def _is_admin(user_id: int, settings: Settings) -> bool:
    return user_id in settings.admin_ids


@router.message(Command("stats"))
async def cmd_stats(
    message: Message,
    repo: ApplicationRepository,
    settings: Settings,
) -> None:
    if message.from_user is None:
        return
    if not _is_admin(message.from_user.id, settings):
        await message.answer(texts.ADMIN_ONLY)
        return
    await message.answer(texts.stats_text(await repo.stats()))


@router.message(Command("applications"))
async def cmd_applications(
    message: Message,
    repo: ApplicationRepository,
    settings: Settings,
) -> None:
    if message.from_user is None:
        return
    if not _is_admin(message.from_user.id, settings):
        await message.answer(texts.ADMIN_ONLY)
        return

    limit = DEFAULT_LIMIT
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) > 1 and parts[1].strip().isdigit():
        limit = min(max(int(parts[1].strip()), 1), MAX_LIMIT)

    await message.answer(texts.recent_text(await repo.recent(limit)))


@router.message(Command("export"))
async def cmd_export(
    message: Message,
    repo: ApplicationRepository,
    settings: Settings,
) -> None:
    if message.from_user is None:
        return
    if not _is_admin(message.from_user.id, settings):
        await message.answer(texts.ADMIN_ONLY)
        return

    applications = await repo.recent(limit=1000)
    payload = applications_to_csv(applications)
    stamp = datetime.now().strftime("%Y-%m-%d")
    document = BufferedInputFile(payload, filename=f"applications_{stamp}.csv")
    await message.answer_document(
        document,
        caption=f"🗂 Выгрузка заявок: {len(applications)} шт.",
    )
