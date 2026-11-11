# -*- coding: utf-8 -*-
"""Build KLV-003: two scale-accurate U and L kitchen-living layouts.

This source deliberately keeps every planning coordinate in millimetres.  It is
not an order drawing: water, ventilation, door swing, radiator and final SKU
dimensions remain verification gates before construction or purchase.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "KLV-003_два_варианта_П-и-Г_кухни_М1-25_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "KLV-003_два_варианта_П-и-Г_кухни_М1-25.pdf"

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
ORANGE = "#ad6800"
BLUE = "#2f6e8d"
PALE_ORANGE = "#fff6e8"
PALE_BLUE = "#eef7fb"
PALE_GREEN = "#eff8f1"
PALE_RED = "#fff1ef"

ROOM = (0, 0, 5710, 3500)
D2_GUARD = (0, 0, 1200, 1300)
U_ROUTES = ((0, 350, 5710, 1250), (4810, 350, 5710, 2450))
L_ROUTES = (
    (1200, 900, 2100, 2650),
    (1200, 1750, 4810, 2650),
    (4810, 350, 5710, 2450),
    (4510, 2450, 5110, 2900),
)

U_FIXED = {
    "kitchen_top": (0, 2900, 2400, 3500),
    "kitchen_left": (0, 1350, 600, 2900),
    "kitchen_right": (1800, 1900, 2400, 2900),
    "desk": (2500, 2800, 3700, 3500),
    "sofa": (2500, 1350, 3950, 2050),
    "media": (2500, 0, 3950, 300),
    "chair_bank": (4050, 2700, 4500, 3500),
    "dining_table": (4500, 2700, 5300, 3500),
    "banquette": (5300, 2700, 5710, 3500),
}
U_DYNAMIC = {"desk_chair": (2700, 2050, 3600, 2800)}

L_FIXED = {
    "kitchen_top": (0, 2900, 3410, 3500),
    "kitchen_left": (0, 1300, 600, 2900),
    "desk": (4510, 2900, 5710, 3500),
    "sofa_wall": (2150, 0, 3950, 600),
    "table_open": (2150, 500, 3950, 1250),
    "chair_kitchen_1": (2450, 1250, 2950, 1700),
    "chair_kitchen_2": (3150, 1250, 3650, 1700),
}
L_DYNAMIC = {"desk_chair": (5110, 2490, 5710, 3110)}


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def validate_variant(
    name: str,
    fixed: dict[str, tuple[int, int, int, int]],
    dynamic: dict[str, tuple[int, int, int, int]],
    routes: tuple[tuple[int, int, int, int], ...],
    allowed_fixed_pairs: set[frozenset[str]] | None = None,
    allowed_dynamic_fixed: set[frozenset[str]] | None = None,
) -> None:
    allowed_fixed_pairs = allowed_fixed_pairs or set()
    allowed_dynamic_fixed = allowed_dynamic_fixed or set()
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
    names = list(fixed)
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            if frozenset((left, right)) in allowed_fixed_pairs:
                continue
            if overlap(fixed[left], fixed[right]):
                raise AssertionError(f"{name}: fixed overlap {left}/{right}")
    for moving, moving_rect in dynamic.items():
        for item, fixed_rect in fixed.items():
            if frozenset((moving, item)) in allowed_dynamic_fixed:
                continue
            if overlap(moving_rect, fixed_rect):
                raise AssertionError(f"{name}: dynamic overlap {moving}/{item}")
    # A dynamic chair can reach an adjacent object only where this is explicitly planned.
    if name == "U":
        assert fixed["sofa"][3] == dynamic["desk_chair"][1] == 2050
        assert not overlap(fixed["sofa"], dynamic["desk_chair"])
        assert 1800 - 600 == 1200
        assert fixed["chair_bank"][1] - U_ROUTES[1][3] == 250
    if name == "L":
        assert fixed["sofa_wall"][0] - L_ROUTES[0][2] == 50
        assert fixed["sofa_wall"][3] - fixed["table_open"][1] == 100
        assert L_ROUTES[1][1] - fixed["chair_kitchen_1"][3] == 50
        assert fixed["kitchen_top"][1] - L_ROUTES[1][3] == 250
        assert L_ROUTES[3] == (4510, 2450, 5110, 2900)
        assert L_ROUTES[3][2] == dynamic["desk_chair"][0] == 5110
        assert L_ROUTES[3][3] == fixed["desk"][1] == 2900
        assert L_ROUTES[3][2] - L_ROUTES[3][0] == 600
        assert dynamic["desk_chair"][1] - L_ROUTES[2][3] == 40
        assert dynamic["desk_chair"][0] - fixed["desk"][0] == 600
        chair_symbol = (5410 - 264, 2800 - 249, 5410 + 264, 2800 + 284)
        chair_envelope = dynamic["desk_chair"]
        assert chair_envelope[0] <= chair_symbol[0] and chair_symbol[2] <= chair_envelope[2]
        assert chair_envelope[1] <= chair_symbol[1] and chair_symbol[3] <= chair_envelope[3]
        assert fixed["desk"][0] - fixed["kitchen_top"][2] == 1100
        assert (fixed["sofa_wall"][2] - fixed["sofa_wall"][0]) / 3 == 600


def validate_geometry() -> None:
    validate_variant("U", U_FIXED, U_DYNAMIC, U_ROUTES)
    validate_variant(
        "L", L_FIXED, L_DYNAMIC, L_ROUTES,
        {frozenset(("sofa_wall", "table_open"))},
        {frozenset(("desk_chair", "desk"))},
    )
    assert D2_GUARD == (0, 0, 1200, 1300)
    print("PASS KLV-003 geometry: U and revised L fixed/dynamic envelopes, D2 guard and 900-mm D2->O1 routes")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=None, bullet=None):
    leading = leading or size * 1.28
    lines = base.wrap(value, width)
    for index, line in enumerate(lines):
        prefix = bullet if index == 0 and bullet else ("  " if bullet else "")
        text(c, font, x, y, size, prefix + line, color)
        y -= leading
    return y


def page_frame(c, regular, bold, title, subtitle, sheet, scale_label="М 1:25"):
    page_w, page_h = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, page_w - 16 * mm, page_h - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13, title)
    text(c, regular, 14, 274, 5.1, subtitle, MUTED)
    text(c, regular, 406, 14, 4.1, f"KLV-003 | лист {sheet}/3 | {scale_label}", MUTED, right=True)


def pale_panel(c, x, y, w, h, fill, title, regular, bold):
    base.box(c, x, y, w, h, fill, "#b8c1c8", 0.18, 2.0)
    text(c, bold, x + 3, y + h - 5, 5.0, title)


def dashed_model(c, x, y, w, h, color, label, regular, label_y=None):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(0.22 * mm); c.setDash(1.4 * mm, 0.8 * mm)
    c.rect(base.qx(x) * mm, base.qy(y) * mm, base.p(w) * mm, base.p(h) * mm, fill=0, stroke=1)
    c.setDash()
    base.label_model(c, regular, x + w / 2, label_y or y + h / 2, label, 2.8, color)


def draw_d2_guard(c, regular):
    c.setFillColor(HexColor(PALE_ORANGE)); c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.18 * mm)
    c.setDash(1.2 * mm, 0.8 * mm)
    c.rect(base.qx(0) * mm, base.qy(0) * mm, base.p(1200) * mm, base.p(1300) * mm, fill=1, stroke=1)
    c.setDash()
    base.label_model(c, regular, 600, 1160, "D2 GUARD 1200x1300", 3.0, ORANGE)


def draw_route_rect(c, rect, regular, label=None, label_at=None):
    x1, y1, x2, y2 = rect
    c.setStrokeColor(HexColor(ROUTE)); c.setLineWidth(0.35 * mm); c.setDash(1.8 * mm, 1.0 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()
    if label and label_at:
        base.label_model(c, regular, label_at[0], label_at[1], label, 2.8, ORANGE)


def draw_route_l(c, regular):
    draw_route_rect(c, L_ROUTES[0], regular, "900 от D2", (1650, 1760))
    draw_route_rect(c, L_ROUTES[1], regular, "проход 900 над столом", (3450, 2580))
    draw_route_rect(c, L_ROUTES[2], regular, "900 к O1", (5260, 2380))
    x1, y1, x2, y2 = L_ROUTES[3]
    c.setStrokeColor(HexColor(BLUE)); c.setLineWidth(0.35 * mm); c.setDash(1.8 * mm, 1.0 * mm)
    c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
    c.setDash()
    base.label_model(c, regular, 4810, 2840, "доступ к РМ 600", 2.8, BLUE)


def draw_shell(c, regular, bold, mode):
    base.draw_room_shell(c, regular, bold, mode)
    draw_d2_guard(c, regular)
    if mode == "U":
        base.draw_route(c, regular, 900)
        base.label_model(c, regular, 3400, 1270, "проход D2 -> O1 900", 3.0, ORANGE)
        base.label_model(c, regular, 5260, 2385, "O1 зона разворота", 2.8, ORANGE)
    else:
        draw_route_l(c, regular)


def kitchen_module(c, regular, x, y, w, h, label, fill=KITCHEN):
    base.model_box(c, x, y, w, h, fill, "#6e5a34", 0.20)
    base.label_model(c, regular, x + w / 2, y + h / 2 - 15, label, 2.8, "#5b4827")


def draw_sink(c, x, y):
    base.model_box(c, x + 100, y + 130, 340, 240, "#edf2f2", "#617377", 0.12, 24)
    base.model_line(c, x + 270, y + 370, x + 270, y + 460, "#617377", 0.16)


def draw_hob(c, x, y):
    for dx, dy in ((150, 150), (380, 150), (150, 360), (380, 360)):
        c.setStrokeColor(HexColor("#5b4827")); c.setLineWidth(0.14 * mm)
        c.circle(base.qx(x + dx) * mm, base.qy(y + dy) * mm, base.p(68) * mm, fill=0, stroke=1)


def draw_kitchen_u(c, regular, bold):
    for x, w, label in ((0, 600, "K00 УГОЛ"), (600, 600, "K01 ХОЛ."), (1200, 600, "K02 ПЕНАЛ"), (1800, 600, "K03 МОЙКА")):
        kitchen_module(c, regular, x, 2900, w, 600, label, "#e7ca90" if "ХОЛ" in label or "ПЕНАЛ" in label else KITCHEN)
    draw_sink(c, 1800, 2900)
    for y, h, label in ((1350, 550, "K04 ПММ"), (1900, 500, "K05 ЯЩ."), (2400, 500, "K06 ВАРКА")):
        kitchen_module(c, regular, 0, y, 600, h, label)
    draw_hob(c, 0, 2400)
    for y, h, label in ((1900, 500, "K07 ЯЩ."), (2400, 500, "K08 ПОДГ.")):
        kitchen_module(c, regular, 1800, y, 600, h, label)
    base.label_model(c, bold, 1200, 3425, "П-КУХНЯ: 4950 мм фронтов", 4.2, "#6e5a34")
    dashed_model(c, 600, 1900, 1200, 1000, BLUE, "внутри П: 1200", regular, 2400)


def draw_kitchen_l(c, regular, bold):
    top_modules = (
        (0, 600, "K00 УГОЛ"),
        (600, 600, "K01 МОЙКА"),
        (1200, 600, "K02 ПММ"),
        (1800, 700, "K03 ПОДГ."),
        (2500, 600, "K04 ВАРКА"),
        (3100, 310, "K05 ЯЩ."),
    )
    for x, w, label in top_modules:
        kitchen_module(c, regular, x, 2900, w, 600, label)
    draw_sink(c, 600, 2900)
    draw_hob(c, 2500, 2900)
    for y, h, label in ((1300, 600, "K06 ХОЛ."), (1900, 500, "K07 ПЕНАЛ"), (2400, 500, "K08 ХОЗ.")):
        kitchen_module(c, regular, 0, y, 600, h, label, "#e7ca90" if "ХОЛ" in label or "ПЕНАЛ" in label else KITCHEN)
    base.label_model(c, bold, 1705, 3425, "Г-КУХНЯ: 5010 мм фронтов", 4.2, "#6e5a34")


def draw_desk(c, regular, x, y, h=700, active_center=None):
    cx = x + 600 if active_center is None else active_center
    work_label = "стол вдоль 5710" if active_center is None else "рабочая зона справа"
    base.model_box(c, x, y, 1200, h, WORK, "#4e7589", 0.24, 40)
    divider = x + 600 if active_center is None else x + 400
    base.model_line(c, divider, y + 70, divider, y + h - 70, "#6a94a8", 0.14)
    base.model_box(c, cx - 170, y + h / 2 - 55, 340, 110, "#f3f7f8", "#4e7589", 0.12, 12)
    base.label_model(c, regular, cx, y + h * 0.68, f"РМ 1200x{h}", 3.7, "#2e5b70")
    base.label_model(c, regular, cx, y + h * 0.48, work_label, 2.8, "#2e5b70")


def draw_task_chair_compact(c, cx, cy):
    """Draw a chair symbol wholly inside the declared 600x620 dynamic envelope."""
    c.setFillColor(HexColor("#eff5f8")); c.setStrokeColor(HexColor("#4b6d82")); c.setLineWidth(0.18 * mm)
    c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(230) * mm, fill=1, stroke=1)
    for dx, dy in ((0, 260), (240, 70), (150, -225), (-150, -225), (-240, 70)):
        base.model_line(c, cx, cy, cx + dx, cy + dy, "#4b6d82", 0.15)
        c.setFillColor(HexColor("#4b6d82"))
        c.circle(base.qx(cx + dx) * mm, base.qy(cy + dy) * mm, base.p(24) * mm, fill=1, stroke=0)
    base.model_box(c, cx - 205, cy + 190, 410, 85, "#d5e7f2", "#4b6d82", 0.16, 30)


def draw_sofa(c, regular, x, y, w=1300, h=650):
    base.model_box(c, x, y, w, h, LOUNGE, "#745e53", 0.24, 65)
    for px in (x + 80, x + w / 2 - 200, x + w - 480):
        base.model_box(c, px, y + 115, 330, max(280, h - 350), "#f0e8e2", "#8b756b", 0.10, 26)
    base.label_model(c, regular, x + w / 2, y + 55, f"диван {w}x{h}", 3.4, "#624f47")


def draw_media(c, regular, x, y, w=1300):
    base.model_box(c, x, y, w, 300, MEDIA, "#7d6072", 0.20, 20)
    base.model_box(c, x + w / 2 - 210, y + 55, 420, 150, "#202b37", "#6b5063", 0.12, 12)
    base.label_model(c, regular, x + w / 2, y + 220, "ТВ / медиа", 2.8, "#624655")


def draw_dining(c, regular, x_table, x_chair, x_bench):
    base.model_box(c, x_table, 2700, 800, 800, DINING, "#506c4d", 0.24, 40)
    base.model_line(c, x_table + 400, 2700, x_table + 400, 3500, "#6b8665", 0.14)
    base.model_line(c, x_table, 3100, x_table + 800, 3100, "#6b8665", 0.14)
    for y in (2700, 3100):
        base.draw_chair(c, x_chair + 25, y + 35, 360, 320, facing="right")
    bench_w = 5710 - x_bench
    base.model_box(c, x_bench, 2700, bench_w, 800, "#d5e7cf", "#506c4d", 0.22, min(44, bench_w / 8))
    base.label_model(c, regular, x_table + 400, 3115, "СТОЛ", 3.2, "#405d3c")
    base.label_model(c, regular, x_table + 400, 2980, "800x800", 3.0, "#405d3c")
    base.label_model(c, regular, x_bench + bench_w / 2, 3080, "банкетка", 2.8, "#405d3c")


def draw_wall_sofa_table_l(c, regular, bold):
    # The sofa is fixed to the lower 5710-mm wall.  The opened tabletop projects
    # 100 mm over the upholstered footprint, so a central pedestal is mandatory.
    # This yields 600 mm per person on the sofa and two loose kitchen-side chairs.
    draw_sofa(c, regular, 2150, 0, 1800, 600)
    for x in (2750, 3350):
        base.model_line(c, x, 0, x, 600, "#8d756c", 0.12)
    base.label_model(c, bold, 3050, 455, "3 МЕСТА НА ДИВАНЕ | 3x600", 3.1, "#624f47")

    base.model_box(c, 2150, 500, 1800, 750, DINING, "#506c4d", 0.25, 42)
    for x in (2750, 3350):
        base.model_line(c, x, 500, x, 1250, "#6b8665", 0.14)
    # Central pedestal keeps the sofa-side knee space usable.
    base.model_box(c, 2925, 735, 250, 280, "#d8e2d5", "#506c4d", 0.18, 12)
    base.label_model(c, bold, 3050, 1010, "СТОЛ РАЗЛОЖЕН 1800x750", 3.5, "#405d3c")
    base.label_model(c, regular, 3050, 865, "сложенный 1200x750 - по SKU", 2.8, "#405d3c")
    base.label_model(c, regular, 3050, 745, "центральное подстолье", 2.6, "#405d3c")

    base.draw_chair(c, 2450, 1250, 500, 450, facing="down")
    base.draw_chair(c, 3150, 1250, 500, 450, facing="down")
    base.label_model(c, bold, 3050, 1645, "2 СТУЛА СО СТОРОНЫ КУХНИ", 3.0, "#405d3c")
    base.model_line(c, 2050, 500, 2050, 600, ORANGE, 0.18)
    base.label_model(c, regular, 2090, 560, "нахлест столешницы 100", 2.7, ORANGE, center=False)


def dimensions(c, regular, layout):
    # Overall model dimensions, plus primary furniture dimensions shown at scale.
    base.dim_h(c, regular, base.OX, base.OX + base.p(5710), base.OY - 5.0, "5710 - чистый размер B01")
    if layout == "U":
        base.dim_h(c, regular, base.qx(0), base.qx(2400), base.qy(2860), "2400")
        base.dim_v(c, regular, base.qx(2460), base.qy(2800), base.qy(3500), "700")
        base.dim_h(c, regular, base.qx(2500), base.qx(3700), base.qy(2770), "1200")
        base.dim_h(c, regular, base.qx(2500), base.qx(3950), base.qy(1310), "1450")
        base.dim_v(c, regular, base.qx(3980), base.qy(1350), base.qy(2050), "700")
        base.dim_h(c, regular, base.qx(4500), base.qx(5300), base.qy(3440), "800")
    else:
        base.dim_h(c, regular, base.qx(0), base.qx(3410), base.qy(2860), "3410")
        base.dim_h(c, regular, base.qx(3410), base.qx(4510), base.qy(2860), "1100")
        base.dim_h(c, regular, base.qx(4510), base.qx(5710), base.qy(2860), "1200")
        base.dim_v(c, regular, base.qx(4470), base.qy(2900), base.qy(3500), "600")
        base.dim_h(c, regular, base.qx(2150), base.qx(3950), base.qy(460), "1800")
        base.dim_v(c, regular, base.qx(3990), base.qy(0), base.qy(600), "600")
        base.dim_v(c, regular, base.qx(3990), base.qy(500), base.qy(1250), "750")


def draw_variant_page(c, regular, bold, mode):
    is_u = mode == "U"
    title = "ВАРИАНТ U - П-КУХНЯ" if is_u else "ВАРИАНТ L - Г-КУХНЯ"
    subtitle = "B01 5710x3500 мм. Мебель и техника - проектные габариты; D2/O1 и контур B01 сохранены."
    page_frame(c, regular, bold, title, subtitle, 1 if is_u else 2)
    draw_shell(c, regular, bold, mode)
    if is_u:
        draw_kitchen_u(c, regular, bold)
        draw_desk(c, regular, 2500, 2800)
        dashed_model(c, 2700, 2050, 900, 750, BLUE, "РМ стул 750", regular, 2410)
        base.draw_task_chair(c, 3150, 2425, "up")
        draw_sofa(c, regular, 2500, 1350, 1450, 700)
        draw_media(c, regular, 2500, 0, 1450)
        draw_dining(c, regular, 4500, 4050, 5300)
        dimensions(c, regular, "U")
        capacity = "Хранение: 1.55-1.75 м3 полезного объема, без холодильника и ПММ."
        verdict = "Плюс: максимум закрытых фронтов. Минус: диван 1450x700 и компактная зона стула 750 касаются по y=2050; прохода между ними нет."
        use = "Сценарий: стол на 4 ежедневно. Ужин на 6 - только концепция после выбора раскладного SKU и временных стульев. Социально: 6-7."
    else:
        draw_kitchen_l(c, regular, bold)
        draw_desk(c, regular, 4510, 2900, 600, 5410)
        dashed_model(c, 5110, 2490, 600, 620, BLUE, "РМ кресло max 600x620", regular, 2620)
        draw_task_chair_compact(c, 5410, 2800)
        draw_wall_sofa_table_l(c, regular, bold)
        dimensions(c, regular, "L")
        capacity = "Хранение: ориентир 1.65-1.85 м3 полезного объема, без холодильника и ПММ."
        verdict = "Диван-банкетка 1800x600 стоит у длинной стены. Стол 1800x750 перед ним: 3 места по 600 на диване и 2 стула со стороны кухни."
        use = "РМ оставлено как на вашей схеме: 1200x600 справа сверху. Слева от кресла выделен боковой доступ 600; в разложенном режиме 5 мест и маршрут 900 к O1 сохранен."

    pale_panel(c, 255, 213, 151, 50, PALE_BLUE, "ЧТО ПРОВЕРЕНО ГЕОМЕТРИЕЙ", regular, bold)
    yy = 253
    for line in ("- B01: 5710x3500 мм", "- D2 guard: 1200x1300 мм", "- маршрут D2 -> O1: 900 мм", "- мебель не входит в guard и маршрут"):
        text(c, regular, 259, yy, 4.1, line, INK); yy -= 6.0
    pale_panel(c, 255, 142, 151, 62, PALE_GREEN if not is_u else PALE_ORANGE, "СЦЕНАРИЙ И КОМПРОМИСС", regular, bold)
    yy = 194
    for para in (capacity, verdict, use):
        yy = wrapped(c, regular, 259, yy, 4.1, para, 51, INK, 5.2, "-") - 1.8
    pale_panel(c, 255, 74, 151, 58, "#f7f7f7", "КАК ЧИТАТЬ ЛИСТ", regular, bold)
    yy = 122
    for line in ("Пунктир синий - динамика стула.", "Пунктир оранжевый - D2 guard и", "сохраняемый маршрут к террасе.", "Темный контур - предмет в масштабе."):
        text(c, regular, 259, yy, 4.0, line, MUTED); yy -= 5.4
    pale_panel(c, 255, 25, 151, 39, PALE_RED, "НЕ ДЛЯ ЗАКАЗА БЕЗ ПРОВЕРКИ", regular, bold)
    yy = 54
    for line in ("Вода/канализация, вытяжка, D2/O1 створки,", "радиатор/шторы, E-01 и реальные SKU - н/д."):
        text(c, regular, 259, yy, 3.9, line, BAD); yy -= 5.4
    c.showPage()


def compare_metric(c, regular, bold, y, label, u, l, winner):
    text(c, bold, 18, y, 5.0, label)
    base.box(c, 115, y - 3.4, 110, 7.0, "#fff7e8" if winner == "U" else "#f7f7f7", "#cfd5d8", 0.14, 1.3)
    base.box(c, 230, y - 3.4, 110, 7.0, "#eff8f1" if winner == "L" else "#f7f7f7", "#cfd5d8", 0.14, 1.3)
    text(c, regular, 118, y - 0.2, 4.2, u)
    text(c, regular, 233, y - 0.2, 4.2, l)


def draw_comparison_page(c, regular, bold):
    page_frame(c, regular, bold, "СРАВНЕНИЕ - ВЫБОР ДЛЯ СЕМЬИ И ГОСТЕЙ", "Оба варианта соблюдают B01, D2 guard и маршрут D2 -> O1. Оценки хранения и вместимости ориентировочные.", 3, "эскизы М 1:40")
    text(c, bold, 91.5, 258, 7.0, "U - П-КУХНЯ", center=True)
    text(c, bold, 301.5, 258, 7.0, "L - Г-КУХНЯ", center=True)

    # Compact true-scale thumbnails using the same coordinates, intentionally reduced to fit the page.
    old_ox, old_oy, old_scale = base.OX, base.OY, base.SCALE
    try:
        base.SCALE = 1 / 40
        base.OX, base.OY = 20.0, 112.0
        base.box(c, base.OX, base.OY, base.p(5710), base.p(3500), "#ffffff", INK, 0.42)
        draw_d2_guard(c, regular); base.draw_route(c, regular, 900); draw_kitchen_u(c, regular, bold)
        draw_desk(c, regular, 2500, 2800); draw_sofa(c, regular, 2500, 1350, 1450, 700); draw_media(c, regular, 2500, 0, 1450); draw_dining(c, regular, 4500, 4050, 5300)
        base.OX, base.OY = 230.0, 112.0
        base.box(c, base.OX, base.OY, base.p(5710), base.p(3500), "#ffffff", INK, 0.42)
        draw_d2_guard(c, regular); draw_route_l(c, regular); draw_kitchen_l(c, regular, bold)
        draw_desk(c, regular, 4510, 2900, 600, 5410); draw_wall_sofa_table_l(c, regular, bold)
    finally:
        base.OX, base.OY, base.SCALE = old_ox, old_oy, old_scale

    base.box(c, 12, 25, 396, 52, "#f9fafb", "#b8c1c8", 0.22, 2)
    text(c, bold, 18, 68, 5.0, "КРИТЕРИЙ")
    text(c, bold, 115, 68, 5.0, "U")
    text(c, bold, 230, 68, 5.0, "L")
    compare_metric(c, regular, bold, 61, "Полезное хранение", "1.55-1.75 м3", "1.65-1.85 м3", "L")
    compare_metric(c, regular, bold, 53, "Кухонная геометрия", "П, внутри 1200", "Г, фронты 5010", "L")
    compare_metric(c, regular, bold, 45, "Диван у длинной стены", "нет", "1800x600, 3", "L")
    compare_metric(c, regular, bold, 37, "Стол разложен", "4 места", "3+2 = 5", "L")
    compare_metric(c, regular, bold, 29, "Рабочий стол", "1200x700", "1200x600, как был", "L")

    base.box(c, 12, 10.5, 218, 13.0, PALE_GREEN, "#87aa8e", 0.20, 1.5)
    text(c, bold, 16, 18.2, 4.2, "РЕКОМЕНДАЦИЯ: L - Г-КУХНЯ", GOOD)
    text(c, regular, 16, 13.3, 3.75, "Выполняет вашу схему: диван у стены, стол 3+2, РМ справа.", INK)
    base.box(c, 234, 10.5, 174, 13.0, PALE_ORANGE, "#d2a35f", 0.20, 1.5)
    text(c, bold, 238, 18.2, 4.2, "U - П-КУХНЯ", ORANGE)
    text(c, regular, 238, 13.3, 3.75, "Выбирать, если хранение важнее свободной гостиной.", INK)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3), pageCompression=1)
    c.setTitle("KLV-003 - два варианта П- и Г-кухни")
    c.setAuthor("Codex")
    draw_variant_page(c, regular, bold, "U")
    draw_variant_page(c, regular, bold, "L")
    draw_comparison_page(c, regular, bold)
    c.save()
    shutil.copy2(TMP_PDF, OUT_PDF)
    print(f"PASS KLV-003 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
