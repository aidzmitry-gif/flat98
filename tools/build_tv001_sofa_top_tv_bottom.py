# -*- coding: utf-8 -*-
"""TV-001: scale-accurate TV-first kitchen-living option for B01.

All coordinates are model millimetres.  It is a concept drawing, not an order
drawing: door swings, water, ventilation, radiators and exact furniture SKUs
remain gates before any purchase or construction work.
"""
from __future__ import annotations

import shutil
from itertools import combinations
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-001_диван-верхняя_стена_ТВ-нижняя_М1-25_rev13_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-001_диван-верхняя_стена_ТВ-нижняя_М1-25_rev13.pdf"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
LOUNGE = base.LOUNGE
WORK = base.WORK
MEDIA = base.MEDIA
ROUTE = base.ROUTE
GOOD = base.GOOD
BAD = base.BAD
BLUE = "#2f6e8d"
ORANGE = "#ad6800"
PALE_BLUE = "#eef7fb"
PALE_GREEN = "#eff8f1"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"
GRAY = "#d9dde1"

ROOM = (0, 0, 5710, 3500)
D2_GUARD = (0, 0, 1200, 1300)
# B01: one straight right facade, measured from the top/sofa corner to the
# lower/TV corner.  These are lengths along a single plane, never returns.
RIGHT_FACADE_TOP_WALL = 1300
O1_WIDTH = 1600
RIGHT_FACADE_BOTTOM_WALL = 600

# Main route is the verified project strip. The blue strip is the 600-mm
# approach to the permanent work chair from below. It is not a dining aisle.
ROUTES = (
    (0, 350, 5710, 1250),
    (4810, 350, 5710, 2450),
    (4510, 1250, 5110, 2490),
)

# A 700-mm working strip in front of the left kitchen branch. This is not a
# circulation route: it is reserved for opening/loading the PPM and kitchen
# fronts. A dining chair cannot permanently occupy it.
KITCHEN_LEFT_WORK_ZONE = (600, 1300, 1300, 2900)
KITCHEN_TOP_WORK_ZONE = (0, 2200, 2400, 2900)
# Conservative 700-mm opening/loading envelopes: one appliance or front may
# occupy this belt at a time, so it is not a second circulation route.
KITCHEN_OPENING_ENVELOPES = {
    "левая ветвь / ПММ и фасады": KITCHEN_LEFT_WORK_ZONE,
    "верхняя ветвь / фасады": KITCHEN_TOP_WORK_ZONE,
}

DAY_FIXED = {
    # Four 600-mm modules form a continuous run: the outer two are tall
    # columns. The 30-mm side shadow at the sofa arm is a mounting/service
    # gap, never a passage.
    "kitchen_top": (0, 2900, 2400, 3500),
    "kitchen_left": (0, 1300, 600, 2900),
    "desk": (4510, 2900, 5710, 3500),
    # 30 mm to kitchen and 80 mm to desk: both are technical gaps, not aisles.
    "sofa_closed": (2430, 2500, 4430, 3500),
    "tv_media": (2610, 0, 4210, 300),
    # HuanaXin CJ196 is stored folded at the kitchen side of the lower wall.
    # Its 800x110 envelope leaves 240 mm before the D2->O1 route; no wheels.
    "dining_console": (1300, 0, 2100, 110),
}

# Daily dinner mode: HuanaXin CJ196 stays open at 1400x800, 70 mm from the
# kitchen end as in v29. Two people sit on the sofa and two on compact folding
# stools. The 900-mm D2->O1 route is free only while chairs are pushed in or
# stored; pull-out during seating deliberately enters this route.
MEAL_FIXED = {
    "kitchen_top": DAY_FIXED["kitchen_top"],
    "kitchen_left": DAY_FIXED["kitchen_left"],
    "desk": DAY_FIXED["desk"],
    "sofa_closed": DAY_FIXED["sofa_closed"],
    "tv_media": DAY_FIXED["tv_media"],
    "meal_table": (2470, 1700, 3870, 2500),
    "meal_chair_1": (2620, 1300, 3020, 1700),
    "meal_chair_2": (3320, 1300, 3720, 1700),
}

NIGHT_FIXED = {
    "kitchen_top": DAY_FIXED["kitchen_top"],
    "kitchen_left": DAY_FIXED["kitchen_left"],
    "desk": DAY_FIXED["desk"],
    "tv_media": DAY_FIXED["tv_media"],
    "dining_console": DAY_FIXED["dining_console"],
}

# Guest dinner: move the same CJ196 200 mm right, to the sofa centre. It gives
# a more useful 270-mm kitchen-side gap but is not the permanent daily setup.
GUEST_FIXED = {
    "kitchen_top": DAY_FIXED["kitchen_top"],
    "kitchen_left": DAY_FIXED["kitchen_left"],
    "desk": DAY_FIXED["desk"],
    "sofa_guest": DAY_FIXED["sofa_closed"],
    "tv_media": DAY_FIXED["tv_media"],
    "guest_table": (2670, 1700, 4070, 2500),
    "guest_chair_1": (2820, 1300, 3220, 1700),
    "guest_chair_2": (3520, 1300, 3920, 1700),
}

DAY_DYNAMIC = {"desk_chair": (4510, 2490, 5110, 3110)}
MEAL_DYNAMIC = DAY_DYNAMIC
NIGHT_DYNAMIC = {
    "desk_chair": DAY_DYNAMIC["desk_chair"],
    # Double sleeper: 1400x2000, opened forward from the upper wall.
    "sofa_open": (2430, 2100, 4430, 3500),
}
GUEST_DYNAMIC = {"desk_chair": DAY_DYNAMIC["desk_chair"]}

# These are operational, not parked, chair envelopes: 400 mm pull-out from
# the table toward D2. They prove why the 900-mm D2->O1 strip must not be
# described as simultaneously free while people are seated.
MEAL_CHAIR_PULL_ENVELOPES = {
    "дневной стул 1 при посадке": (2620, 700, 3020, 1700),
    "дневной стул 2 при посадке": (3320, 700, 3720, 1700),
}
GUEST_CHAIR_PULL_ENVELOPES = {
    "гостевой стул 1 при посадке": (2820, 700, 3220, 1700),
    "гостевой стул 2 при посадке": (3520, 700, 3920, 1700),
}


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def validate_layout(
    name: str,
    fixed: dict[str, tuple[int, int, int, int]],
    dynamic: dict[str, tuple[int, int, int, int]],
    allowed_dynamic_fixed: set[frozenset[str]],
    routes: tuple[tuple[int, int, int, int], ...] = ROUTES,
) -> None:
    for group_name, group in (("fixed", fixed), ("dynamic", dynamic)):
        for item, rect in group.items():
            x1, y1, x2, y2 = rect
            if not (0 <= x1 < x2 <= 5710 and 0 <= y1 < y2 <= 3500):
                raise AssertionError(f"{name}/{group_name}/{item} outside B01: {rect}")
            if overlap(rect, D2_GUARD):
                raise AssertionError(f"{name}/{group_name}/{item} enters D2 guard: {rect}")
            for route in routes:
                if overlap(rect, route):
                    raise AssertionError(f"{name}/{group_name}/{item} enters route: {rect}")
    for left, right in combinations(fixed, 2):
        if overlap(fixed[left], fixed[right]):
            raise AssertionError(f"{name}: fixed overlap {left}/{right}")
    for moving, moving_rect in dynamic.items():
        for item, fixed_rect in fixed.items():
            if frozenset((moving, item)) in allowed_dynamic_fixed:
                continue
            if overlap(moving_rect, fixed_rect):
                raise AssertionError(f"{name}: dynamic overlap {moving}/{item}")


def validate_geometry() -> None:
    allowed = {frozenset(("desk_chair", "desk"))}
    validate_layout("DAY", DAY_FIXED, DAY_DYNAMIC, allowed)
    validate_layout("MEAL", MEAL_FIXED, MEAL_DYNAMIC, allowed)
    validate_layout("NIGHT", NIGHT_FIXED, NIGHT_DYNAMIC, allowed)
    validate_layout("GUEST", GUEST_FIXED, GUEST_DYNAMIC, allowed)
    assert D2_GUARD == (0, 0, 1200, 1300)
    assert RIGHT_FACADE_TOP_WALL + O1_WIDTH + RIGHT_FACADE_BOTTOM_WALL == ROOM[3]
    assert DAY_FIXED["sofa_closed"][0] - DAY_FIXED["kitchen_top"][2] == 30
    assert DAY_FIXED["desk"][0] - DAY_FIXED["sofa_closed"][2] == 80
    assert ROUTES[2][2] - ROUTES[2][0] == 600
    assert ROUTES[2][0] == DAY_FIXED["desk"][0]
    assert ROUTES[2][3] == DAY_DYNAMIC["desk_chair"][1]
    assert NIGHT_DYNAMIC["sofa_open"][1] - ROUTES[0][3] == 850
    assert ROUTES[1][0] - NIGHT_DYNAMIC["sofa_open"][2] == 380
    assert DAY_FIXED["sofa_closed"][1] - DAY_FIXED["tv_media"][3] == 2200
    assert ROUTES[0][1] - DAY_FIXED["dining_console"][3] == 240
    for item in ("meal_table", "meal_chair_1", "meal_chair_2"):
        assert not overlap(MEAL_FIXED[item], KITCHEN_LEFT_WORK_ZONE), item
        assert not overlap(MEAL_FIXED[item], KITCHEN_TOP_WORK_ZONE), item
    for envelope_name, envelope in KITCHEN_OPENING_ENVELOPES.items():
        for item in ("meal_table", "meal_chair_1", "meal_chair_2"):
            assert not overlap(MEAL_FIXED[item], envelope), f"{item}/{envelope_name}"
        for item in ("guest_table", "guest_chair_1", "guest_chair_2"):
            assert not overlap(GUEST_FIXED[item], envelope), f"{item}/{envelope_name}"
    assert MEAL_FIXED["meal_table"][0] - DAY_FIXED["kitchen_top"][2] == 70
    assert MEAL_FIXED["meal_table"][0] + MEAL_FIXED["meal_table"][2] == 2 * 3170
    assert DAY_FIXED["sofa_closed"][1] - MEAL_FIXED["meal_table"][3] == 0
    assert MEAL_FIXED["meal_chair_1"][1] - ROUTES[0][3] == 50
    for envelope in MEAL_CHAIR_PULL_ENVELOPES.values():
        assert overlap(envelope, ROUTES[0]), "dining pull-out must be marked as temporary route occupation"
    assert NIGHT_DYNAMIC["sofa_open"][2] - NIGHT_DYNAMIC["sofa_open"][0] == 2000
    assert NIGHT_DYNAMIC["sofa_open"][3] - NIGHT_DYNAMIC["sofa_open"][1] == 1400
    assert GUEST_FIXED["guest_table"][3] == DAY_FIXED["sofa_closed"][1]
    assert GUEST_FIXED["guest_table"][2] - GUEST_FIXED["guest_table"][0] == 1400
    assert GUEST_FIXED["guest_table"][3] - GUEST_FIXED["guest_table"][1] == 800
    assert GUEST_FIXED["guest_table"][0] - DAY_FIXED["kitchen_top"][2] == 270
    assert GUEST_FIXED["guest_chair_1"][1] - ROUTES[0][3] == 50
    for envelope in GUEST_CHAIR_PULL_ENVELOPES.values():
        assert overlap(envelope, ROUTES[0]), "guest chair pull-out must be marked as temporary route occupation"
    # Backrest is on the lower side: seated person faces the upper wall/monitor.
    chair_symbol = (4810 - 264, 2800 - 275, 4810 + 264, 2800 + 284)
    chair_envelope = DAY_DYNAMIC["desk_chair"]
    assert chair_envelope[0] <= chair_symbol[0] and chair_symbol[2] <= chair_envelope[2]
    assert chair_envelope[1] <= chair_symbol[1] and chair_symbol[3] <= chair_envelope[3]
    print("PASS TV-001 rev13 geometry: daily CJ196 position 70 mm to kitchen; guest shift 270 mm; 30-mm kitchen-sofa and 80-mm sofa-desk service gaps; D2->O1 free at 900 mm only with chairs pushed in/stored")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=None, bullet=None):
    leading = leading or size * 1.28
    for index, row in enumerate(base.wrap(value, width)):
        prefix = (bullet + " ") if bullet and index == 0 else ("  " if bullet else "")
        text(c, font, x, y, size, prefix + row, color)
        y -= leading
    return y


def page_frame(c, regular, bold, title, subtitle, page_no, scale_label="М 1:25"):
    width, height = landscape(A3)
    c.setFillColor(white); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13.8, title)
    text(c, regular, 14, 274, 5.0, subtitle, MUTED)
    text(c, regular, 404, 14, 3.8, f"TV-001 | лист {page_no}/7 | {scale_label}", MUTED, right=True)


def draw_d2_guard(c, regular):
    x1, y1, x2, y2 = D2_GUARD
    c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.32 * mm); c.setDash(1.7 * mm, 0.9 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()
    base.label_model(c, regular, 600, 490, "D2 GUARD 1200x1300", 2.6, ORANGE)


def draw_route_rect(c, regular, rect, label, at, color=ROUTE):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(color)); c.setLineWidth(0.35 * mm); c.setDash(1.8 * mm, 1.0 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, at[0], at[1], label, 2.8, color)


def draw_routes(c, regular):
    draw_route_rect(
        c,
        regular,
        ROUTES[0],
        "D2 -> O1 900",
        (3500, 455),
        ROUTE,
    )
    draw_route_rect(c, regular, ROUTES[1], "900 к O1", (5255, 2380))
    draw_route_rect(c, regular, ROUTES[2], "подход снизу 600", (4810, 2400), BLUE)


def kitchen_module(c, regular, x, y, w, h, label):
    base.model_box(c, x, y, w, h, KITCHEN, "#6e5a34", 0.20)
    base.label_model(c, regular, x + w / 2, y + h / 2 - 10, label, 2.7, "#5b4827")


def draw_kitchen(c, regular, bold):
    # Compact L-kitchen: it intentionally gives up length to preserve a real bed.
    kitchen_module(c, regular, 0, 2900, 600, 600, "ХОЛ./ПЕНАЛ")
    kitchen_module(c, regular, 600, 2900, 600, 600, "МОЙКА")
    kitchen_module(c, regular, 1200, 2900, 600, 600, "ВАРКА")
    kitchen_module(c, regular, 1800, 2900, 600, 600, "ПЕНАЛ СВЧ/ДУХ")
    # The dishwasher is a distinct 450-mm appliance in the closest left
    # module, not an impossible second appliance inside the 600-mm sink base.
    for y, label in ((1300, "ХРАН."), (1835, "ПЕНАЛ"), (2365, "ПММ 450")):
        kitchen_module(c, regular, 0, y, 600, 530, label)
    base.model_box(c, 730, 3050, 340, 240, "#edf2f2", "#617377", 0.12, 22)
    base.model_line(c, 900, 3290, 900, 3370, "#617377", 0.16)
    c.setStrokeColor(HexColor("#6e5a34")); c.setLineWidth(0.14 * mm)
    for x, y in ((1380, 3065), (1600, 3065), (1380, 3280), (1600, 3280)):
        c.circle(base.qx(x) * mm, base.qy(y) * mm, base.p(65) * mm, fill=0, stroke=1)
    # Opening/loading belts, intentionally separate from circulation. They are
    # conservative 700-mm envelopes for a single open front/appliance.
    for rect in KITCHEN_OPENING_ENVELOPES.values():
        x1, y1, x2, y2 = rect
        c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.18 * mm); c.setDash(1.1 * mm, 0.7 * mm)
        c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
        c.setDash()
    base.label_model(c, bold, 1200, 3440, "Г-КУХНЯ 4000 мм фронтов; 2 колонны", 3.4, "#6e5a34")
    base.label_model(c, regular, 1200, 2825, "правая колонна 600: СВЧ/духовка; до дивана тех. зазор 30 мм", 2.7, ORANGE)
    base.label_model(c, regular, 1780, 2270, "рабочий пояс 700: с открытым фасадом локально сужен", 2.2, ORANGE)


def draw_task_chair_compact(c, cx, cy):
    # The desk is above the chair, therefore the person looks upward to the
    # top wall; the chair backrest is drawn on the lower side.
    c.setFillColor(HexColor("#eff5f8")); c.setStrokeColor(HexColor("#4b6d82")); c.setLineWidth(0.18 * mm)
    c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(230) * mm, fill=1, stroke=1)
    for dx, dy in ((0, 260), (240, 70), (150, -225), (-150, -225), (-240, 70)):
        base.model_line(c, cx, cy, cx + dx, cy + dy, "#4b6d82", 0.15)
        c.setFillColor(HexColor("#4b6d82"))
        c.circle(base.qx(cx + dx) * mm, base.qy(cy + dy) * mm, base.p(24) * mm, fill=1, stroke=0)
    base.model_box(c, cx - 205, cy - 275, 410, 85, "#d5e7f2", "#4b6d82", 0.16, 30)


def draw_desk(c, regular):
    x, y, w, h = DAY_FIXED["desk"]
    base.model_box(c, x, y, w - x, h - y, WORK, "#4e7589", 0.24, 38)
    base.model_line(c, 5110, y + 70, 5110, h - 70, "#6a94a8", 0.14)
    base.model_box(c, 4640, 3160, 340, 110, "#f3f7f8", "#4e7589", 0.12, 12)
    base.label_model(c, regular, 4810, 3310, "РМ 1200x600", 3.4, "#2e5b70")
    base.label_model(c, regular, 4810, 3165, "работа слева", 2.6, "#2e5b70")
    base.label_model(c, regular, 5410, 3165, "закр. хранение", 2.5, "#2e5b70")
    x1, y1, x2, y2 = DAY_DYNAMIC["desk_chair"]
    c.setStrokeColor(HexColor(BLUE)); c.setLineWidth(0.28 * mm); c.setDash(1.6 * mm, 0.9 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash(); base.label_model(c, regular, 4810, 2635, "кресло max 600x620", 2.5, BLUE)
    draw_task_chair_compact(c, 4810, 2800)


def draw_tv(c, regular, bold, x=2610, label_x=3410):
    base.draw_tv(c, regular, x, 0, 1600, 300, "bottom")
    base.label_model(c, bold, label_x, 315, "ТВ 65 дюймов рекоменд.; 75 - по SKU", 2.9, "#624a59")


def draw_sofa_day(c, regular, bold, x=2430, label_x=3430, note="спинка у верхней стены; до РМ тех. зазор 80"):
    base.draw_sofa(c, regular, x, 2500, 2000, 1000, "down")
    base.label_model(c, bold, label_x, 2595, "ДЕНЬ: ДИВАН-КРОВАТЬ 2000x1000", 3.1, "#544943")
    base.label_model(c, regular, label_x, 2450, note, 2.7, "#544943")


def draw_sofa_night(c, regular, bold):
    # Ghosted day outline so the transformation remains explicit.
    c.setStrokeColor(HexColor("#96717a")); c.setLineWidth(0.22 * mm); c.setDash(1.2 * mm, 0.8 * mm)
    c.rect(base.qx(2430) * mm, base.qy(2500) * mm, base.p(2000) * mm, base.p(1000) * mm, fill=0, stroke=1)
    c.setDash()
    base.model_box(c, 2430, 2100, 2000, 1400, "#f1dfe4", "#8b5362", 0.28, 50)
    for x in (2570, 3490):
        base.model_box(c, x, 3160, 720, 220, "#fff7f8", "#a77a84", 0.12, 28)
    base.model_line(c, 2430, 2500, 4430, 2500, "#a77a84", 0.14)
    base.label_model(c, bold, 3430, 2720, "НОЧЬ: СПАЛЬНОЕ МЕСТО 2000x1400", 3.5, "#7a3848")
    base.label_model(c, regular, 3430, 2570, "2 гостя; открыть только после уборки стола и стульев", 2.7, "#7a3848")
    base.label_model(c, regular, 3430, 2390, "850 до основного маршрута; O1 900 сохранен", 2.7, "#7a3848")


def draw_dining_console(c, regular, bold, night=False):
    x1, y1, x2, y2 = DAY_FIXED["dining_console"]
    cx = (x1 + x2) / 2
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, "#e5e9ec", "#78838d", 0.20, 20)
    base.label_model(c, bold, cx, 80, "CJ196 СЛОЖЕН 800x110", 2.7, "#59646e")
    base.label_model(
        c,
        regular,
        cx,
        55,
        "у нижней стены ближе к кухне; 240 до маршрута" if not night else "ночью остается сложенным",
        2.35,
        ORANGE if not night else "#59646e",
    )


def draw_meal_table(c, regular, bold):
    x1, y1, x2, y2 = MEAL_FIXED["meal_table"]
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.23, 38)
    base.model_line(c, (x1 + x2) / 2, y1, (x1 + x2) / 2, y2, "#6b8665", 0.14)
    for key in ("meal_chair_1", "meal_chair_2"):
        cx1, cy1, cx2, cy2 = MEAL_FIXED[key]
        base.draw_chair(c, cx1, cy1, cx2 - cx1, cy2 - cy1, facing="up")
    # Red dashed portions are the chair pull-out envelopes; they visibly cross
    # the orange route and therefore are an operational warning, not clearance.
    c.setStrokeColor(HexColor(BAD)); c.setLineWidth(0.16 * mm); c.setDash(0.9 * mm, 0.6 * mm)
    for pull in MEAL_CHAIR_PULL_ENVELOPES.values():
        px1, py1, px2, py2 = pull
        c.rect(base.qx(px1) * mm, base.qy(py1) * mm, base.p(px2 - px1) * mm, base.p(py2 - py1) * mm, fill=0, stroke=1)
    c.setDash()
    base.label_model(c, bold, 3170, 2100, "ДЕНЬ: CJ196 1400x800 ПОСТОЯННО", 2.65, "#405d3c")
    base.label_model(c, regular, 3170, 1950, "70 до кухни; ежедневно 2 стула max 400x400", 2.25, "#405d3c")
    base.label_model(c, regular, 3170, 1800, "900 D2->O1 только при задвинутых/убранных стульях", 2.15, ORANGE)


def draw_guest_table(c, regular, bold, fixed=GUEST_FIXED, label_x=3170):
    x1, y1, x2, y2 = fixed["guest_table"]
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, DINING, "#506c4d", 0.24, 45)
    base.model_line(c, (x1 + x2) / 2, y1, (x1 + x2) / 2, y2, "#6b8665", 0.14)
    for key in ("guest_chair_1", "guest_chair_2"):
        cx1, cy1, cx2, cy2 = fixed[key]
        base.draw_chair(c, cx1, cy1, cx2 - cx1, cy2 - cy1, facing="up")
    c.setStrokeColor(HexColor(BAD)); c.setLineWidth(0.16 * mm); c.setDash(0.9 * mm, 0.6 * mm)
    for pull in GUEST_CHAIR_PULL_ENVELOPES.values():
        px1, py1, px2, py2 = pull
        c.rect(base.qx(px1) * mm, base.qy(py1) * mm, base.p(px2 - px1) * mm, base.p(py2 - py1) * mm, fill=0, stroke=1)
    c.setDash()
    base.label_model(c, bold, label_x, 2135, "ГОСТИ: CJ196 СДВИНУТ К ЦЕНТРУ ДИВАНА", 2.8, "#405d3c")
    base.label_model(c, regular, label_x, 2005, "1400x800; 270 до кухни; 2 на диване + 2 стула", 2.35, "#405d3c")
    base.label_model(c, regular, label_x, 1880, "900 D2->O1 свободен только с задвинутыми/убранными стульями", 2.25, ORANGE)


def draw_night_storage(c, regular, bold):
    draw_dining_console(c, regular, bold, night=True)
    base.label_model(c, regular, 1700, 390, "Ночной шаг: сложить CJ196 и убрать два складных стула", 2.6, ORANGE)


def dimensions(c, regular, mode):
    base.dim_h(c, regular, base.OX, base.OX + base.p(5710), base.OY - 5.0, "5710 - чистый размер B01")
    base.dim_h(c, regular, base.qx(0), base.qx(2400), base.qy(2860), "2400")
    base.dim_h(c, regular, base.qx(2400), base.qx(2430), base.qy(2860), "30", ORANGE)
    base.dim_h(c, regular, base.qx(2430), base.qx(4430), base.qy(2460), "2000")
    base.dim_v(c, regular, base.qx(2350), base.qy(2500), base.qy(3500), "1000")
    # Explicitly dimension the intentionally tight sofa-to-desk clearance.
    base.dim_h(c, regular, base.qx(4430), base.qx(4510), base.qy(2860), "80", ORANGE)
    base.dim_h(c, regular, base.qx(2610), base.qx(4210), base.qy(340), "1600")
    base.dim_v(c, regular, base.qx(4240), base.qy(0), base.qy(300), "300")
    if mode == "night":
        base.dim_v(c, regular, base.qx(2350), base.qy(2100), base.qy(3500), "1400")
    if mode in ("meal", "guest"):
        fixed = MEAL_FIXED if mode == "meal" else GUEST_FIXED
        key = "meal_table" if mode == "meal" else "guest_table"
        x1, y1, x2, y2 = fixed[key]
        base.dim_h(c, regular, base.qx(2400), base.qx(x1), base.qy(1630), str(x1 - 2400), ORANGE)
        base.dim_h(c, regular, base.qx(x1), base.qx(x2), base.qy(1660), "1400")
        base.dim_v(c, regular, base.qx(x2 + 40), base.qy(y1), base.qy(y2), "800")


def panel(c, regular, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7, 4.3, title)


def sidebar(c, regular, bold, mode):
    panel(c, regular, bold, 255, 210, 151, 58, "ЧТО ПРОВЕРЕНО ГЕОМЕТРИЕЙ", PALE_BLUE)
    yy = 254
    geometry_lines = (
        "- B01: 5710x3500 мм",
        "- правая стена: прямая 3500; 1300+O1 1600+600",
        "- D2 guard: 1200x1300 мм",
        "- D2 -> O1: 900 мм",
        "- подход к креслу снизу: 600 мм",
        "- стационарная мебель вне guard и маршрутов",
    )
    for line in geometry_lines:
        text(c, regular, 259, yy, 3.9, line, INK); yy -= 5.8

    if mode == "day":
        panel(c, regular, bold, 255, 134, 151, 66, "ДЕНЬ: КИНО И РАБОТА", PALE_GREEN)
        paragraphs = (
            "Диван 2000x1000 у верхней стены смотрит на ТВ снизу. До РМ технический зазор 80 мм; это не проход.",
            "CJ196 ежедневно открыт 1400x800 в положении 70 мм от кухни; это не проход и не зона хранения.",
            "Г-кухня 4000 мм фронтов: 4 модуля по 600, справа колонна СВЧ/духовки; до дивана техзазор 30 мм.",
        )
    elif mode == "meal":
        panel(c, regular, bold, 255, 134, 151, 66, "ЕЖЕДНЕВНО: 2 МЕСТА", PALE_ORANGE)
        paragraphs = (
            "CJ196 постоянно открыт 1400x800: 70 мм до торца кухни; ежедневно используются два стула. Это технологический зазор, не проход.",
            "Левая ветвь кухни, ПММ и хранение полностью свободны; стол не входит в рабочие зоны.",
            "D2 -> O1 геометрически 900 мм только с задвинутыми или убранными стульями; при посадке стулья временно занимают маршрут.",
        )
    elif mode == "night":
        panel(c, regular, bold, 255, 134, 151, 66, "НОЧЬ: ГОСТИ С НОЧЕВКОЙ", PALE_ORANGE)
        paragraphs = (
            "CJ196 складывается до 800x110 или переставляется, два стула убираются отдельно. Только после этого открывается кровать.",
            "Матрасный конверт 1400x2000 рассчитан на 2 гостей. D2 -> O1 свободен после уборки стола и стульев.",
            "РМ геометрически доступно, но ночью это не приватное и не тихое рабочее место.",
        )
    else:
        panel(c, regular, bold, 255, 134, 151, 66, "УЖИН: CJ196 У ДИВАНА", PALE_ORANGE)
        paragraphs = (
            "Для гостей тот же CJ196 сдвигается вправо на 200 мм: 270 мм до торца кухни и ближе к центру дивана.",
            "Это нормальный сценарий ужина на 4; не нужна перестановка дивана или кухонных модулей.",
            "D2 -> O1 геометрически 900 мм лишь с задвинутыми/убранными стульями; при посадке они временно занимают маршрут.",
        )
    yy = 184
    for para in paragraphs:
        yy = wrapped(c, regular, 259, yy, 3.9, para, 53, INK, 5.0, "-") - 1.5

    panel(c, regular, bold, 255, 68, 151, 56, "НЕ ЗАКАЗЫВАТЬ БЕЗ SKU-ПРОВЕРКИ", PALE_RED)
    yy = 108
    for line in (
        "Внешний габарит дивана,",
        "механизм раскладки и подлокотники;",
        "D2/O1 створки; вода, вытяжка,",
        "радиатор, E-01 и высоты н/д.",
    ):
        text(c, regular, 259, yy, 3.85, line, BAD); yy -= 5.3


def draw_page(c, regular, bold, mode):
    is_day = mode == "day"
    is_meal = mode == "meal"
    is_night = mode == "night"
    page_frame(
        c,
        regular,
        bold,
        "TV-001 - ДИВАН СВЕРХУ, ТВ СНИЗУ" if is_day else (
            "TV-001 - ЕЖЕДНЕВНЫЙ СТОЛ: 2 МЕСТА" if is_meal else (
                "TV-001 - НОЧНОЙ РЕЖИМ ДЛЯ ГОСТЕЙ" if is_night else "TV-001 - УЖИН: CJ196 У ДИВАНА"
            )
        ),
        "B01 5710x3500 мм. Правая стена прямая: 1300 + O1 1600 + 600; мебель - проектные габариты до SKU.",
        1 if is_day else (2 if is_meal else (3 if is_night else 4)),
    )
    base.draw_room_shell(
        c,
        regular,
        bold,
        "TV-001 / ДЕНЬ" if is_day else ("TV-001 / ЕЖЕДНЕВНО" if is_meal else ("TV-001 / НОЧЬ" if is_night else "TV-001 / ГОСТИ")),
    )
    draw_d2_guard(c, regular); draw_routes(c, regular); draw_kitchen(c, regular, bold)
    draw_desk(c, regular); draw_tv(c, regular, bold)
    if is_day:
        draw_sofa_day(c, regular, bold); draw_meal_table(c, regular, bold)
    elif is_meal:
        draw_sofa_day(c, regular, bold); draw_meal_table(c, regular, bold)
    elif is_night:
        draw_sofa_night(c, regular, bold); draw_night_storage(c, regular, bold)
    else:
        draw_sofa_day(c, regular, bold); draw_guest_table(c, regular, bold)
    dimensions(c, regular, mode)
    sidebar(c, regular, bold, mode)
    c.showPage()


def node_box(c, x, y, w, h, fill, stroke, radius=2.0):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor(stroke)); c.setLineWidth(0.28 * mm)
    c.roundRect(x * mm, y * mm, w * mm, h * mm, radius * mm, fill=1, stroke=1)


def node_dim_h(c, font, x1, x2, y, label, color=MUTED, size=4.6):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(0.18 * mm)
    c.line(x1 * mm, y * mm, x2 * mm, y * mm)
    for x in (x1, x2):
        c.line(x * mm, (y - 1.8) * mm, x * mm, (y + 1.8) * mm)
    text(c, font, (x1 + x2) / 2, y + 2.0, size, label, color, center=True)


def node_dim_v(c, font, x, y1, y2, label, color=MUTED, size=4.5):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(0.18 * mm)
    c.line(x * mm, y1 * mm, x * mm, y2 * mm)
    for y in (y1, y2):
        c.line((x - 1.8) * mm, y * mm, (x + 1.8) * mm, y * mm)
    text(c, font, x + 2.4, (y1 + y2) / 2, size, label, color)


def draw_upper_line_dimension_node(c, regular, bold):
    """Large 1:15 dimension node for the compact kitchen-sofa-desk chain."""
    page_frame(
        c,
        regular,
        bold,
        "TV-001 - УВЕЛИЧЕННЫЙ УЗЕЛ ВЕРХНЕЙ ЛИНИИ",
        "Ключевые размеры в мм. М 1:15; габариты мебели - до выбора конкретных SKU.",
        5,
        "М 1:15",
    )
    scale = 1 / 15
    x0, top_y = 15.0, 230.0
    px = lambda model_x: x0 + model_x * scale
    width = 5710 * scale

    kitchen_x, kitchen_w, kitchen_h = px(0), 2400 * scale, 600 * scale
    sofa_x, sofa_w, sofa_h = px(2430), 2000 * scale, 1000 * scale
    desk_x, desk_w, desk_h = px(4510), 1200 * scale, 600 * scale
    kitchen_y = top_y - kitchen_h
    sofa_y = top_y - sofa_h
    desk_y = top_y - desk_h
    table_x, table_w, table_h = px(2470), 1400 * scale, 800 * scale
    table_y = sofa_y - table_h
    chair_w, chair_h = 400 * scale, 400 * scale
    chair_y = table_y - chair_h
    route_y, route_h = 20.0, 900 * scale

    # Outer top wall and top dimension chain.
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.55 * mm)
    c.line(x0 * mm, top_y * mm, (x0 + width) * mm, top_y * mm)
    text(c, bold, x0, top_y + 4.5, 5.0, "ВЕРХНЯЯ СТЕНА", INK)
    node_dim_h(c, regular, x0, x0 + width, 255, "5710 - чистый размер B01", INK, 5.3)
    node_dim_h(c, regular, kitchen_x, kitchen_x + kitchen_w, 244, "2400", INK, 5.0)
    node_dim_h(c, regular, kitchen_x + kitchen_w, sofa_x, 244, "30", ORANGE, 4.2)
    node_dim_h(c, regular, sofa_x, sofa_x + sofa_w, 244, "2000", INK, 5.0)
    node_dim_h(c, regular, sofa_x + sofa_w, desk_x, 244, "80", ORANGE, 4.2)
    node_dim_h(c, regular, desk_x, desk_x + desk_w, 244, "1200", INK, 5.0)

    # Upper wall furniture.
    node_box(c, kitchen_x, kitchen_y, kitchen_w, kitchen_h, KITCHEN, "#6e5a34")
    node_box(c, sofa_x, sofa_y, sofa_w, sofa_h, LOUNGE, "#6f625e", 4.0)
    node_box(c, desk_x, desk_y, desk_w, desk_h, WORK, "#4e7589")
    text(c, bold, kitchen_x + kitchen_w / 2, kitchen_y + 24, 5.1, "КУХНЯ", "#594626", center=True)
    text(c, regular, kitchen_x + kitchen_w / 2, kitchen_y + 16, 4.2, "2400 по верхней стене", "#594626", center=True)
    text(c, regular, kitchen_x + kitchen_w / 2, kitchen_y + 8, 4.0, "4000 общая длина фронтов; глубина 600", "#594626", center=True)
    text(c, bold, sofa_x + sofa_w / 2, sofa_y + 37, 5.0, "ДИВАН-КРОВАТЬ", "#544943", center=True)
    text(c, regular, sofa_x + sofa_w / 2, sofa_y + 27, 4.5, "2000 x 1000", "#544943", center=True)
    text(c, bold, desk_x + desk_w / 2, desk_y + 24, 4.7, "РАБОЧИЙ СТОЛ", "#2e5b70", center=True)
    text(c, regular, desk_x + desk_w / 2, desk_y + 15, 4.4, "1200 x 600", "#2e5b70", center=True)
    text(c, regular, desk_x + desk_w / 2, desk_y + 7, 3.9, "в правом верхнем углу", "#2e5b70", center=True)
    text(c, bold, kitchen_x + kitchen_w + 1.0, 204, 4.2, "30", ORANGE, center=True)
    text(c, regular, kitchen_x + kitchen_w + 1.0, 197, 3.4, "тех. зазор", ORANGE, center=True)
    text(c, bold, sofa_x + sofa_w + 3.3, 204, 4.2, "80", ORANGE, center=True)
    text(c, regular, sofa_x + sofa_w + 3.3, 197, 3.4, "тех. зазор", ORANGE, center=True)

    # Real HuanaXin CJ196 table directly at the sofa front and two folding chairs.
    node_box(c, table_x, table_y, table_w, table_h, DINING, "#506c4d", 3.0)
    c.setStrokeColor(HexColor("#6b8665")); c.setLineWidth(0.18 * mm)
    c.line((table_x + table_w / 2) * mm, table_y * mm, (table_x + table_w / 2) * mm, (table_y + table_h) * mm)
    for chair_x in (px(2620), px(3320)):
        node_box(c, chair_x, chair_y, chair_w, chair_h, "#f6f2ed", "#6d6258", 2.5)
    text(c, bold, table_x + table_w / 2, table_y + 27, 5.0, "HUANAXIN CJ196", "#405d3c", center=True)
    text(c, regular, table_x + table_w / 2, table_y + 17, 4.4, "1400 x 800", "#405d3c", center=True)
    text(c, regular, table_x + table_w / 2, table_y + 8, 3.9, "вплотную к дивану: зазор 0", "#405d3c", center=True)
    text(c, regular, table_x + table_w / 2, chair_y + 11, 3.55, "постоянный DAY: 2 стула max 400 x 400; при посадке занимают маршрут", "#5c5044", center=True)
    node_dim_v(c, regular, table_x + table_w + 4.0, table_y, table_y + table_h, "800", INK, 4.5)
    node_dim_h(c, regular, table_x, table_x + table_w, table_y - 4.0, "1400", INK, 4.5)
    text(c, bold, table_x + table_w + 8.0, sofa_y - 3.5, 4.2, "0", GOOD)
    text(c, regular, table_x + table_w + 8.0, sofa_y - 10.0, 3.4, "стол / диван", GOOD)

    # Clean primary route and the deliberately limited work-chair approach.
    c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.35 * mm); c.setDash(1.8 * mm, 1.0 * mm)
    c.rect(x0 * mm, route_y * mm, width * mm, route_h * mm, fill=0, stroke=1)
    c.setDash()
    text(c, bold, x0 + width / 2, route_y + 7.0, 4.9, "D2 -> O1: чистый маршрут 900", ORANGE, center=True)
    text(c, regular, x0 + width / 2, route_y + 15.0, 3.55, "свободен только с задвинутыми/убранными стульями", ORANGE, center=True)
    # Dedicated 600-mm approach to the desk chair from below.
    approach_x, approach_w = desk_x, 600 * scale
    c.setStrokeColor(HexColor(BLUE)); c.setLineWidth(0.30 * mm); c.setDash(1.5 * mm, 0.9 * mm)
    c.rect(approach_x * mm, route_y * mm, approach_w * mm, (sofa_y - route_y) * mm, fill=0, stroke=1)
    c.setDash()
    text(c, regular, approach_x + approach_w / 2, sofa_y - 6.0, 3.9, "подход к креслу снизу 600", BLUE, center=True)
    c.setFillColor(HexColor("#eff5f8")); c.setStrokeColor(HexColor("#4b6d82")); c.setLineWidth(0.20 * mm)
    c.circle((approach_x + approach_w / 2) * mm, (sofa_y + 7.0) * mm, 11.0 * mm, fill=1, stroke=1)
    text(c, regular, approach_x + approach_w / 2, sofa_y + 4.8, 3.5, "кресло", "#2e5b70", center=True)
    text(c, regular, x0, 26.0, 4.0, "Все размеры - между внешними габаритами мебели; 30 и 80 мм - технические зазоры, не проходы.", MUTED)
    c.showPage()


def schedule_panel(c, regular, bold, x, y, w, h, title, fill):
    node_box(c, x, y, w, h, fill, "#bdc7ce", 2.0)
    text(c, bold, x + 5, y + h - 9, 5.2, title)
    c.setStrokeColor(HexColor("#bdc7ce")); c.setLineWidth(0.20 * mm)
    c.line((x + 4) * mm, (y + h - 13) * mm, (x + w - 4) * mm, (y + h - 13) * mm)


def schedule_row(c, regular, bold, x, y, w, label, value, note, value_color=INK):
    text(c, regular, x, y + 7.2, 4.35, label, INK)
    text(c, bold, x + w, y + 7.0, 5.8, value, value_color, right=True)
    text(c, regular, x, y, 3.65, note, MUTED)
    c.setStrokeColor(HexColor("#d0d6db")); c.setLineWidth(0.12 * mm)
    c.line(x * mm, (y - 3.2) * mm, (x + w) * mm, (y - 3.2) * mm)


def draw_readable_dimension_schedule(c, regular, bold):
    """A large A3 schedule so users can read every key size without zooming."""
    page_frame(
        c,
        regular,
        bold,
        "TV-001 - КРУПНАЯ ВЕДОМОСТЬ РАЗМЕРОВ",
        "Все значения - мм; B01 фиксирует прямую правую стену 1300 + O1 1600 + 600; мебель - до SKU.",
        6,
        "РАЗМЕРЫ, ММ",
    )

    # Dimension ribbon: intentionally not to scale, made for legibility.
    text(c, bold, 15, 258, 5.0, "ВЕРХНЯЯ ЦЕПОЧКА B01 (размерная, не в масштабе)")
    ribbon_y, ribbon_h = 237, 16
    blocks = (
        (15, 135, KITCHEN, "КУХНЯ", "2400"),
        (150, 7, "#fff1d6", "", "30"),
        (157, 118, LOUNGE, "ДИВАН", "2000"),
        (275, 16, "#fff1d6", "ТЕХ. ЗАЗОР", "80"),
        (291, 94, WORK, "РАБОЧИЙ СТОЛ", "1200"),
    )
    for x, w, fill, label, value in blocks:
        node_box(c, x, ribbon_y, w, ribbon_h, fill, "#65717a", 1.8)
        text(c, bold, x + w / 2, ribbon_y + 9.0, 4.0 if w < 30 else 4.6, label, INK, center=True)
        text(c, bold, x + w / 2, ribbon_y + 3.0, 6.0 if w >= 30 else 5.0, value, ORANGE if value in ("30", "80") else INK, center=True)
    text(c, bold, 405, 242.5, 6.3, "= 5710", INK, right=True)
    text(c, regular, 15, 229, 4.0, "30 и 80 мм - технические зазоры, не проходы. Рабочий стол остается в правом верхнем углу.", BAD)

    schedule_panel(c, regular, bold, 15, 45, 187, 176, "МЕБЕЛЬ И КУХНЯ", PALE_BLUE)
    left_rows = (
        ("Контур B01 по проектному ТЗ", "5710 x 3500", "не подменяет контрольный обмер"),
        ("Кухня: участок по верхней стене", "2400 x 600", "4 модуля по 600; справа пенал СВЧ/духовки"),
        ("Кухня: общая длина Г-фронтов", "4000", "2400 верх + 1600 левая ветвь"),
        ("Диван-кровать, внешний габарит", "2000 x 1000", "ночное место 2000 x 1400"),
        ("Рабочий стол", "1200 x 600", "кресло: конверт max 600 x 620"),
        ("ТВ / медиа-тумба", "1600 x 300", "65 дюймов рекоменд.; 75 - только после SKU"),
        ("Складной стол HuanaXin CJ196", "800 x 110 / 1400 x 800", "сложен / обеденный режим; без колес"),
    )
    y = 197
    for label, value, note in left_rows:
        schedule_row(c, regular, bold, 20, y, 177, label, value, note)
        y -= 21

    schedule_panel(c, regular, bold, 213, 45, 192, 176, "ГОСТИ, ЗАЗОРЫ И ПРОХОДЫ", PALE_GREEN)
    right_rows = (
        ("Левая ветвь кухни: рабочая зона", "700", "перед фасадами ПММ и хранения", GOOD),
        ("CJ196, ежедневно открыт", "1400 x 800", "70 мм до торца кухни; зазор не проход", GOOD),
        ("CJ196, гости: сдвиг вправо", "+200", "270 мм до кухни; ближе к центру дивана", GOOD),
        ("Посадка на 4", "2 + 2", "2 места диван + 2 складных стула", INK),
        ("Складной стул x2", "max 400 x 400", "контур для сохранения прохода", INK),
        ("Стол -> диван", "0", "контакт габаритов, без зазора", GOOD),
        ("Кухня -> диван", "30", "технический зазор, не проход", BAD),
        ("Диван -> рабочий стол", "80", "технический зазор, не проход", BAD),
        ("Диван -> фасад ТВ-тумбы", "2200", "проектная дистанция просмотра", INK),
        ("Правая фасадная стена B01", "3500", "одна прямая: 1300 + O1 1600 + 600", GOOD),
        ("D2 -> O1, чистый маршрут", "900", "при задвинутых/убранных стульях", ORANGE),
        ("Подход к креслу снизу", "600", "чистая полоса; не размер кресла", BLUE),
    )
    y = 202
    for label, value, note, color in right_rows:
        schedule_row(c, regular, bold, 218, y, 182, label, value, note, color)
        y -= 15.5

    node_box(c, 15, 24, 390, 14, PALE_RED, "#dcaaa4", 1.6)
    text(c, bold, 20, 31.5, 4.4, "ВАЖНО", BAD)
    text(c, regular, 48, 31.5, 4.0, "CJ196: DAY 70 мм до кухни; ГОСТИ +200 мм = 270. 900 D2->O1 - только без выдвинутых стульев.", BAD)
    c.showPage()


def draw_permanent_table_design_nodes(c, regular, bold):
    """Sheet 7: compact non-construction design notes for the fixed daily table."""
    page_frame(
        c,
        regular,
        bold,
        "TV-001 - ДИЗАЙНЕРСКИЕ УЗЛЫ ПОСТОЯННОГО СТОЛА",
        "Концептуальные узлы, не рабочий проект. Точки, высоты, трассы и SKU - после контрольного обмера.",
        7,
        "СХЕМАТИЧНО",
    )

    node_box(c, 15, 238, 390, 23, PALE_RED, "#dcaaa4", 2.4)
    text(c, bold, 22, 251.5, 5.7, "НЕ МЕНЯТЬ РАССТАНОВКУ", BAD)
    text(c, bold, 22, 243.5, 5.0, "DAY 70; ГОСТИ +200 = 270; 900 только с задвинутыми стульями", BAD)

    # A: kitchen end / permanent table plan and removable spacers.
    node_box(c, 15, 137, 187, 90, PALE_ORANGE, "#c79d5a", 2.4)
    text(c, bold, 21, 217, 5.2, "A. ТОРЕЦ КУХНИ + ПОСТОЯННЫЙ СТОЛ", "#6e5a34")
    text(c, regular, 21, 210, 3.7, "ПЛАН / ПРОВЕРЯЕМЫЙ УЗЕЛ DAY", MUTED)
    # schematic: kitchen end, 70-mm gap, table and gliders
    node_box(c, 24, 166, 42, 29, KITCHEN, "#6e5a34", 1.5)
    text(c, bold, 45, 178, 4.2, "ТОРЕЦ\nКУХНИ", "#5b4827", center=True)
    c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.25 * mm)
    c.line(66 * mm, 180 * mm, 80 * mm, 180 * mm)
    c.line(66 * mm, 177 * mm, 66 * mm, 183 * mm); c.line(80 * mm, 177 * mm, 80 * mm, 183 * mm)
    text(c, bold, 73, 184, 4.4, "70", ORANGE, center=True)
    node_box(c, 80, 166, 66, 29, DINING, "#506c4d", 2.2)
    text(c, bold, 113, 179, 4.3, "CJ196 DAY", "#405d3c", center=True)
    for x in (88, 138):
        for y in (170, 190):
            c.setFillColor(HexColor("#f4efe2")); c.setStrokeColor(HexColor("#776b58")); c.circle(x * mm, y * mm, 2.2 * mm, fill=1, stroke=1)
    wrapped(c, regular, 153, 187, 3.75, "4 одинаковых глайдера 25-30; выбрать после теста на плитке и реальном весе.", 30, INK, 4.4)
    text(c, regular, 22, 155, 3.85, "Скрытый демпфер под столешницей: удар не принимает лицевой фасад кухни.", INK)
    text(c, regular, 22, 147, 3.85, "Съёмная проставка DAY 70 / ГОСТИ 270; один комплект глайдеров на все 4 опоры.", INK)

    # B: lighting range for two table positions.
    node_box(c, 213, 137, 192, 90, PALE_BLUE, "#6d9bb1", 2.4)
    text(c, bold, 219, 217, 5.2, "B. СВЕТ НАД ДВУМЯ ПОЛОЖЕНИЯМИ", "#2f6e8d")
    text(c, regular, 219, 210, 3.7, "ПОТОЛОК / ОРИЕНТИР, НЕ МОНТАЖНАЯ СХЕМА", MUTED)
    c.setStrokeColor(HexColor("#60727d")); c.setLineWidth(0.55 * mm)
    c.line(228 * mm, 194 * mm, 388 * mm, 194 * mm)
    c.setStrokeColor(HexColor("#2f6e8d")); c.setLineWidth(0.7 * mm)
    c.line(252 * mm, 187 * mm, 358 * mm, 187 * mm)
    text(c, regular, 305, 190.5, 3.6, "трек ориент. 1600 вдоль длинной стороны", BLUE, center=True)
    c.setStrokeColor(HexColor("#2f6e8d")); c.setLineWidth(0.18 * mm)
    for x in (285, 329):
        c.line(x * mm, 187 * mm, x * mm, 174 * mm)
        c.setFillColor(HexColor("#f5e6a6")); c.circle(x * mm, 172 * mm, 3.5 * mm, fill=1, stroke=1)
    c.setDash(1.2 * mm, 0.8 * mm); c.setStrokeColor(HexColor(ORANGE)); c.rect(248 * mm, 153 * mm, 92 * mm, 14 * mm, fill=0, stroke=1); c.setDash()
    text(c, regular, 294, 157, 3.65, "диапазон DAY 70 + ГОСТИ 270; ось около x3270", ORANGE, center=True)
    text(c, regular, 220, 145, 3.8, "2 регулируемых, 3000K, CRI90+: проверить высоту, электровывод, блики и обе позиции.", INK)

    # C: sofa/table section and seating ergonomics.
    node_box(c, 15, 37, 187, 90, PALE_GREEN, "#78a181", 2.4)
    text(c, bold, 21, 117, 5.2, "C. РАЗРЕЗ: ДИВАН / СТОЛ", "#426b4b")
    text(c, regular, 21, 110, 3.7, "ЭРГОНОМИКА ДО ВЫБОРА КОНКРЕТНОГО SKU", MUTED)
    c.setStrokeColor(HexColor("#65717a")); c.setLineWidth(0.25 * mm); c.line(24 * mm, 59 * mm, 188 * mm, 59 * mm)
    node_box(c, 30, 59, 44, 23, LOUNGE, "#6f625e", 2.0)
    c.setStrokeColor(HexColor("#6f625e")); c.setLineWidth(0.30 * mm); c.line(34 * mm, 82 * mm, 34 * mm, 99 * mm); c.line(34 * mm, 99 * mm, 68 * mm, 99 * mm)
    node_box(c, 100, 76, 48, 4, DINING, "#506c4d", 1.0)
    c.setStrokeColor(HexColor("#506c4d")); c.setLineWidth(0.32 * mm); c.line(108 * mm, 76 * mm, 108 * mm, 59 * mm); c.line(140 * mm, 76 * mm, 140 * mm, 59 * mm)
    node_dim_v(c, regular, 152, 59, 80, "740-760", "#405d3c", 3.7)
    node_dim_v(c, regular, 78, 59, 79, "430-470", "#544943", 3.7)
    text(c, regular, 23, 49, 3.85, "Желателен R40-60; проверить подстолье, колени и механизм по реальному SKU.", INK)
    text(c, regular, 23, 42, 3.85, "Перед раскрытием дивана стол переместить в заранее проверенную сервисную позицию.", BAD)

    # D: sofa wall / terrace window / concealed services.
    node_box(c, 213, 37, 192, 90, PALE_GREEN, "#78a181", 2.4)
    text(c, bold, 219, 117, 5.2, "D. СТЕНА ДИВАНА / ТЕРРАСА / КАБЕЛИ", "#426b4b")
    text(c, regular, 219, 110, 3.7, "АТМОСФЕРА И СЕРВИС, НЕ ЭЛЕКТРОПРОЕКТ", MUTED)
    # wall, acoustic panels, window and media service schematic
    c.setStrokeColor(HexColor("#65717a")); c.setLineWidth(0.45 * mm); c.line(226 * mm, 66 * mm, 226 * mm, 101 * mm)
    for x in (239, 267):
        node_box(c, x, 78, 21, 18, "#e4d9cf", "#9a887b", 1.2)
        text(c, regular, x + 10.5, 85, 3.1, "АКУСТ.\nПАННО", "#66584f", center=True)
    node_box(c, 296, 64, 35, 38, "#d7eef7", "#477890", 1.1)
    text(c, regular, 313.5, 80, 3.3, "O1\nТЕРРАСА", BLUE, center=True)
    c.setStrokeColor(HexColor("#65717a")); c.setLineWidth(0.25 * mm); c.setDash(1.0 * mm, 0.6 * mm)
    c.line(344 * mm, 94 * mm, 381 * mm, 94 * mm); c.line(344 * mm, 94 * mm, 344 * mm, 70 * mm); c.setDash()
    node_box(c, 344, 61, 43, 9, MEDIA, "#624a59", 1.0)
    text(c, regular, 365.5, 64, 3.2, "TV: вентиляция", "#4d3743", center=True)
    text(c, regular, 219, 51, 3.7, "Панно 25-40: звукопоглощение, не звукоизоляция. Штор и ковра в D2->O1 нет.", INK)
    text(c, regular, 219, 44.5, 3.7, "Плёнка O1 - только с письменным допуском производителя стеклопакета и согласованием фасада.", INK)
    text(c, regular, 219, 38.5, 3.7, "РМ: лоток; питание/Cat6 - электропроект. TV: вентиляция по SKU. Не перекрывать O1.", INK)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3), pageCompression=1)
    c.setTitle("TV-001 - диван у верхней стены и ТВ у нижней")
    c.setAuthor("Codex")
    draw_page(c, regular, bold, "day")
    draw_page(c, regular, bold, "meal")
    draw_page(c, regular, bold, "night")
    draw_page(c, regular, bold, "guest")
    draw_upper_line_dimension_node(c, regular, bold)
    draw_readable_dimension_schedule(c, regular, bold)
    draw_permanent_table_design_nodes(c, regular, bold)
    c.save()
    shutil.copy2(TMP_PDF, OUT_PDF)
    print(f"PASS TV-001 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
