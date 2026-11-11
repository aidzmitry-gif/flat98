# -*- coding: utf-8 -*-
"""TV-012 - horizontal dining table in the kitchen zone, based on the photo.

This sheet preserves the TV-010 kitchen and places CJ196 1400x800 along X.
Two chairs are shown on the D2/TV side, as in the reference photo.  Their
seated envelopes intentionally occupy the D2->O1 control route.  The plan is
honest about the other consequence: with the current TV-010 dishwasher in
zone 3, its door cannot be operated while this full table is in place.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_tv010_swap_sink_dishwasher as v10


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-012_стол_в_кухне_фото_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-012_стол_в_кухне_стулья_М1-25.pdf"

base = v10.v9.base
v9 = v10.v9
previous = v9.previous

INK = v9.INK
MUTED = v9.MUTED
DINING = v9.DINING
GOOD = v9.GOOD
BAD = v9.BAD
ORANGE = v9.ORANGE
BLUE = v9.BLUE
PALE_GREEN = v9.PALE_GREEN
PALE_BLUE = v9.PALE_BLUE
PALE_ORANGE = v9.PALE_ORANGE
PALE_RED = "#fff1ef"

ROOM = v9.ROOM
TABLE = (1300, 1400, 2700, 2200)  # 1400 x 800; long side as in the photo.
CHAIRS = (
    (1450, 1000, 1850, 1400),
    (2150, 1000, 2550, 1400),
)
# 600 mm from table edge to the back of the occupied/slide-in seat zone.
SEAT_ENVELOPES = (
    (1450, 800, 1850, 1400),
    (2150, 800, 2550, 1400),
)
DISHWASHER_DOOR = (1200, 2300, 1800, 2900)
ROUTE = v9.ROUTE_900_REFERENCE


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def intersection(a: tuple[int, int, int, int], b: tuple[int, int, int, int]):
    if not overlap(a, b):
        return None
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def validate_geometry() -> None:
    v10.validate_geometry()
    assert TABLE[2] - TABLE[0] == 1400
    assert TABLE[3] - TABLE[1] == 800
    assert TABLE[0] - v9.LEFT_KITCHEN[2] == 700
    assert v9.TOP_KITCHEN[1] - TABLE[3] == 700
    assert TABLE[1] - ROUTE[3] == 150
    assert v9.SOFA[1] - TABLE[3] == 300
    assert not overlap(TABLE, v9.TOP_KITCHEN)
    assert not overlap(TABLE, v9.LEFT_KITCHEN)
    assert not overlap(TABLE, v9.SOFA)
    for chair, seat in zip(CHAIRS, SEAT_ENVELOPES, strict=True):
        assert chair[2] - chair[0] == 400 and chair[3] - chair[1] == 400
        assert seat[2] - seat[0] == 400 and seat[3] - seat[1] == 600
        assert seat[0] == chair[0] and seat[2] == chair[2] and seat[3] == chair[3]
        assert overlap(chair, ROUTE)
        assert overlap(seat, ROUTE)
        assert not overlap(chair, previous.D2_GUARD)
        assert not overlap(chair, v9.SOFA)
    assert intersection(SEAT_ENVELOPES[0], ROUTE) == (1450, 800, 1850, 1250)
    assert intersection(SEAT_ENVELOPES[1], ROUTE) == (2150, 800, 2550, 1250)
    # The table is physically clear of the door outline by only 100 mm.
    assert TABLE[3] == 2200 and DISHWASHER_DOOR[1] == 2300
    assert DISHWASHER_DOOR[1] - TABLE[3] == 100
    assert not overlap(TABLE, DISHWASHER_DOOR)
    assert {number for number, *_ in v9.ZONE_MARKERS} == set(range(1, 13))
    print("PASS TV-012: photo-style 1400x800 table, 700 left/top, two chairs, route and dishwasher trade-offs shown")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def panel(c, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7.5, 6.5, title)


def dashed_rect(c, rect, color, width=0.28):
    v9.dashed_rect(c, rect, color, width)


def draw_table_and_chairs(c, regular, bold):
    x1, y1, x2, y2 = TABLE
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.26, 38)
    base.model_line(c, 2000, y1, 2000, y2, "#6b8665", 0.14)
    base.label_model(c, bold, 2000, 1820, "СТОЛ CJ196 1400x800", 4.35, "#405d3c")
    base.label_model(c, regular, 2000, 1685, "В КУХОННОЙ ЗОНЕ; длинная сторона вдоль кухни", 3.05, "#405d3c")

    for seat in SEAT_ENVELOPES:
        dashed_rect(c, seat, BLUE, 0.22)
    for chair in CHAIRS:
        base.draw_chair(c, chair[0], chair[1], chair[2] - chair[0], chair[3] - chair[1], facing="up")
    base.label_model(c, regular, 2000, 890, "2 СТУЛА 400x400; ЗОНА ПОСАДКИ 600", 3.15, BLUE)
    base.label_model(c, regular, 2000, 760, "СТОРОНА D2 / ТВ - не сторона кухни", 2.9, BLUE)


def draw_constraints(c, regular):
    # 700 mm at the table's left side to the face of the 600-mm left branch.
    dashed_rect(c, (600, 1400, 1300, 2200), GOOD, 0.30)
    base.label_model(c, regular, 950, 1870, "700: фасады\nлевой ветви -> стол", 3.3, GOOD)
    # 700-mm kitchen work band in front of the top run.
    dashed_rect(c, (1300, 2200, 2700, 2900), ORANGE, 0.30)
    base.label_model(c, regular, 2450, 2540, "700 до верхней кухни", 3.25, ORANGE)
    # Show the control route and the portion occupied by seated chairs.
    dashed_rect(c, ROUTE, BAD, 0.34)
    base.label_model(c, regular, 3650, 670, "D2 -> O1 900: при посадке стулья занимают 450", 3.15, BAD)
    # Dishwasher door and compact 100-mm gap to the table.
    dashed_rect(c, DISHWASHER_DOOR, "#b54a3b", 0.30)
    base.label_model(c, regular, 1500, 2560, "ПММ №3: дверца 600\nв открытом виде", 3.05, "#b54a3b")
    base.label_model(c, regular, 1500, 2395, "до стола только 100", 3.05, "#b54a3b")
    base.dim_v(c, regular, base.qx(1850), base.qy(2200), base.qy(2300), "100", "#b54a3b")


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(TABLE[0]), base.qx(TABLE[2]), base.qy(700), "1400", "#405d3c")
    base.dim_v(c, regular, base.qx(2740), base.qy(TABLE[1]), base.qy(TABLE[3]), "800", "#405d3c")
    base.dim_h(c, regular, base.qx(600), base.qx(1300), base.qy(1330), "700", GOOD)
    base.dim_v(c, regular, base.qx(2740), base.qy(2200), base.qy(2900), "700", ORANGE)
    base.dim_v(c, regular, base.qx(2580), base.qy(800), base.qy(1400), "600", BLUE)
    base.dim_v(c, regular, base.qx(2620), base.qy(1000), base.qy(1400), "400", BLUE)


def sidebar(c, regular, bold):
    x, w = 270, 136
    panel(c, bold, x, 206, w, 62, "КАК НА ФОТО", PALE_GREEN)
    yy = 252
    for line in (
        "стол CJ196 1400x800",
        "x=1300..2700; y=1400..2200",
        "700 до левой ветви",
        "700 до верхней кухни",
        "2 стула со стороны D2/ТВ",
        "не со стороны кухни",
    ):
        text(c, regular, x + 4, yy, 5.0, line); yy -= 6.0

    panel(c, bold, x, 138, w, 58, "ПОСАДКА", PALE_BLUE)
    yy = 183
    for line in (
        "стул: 400x400",
        "зона посадки: 600",
        "2 взрослых места - комфортно",
        "проход D2->O1 в ужин",
        "временно занят на 450",
        "это не постоянный проход",
    ):
        text(c, regular, x + 4, yy, 5.0, line); yy -= 6.0

    panel(c, bold, x, 65, w, 65, "ВАЖНО", PALE_ORANGE)
    yy = 112
    for line in (
        "ПММ №3: дверца откроется,",
        "но до стола только 100",
        "при таком зазоре",
        "загрузка ПММ невозможна",
        "вода, слив, вентканал",
        "подтвердить до заказа",
    ):
        text(c, regular, x + 4, yy, 5.0, line, "#80582d"); yy -= 6.0


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 12.9, "TV-012 - СТОЛ В КУХНЕ, КАК НА ФОТО")
    text(c, regular, 14, 274, 4.8,
         "Масштаб: B01 5710x3500. Стулья показаны в занятом положении; не заказ до привязки инженерии.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-012 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-012 / СТОЛ В КУХНЕ")
    previous.draw_d2_guard(c, regular)
    v10.draw_kitchen(c, regular, bold)
    v9.draw_sofa_desk_tv(c, regular, bold)
    draw_constraints(c, regular)
    draw_table_and_chairs(c, regular, bold)
    dimensions(c, regular)
    v9.draw_numbers(c, regular, bold)
    sidebar(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-012 - стол в кухне, как на фото")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-012 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
