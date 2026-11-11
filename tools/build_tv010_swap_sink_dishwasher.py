# -*- coding: utf-8 -*-
"""TV-010 - keeps TV-009 geometry, swapping only zones 3 and 5.

Zone 3 is now the 600-mm dishwasher in the upper kitchen run.  Zone 5 is
the 600-mm sink module in the left return.  This is a scale planning study,
not a plumbing installation drawing: water, drain and ventilation axes remain
to be verified on site before ordering the kitchen.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_tv009_numbered_kitchen_modules as v9


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-010_мойка_и_ПММ_перестановка_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-010_перестановка_мойки_и_ПММ_М1-25.pdf"

INK = v9.INK
MUTED = v9.MUTED
KITCHEN = v9.KITCHEN
PALE_GREEN = v9.PALE_GREEN
PALE_BLUE = v9.PALE_BLUE
PALE_ORANGE = v9.PALE_ORANGE

CORNER_PREP = v9.CORNER_PREP
HOB = v9.HOB
TALL_PENAL = v9.TALL_PENAL
FRIDGE = v9.FRIDGE
PANTRY = v9.PANTRY
CORNER_FILLER = v9.CORNER_FILLER

# Functional exchange requested by the user; coordinates stay untouched.
DISHWASHER_TOP = v9.SINK_PREP
SINK_LEFT = v9.DISHWASHER


def validate_geometry() -> None:
    v9.validate_geometry()
    assert DISHWASHER_TOP == (1200, 2900, 1800, 3500)
    assert SINK_LEFT == (0, 2250, 600, 2850)
    assert DISHWASHER_TOP[2] - DISHWASHER_TOP[0] == 600
    assert DISHWASHER_TOP[3] - DISHWASHER_TOP[1] == 600
    assert SINK_LEFT[2] - SINK_LEFT[0] == 600
    assert SINK_LEFT[3] - SINK_LEFT[1] == 600
    assert {number for number, *_ in v9.ZONE_MARKERS} == set(range(1, 13))
    print("PASS TV-010: zones 3 and 5 swapped; both modules remain 600x600")


def draw_sink_left(c, regular) -> None:
    """Draw the sink as a footprint in the former dishwasher module."""
    v9.kitchen_module(c, regular, SINK_LEFT, "", "#f1d6a0")
    c.setStrokeColor(HexColor("#58717d"))
    c.setLineWidth(0.22 * mm)
    c.circle(v9.base.qx(300) * mm, v9.base.qy(2545) * mm, v9.base.p(145) * mm, fill=0, stroke=1)
    v9.base.label_model(c, regular, 300, 2690, "МОЙКА 600", 3.7, "#58717d")
    v9.base.label_model(c, regular, 300, 2350, "вода / слив\nпо месту", 2.85, "#58717d")


def draw_kitchen(c, regular, bold) -> None:
    v9.kitchen_module(c, regular, CORNER_PREP, "УГОЛ /\nПОДГОТОВКА 600", "#ead7ae", 3.2)
    v9.kitchen_module(c, regular, HOB, "ВАРКА 600\nЯЩИКИ СНИЗУ", "#e7ca90", 3.2)
    v9.kitchen_module(c, regular, DISHWASHER_TOP, "ПММ 600", "#f1d6a0", 3.8)
    v9.kitchen_module(c, regular, TALL_PENAL, "", "#d7b775")
    v9.kitchen_module(c, regular, FRIDGE, "ХОЛОДИЛЬНИК 600", "#e7ca90", 3.5)
    v9.kitchen_module(c, regular, PANTRY, "ВЫКАТ /\nХРАН. 350", "#ead5a8", 3.05)
    draw_sink_left(c, regular)
    v9.kitchen_module(c, regular, CORNER_FILLER, "ДОБОР 50", "#f8efd8", 2.6)

    # Zone 2: induction hob remains in the former sink module.
    c.setStrokeColor(HexColor("#65523a"))
    c.setLineWidth(0.14 * mm)
    for cx, cy in ((780, 3070), (1020, 3070), (780, 3310), (1020, 3310)):
        c.circle(v9.base.qx(cx) * mm, v9.base.qy(cy) * mm, v9.base.p(72) * mm, fill=0, stroke=1)

    # Zone 4: tall unit stays unchanged.
    v9.base.model_line(c, 1800, 3100, 2400, 3100, "#80653c", 0.16)
    v9.base.model_line(c, 1800, 3300, 2400, 3300, "#80653c", 0.16)
    v9.base.label_model(c, bold, 2100, 3415, "ПЕНАЛ 600", 3.6, "#5b4827")
    v9.base.label_model(c, regular, 2100, 3235, "СВЧ", 3.5, "#5b4827")
    v9.base.label_model(c, regular, 2100, 3040, "ДУХОВКА", 3.35, "#5b4827")
    v9.base.label_model(c, regular, 2100, 2945, "ХРАНЕНИЕ", 3.1, "#5b4827")
    v9.base.label_model(c, bold, 1200, 3440, "Г-КУХНЯ: 2400 + 1600 ФРОНТОВ", 4.8, "#5b4827")


def draw_constraints(c, regular) -> None:
    """Keep TV-009 clearances and reveal the consequence of the swap."""
    v9.draw_constraints(c, regular)
    # A 600-mm dishwasher door projects toward the table corner. The table does
    # not intersect the door, but the nearest corners are only about 140 mm
    # apart diagonally; show this as a check, not an ergonomic approval.
    v9.dashed_rect(c, (1200, 2300, 1800, 2900), "#b54a3b", 0.30)
    v9.base.label_model(c, regular, 1500, 2550, "ПММ: дверца 600\nв открытом виде", 3.05, "#b54a3b")
    v9.base.label_model(c, regular, 1500, 2385, "до угла стола ~140\nпо диагонали", 3.0, "#b54a3b")


def sidebar(c, regular, bold) -> None:
    x, w = 270, 136
    v9.panel(c, bold, x, 206, w, 62, "ЗОНЫ 1-6", PALE_GREEN)
    yy = 252
    for line in (
        "1 угол / подготовка 600",
        "2 варка / ящики",
        "3 ПММ 600",
        "4 пенал: СВЧ / духовка / хран.",
        "5 мойка 600",
        "6 выкатное хранение 350",
    ):
        v9.text(c, regular, x + 4, yy, 5.1, line); yy -= 6.0

    v9.panel(c, bold, x, 138, w, 58, "ЗОНЫ 7-12", PALE_BLUE)
    yy = 183
    for line in (
        "7 холодильник 600",
        "8 стол CJ196",
        "9 диван-кровать",
        "10 рабочее место",
        "11 ТВ / медиа",
        "12 контроль D2 -> O1",
    ):
        v9.text(c, regular, x + 4, yy, 5.1, line); yy -= 6.0

    v9.panel(c, bold, x, 65, w, 65, "ВАЖНАЯ ЛОГИКА", PALE_ORANGE)
    yy = 112
    for line in (
        "- зона 1: подготовка 600",
        "- зона 5: мойка 600",
        "- №3 ПММ: дверца 600",
        "  близко к углу стола",
        "- минимум ~140 диагонально",
        "  проверить удобство вживую",
        "- вода, слив и вентканал",
        "  подтвердить до заказа",
    ):
        v9.text(c, regular, x + 4, yy, 5.1, line, "#80582d"); yy -= 6.0


def page_frame(c, regular, bold) -> None:
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK))
    c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    v9.text(c, bold, 14, 282, 13.2, "TV-010 - ПЕРЕСТАНОВКА МОЙКИ И ПММ")
    v9.text(c, regular, 14, 274, 4.9,
            "Зоны 3 и 5 обменены функциями. Масштаб: B01 5710x3500; не заказ до привязки инженерии.", MUTED)
    v9.text(c, regular, 404, 14, 3.8, "TV-010 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_page(c, regular, bold) -> None:
    page_frame(c, regular, bold)
    v9.base.draw_room_shell(c, regular, bold, "TV-010 / МОЙКА <-> ПММ")
    v9.previous.draw_d2_guard(c, regular)
    draw_kitchen(c, regular, bold)
    draw_constraints(c, regular)
    v9.draw_table(c, regular, bold)
    v9.draw_sofa_desk_tv(c, regular, bold)
    v9.dimensions(c, regular)
    v9.draw_numbers(c, regular, bold)
    sidebar(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = v9.base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-010 - перестановка мойки и ПММ")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-010 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
