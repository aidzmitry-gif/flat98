# -*- coding: utf-8 -*-
"""TV-005: full CJ196 table placed in the kitchen zone of B01.

All coordinates are model millimetres and print at M 1:25.  This is a new
comparison option, not a silent rewrite of TV-001/TV-004.  It intentionally
shortens the former 1600-mm kitchen return so the table can genuinely sit in
the kitchen zone while the 900-mm D2->O1 route remains clear even with the
three shown seats in place.
"""
from __future__ import annotations

from itertools import combinations
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-005_стол-в-кухонной-зоне_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-005_стол-в-кухонной-зоне_М1-25.pdf"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
WORK = base.WORK
GOOD = base.GOOD
BAD = base.BAD
BLUE = "#2f6e8d"
ORANGE = "#ad6800"
GRAY = "#aab4bc"
PALE_BLUE = "#eef7fb"
PALE_GREEN = "#eff8f1"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"
SIDEBAR_X = 270
SIDEBAR_W = 136

ROOM = (0, 0, 5710, 3500)
D2_GUARD = (0, 0, 1200, 1300)
MAIN_ROUTE = (0, 350, 5710, 1250)
O1_ROUTE = (4810, 350, 5710, 2450)
DESK_APPROACH = (4510, 1250, 5110, 2490)

KITCHEN_TOP = (0, 2900, 2400, 3500)
# Only this 650-mm return can coexist with the table.  The previous 1600-mm
# return is drawn as a grey rejected contour because its opening/front zone
# would overlap the table.
SHORT_RETURN = (0, 2250, 600, 2900)
SHORT_RETURN_FRONT = (600, 2250, 1300, 2900)
FORMER_RETURN = (0, 1300, 600, 2900)
FORMER_RETURN_FRONT = (600, 1300, 1300, 2900)

TABLE = (670, 1400, 2070, 2200)  # CJ196 1400x800 in the kitchen zone
CHAIR_1 = (2070, 1450, 2470, 1850)  # adult, long right side
CHAIR_2 = (2070, 1850, 2470, 2250)  # adult, long right side
CHILD_CHAIR = (220, 1550, 670, 2000)  # child at the left end
KITCHEN_CLEARANCE = (670, 2200, 2070, 2900)

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
    items = {
        "kitchen_top": KITCHEN_TOP,
        "short_return": SHORT_RETURN,
        "table": TABLE,
        "chair_1": CHAIR_1,
        "chair_2": CHAIR_2,
        "child_chair": CHILD_CHAIR,
        "sofa": SOFA,
        "desk": DESK,
        "tv_media": TV_MEDIA,
    }
    for name, rect in items.items():
        assert_in_room(name, rect)
        if overlap(rect, D2_GUARD):
            raise AssertionError(f"{name} enters D2 guard")
    assert_in_room("desk_chair", DESK_CHAIR)
    for left, right in combinations(items, 2):
        if overlap(items[left], items[right]):
            raise AssertionError(f"fixed overlap {left}/{right}")
    if overlap(DESK_CHAIR, SOFA):
        raise AssertionError("desk chair overlaps sofa")
    for name, rect in items.items():
        if overlap(rect, MAIN_ROUTE):
            raise AssertionError(f"{name} blocks 900-mm D2->O1 route")
        if overlap(rect, O1_ROUTE):
            raise AssertionError(f"{name} blocks O1 route")
        if name != "desk" and overlap(rect, DESK_APPROACH):
            raise AssertionError(f"{name} blocks desk approach")
    if overlap(SHORT_RETURN_FRONT, TABLE):
        raise AssertionError("short return fronts are blocked")
    if not overlap(FORMER_RETURN_FRONT, TABLE):
        raise AssertionError("former long return conflict must be explicit")
    assert TABLE[2] - TABLE[0] == 1400
    assert TABLE[3] - TABLE[1] == 800
    assert TABLE[0] - 600 == 70
    assert KITCHEN_TOP[1] - TABLE[3] == 700
    assert MAIN_ROUTE[3] - MAIN_ROUTE[1] == 900
    assert SHORT_RETURN[1] - TABLE[3] == 50
    print("PASS TV-005: table in kitchen zone; 700 kitchen clearance; 900 D2->O1 remains clear with seats; shortened return shown")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=None, bullet=None):
    leading = leading or size * 1.28
    for index, row in enumerate(base.wrap(value, width)):
        prefix = (bullet + " ") if bullet and index == 0 else ("  " if bullet else "")
        text(c, font, x, y, size, prefix + row, color)
        y -= leading
    return y


def panel(c, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7.5, 6.8, title)


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13.2, "TV-005 - СТОЛ CJ196 В КУХОННОЙ ЗОНЕ")
    text(c, regular, 14, 274, 4.9,
         "Новый вариант: стол слева от дивана, перед кухней. Масштаб B01; мебель - проектные габариты до SKU.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-005 | лист 1/1 | М 1:25", MUTED, right=True)


def route_rect(c, regular, rect, label, at, color, width=0.30):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width * mm); c.setDash(1.5 * mm, 0.85 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, at[0], at[1], label, 3.7, color)


def draw_d2_guard(c, regular):
    x1, y1, x2, y2 = D2_GUARD
    c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.32 * mm); c.setDash(1.7 * mm, 0.9 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, 600, 490, "D2 GUARD 1200x1300", 3.6, ORANGE)


def kitchen_module(c, regular, x, y, w, h, label):
    base.model_box(c, x, y, w, h, KITCHEN, "#6e5a34", 0.20)
    base.label_model(c, regular, x + w / 2, y + h / 2 - 10, label, 3.7, "#5b4827")


def draw_kitchen(c, regular, bold):
    for x, label in ((0, "ХОЛ./ПЕНАЛ"), (600, "МОЙКА/ПММ"),
                     (1200, "ВАРКА"), (1800, "ПЕНАЛ СВЧ/ДУХ")):
        kitchen_module(c, regular, x, 2900, 600, 600, label)
    base.model_box(c, 730, 3050, 340, 240, "#edf2f2", "#617377", 0.12, 22)
    base.model_line(c, 900, 3290, 900, 3370, "#617377", 0.16)
    c.setStrokeColor(HexColor("#6e5a34")); c.setLineWidth(0.14 * mm)
    for x, y in ((1380, 3065), (1600, 3065), (1380, 3280), (1600, 3280)):
        c.circle(base.qx(x) * mm, base.qy(y) * mm, base.p(65) * mm, fill=0, stroke=1)
    base.label_model(c, bold, 1200, 3440, "КУХНЯ: ВЕРХНЯЯ ЛИНИЯ 2400", 4.8, "#5b4827")

    # Ghost the former return first, then overlay the only active short return.
    x1, y1, x2, y2 = FORMER_RETURN
    c.setFillColor(HexColor("#f1f3f5")); c.setStrokeColor(HexColor(GRAY)); c.setLineWidth(0.20 * mm)
    c.setDash(1.1 * mm, 0.75 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=1, stroke=1)
    c.setDash()
    base.label_model(c, regular, 300, 1790, "бывшая ветвь", 3.6, "#6b7280")
    base.label_model(c, regular, 300, 1675, "600x1600 - убрать", 3.6, "#6b7280")
    kitchen_module(c, regular, 0, 2250, 600, 650, "ВОЗВРАТ")
    base.label_model(c, regular, 300, 2500, "600x650", 3.8, "#5b4827")


def draw_clearance(c, regular):
    x1, y1, x2, y2 = KITCHEN_CLEARANCE
    c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.28 * mm); c.setDash(1.25 * mm, 0.8 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, 1370, 2565, "700 перед кухней: готовка/фасады", 3.9, ORANGE)


def draw_table(c, regular, bold):
    x1, y1, x2, y2 = TABLE
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 42)
    base.model_line(c, x1 + 700, y1, x1 + 700, y2, "#6b8665", 0.14)
    base.label_model(c, bold, 1370, 1810, "СТОЛ CJ196", 4.8, "#405d3c")
    base.label_model(c, regular, 1370, 1685, "1400x800; H750 по визуализации", 3.8, "#405d3c")
    for rect, facing in ((CHAIR_1, "left"), (CHAIR_2, "left"), (CHILD_CHAIR, "right")):
        cx1, cy1, cx2, cy2 = rect
        base.draw_chair(c, cx1, cy1, cx2 - cx1, cy2 - cy1, facing=facing)
    base.label_model(c, regular, 2270, 2285, "2 взрослых", 3.5, "#6d6258")
    base.label_model(c, regular, 445, 2060, "ребёнок", 3.5, "#6d6258")


def draw_sofa(c, regular, bold):
    base.draw_sofa(c, regular, 2430, 2500, 2000, 1000, "down")
    base.label_model(c, bold, 3430, 2595, "ДИВАН-КРОВАТЬ 2000x1000", 4.6, "#544943")
    base.label_model(c, regular, 3430, 2450, "стол расположен слева, не перед диваном", 3.8, "#544943")


def draw_desk(c, regular):
    base.model_box(c, 4510, 2900, 1200, 600, WORK, "#4e7589", 0.24, 38)
    base.model_line(c, 5110, 2970, 5110, 3430, "#6a94a8", 0.14)
    base.model_box(c, 4640, 3160, 340, 110, "#f3f7f8", "#4e7589", 0.12, 12)
    base.label_model(c, regular, 4810, 3310, "РМ 1200x600", 4.8, "#2e5b70")
    x1, y1, x2, y2 = DESK_CHAIR
    c.setStrokeColor(HexColor(BLUE)); c.setLineWidth(0.28 * mm); c.setDash(1.6 * mm, 0.9 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.draw_chair(c, 4560, 2600, 500, 500, facing="up")
    base.label_model(c, regular, 4810, 2495, "кресло max 600x620", 3.6, BLUE)


def draw_tv(c, regular, bold):
    base.draw_tv(c, regular, 2610, 0, 1600, 300, "bottom")
    base.label_model(c, bold, 3410, 315, "ТВ / МЕДИА 1600x300", 4.3, "#624a59")


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(0), base.qx(2400), base.qy(2860), "2400")
    base.dim_h(c, regular, base.qx(600), base.qx(670), base.qy(2230), "70", ORANGE)
    base.dim_h(c, regular, base.qx(670), base.qx(2070), base.qy(2250), "1400", "#405d3c")
    base.dim_v(c, regular, base.qx(2110), base.qy(1400), base.qy(2200), "800", "#405d3c")
    base.dim_v(c, regular, base.qx(2185), base.qy(2200), base.qy(2900), "700", ORANGE)
    base.dim_v(c, regular, base.qx(2250), base.qy(2200), base.qy(2250), "50", GRAY)
    base.dim_v(c, regular, base.qx(4450), base.qy(350), base.qy(1250), "900", GOOD)
    base.dim_h(c, regular, base.qx(2430), base.qx(4430), base.qy(2460), "2000")
    base.dim_h(c, regular, base.qx(4510), base.qx(5710), base.qy(2860), "1200")
    base.dim_h(c, regular, base.qx(2610), base.qx(4210), base.qy(340), "1600")
    base.dim_v(c, regular, base.qx(4240), base.qy(0), base.qy(300), "300")


def sidebar(c, regular, bold):
    panel(c, bold, SIDEBAR_X, 210, SIDEBAR_W, 58, "ЧТО ИЗМЕНЕНО", PALE_GREEN)
    yy = 254
    for line in (
        "- стол перенесён в кухонную зону",
        "- координаты: X=670..2070",
        "  Y=1400..2200 мм",
        "- два взрослых сидят справа",
        "- ребёнок - у левого торца",
        "- D2 -> O1 остаётся 900 мм",
    ):
        text(c, regular, SIDEBAR_X + 4, yy, 5.8, line, INK); yy -= 5.7
    panel(c, bold, SIDEBAR_X, 136, SIDEBAR_W, 64, "ПРОХОД И КУХНЯ", PALE_ORANGE)
    yy = 185
    for paragraph in (
        "Перед верхней линией кухни до стола 700 мм. Это рабочий пояс: фасады и готовка доступны.",
        "Стулья не заходят в нижнюю полосу D2 -> O1: 900 мм остаются и при посадке.",
    ):
        yy = wrapped(c, regular, SIDEBAR_X + 4, yy, 5.8, paragraph, 43, INK, 6.2, "-") - 1.0
    panel(c, bold, SIDEBAR_X, 68, SIDEBAR_W, 56, "ЦЕНА РЕШЕНИЯ: ХРАНЕНИЕ", PALE_RED)
    yy = 108
    for line in (
        "Полная левая Г-ветвь 600x1600",
        "здесь невозможна: её фасады",
        "пересекаются со столом. Остаётся",
        "короткий возврат 600x650.",
        "Потеря фронтов: 950 мм.",
    ):
        text(c, regular, SIDEBAR_X + 4, yy, 5.8, line, BAD); yy -= 5.7


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-005 / СТОЛ В КУХНЕ")
    draw_d2_guard(c, regular)
    route_rect(c, regular, MAIN_ROUTE, "D2 -> O1: 900 мм даже с местами за столом", (3530, 720), GOOD, 0.36)
    route_rect(c, regular, O1_ROUTE, "900 к O1", (5255, 2380), GOOD, 0.30)
    route_rect(c, regular, DESK_APPROACH, "подход к креслу 600", (4810, 2400), BLUE, 0.30)
    draw_kitchen(c, regular, bold)
    draw_clearance(c, regular)
    draw_table(c, regular, bold)
    draw_sofa(c, regular, bold)
    draw_desk(c, regular)
    draw_tv(c, regular, bold)
    dimensions(c, regular)
    sidebar(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-005 - стол CJ196 в кухонной зоне")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-005 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
