"""Работа с базой данных SQLite."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import aiosqlite

from bot.models import Application, ApplicationStats

SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT    NOT NULL,
    user_id    INTEGER NOT NULL,
    username   TEXT,
    full_name  TEXT    NOT NULL,
    contact    TEXT    NOT NULL,
    type       TEXT    NOT NULL,
    message    TEXT    NOT NULL,
    status     TEXT    NOT NULL DEFAULT 'new'
);

CREATE INDEX IF NOT EXISTS idx_applications_created_at
    ON applications (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_applications_user_id
    ON applications (user_id);
"""


class ApplicationRepository:
    """Репозиторий заявок поверх SQLite.

    Одно соединение на процесс бота: этого достаточно для учебного проекта
    и последовательной обработки обновлений Telegram.
    """

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        if self._connection is not None:
            return
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = await aiosqlite.connect(self._db_path)
        self._connection.row_factory = aiosqlite.Row
        await self._connection.executescript(SCHEMA)
        await self._connection.commit()

    async def close(self) -> None:
        if self._connection is not None:
            await self._connection.close()
            self._connection = None

    async def add(
        self,
        *,
        user_id: int,
        username: str | None,
        full_name: str,
        contact: str,
        type_label: str,
        message: str,
    ) -> Application:
        created_at = datetime.now().replace(microsecond=0).isoformat(sep=" ")
        cursor = await self._db.execute(
            """
            INSERT INTO applications
                (created_at, user_id, username, full_name, contact, type, message)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (created_at, user_id, username, full_name, contact, type_label, message),
        )
        await self._db.commit()
        return Application(
            id=int(cursor.lastrowid or 0),
            created_at=created_at,
            user_id=user_id,
            username=username,
            full_name=full_name,
            contact=contact,
            type_label=type_label,
            message=message,
        )

    async def count(self) -> int:
        return await self._scalar("SELECT COUNT(*) FROM applications")

    async def recent(self, limit: int = 10) -> list[Application]:
        limit = max(1, min(limit, 1000))
        async with self._db.execute(
            "SELECT * FROM applications ORDER BY id DESC LIMIT ?", (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
        return [self._to_application(row) for row in rows]

    async def stats(self) -> ApplicationStats:
        total = await self._scalar("SELECT COUNT(*) FROM applications")
        new = await self._scalar(
            "SELECT COUNT(*) FROM applications WHERE status = 'new'"
        )
        since = (datetime.now() - timedelta(days=7)).replace(microsecond=0)
        week = await self._scalar(
            "SELECT COUNT(*) FROM applications WHERE created_at >= ?",
            (since.isoformat(sep=" "),),
        )

        by_type: dict[str, int] = {}
        async with self._db.execute(
            """
            SELECT type, COUNT(*) AS amount
            FROM applications
            GROUP BY type
            ORDER BY amount DESC, type
            """
        ) as cursor:
            async for row in cursor:
                by_type[str(row["type"])] = int(row["amount"])

        return ApplicationStats(total=total, new=new, week=week, by_type=by_type)

    @property
    def _db(self) -> aiosqlite.Connection:
        if self._connection is None:
            raise RuntimeError("Соединение с базой не открыто: вызовите connect()")
        return self._connection

    async def _scalar(self, query: str, params: tuple[object, ...] = ()) -> int:
        async with self._db.execute(query, params) as cursor:
            row = await cursor.fetchone()
        return int(row[0]) if row else 0

    @staticmethod
    def _to_application(row: aiosqlite.Row) -> Application:
        return Application(
            id=int(row["id"]),
            created_at=str(row["created_at"]),
            user_id=int(row["user_id"]),
            username=row["username"],
            full_name=str(row["full_name"]),
            contact=str(row["contact"]),
            type_label=str(row["type"]),
            message=str(row["message"]),
            status=str(row["status"]),
        )
