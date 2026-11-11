# -*- coding: utf-8 -*-
"""TV-001 rev16: engineering-readiness supplement to the approved rev15 plan.

The first three sheets are deliberately drawn by the rev15 generator unchanged.
Sheets 4-5 add only verified rectangles and pre-order/rough-in gates; they do
not invent socket positions, mounting heights, ventilation routes or ratings.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_tv001_rev14_table_in_kitchen as rev15


ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "output" / "pdf" / "TV-001_rev16_инженерная_готовность.pdf"
PREVIEW_PREFIX = ROOT / "output" / "preview" / "TV-001_rev16"

INK = rev15.INK
MUTED = rev15.MUTED
GOOD = rev15.GOOD
BAD = rev15.BAD
ORANGE = rev15.ORANGE
BLUE = rev15.BLUE
PALE_BLUE = rev15.PALE_BLUE
PALE_GREEN = rev15.PALE_GREEN
PALE_ORANGE = rev15.PALE_ORANGE
PALE_RED = rev15.PALE_RED

# The confirmed 700-mm work belts are reused as 1:1 checking fields.  They are
# deliberately NOT described as door-swing envelopes: hinge side, handle
# projection and opening angle must come from the selected SKU.
TOP_FRONT_CHECK_ZONE = (0, 2200, 2400, 2900)
LEFT_FRONT_CHECK_ZONE = (600, 2200, 1300, 2900)


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def assert_in_room(name: str, rect: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    if not (0 <= x1 < x2 <= rev15.ROOM[2] and 0 <= y1 < y2 <= rev15.ROOM[3]):
        raise AssertionError(f"{name} outside B01: {rect}")


def validate_rev16() -> None:
    rev15.validate_geometry()
    assert rev15.TABLE == (670, 1400, 2070, 2200)
    assert rev15.KITCHEN_LEFT_SHORT == (0, 2200, 600, 2900)
    assert rev15.KITCHEN_LEFT_FRIDGE == (0, 2300, 600, 2900)
    assert rev15.KITCHEN_LEFT_FILLER == (0, 2200, 600, 2300)
    assert rev15.KITCHEN_LEFT_FRIDGE[3] - rev15.KITCHEN_LEFT_FRIDGE[1] == 600
    assert rev15.KITCHEN_LEFT_FILLER[3] - rev15.KITCHEN_LEFT_FILLER[1] == 100
    assert rev15.TABLE[0] - rev15.KITCHEN_LEFT_SHORT[2] == 70
    assert rev15.KITCHEN_TOP[1] - rev15.TABLE[3] == 700
    for name, rect in {
        "top_front_check_zone": TOP_FRONT_CHECK_ZONE,
        "left_front_check_zone": LEFT_FRONT_CHECK_ZONE,
    }.items():
        assert_in_room(name, rect)
    assert not overlap(rev15.TABLE, TOP_FRONT_CHECK_ZONE)
    assert not overlap(rev15.TABLE, LEFT_FRONT_CHECK_ZONE)
    assert LEFT_FRONT_CHECK_ZONE[1] - rev15.TABLE[3] == 0
    assert rev15.SOFA == (2430, 2500, 4430, 3500)
    assert rev15.DESK == (4510, 2900, 5710, 3500)
    assert rev15.TV == (2610, 0, 4210, 300)
    print("PASS rev16 assertions: approved table/short branch/sofa-TV-desk retained; conditional SKU envelopes labelled separately")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    rev15.text(c, font, x, y, size, value, color, center=center, right=right)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=None, bullet=None):
    return rev15.wrapped(c, font, x, y, size, value, width, color, leading, bullet)


def page_frame(c, regular, bold, title, subtitle, page_no, scale="М 1:25"):
    width, height = landscape(A3)
    c.setFillColor(white); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 12.4, title)
    text(c, regular, 14, 274, 4.8, subtitle, MUTED)
    text(c, regular, 404, 14, 3.8, f"TV-001 rev16 | лист {page_no}/5 | {scale}", MUTED, right=True)


def panel(c, regular, bold, x, y, w, h, title, fill):
    rev15.panel(c, regular, bold, x, y, w, h, title, fill)


def draw_operational_contours(c, regular, bold):
    page_frame(
        c, regular, bold,
        "TV-001 rev16 - ЭКСПЛУАТАЦИОННЫЕ КОНТУРЫ",
        "Подтверждённая геометрия + рабочие пояса для проверки 1:1. Это не траектории дверей.",
        4,
    )
    # Existing rev15 model geometry, with its approved 700-mm branch and table.
    rev15.draw_common(c, regular, bold, short_left=True, show_seated=False)

    # Conditional, intentionally noncommittal opening zones. No sockets, heights
    # or ventilation are drawn because they are not confirmed in the source plan.
    rev15.route_rect(
        c, regular, TOP_FRONT_CHECK_ZONE,
        "ПОСЛЕ SKU: проверить фасады / ПММ / духовку 1:1", (1440, 2520),
        ORANGE, 0.36, PALE_ORANGE,
    )
    rev15.route_rect(
        c, regular, LEFT_FRONT_CHECK_ZONE,
        "ПОСЛЕ SKU: проверить дверь холодильника 1:1", (955, 2080),
        BAD, 0.36, PALE_RED,
    )

    panel(c, regular, bold, 255, 198, 151, 70, "ПОДТВЕРЖДЕНО ПЛАНОМ", PALE_GREEN)
    y = 250
    for line in (
        "- B01 5710x3500; D2 guard и маршруты",
        "- стол 1400x800: x670...2070, y1400...2200",
        "- левая ветвь 700: холод. 600 + добор 100",
        "- диван, ТВ, РМ, O1 без сдвига",
        "- 70/700/150 - плановые расстояния",
    ):
        text(c, regular, 259, y, 5.0, line); y -= 6.2

    panel(c, regular, bold, 255, 118, 151, 72, "ЗОНЫ ПРОВЕРКИ «ПОСЛЕ SKU»", PALE_ORANGE)
    y = 171
    for paragraph in (
        "Оранжевый и красный - это существующие 700-мм рабочие пояса, в которых нужно провести макетирование 1:1.",
        "Они не задают ход двери. Петли, угол, ручку, свес и реальную глубину проверяют по паспорту и макету SKU.",
    ):
        y = wrapped(c, regular, 259, y, 4.8, paragraph, 54, INK, 5.4, "-") - 1.3

    panel(c, regular, bold, 255, 65, 151, 45, "ЧЕГО НА ЛИСТЕ НЕТ", PALE_RED)
    y = 97
    for line in (
        "Нет розеток, высот, вентиляции,",
        "трасс, автоматов и сечений: данные",
        "не подтверждены - не придумываем.",
    ):
        text(c, regular, 259, y, 4.9, line, BAD); y -= 5.8
    c.showPage()


def checklist_row(c, regular, bold, x, y, tag, title, body, fill):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor("#bdc7ce")); c.setLineWidth(0.18 * mm)
    c.roundRect(x * mm, y * mm, 188 * mm, 34 * mm, 1.8 * mm, fill=1, stroke=1)
    c.setFillColor(white); c.rect((x + 4) * mm, (y + 24) * mm, 4.5 * mm, 4.5 * mm, fill=1, stroke=1)
    text(c, bold, x + 11, y + 24.5, 5.7, tag, BLUE)
    text(c, bold, x + 31, y + 24.5, 6.2, title)
    wrapped(c, regular, x + 11, y + 17.0, 5.0, body, 112, INK, 5.0)


def draw_preorder_checklist(c, regular, bold):
    page_frame(
        c, regular, bold,
        "TV-001 rev16 - ПЕРЕД ЗАКАЗОМ / ШТРОБЛЕНИЕМ",
        "P0 закрыть до штробления и заказа кухни; P1 - до оплаты изделий и финального шаблона.",
        5,
        "CHECKLIST",
    )
    panel(c, regular, bold, 15, 246, 390, 17, "СТОП-УСЛОВИЕ", PALE_RED)
    text(c, regular, 20, 251, 5.8, "B01 5710x3500 и O1 1600 - планировочная база, не размеры заказа. Лист не является монтажной схемой.", BAD)

    left = (
        ("P0-01", "Контур B01 / правая стена", "Все 4 стены у пола, на H=900 и H=1500; обе диагонали. Правую стену проверить 2-м правилом и по вертикали."),
        ("P0-02", "D2 / O1 / терраса", "Чистые WхH, оси от двух углов, створки, ручки, порог/перепад и фактический ход. Фото с рулеткой."),
        ("P0-03", "Вода / слив / вентканал", "Каждая точка: две привязки + H от чистого пола; диаметры, уклон слива, сечение/трасса вентканала и ревизия."),
        ("P0-04", "E-01 / потолок", "Каждая электроточка: x/y/h от базовых углов. Высота потолка над кухней, диваном, РМ и граница локальных 2530 мм."),
        ("P0-05", "Неучтённое / фото", "Радиатор, короба, стояки, люки и датчики: WхHхD, две оси и H. Каждую точку снять с рулеткой и ID до закрытия."),
    )
    right = (
        ("P0-06", "Точные SKU техники", "Холодильник, ПММ, духовка/СВЧ, варка, вытяжка и TV: паспорты, глубины, вентзазоры, петли/ручки и макет открывания 1:1."),
        ("P0-07", "Электропроект / группы", "До штробления разделить технику, фартук, РМ и TV. Номиналы, сечения, защиту и PE утверждает электрик после проверки щита и паспортов."),
        ("P0-08", "Свет L1 / L2 / L3 / L4", "До штробления: L1 общий; L2 непрерывная подсветка фартука; L3 РМ/видеосвязь; L4 мягкий TV/вечер. Каждая группа имеет ручное управление."),
        ("P1-01", "Стол / диван / стулья", "CJ196: LхWхH, масса, ножки/царги, замки и подпятники; стул до 400x400. Диван: внешний и разложенный контур, механизм без роликов."),
        ("P1-02", "Финальный допуск", "После чистовых стен/пола повторить обмер теми же базами. Затем снять шаблон столешницы, утвердить доборы и исполнительную ведомость."),
    )
    y = 207
    for tag, title, body in left:
        checklist_row(c, regular, bold, 15, y, tag, title, body, PALE_BLUE if tag.startswith("P0") else PALE_GREEN)
        y -= 40
    y = 207
    for tag, title, body in right:
        checklist_row(c, regular, bold, 215, y, tag, title, body, PALE_BLUE if tag.startswith("P0") else PALE_GREEN)
        y -= 40
    panel(c, regular, bold, 15, 18, 390, 17, "ПОРЯДОК", PALE_ORANGE)
    text(c, regular, 20, 23, 5.4, "Сначала все P0: обмер, SKU техники, электропроект и макет 1:1. Затем оплата мебели; после отделки - повторный обмер и шаблон.", ORANGE)
    c.showPage()


def pdftoppm_path() -> str | None:
    found = shutil.which("pdftoppm")
    if found:
        return found
    bundled = Path(r"C:\Users\aidzm\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")
    return str(bundled) if bundled.exists() else None


def render_previews() -> None:
    executable = pdftoppm_path()
    if not executable:
        raise RuntimeError("pdftoppm is required to produce the requested rev16 PNG previews")
    PREVIEW_PREFIX.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([executable, "-png", "-r", "150", str(OUT_PDF), str(PREVIEW_PREFIX)], check=True)
    previews = [PREVIEW_PREFIX.parent / f"TV-001_rev16-{number}.png" for number in range(1, 6)]
    if not all(path.exists() and path.stat().st_size > 0 for path in previews):
        raise AssertionError("rev16 preview rendering did not produce all five PNG files")
    print("PASS rev16 previews: TV-001_rev16-1.png ... -5.png")


def build() -> None:
    validate_rev16()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = rev15.base.fonts()
    c = canvas.Canvas(str(OUT_PDF), pagesize=landscape(A3))
    c.setTitle("TV-001 rev16 - инженерная готовность")
    c.setAuthor("Codex")
    # Required preservation of rev15 leaves 1-3.
    rev15.draw_requested(c, regular, bold)
    rev15.draw_recommended(c, regular, bold)
    rev15.draw_scenarios(c, regular, bold)
    draw_operational_contours(c, regular, bold)
    draw_preorder_checklist(c, regular, bold)
    c.save()
    if not OUT_PDF.exists() or OUT_PDF.stat().st_size == 0:
        raise AssertionError("rev16 PDF missing or empty")
    print(f"PASS rev16 PDF: {OUT_PDF}")
    render_previews()


if __name__ == "__main__":
    build()
