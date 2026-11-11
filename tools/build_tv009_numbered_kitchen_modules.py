# -*- coding: utf-8 -*-
"""TV-009 - numbered kitchen-module revision requested by the user.

Keeps the real-size B01 geometry and table shift from TV-008, but changes the
top line: hob moves into the former sink module, the former hob becomes a tall
oven/microwave/storage unit, and the former preparation module combines an
upper preparation surface with the sink below it.  Numbers are deliberate
conversation anchors, not equipment IDs for ordering.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base
import build_tv008_functional_kitchen_scheme as previous


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-009_нумерованная_кухня_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-009_нумерованная_схема_кухни_М1-25.pdf"

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
PALE_BLUE = "#eef7fb"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"

ROOM = previous.ROOM
TOP_KITCHEN = previous.TOP_KITCHEN
LEFT_KITCHEN = previous.LEFT_KITCHEN
CORNER_PREP = previous.CORNER_PREP
HOB = previous.SINK
SINK_PREP = previous.PREP
TALL_PENAL = previous.HOB
FRIDGE = previous.FRIDGE
PANTRY = previous.PANTRY
DISHWASHER = previous.DISHWASHER
CORNER_FILLER = previous.CORNER_FILLER
TABLE = previous.TABLE
OLD_TABLE = previous.OLD_TABLE
SOFA = previous.SOFA
DESK = previous.DESK
DESK_CHAIR = previous.DESK_CHAIR
TV_MEDIA = previous.TV_MEDIA
D2_GUARD = previous.D2_GUARD
ROUTE_900_REFERENCE = previous.ROUTE_900_REFERENCE
O1_ROUTE = previous.O1_ROUTE

# Markers intentionally sit at zone edges, not on top of functional labels.
ZONE_MARKERS = (
    (1, 100, 3420, "#7b5f2c"),
    (2, 700, 3420, "#7b5f2c"),
    (3, 1300, 3420, "#58717d"),
    (4, 1900, 3420, "#6b5230"),
    (5, 100, 2780, "#58717d"),
    (6, 100, 2180, "#7b5f2c"),
    (7, 100, 1780, "#7b5f2c"),
    (8, 2480, 2050, "#4e6c49"),
    (9, 2600, 3420, "#70585b"),
    (10, 4660, 3420, "#2f6e8d"),
    (11, 4250, 150, "#70585b"),
    (12, 4100, 900, "#b54a3b"),
)


def validate_geometry() -> None:
    previous.validate_geometry()
    assert HOB == (600, 2900, 1200, 3500)
    assert SINK_PREP == (1200, 2900, 1800, 3500)
    assert TALL_PENAL == (1800, 2900, 2400, 3500)
    assert HOB[2] - HOB[0] == 600
    assert SINK_PREP[2] - SINK_PREP[0] == 600
    assert TALL_PENAL[2] - TALL_PENAL[0] == 600
    assert SINK_PREP[0] - TOP_KITCHEN[0] == 1200
    assert {number for number, *_ in ZONE_MARKERS} == set(range(1, 13))
    print("PASS TV-009: numbered zones; hob moved; sink/prep and tall oven/microwave/storage module")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def panel(c, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7.5, 6.5, title)


def dashed_rect(c, rect, color, width=0.28):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width * mm); c.setDash(1.5 * mm, 0.85 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()


def zone_marker(c, bold, number, cx, cy, fill="#263442"):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor("#ffffff")); c.setLineWidth(0.18 * mm)
    c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(60) * mm, fill=1, stroke=1)
    base.label_model(c, bold, cx, cy - 20, str(number), 2.9, "#ffffff")


def kitchen_module(c, regular, rect, label, fill=KITCHEN, size=3.4):
    x1, y1, x2, y2 = rect
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, fill, "#6e5a34", 0.20)
    base.label_model(c, regular, (x1 + x2) / 2, (y1 + y2) / 2 - 10, label, size, "#5b4827")


def draw_kitchen(c, regular, bold):
    kitchen_module(c, regular, CORNER_PREP, "УГОЛ /\nПОДГОТОВКА 600", "#ead7ae", 3.2)
    kitchen_module(c, regular, HOB, "ВАРКА 600\nЯЩИКИ СНИЗУ", "#e7ca90", 3.2)
    kitchen_module(c, regular, SINK_PREP, "", "#f1d6a0")
    kitchen_module(c, regular, TALL_PENAL, "", "#d7b775")
    kitchen_module(c, regular, FRIDGE, "ХОЛОДИЛЬНИК 600", "#e7ca90", 3.5)
    kitchen_module(c, regular, PANTRY, "ВЫКАТ /\nХРАН. 350", "#ead5a8", 3.05)
    kitchen_module(c, regular, DISHWASHER, "ПММ 600", "#f1d6a0", 3.8)
    kitchen_module(c, regular, CORNER_FILLER, "ДОБОР 50", "#f8efd8", 2.6)

    # Zone 3: user-requested visual hierarchy: preparation above, sink below.
    base.label_model(c, regular, 1500, 3380, "ПОДГОТОВКА", 3.65, "#5b4827")
    c.setStrokeColor(HexColor("#58717d")); c.setLineWidth(0.22 * mm)
    c.circle(base.qx(1500) * mm, base.qy(3150) * mm, base.p(150) * mm, fill=0, stroke=1)
    base.label_model(c, regular, 1500, 2965, "МОЙКА НИЖЕ", 3.45, "#58717d")

    # Zone 2: induction hob in the former sink module.
    c.setStrokeColor(HexColor("#65523a")); c.setLineWidth(0.14 * mm)
    for cx, cy in ((780, 3070), (1020, 3070), (780, 3310), (1020, 3310)):
        c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(72) * mm, fill=0, stroke=1)

    # Zone 4: tall unit is drawn as a footprint and labelled by vertical functions.
    base.model_line(c, 1800, 3100, 2400, 3100, "#80653c", 0.16)
    base.model_line(c, 1800, 3300, 2400, 3300, "#80653c", 0.16)
    base.label_model(c, bold, 2100, 3415, "ПЕНАЛ 600", 3.6, "#5b4827")
    base.label_model(c, regular, 2100, 3235, "СВЧ", 3.5, "#5b4827")
    base.label_model(c, regular, 2100, 3040, "ДУХОВКА", 3.35, "#5b4827")
    base.label_model(c, regular, 2100, 2945, "ХРАНЕНИЕ", 3.1, "#5b4827")
    base.label_model(c, bold, 1200, 3440, "Г-КУХНЯ: 2400 + 1600 ФРОНТОВ", 4.8, "#5b4827")


def draw_table(c, regular, bold):
    x1, y1, x2, y2 = OLD_TABLE
    c.setFillColor(HexColor("#eef1f3")); c.setStrokeColor(HexColor("#9aa3aa")); c.setLineWidth(0.18 * mm); c.setDash(1.1 * mm, 0.75 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=1, stroke=1); c.setDash()
    base.label_model(c, regular, 1700, 1510, "TV-007: стол был здесь", 3.0, "#7b858d")
    x1, y1, x2, y2 = TABLE
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 42)
    base.model_line(c, x1, y1 + 700, x2, y1 + 700, "#6b8665", 0.14)
    base.label_model(c, bold, 2300, 1570, "СТОЛ CJ196", 4.7, "#405d3c")
    base.label_model(c, regular, 2300, 1435, "800 x 1400; сдвиг вправо +600", 3.45, "#405d3c")


def draw_sofa_desk_tv(c, regular, bold):
    base.draw_sofa(c, regular, 2430, 2500, 2000, 1000, "down")
    base.label_model(c, bold, 3430, 2595, "ДИВАН-КРОВАТЬ 2000x1000", 3.15, "#544943")
    base.model_box(c, DESK[0], DESK[1], DESK[2] - DESK[0], DESK[3] - DESK[1], WORK, "#4e7589", 0.24, 38)
    base.label_model(c, regular, 5110, 3310, "РМ 1200x600", 3.2, "#2e5b70")
    dashed_rect(c, DESK_CHAIR, BLUE, 0.24)
    base.label_model(c, regular, 4810, 2400, "подход к креслу 600", 3.3, BLUE)
    base.draw_tv(c, regular, TV_MEDIA[0], TV_MEDIA[1], TV_MEDIA[2] - TV_MEDIA[0], TV_MEDIA[3] - TV_MEDIA[1], "bottom")
    base.label_model(c, regular, 3410, 315, "ТВ + МЕДИА 1600x300", 3.1, "#624a59")


def draw_constraints(c, regular):
    dashed_rect(c, (600, 1300, 1900, 2200), GREEN, 0.30)
    base.label_model(c, regular, 1250, 2060, "1300: фасады левой ветви -> стол", 3.6, GREEN)
    # Only the true overlap of the table and upper kitchen is shown; it must not cover the sofa.
    dashed_rect(c, (1900, 2200, 2400, 2900), ORANGE, 0.30)
    base.label_model(c, regular, 2140, 2570, "700 до верхней кухни", 3.15, ORANGE)
    dashed_rect(c, O1_ROUTE, GOOD, 0.25)
    base.label_model(c, regular, 5255, 2380, "O1 1600 -> терраса", 3.4, GOOD)
    dashed_rect(c, ROUTE_900_REFERENCE, BAD, 0.34)
    base.label_model(c, regular, 3650, 670, "12: D2 -> O1 900, стол пересекает полосу на 450", 3.35, BAD)


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(0), base.qx(2400), base.qy(2860), "2400")
    base.dim_v(c, regular, base.qx(630), base.qy(1300), base.qy(2900), "1600", "#5b4827")
    base.dim_h(c, regular, base.qx(600), base.qx(1900), base.qy(1240), "1300", GREEN)
    base.dim_v(c, regular, base.qx(1850), base.qy(2200), base.qy(2900), "700", ORANGE)
    base.dim_h(c, regular, base.qx(1900), base.qx(2700), base.qy(760), "800", "#405d3c")
    base.dim_v(c, regular, base.qx(2740), base.qy(800), base.qy(2200), "1400", "#405d3c")
    base.dim_h(c, regular, base.qx(1300), base.qx(1900), base.qy(740), "+600", GREEN)
    base.dim_v(c, regular, base.qx(4200), base.qy(2200), base.qy(2500), "300", "#544943")
    base.dim_h(c, regular, base.qx(2610), base.qx(4210), base.qy(340), "1600")


def draw_numbers(c, regular, bold):
    for num, cx, cy, fill in ZONE_MARKERS:
        zone_marker(c, bold, num, cx, cy, fill)


def sidebar(c, regular, bold):
    x, w = 270, 136
    panel(c, bold, x, 206, w, 62, "ЗОНЫ 1-6", PALE_GREEN)
    yy = 252
    for line in (
        "1 угол / подготовка",
        "2 варка / ящики",
        "3 подготовка + мойка",
        "4 пенал: СВЧ / духовка / хран.",
        "5 ПММ 600",
        "6 выкатное хранение 350",
    ):
        text(c, regular, x + 4, yy, 5.1, line); yy -= 6.0

    panel(c, bold, x, 138, w, 58, "ЗОНЫ 7-12", PALE_BLUE)
    yy = 183
    for line in (
        "7 холодильник 600",
        "8 стол CJ196",
        "9 диван-кровать",
        "10 рабочее место",
        "11 ТВ / медиа",
        "12 контроль D2 -> O1",
    ):
        text(c, regular, x + 4, yy, 5.1, line); yy -= 6.0

    panel(c, bold, x, 65, w, 65, "ВАЖНАЯ ЛОГИКА", PALE_ORANGE)
    yy = 112
    for line in (
        "- зона 1 остаётся главной",
        "  чистой подготовкой 600",
        "- зона 3: сверху подготовка,",
        "  внутри/ниже мойка",
        "- вода, слив и вентканал",
        "  подтвердить до заказа",
    ):
        text(c, regular, x + 4, yy, 5.1, line, "#80582d"); yy -= 6.0


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13.2, "TV-009 - НУМЕРОВАННАЯ СХЕМА КУХНИ")
    text(c, regular, 14, 274, 4.9,
         "Все номера - функциональные зоны для обсуждения. Масштаб: B01 5710x3500; не заказ до привязки инженерии.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-009 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-009 / НУМЕРОВАННАЯ КУХНЯ")
    previous.draw_d2_guard(c, regular)
    draw_kitchen(c, regular, bold)
    draw_constraints(c, regular)
    draw_table(c, regular, bold)
    draw_sofa_desk_tv(c, regular, bold)
    dimensions(c, regular)
    draw_numbers(c, regular, bold)
    sidebar(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-009 - нумерованная схема кухни")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-009 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
