# -*- coding: utf-8 -*-
"""TV-008 - functional kitchen layout for B01, drawn in real millimetres.

This is a comparison and decision sheet, not a furniture manufacturing drawing.
It replaces the provisional sink-in-corner / duplicate-dishwasher logic of
TV-007 with a complete work sequence and makes the dining-table shift explicit.
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
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-008_функциональная_кухня_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-008_функциональная_схема_кухни_М1-25.pdf"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
WORK = base.WORK
GOOD = base.GOOD
BAD = base.BAD
ORANGE = "#ad6800"
BLUE = "#2f6e8d"
GREEN = "#4f7d62"
PALE_GREEN = "#eff8f1"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"
PALE_BLUE = "#eef7fb"

ROOM = (0, 0, 5710, 3500)
TOP_KITCHEN = (0, 2900, 2400, 3500)
LEFT_KITCHEN = (0, 1300, 600, 2900)

# Main work line, from the L-corner toward the free end by the sofa.
CORNER_PREP = (0, 2900, 600, 3500)
SINK = (600, 2900, 1200, 3500)
PREP = (1200, 2900, 1800, 3500)
HOB = (1800, 2900, 2400, 3500)

# Return, from the entrance/free end toward the L-corner.
FRIDGE = (0, 1300, 600, 1900)
PANTRY = (0, 1900, 600, 2250)
DISHWASHER = (0, 2250, 600, 2850)
CORNER_FILLER = (0, 2850, 600, 2900)

# The current Option A table was x=1300..2100.  This is the proposed right shift.
OLD_TABLE = (1300, 800, 2100, 2200)
TABLE = (1900, 800, 2700, 2200)
SOFA = (2430, 2500, 4430, 3500)
DESK = (4510, 2900, 5710, 3500)
DESK_CHAIR = (4510, 2490, 5110, 3110)
TV_MEDIA = (2610, 0, 4210, 300)
D2_GUARD = (0, 0, 1200, 1300)
ROUTE_900_REFERENCE = (0, 350, 5710, 1250)
O1_ROUTE = (4810, 350, 5710, 2450)


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def in_room(name: str, rect: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    if not (0 <= x1 < x2 <= ROOM[2] and 0 <= y1 < y2 <= ROOM[3]):
        raise AssertionError(f"{name} outside B01: {rect}")


def validate_geometry() -> None:
    fixed = {
        "top_kitchen": TOP_KITCHEN,
        "left_kitchen": LEFT_KITCHEN,
        "corner_prep": CORNER_PREP,
        "sink": SINK,
        "prep": PREP,
        "hob": HOB,
        "fridge": FRIDGE,
        "pantry": PANTRY,
        "dishwasher": DISHWASHER,
        "filler": CORNER_FILLER,
        "old_table": OLD_TABLE,
        "table": TABLE,
        "sofa": SOFA,
        "desk": DESK,
        "tv": TV_MEDIA,
    }
    for name, rect in fixed.items():
        in_room(name, rect)
    for left, right in combinations(("top_kitchen", "left_kitchen", "table", "sofa", "desk", "tv"), 2):
        if overlap(fixed[left], fixed[right]):
            raise AssertionError(f"fixed overlap {left}/{right}")
    assert sum(rect[2] - rect[0] for rect in (CORNER_PREP, SINK, PREP, HOB)) == 2400
    assert sum(rect[3] - rect[1] for rect in (FRIDGE, PANTRY, DISHWASHER, CORNER_FILLER)) == 1600
    assert SINK[0] - TOP_KITCHEN[0] == 600  # sink is not a corner module
    assert PREP[2] - PREP[0] == 600
    assert DISHWASHER[3] - DISHWASHER[1] == 600
    assert FRIDGE[3] - FRIDGE[1] == 600
    assert TABLE[2] - TABLE[0] == 800 and TABLE[3] - TABLE[1] == 1400
    assert TABLE[0] - LEFT_KITCHEN[2] == 1300
    assert TOP_KITCHEN[1] - TABLE[3] == 700
    assert SOFA[1] - TABLE[3] == 300
    assert TABLE[0] - OLD_TABLE[0] == 600
    assert overlap(TABLE, ROUTE_900_REFERENCE)
    route_overlap = min(TABLE[3], ROUTE_900_REFERENCE[3]) - max(TABLE[1], ROUTE_900_REFERENCE[1])
    assert route_overlap == 450
    print("PASS TV-008: kitchen 2400+1600; sink off corner; 600 prep; dishwasher 600; table shift +600")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def panel(c, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7.5, 6.8, title)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=5.7, bullet=None):
    for index, row in enumerate(base.wrap(value, width)):
        prefix = (bullet + " ") if bullet and index == 0 else ("  " if bullet else "")
        text(c, font, x, y, size, prefix + row, color)
        y -= leading
    return y


def dashed_rect(c, rect, color, width=0.28):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width * mm); c.setDash(1.5 * mm, 0.85 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()


def draw_d2_guard(c, regular):
    """Keep the entrance-control envelope visible without assuming door swing."""
    dashed_rect(c, D2_GUARD, "#c2771b", 0.28)
    base.label_model(c, regular, 600, 620, "D2: 910 B01 / 915 контроль", 3.35, "#a85d18")
    base.label_model(c, regular, 600, 440, "проём и открывание уточнить", 2.8, "#a85d18")


def kitchen_module(c, regular, rect, label, fill=KITCHEN, size=3.5):
    x1, y1, x2, y2 = rect
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, fill, "#6e5a34", 0.20)
    base.label_model(c, regular, (x1 + x2) / 2, (y1 + y2) / 2 - 12, label, size, "#5b4827")


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13.2, "TV-008 - ФУНКЦИОНАЛЬНАЯ СХЕМА КУХНИ")
    text(c, regular, 14, 274, 4.9,
         "Масштабная проверка компоновки. Не заказ кухни: вода, канализация и вентканал пока не имеют двух привязок.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-008 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_kitchen(c, regular, bold):
    kitchen_module(c, regular, CORNER_PREP, "УГОЛ / ПОДГ. 600", "#ead7ae", 3.35)
    kitchen_module(c, regular, SINK, "МОЙКА 600", "#f1d6a0", 4.0)
    kitchen_module(c, regular, PREP, "ПОДГОТОВКА 600", "#ead7ae", 3.45)
    kitchen_module(c, regular, HOB, "ВАРКА 600\nДУХОВКА СНИЗУ", "#e7ca90", 3.15)
    kitchen_module(c, regular, FRIDGE, "ХОЛОДИЛЬНИК 600", "#e7ca90", 3.7)
    kitchen_module(c, regular, PANTRY, "ВЫКАТ /\nХРАН. 350", "#ead5a8", 3.15)
    kitchen_module(c, regular, DISHWASHER, "ПММ 600", "#f1d6a0", 4.0)
    kitchen_module(c, regular, CORNER_FILLER, "ДОБОР 50", "#f8efd8", 2.7)
    base.label_model(c, bold, 1200, 3440, "Г-КУХНЯ: 2400 + 1600 ФРОНТОВ", 4.8, "#5b4827")

    # A simple sink bowl and a four-zone hob make the functional roles readable.
    c.setStrokeColor(HexColor("#58717d")); c.setLineWidth(0.22 * mm)
    c.circle(base.qx(900) * mm, base.qy(3200) * mm, base.p(165) * mm, fill=0, stroke=1)
    c.setStrokeColor(HexColor("#65523a")); c.setLineWidth(0.14 * mm)
    for cx, cy in ((1980, 3070), (2220, 3070), (1980, 3310), (2220, 3310)):
        c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(75) * mm, fill=0, stroke=1)


def draw_table(c, regular, bold):
    # TV-007 position is retained only as a ghosted comparison.
    x1, y1, x2, y2 = OLD_TABLE
    c.setFillColor(HexColor("#eef1f3")); c.setStrokeColor(HexColor("#9aa3aa")); c.setLineWidth(0.18 * mm); c.setDash(1.1 * mm, 0.75 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=1, stroke=1); c.setDash()
    base.label_model(c, regular, 1700, 1510, "TV-007: стол был здесь", 3.2, "#7b858d")

    x1, y1, x2, y2 = TABLE
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 42)
    base.model_line(c, x1, y1 + 700, x2, y1 + 700, "#6b8665", 0.14)
    base.label_model(c, bold, 2300, 1570, "СТОЛ CJ196", 4.8, "#405d3c")
    base.label_model(c, regular, 2300, 1435, "800 x 1400; сдвиг вправо +600", 3.55, "#405d3c")


def draw_sofa_desk_tv(c, regular, bold):
    base.draw_sofa(c, regular, 2430, 2500, 2000, 1000, "down")
    base.label_model(c, bold, 3430, 2595, "ДИВАН-КРОВАТЬ 2000x1000", 3.2, "#544943")
    base.model_box(c, DESK[0], DESK[1], DESK[2] - DESK[0], DESK[3] - DESK[1], WORK, "#4e7589", 0.24, 38)
    base.label_model(c, regular, 5110, 3310, "РМ 1200x600", 3.2, "#2e5b70")
    dashed_rect(c, DESK_CHAIR, BLUE, 0.24)
    base.label_model(c, regular, 4810, 2400, "подход к креслу 600", 3.3, BLUE)
    base.draw_tv(c, regular, TV_MEDIA[0], TV_MEDIA[1], TV_MEDIA[2] - TV_MEDIA[0], TV_MEDIA[3] - TV_MEDIA[1], "bottom")
    base.label_model(c, regular, 3410, 315, "ТВ + МЕДИА 1600x300", 3.1, "#624a59")


def draw_constraints(c, regular):
    # New table position creates real appliance clearance along the return.
    dashed_rect(c, (600, 1300, 1900, 2200), GREEN, 0.30)
    base.label_model(c, regular, 1250, 2060, "1300: фасады левой ветви -> стол", 3.7, GREEN)
    dashed_rect(c, (1900, 2200, 2700, 2900), ORANGE, 0.30)
    base.label_model(c, regular, 2300, 2560, "700: верхняя кухня -> стол", 3.65, ORANGE)
    dashed_rect(c, O1_ROUTE, GOOD, 0.25)
    base.label_model(c, regular, 5255, 2380, "O1 1600 -> терраса", 3.4, GOOD)
    dashed_rect(c, ROUTE_900_REFERENCE, BAD, 0.34)
    base.label_model(c, regular, 3650, 670, "D2 -> O1 900: стол всё ещё пересекает полосу на 450", 3.5, BAD)


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(0), base.qx(2400), base.qy(2860), "2400")
    base.dim_v(c, regular, base.qx(630), base.qy(1300), base.qy(2900), "1600", "#5b4827")
    base.dim_h(c, regular, base.qx(600), base.qx(1900), base.qy(1240), "1300", GREEN)
    base.dim_v(c, regular, base.qx(2735), base.qy(2200), base.qy(2900), "700", ORANGE)
    base.dim_h(c, regular, base.qx(1900), base.qx(2700), base.qy(760), "800", "#405d3c")
    base.dim_v(c, regular, base.qx(2740), base.qy(800), base.qy(2200), "1400", "#405d3c")
    base.dim_h(c, regular, base.qx(1300), base.qx(1900), base.qy(740), "+600", GREEN)
    base.dim_v(c, regular, base.qx(4200), base.qy(2200), base.qy(2500), "300", "#544943")
    base.dim_h(c, regular, base.qx(2610), base.qx(4210), base.qy(340), "1600")


def sidebar(c, regular, bold):
    x, w = 270, 136
    panel(c, bold, x, 210, w, 58, "ЧТО ИСПРАВЛЕНО", PALE_GREEN)
    yy = 254
    for line in (
        "- мойка не в углу",
        "- ПММ только одна: 600 мм",
        "- между мойкой и варкой 600",
        "  подготовки",
        "- холодильник и ПММ получают",
        "  рабочий подход 1300 мм",
    ):
        text(c, regular, x + 4, yy, 5.5, line); yy -= 5.0

    panel(c, bold, x, 139, w, 61, "ПОРЯДОК РАБОТЫ", PALE_BLUE)
    yy = 185
    for paragraph in (
        "Холодильник -> мойка/ПММ -> подготовка -> варка.",
        "Часто используемое хранение: выкатной пенал, ящики у варки и верхние шкафы.",
    ):
        yy = wrapped(c, regular, x + 4, yy, 5.5, paragraph, 45, INK, 5.8, "-") - 1.3

    panel(c, bold, x, 66, w, 63, "НЕ ФИНАЛИЗИРОВАТЬ ДО ОБМЕРА", PALE_RED)
    yy = 113
    for line in (
        "- вода и канализация мойки/ПММ",
        "- вентканал и трасса вытяжки",
        "- открывание D2, O1 и холодильника",
        "- паспорта техники и монтажные",
        "  доборы угла 50-100 мм",
    ):
        text(c, regular, x + 4, yy, 5.35, line, BAD); yy -= 5.0


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-008 / ФУНКЦИОНАЛЬНАЯ КУХНЯ")
    draw_d2_guard(c, regular)
    draw_kitchen(c, regular, bold)
    draw_constraints(c, regular)
    draw_table(c, regular, bold)
    draw_sofa_desk_tv(c, regular, bold)
    dimensions(c, regular)
    sidebar(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-008 - функциональная схема кухни")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-008 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
