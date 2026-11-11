# -*- coding: utf-8 -*-
"""TV-011 rev.3 - clean sheet using the user's coordinates unchanged.

This revision is intentionally not an alternative layout.  It keeps the exact
submitted locations, applies the reference material direction, and presents
the warnings supplied with the interactive scheme without moving any element.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_tv011_rev02_exact_coords_materials as r2


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-011_rev03_user_coords_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-011_rev03_ваши_координаты_и_материалы_М1-25.pdf"

base = r2.base
INK = r2.INK
MUTED = r2.MUTED
ORANGE = r2.ORANGE
BAD = r2.BAD
GOOD = r2.GOOD
FACADE = r2.FACADE
COUNTERTOP = r2.COUNTERTOP
BACKSPLASH = r2.BACKSPLASH
VEIN = r2.VEIN
BRASS = r2.BRASS
PALE_GREEN = r2.PALE_GREEN
PALE_BLUE = r2.PALE_BLUE
PALE_ORANGE = r2.PALE_ORANGE


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    r2.text(c, font, x, y, size, value, color, center=center, right=right)


def panel(c, bold, x, y, w, h, title, fill):
    r2.panel(c, bold, x, y, w, h, title, fill)


def dashed_rect(c, rect, color, width=0.28):
    r2.dashed_rect(c, rect, color, width)


def label_lines(c, font, cx, cy, lines, size, color, step=70):
    r2.label_lines(c, font, cx, cy, lines, size, color, step)


def validate_geometry() -> None:
    r2.validate_geometry()
    # Explicitly retain every coordinate given by the user.
    assert r2.TABLE_BBOX == (1200, 1300, 2050, 2150)
    assert r2.CHAIRS["8A"][:4] == (1850, 2150, 2250, 2550)
    assert r2.CHAIRS["8B"][:4] == (1000, 2150, 1400, 2550)
    assert r2.CHAIRS["8C"][:4] == (1900, 950, 2300, 1350)
    assert r2.CHAIRS["8D"][:4] == (950, 950, 1350, 1350)
    assert r2.SOFA == (2450, 2500, 4450, 3500)
    assert r2.DESK == (4500, 2900, 5700, 3500)
    assert r2.TV_MEDIA == (2700, 0, 4300, 300)
    print("PASS TV-011 rev.3: exact user coordinates retained; only materials and warning annotations added")


def draw_table_and_chairs(c, regular, bold):
    """The table and chairs are drawn from submitted footprints, with no shift."""
    c.setFillColor(HexColor(COUNTERTOP)); c.setStrokeColor(HexColor("#6e685e")); c.setLineWidth(0.28 * mm)
    c.circle(base.qx(r2.TABLE_CENTER[0]) * mm, base.qy(r2.TABLE_CENTER[1]) * mm, base.p(r2.TABLE_RADIUS) * mm, fill=1, stroke=1)
    c.setStrokeColor(HexColor(VEIN)); c.setLineWidth(0.13 * mm)
    base.model_line(c, 1390, 1510, 1835, 1930, VEIN, 0.13)
    base.model_line(c, 1470, 1390, 1940, 1870, VEIN, 0.13)
    base.label_model(c, bold, r2.TABLE_CENTER[0], 1785, "8 СТОЛ Ø850", 5.4, "#5a554d")
    base.label_model(c, regular, r2.TABLE_CENTER[0], 1645, "x1200 y1300", 3.5, "#5a554d")

    for marker, (x1, y1, x2, y2, facing) in r2.CHAIRS.items():
        base.draw_chair(c, x1, y1, x2 - x1, y2 - y1, facing=facing, fill="#f6f2ed")
        c.setStrokeColor(HexColor("#79736b")); c.setLineWidth(0.18 * mm)
        c.rect(base.qx(x1) * mm, base.qy(y1) * mm, base.p(x2 - x1) * mm, base.p(y2 - y1) * mm, fill=0, stroke=1)
        base.label_model(c, bold, (x1 + x2) / 2, (y1 + y2) / 2 - 18, marker, 4.8, "#5b554e")
        base.label_model(c, regular, (x1 + x2) / 2, y1 + 45, f"x{x1} y{y1}", 2.9, "#5b554e")


def draw_user_warnings(c, regular):
    """Only the warning relationships supplied by the user are visualized."""
    dashed_rect(c, r2.TOP_WORK, ORANGE, 0.26)
    dashed_rect(c, r2.LEFT_WORK, ORANGE, 0.26)
    dashed_rect(c, r2.PMM_DOOR, BAD, 0.30)
    dashed_rect(c, r2.ROUTE_D2_O1, BAD, 0.30)

    base.label_model(c, regular, 1200, 2765, "8A / 8B -> РАБОЧАЯ ЗОНА 700", 3.5, ORANGE)
    label_lines(c, regular, 1500, 2540, ("8B -> ДВЕРЦА ПММ", "600 (ПРЕДУПРЕЖДЕНИЕ)"), 3.35, BAD, 58)
    base.label_model(c, regular, 4200, 770, "8C / 8D -> 12: МАРШРУТ D2 -> O1", 3.4, BAD)
    base.label_model(c, regular, 965, 2050, "СТОЛ -> РАБОЧАЯ ЗОНА 700", 3.25, ORANGE)
    base.label_model(c, regular, 955, 1305, "8D -> РАБОЧАЯ ЗОНА 700", 3.0, ORANGE)

    # The two lower chairs get a neutral leader to the round table: the same
    # relationship that the interactive layout calls out, without moving them.
    c.setStrokeColor(HexColor(ORANGE)); c.setLineWidth(0.16 * mm); c.setDash(1.1 * mm, 0.75 * mm)
    c.line(base.qx(1375) * mm, base.qy(1350) * mm, base.qx(1460) * mm, base.qy(1455) * mm)
    c.line(base.qx(1900) * mm, base.qy(1350) * mm, base.qx(1790) * mm, base.qy(1455) * mm)
    c.setDash()
    base.label_model(c, regular, 1255, 1410, "Ø850 ↔ 8D", 2.9, ORANGE)
    base.label_model(c, regular, 1990, 1410, "Ø850 ↔ 8C", 2.9, ORANGE)


def dimensions(c, regular):
    base.dim_h(c, regular, base.qx(r2.TABLE_BBOX[0]), base.qx(r2.TABLE_BBOX[2]), base.qy(855), "Ø850", "#5a554d")
    base.dim_h(c, regular, base.qx(600), base.qx(1200), base.qy(1235), "600", ORANGE)
    base.dim_v(c, regular, base.qx(2085), base.qy(2150), base.qy(2200), "50", ORANGE)
    text(c, regular, 900, 1255, 3.25, "ДО ЛЕВОГО ФАСАДА", ORANGE, center=True)
    text(c, regular, 2110, 2180, 3.2, "ДО ПОЛОСЫ 700", ORANGE)


def draw_reference_panel(c, regular, bold):
    x, w = 270, 136
    panel(c, bold, x, 211, w, 57, "ОТДЕЛКА ПО ВАШЕМУ РЕФЕРЕНСУ", PALE_GREEN)
    if r2.REF_IMAGE.exists():
        c.drawImage(str(r2.REF_IMAGE), (x + 4) * mm, 217 * mm, 28 * mm, 43 * mm, preserveAspectRatio=True, anchor="c")
    text(c, regular, x + 36, 255, 4.6, "ФАСАД: матовый тёплый ivory", "#5b5146")
    r2.material_swatch(c, x + 36, 246, 12, 6, FACADE, "#D9D0C2")
    text(c, regular, x + 36, 236, 4.6, "СТОЛЕШНИЦА: светлый камень", "#5b5146")
    r2.material_swatch(c, x + 36, 227, 12, 6, COUNTERTOP, "#F3F0E8", marble=True)
    text(c, regular, x + 36, 217, 4.6, "ФАРТУК: бело-серый мрамор", "#5b5146")

    panel(c, bold, x, 146, w, 57, "ВНЕСЕНО БЕЗ СДВИГА", PALE_BLUE)
    y = 190
    for line in (
        "1-4: x0-2400, y2900", "5: x0 y2250; 6: x0 y1900", "7: x0 y1300; 8: x1200 y1300", "8A/8B: y2150; 8C/8D: y950", "9: x2450 y2500; 10: x4500 y2900", "11: x2700 y0; B01 5710x3500",
    ):
        text(c, regular, x + 4, y, 4.7, line, "#365260"); y -= 6.1

    panel(c, bold, x, 65, w, 76, "ПРЕДУПРЕЖДЕНИЯ ИЗ ВАШЕЙ СХЕМЫ", PALE_ORANGE)
    y = 124
    for line in (
        "Ø850 ↔ 8C; Ø850 ↔ 8D", "Ø850 -> рабочая зона 700", "8A -> рабочая зона 700", "8B -> рабочая зона 700", "8B -> дверца ПММ 600", "8C -> 12 маршрут D2 -> O1", "8D -> 12 маршрут D2 -> O1", "8D -> рабочая зона 700", "Материалы: образец до заказа.",
    ):
        text(c, regular, x + 4, y, 4.5, line, "#80582d"); y -= 5.8


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 12.4, "TV-011 rev.3 - ВАШИ КООРДИНАТЫ + МАТЕРИАЛЫ")
    text(c, regular, 14, 274, 4.9,
         "B01 5710x3500; М 1:25. Все элементы стоят в переданных координатах. Добавлены только отделка и предупреждения вашей схемы.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-011 rev.3 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-011 rev.3 / ВАШИ КООРДИНАТЫ")
    draw_user_warnings(c, regular)
    r2.draw_kitchen_material(c, regular, bold)
    draw_table_and_chairs(c, regular, bold)
    r2.draw_other_furniture(c, regular, bold)
    dimensions(c, regular)
    r2.draw_numbers(c, regular, bold)
    draw_reference_panel(c, regular, bold)
    c.showPage()


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-011 rev.3 - ваши координаты и материалы")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-011 rev.3 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
