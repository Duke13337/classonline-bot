"""Точка входа и сборка приложения."""

from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import Settings
from bot.database import ApplicationRepository
from bot.handlers import admin, application, common, fallback

logger = logging.getLogger(__name__)


def build_dispatcher(repo: ApplicationRepository, settings: Settings) -> Dispatcher:
    """Собирает диспетчер и передаёт зависимости в обработчики."""
    dispatcher = Dispatcher(storage=MemoryStorage())
    dispatcher["repo"] = repo
    dispatcher["settings"] = settings
    dispatcher.include_routers(
        common.router,
        application.router,
        admin.router,
        fallback.router,
    )
    return dispatcher


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )

    settings = Settings.from_env()
    repo = ApplicationRepository(settings.db_path)
    await repo.connect()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dispatcher = build_dispatcher(repo, settings)

    logger.info("База данных: %s", settings.db_path)
    logger.info("Администраторы: %s", sorted(settings.admin_ids) or "не заданы")

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Бот запущен. Остановка — Ctrl+C.")
        await dispatcher.start_polling(bot)
    finally:
        await repo.close()
        await bot.session.close()
        logger.info("Бот остановлен.")
