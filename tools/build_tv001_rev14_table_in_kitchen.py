# -*- coding: utf-8 -*-
"""TV-001 rev15: put the real 1400x800 table in the kitchen zone.

The first sheet reproduces the requested visual topology and exposes its real
conflict with the 1600-mm left kitchen branch.  The second sheet is the smallest
buildable correction: keep the 2400-mm upper run, shorten the left branch to
700 mm (600-mm refrigerator plus 100-mm blind filler), and keep the table/route
coordinates unchanged.  The third sheet verifies day, dinner, guest, and night
scenarios.

All model coordinates are millimetres in B01 5710x3500.  The PDF is M 1:25.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base


ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "output" / "pdf" / "TV-001_rev15_стол-в-зоне-кухни_сценарии.pdf"
PREVIEW_PREFIX = ROOT / "output" / "preview" / "TV-001_rev15_стол-в-зоне-кухни"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
LOUNGE = base.LOUNGE
WORK = base.WORK
MEDIA = base.MEDIA
GOOD = base.GOOD
BAD = base.BAD
ORANGE = "#ad6800"
BLUE = "#2f6e8d"
PALE_BLUE = "#eef7fb"
PALE_GREEN = "#eff8f1"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"

ROOM = (0, 0, 5710, 3500)
D2_GUARD = (0, 0, 1200, 1300)
MAIN_ROUTE = (0, 350, 5710, 1250)
O1_ROUTE = (4810, 350, 5710, 2450)
DESK_APPROACH = (4510, 1250, 5110, 2490)

KITCHEN_TOP = (0, 2900, 2400, 3500)
KITCHEN_LEFT_FULL = (0, 1300, 600, 2900)
KITCHEN_LEFT_SHORT = (0, 2200, 600, 2900)
KITCHEN_LEFT_FILLER = (0, 2200, 600, 2300)
KITCHEN_LEFT_FRIDGE = (0, 2300, 600, 2900)
TOP_WORK = (0, 2200, 2400, 2900)
LEFT_WORK_FULL = (600, 1300, 1300, 2900)
LEFT_WORK_SHORT = (600, 2200, 1300, 2900)

SOFA = (2430, 2500, 4430, 3500)
DESK = (4510, 2900, 5710, 3500)
TV = (2610, 0, 4210, 300)

# Exact kitchen-side interpretation of the user's visual:
# - 70 mm from the face of the left kitchen branch (x=600 -> x=670)
# - 700 mm from the face of the upper run (y=2200 -> y=2900)
# - 150 mm above the protected 900-mm route (y=1250 -> y=1400)
TABLE = (670, 1400, 2070, 2200)
CHAIRS_SEATED = (
    # Shifted right so the unknown D2 swing/guard stays untouched.
    (1200, 1000, 1600, 1400),
    (1670, 1000, 2070, 1400),
)
CHAIRS_STOWED = (
    (1200, 1420, 1600, 1780),
    (1670, 1420, 2070, 1780),
)

GUEST_TABLE = (2730, 1700, 4130, 2500)
GUEST_CHAIRS = (
    (2880, 1300, 3280, 1700),
    (3580, 1300, 3980, 1700),
)
GUEST_CHAIR_PULL = (
    (2880, 700, 3280, 1700),
    (3580, 700, 3980, 1700),
)
SOFA_OPEN = (2430, 2100, 4430, 3500)


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def intersection(a: tuple[int, int, int, int], b: tuple[int, int, int, int]):
    if not overlap(a, b):
        return None
    return (max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3]))


def assert_in_room(name: str, rect: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    if not (0 <= x1 < x2 <= ROOM[2] and 0 <= y1 < y2 <= ROOM[3]):
        raise AssertionError(f"{name} outside B01: {rect}")


def validate_geometry() -> None:
    for name, rect in {
        "kitchen_top": KITCHEN_TOP,
        "kitchen_left_full": KITCHEN_LEFT_FULL,
        "kitchen_left_short": KITCHEN_LEFT_SHORT,
        "kitchen_left_filler": KITCHEN_LEFT_FILLER,
        "kitchen_left_fridge": KITCHEN_LEFT_FRIDGE,
        "sofa": SOFA,
        "desk": DESK,
        "tv": TV,
        "table": TABLE,
        "top_work": TOP_WORK,
        "left_work_full": LEFT_WORK_FULL,
        "left_work_short": LEFT_WORK_SHORT,
        "guest_table": GUEST_TABLE,
        "sofa_open": SOFA_OPEN,
    }.items():
        assert_in_room(name, rect)

    assert TABLE[2] - TABLE[0] == 1400
    assert TABLE[3] - TABLE[1] == 800
    assert TABLE[0] - KITCHEN_LEFT_FULL[2] == 70
    assert KITCHEN_TOP[1] - TABLE[3] == 700
    assert TABLE[1] - MAIN_ROUTE[3] == 150
    assert not overlap(TABLE, MAIN_ROUTE)
    assert not overlap(TABLE, O1_ROUTE)
    assert not overlap(TABLE, TOP_WORK)
    assert not overlap(TABLE, LEFT_WORK_SHORT)

    conflict = intersection(TABLE, LEFT_WORK_FULL)
    assert conflict == (670, 1400, 1300, 2200)
    assert (conflict[2] - conflict[0]) * (conflict[3] - conflict[1]) == 504000

    for index, chair in enumerate(CHAIRS_SEATED, 1):
        assert_in_room(f"chair_seated_{index}", chair)
        assert overlap(chair, MAIN_ROUTE)
        assert not overlap(chair, D2_GUARD)
    for index, chair in enumerate(CHAIRS_STOWED, 1):
        assert_in_room(f"chair_stowed_{index}", chair)
        assert not overlap(chair, MAIN_ROUTE)

    assert KITCHEN_LEFT_SHORT[3] - KITCHEN_LEFT_SHORT[1] == 700
    assert KITCHEN_LEFT_FRIDGE[1] - TABLE[3] == 100
    assert KITCHEN_LEFT_FILLER[3] - KITCHEN_LEFT_FILLER[1] == 100
    assert KITCHEN_LEFT_FRIDGE[3] - KITCHEN_LEFT_FRIDGE[1] == 600
    assert KITCHEN_LEFT_FILLER[3] == KITCHEN_LEFT_FRIDGE[1]

    assert GUEST_TABLE[0] + GUEST_TABLE[2] == SOFA[0] + SOFA[2]
    assert GUEST_TABLE[3] == SOFA[1]
    assert GUEST_TABLE[2] - GUEST_TABLE[0] == 1400
    assert GUEST_TABLE[3] - GUEST_TABLE[1] == 800
    for forbidden in (MAIN_ROUTE, O1_ROUTE, DESK_APPROACH, TOP_WORK, LEFT_WORK_SHORT):
        assert not overlap(GUEST_TABLE, forbidden)
    for index, chair in enumerate(GUEST_CHAIRS, 1):
        assert_in_room(f"guest_chair_{index}", chair)
        assert not overlap(chair, MAIN_ROUTE)
        assert not overlap(chair, D2_GUARD)
        assert not overlap(chair, O1_ROUTE)
        assert not overlap(chair, DESK_APPROACH)
    for index, pull in enumerate(GUEST_CHAIR_PULL, 1):
        assert_in_room(f"guest_pull_{index}", pull)
        assert overlap(pull, MAIN_ROUTE)
        assert not overlap(pull, D2_GUARD)

    assert not overlap(TABLE, SOFA_OPEN)
    assert SOFA_OPEN[0] - TABLE[2] == 360
    assert SOFA_OPEN[1] - MAIN_ROUTE[3] == 850
    assert O1_ROUTE[0] - SOFA_OPEN[2] == 380
    for forbidden in (MAIN_ROUTE, O1_ROUTE, DESK_APPROACH, D2_GUARD):
        assert not overlap(SOFA_OPEN, forbidden)
    print("PASS rev15: table at kitchen; 70/700/150; fridge offset 100 via blind filler; day/2/guest/night scenarios verified")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=None, bullet=None):
    leading = leading or size * 1.3
    for index, row in enumerate(base.wrap(value, width)):
        prefix = (bullet + " ") if bullet and index == 0 else ("  " if bullet else "")
        text(c, font, x, y, size, prefix + row, color)
        y -= leading
    return y


def panel(c, regular, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7, 4.3, title)


def page_frame(c, regular, bold, title, subtitle, page_no):
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 12.4, title)
    text(c, regular, 14, 274, 4.8, subtitle, MUTED)
    text(c, regular, 404, 14, 3.8, f"TV-001 rev15 | лист {page_no}/3 | М 1:25", MUTED, right=True)


def route_rect(c, regular, rect, label, at, color=GOOD, width=0.30, fill=None):
    x1, y1, x2, y2 = rect
    if fill:
        c.saveState()
        c.setFillColor(HexColor(fill))
        if hasattr(c, "setFillAlpha"):
            c.setFillAlpha(0.28)
        c.rect(base.qx(x1) * mm, base.qy(y1) * mm,
               base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=1, stroke=0)
        c.restoreState()
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width * mm); c.setDash(1.6 * mm, 0.9 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm,
           base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()
    base.label_model(c, regular, at[0], at[1], label, 2.65, color)


def draw_d2_guard(c, regular):
    x1, y1, x2, y2 = D2_GUARD
    c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.30 * mm); c.setDash(1.5 * mm, 0.9 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm,
           base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()
    base.label_model(c, regular, 600, 500, "D2 GUARD 1200x1300", 2.55, ORANGE)


def kitchen_module(c, regular, x, y, w, h, label, size=2.5):
    base.model_box(c, x, y, w, h, KITCHEN, "#6e5a34", 0.20)
    base.label_model(c, regular, x + w / 2, y + h / 2 - 10, label, size, "#5b4827")


def draw_kitchen(c, regular, bold, short_left=False):
    modules = (
        (0, 600, "МОЙКА"),
        (600, 450, "ПММ 450"),
        (1050, 600, "ВАРКА/ДУХ."),
        (1650, 600, "СВЧ/ДУХ."),
        (2250, 150, "ДОБОР"),
    )
    for x, w, label in modules:
        kitchen_module(c, regular, x, 2900, w, 600, label, 2.35 if w < 300 else 2.5)
    base.label_model(c, bold, 1200, 3440, "ВЕРХНЯЯ ВЕТВЬ 2400", 3.15, "#6e5a34")

    if short_left:
        kitchen_module(c, regular, 0, 2200, 600, 100, "ДОБОР 100", 2.1)
        kitchen_module(c, regular, 0, 2300, 600, 600, "ХОЛОДИЛЬНИК", 2.35)
        base.label_model(c, bold, 300, 2125, "ЛЕВАЯ ВЕТВЬ 700", 2.5, "#6e5a34")
    else:
        for y, h, label in (
            (1300, 600, "ХОЛОДИЛЬНИК"),
            (1900, 600, "ХРАНЕНИЕ"),
            (2500, 400, "ХРАНЕНИЕ"),
        ):
            kitchen_module(c, regular, 0, y, 600, h, label, 2.25)
        base.label_model(c, bold, 300, 1225, "ЛЕВАЯ ВЕТВЬ 1600", 2.55, "#6e5a34")


def draw_sofa_desk_tv(c, regular, bold):
    base.draw_sofa(c, regular, SOFA[0], SOFA[1], SOFA[2] - SOFA[0], SOFA[3] - SOFA[1], "down")
    base.label_model(c, bold, 3430, 2590, "ДИВАН-КРОВАТЬ 2000x1000", 2.75, "#544943")

    base.model_box(c, DESK[0], DESK[1], DESK[2] - DESK[0], DESK[3] - DESK[1], WORK, "#4e7589", 0.24, 35)
    base.model_box(c, 4640, 3160, 340, 110, "#f3f7f8", "#4e7589", 0.12, 12)
    base.label_model(c, bold, 5110, 3310, "РМ 1200x600", 3.0, "#2e5b70")
    base.draw_task_chair(c, 4810, 2800, "up")

    base.draw_tv(c, regular, TV[0], TV[1], TV[2] - TV[0], TV[3] - TV[1], "bottom")
    base.label_model(c, bold, 3410, 315, "ТВ / МЕДИА 1600x300", 2.75, "#624a59")


def draw_table(c, regular, bold, show_seated=True):
    x1, y1, x2, y2 = TABLE
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.32, 45)
    base.model_line(c, x1 + 700, y1, x1 + 700, y2, "#6b8665", 0.14)
    base.label_model(c, bold, 1370, 1850, "CJ196 1400x800", 3.1, "#405d3c")
    base.label_model(c, regular, 1370, 1725, "СТОЛ В ЗОНЕ КУХНИ", 2.7, "#405d3c")

    if show_seated:
        for chair in CHAIRS_SEATED:
            base.draw_chair(c, chair[0], chair[1], chair[2] - chair[0], chair[3] - chair[1], facing="up")
        base.label_model(c, regular, 1370, 930, "при посадке стулья заходят в маршрут", 2.55, BAD)
    else:
        for chair in CHAIRS_STOWED:
            x1c, y1c, x2c, y2c = chair
            c.setStrokeColor(HexColor("#6d6258")); c.setLineWidth(0.20 * mm); c.setDash(1.0 * mm, 0.7 * mm)
            c.rect(base.qx(x1c) * mm, base.qy(y1c) * mm,
                   base.p(x2c - x1c) * mm, base.p(y2c - y1c) * mm, fill=0, stroke=1)
            c.setDash()
        base.label_model(c, regular, 1370, 1450, "2 складных стула задвинуты", 2.45, "#6d6258")


def draw_dimensions(c, regular, short_left=False):
    base.dim_h(c, regular, base.qx(670), base.qx(2070), base.qy(2250), "1400")
    base.dim_v(c, regular, base.qx(2120), base.qy(1400), base.qy(2200), "800")
    base.dim_v(c, regular, base.qx(2160), base.qy(2200), base.qy(2900), "700", GOOD)
    base.dim_v(c, regular, base.qx(2220), base.qy(1250), base.qy(1400), "150", ORANGE)
    base.dim_h(c, regular, base.qx(600), base.qx(670), base.qy(1350), "70", ORANGE)
    if short_left:
        base.dim_v(c, regular, base.qx(630), base.qy(2200), base.qy(2300), "100", GOOD)


def draw_common(c, regular, bold, short_left=False, show_seated=True):
    base.draw_room_shell(c, regular, bold, "TV-001 rev15")
    draw_d2_guard(c, regular)
    route_rect(c, regular, MAIN_ROUTE, "D2 -> O1: 900 мм; свободен без выдвинутых стульев", (3350, 520), GOOD, 0.32, PALE_GREEN)
    route_rect(c, regular, O1_ROUTE, "900 к O1", (5250, 2380), GOOD, 0.30, PALE_GREEN)
    route_rect(c, regular, DESK_APPROACH, "подход к креслу 600", (4810, 2390), BLUE, 0.28, PALE_BLUE)
    route_rect(c, regular, TOP_WORK, "рабочий пояс верхней ветви 700", (1400, 2770), ORANGE, 0.28, PALE_ORANGE)
    route_rect(c, regular, LEFT_WORK_SHORT if short_left else LEFT_WORK_FULL,
               "рабочий пояс левой ветви 700", (955, 2330 if short_left else 2050), ORANGE, 0.28, PALE_ORANGE)
    draw_kitchen(c, regular, bold, short_left=short_left)
    draw_sofa_desk_tv(c, regular, bold)
    draw_table(c, regular, bold, show_seated=show_seated)
    draw_dimensions(c, regular, short_left=short_left)


def requested_sidebar(c, regular, bold):
    panel(c, regular, bold, 255, 205, 151, 65, "ГДЕ СТОЛ НА ПЛАНЕ", PALE_GREEN)
    y = 252
    for line in (
        "- зелёный CJ196: x=670...2070",
        "- y=1400...2200; размер 1400x800",
        "- 70 мм от фронта левой ветви",
        "- 700 мм до верхней ветви кухни",
        "- 150 мм до полосы D2 -> O1",
    ):
        text(c, regular, 259, y, 3.8, line); y -= 5.7

    panel(c, regular, bold, 255, 126, 151, 69, "ПРОВЕРКА РЕАЛЬНЫХ РАССТОЯНИЙ", PALE_RED)
    y = 178
    for paragraph in (
        "При полной левой ветви 1600 мм стол физически помещается, но перекрывает её 700-мм рабочий пояс на участке 630x800 мм.",
        "Значит фасады/ПММ/холодильник на этом участке нельзя нормально открывать. Надпись v29 «Г-пояс 700» для этой позиции была ошибочной.",
    ):
        y = wrapped(c, regular, 259, y, 3.75, paragraph, 55, BAD, 4.75, "-") - 1.4

    panel(c, regular, bold, 255, 67, 151, 49, "СЦЕНАРИЙ СТУЛЬЕВ", PALE_ORANGE)
    y = 100
    for line in (
        "Два стула 400x400 при посадке",
        "заходят на 250 мм в маршрут 900.",
        "D2 guard при этом не пересекается.",
        "Полное задвигание — после проверки",
        "ножек/царг реального CJ196.",
    ):
        text(c, regular, 259, y, 3.55, line, ORANGE); y -= 4.7


def recommended_sidebar(c, regular, bold):
    panel(c, regular, bold, 255, 200, 151, 70, "МИНИМАЛЬНОЕ РАБОЧЕЕ ИСПРАВЛЕНИЕ", PALE_GREEN)
    y = 251
    for paragraph in (
        "Стол остаётся там же: 1400x800, 70/700/150 мм без изменения.",
        "Левая ветвь 700 мм: холодильник 600 + глухой добор 100. До корпуса холодильника 100 мм; ближайший зазор стол–ветвь 70 мм. Это не проход.",
    ):
        y = wrapped(c, regular, 259, y, 3.8, paragraph, 55, INK, 4.9, "-") - 1.6

    panel(c, regular, bold, 255, 125, 151, 65, "ЧТО СОХРАНЕНО", PALE_BLUE)
    y = 174
    for line in (
        "- верхняя кухня 2400 до дивана",
        "- стол именно в кухонной части",
        "- рабочий пояс верхней ветви 700",
        "- основной маршрут 900 статически",
        "- диван, ТВ, РМ и терраса без сдвига",
    ):
        text(c, regular, 259, y, 3.75, line); y -= 5.6

    panel(c, regular, bold, 255, 67, 151, 48, "ОГРАНИЧЕНИЕ", PALE_ORANGE)
    y = 99
    for line in (
        "Во время посадки стулья занимают маршрут.",
        "Один стул касается границы D2 без запаса.",
        "Для четырёх гостей стол переносится к дивану.",
        "Петли холодильника и каркас стола — после SKU.",
    ):
        text(c, regular, 259, y, 3.7, line, ORANGE); y -= 5.2


def draw_requested(c, regular, bold):
    page_frame(
        c, regular, bold,
        "TV-001 rev15 — СТОЛ ДЕЙСТВИТЕЛЬНО В ЗОНЕ КУХНИ",
        "Лист 1: точный перенос выбранной картинки в план; красным показана скрытая коллизия полной Г-ветви.",
        1,
    )
    draw_common(c, regular, bold, short_left=False, show_seated=True)
    conflict = intersection(TABLE, LEFT_WORK_FULL)
    assert conflict is not None
    route_rect(c, regular, conflict, "КОНФЛИКТ 630x800", (985, 1810), BAD, 0.45, PALE_RED)
    requested_sidebar(c, regular, bold)
    c.showPage()


def draw_recommended(c, regular, bold):
    page_frame(
        c, regular, bold,
        "TV-001 rev15 — РАБОЧАЯ КОРРЕКЦИЯ БЕЗ СДВИГА СТОЛА",
        "Лист 2: стол остаётся в кухне; сокращается только блокирующая его часть левой ветви.",
        2,
    )
    draw_common(c, regular, bold, short_left=True, show_seated=False)
    recommended_sidebar(c, regular, bold)
    c.showPage()


MINI_SCALE = 0.0275


def mini_rect(c, ox, oy, rect, fill, stroke=INK, width=0.18, dash=None, radius=0):
    x1, y1, x2, y2 = rect
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke))
    c.setLineWidth(width * mm)
    c.setDash(*(dash or []))
    x = ox + x1 * MINI_SCALE
    y = oy + y1 * MINI_SCALE
    w = (x2 - x1) * MINI_SCALE
    h = (y2 - y1) * MINI_SCALE
    if radius:
        c.roundRect(x * mm, y * mm, w * mm, h * mm, radius * mm, fill=1, stroke=1)
    else:
        c.rect(x * mm, y * mm, w * mm, h * mm, fill=1, stroke=1)
    c.setDash()


def mini_outline(c, ox, oy, rect, color, width=0.24, dash=(1.2 * mm, 0.7 * mm)):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(color)); c.setLineWidth(width * mm); c.setDash(*dash)
    c.rect((ox + x1 * MINI_SCALE) * mm, (oy + y1 * MINI_SCALE) * mm,
           ((x2 - x1) * MINI_SCALE) * mm, ((y2 - y1) * MINI_SCALE) * mm,
           fill=0, stroke=1)
    c.setDash()


def mini_label(c, font, ox, oy, x, y, value, size=3.0, color=INK, center=True):
    text(c, font, ox + x * MINI_SCALE, oy + y * MINI_SCALE, size, value, color, center=center)


def draw_mini_scenario(
    c, regular, bold, ox, oy, title, status,
    table_rect=TABLE, sofa_rect=SOFA, chairs=(), chair_pull=(), stowed=False,
):
    room_w = ROOM[2] * MINI_SCALE
    room_h = ROOM[3] * MINI_SCALE
    text(c, bold, ox, oy + room_h + 7.0, 5.2, title)
    text(c, regular, ox, oy - 6.0, 3.7, status, GOOD if not chair_pull else ORANGE)

    base.box(c, ox, oy, room_w, room_h, "#ffffff", "#111827", 0.40)
    mini_outline(c, ox, oy, D2_GUARD, ORANGE, 0.18)
    mini_outline(c, ox, oy, MAIN_ROUTE, BAD if chair_pull else GOOD, 0.24)
    mini_outline(c, ox, oy, O1_ROUTE, GOOD, 0.22)
    mini_outline(c, ox, oy, DESK_APPROACH, BLUE, 0.18)

    mini_rect(c, ox, oy, KITCHEN_TOP, KITCHEN, "#6e5a34", 0.18)
    mini_rect(c, ox, oy, KITCHEN_LEFT_SHORT, KITCHEN, "#6e5a34", 0.18)
    mini_rect(c, ox, oy, KITCHEN_LEFT_FILLER, "#ead5a8", "#6e5a34", 0.14)
    mini_rect(c, ox, oy, DESK, WORK, "#4e7589", 0.18)
    mini_rect(c, ox, oy, TV, MEDIA, "#6d5364", 0.18, radius=1.1)
    mini_rect(c, ox, oy, sofa_rect, LOUNGE, "#665a54", 0.20, radius=2.0)
    mini_rect(c, ox, oy, table_rect, DINING, "#506c4d", 0.24, radius=1.3)

    if stowed:
        for chair in CHAIRS_STOWED:
            mini_outline(c, ox, oy, chair, "#6d6258", 0.14, (0.8 * mm, 0.5 * mm))
    for chair in chairs:
        mini_rect(c, ox, oy, chair, "#f6f2ed", "#6d6258", 0.16, radius=1.0)
    for pull in chair_pull:
        mini_outline(c, ox, oy, pull, BAD, 0.20)

    mini_label(c, bold, ox, oy, (table_rect[0] + table_rect[2]) / 2,
               (table_rect[1] + table_rect[3]) / 2, "СТОЛ 1400x800", 2.8, "#405d3c")
    mini_label(c, regular, ox, oy, 3430, (sofa_rect[1] + sofa_rect[3]) / 2,
               "ДИВАН" if sofa_rect == SOFA else "СПАЛЬНОЕ МЕСТО", 2.7, "#544943")
    mini_label(c, regular, ox, oy, 5110, 3320, "РМ", 2.7, BLUE)
    mini_label(c, regular, ox, oy, 3410, 100, "ТВ", 2.7, "#624a59")
    mini_label(c, regular, ox, oy, 5250, 2250, "O1", 2.6, GOOD)


def draw_scenarios(c, regular, bold):
    page_frame(
        c, regular, bold,
        "TV-001 rev15 — ЧЕТЫРЕ РЕАЛЬНЫХ СЦЕНАРИЯ",
        "Стол постоянно хранится у кухни; к дивану переносится только для четырёх гостей.",
        3,
    )
    draw_mini_scenario(
        c, regular, bold, 18, 155,
        "A. ДЕНЬ — СТОЛ У КУХНИ",
        "Стулья задвинуты: D2 -> O1 сохраняет 900 мм.",
        stowed=True,
    )
    draw_mini_scenario(
        c, regular, bold, 220, 155,
        "B. УЖИН НА 2",
        "Во время посадки 250 мм маршрута временно заняты.",
        chairs=CHAIRS_SEATED,
        chair_pull=CHAIRS_SEATED,
    )
    draw_mini_scenario(
        c, regular, bold, 18, 35,
        "C. ГОСТИ НА 4 — СТОЛ К ДИВАНУ",
        "2 на диване + 2 стула; перенос вручную +2060/+300 мм.",
        table_rect=GUEST_TABLE,
        chairs=GUEST_CHAIRS,
        chair_pull=GUEST_CHAIR_PULL,
    )
    draw_mini_scenario(
        c, regular, bold, 220, 35,
        "D. НОЧЬ — СТОЛ НЕ ДВИГАЕМ",
        "До спального места 360 мм по X; маршруты сохранены.",
        sofa_rect=SOFA_OPEN,
        stowed=True,
    )
    c.showPage()


def render_previews() -> None:
    executable = shutil.which("pdftoppm")
    if not executable:
        print("WARN: pdftoppm not found; PDF built, PNG previews skipped")
        return
    PREVIEW_PREFIX.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [executable, "-png", "-r", "150", str(OUT_PDF), str(PREVIEW_PREFIX)],
        check=True,
    )
    print(f"PASS rev15 previews: {PREVIEW_PREFIX}-1.png; -2.png; -3.png")


def build() -> None:
    validate_geometry()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(OUT_PDF), pagesize=landscape(A3))
    c.setTitle("TV-001 rev15 — стол в зоне кухни и сценарии")
    c.setAuthor("Codex")
    draw_requested(c, regular, bold)
    draw_recommended(c, regular, bold)
    draw_scenarios(c, regular, bold)
    c.save()
    print(f"PASS rev15 PDF: {OUT_PDF}")
    render_previews()


if __name__ == "__main__":
    build()
