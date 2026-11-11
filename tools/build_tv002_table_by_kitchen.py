# -*- coding: utf-8 -*-
"""TV-002: conditional kitchen-side dining table for B01.

This is deliberately a comparison sheet, not a replacement for TV-001.
All coordinates are model millimetres; the drawing is printed at M 1:25.
The table is allowed to reduce the former 900-mm D2->O1 strip to 800 mm
only while the two dining chairs are pushed in.  The dining action itself
blocks that route, so the trade-off is shown rather than hidden.
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
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-002_стол-у-кухни_проход-800_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-002_стол-у-кухни_проход-800_М1-25.pdf"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
LOUNGE = base.LOUNGE
WORK = base.WORK
MEDIA = base.MEDIA
GOOD = base.GOOD
BAD = base.BAD
BLUE = "#2f6e8d"
ORANGE = "#ad6800"
GRAY = "#aab4bc"
PALE_BLUE = "#eef7fb"
PALE_GREEN = "#eff8f1"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"

ROOM = (0, 0, 5710, 3500)
D2_GUARD = (0, 0, 1200, 1300)

# TV-001 route, shown in orange as the former benchmark.  TV-002 intentionally
# retains only the lower 800 mm while the dining chairs are pushed in.
OLD_MAIN_ROUTE = (0, 350, 5710, 1250)
STATIC_MAIN_ROUTE = (0, 350, 5710, 1150)
O1_ROUTE = (4810, 350, 5710, 2450)
DESK_APPROACH = (4510, 1250, 5110, 2490)

# The active kitchen in TV-002 is a straight 2310-mm row.  The old 1600-mm
# left L-leg is deliberately drawn as a ghost because the table would make its
# fronts unusable; retaining it would be a false layout claim.
KITCHEN_TOP = (0, 2900, 2310, 3500)
RETIRED_LEFT_LEG = (0, 1300, 600, 2900)

FIXED = {
    "kitchen_top": KITCHEN_TOP,
    "sofa": (2410, 2500, 4410, 3500),
    "desk": (4510, 2900, 5710, 3500),
    "tv_media": (2610, 0, 4210, 300),
    # Full-size dining top: length horizontal, depth vertical.
    "table": (600, 1600, 2100, 2300),
    # Two adult chairs are pushed into the lower long side of the table.
    "chair_1": (1200, 1150, 1700, 1600),
    "chair_2": (1700, 1150, 2200, 1600),
    # A child chair takes the right end, outside the lower route.
    "child_chair": (2100, 1700, 2550, 2150),
}

# When the adults sit down, their chairs are pulled toward D2; that dynamic
# envelope is intentionally incompatible with D2->O1 and is highlighted red.
CHAIR_PULL_ZONE = (1200, 550, 2200, 1150)
DESK_CHAIR = (4510, 2490, 5110, 3110)


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def assert_in_room(name: str, rect: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    if not (0 <= x1 < x2 <= ROOM[2] and 0 <= y1 < y2 <= ROOM[3]):
        raise AssertionError(f"{name} outside B01: {rect}")


def validate_geometry() -> None:
    for name, rect in FIXED.items():
        assert_in_room(name, rect)
        if overlap(rect, D2_GUARD):
            raise AssertionError(f"{name} enters D2 guard: {rect}")
    assert_in_room("desk_chair", DESK_CHAIR)
    assert_in_room("chair_pull_zone", CHAIR_PULL_ZONE)

    for left, right in combinations(FIXED, 2):
        if overlap(FIXED[left], FIXED[right]):
            raise AssertionError(f"fixed overlap {left}/{right}")
    if overlap(DESK_CHAIR, FIXED["sofa"]):
        raise AssertionError("desk chair overlaps sofa")

    # The explicitly reduced 800-mm path must remain clear in the static mode.
    for name, rect in FIXED.items():
        if overlap(rect, STATIC_MAIN_ROUTE):
            raise AssertionError(f"{name} blocks static 800-mm D2->O1 route")
        if overlap(rect, O1_ROUTE):
            raise AssertionError(f"{name} blocks O1 vertical route")
        if name != "desk" and overlap(rect, DESK_APPROACH):
            raise AssertionError(f"{name} blocks desk approach")

    assert FIXED["chair_1"][1] < OLD_MAIN_ROUTE[3]
    assert FIXED["chair_1"][1] == STATIC_MAIN_ROUTE[3]
    assert OLD_MAIN_ROUTE[3] - STATIC_MAIN_ROUTE[3] == 100
    assert STATIC_MAIN_ROUTE[3] - STATIC_MAIN_ROUTE[1] == 800
    assert overlap(CHAIR_PULL_ZONE, STATIC_MAIN_ROUTE)
    assert FIXED["table"][2] - FIXED["table"][0] == 1500
    assert FIXED["table"][3] - FIXED["table"][1] == 700
    assert KITCHEN_TOP[1] - FIXED["table"][3] == 600
    # This is the revealed conflict: in TV-001 the table touches the face of
    # the left L-leg, so that leg must be omitted/relocated in TV-002.
    assert FIXED["table"][0] == RETIRED_LEFT_LEG[2]
    print("PASS TV-002: B01 bounds; 800-mm static route; table 1500x700; explicit chair-pull conflict")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=None, bullet=None):
    leading = leading or size * 1.28
    for index, row in enumerate(base.wrap(value, width)):
        prefix = (bullet + " ") if bullet and index == 0 else ("  " if bullet else "")
        text(c, font, x, y, size, prefix + row, color)
        y -= leading
    return y


def panel(c, regular, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7, 4.3, title)


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13.8, "TV-002 - ТЕСТ: СТОЛ У КУХНИ, ПРОХОД 800 ММ")
    text(c, regular, 14, 274, 5.0,
         "Эпизодический режим ужина, не базовая планировка. Реальный масштаб; мебель - габариты до SKU.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-002 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_d2_guard(c, regular):
    x1, y1, x2, y2 = D2_GUARD
    c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.32 * mm); c.setDash(1.7 * mm, 0.9 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, 600, 490, "D2 GUARD 1200x1300", 2.6, ORANGE)


def route_rect(c, regular, rect, label, at, color, width=0.30):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width * mm); c.setDash(1.5 * mm, 0.85 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, at[0], at[1], label, 2.75, color)


def kitchen_module(c, regular, x, y, w, h, label):
    base.model_box(c, x, y, w, h, KITCHEN, "#6e5a34", 0.20)
    base.label_model(c, regular, x + w / 2, y + h / 2 - 10, label, 2.7, "#5b4827")


def draw_kitchen(c, regular, bold):
    for x, w, label in ((0, 600, "ХОЛ./ПЕНАЛ"), (600, 600, "МОЙКА/ПММ"),
                        (1200, 600, "ВАРКА"), (1800, 450, "ЯЩИКИ")):
        kitchen_module(c, regular, x, 2900, w, 600, label)
    base.model_box(c, 2250, 2900, 60, 600, KITCHEN, "#6e5a34", 0.20)
    base.model_box(c, 730, 3050, 340, 240, "#edf2f2", "#617377", 0.12, 22)
    base.model_line(c, 900, 3290, 900, 3370, "#617377", 0.16)
    c.setStrokeColor(HexColor("#6e5a34")); c.setLineWidth(0.14 * mm)
    for x, y in ((1380, 3065), (1600, 3065), (1380, 3280), (1600, 3280)):
        c.circle(base.qx(x) * mm, base.qy(y) * mm, base.p(65) * mm, fill=0, stroke=1)
    base.label_model(c, bold, 1155, 3440, "ПРЯМАЯ КУХНЯ 2310 мм", 3.4, "#6e5a34")

    # Ghost the TV-001 L-leg: it cannot remain active with this dining table.
    x1, y1, x2, y2 = RETIRED_LEFT_LEG
    c.setFillColor(HexColor("#f1f3f5")); c.setStrokeColor(HexColor(GRAY)); c.setLineWidth(0.22 * mm)
    c.setDash(1.1 * mm, 0.75 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=1, stroke=1)
    c.setDash()
    base.label_model(c, bold, 300, 2150, "ЛЕВАЯ ВЕТВЬ", 2.6, "#6b7280")
    base.label_model(c, regular, 300, 2010, "TV-001: убрать", 2.4, "#6b7280")
    base.label_model(c, regular, 300, 1870, "1600 фронтов", 2.4, "#6b7280")


def draw_sofa(c, regular, bold):
    base.draw_sofa(c, regular, 2410, 2500, 2000, 1000, "down")
    base.label_model(c, bold, 3410, 2595, "ДИВАН-КРОВАТЬ 2000x1000", 3.1, "#544943")
    base.label_model(c, regular, 3410, 2450, "верхняя стена; зазор до РМ 100", 2.7, "#544943")


def draw_desk(c, regular):
    base.model_box(c, 4510, 2900, 1200, 600, WORK, "#4e7589", 0.24, 38)
    base.model_line(c, 5110, 2970, 5110, 3430, "#6a94a8", 0.14)
    base.model_box(c, 4640, 3160, 340, 110, "#f3f7f8", "#4e7589", 0.12, 12)
    base.label_model(c, regular, 4810, 3310, "РМ 1200x600", 3.4, "#2e5b70")
    x1, y1, x2, y2 = DESK_CHAIR
    c.setStrokeColor(HexColor(BLUE)); c.setLineWidth(0.28 * mm); c.setDash(1.6 * mm, 0.9 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.draw_chair(c, 4560, 2600, 500, 500, facing="up")
    base.label_model(c, regular, 4810, 2495, "кресло max 600x620", 2.5, BLUE)


def draw_tv(c, regular, bold):
    base.draw_tv(c, regular, 2610, 0, 1600, 300, "bottom")
    base.label_model(c, bold, 3410, 315, "ТВ / МЕДИА 1600x300", 2.9, "#624a59")


def draw_table(c, regular, bold):
    x1, y1, x2, y2 = FIXED["table"]
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 45)
    base.model_line(c, x1 + 750, y1, x1 + 750, y2, "#6b8665", 0.14)
    for key, facing in (("chair_1", "up"), ("chair_2", "up"), ("child_chair", "left")):
        cx1, cy1, cx2, cy2 = FIXED[key]
        base.draw_chair(c, cx1, cy1, cx2 - cx1, cy2 - cy1, facing=facing)
    base.label_model(c, bold, 1350, 1975, "ОБЕДЕННЫЙ СТОЛ", 3.1, "#405d3c")
    base.label_model(c, regular, 1350, 1845, "1500x700; 2 взрослых + ребёнок", 2.55, "#405d3c")

    # Dynamic chair pull is shown as a red exclusion, not as a usable route.
    x1, y1, x2, y2 = CHAIR_PULL_ZONE
    c.setStrokeColor(HexColor(BAD)); c.setLineWidth(0.28 * mm); c.setDash(1.25 * mm, 0.8 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, 1700, 780, "выдвижение стульев: D2 -> O1 временно занят", 2.5, BAD)


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(0), base.qx(2310), base.qy(2860), "2310")
    base.dim_h(c, regular, base.qx(600), base.qx(2100), base.qy(2370), "1500")
    base.dim_v(c, regular, base.qx(2175), base.qy(1600), base.qy(2300), "700")
    base.dim_v(c, regular, base.qx(2270), base.qy(2300), base.qy(2900), "600", ORANGE)
    base.dim_v(c, regular, base.qx(2350), base.qy(1150), base.qy(1250), "100", BAD)
    base.dim_v(c, regular, base.qx(4450), base.qy(350), base.qy(1150), "800", GOOD)
    base.dim_v(c, regular, base.qx(2350), base.qy(1300), base.qy(2900), "1600", GRAY)
    base.dim_h(c, regular, base.qx(2410), base.qx(4410), base.qy(2460), "2000")
    base.dim_h(c, regular, base.qx(2610), base.qx(4210), base.qy(340), "1600")
    base.dim_v(c, regular, base.qx(4240), base.qy(0), base.qy(300), "300")


def sidebar(c, regular, bold):
    panel(c, regular, bold, 255, 210, 151, 58, "ЧТО ПОКАЗАНО В МАСШТАБЕ", PALE_BLUE)
    yy = 254
    for line in (
        "- B01: 5710x3500 мм",
        "- стол: 1500x700 мм",
        "- стулья задвинуты: D2 -> O1 800 мм",
        "- при посадке: маршрут временно занят",
        "- O1 и подход к РМ сохранены",
    ):
        text(c, regular, 259, yy, 3.9, line, INK); yy -= 5.8

    panel(c, regular, bold, 255, 134, 151, 66, "КОМПРОМИСС КУХНЯ / СТОЛ", PALE_ORANGE)
    yy = 184
    for para in (
        "Стол стоит в кухонной зоне: сверху до кухонного фронта остаётся 600 мм. Это режим сервировки и ужина, а не одновременной готовки.",
        "Левую ветвь Г-кухни TV-001 (1600 мм фронтов) нужно убрать или полностью перепроектировать: иначе стол блокирует фасады.",
    ):
        yy = wrapped(c, regular, 259, yy, 3.85, para, 53, INK, 4.95, "-") - 1.4

    panel(c, regular, bold, 255, 68, 151, 56, "НЕ БАЗОВАЯ ПЛАНИРОВКА", PALE_RED)
    yy = 108
    for line in (
        "800 мм - только при задвинутых",
        "двух стульях. При посадке",
        "полоса D2 -> O1 закрыта.",
        "Сначала готовить, потом садиться.",
        "Не заказывать без SKU-проверки.",
    ):
        text(c, regular, 259, yy, 3.85, line, BAD); yy -= 5.3


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-002 / СТОЛ У КУХНИ")
    draw_d2_guard(c, regular)
    route_rect(c, regular, OLD_MAIN_ROUTE, "бывшая полоса 900: стулья заходят на 100", (3300, 1180), ORANGE, 0.24)
    route_rect(c, regular, STATIC_MAIN_ROUTE, "D2 -> O1: 800 мм, стулья задвинуты", (3450, 720), GOOD, 0.36)
    route_rect(c, regular, O1_ROUTE, "900 к O1", (5255, 2380), GOOD, 0.30)
    route_rect(c, regular, DESK_APPROACH, "подход к креслу 600", (4810, 2400), BLUE, 0.30)
    draw_kitchen(c, regular, bold)
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
    c.setTitle("TV-002 - стол у кухни, проход 800 мм")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-002 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
