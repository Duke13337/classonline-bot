"""Сборка паспорта проекта в DOCX.

Запуск:  .venv\\Scripts\\python.exe tools\\build_passport.py
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "Паспорт_проекта.docx"

NAVY = RGBColor(0x0B, 0x16, 0x26)
BLUE = RGBColor(0x22, 0x9E, 0xD9)
BLUE_DARK = RGBColor(0x18, 0x7C, 0xAE)
TEXT = RGBColor(0x10, 0x18, 0x28)
GRAY = RGBColor(0x64, 0x74, 0x8B)
GRAY_LIGHT = RGBColor(0x9A, 0xA8, 0xB8)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

FONT = "Segoe UI"
MONO = "Consolas"

FIELDS = [
    ("Название организации", "КлассОнлайн"),
    (
        "Задача проекта",
        "Разработать Telegram-бота для приёма заявок на занятия, вопросов по курсам "
        "и прочих обращений с сохранением в SQLite, уведомлениями администратору "
        "и командами статистики.",
    ),
    ("Количество участников", "1"),
    ("Участники (ФИО)", "Зеленов Данил Сергеевич"),
    ("Группа(ы)", "11/3-РПО-24/1"),
    ("Куратор", "Максим Николаевич"),
    (
        "Технологический стек",
        "Python 3.12, aiogram 3.31, SQLite (aiosqlite), python-dotenv, pytest, "
        "Git и GitHub",
    ),
    ("Место практики", "IT TOP college"),
    ("Период", "ноябрь 2026"),
    ("Репозиторий", "github.com/Duke13337/classonline-bot"),
]


def set_font(run, *, name: str = FONT, size: float = 10.5, bold: bool = False,
             color: RGBColor = TEXT, italic: bool = False) -> None:
    run.font.name = name
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), name)


def add_run(paragraph, text: str, **kwargs):
    run = paragraph.add_run(text)
    set_font(run, **kwargs)
    return run


def spacing(paragraph, *, before: float = 0, after: float = 0, line: float = 1.0) -> None:
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = line


def bottom_border(paragraph, *, color: str = "E2E8F0", size: int = 6) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), str(size))
    bottom.set(qn("w:space"), "6")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    ppr.insert_element_before(
        borders,
        "w:shd",
        "w:tabs",
        "w:suppressAutoHyphens",
        "w:kinsoku",
        "w:wordWrap",
        "w:overflowPunct",
        "w:topLinePunct",
        "w:autoSpaceDE",
        "w:autoSpaceDN",
        "w:bidi",
        "w:adjustRightInd",
        "w:snapToGrid",
        "w:spacing",
        "w:ind",
        "w:contextualSpacing",
        "w:mirrorIndents",
        "w:suppressOverlap",
        "w:jc",
        "w:textDirection",
        "w:textAlignment",
        "w:textboxTightWrap",
        "w:outlineLvl",
        "w:divId",
        "w:cnfStyle",
        "w:rPr",
        "w:sectPr",
        "w:pPrChange",
    )


def shade_cell(cell, color: str) -> None:
    tcpr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcpr.append(shd)


def cell_margins(cell, *, top: float = 0.10, bottom: float = 0.10,
                 left: float = 0.16, right: float = 0.16) -> None:
    tcpr = cell._tc.get_or_add_tcPr()
    mar = OxmlElement("w:tcMar")
    for tag, value in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{tag}")
        node.set(qn("w:w"), str(int(value * 567)))
        node.set(qn("w:type"), "dxa")
        mar.append(node)
    tcpr.append(mar)


def table_borders(table, *, color: str = "E2E8F0", size: int = 4) -> None:
    tbl_pr = table._tbl.tblPr
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        node = OxmlElement(f"w:{edge}")
        if edge in ("left", "right", "insideV"):
            node.set(qn("w:val"), "nil")
        else:
            node.set(qn("w:val"), "single")
            node.set(qn("w:sz"), str(size))
            node.set(qn("w:space"), "0")
            node.set(qn("w:color"), color)
        borders.append(node)
    tbl_pr.insert_element_before(
        borders,
        "w:shd",
        "w:tblLayout",
        "w:tblCellMar",
        "w:tblLook",
        "w:tblCaption",
        "w:tblDescription",
    )


def set_column_widths(table, widths: list[float]) -> None:
    table.autofit = False
    for row in table.rows:
        for index, width in enumerate(widths):
            row.cells[index].width = Cm(width)
    for index, width in enumerate(widths):
        table.columns[index].width = Cm(width)


def section_title(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    spacing(paragraph, before=10, after=4)
    add_run(paragraph, text, size=12, bold=True, color=NAVY)
    bottom_border(paragraph, color="DDEDF8", size=8)


def bullet(doc: Document, text: str) -> None:
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Cm(0.55)
    paragraph.paragraph_format.first_line_indent = Cm(-0.35)
    spacing(paragraph, before=0, after=2, line=1.05)
    add_run(paragraph, "•  ", size=9.5, bold=True, color=BLUE)
    add_run(paragraph, text, size=9.5, color=TEXT)


def build() -> None:
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = TEXT
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.insert(0, rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set(qn(attr), FONT)

    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(1.9)
    section.right_margin = Cm(1.9)
    section.top_margin = Cm(1.3)
    section.bottom_margin = Cm(1.2)
    section.header_distance = Cm(0.8)
    section.footer_distance = Cm(0.7)

    # Шапка
    kicker = doc.add_paragraph()
    spacing(kicker, before=0, after=4)
    add_run(kicker, "IT TOP COLLEGE  ·  ПРОИЗВОДСТВЕННАЯ ПРАКТИКА", size=8.5,
            bold=True, color=BLUE_DARK)

    title = doc.add_paragraph()
    spacing(title, before=2, after=2, line=0.95)
    add_run(title, "Telegram-бот «КлассОнлайн»", size=24, bold=True, color=NAVY)

    subtitle = doc.add_paragraph()
    spacing(subtitle, before=0, after=8)
    add_run(subtitle, "Паспорт проекта · приём заявок на занятия и обращений учеников",
            size=11, color=GRAY)
    bottom_border(subtitle, color="229ED9", size=12)

    # Таблица полей
    table = doc.add_table(rows=1, cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_borders(table)
    header = table.rows[0]
    for index, text in enumerate(("Параметр", "Значение")):
        cell = header.cells[index]
        shade_cell(cell, "0B1626")
        cell_margins(cell, top=0.16, bottom=0.16)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        paragraph = cell.paragraphs[0]
        spacing(paragraph, before=0, after=0)
        add_run(paragraph, text, size=9, bold=True, color=WHITE)

    for index, (name, value) in enumerate(FIELDS, start=1):
        row = table.add_row()
        name_cell, value_cell = row.cells
        fill = "F4F7FB" if index % 2 else "FFFFFF"
        shade_cell(name_cell, fill)
        shade_cell(value_cell, fill)
        for cell in (name_cell, value_cell):
            cell_margins(cell)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        name_p = name_cell.paragraphs[0]
        spacing(name_p, before=0, after=0, line=1.0)
        add_run(name_p, name, size=9, bold=True, color=NAVY)
        value_p = value_cell.paragraphs[0]
        spacing(value_p, before=0, after=0, line=1.04)
        add_run(value_p, value, size=9.5, color=TEXT)

    set_column_widths(table, [5.3, 11.9])

    # Краткое описание
    section_title(doc, "Краткое описание")
    description = doc.add_paragraph()
    spacing(description, before=0, after=0, line=1.08)
    add_run(
        description,
        "Онлайн-школа «КлассОнлайн» принимает обращения учеников и родителей "
        "в личных сообщениях Telegram. Сообщения теряются в переписке, а "
        "администратор не видит общей статистики. Бот становится единой точкой "
        "входа: пользователь выбирает тип обращения, указывает имя и контакт, "
        "описывает запрос и подтверждает отправку. Заявка сохраняется в SQLite, "
        "получает номер, а администратор сразу получает уведомление.",
        size=9.5,
        color=TEXT,
    )

    # Показатели
    section_title(doc, "Ключевые показатели")
    metrics = [
        ("3", "типа обращений"),
        ("9", "полей в таблице"),
        ("40", "автотестов"),
        ("14", "заявок в демо-базе"),
    ]
    metric_table = doc.add_table(rows=2, cols=4)
    metric_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_borders(metric_table, color="FFFFFF", size=2)
    for column, (value, label) in enumerate(metrics):
        top = metric_table.cell(0, column)
        bottom = metric_table.cell(1, column)
        shade_cell(top, "F4F7FB")
        shade_cell(bottom, "F4F7FB")
        cell_margins(top, top=0.15, bottom=0.02, left=0.12, right=0.12)
        cell_margins(bottom, top=0.01, bottom=0.15, left=0.12, right=0.12)
        value_p = top.paragraphs[0]
        value_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        spacing(value_p, before=0, after=0)
        add_run(value_p, value, size=18, bold=True, color=NAVY)
        label_p = bottom.paragraphs[0]
        label_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        spacing(label_p, before=0, after=0)
        add_run(label_p, label, size=7.5, color=GRAY)

    # Результаты
    section_title(doc, "Результаты")
    for text in (
        "Реализован Telegram-бот с тремя типами обращений и пошаговым диалогом.",
        "Спроектирована база SQLite: 9 полей, 2 индекса, статусы заявок.",
        "Добавлены админ-команды /stats, /applications и /export, уведомления о заявках.",
        "Написаны 40 автотестов и подготовлена полная документация проекта.",
        "Проект опубликован на GitHub и готов к демонстрации.",
    ):
        bullet(doc, text)

    # Запуск
    section_title(doc, "Запуск")
    command_table = doc.add_table(rows=1, cols=1)
    command_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_borders(command_table, color="E2E8F0", size=4)
    cell = command_table.cell(0, 0)
    shade_cell(cell, "0B1626")
    cell_margins(cell, top=0.16, bottom=0.16, left=0.28, right=0.28)
    paragraph = cell.paragraphs[0]
    spacing(paragraph, before=0, after=0, line=1.08)
    commands = (
        "python -m venv .venv\n"
        ".venv\\Scripts\\activate\n"
        "pip install -r requirements.txt\n"
        "copy .env.example .env\n"
        "python -m bot"
    )
    add_run(paragraph, commands, size=8.5, name=MONO, color=RGBColor(0xC9, 0xD6, 0xE4))
    set_column_widths(command_table, [17.2])

    note = doc.add_paragraph()
    spacing(note, before=5, after=0)
    add_run(
        note,
        "Перед запуском укажите в .env токен от @BotFather и Telegram ID "
        "администраторов в ADMIN_IDS.",
        size=8,
        color=GRAY,
        italic=True,
    )

    # Футер
    footer_p = section.footer.paragraphs[0]
    footer_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    add_run(
        footer_p,
        "КлассОнлайн · паспорт проекта · Зеленов Данил Сергеевич · 2026",
        size=7.5,
        color=GRAY_LIGHT,
    )

    props = doc.core_properties
    props.title = "Паспорт проекта: Telegram-бот «КлассОнлайн»"
    props.author = "Зеленов Данил Сергеевич"
    props.subject = "Производственная практика, IT TOP college"
    props.keywords = "Telegram-бот, aiogram, SQLite, Python, КлассОнлайн"

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    print(f"Паспорт сохранён: {OUT}")


if __name__ == "__main__":
    build()
