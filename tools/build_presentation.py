"""Сборка презентации проекта «КлассОнлайн» (python-pptx).

Запуск:  .venv\\Scripts\\python.exe tools\\build_presentation.py
"""

from __future__ import annotations

from pathlib import Path

from lxml import etree
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "presentation" / "screenshots"
OUT = ROOT / "presentation" / "КлассОнлайн_презентация.pptx"

# ---------------------------------------------------------------------------
# Палитра и шрифты
# ---------------------------------------------------------------------------

NAVY = RGBColor(0x0B, 0x16, 0x26)
NAVY_SOFT = RGBColor(0x10, 0x23, 0x3A)
NAVY_LINE = RGBColor(0x1C, 0x35, 0x50)
BLUE = RGBColor(0x22, 0x9E, 0xD9)
BLUE_DARK = RGBColor(0x18, 0x7C, 0xAE)
BLUE_LIGHT = RGBColor(0xE8, 0xF4, 0xFB)
BLUE_PALE = RGBColor(0xF3, 0xFA, 0xFE)
TEXT = RGBColor(0x10, 0x18, 0x28)
TEXT_SOFT = RGBColor(0x33, 0x41, 0x55)
GRAY = RGBColor(0x64, 0x74, 0x8B)
GRAY_LIGHT = RGBColor(0x9A, 0xA8, 0xB8)
BG = RGBColor(0xF7, 0xF9, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BORDER = RGBColor(0xE2, 0xE8, 0xF0)
GREEN = RGBColor(0x22, 0xC5, 0x5E)
GREEN_DARK = RGBColor(0x15, 0x80, 0x3D)
ORANGE = RGBColor(0xF5, 0x9E, 0x0B)
RED = RGBColor(0xE1, 0x4D, 0x4D)
TEAL = RGBColor(0x14, 0xB8, 0xA6)

FONT = "Segoe UI"
FONT_MONO = "Consolas"
FONT_EMOJI = "Segoe UI Emoji"

W = 13.333
H = 7.5
MARGIN = 0.8
CONTENT_W = W - 2 * MARGIN
TOTAL_SLIDES = 13


# ---------------------------------------------------------------------------
# Базовые помощники
# ---------------------------------------------------------------------------


def set_bg(slide, color: RGBColor) -> None:
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rect(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    *,
    fill: RGBColor | None = WHITE,
    line: RGBColor | None = BORDER,
    radius: float = 0.06,
    line_width: float = 1.0,
    shape_type=MSO_SHAPE.ROUNDED_RECTANGLE,
):
    shape = slide.shapes.add_shape(
        shape_type, Inches(x), Inches(y), Inches(w), Inches(h)
    )
    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(line_width)
    shape.shadow.inherit = False
    if shape_type == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            shape.adjustments[0] = radius
        except (IndexError, ValueError):
            pass
    return shape


def add_circle(slide, x: float, y: float, d: float, *, fill, line=None, line_width=1.0):
    return add_rect(
        slide,
        x,
        y,
        d,
        d,
        fill=fill,
        line=line,
        line_width=line_width,
        shape_type=MSO_SHAPE.OVAL,
    )


def _apply_run(run, spec: dict) -> None:
    font = run.font
    font.name = spec.get("font", FONT)
    font.size = Pt(spec.get("size", 14))
    font.bold = spec.get("bold", False)
    font.italic = spec.get("italic", False)
    font.color.rgb = spec.get("color", TEXT)
    spacing = spec.get("spacing")
    if spacing:
        run._r.get_or_add_rPr().set("spc", str(int(spacing * 100)))


def add_rich(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    paragraphs: list[dict],
    *,
    anchor=MSO_ANCHOR.TOP,
    margins: float = 0.0,
):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margins)
    tf.margin_top = tf.margin_bottom = Inches(margins)
    tf.vertical_anchor = anchor

    for index, para in enumerate(paragraphs):
        p = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        p.alignment = para.get("align", PP_ALIGN.LEFT)
        p.line_spacing = para.get("line_spacing", 1.0)
        p.space_before = Pt(para.get("space_before", 0))
        p.space_after = Pt(para.get("space_after", 0))
        for spec in para["runs"]:
            run = p.add_run()
            run.text = spec["text"]
            _apply_run(run, spec)
    return box


def P(
    text: str,
    *,
    size: float = 14,
    color: RGBColor = TEXT,
    bold: bool = False,
    italic: bool = False,
    font: str = FONT,
    align=PP_ALIGN.LEFT,
    line_spacing: float = 1.0,
    space_after: float = 0,
    space_before: float = 0,
    spacing: float | None = None,
) -> dict:
    spec = {
        "text": text,
        "size": size,
        "color": color,
        "bold": bold,
        "italic": italic,
        "font": font,
        "spacing": spacing,
    }
    return {
        "runs": [spec],
        "align": align,
        "line_spacing": line_spacing,
        "space_after": space_after,
        "space_before": space_before,
    }


def add_text(slide, x, y, w, h, text, **kwargs):
    align = kwargs.pop("align", PP_ALIGN.LEFT)
    anchor = kwargs.pop("anchor", MSO_ANCHOR.TOP)
    return add_rich(
        slide,
        x,
        y,
        w,
        h,
        [P(text, align=align, **kwargs)],
        anchor=anchor,
    )


def add_chip(
    slide,
    x: float,
    y: float,
    w: float,
    h: float,
    text: str,
    *,
    fill: RGBColor = BLUE_LIGHT,
    color: RGBColor = BLUE_DARK,
    size: float = 9.5,
    bold: bool = True,
    font: str = FONT,
    line: RGBColor | None = None,
):
    shape = add_rect(slide, x, y, w, h, fill=fill, line=line, radius=0.5)
    tf = shape.text_frame
    tf.clear()
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = Inches(0.05)
    tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    _apply_run(
        run,
        {
            "text": text,
            "size": size,
            "color": color,
            "bold": bold,
            "font": font,
        },
    )
    return shape


def add_icon(slide, x: float, y: float, d: float, emoji: str, *, fill=BLUE_LIGHT):
    add_circle(slide, x, y, d, fill=fill)
    add_text(
        slide,
        x,
        y + 0.01,
        d,
        d - 0.02,
        emoji,
        size=d * 30,
        font=FONT_EMOJI,
        align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE,
    )


def add_arrow(slide, x: float, y: float, w: float, h: float, *, shape=MSO_SHAPE.RIGHT_ARROW, fill=RGBColor(0xC3, 0xD2, 0xE0)):
    arrow = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = fill
    arrow.line.fill.background()
    arrow.shadow.inherit = False
    return arrow


def add_picture(slide, name: str, x: float, y: float, h: float):
    path = SHOTS / name
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), height=Inches(h))


def add_header(slide, kicker: str, title: str, number: int) -> None:
    set_bg(slide, BG)
    # Декоративные окружности в правом верхнем углу
    ring = add_circle(slide, 12.55, -1.25, 2.6, fill=None, line=RGBColor(0xDD, 0xE9, 0xF4), line_width=1.2)
    ring.line.color.rgb = RGBColor(0xDD, 0xE9, 0xF4)
    add_circle(slide, 12.32, 0.32, 0.09, fill=BLUE, line=None)

    add_text(
        slide,
        MARGIN,
        0.42,
        8.0,
        0.26,
        kicker,
        size=9,
        color=BLUE_DARK,
        bold=True,
        spacing=1.6,
    )
    add_text(slide, MARGIN, 0.65, 11.4, 0.62, title, size=28, color=NAVY, bold=True)
    add_rect(slide, MARGIN, 1.32, CONTENT_W, 0.014, fill=BORDER, line=None, radius=0)

    # Футер
    add_text(
        slide,
        MARGIN,
        7.13,
        7.0,
        0.22,
        "КлассОнлайн · производственная практика",
        size=8,
        color=GRAY_LIGHT,
    )
    add_text(
        slide,
        W - 1.45,
        7.13,
        0.65,
        0.22,
        f"{number:02d} / {TOTAL_SLIDES}",
        size=8,
        color=GRAY_LIGHT,
        align=PP_ALIGN.RIGHT,
    )


def add_card_title(slide, x, y, w, title, body, *, title_size=14, body_size=10.5, color=NAVY):
    add_text(slide, x, y, w, 0.3, title, size=title_size, color=color, bold=True)
    add_text(slide, x, y + 0.34, w, 0.8, body, size=body_size, color=GRAY, line_spacing=1.08)


def add_table_style(slide, rows, cols, x, y, w, h):
    frame = slide.shapes.add_table(rows, cols, Inches(x), Inches(y), Inches(w), Inches(h))
    table = frame.table
    table.first_row = True
    table.horz_banding = False
    table.vert_banding = False
    tbl_pr = table._tbl.tblPr
    style = tbl_pr.find(qn("a:tableStyleId"))
    if style is None:
        style = etree.SubElement(tbl_pr, qn("a:tableStyleId"))
    style.text = "{2D5ABB26-0587-4C30-8999-92F81FD0307C}"  # No Style, No Grid
    return table


def style_cell(cell, text, *, size=9.5, color=TEXT, bold=False, font=FONT, fill=WHITE, align=PP_ALIGN.LEFT):
    cell.fill.solid()
    cell.fill.fore_color.rgb = fill
    cell.margin_left = Inches(0.08)
    cell.margin_right = Inches(0.06)
    cell.margin_top = Inches(0.02)
    cell.margin_bottom = Inches(0.02)
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf = cell.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = align
    p.text = ""
    run = p.add_run()
    run.text = text
    _apply_run(
        run,
        {
            "text": text,
            "size": size,
            "color": color,
            "bold": bold,
            "font": font,
        },
    )


# ---------------------------------------------------------------------------
# Слайды
# ---------------------------------------------------------------------------


def slide_title(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, NAVY)

    add_circle(slide, 8.95, 0.25, 4.7, fill=None, line=NAVY_LINE, line_width=1.3)
    add_circle(slide, 11.85, 5.35, 2.3, fill=None, line=RGBColor(0x17, 0x2C, 0x44), line_width=1.1)
    add_circle(slide, 12.3, 0.45, 0.11, fill=BLUE, line=None)
    add_circle(slide, 8.6, 5.9, 0.08, fill=TEAL, line=None)

    add_text(
        slide,
        0.85,
        0.62,
        6.5,
        0.26,
        "IT TOP COLLEGE · ПРОИЗВОДСТВЕННАЯ ПРАКТИКА",
        size=9.5,
        color=BLUE,
        bold=True,
        spacing=1.4,
    )
    add_rich(
        slide,
        0.85,
        1.0,
        7.1,
        1.75,
        [
            P("Telegram-бот", size=45, color=WHITE, bold=True, line_spacing=0.92),
            P("«КлассОнлайн»", size=45, color=WHITE, bold=True, line_spacing=0.92),
        ],
    )
    add_text(
        slide,
        0.85,
        2.78,
        6.35,
        0.75,
        "Автоматизация приёма заявок на занятия и обращений учеников и родителей",
        size=16,
        color=RGBColor(0xA9, 0xBC, 0xD3),
        line_spacing=1.15,
    )

    add_rect(slide, 0.85, 3.72, 5.65, 0.012, fill=NAVY_LINE, line=None, radius=0)

    labels = [
        (0.85, 3.98, "ВЫПОЛНИЛ", "Зеленов Данил Сергеевич"),
        (3.95, 3.98, "ГРУППА", "11/3-РПО-24/1"),
        (0.85, 4.78, "МЕСТО ПРАКТИКИ", "IT TOP college"),
        (3.95, 4.78, "ОРГАНИЗАЦИЯ", "КлассОнлайн"),
        (0.85, 5.58, "РУКОВОДИТЕЛЬ", "Максим Николаевич"),
    ]
    for x, y, label, value in labels:
        add_text(slide, x, y, 2.9, 0.2, label, size=8, color=RGBColor(0x7F, 0x95, 0xB0), bold=True, spacing=1.0)
        add_text(slide, x, y + 0.2, 3.0, 0.3, value, size=12.5, color=WHITE, bold=True)

    add_text(
        slide,
        0.85,
        6.55,
        4.0,
        0.24,
        "ноябрь 2026",
        size=9,
        color=RGBColor(0x6F, 0x86, 0xA2),
    )

    # Телефон
    add_picture(slide, "start.png", 9.42, 0.5, 6.5)


def slide_goal(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "01 · ПРАКТИКА", "Цель и задачи", 2)

    add_rect(slide, MARGIN, 1.6, 5.0, 5.18, fill=NAVY, line=None, radius=0.05)
    add_chip(slide, 1.1, 1.9, 1.25, 0.34, "ЦЕЛЬ", fill=RGBColor(0x17, 0x32, 0x4D), color=BLUE, size=8.5)
    add_text(
        slide,
        1.1,
        2.45,
        4.3,
        2.2,
        "Собрать обращения в одном месте и убрать ручную обработку сообщений.",
        size=22,
        color=WHITE,
        bold=True,
        line_spacing=1.12,
    )
    add_rect(slide, 1.1, 4.72, 4.3, 0.012, fill=NAVY_LINE, line=None, radius=0)
    add_text(
        slide,
        1.1,
        4.95,
        4.15,
        1.12,
        "Telegram-бот становится единой точкой входа для учеников и родителей: "
        "заявка сохраняется автоматически и не теряется в переписке.",
        size=11.5,
        color=RGBColor(0xA9, 0xBC, 0xD3),
        line_spacing=1.2,
    )

    facts = [("3 типа", 1.1, 1.22), ("9 полей", 2.44, 1.02), ("40 тестов", 3.58, 1.32)]
    for text, x, width in facts:
        add_chip(
            slide,
            x,
            6.2,
            width,
            0.36,
            text,
            fill=RGBColor(0x17, 0x32, 0x4D),
            color=BLUE,
            size=8.5,
            line=RGBColor(0x20, 0x3E, 0x5B),
        )

    tasks = [
        "Разобрать процесс обработки обращений",
        "Спроектировать сценарий диалога",
        "Реализовать бота на Python и aiogram",
        "Спроектировать базу данных SQLite",
        "Добавить админ-команды и уведомления",
        "Протестировать и оформить документацию",
    ]
    y = 1.6
    for index, task in enumerate(tasks, start=1):
        add_rect(slide, 6.15, y, 6.35, 0.74, fill=WHITE, line=BORDER, radius=0.09)
        add_circle(slide, 6.32, y + 0.17, 0.4, fill=BLUE_LIGHT, line=None)
        add_text(
            slide,
            6.32,
            y + 0.18,
            0.4,
            0.38,
            f"{index}",
            size=11,
            color=BLUE_DARK,
            bold=True,
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        add_text(
            slide,
            6.9,
            y + 0.19,
            5.4,
            0.4,
            task,
            size=12.5,
            color=TEXT,
            bold=False,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        y += 0.84


def slide_org(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "02 · ОРГАНИЗАЦИЯ", "КлассОнлайн и роль практиканта", 3)

    add_rect(slide, MARGIN, 1.6, 4.55, 5.18, fill=NAVY, line=None, radius=0.05)
    add_circle(slide, 1.12, 1.92, 0.95, fill=BLUE, line=None)
    add_text(
        slide,
        1.12,
        1.97,
        0.95,
        0.86,
        "К",
        size=34,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
        anchor=MSO_ANCHOR.MIDDLE,
    )
    add_text(slide, 1.12, 3.08, 3.8, 0.4, "КлассОнлайн", size=22, color=WHITE, bold=True)
    add_text(
        slide,
        1.12,
        3.52,
        3.7,
        0.5,
        "онлайн-занятия и курсы для школьников",
        size=11.5,
        color=RGBColor(0xA9, 0xBC, 0xD3),
    )
    add_rect(slide, 1.12, 4.15, 3.95, 0.012, fill=NAVY_LINE, line=None, radius=0)

    facts = [
        ("ФОРМАТ", "онлайн-школа"),
        ("КЛИЕНТЫ", "ученики и родители"),
        ("КАНАЛ", "личные сообщения, вручную"),
    ]
    y = 4.4
    for label, value in facts:
        add_text(slide, 1.12, y, 3.7, 0.18, label, size=7.5, color=RGBColor(0x7F, 0x95, 0xB0), bold=True, spacing=0.8)
        add_text(slide, 1.12, y + 0.18, 3.85, 0.25, value, size=10.5, color=WHITE)
        y += 0.7

    cards = [
        ("⚠️", "Проблема", "Обращения теряются в личных сообщениях, нет единой базы и статистики."),
        ("💡", "Решение", "Бот как единая точка входа: заявка сохраняется автоматически."),
        ("🧩", "Роль практиканта", "Проектирование сценария, разработка, база данных, тесты, документация."),
        ("🧰", "Инструменты", "Python, aiogram 3, SQLite, pytest, Git и GitHub."),
    ]
    positions = [(5.62, 1.6), (9.22, 1.6), (5.62, 3.45), (9.22, 3.45)]
    for (emoji, title, body), (x, y) in zip(cards, positions):
        add_rect(slide, x, y, 3.45, 1.7, fill=WHITE, line=BORDER, radius=0.07)
        add_icon(slide, x + 0.22, y + 0.2, 0.48, emoji)
        add_text(slide, x + 0.8, y + 0.24, 2.45, 0.3, title, size=12.5, color=NAVY, bold=True)
        add_text(slide, x + 0.22, y + 0.82, 3.0, 0.75, body, size=10, color=GRAY, line_spacing=1.12)

    add_text(
        slide,
        5.62,
        5.5,
        7.05,
        0.85,
        "Куратор проекта — Максим Николаевич. Практика проходит на базе IT TOP college, "
        "задача сформулирована онлайн-школой «КлассОнлайн».",
        size=10,
        color=GRAY,
        line_spacing=1.15,
    )


def slide_done(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "03 · РЕЗУЛЬТАТ", "Что сделано", 4)

    cards = [
        ("🧭", "Сценарий", "Три типа обращений, пошаговые состояния, отмена и проверка ввода."),
        ("🤖", "Telegram-бот", "aiogram 3, FSM, инлайн-кнопки и команды /start, /help, /cancel."),
        ("🗄️", "База данных", "SQLite: 9 полей, статусы, индексы по дате и пользователю."),
        ("🛠️", "Админ-функции", "/stats, /applications, /export CSV и уведомления о заявках."),
        ("✅", "Тестирование", "pytest: 40 тестов на валидацию, базу, тексты и экспорт."),
        ("📚", "Документация", "README, техническое описание, паспорт проекта, презентация."),
    ]
    coords = [
        (MARGIN, 1.62),
        (4.78, 1.62),
        (8.76, 1.62),
        (MARGIN, 4.28),
        (4.78, 4.28),
        (8.76, 4.28),
    ]
    for (emoji, title, body), (x, y) in zip(cards, coords):
        add_rect(slide, x, y, 3.85, 2.4, fill=WHITE, line=BORDER, radius=0.06)
        add_icon(slide, x + 0.25, y + 0.24, 0.55, emoji)
        add_text(slide, x + 0.25, y + 0.98, 3.3, 0.32, title, size=14.5, color=NAVY, bold=True)
        add_text(slide, x + 0.25, y + 1.38, 3.35, 0.85, body, size=10.5, color=GRAY, line_spacing=1.12)
        add_rect(slide, x + 0.25, y + 2.1, 0.55, 0.045, fill=BLUE, line=None, radius=0)


def slide_stack(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "04 · СТЕК", "Технологии и инструменты", 5)

    tech = [
        ("🐍", "Python 3.12", "язык бота"),
        ("🤖", "aiogram 3.31", "фреймворк"),
        ("✈️", "Telegram Bot API", "канал общения"),
        ("🗄️", "SQLite", "база данных"),
        ("⚡", "aiosqlite", "асинхронные запросы"),
        ("🔐", "python-dotenv", "токен в .env"),
        ("🧪", "pytest", "автотесты"),
        ("🌿", "Git + GitHub", "версии и публикация"),
    ]
    xs = [MARGIN, 3.86, 6.92, 9.98]
    ys = [1.6, 3.28]
    for index, (emoji, name, role) in enumerate(tech):
        x = xs[index % 4]
        y = ys[index // 4]
        add_rect(slide, x, y, 2.85, 1.5, fill=WHITE, line=BORDER, radius=0.07)
        add_icon(slide, x + 0.2, y + 0.2, 0.46, emoji)
        add_text(slide, x + 0.2, y + 0.78, 2.45, 0.28, name, size=12.5, color=NAVY, bold=True)
        add_text(slide, x + 0.2, y + 1.09, 2.45, 0.26, role, size=9.5, color=GRAY)

    add_rect(slide, MARGIN, 5.15, CONTENT_W, 1.22, fill=BLUE_LIGHT, line=None, radius=0.05)
    add_rect(slide, MARGIN, 5.15, 0.08, 1.22, fill=BLUE, line=None, radius=0)
    add_text(slide, 1.1, 5.35, 4.0, 0.28, "Почему aiogram 3", size=13.5, color=NAVY, bold=True)
    add_rich(
        slide,
        1.1,
        5.68,
        10.9,
        0.8,
        [
            P(
                "Асинхронная обработка, FSM для многошаговых форм, роутеры и фильтры, "
                "удобные инлайн-клавиатуры и HTML-разметка сообщений.",
                size=11,
                color=TEXT_SOFT,
                line_spacing=1.12,
            ),
            P(
                "Токен бота и список ADMIN_IDS хранятся в .env — секреты не попадают в репозиторий.",
                size=9.5,
                color=GRAY,
                line_spacing=1.08,
                space_before=3,
            ),
        ],
    )


def slide_arch(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "05 · АРХИТЕКТУРА", "Как устроен бот", 6)

    bands = [
        ("01", "Telegram", "Пользователь: ученик или родитель"),
        ("02", "aiogram 3 · handlers + FSM", "Сценарий диалога, состояния, инлайн-клавиатуры"),
        ("03", "Валидация и тексты", "validation.py · texts.py · services.py"),
        ("04", "ApplicationRepository", "Единственное место, где выполняется SQL"),
        ("05", "SQLite · applications.db", "Таблицы, индексы, выборки и статистика"),
    ]
    x, w = MARGIN, 7.35
    y = 1.55
    for number, title, subtitle in bands:
        add_rect(slide, x, y, w, 0.78, fill=WHITE, line=BORDER, radius=0.08)
        add_circle(slide, x + 0.18, y + 0.19, 0.4, fill=BLUE_LIGHT, line=None)
        add_text(
            slide,
            x + 0.18,
            y + 0.2,
            0.4,
            0.38,
            number,
            size=9.5,
            color=BLUE_DARK,
            bold=True,
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        add_text(slide, x + 0.72, y + 0.13, 6.3, 0.28, title, size=12.5, color=NAVY, bold=True)
        add_text(slide, x + 0.72, y + 0.42, 6.3, 0.24, subtitle, size=9.5, color=GRAY)
        if number != "05":
            add_arrow(slide, x + w / 2 - 0.09, y + 0.79, 0.18, 0.18, shape=MSO_SHAPE.DOWN_ARROW, fill=RGBColor(0xC9, 0xD6, 0xE3))
        y += 0.97

    add_rect(slide, 8.55, 1.55, 3.95, 4.85, fill=NAVY, line=None, radius=0.05)
    add_text(slide, 8.85, 1.85, 3.3, 0.3, "Принципы", size=16, color=WHITE, bold=True)

    principles = [
        "Один сценарий — отдельный router",
        "FSM хранит черновик заявки",
        "SQL — только в репозитории",
        "Токен и ADMIN_IDS — в .env",
        "Ввод пользователя экранируется",
    ]
    y = 2.38
    for item in principles:
        add_text(slide, 8.85, y, 0.18, 0.26, "•", size=11, color=BLUE, bold=True)
        add_text(slide, 9.1, y, 3.1, 0.5, item, size=10.5, color=RGBColor(0xC9, 0xD6, 0xE4), line_spacing=1.05)
        y += 0.56

    add_chip(slide, 8.85, 5.62, 1.15, 0.34, "aiogram", fill=RGBColor(0x17, 0x32, 0x4D), color=BLUE, size=8.5)
    add_chip(slide, 10.1, 5.62, 0.95, 0.34, "SQLite", fill=RGBColor(0x17, 0x32, 0x4D), color=BLUE, size=8.5)
    add_chip(slide, 11.15, 5.62, 1.05, 0.34, ".env", fill=RGBColor(0x17, 0x32, 0x4D), color=BLUE, size=8.5)

    add_text(
        slide,
        MARGIN,
        6.55,
        CONTENT_W,
        0.35,
        "Новый тип обращения добавляется записью в TYPES и кнопкой — без изменения схемы базы.",
        size=9.5,
        color=GRAY,
        italic=True,
    )


def slide_flow(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "06 · СЦЕНАРИЙ", "Путь пользователя", 7)

    steps = [
        ("/start", "Приветствие и меню из четырёх кнопок."),
        ("Тип обращения", "Запись на занятие, вопрос по курсу или прочее."),
        ("Имя и контакт", "Телефон, e-mail или @username. Проверка формата."),
        ("Текст", "Описание запроса от 5 до 1000 символов."),
        ("Подтверждение", "Заявка сохраняется в SQLite и получает номер."),
    ]
    w = 2.15
    gap = 0.28
    x = 0.73
    for index, (title, body) in enumerate(steps, start=1):
        add_rect(slide, x, 1.7, w, 2.55, fill=WHITE, line=BORDER, radius=0.06)
        add_circle(slide, x + 0.2, 1.9, 0.42, fill=BLUE_LIGHT, line=None)
        add_text(
            slide,
            x + 0.2,
            1.91,
            0.42,
            0.4,
            f"{index}",
            size=10.5,
            color=BLUE_DARK,
            bold=True,
            align=PP_ALIGN.CENTER,
            anchor=MSO_ANCHOR.MIDDLE,
        )
        add_text(slide, x + 0.2, 2.52, w - 0.4, 0.3, title, size=13, color=NAVY, bold=True)
        add_text(slide, x + 0.2, 2.95, w - 0.4, 1.05, body, size=9.5, color=GRAY, line_spacing=1.12)
        if index < len(steps):
            add_arrow(slide, x + w + 0.055, 2.8, 0.17, 0.18, fill=RGBColor(0xBE, 0xCF, 0xE0))
        x += w + gap

    add_rect(slide, MARGIN, 4.65, 5.75, 1.5, fill=WHITE, line=BORDER, radius=0.06)
    add_text(slide, 1.05, 4.85, 5.2, 0.28, "Проверка ввода", size=12.5, color=NAVY, bold=True)
    add_text(
        slide,
        1.05,
        5.18,
        5.25,
        0.8,
        "Имя — от 2 символов; контакт — телефон, e-mail или @username; "
        "текст — 5–1000 символов. При ошибке заявка не сохраняется.",
        size=9.5,
        color=GRAY,
        line_spacing=1.12,
    )

    add_rect(slide, 6.73, 4.65, 5.8, 1.5, fill=WHITE, line=BORDER, radius=0.06)
    add_text(slide, 6.98, 4.85, 5.2, 0.28, "Администратор", size=12.5, color=NAVY, bold=True)
    add_text(
        slide,
        6.98,
        5.18,
        5.25,
        0.8,
        "Новая заявка сразу приходит в личные сообщения. "
        "Команды: /stats, /applications, /export.",
        size=9.5,
        color=GRAY,
        line_spacing=1.12,
    )

    add_chip(slide, 5.05, 6.5, 3.2, 0.36, "/cancel — отмена на любом шаге", fill=BLUE_LIGHT, color=BLUE_DARK, size=9)


def slide_ui(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "07 · ИНТЕРФЕЙС", "Как это выглядит", 8)

    phone_h = 5.25
    phone_w = phone_h * 720 / 1560
    xs = [0.8, 3.38, 5.96]
    shots = [
        ("start.png", "Старт и меню"),
        ("form.png", "Заполнение заявки"),
        ("success.png", "Подтверждение"),
    ]
    for x, (name, caption) in zip(xs, shots):
        add_picture(slide, name, x, 1.42, phone_h)
        add_text(
            slide,
            x - 0.15,
            6.74,
            phone_w + 0.3,
            0.24,
            caption,
            size=9,
            color=GRAY,
            align=PP_ALIGN.CENTER,
        )

    add_rect(slide, 8.72, 1.55, 3.8, 5.25, fill=WHITE, line=BORDER, radius=0.05)
    add_text(slide, 9.0, 1.8, 3.25, 0.3, "Детали интерфейса", size=15, color=NAVY, bold=True)

    bullets = [
        ("Инлайн-кнопки", "Пользователю не нужно помнить команды."),
        ("Подсказки", "На каждом шаге — понятный текст и кнопка отмены."),
        ("Валидация", "Ошибка ввода не создаёт заявку."),
        ("Подтверждение", "Номер заявки и дата видны сразу."),
    ]
    y = 2.28
    for title, body in bullets:
        add_circle(slide, 9.0, y + 0.06, 0.08, fill=BLUE, line=None)
        add_text(slide, 9.22, y, 2.95, 0.24, title, size=10.5, color=NAVY, bold=True)
        add_text(slide, 9.22, y + 0.24, 3.0, 0.55, body, size=9.5, color=GRAY, line_spacing=1.1)
        y += 0.84

    add_rect(slide, 9.0, 5.66, 3.2, 0.5, fill=BLUE_PALE, line=None, radius=0.08)
    add_rect(slide, 9.0, 5.66, 0.06, 0.5, fill=BLUE, line=None, radius=0)
    add_text(
        slide,
        9.16,
        5.7,
        2.92,
        0.42,
        "«Заявка №14 принята» — номер и дата приходят сразу.",
        size=8.5,
        color=TEXT_SOFT,
        italic=True,
        line_spacing=1.05,
    )

    add_chip(slide, 9.0, 6.3, 3.2, 0.36, "HTML-разметка и эмодзи", fill=BLUE_LIGHT, color=BLUE_DARK, size=8.5)


def slide_db(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "08 · ДАННЫЕ", "Структура базы данных", 9)

    rows = [
        ("id", "INTEGER PK", "номер заявки"),
        ("created_at", "TEXT", "дата и время создания"),
        ("user_id", "INTEGER", "Telegram ID пользователя"),
        ("username", "TEXT", "@username"),
        ("full_name", "TEXT", "имя пользователя"),
        ("contact", "TEXT", "телефон или e-mail"),
        ("type", "TEXT", "тип обращения"),
        ("message", "TEXT", "текст обращения"),
        ("status", "TEXT", "статус заявки"),
    ]
    table = add_table_style(slide, len(rows) + 1, 3, MARGIN, 1.55, 7.35, 4.55)
    table.columns[0].width = Inches(1.55)
    table.columns[1].width = Inches(1.55)
    table.columns[2].width = Inches(4.25)
    table.rows[0].height = Inches(0.43)
    for index in range(1, len(rows) + 1):
        table.rows[index].height = Inches(0.45)

    for col, text in enumerate(("Поле", "Тип", "Назначение")):
        style_cell(table.cell(0, col), text, size=9.5, color=WHITE, bold=True, fill=NAVY)
    for r, (field, kind, purpose) in enumerate(rows, start=1):
        fill = WHITE if r % 2 else RGBColor(0xF4, 0xF7, 0xFB)
        style_cell(table.cell(r, 0), field, size=9, color=NAVY, bold=True, font=FONT_MONO, fill=fill)
        style_cell(table.cell(r, 1), kind, size=8.5, color=BLUE_DARK, font=FONT_MONO, fill=fill)
        style_cell(table.cell(r, 2), purpose, size=9, color=GRAY, fill=fill)

    add_rect(slide, 8.5, 1.55, 4.0, 3.35, fill=NAVY, line=None, radius=0.05)
    add_text(slide, 8.75, 1.72, 3.4, 0.22, "schema.sql", size=8, color=RGBColor(0x7F, 0x95, 0xB0), bold=True, spacing=1.0)
    code = (
        "CREATE TABLE applications (\n"
        "  id         INTEGER PRIMARY KEY,\n"
        "  created_at TEXT NOT NULL,\n"
        "  user_id    INTEGER NOT NULL,\n"
        "  username   TEXT,\n"
        "  full_name  TEXT NOT NULL,\n"
        "  contact    TEXT NOT NULL,\n"
        "  type       TEXT NOT NULL,\n"
        "  message    TEXT NOT NULL,\n"
        "  status     TEXT NOT NULL DEFAULT 'new'\n"
        ");\n"
        "\n"
        "CREATE INDEX idx_applications_created_at\n"
        "  ON applications (created_at DESC);\n"
        "\n"
        "CREATE INDEX idx_applications_user_id\n"
        "  ON applications (user_id);"
    )
    add_text(
        slide,
        8.75,
        2.02,
        3.55,
        2.7,
        code,
        size=7.6,
        color=RGBColor(0xC9, 0xD6, 0xE4),
        font=FONT_MONO,
        line_spacing=1.08,
    )

    chips = [("9 полей", 8.5), ("2 индекса", 9.78), ("1 таблица", 11.16)]
    for text, x in chips:
        add_chip(slide, x, 5.12, 1.18, 0.36, text, fill=BLUE_LIGHT, color=BLUE_DARK, size=8.5)

    add_rect(slide, 8.5, 5.72, 4.0, 1.15, fill=WHITE, line=BORDER, radius=0.06)
    add_text(slide, 8.72, 5.88, 1.7, 0.2, "В демо-базе", size=8, color=GRAY, bold=True)
    add_text(slide, 8.72, 6.1, 3.6, 0.35, "14 заявок · 3 типа обращений", size=12.5, color=NAVY, bold=True)

    add_text(
        slide,
        MARGIN,
        6.35,
        CONTENT_W,
        0.35,
        "Индексы по created_at и user_id ускоряют статистику и выборку заявок пользователя.",
        size=9,
        color=GRAY,
    )


def slide_admin(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "09 · АДМИНИСТРИРОВАНИЕ", "Инструменты администратора", 10)

    add_picture(slide, "admin.png", 0.8, 1.42, 5.25)
    add_text(slide, 0.65, 6.74, 2.75, 0.24, "Статистика и последние заявки", size=9, color=GRAY, align=PP_ALIGN.CENTER)

    features = [
        ("/stats", "Всего, новых, за 7 дней и разбивка по типам обращений."),
        ("/applications [N]", "Последние N заявок: дата, тип, имя, контакт и текст."),
        ("/export", "CSV с BOM: открывается в Excel без настройки кодировки."),
        ("уведомления", "Новая заявка сразу приходит администратору в Telegram."),
    ]
    y = 1.55
    for command, body in features:
        add_rect(slide, 3.55, y, 8.95, 0.9, fill=WHITE, line=BORDER, radius=0.07)
        add_text(slide, 3.8, y + 0.15, 2.0, 0.28, command, size=11, color=BLUE_DARK, bold=True, font=FONT_MONO)
        add_text(slide, 3.8, y + 0.47, 8.4, 0.3, body, size=9.5, color=GRAY)
        y += 0.99

    add_rect(slide, 3.55, 5.7, 8.95, 1.12, fill=NAVY, line=None, radius=0.05)
    add_text(slide, 3.82, 5.88, 1.6, 0.22, "ADMIN_IDS", size=8.5, color=BLUE, bold=True, spacing=1.2)
    add_text(
        slide,
        3.82,
        6.12,
        8.35,
        0.55,
        "Доступ к командам проверяется по Telegram ID. Остальные пользователи получают вежливый отказ.",
        size=10.5,
        color=RGBColor(0xC9, 0xD6, 0xE4),
        line_spacing=1.1,
    )


def slide_tests(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "10 · КАЧЕСТВО", "Тестирование", 11)

    add_rect(slide, MARGIN, 1.55, 4.0, 3.2, fill=NAVY, line=None, radius=0.05)
    add_text(slide, 1.15, 1.72, 2.5, 1.05, "40", size=58, color=WHITE, bold=True)
    add_text(slide, 1.15, 2.78, 3.2, 0.3, "тестов проходят", size=13, color=RGBColor(0xA9, 0xBC, 0xD3))
    add_text(slide, 1.15, 3.35, 3.4, 0.22, "$ pytest -q", size=8.5, color=RGBColor(0x7F, 0x95, 0xB0), font=FONT_MONO)
    add_text(slide, 1.15, 3.6, 3.4, 0.24, "40 passed in 0.22s", size=9.5, color=RGBColor(0x6E, 0xE7, 0xB7), font=FONT_MONO)

    stats = [
        ("Валидация", "24 теста"),
        ("База данных", "4 теста"),
        ("Тексты и HTML", "9 тестов"),
        ("CSV-экспорт", "3 теста"),
    ]
    positions = [(5.1, 1.55), (8.8, 1.55), (5.1, 3.05), (8.8, 3.05)]
    for (title, count), (x, y) in zip(stats, positions):
        add_rect(slide, x, y, 3.55, 1.35, fill=WHITE, line=BORDER, radius=0.07)
        add_text(slide, x + 0.22, y + 0.2, 3.1, 0.24, title, size=9.5, color=GRAY, bold=True)
        add_text(slide, x + 0.22, y + 0.52, 3.1, 0.5, count, size=21, color=NAVY, bold=True)

    add_rect(slide, MARGIN, 5.0, CONTENT_W, 1.55, fill=WHITE, line=BORDER, radius=0.06)
    add_text(slide, 1.05, 5.18, 4.0, 0.26, "Что проверяется", size=12.5, color=NAVY, bold=True)
    checks_left = [
        "имя, контакт и границы текста",
        "сохранение и переживание перезапуска",
        "статистика по типам и за 7 дней",
    ]
    checks_right = [
        "экранирование HTML в сообщениях",
        "CSV с BOM и корректными полями",
        "сборка роутеров и зависимости",
    ]
    for column, checks in ((1.05, checks_left), (6.75, checks_right)):
        y = 5.52
        for check in checks:
            add_text(slide, column, y, 0.16, 0.22, "✓", size=9.5, color=GREEN_DARK, bold=True)
            add_text(slide, column + 0.2, y, 4.8, 0.22, check, size=9, color=GRAY)
            y += 0.31

    add_text(
        slide,
        MARGIN,
        6.68,
        CONTENT_W,
        0.25,
        "Тестовая база создаётся во временной папке и не затрагивает рабочую.",
        size=8.5,
        color=GRAY_LIGHT,
    )


def slide_results(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_header(slide, "11 · ИТОГИ", "Результаты практики", 12)

    results = [
        ("🤖", "Работающий бот", "Три типа обращений, пошаговый диалог, уведомления администратору."),
        ("🗄️", "База данных", "SQLite, 9 полей, демо-данные и выгрузка заявок в CSV."),
        ("📚", "Документация", "README, техническое описание, паспорт проекта и презентация."),
    ]
    xs = [MARGIN, 4.79, 8.78]
    for (emoji, title, body), x in zip(results, xs):
        add_rect(slide, x, 1.55, 3.75, 2.1, fill=WHITE, line=BORDER, radius=0.06)
        add_icon(slide, x + 0.24, 1.78, 0.5, emoji)
        add_text(slide, x + 0.24, 2.4, 3.25, 0.3, title, size=13.5, color=NAVY, bold=True)
        add_text(slide, x + 0.24, 2.78, 3.25, 0.7, body, size=9.5, color=GRAY, line_spacing=1.12)

    add_rect(slide, MARGIN, 3.9, 6.35, 2.85, fill=WHITE, line=BORDER, radius=0.06)
    add_text(slide, 1.05, 4.1, 5.6, 0.3, "Навыки", size=13.5, color=NAVY, bold=True)
    skills = [
        ("сценарии", "проектирование"),
        ("aiogram 3", "FSM и роутеры"),
        ("SQLite", "схема и запросы"),
        ("pytest", "автотесты"),
        ("Git", "версии и GitHub"),
        ("docs", "техдокументация"),
    ]
    for index, (name, role) in enumerate(skills):
        x = 1.05 + (index % 2) * 3.0
        y = 4.55 + (index // 2) * 0.66
        add_chip(slide, x, y, 2.8, 0.5, f"{name} · {role}", fill=BLUE_PALE, color=TEXT_SOFT, size=8.5, bold=False, line=BORDER)

    add_rect(slide, 7.4, 3.9, 5.13, 2.85, fill=NAVY, line=None, radius=0.05)
    add_text(slide, 7.68, 4.1, 4.5, 0.3, "Куда развивать", size=13.5, color=WHITE, bold=True)
    future = [
        "Веб-панель администратора",
        "PostgreSQL вместо SQLite",
        "Интеграция с CRM",
        "Напоминания о занятиях",
    ]
    y = 4.62
    for item in future:
        add_text(slide, 7.68, y, 0.2, 0.24, "→", size=10, color=BLUE, bold=True)
        add_text(slide, 7.95, y, 4.2, 0.3, item, size=10.5, color=RGBColor(0xC9, 0xD6, 0xE4))
        y += 0.45

    add_text(
        slide,
        7.68,
        6.28,
        4.5,
        0.3,
        "Для запуска достаточно указать токен в .env",
        size=8.5,
        color=RGBColor(0x7F, 0x95, 0xB0),
        italic=True,
    )


def slide_thanks(prs: Presentation) -> None:
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    set_bg(slide, NAVY)

    add_circle(slide, -1.1, -1.4, 3.6, fill=None, line=NAVY_LINE, line_width=1.2)
    add_circle(slide, 11.2, 4.9, 3.4, fill=None, line=RGBColor(0x17, 0x2C, 0x44), line_width=1.2)
    add_circle(slide, 1.35, 6.2, 0.1, fill=TEAL, line=None)
    add_circle(slide, 11.9, 1.3, 0.08, fill=BLUE, line=None)

    add_text(
        slide,
        0.8,
        2.15,
        11.7,
        0.85,
        "Спасибо за внимание!",
        size=40,
        color=WHITE,
        bold=True,
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        0.8,
        3.12,
        11.7,
        0.4,
        "Готов ответить на вопросы",
        size=16,
        color=RGBColor(0xA9, 0xBC, 0xD3),
        align=PP_ALIGN.CENTER,
    )

    add_rect(slide, 5.9, 4.0, 1.5, 0.014, fill=NAVY_LINE, line=None, radius=0)
    add_chip(
        slide,
        4.17,
        4.35,
        5.0,
        0.48,
        "github.com/Duke13337/classonline-bot",
        fill=RGBColor(0x13, 0x2B, 0x45),
        color=RGBColor(0x6F, 0xC8, 0xF0),
        size=11,
        line=RGBColor(0x20, 0x3E, 0x5B),
    )
    add_text(
        slide,
        0.8,
        5.18,
        11.7,
        0.3,
        "Python · aiogram 3 · SQLite · pytest",
        size=10,
        color=RGBColor(0x7F, 0x95, 0xB0),
        align=PP_ALIGN.CENTER,
    )
    add_text(
        slide,
        0.8,
        6.6,
        11.7,
        0.3,
        "Telegram-бот «КлассОнлайн» · производственная практика · 2026",
        size=8.5,
        color=RGBColor(0x5E, 0x73, 0x8C),
        align=PP_ALIGN.CENTER,
    )


def main() -> None:
    prs = Presentation()
    prs.slide_width = Inches(W)
    prs.slide_height = Inches(H)

    slide_title(prs)
    slide_goal(prs)
    slide_org(prs)
    slide_done(prs)
    slide_stack(prs)
    slide_arch(prs)
    slide_flow(prs)
    slide_ui(prs)
    slide_db(prs)
    slide_admin(prs)
    slide_tests(prs)
    slide_results(prs)
    slide_thanks(prs)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    prs.save(OUT)
    print(f"Презентация сохранена: {OUT}")
    print(f"Слайдов: {len(prs.slides)}")


if __name__ == "__main__":
    main()
