# -*- coding: utf-8 -*-
"""TV-003: transforming dining table by the kitchen in room B01.

This is a two-mode, scale-accurate test — not a purchase drawing.  All
coordinates are model millimetres and are printed at M 1:25.  The everyday
mode stores a 1500x700 folding table as 1500x350, deliberately folded away
from the kitchen.  The dinner mode reveals the real chair/path compromise.
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
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-003_стол-трансформер_кухня_день-гости_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-003_стол-трансформер_кухня_день-гости_М1-25.pdf"

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
DAY_ROUTE = (0, 350, 5710, 1250)       # 900-mm D2 -> O1 strip
DINNER_ROUTE = (0, 350, 5710, 1150)    # 800-mm strip with chairs pushed in
O1_ROUTE = (4810, 350, 5710, 2450)
DESK_APPROACH = (4510, 1250, 5110, 2490)

# The top kitchen is short because the sofa and the workstation occupy the
# remaining upper wall.  A former 1600-mm return cannot stay with this table:
# its fronts would be blocked.  The 550-mm return shown here is the largest
# compact end return that stays clear of the expanded table plus a 50-mm
# technical gap; final module/SKU must still be checked on site.
KITCHEN_TOP = (0, 2900, 2310, 3500)
SHORT_RETURN = (0, 2350, 600, 2900)
SHORT_RETURN_FRONT = (600, 2350, 1200, 2900)
FORMER_FULL_RETURN = (0, 1300, 600, 2900)
FORMER_FULL_RETURN_FRONT = (600, 1300, 1200, 2900)

SOFA = (2410, 2500, 4410, 3500)
DESK = (4510, 2900, 5710, 3500)
TV_MEDIA = (2610, 0, 4210, 300)
DESK_CHAIR = (4510, 2490, 5110, 3110)

# Hinge/leaf convention for the test: when folded, the kitchen-side leaf is
# folded away from the kitchen, reducing the depth from 700 to 350 mm.
TABLE_FOLDED = (600, 1600, 2100, 1950)
TABLE_OPEN = (600, 1600, 2100, 2300)

# In the day state seating is parked in the free right-hand niche.  That is
# essential: the stated 900-mm route is true only while chairs are stored.
FOLDED_CHAIRS_PARKED = (2100, 1500, 2550, 1950)
CHILD_CHAIR_PARKED = (2100, 1950, 2550, 2400)

# Dinner state: two adults use the lower long side and a child uses the end.
# The chair-pull envelope, which enters the route while people sit, is drawn
# as a warning instead of being treated as free circulation.
CHAIR_1 = (1200, 1150, 1700, 1600)
CHAIR_2 = (1700, 1150, 2200, 1600)
CHILD_CHAIR = (2100, 1700, 2550, 2150)
CHAIR_PULL_ZONE = (1200, 550, 2200, 1150)


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def assert_in_room(name: str, rect: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    if not (0 <= x1 < x2 <= ROOM[2] and 0 <= y1 < y2 <= ROOM[3]):
        raise AssertionError(f"{name} outside B01: {rect}")


def validate_mode(name: str, items: dict[str, tuple[int, int, int, int]], route: tuple[int, int, int, int]) -> None:
    for item_name, rect in items.items():
        assert_in_room(item_name, rect)
        if overlap(rect, D2_GUARD):
            raise AssertionError(f"{name}: {item_name} enters D2 guard")
    assert_in_room("desk_chair", DESK_CHAIR)
    for left, right in combinations(items, 2):
        if overlap(items[left], items[right]):
            raise AssertionError(f"{name}: fixed overlap {left}/{right}")
    if overlap(DESK_CHAIR, SOFA):
        raise AssertionError(f"{name}: desk chair overlaps sofa")
    for item_name, rect in items.items():
        if overlap(rect, route):
            raise AssertionError(f"{name}: {item_name} blocks stated D2->O1 route")
        if overlap(rect, O1_ROUTE):
            raise AssertionError(f"{name}: {item_name} blocks O1 route")
        if item_name != "desk" and overlap(rect, DESK_APPROACH):
            raise AssertionError(f"{name}: {item_name} blocks desk approach")


def validate_geometry() -> None:
    common = {
        "kitchen_top": KITCHEN_TOP,
        "short_return": SHORT_RETURN,
        "sofa": SOFA,
        "desk": DESK,
        "tv_media": TV_MEDIA,
    }
    day = {
        **common,
        "table_folded": TABLE_FOLDED,
        "folded_chairs_parked": FOLDED_CHAIRS_PARKED,
        "child_chair_parked": CHILD_CHAIR_PARKED,
    }
    dinner = {
        **common,
        "table_open": TABLE_OPEN,
        "chair_1": CHAIR_1,
        "chair_2": CHAIR_2,
        "child_chair": CHILD_CHAIR,
    }
    validate_mode("day", day, DAY_ROUTE)
    validate_mode("dinner", dinner, DINNER_ROUTE)
    assert_in_room("chair_pull_zone", CHAIR_PULL_ZONE)
    if not overlap(CHAIR_PULL_ZONE, DINNER_ROUTE):
        raise AssertionError("dinner: chair pull zone must expose the path conflict")
    if overlap(SHORT_RETURN_FRONT, TABLE_FOLDED) or overlap(SHORT_RETURN_FRONT, TABLE_OPEN):
        raise AssertionError("short return fronts are blocked by the table")
    if overlap(FORMER_FULL_RETURN_FRONT, TABLE_FOLDED) is False:
        raise AssertionError("former full return conflict should remain visible")
    assert TABLE_FOLDED[2] - TABLE_FOLDED[0] == 1500
    assert TABLE_FOLDED[3] - TABLE_FOLDED[1] == 350
    assert TABLE_OPEN[2] - TABLE_OPEN[0] == 1500
    assert TABLE_OPEN[3] - TABLE_OPEN[1] == 700
    assert KITCHEN_TOP[1] - TABLE_FOLDED[3] == 950
    assert KITCHEN_TOP[1] - TABLE_OPEN[3] == 600
    assert DAY_ROUTE[3] - DAY_ROUTE[1] == 900
    assert DINNER_ROUTE[3] - DINNER_ROUTE[1] == 800
    assert SHORT_RETURN[1] - TABLE_OPEN[3] == 50
    print("PASS TV-003: B01 bounds; folded 1500x350 / route 900; open 1500x700 / static route 800; chair pull conflict visible")


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
    text(c, bold, x + 4, y + h - 7, 4.25, title)


def page_frame(c, regular, bold, title, subtitle, page_no):
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13.4, title)
    text(c, regular, 14, 274, 5.0, subtitle, MUTED)
    text(c, regular, 404, 14, 3.8, f"TV-003 | лист {page_no}/2 | М 1:25", MUTED, right=True)


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
    base.label_model(c, bold, 1155, 3440, "КУХНЯ 2310 мм + КОРОТКИЙ ВОЗВРАТ", 3.2, "#5b4827")

    # The original full 1600-mm leg is a ghost, explicitly rejected rather
    # than silently removed from the scheme.
    x1, y1, x2, y2 = FORMER_FULL_RETURN
    c.setFillColor(HexColor("#f1f3f5")); c.setStrokeColor(HexColor(GRAY)); c.setLineWidth(0.20 * mm)
    c.setDash(1.1 * mm, 0.75 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=1, stroke=1)
    c.setDash()
    base.label_model(c, regular, 300, 1885, "была Г-ветвь 1600", 2.25, "#6b7280")
    base.label_model(c, regular, 300, 1765, "не активна", 2.25, "#6b7280")

    # Shortened return is the only active L element.  Draw it after the ghost
    # so the final plan unmistakably distinguishes it from the former leg.
    # It ends before the table's y=2300 edge, so its fronts remain reachable.
    kitchen_module(c, regular, 0, 2350, 600, 550, "КОР. ВОЗВРАТ")
    base.label_model(c, regular, 300, 2545, "600x550", 2.5, "#5b4827")


def draw_sofa(c, regular, bold):
    base.draw_sofa(c, regular, 2410, 2500, 2000, 1000, "down")
    base.label_model(c, bold, 3410, 2595, "ДИВАН-КРОВАТЬ 2000x1000", 3.1, "#544943")
    base.label_model(c, regular, 3410, 2450, "верхняя стена; до РМ 100", 2.65, "#544943")


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


def draw_day_table(c, regular, bold):
    x1, y1, x2, y2 = TABLE_FOLDED
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 42)
    base.model_line(c, x1 + 750, y1, x1 + 750, y2, "#6b8665", 0.14)
    base.label_model(c, bold, 1350, 1765, "СТОЛ СЛОЖЕН", 3.0, "#405d3c")
    base.label_model(c, regular, 1350, 1645, "1500x350; лист от кухни", 2.55, "#405d3c")
    base.model_box(c, 2100, 1500, 450, 450, "#f6f2ed", "#6d6258", 0.18, 55)
    base.model_line(c, 2160, 1560, 2490, 1890, "#6d6258", 0.18)
    base.model_line(c, 2160, 1890, 2490, 1560, "#6d6258", 0.18)
    base.label_model(c, regular, 2325, 1740, "2 стула", 2.3, "#6d6258")
    base.label_model(c, regular, 2325, 1635, "сложены", 2.3, "#6d6258")
    base.draw_chair(c, 2100, 1950, 450, 450, facing="left", fill="#f6f2ed")
    base.label_model(c, regular, 2325, 2170, "детский", 2.25, "#6d6258")
    base.label_model(c, regular, 2325, 2065, "стул паркуется", 2.25, "#6d6258")


def draw_dinner_table(c, regular, bold):
    x1, y1, x2, y2 = TABLE_OPEN
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 45)
    base.model_line(c, x1 + 750, y1, x1 + 750, y2, "#6b8665", 0.14)
    for rect, facing in ((CHAIR_1, "up"), (CHAIR_2, "up"), (CHILD_CHAIR, "left")):
        cx1, cy1, cx2, cy2 = rect
        base.draw_chair(c, cx1, cy1, cx2 - cx1, cy2 - cy1, facing=facing)
    base.label_model(c, bold, 1350, 1975, "СТОЛ ОТКРЫТ", 3.1, "#405d3c")
    base.label_model(c, regular, 1350, 1845, "1500x700; 2 взрослых + ребёнок", 2.55, "#405d3c")
    x1, y1, x2, y2 = CHAIR_PULL_ZONE
    c.setStrokeColor(HexColor(BAD)); c.setLineWidth(0.28 * mm); c.setDash(1.25 * mm, 0.8 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, 1700, 780, "при посадке: D2 -> O1 временно занят", 2.45, BAD)


def dimensions(c, regular, mode):
    table = TABLE_FOLDED if mode == "day" else TABLE_OPEN
    table_depth = 350 if mode == "day" else 700
    kitchen_clear = 950 if mode == "day" else 600
    route = DAY_ROUTE if mode == "day" else DINNER_ROUTE
    base.dim_h(c, regular, base.qx(0), base.qx(2310), base.qy(2860), "2310")
    base.dim_h(c, regular, base.qx(600), base.qx(2100), base.qy(table[3] + 65), "1500")
    base.dim_v(c, regular, base.qx(2175), base.qy(table[1]), base.qy(table[3]), str(table_depth), "#405d3c")
    base.dim_v(c, regular, base.qx(2270), base.qy(table[3]), base.qy(2900), str(kitchen_clear), ORANGE)
    base.dim_v(c, regular, base.qx(4450), base.qy(route[1]), base.qy(route[3]), str(route[3] - route[1]), GOOD)
    base.dim_v(c, regular, base.qx(2350), base.qy(TABLE_OPEN[3]), base.qy(SHORT_RETURN[1]), "50", GRAY)
    base.dim_h(c, regular, base.qx(2410), base.qx(4410), base.qy(2460), "2000")
    base.dim_h(c, regular, base.qx(4510), base.qx(5710), base.qy(2860), "1200")
    base.dim_h(c, regular, base.qx(2610), base.qx(4210), base.qy(340), "1600")
    base.dim_v(c, regular, base.qx(4240), base.qy(0), base.qy(300), "300")


def sidebar_day(c, regular, bold):
    panel(c, bold, 255, 210, 151, 58, "ДЕНЬ: РЕАЛЬНО СВОБОДНЫЙ ПРОХОД", PALE_GREEN)
    yy = 254
    for line in (
        "- B01: 5710x3500 мм",
        "- стол сложен: 1500x350 мм",
        "- до фронтов кухни: 950 мм",
        "- D2 -> O1: непрерывно 900 мм",
        "- стулья не стоят в проходе",
    ):
        text(c, regular, 259, yy, 3.9, line, INK); yy -= 5.8
    panel(c, bold, 255, 138, 151, 62, "ЧЕСТНОЕ УСЛОВИЕ 900 ММ", PALE_ORANGE)
    yy = 185
    for paragraph in (
        "900 мм — это режим хранения: два складных стула и детский стул припаркованы справа.",
        "Чтобы сесть за сложенный стол, стул снова меняет маршрут. Это не постоянная посадка семьи.",
    ):
        yy = wrapped(c, regular, 259, yy, 3.85, paragraph, 53, INK, 4.95, "-") - 1.1
    panel(c, bold, 255, 68, 151, 56, "КУХНЯ И ХРАНЕНИЕ", PALE_BLUE)
    yy = 108
    for line in (
        "Активно: верхняя линия 2310",
        "и короткий возврат 600x550.",
        "Полная Г-ветвь 600x1600",
        "не остаётся: стол закрыл бы",
        "её фасады. SKU не выбран.",
    ):
        text(c, regular, 259, yy, 3.85, line, INK); yy -= 5.3


def sidebar_dinner(c, regular, bold):
    panel(c, bold, 255, 210, 151, 58, "УЖИН: СТОЛ ОТКРЫТ", PALE_ORANGE)
    yy = 254
    for line in (
        "- стол: 1500x700 мм",
        "- до фронтов кухни: 600 мм",
        "- 2 взрослых + ребёнок",
        "- D2 -> O1: 800 мм статически",
        "- при посадке полоса занята",
    ):
        text(c, regular, 259, yy, 3.9, line, INK); yy -= 5.8
    panel(c, bold, 255, 138, 151, 62, "ЧТО ПРОИСХОДИТ В УЖИН", PALE_RED)
    yy = 185
    for paragraph in (
        "600 мм перед кухней — для сервировки, а не одновременной готовки и сидящих людей.",
        "Когда стулья выдвинуты, красная зона закрывает маршрут D2 -> O1. Готовить сначала, садиться после.",
    ):
        yy = wrapped(c, regular, 259, yy, 3.85, paragraph, 53, BAD, 4.95, "-") - 1.1
    panel(c, bold, 255, 68, 151, 56, "ПРОВЕРИТЬ ДО ПОКУПКИ", PALE_BLUE)
    yy = 108
    for line in (
        "1. Направление складывания",
        "   листа — от кухни.",
        "2. Фактические ножки/царга.",
        "3. Сложенные стулья и детский",
        "   стул именно в этом габарите.",
        "4. Фасады короткого возврата.",
    ):
        text(c, regular, 259, yy, 3.85, line, INK); yy -= 5.3


def draw_page(c, regular, bold, mode):
    if mode == "day":
        page_frame(c, regular, bold,
                   "TV-003 — СТОЛ У КУХНИ: ДЕНЬ / ПОЛОВИНА СЛОЖЕНА",
                   "Масштабный режим хранения: стол 1500x350, кухонный проход 950 и маршрут D2 -> O1 900 мм.", 1)
    else:
        page_frame(c, regular, bold,
                   "TV-003 — СТОЛ У КУХНИ: УЖИН / ПОЛНОСТЬЮ ОТКРЫТ",
                   "Масштабный режим ужина: стол 1500x700. Ограничения маршрута показаны, а не скрыты.", 2)
    base.draw_room_shell(c, regular, bold, "TV-003 / СТОЛ-ТРАНСФОРМЕР")
    draw_d2_guard(c, regular)
    if mode == "day":
        route_rect(c, regular, DAY_ROUTE, "D2 -> O1: 900 мм, стол и стулья сложены", (3500, 720), GOOD, 0.36)
        route_rect(c, regular, O1_ROUTE, "900 к O1", (5255, 2380), GOOD, 0.30)
        route_rect(c, regular, DESK_APPROACH, "подход к креслу 600", (4810, 2400), BLUE, 0.30)
    else:
        route_rect(c, regular, DAY_ROUTE, "бывшие 900: стулья заходят на 100", (3350, 1180), ORANGE, 0.24)
        route_rect(c, regular, DINNER_ROUTE, "D2 -> O1: 800 мм, стулья задвинуты", (3450, 720), GOOD, 0.36)
        route_rect(c, regular, O1_ROUTE, "900 к O1", (5255, 2380), GOOD, 0.30)
        route_rect(c, regular, DESK_APPROACH, "подход к креслу 600", (4810, 2400), BLUE, 0.30)
    draw_kitchen(c, regular, bold)
    if mode == "day":
        draw_day_table(c, regular, bold)
        sidebar_day(c, regular, bold)
    else:
        draw_dinner_table(c, regular, bold)
        sidebar_dinner(c, regular, bold)
    draw_sofa(c, regular, bold)
    draw_desk(c, regular)
    draw_tv(c, regular, bold)
    dimensions(c, regular, mode)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-003 — стол-трансформер у кухни: день и ужин")
    c.setAuthor("Codex")
    draw_page(c, regular, bold, "day")
    draw_page(c, regular, bold, "dinner")
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-003 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
