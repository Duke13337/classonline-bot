"""Тесты текстов бота."""

from bot import texts
from bot.models import Application, ApplicationStats

APPLICATION = Application(
    id=14,
    created_at="2026-11-14 12:40:05",
    user_id=100,
    username="danil",
    full_name="Данил <b>",
    contact="@danil",
    type_label="Прочее",
    message="Текст <script>alert()</script>",
)


def test_human_datetime() -> None:
    assert texts.human_datetime("2026-11-14 12:40:05") == "14.11.2026 12:40"


def test_human_datetime_keeps_unknown_value() -> None:
    assert texts.human_datetime("не дата") == "не дата"


def test_start_escapes_name() -> None:
    assert "&lt;b&gt;" in texts.start_text("<b>")


def test_summary_escapes_html() -> None:
    summary = texts.summary_text(
        {
            "type_label": "Прочее",
            "full_name": "Данил",
            "contact": "@danil",
            "message": "<b>привет</b>",
        }
    )
    assert "&lt;b&gt;привет&lt;/b&gt;" in summary
    assert "<b>привет</b>" not in summary


def test_success_contains_number_and_date() -> None:
    message = texts.success_text(APPLICATION)
    assert "№14" in message
    assert "14.11.2026 12:40" in message


def test_admin_notification_escapes_user_data() -> None:
    message = texts.admin_notification(APPLICATION)
    assert "@danil" in message
    assert "&lt;script&gt;" in message
    assert "<script>" not in message


def test_stats_text_lists_types() -> None:
    stats = ApplicationStats(
        total=3,
        new=2,
        week=1,
        by_type={"Запись на занятие": 2, "Прочее": 1},
    )
    message = texts.stats_text(stats)
    assert "Всего: <b>3</b>" in message
    assert "• Запись на занятие — 2" in message


def test_recent_text_empty_list() -> None:
    assert texts.recent_text([]) == texts.EMPTY_LIST


def test_recent_text_shortens_long_message() -> None:
    application = Application(
        id=1,
        created_at="2026-11-14 12:40:05",
        user_id=1,
        username=None,
        full_name="Иван",
        contact="@ivan",
        type_label="Прочее",
        message="Слово " * 100,
    )
    message = texts.recent_text([application])
    assert "…" in message
    assert "№1" in message
