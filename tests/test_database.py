"""Тесты работы с базой данных."""

import asyncio
from collections.abc import Coroutine
from pathlib import Path
from typing import Any

from bot.database import ApplicationRepository


def run(coro: Coroutine[Any, Any, None]) -> None:
    asyncio.run(coro)


def test_add_and_read(tmp_path: Path) -> None:
    async def scenario() -> None:
        repo = ApplicationRepository(tmp_path / "test.db")
        await repo.connect()
        try:
            first = await repo.add(
                user_id=100,
                username="danil",
                full_name="Данил Зеленов",
                contact="@danil",
                type_label="Запись на занятие",
                message="Хочу на математику",
            )
            second = await repo.add(
                user_id=101,
                username=None,
                full_name="Анна Смирнова",
                contact="anna@example.com",
                type_label="Прочее",
                message="Вопрос по оплате",
            )

            assert first.id == 1
            assert second.id == 2
            assert first.status == "new"
            assert await repo.count() == 2

            rows = await repo.recent()
            assert [row.id for row in rows] == [2, 1]
            assert rows[0].full_name == "Анна Смирнова"
            assert rows[1].username == "danil"
        finally:
            await repo.close()

    run(scenario())


def test_data_survives_reconnect(tmp_path: Path) -> None:
    db_path = tmp_path / "persistent.db"

    async def scenario() -> None:
        repo = ApplicationRepository(db_path)
        await repo.connect()
        await repo.add(
            user_id=1,
            username=None,
            full_name="Иван Петров",
            contact="+7 900 000-00-00",
            type_label="Прочее",
            message="Проверка сохранения",
        )
        await repo.close()

        repo = ApplicationRepository(db_path)
        await repo.connect()
        try:
            assert await repo.count() == 1
        finally:
            await repo.close()

    run(scenario())


def test_stats(tmp_path: Path) -> None:
    async def scenario() -> None:
        repo = ApplicationRepository(tmp_path / "stats.db")
        await repo.connect()
        try:
            for type_label in (
                "Запись на занятие",
                "Запись на занятие",
                "Вопрос по курсу",
            ):
                await repo.add(
                    user_id=1,
                    username=None,
                    full_name="Тестовый Пользователь",
                    contact="@tester",
                    type_label=type_label,
                    message="Тестовая заявка",
                )

            stats = await repo.stats()
            assert stats.total == 3
            assert stats.new == 3
            assert stats.week == 3
            assert stats.by_type == {
                "Запись на занятие": 2,
                "Вопрос по курсу": 1,
            }
        finally:
            await repo.close()

    run(scenario())


def test_recent_limit(tmp_path: Path) -> None:
    async def scenario() -> None:
        repo = ApplicationRepository(tmp_path / "limit.db")
        await repo.connect()
        try:
            for index in range(1, 4):
                await repo.add(
                    user_id=index,
                    username=None,
                    full_name=f"Пользователь {index}",
                    contact="@tester",
                    type_label="Прочее",
                    message=f"Заявка {index}",
                )

            assert len(await repo.recent(limit=2)) == 2
            assert len(await repo.recent(limit=0)) == 1
        finally:
            await repo.close()

    run(scenario())
