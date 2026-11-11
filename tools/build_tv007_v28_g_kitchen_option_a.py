# -*- coding: utf-8 -*-
"""TV-007: the G-kitchen from the user's v28 visual in option A.

This is a separate comparison sheet.  It keeps the selected rotated table
(800 x 1400) and adds the full 2400 + 1600 kitchen frontage from the v28
visual.  The 700-mm L-shaped kitchen working zone is intentionally for one
person, not a circulation route.  The sheet therefore preserves the explicit
warning that the old 900-mm D2->O1 band is not available in option A.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base
import build_tv006_rotated_table_option_a as option_a


ROOT = Path(__file__).resolve().parents[1]
SOURCE_IMAGE = ROOT / "кухня гостинная" / "кухня_визуализация_TV-001_v28_проход_рабочая_зона_кухни_700мм.png"
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-007_Г-кухня_v28_стол-90_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-007_Г-кухня_v28_стол-90_М1-25.pdf"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
WORK = base.WORK
GOOD = base.GOOD
BAD = base.BAD
ORANGE = "#ad6800"
BLUE = "#2f6e8d"
PALE_GREEN = "#eff8f1"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"

ROOM = (0, 0, 5710, 3500)
D2_GUARD = (0, 0, 1200, 1300)
ROUTE_900_REFERENCE = (0, 350, 5710, 1250)
O1_ROUTE = (4810, 350, 5710, 2450)
DESK_APPROACH = (4510, 1250, 5110, 2490)

# The kitchen read from visual v28: upper run 2400 and left return 1600.
KITCHEN_TOP = (0, 2900, 2400, 3500)
LEFT_BRANCH = (0, 1300, 600, 2900)
FRIDGE = (0, 1300, 600, 1900)
TALL_STORAGE = (0, 1900, 600, 2400)
DISHWASHER_BRANCH = (0, 2400, 600, 2900)
FRIDGE_DOOR = (600, 1300, 1300, 1900)

# Selected option A, now bounded on the left by the full kitchen return.
TABLE = (1300, 800, 2100, 2200)
# Seating is on the side opposite the kitchen so the G-working zone stays free.
CHAIR_RIGHT_1 = (2100, 850, 2500, 1250)
CHAIR_RIGHT_2 = (2100, 1300, 2500, 1700)
CHILD_CHAIR = (2100, 1750, 2500, 2150)

WORK_LEFT = (600, 1300, 1300, 2200)
WORK_TOP = (600, 2200, 2400, 2900)

SOFA = (2430, 2500, 4430, 3500)
DESK = (4510, 2900, 5710, 3500)
DESK_CHAIR = (4510, 2490, 5110, 3110)
TV_MEDIA = (2610, 0, 4210, 300)


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def assert_in_room(name: str, rect: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    if not (0 <= x1 < x2 <= ROOM[2] and 0 <= y1 < y2 <= ROOM[3]):
        raise AssertionError(f"{name} outside B01: {rect}")


def validate_geometry() -> None:
    if not SOURCE_IMAGE.exists():
        raise FileNotFoundError(f"Missing v28 source visual: {SOURCE_IMAGE}")
    fixed = {
        "kitchen_top": KITCHEN_TOP,
        "left_branch": LEFT_BRANCH,
        "fridge": FRIDGE,
        "tall_storage": TALL_STORAGE,
        "dishwasher_branch": DISHWASHER_BRANCH,
        "fridge_door": FRIDGE_DOOR,
        "table": TABLE,
        "chair_right_1": CHAIR_RIGHT_1,
        "chair_right_2": CHAIR_RIGHT_2,
        "child_chair": CHILD_CHAIR,
        "sofa": SOFA,
        "desk": DESK,
        "tv_media": TV_MEDIA,
    }
    for name, rect in fixed.items():
        assert_in_room(name, rect)

    for left, right in combinations(("kitchen_top", "left_branch", "table", "sofa", "desk", "tv_media"), 2):
        if overlap(fixed[left], fixed[right]):
            raise AssertionError(f"fixed overlap {left}/{right}")
    if overlap(D2_GUARD, LEFT_BRANCH):
        raise AssertionError("left kitchen branch enters D2 guard")
    if overlap(TABLE, FRIDGE_DOOR):
        raise AssertionError("table enters fridge door zone")
    if overlap(SOFA, DESK_CHAIR):
        raise AssertionError("desk chair overlaps sofa")

    assert KITCHEN_TOP[2] - KITCHEN_TOP[0] == 2400
    assert LEFT_BRANCH[3] - LEFT_BRANCH[1] == 1600
    assert (KITCHEN_TOP[2] - KITCHEN_TOP[0]) + (LEFT_BRANCH[3] - LEFT_BRANCH[1]) == 4000
    assert FRIDGE == (0, 1300, 600, 1900)
    assert TABLE[2] - TABLE[0] == 800
    assert TABLE[3] - TABLE[1] == 1400
    assert TABLE[0] - LEFT_BRANCH[2] == 700
    assert KITCHEN_TOP[1] - TABLE[3] == 700
    for chair in (CHAIR_RIGHT_1, CHAIR_RIGHT_2, CHILD_CHAIR):
        assert not overlap(chair, WORK_LEFT)
        assert not overlap(chair, WORK_TOP)
    assert overlap(TABLE, ROUTE_900_REFERENCE)
    overlap_height = min(TABLE[3], ROUTE_900_REFERENCE[3]) - max(TABLE[1], ROUTE_900_REFERENCE[1])
    assert overlap_height == 450
    print("PASS TV-007: v28 G-kitchen 2400+1600; 700-mm kitchen work zone; rotated option-A table; 900 route intentionally not claimed")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def panel(c, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7.5, 6.8, title)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=6.0, bullet=None):
    for index, row in enumerate(base.wrap(value, width)):
        prefix = (bullet + " ") if bullet and index == 0 else ("  " if bullet else "")
        text(c, font, x, y, size, prefix + row, color)
        y -= leading
    return y


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13.2, "TV-007 - Г-КУХНЯ ИЗ ВИЗУАЛИЗАЦИИ v28")
    text(c, regular, 14, 274, 4.9,
         "Вариант A сохранён: стол 90 град. и 700 мм до верхней кухни. Кухня перенесена по v28 как геометрия, не по перспективе.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-007 | лист 1/1 | М 1:25", MUTED, right=True)


def dashed_rect(c, rect, color, width=0.30):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width * mm); c.setDash(1.5 * mm, 0.85 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()


def kitchen_module(c, regular, x, y, width, height, label, fill=KITCHEN, size=3.6):
    base.model_box(c, x, y, width, height, fill, "#6e5a34", 0.20)
    base.label_model(c, regular, x + width / 2, y + height / 2 - 10, label, size, "#5b4827")


def draw_kitchen(c, regular, bold):
    for x, width, label in (
        (0, 600, "МОЙКА"),
        (600, 450, "ПММ 450"),
        (1050, 600, "ВАРКА/ДУХ."),
        (1650, 600, "СВЧ/ДУХ."),
        (2250, 150, "ДОБОР"),
    ):
        kitchen_module(c, regular, x, 2900, width, 600, label, size=3.5 if width >= 450 else 3.1)
    kitchen_module(c, regular, 0, 1300, 600, 600, "ХОЛОДИЛЬНИК", "#e7ca90", 4.1)
    kitchen_module(c, regular, 0, 1900, 600, 500, "ПЕНАЛ/ХРАН", "#ead5a8", 3.6)
    kitchen_module(c, regular, 0, 2400, 600, 500, "ПММ 450", KITCHEN, 3.8)
    base.label_model(c, bold, 1200, 3440, "Г-КУХНЯ: 4000 ФРОНТОВ (2400 + 1600)", 4.8, "#5b4827")


def draw_work_zone(c, regular):
    dashed_rect(c, WORK_LEFT, ORANGE, 0.32)
    dashed_rect(c, WORK_TOP, ORANGE, 0.32)
    dashed_rect(c, FRIDGE_DOOR, "#c17d20", 0.20)
    base.label_model(c, regular, 950, 2060, "700: Г-зона кухни", 3.8, ORANGE)
    base.label_model(c, regular, 1700, 2560, "700: один человек; не транзит", 3.8, ORANGE)
    base.label_model(c, regular, 950, 1600, "дверь хол. - SKU", 3.2, "#a66b16")


def draw_table(c, regular, bold):
    x1, y1, x2, y2 = TABLE
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 42)
    base.model_line(c, x1, y1 + 700, x2, y1 + 700, "#6b8665", 0.14)
    base.label_model(c, bold, 1700, 1570, "СТОЛ CJ196", 4.8, "#405d3c")
    base.label_model(c, regular, 1700, 1435, "800 x 1400; поворот 90 град.", 3.8, "#405d3c")
    for rect in (CHAIR_RIGHT_1, CHAIR_RIGHT_2, CHILD_CHAIR):
        x1, y1, x2, y2 = rect
        base.draw_chair(c, x1, y1, x2 - x1, y2 - y1, facing="left")
    base.label_model(c, regular, 2300, 2225, "3 места - не в кухне", 3.5, "#6d6258")


def draw_sofa(c, regular, bold):
    """Keep the TV-006 sofa, but keep its note clear of the 2000-mm dimension."""
    base.draw_sofa(c, regular, 2430, 2500, 2000, 1000, "down")
    base.label_model(c, bold, 3430, 2595, "ДИВАН-КРОВАТЬ 2000x1000", 4.6, "#544943")
    # The shared TV-006 note sits at y=2450, exactly on the sofa dimension.
    # Here it is deliberately moved into the 150-mm clear gap above the table.
    base.label_model(c, regular, 3430, 2350, "стол расположен слева, не перед диваном", 3.6, "#544943")


def draw_900_conflict(c, regular):
    dashed_rect(c, ROUTE_900_REFERENCE, BAD, 0.36)
    base.label_model(c, regular, 3520, 670, "D2 -> O1 900: ПЕРЕСЕЧЕНИЕ СО СТОЛОМ 450", 3.9, BAD)


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(600), base.qx(1300), base.qy(1960), "700", ORANGE)
    base.dim_h(c, regular, base.qx(1300), base.qx(2100), base.qy(760), "800", "#405d3c")
    base.dim_v(c, regular, base.qx(2140), base.qy(800), base.qy(2200), "1400", "#405d3c")
    base.dim_v(c, regular, base.qx(2180), base.qy(2200), base.qy(2900), "700", ORANGE)
    base.dim_v(c, regular, base.qx(630), base.qy(1300), base.qy(2900), "1600", "#5b4827")
    base.dim_v(c, regular, base.qx(665), base.qy(1300), base.qy(1900), "600", "#5b4827")
    base.dim_h(c, regular, base.qx(0), base.qx(2400), base.qy(2860), "2400")
    base.dim_h(c, regular, base.qx(2430), base.qx(4430), base.qy(2460), "2000")
    base.dim_h(c, regular, base.qx(4510), base.qx(5710), base.qy(2860), "1200")
    base.dim_h(c, regular, base.qx(2610), base.qx(4210), base.qy(340), "1600")
    base.dim_v(c, regular, base.qx(4240), base.qy(0), base.qy(300), "300")


def sidebar(c, regular, bold):
    x, w = 270, 136
    panel(c, bold, x, 210, w, 58, "ПЕРЕНЕСЕНО ИЗ v28", PALE_GREEN)
    yy = 254
    for line in (
        "- верхняя линия 2400 мм",
        "- левая ветвь 1600 мм",
        "- всего фронтов: 4000 мм",
        "- Г-зона работы: чистые 700 мм",
        "- холодильник на левой ветви",
    ):
        text(c, regular, x + 4, yy, 5.8, line); yy -= 5.7

    panel(c, bold, x, 136, w, 64, "КАК ИЗМЕНЁН TV-006", PALE_ORANGE)
    yy = 185
    for paragraph in (
        "Стол 800 x 1400 остаётся повернутым. Все три места перенесены на сторону, противоположную кухне.",
        "Так Г-зона кухни остаётся свободной для одного человека при закрытых фасадах.",
    ):
        yy = wrapped(c, regular, x + 4, yy, 5.8, paragraph, 43, INK, 6.2, "-") - 1.0

    panel(c, bold, x, 68, w, 56, "ГРАНИЦА ВАРИАНТА A", PALE_RED)
    yy = 108
    for line in (
        "- 700 у кухни сохранены",
        "- 900 D2 -> O1 не возвращены",
        "- стол пересекает старую полосу",
        "  на 450 мм; это показано красным",
    ):
        text(c, regular, x + 4, yy, 5.8, line, BAD); yy -= 5.7


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-007 / Г-КУХНЯ v28")
    option_a.previous.draw_d2_guard(c, regular)
    dashed_rect(c, O1_ROUTE, GOOD, 0.30)
    base.label_model(c, regular, 5255, 2380, "900 к O1 вне зоны стола", 3.6, GOOD)
    dashed_rect(c, DESK_APPROACH, BLUE, 0.30)
    base.label_model(c, regular, 4810, 2400, "подход к креслу 600", 3.6, BLUE)
    draw_kitchen(c, regular, bold)
    draw_work_zone(c, regular)
    draw_900_conflict(c, regular)
    draw_table(c, regular, bold)
    draw_sofa(c, regular, bold)
    option_a.previous.draw_desk(c, regular)
    option_a.previous.draw_tv(c, regular, bold)
    dimensions(c, regular)
    sidebar(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-007 - Г-кухня из визуализации v28")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-007 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
