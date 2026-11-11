# -*- coding: utf-8 -*-
"""TV-011 rev.2 - audit of the user-supplied coordinate layout.

The sheet deliberately preserves every submitted coordinate rather than fixing
the layout silently.  It distinguishes physical contour clearance from an
ergonomic / operating conflict, and adds a material direction sampled only as
a visual reference from the supplied kitchen photograph.
"""
from __future__ import annotations

import math
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_tv010_swap_sink_dishwasher as v10
import build_tv009_numbered_kitchen_modules as v9


ROOT = Path(__file__).resolve().parents[1]
REF_IMAGE = ROOT / "кухня гостинная" / "Референсы" / "photo_2026-08-29_15-34-15.jpg"
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-011_rev02_проверка_координат_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-011_rev02_проверка_координат_и_материалы_М1-25.pdf"

base = v9.base
INK = v9.INK
MUTED = v9.MUTED
GOOD = base.GOOD
BAD = v9.BAD
ORANGE = v9.ORANGE
BLUE = v9.BLUE

# Visual direction from the supplied reference photo, not a vendor specification.
FACADE = "#d9d0c2"
FACADE_TALL = "#d0c5b6"
FACADE_LIGHT = "#e1d9cd"
COUNTERTOP = "#f3f0e8"
BACKSPLASH = "#ecebe5"
VEIN = "#96948d"
BRASS = "#a98545"
APPLIANCE = "#1e1e1d"
PALE_RED = "#fff1ef"
PALE_ORANGE = "#fff6e8"
PALE_BLUE = "#eef7fb"
PALE_GREEN = "#eff8f1"

ROOM = (0, 0, 5710, 3500)
TOP_WORK = (0, 2200, 2400, 2900)
LEFT_WORK = (600, 1300, 1300, 2900)
PMM_DOOR = (1200, 2300, 1800, 2900)
D2_GUARD = (0, 0, 1200, 1300)
ROUTE_D2_O1 = (0, 350, 5710, 1250)
O1_ROUTE = (4810, 350, 5710, 2450)

# Coordinates supplied by the user, in millimetres from B01 lower-left corner.
TABLE_BBOX = (1200, 1300, 2050, 2150)
TABLE_CENTER = (1625, 1725)
TABLE_RADIUS = 425
CHAIRS = {
    "8A": (1850, 2150, 2250, 2550, "down"),
    "8B": (1000, 2150, 1400, 2550, "down"),
    "8C": (1900, 950, 2300, 1350, "up"),
    "8D": (950, 950, 1350, 1350, "up"),
}
SOFA = (2450, 2500, 4450, 3500)
DESK = (4500, 2900, 5700, 3500)
TV_MEDIA = (2700, 0, 4300, 300)

MARKERS = (
    (1, 100, 3420, "#7b5f2c"), (2, 700, 3420, "#7b5f2c"),
    (3, 1300, 3420, "#58717d"), (4, 1900, 3420, "#6b5230"),
    (5, 100, 2780, "#58717d"), (6, 100, 2180, "#7b5f2c"),
    (7, 100, 1780, "#7b5f2c"), (8, 1625, 1725, "#4e6c49"),
    (9, 4300, 3400, "#70585b"), (10, 5580, 3400, "#2f6e8d"),
    (11, 4250, 150, "#70585b"), (12, 4300, 600, "#b54a3b"),
)


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def intersection(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> tuple[int, int, int, int] | None:
    if not overlap(a, b):
        return None
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def circle_to_rect_gap(rect: tuple[int, int, int, int]) -> float:
    """Shortest signed gap from table circumference to a chair rectangle."""
    x1, y1, x2, y2 = rect
    px = min(max(TABLE_CENTER[0], x1), x2)
    py = min(max(TABLE_CENTER[1], y1), y2)
    return math.hypot(TABLE_CENTER[0] - px, TABLE_CENTER[1] - py) - TABLE_RADIUS


def validate_geometry() -> None:
    """Verify the submitted coordinates and their actual consequences."""
    v10.validate_geometry()
    assert TABLE_BBOX == (1200, 1300, 2050, 2150)
    assert TABLE_CENTER == (1625, 1725) and TABLE_RADIUS == 425
    assert TABLE_BBOX[2] - TABLE_BBOX[0] == 850
    assert TABLE_BBOX[3] - TABLE_BBOX[1] == 850
    assert TABLE_BBOX[0] - 600 == 600  # left facade, not 700
    assert 2200 - TABLE_BBOX[3] == 50
    assert 2900 - TABLE_BBOX[3] == 750
    assert intersection(CHAIRS["8A"][:4], TOP_WORK) == (1850, 2200, 2250, 2550)
    assert intersection(CHAIRS["8B"][:4], TOP_WORK) == (1000, 2200, 1400, 2550)
    assert intersection(CHAIRS["8B"][:4], LEFT_WORK) == (1000, 2150, 1300, 2550)
    assert intersection(CHAIRS["8B"][:4], PMM_DOOR) == (1200, 2300, 1400, 2550)
    assert intersection(CHAIRS["8C"][:4], ROUTE_D2_O1) == (1900, 950, 2300, 1250)
    assert intersection(CHAIRS["8D"][:4], ROUTE_D2_O1) == (950, 950, 1350, 1250)
    assert intersection(CHAIRS["8D"][:4], D2_GUARD) == (950, 950, 1200, 1300)
    assert math.isclose(circle_to_rect_gap(CHAIRS["8A"][:4]), 55.884, abs_tol=0.1)
    assert math.isclose(circle_to_rect_gap(CHAIRS["8B"][:4]), 55.884, abs_tol=0.1)
    assert math.isclose(circle_to_rect_gap(CHAIRS["8C"][:4]), 40.027, abs_tol=0.1)
    assert math.isclose(circle_to_rect_gap(CHAIRS["8D"][:4]), 40.027, abs_tol=0.1)
    assert REF_IMAGE.exists()
    print("PASS TV-011 rev.2: submitted coordinates reproduced; operational conflicts measured and labelled")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def panel(c, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7.5, 6.4, title)


def dashed_rect(c, rect, color, width=0.28):
    v9.dashed_rect(c, rect, color, width)


def label_lines(c, font, cx, cy, lines, size, color, step=70):
    offset = (len(lines) - 1) * step / 2
    for index, line in enumerate(lines):
        base.label_model(c, font, cx, cy + offset - index * step, line, size, color)


def kitchen_module(c, regular, rect, lines, fill=FACADE, text_color="#5b5146", size=4.4):
    x1, y1, x2, y2 = rect
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, fill, "#8f8476", 0.20)
    if lines:
        label_lines(c, regular, (x1 + x2) / 2, (y1 + y2) / 2, lines, size, text_color)


def marble_band(c, rect):
    x1, y1, x2, y2 = rect
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, COUNTERTOP, "#b8b4aa", 0.15)
    width, height = x2 - x1, y2 - y1
    for offset in (0.16, 0.48, 0.77):
        sx = x1 + width * offset
        base.model_line(c, sx - 65, y1 + height * 0.18, sx + 85, y1 + height * 0.82, VEIN, 0.12)


def draw_kitchen_material(c, regular, bold):
    """TV-010 functional positions, now rendered in reference-photo direction."""
    kitchen_module(c, regular, v10.CORNER_PREP, ("УГОЛ", "ПОДГОТОВКА"))
    kitchen_module(c, regular, v10.HOB, ("ВАРКА", "ЯЩИКИ"))
    kitchen_module(c, bold, v10.DISHWASHER_TOP, ("ПММ", "600"), FACADE_LIGHT, size=5.1)
    kitchen_module(c, regular, v10.TALL_PENAL, ("ПЕНАЛ", "СВЧ / ДУХОВКА"), FACADE_TALL, size=4.25)
    kitchen_module(c, regular, v10.SINK_LEFT, ("МОЙКА", "600"), FACADE_LIGHT, size=4.9)
    kitchen_module(c, regular, v10.PANTRY, ("ВЫКАТ", "350"), FACADE, size=4.5)
    kitchen_module(c, regular, v10.FRIDGE, ("ХОЛОДИЛЬНИК", "600"), FACADE_TALL, size=4.15)
    kitchen_module(c, regular, v10.CORNER_FILLER, ("ДОБОР 50",), "#e9e2d7", size=3.0)

    # Warm white polished countertop in plan and marble-like backsplash strips.
    marble_band(c, (0, 2900, 2400, 2955))
    marble_band(c, (545, 1300, 600, 2900))
    base.model_box(c, 0, 3445, 2400, 55, BACKSPLASH, "#b8b4aa", 0.13)
    for sx in (250, 880, 1510, 2090):
        base.model_line(c, sx - 85, 3450, sx + 100, 3490, VEIN, 0.10)
    base.model_box(c, 0, 1300, 55, 1600, BACKSPLASH, "#b8b4aa", 0.13)
    for sy in (1490, 2020, 2530):
        base.model_line(c, 5, sy - 55, 48, sy + 70, VEIN, 0.10)

    # Black hob and brass sink/faucet accents from the reference.
    c.setFillColor(HexColor(APPLIANCE)); c.setStrokeColor(HexColor("#111111")); c.setLineWidth(0.16 * mm)
    c.roundRect(base.qx(680) * mm, base.qy(3000) * mm, base.p(440) * mm, base.p(400) * mm, base.p(24) * mm, fill=1, stroke=1)
    c.setStrokeColor(HexColor("#5a534a")); c.setLineWidth(0.13 * mm)
    for cx, cy in ((790, 3090), (1010, 3090), (790, 3310), (1010, 3310)):
        c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(70) * mm, fill=0, stroke=1)
    c.setStrokeColor(HexColor(BRASS)); c.setLineWidth(0.24 * mm)
    c.rect(base.qx(130) * mm, base.qy(2380) * mm, base.p(330) * mm, base.p(330) * mm, fill=0, stroke=1)
    c.arc(base.qx(280) * mm, base.qy(2620) * mm, base.qx(450) * mm, base.qy(2820) * mm, 0, 180)
    base.model_line(c, 300, 2680, 300, 2820, BRASS, 0.22)

    base.model_line(c, 0, 2895, 2400, 2895, BRASS, 0.18)
    base.model_line(c, 605, 1300, 605, 2900, BRASS, 0.18)
    base.label_model(c, bold, 1200, 3440, "Г-КУХНЯ 2400 + 1600; МАТЕРИАЛЫ ПО РЕФЕРЕНСУ", 4.7, "#5b5146")


def draw_table_and_chairs(c, regular, bold):
    c.setFillColor(HexColor("#efe9dd")); c.setStrokeColor(HexColor("#6e685e")); c.setLineWidth(0.28 * mm)
    c.circle(base.qx(TABLE_CENTER[0]) * mm, base.qy(TABLE_CENTER[1]) * mm, base.p(TABLE_RADIUS) * mm, fill=1, stroke=1)
    c.setStrokeColor(HexColor(VEIN)); c.setLineWidth(0.13 * mm)
    base.model_line(c, 1390, 1510, 1835, 1930, VEIN, 0.13)
    base.model_line(c, 1470, 1390, 1940, 1870, VEIN, 0.13)
    base.label_model(c, bold, TABLE_CENTER[0], 1785, "8 СТОЛ Ø850", 5.4, "#5a554d")
    base.label_model(c, regular, TABLE_CENTER[0], 1645, "КООРД. x1200 y1300", 3.3, "#5a554d")

    colors = {"8A": ORANGE, "8B": BAD, "8C": ORANGE, "8D": BAD}
    for marker, (x1, y1, x2, y2, facing) in CHAIRS.items():
        base.draw_chair(c, x1, y1, x2 - x1, y2 - y1, facing=facing, fill="#f6f2ed")
        dashed_rect(c, (x1, y1, x2, y2), colors[marker], 0.26)
        base.label_model(c, bold, (x1 + x2) / 2, (y1 + y2) / 2 - 18, marker, 4.8, "#5b554e")


def draw_other_furniture(c, regular, bold):
    base.draw_sofa(c, regular, SOFA[0], SOFA[1], SOFA[2] - SOFA[0], SOFA[3] - SOFA[1], "down")
    base.label_model(c, bold, 3450, 2595, "9 ДИВАН-КРОВАТЬ 2000x1000", 3.05, "#544943")
    base.model_box(c, DESK[0], DESK[1], DESK[2] - DESK[0], DESK[3] - DESK[1], "#dbeaf2", "#4e7589", 0.24, 38)
    base.label_model(c, regular, 5100, 3310, "10 РМ 1200x600", 3.1, "#2e5b70")
    base.draw_tv(c, regular, TV_MEDIA[0], TV_MEDIA[1], TV_MEDIA[2] - TV_MEDIA[0], TV_MEDIA[3] - TV_MEDIA[1], "bottom")
    base.label_model(c, regular, 3500, 315, "11 ТВ / МЕДИА 1600x300", 3.0, "#624a59")


def fill_conflict(c, rect, fill, border):
    x1, y1, x2, y2 = rect
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, fill, border, 0.14)


def draw_constraints(c, regular):
    dashed_rect(c, TOP_WORK, ORANGE, 0.26)
    dashed_rect(c, LEFT_WORK, ORANGE, 0.26)
    dashed_rect(c, PMM_DOOR, BAD, 0.30)
    dashed_rect(c, ROUTE_D2_O1, BAD, 0.30)
    dashed_rect(c, D2_GUARD, "#c2771b", 0.28)
    dashed_rect(c, O1_ROUTE, GOOD, 0.22)

    # Measured collision areas, intentionally shown before furniture hides their interiors.
    for rect in (
        intersection(CHAIRS["8A"][:4], TOP_WORK),
        intersection(CHAIRS["8B"][:4], TOP_WORK),
        intersection(CHAIRS["8B"][:4], LEFT_WORK),
        intersection(CHAIRS["8B"][:4], PMM_DOOR),
        intersection(CHAIRS["8C"][:4], ROUTE_D2_O1),
        intersection(CHAIRS["8D"][:4], ROUTE_D2_O1),
        intersection(CHAIRS["8D"][:4], D2_GUARD),
    ):
        if rect:
            fill_conflict(c, rect, PALE_RED, "#cf6b5c")

    base.label_model(c, regular, 1200, 2765, "8A/8B: 350 В РАБОЧЕМ ПОЯСЕ 700", 3.6, ORANGE)
    base.label_model(c, regular, 980, 2050, "СТОЛ: 600 ДО ФАСАДА; НУЖНО 700", 3.45, BAD)
    label_lines(c, regular, 1500, 2540, ("8B x ДВЕРЦА ПММ", "ПЕРЕСЕЧЕНИЕ 200x250"), 3.5, BAD, 62)
    base.label_model(c, regular, 4200, 770, "8C/8D: МАРШРУТ 900 СУЖЕН ДО 600", 3.5, BAD)
    label_lines(c, regular, 610, 720, ("8D В КОНТРОЛЕ D2", "250x350; ОТКРЫВАНИЕ УТОЧНИТЬ"), 3.1, "#b36c1f", 55)
    base.label_model(c, regular, 5260, 2220, "ПРОХОД К O1: 900 (НЕ ШИРИНА ПРОЁМА)", 3.3, GOOD)


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(TABLE_BBOX[0]), base.qx(TABLE_BBOX[2]), base.qy(855), "Ø850", "#5a554d")
    base.dim_h(c, regular, base.qx(600), base.qx(1200), base.qy(1235), "600", BAD)
    base.dim_v(c, regular, base.qx(2085), base.qy(2150), base.qy(2200), "50", ORANGE)
    base.dim_h(c, regular, base.qx(1200), base.qx(1400), base.qy(2265), "200", BAD)
    base.dim_v(c, regular, base.qx(1435), base.qy(2300), base.qy(2550), "250", BAD)
    text(c, regular, 900, 1255, 3.25, "ДО ЛЕВОГО ФАСАДА (НЕ 700)", BAD, center=True)
    text(c, regular, 2110, 2180, 3.2, "ДО ПОЛОСЫ 700", ORANGE)


def zone_marker(c, bold, number, cx, cy, fill):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(white); c.setLineWidth(0.18 * mm)
    c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(60) * mm, fill=1, stroke=1)
    base.label_model(c, bold, cx, cy - 22, str(number), 3.1, "#ffffff")


def draw_numbers(c, regular, bold):
    for number, cx, cy, fill in MARKERS:
        zone_marker(c, bold, number, cx, cy, fill)


def material_swatch(c, x, y, w, h, fill, label, marble=False):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor("#a7a39a")); c.setLineWidth(0.15 * mm)
    c.roundRect(x * mm, y * mm, w * mm, h * mm, 1.2 * mm, fill=1, stroke=1)
    if marble:
        c.setStrokeColor(HexColor(VEIN)); c.setLineWidth(0.18 * mm)
        c.line((x + 1) * mm, (y + 2) * mm, (x + w - 1) * mm, (y + h - 2) * mm)
        c.line((x + w * 0.35) * mm, (y + 1) * mm, (x + w * 0.7) * mm, (y + h - 1) * mm)
    text(c, base.fonts()[0], x + w + 2, y + h / 2 - 1.5, 4.1, label)


def draw_reference_materials(c, regular, bold):
    x, w = 270, 136
    panel(c, bold, x, 211, w, 57, "МАТЕРИАЛЫ ИЗ РЕФЕРЕНСА", PALE_GREEN)
    if REF_IMAGE.exists():
        c.drawImage(str(REF_IMAGE), (x + 4) * mm, 217 * mm, 28 * mm, 43 * mm, preserveAspectRatio=True, anchor="c")
    text(c, regular, x + 36, 255, 4.6, "тёплый матовый фасад", "#5b5146")
    material_swatch(c, x + 36, 246, 12, 6, FACADE, "#D9D0C2")
    text(c, regular, x + 36, 236, 4.6, "столешница: светлый", "#5b5146")
    material_swatch(c, x + 36, 227, 12, 6, COUNTERTOP, "#F3F0E8", marble=True)
    text(c, regular, x + 36, 217, 4.6, "фартук: белый мрамор", "#5b5146")

    panel(c, bold, x, 143, w, 62, "ВЕРДИКТ ПО КООРДИНАТАМ", PALE_RED)
    y = 190
    for line, color in (
        ("FAIL: не единый рабочий режим", BAD),
        ("8B x дверца ПММ: 200x250", BAD),
        ("8D x контроль D2: 250x350", BAD),
        ("8A/8B в рабочей зоне 700", ORANGE),
        ("8C/8D режут D2 -> O1 до 600", ORANGE),
        ("стол -> фасад слева: 600", ORANGE),
    ):
        text(c, regular, x + 4, y, 4.65, line, color); y -= 6.2

    panel(c, bold, x, 65, w, 70, "ЧЕСТНЫЙ ВЫВОД", PALE_BLUE)
    y = 119
    for line in (
        "Круг Ø850 и стулья не касаются",
        "физически: 40-56 мм до круга.",
        "Но это не запас для посадки.",
        "4 гостя возможны только как",
        "отдельный режим: без готовки,",
        "ПММ и свободного маршрута.",
        "Цвет - ориентир; образцы",
        "проверить при вашем свете.",
    ):
        text(c, regular, x + 4, y, 4.65, line, "#365260"); y -= 6.05


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 12.4, "TV-011 rev.2 - ПРОВЕРКА ВАШИХ КООРДИНАТ + МАТЕРИАЛЫ")
    text(c, regular, 14, 274, 4.9,
         "B01 5710x3500; М 1:25. Координаты пользователя не сдвигались. Красное - эксплуатационный конфликт, оранжевое - эргономика.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-011 rev.2 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-011 rev.2 / ВАШИ КООРДИНАТЫ")
    draw_constraints(c, regular)
    draw_kitchen_material(c, regular, bold)
    draw_table_and_chairs(c, regular, bold)
    draw_other_furniture(c, regular, bold)
    dimensions(c, regular)
    draw_numbers(c, regular, bold)
    draw_reference_materials(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-011 rev.2 - проверка координат и материалы")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-011 rev.2 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
