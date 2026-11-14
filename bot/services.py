"""Экспорт заявок в CSV."""

from __future__ import annotations

import csv
import io
from collections.abc import Sequence

from bot.models import Application

CSV_HEADER = (
    "id",
    "created_at",
    "user_id",
    "username",
    "full_name",
    "contact",
    "type",
    "message",
    "status",
)


def applications_to_csv(applications: Sequence[Application]) -> bytes:
    """Формирует CSV с BOM, чтобы Excel корректно открыл кириллицу."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\r\n")
    writer.writerow(CSV_HEADER)
    for application in applications:
        writer.writerow(
            (
                application.id,
                application.created_at,
                application.user_id,
                application.username or "",
                application.full_name,
                application.contact,
                application.type_label,
                application.message,
                application.status,
            )
        )
    return ("\ufeff" + buffer.getvalue()).encode("utf-8")
