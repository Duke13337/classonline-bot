"""Создаёт демонстрационную базу data/demo.db с заявками за последние 10 дней."""

from __future__ import annotations

import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from bot.database import SCHEMA  # noqa: E402

DB_PATH = ROOT / "data" / "demo.db"

# (дней назад, часов назад, имя, контакт, тип, сообщение, статус)
DEMO_APPLICATIONS = [
    (10, 3, "Анна Смирнова", "+7 912 345-67-89", "Запись на занятие",
     "Хочу записаться на математику, 8 класс, будни после 17:00.", "processed"),
    (9, 5, "Игорь Петров", "igor.petrov@mail.ru", "Вопрос по курсу",
     "Подскажите, есть ли записи прошедших занятий по физике?", "processed"),
    (8, 2, "Мария Иванова", "@maria_iv", "Прочее",
     "Можно ли перенести оплату на следующую неделю?", "processed"),
    (7, 6, "Данил Зеленов", "+7 900 123-45-67", "Запись на занятие",
     "Интересует подготовка к ОГЭ по информатике, 9 класс.", "processed"),
    (6, 1, "Ольга Кузнецова", "olga.k@yandex.ru", "Вопрос по курсу",
     "С какого класса начинается курс по программированию?", "processed"),
    (5, 4, "Тимур Ахметов", "+7 903 555-11-22", "Запись на занятие",
     "Нужны занятия по английскому, 6 класс, выходные.", "new"),
    (4, 7, "Екатерина Соколова", "@kate_sokol", "Прочее",
     "Предложение: добавить в бота расписание на месяц.", "new"),
    (3, 2, "Артём Волков", "+7 916 222-33-44", "Запись на занятие",
     "Подготовка к ЕГЭ по русскому языку, 11 класс.", "new"),
    (3, 8, "Ника Орлова", "nika.orlova@gmail.com", "Вопрос по курсу",
     "Сколько длится одно занятие и есть ли пробный урок?", "new"),
    (2, 3, "Пётр Морозов", "@petr_moroz", "Запись на занятие",
     "Хочу на курс по робототехнике, 5 класс.", "new"),
    (2, 9, "Софья Лебедева", "+7 905 777-88-99", "Вопрос по курсу",
     "Как отменить занятие, если заболел?", "new"),
    (1, 2, "Максим Гусев", "gusev.max@mail.ru", "Прочее",
     "Не приходит напоминание о занятии в Telegram.", "new"),
    (1, 11, "Алиса Николаева", "@alice_nik", "Запись на занятие",
     "Нужна помощь с домашними заданиями по химии, 9 класс.", "new"),
    (0, 1, "Роман Захаров", "+7 926 111-22-33", "Запись на занятие",
     "Запишите на пробное занятие по математике, 7 класс.", "new"),
]


def main() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    now = datetime.now()
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.executescript(SCHEMA)
        for index, row in enumerate(DEMO_APPLICATIONS, start=1):
            days, hours, name, contact, type_label, message, status = row
            created_at = (now - timedelta(days=days, hours=hours)).replace(
                microsecond=0
            ).isoformat(sep=" ")
            connection.execute(
                """
                INSERT INTO applications
                    (created_at, user_id, username, full_name, contact, type, message, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    created_at,
                    1000 + index,
                    f"user_{index}",
                    name,
                    contact,
                    type_label,
                    message,
                    status,
                ),
            )
        connection.commit()
    finally:
        connection.close()

    print(f"Демо-база создана: {DB_PATH}")
    print(f"Заявок: {len(DEMO_APPLICATIONS)}")


if __name__ == "__main__":
    main()
