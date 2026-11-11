# -*- coding: utf-8 -*-
"""TV-006: selected option A for B01.

The CJ196 is turned through 90 degrees and the fridge returns to the short
left-hand return.  This sheet deliberately preserves the requested 700 mm
from the upper kitchen front to the table.  Consequently it does *not* claim
the former 900-mm D2->O1 route: the table intersects that band by 450 mm.
All coordinates are model millimetres, printed at M 1:25.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base
import build_tv005_table_kitchen_zone as previous


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-006_стол-90_холодильник-возврат_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-006_стол-90_холодильник-возврат_М1-25.pdf"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
WORK = base.WORK
GOOD = base.GOOD
BAD = base.BAD
ORANGE = "#ad6800"
BLUE = "#2f6e8d"
GRAY = "#97a0aa"
PALE_GREEN = "#eff8f1"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"

ROOM = (0, 0, 5710, 3500)
D2_GUARD = (0, 0, 1200, 1300)
ROUTE_900_REFERENCE = (0, 350, 5710, 1250)
O1_ROUTE = (4810, 350, 5710, 2450)
DESK_APPROACH = (4510, 1250, 5110, 2490)

# Kitchen after returning the fridge to the left-hand return.
KITCHEN_TOP = (0, 2900, 2400, 3500)
LEFT_FILLER = (0, 2200, 600, 2300)
FRIDGE = (0, 2300, 600, 2900)
FRIDGE_DOOR = (600, 2300, 1200, 2900)  # opening/standing zone; SKU check required

# User-selected option A: 90-degree table, 700 mm both from the upper run and
# from the left return face along the X axis.  Its lower end leaves 800 mm to
# the lower wall, so the old 900-mm circulation strip is intentionally not kept.
TABLE = (1300, 800, 2100, 2200)  # 800 x 1400, CJ196 rotated 90 degrees
CHAIR_RIGHT_1 = (2100, 900, 2500, 1300)
CHAIR_RIGHT_2 = (2100, 1550, 2500, 1950)
CHILD_CHAIR = (900, 1400, 1300, 1800)

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
    fixed = {
        "kitchen_top": KITCHEN_TOP,
        "left_filler": LEFT_FILLER,
        "fridge": FRIDGE,
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

    for left, right in combinations(("kitchen_top", "left_filler", "fridge", "table", "sofa", "desk", "tv_media"), 2):
        if overlap(fixed[left], fixed[right]):
            raise AssertionError(f"fixed overlap {left}/{right}")
    if overlap(TABLE, D2_GUARD):
        raise AssertionError("table enters D2 guard")
    if overlap(FRIDGE, TABLE) or overlap(FRIDGE_DOOR, TABLE):
        raise AssertionError("fridge or its conceptual door zone intersects table")
    if overlap(SOFA, DESK_CHAIR):
        raise AssertionError("desk chair overlaps sofa")

    assert TABLE[2] - TABLE[0] == 800
    assert TABLE[3] - TABLE[1] == 1400
    assert TABLE[0] - FRIDGE[2] == 700
    assert KITCHEN_TOP[1] - TABLE[3] == 700
    assert TABLE[1] == 800
    assert overlap(TABLE, ROUTE_900_REFERENCE)
    overlap_height = min(TABLE[3], ROUTE_900_REFERENCE[3]) - max(TABLE[1], ROUTE_900_REFERENCE[1])
    assert overlap_height == 450
    print("PASS TV-006: option A 90-degree table; 700 to upper kitchen and left return; 900 D2->O1 route intentionally not claimed")


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
    text(c, bold, 14, 282, 13.2, "TV-006 - СТОЛ 90 ГРАД. / ХОЛОДИЛЬНИК НА ВОЗВРАТЕ")
    text(c, regular, 14, 274, 4.9,
         "Выбран вариант A: 700 мм до фасадов верхней кухни. Мебель - проектные габариты до выбора SKU.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-006 | лист 1/1 | М 1:25", MUTED, right=True)


def dashed_rect(c, rect, color, width=0.30):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width * mm); c.setDash(1.5 * mm, 0.85 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()


def draw_kitchen(c, regular, bold):
    modules = (
        (0, 600, "МОЙКА"),
        (600, 450, "ПММ 450"),
        (1050, 600, "ВАРКА/ДУХ."),
        (1650, 600, "СВЧ/ДУХ."),
        (2250, 150, "ДОБОР"),
    )
    for x, width, label in modules:
        base.model_box(c, x, 2900, width, 600, KITCHEN, "#6e5a34", 0.20)
        base.label_model(c, regular, x + width / 2, 3190, label, 3.5 if width >= 450 else 3.1, "#5b4827")
    base.label_model(c, bold, 1200, 3440, "ВЕРХНЯЯ ЛИНИЯ КУХНИ 2400", 4.8, "#5b4827")

    base.model_box(c, LEFT_FILLER[0], LEFT_FILLER[1], 600, 100, "#ead5a8", "#6e5a34", 0.20)
    base.label_model(c, regular, 300, 2238, "ДОБОР 100", 3.5, "#5b4827")
    base.model_box(c, FRIDGE[0], FRIDGE[1], 600, 600, "#e7ca90", "#6e5a34", 0.24)
    base.label_model(c, bold, 300, 2570, "ХОЛОДИЛЬНИК", 4.5, "#5b4827")
    base.label_model(c, regular, 300, 2440, "600 x 600", 3.8, "#5b4827")
    dashed_rect(c, FRIDGE_DOOR, ORANGE, 0.24)
    base.label_model(c, regular, 900, 2500, "дверь/доступ - SKU", 3.3, ORANGE)


def draw_table(c, regular, bold):
    x1, y1, x2, y2 = TABLE
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 42)
    base.model_line(c, x1, y1 + 700, x2, y1 + 700, "#6b8665", 0.14)
    base.label_model(c, bold, 1700, 1570, "СТОЛ CJ196", 4.8, "#405d3c")
    base.label_model(c, regular, 1700, 1435, "800 x 1400; поворот 90 град.", 3.8, "#405d3c")
    for rect, facing in ((CHAIR_RIGHT_1, "left"), (CHAIR_RIGHT_2, "left"), (CHILD_CHAIR, "right")):
        x1, y1, x2, y2 = rect
        base.draw_chair(c, x1, y1, x2 - x1, y2 - y1, facing=facing)
    base.label_model(c, regular, 2300, 1350, "2 взрослых", 3.5, "#6d6258")
    base.label_model(c, regular, 1100, 1855, "ребёнок", 3.5, "#6d6258")


def draw_reference_conflict(c, regular):
    dashed_rect(c, ROUTE_900_REFERENCE, BAD, 0.36)
    base.label_model(c, regular, 3520, 670, "D2 -> O1 900: ПЕРЕСЕЧЕНИЕ СО СТОЛОМ 450", 3.9, BAD)
    base.label_model(c, regular, 1700, 560, "до нижней стены 800; это не подтвержденный маршрут к O1", 3.7, ORANGE)


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(600), base.qx(1300), base.qy(2260), "700", ORANGE)
    base.dim_h(c, regular, base.qx(1300), base.qx(2100), base.qy(760), "800", "#405d3c")
    base.dim_v(c, regular, base.qx(2140), base.qy(800), base.qy(2200), "1400", "#405d3c")
    base.dim_v(c, regular, base.qx(2180), base.qy(2200), base.qy(2900), "700", ORANGE)
    base.dim_v(c, regular, base.qx(1260), base.qy(0), base.qy(800), "800", ORANGE)
    base.dim_v(c, regular, base.qx(630), base.qy(2300), base.qy(2900), "600", "#5b4827")
    base.dim_v(c, regular, base.qx(665), base.qy(2200), base.qy(2300), "100", "#5b4827")
    base.dim_h(c, regular, base.qx(0), base.qx(2400), base.qy(2860), "2400")
    base.dim_h(c, regular, base.qx(2430), base.qx(4430), base.qy(2460), "2000")
    base.dim_h(c, regular, base.qx(4510), base.qx(5710), base.qy(2860), "1200")
    base.dim_h(c, regular, base.qx(2610), base.qx(4210), base.qy(340), "1600")
    base.dim_v(c, regular, base.qx(4240), base.qy(0), base.qy(300), "300")


def sidebar(c, regular, bold):
    x, w = 270, 136
    panel(c, bold, x, 210, w, 58, "ПРИНЯТАЯ КОМПОНОВКА", PALE_GREEN)
    yy = 254
    for line in (
        "- CJ196 повёрнут: 800 x 1400",
        "- от левого возврата до стола 700",
        "- от верхней кухни до стола 700",
        "- холодильник: левый возврат 600",
        "- верхний левый модуль теперь мойка",
    ):
        text(c, regular, x + 4, yy, 5.8, line); yy -= 5.7

    panel(c, bold, x, 136, w, 64, "ЧЕСТНАЯ ЦЕНА ВАРИАНТА A", PALE_RED)
    yy = 185
    for paragraph in (
        "Поворотный стол пересекает прежнюю полосу D2 -> O1 шириной 900 мм на 450 мм.",
        "До нижней стены остаётся 800 мм, но это не заявляется как непрерывный проход к O1.",
    ):
        yy = wrapped(c, regular, x + 4, yy, 5.8, paragraph, 43, BAD, 6.2, "-") - 1.0

    panel(c, bold, x, 68, w, 56, "ПРОВЕРИТЬ ДО ЗАКАЗА", PALE_ORANGE)
    yy = 108
    for line in (
        "- направление двери холодильника",
        "- вентзазоры холодильника",
        "- реальные ножки/царги CJ196",
        "- натурный макет маршрута D2 -> O1",
    ):
        text(c, regular, x + 4, yy, 5.8, line, ORANGE); yy -= 5.7


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-006 / СТОЛ 90 ГРАД")
    previous.draw_d2_guard(c, regular)
    dashed_rect(c, O1_ROUTE, GOOD, 0.30)
    base.label_model(c, regular, 5255, 2380, "900 к O1 вне зоны стола", 3.6, GOOD)
    dashed_rect(c, DESK_APPROACH, BLUE, 0.30)
    base.label_model(c, regular, 4810, 2400, "подход к креслу 600", 3.6, BLUE)
    draw_kitchen(c, regular, bold)
    draw_reference_conflict(c, regular)
    draw_table(c, regular, bold)
    previous.draw_sofa(c, regular, bold)
    previous.draw_desk(c, regular)
    previous.draw_tv(c, regular, bold)
    dimensions(c, regular)
    sidebar(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-006 - стол 90 градусов, холодильник на возврате")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-006 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
