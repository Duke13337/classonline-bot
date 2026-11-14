"""Тесты экспорта в CSV."""

import csv
import io

from bot.models import Application
from bot.services import CSV_HEADER, applications_to_csv


def make_application(**overrides: object) -> Application:
    values: dict[str, object] = {
        "id": 7,
        "created_at": "2026-11-14 12:40:05",
        "user_id": 100,
        "username": "danil",
        "full_name": "Данил Зеленов",
        "contact": "+7 900 123-45-67",
        "type_label": "Запись на занятие",
        "message": "Хочу на математику",
        "status": "new",
    }
    values.update(overrides)
    return Application(**values)  # type: ignore[arg-type]


def test_csv_has_bom_header_and_row() -> None:
    payload = applications_to_csv([make_application()])
    text = payload.decode("utf-8")
    assert text.startswith("\ufeff")

    rows = list(csv.reader(io.StringIO(text.lstrip("\ufeff"))))
    assert rows[0] == list(CSV_HEADER)
    assert rows[1][0] == "7"
    assert rows[1][4] == "Данил Зеленов"
    assert rows[1][7] == "Хочу на математику"


def test_csv_handles_empty_username() -> None:
    rows = list(
        csv.reader(
            io.StringIO(
                applications_to_csv([make_application(username=None)])
                .decode("utf-8")
                .lstrip("\ufeff")
            )
        )
    )
    assert rows[1][3] == ""


def test_csv_without_applications_has_only_header() -> None:
    rows = list(
        csv.reader(
            io.StringIO(
                applications_to_csv([]).decode("utf-8").lstrip("\ufeff")
            )
        )
    )
    assert rows == [list(CSV_HEADER)]
