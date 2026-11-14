"""Тексты сообщений и форматирование ответов бота."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from html import escape

from bot.models import Application, ApplicationStats


@dataclass(frozen=True, slots=True)
class TypeInfo:
    """Тип обращения: код, подпись и подсказка для ввода текста."""

    code: str
    label: str
    hint: str


TYPES: dict[str, TypeInfo] = {
    "lesson": TypeInfo(
        code="lesson",
        label="Запись на занятие",
        hint="Расскажите, на какое занятие хотите записаться: предмет, класс и удобное время.",
    ),
    "question": TypeInfo(
        code="question",
        label="Вопрос по курсу",
        hint="Напишите вопрос по курсу, расписанию или формату обучения.",
    ),
    "other": TypeInfo(
        code="other",
        label="Прочее",
        hint="Опишите ваш вопрос или предложение — передадим администратору.",
    ),
}

START = (
    "👋 <b>Здравствуйте, {name}!</b>\n\n"
    "Это бот онлайн-школы «КлассОнлайн».\n"
    "Помогу записаться на занятие или передать вопрос администратору.\n\n"
    "Выберите тип обращения 👇"
)

HELP = (
    "ℹ️ <b>Как работает бот</b>\n\n"
    "1. Выберите тип обращения.\n"
    "2. Укажите имя и контакт для связи.\n"
    "3. Опишите запрос — заявка сохранится и попадёт администратору.\n\n"
    "<b>Команды</b>\n"
    "/start — главное меню\n"
    "/help — эта справка\n"
    "/cancel — отменить заполнение\n\n"
    "<b>Для администратора</b>\n"
    "/stats — статистика заявок\n"
    "/applications [N] — последние N заявок\n"
    "/export — выгрузка заявок в CSV"
)

CANCEL = "Заполнение заявки отменено.\n\nВернуться в меню — /start."
NAME_PROMPT = (
    "Как вас зовут? Напишите имя и фамилию — так администратору будет проще "
    "с вами связаться."
)
CONTACT_PROMPT = (
    "Укажите контакт для связи: телефон, e-mail или @username в Telegram."
)
TEXT_ONLY = "Пожалуйста, отправьте ответ текстовым сообщением."
ADMIN_ONLY = "🔒 Команда доступна только администратору."
UNKNOWN = (
    "Я не понял команду 🤔\n\n"
    "Откройте меню командой /start или посмотрите справку /help."
)
UNKNOWN_IN_FORM = "Отправьте ответ текстом или нажмите «✖️ Отмена»."
EMPTY_LIST = "🗂 Заявок пока нет."


def start_text(name: str) -> str:
    return START.format(name=escape(name.strip() or "друг"))


def human_datetime(value: str) -> str:
    """Превращает «2026-11-14 12:40:05» в «14.11.2026 12:40»."""
    try:
        moment = datetime.fromisoformat(value)
    except ValueError:
        return value
    return moment.strftime("%d.%m.%Y %H:%M")


def shorten(text: str, limit: int) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _summary_fields(data: dict[str, str]) -> str:
    return (
        f"📌 <b>Тип:</b> {escape(data.get('type_label', '—'))}\n"
        f"👤 <b>Имя:</b> {escape(data.get('full_name', '—'))}\n"
        f"📞 <b>Контакт:</b> {escape(data.get('contact', '—'))}\n"
        f"💬 <b>Сообщение:</b> {escape(data.get('message', '—'))}"
    )


def summary_text(data: dict[str, str]) -> str:
    return (
        "Проверьте заявку:\n\n"
        f"{_summary_fields(data)}\n\n"
        "Если всё верно — нажмите «✅ Отправить»."
    )


def submitted_summary_text(data: dict[str, str]) -> str:
    return f"Заявка отправлена ✅\n\n{_summary_fields(data)}"


def success_text(application: Application) -> str:
    return (
        f"✅ <b>Заявка №{application.id} принята!</b>\n\n"
        f"Дата: {human_datetime(application.created_at)}\n"
        f"Тип: {escape(application.type_label)}\n\n"
        "Администратор свяжется с вами в ближайшее время.\n"
        "Спасибо за обращение!"
    )


def admin_notification(application: Application) -> str:
    username = f"@{application.username}" if application.username else "—"
    return (
        f"🔔 <b>Новая заявка №{application.id}</b>\n\n"
        f"Дата: {human_datetime(application.created_at)}\n"
        f"Тип: {escape(application.type_label)}\n"
        f"Имя: {escape(application.full_name)}\n"
        f"Контакт: {escape(application.contact)}\n"
        f"Telegram: {escape(username)}\n\n"
        f"<b>Сообщение</b>\n{escape(application.message)}"
    )


def stats_text(stats: ApplicationStats) -> str:
    lines = [
        "📊 <b>Статистика заявок</b>",
        "",
        f"Всего: <b>{stats.total}</b>",
        f"Новых: <b>{stats.new}</b>",
        f"За 7 дней: <b>{stats.week}</b>",
    ]
    if stats.by_type:
        lines.append("")
        lines.append("<b>По типам</b>")
        for label, amount in stats.by_type.items():
            lines.append(f"• {escape(label)} — {amount}")
    return "\n".join(lines)


def recent_text(applications: list[Application]) -> str:
    if not applications:
        return EMPTY_LIST

    blocks = ["🗂 <b>Последние заявки</b>"]
    for application in applications:
        blocks.append(
            f"\n<b>№{application.id}</b> · {human_datetime(application.created_at)}\n"
            f"{escape(application.type_label)} · {escape(application.full_name)}\n"
            f"{escape(application.contact)}\n"
            f"{escape(shorten(application.message, 120))}"
        )
    return "\n".join(blocks)
