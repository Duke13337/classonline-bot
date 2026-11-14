"""Настройки приложения, читаются из переменных окружения / .env."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "applications.db"

load_dotenv(BASE_DIR / ".env")


def _parse_admin_ids(raw: str) -> frozenset[int]:
    """Разбирает список ID вида «123, 456;789» в множество целых чисел."""
    result: set[int] = set()
    for chunk in raw.replace(";", ",").split(","):
        chunk = chunk.strip()
        if chunk.lstrip("-").isdigit():
            result.add(int(chunk))
    return frozenset(result)


@dataclass(frozen=True, slots=True)
class Settings:
    """Иммутабельный набор настроек бота."""

    bot_token: str
    admin_ids: frozenset[int] = frozenset()
    db_path: Path = DEFAULT_DB_PATH

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("BOT_TOKEN", "").strip()
        if not token:
            raise RuntimeError(
                "Не задан BOT_TOKEN. Скопируйте .env.example в .env "
                "и укажите токен, полученный у @BotFather."
            )

        raw_path = os.getenv("DB_PATH", "").strip()
        db_path = Path(raw_path).expanduser() if raw_path else DEFAULT_DB_PATH
        if not db_path.is_absolute():
            db_path = (BASE_DIR / db_path).resolve()

        return cls(
            bot_token=token,
            admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
            db_path=db_path,
        )
