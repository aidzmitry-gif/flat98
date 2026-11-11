# -*- coding: utf-8 -*-
"""TV-011 - round four-seat dining mode on the unchanged TV-010 plan.

This is a 1:25 planning sheet.  It preserves the TV-010 kitchen and the
TV-009 sofa, desk and TV positions.  The sofa-open footprint is deliberately
not drawn: TV-010 has no measured active contour for it.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_tv010_swap_sink_dishwasher as v10
import build_tv009_numbered_kitchen_modules as v9


ROOT = Path(__file__).resolve().parents[1]
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-011_round_table_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-011_круглый_стол_4_места_М1-25.pdf"
PREVIEW_PREFIX = ROOT / "output" / "preview" / "TV-011_круглый_стол_4_места"
PREVIEW_PNG = ROOT / "output" / "preview" / "TV-011_круглый_стол_4_места-1.png"

base = v9.base
INK = v9.INK
MUTED = v9.MUTED
GOOD = base.GOOD
ORANGE = v9.ORANGE
BLUE = v9.BLUE
PALE_GREEN = v9.PALE_GREEN
PALE_BLUE = v9.PALE_BLUE
PALE_ORANGE = v9.PALE_ORANGE

ROUTE = (0, 350, 5710, 1250)
TOP_WORK = (0, 2200, 2400, 2900)
LEFT_WORK = (600, 1300, 1300, 2900)
TABLE_CENTER = (3000, 1725)
TABLE = (2575, 1300, 3425, 2150)
TABLE_DIAMETER = 850
CHAIRS = {
    "8A": (2075, 1300, 2475, 1700, "right"),
    "8B": (2075, 1750, 2475, 2150, "right"),
    "8C": (3525, 1300, 3925, 1700, "left"),
    "8D": (3525, 1750, 3925, 2150, "left"),
}
PMM_DOOR = (1200, 2300, 1800, 2900)
SOFA = (2430, 2500, 4430, 3500)
DESK_APPROACH = v9.DESK_CHAIR
O1_ROUTE = v9.O1_ROUTE
D2_GUARD = v9.D2_GUARD

ZONE_MARKERS = (
    (1, 120, 3400, "#7b5f2c"), (2, 720, 3400, "#7b5f2c"),
    (3, 1320, 3400, "#58717d"), (4, 1920, 3400, "#6b5230"),
    (5, 120, 2760, "#58717d"), (6, 120, 2190, "#7b5f2c"),
    (7, 120, 1840, "#7b5f2c"), (8, 3300, 2040, "#4e6c49"),
    (9, 4300, 3400, "#70585b"), (10, 5580, 3400, "#2f6e8d"),
    (11, 2760, 170, "#70585b"), (12, 4400, 600, "#4f7d62"),
)


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def validate_geometry() -> None:
    """Assert the measured clearances; touching boundaries are allowed."""
    v10.validate_geometry()
    assert TABLE_CENTER == (3000, 1725)
    assert TABLE == (2575, 1300, 3425, 2150)
    assert TABLE[2] - TABLE[0] == TABLE_DIAMETER == TABLE[3] - TABLE[1]
    assert ROUTE == (0, 350, 5710, 1250)
    assert TOP_WORK == (0, 2200, 2400, 2900)
    assert LEFT_WORK == (600, 1300, 1300, 2900)
    assert PMM_DOOR == (1200, 2300, 1800, 2900)
    assert SOFA == (2430, 2500, 4430, 3500)
    chair_rects = [coords[:4] for coords in CHAIRS.values()]
    for rect in [TABLE, *chair_rects]:
        assert not overlap(rect, ROUTE)
        assert not overlap(rect, TOP_WORK)
    for rect in chair_rects:
        assert not overlap(rect, LEFT_WORK)
    assert min(rect[1] for rect in [TABLE, *chair_rects]) - ROUTE[3] == 50
    assert TOP_WORK[1] - max(rect[3] for rect in [TABLE, *chair_rects]) == 50
    assert min(rect[0] for rect in chair_rects) - LEFT_WORK[2] == 775
    assert v9.TOP_KITCHEN[1] - max(rect[3] for rect in [TABLE, *chair_rects]) == 750
    assert PMM_DOOR[1] - max(rect[3] for rect in chair_rects) == 150
    assert SOFA[1] - max(rect[3] for rect in [TABLE, *chair_rects]) == 350
    assert DESK_APPROACH[0] - max(rect[2] for rect in chair_rects) == 585
    for rect in [TABLE, *chair_rects]:
        assert not overlap(rect, O1_ROUTE)
        assert not overlap(rect, DESK_APPROACH)
        assert not overlap(rect, D2_GUARD)
    assert {number for number, *_ in ZONE_MARKERS} == set(range(1, 13))
    print("PASS TV-011: round table 850 at x3000, four compact chairs, static route and work fields clear")


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    v9.text(c, font, x, y, size, value, color, center=center, right=right)


def zone_marker(c, bold, number, cx, cy, fill):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor("#ffffff")); c.setLineWidth(0.18 * mm)
    c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(60) * mm, fill=1, stroke=1)
    base.label_model(c, bold, cx, cy - 24, str(number), 4.2, "#ffffff")


def dashed_rect(c, rect, color, width=0.26):
    v9.dashed_rect(c, rect, color, width)


def label_lines(c, font, cx, cy, lines, size, color, step=70):
    """Draw model-space labels as real lines; ReportLab drawString ignores newlines."""
    offset = (len(lines) - 1) * step / 2
    for index, line in enumerate(lines):
        base.label_model(c, font, cx, cy + offset - index * step, line, size, color)


def kitchen_module_readable(c, font, rect, lines, fill, size, step=70):
    x1, y1, x2, y2 = rect
    base.model_box(c, x1, y1, x2 - x1, y2 - y1, fill, "#6e5a34", 0.20)
    label_lines(c, font, (x1 + x2) / 2, (y1 + y2) / 2 - 10, lines, size, "#5b4827", step)


def draw_compact_chair(c, regular, marker, rect, facing):
    x1, y1, x2, y2 = rect
    assert x2 - x1 == 400 and y2 - y1 == 400
    base.draw_chair(c, x1, y1, 400, 400, facing=facing, fill="#f6f2ed")
    base.label_model(c, regular, (x1 + x2) / 2, (y1 + y2) / 2 - 18, marker, 5.2, "#5b554e")


def draw_readable_kitchen(c, regular, bold):
    """Redraw the unchanged TV-010 kitchen with print-readable A3 labels."""
    kitchen_module_readable(c, regular, v10.CORNER_PREP, ("УГОЛ / ПОДГОТОВКА", "600"), "#ead7ae", 5.0)
    kitchen_module_readable(c, regular, v10.HOB, ("ВАРКА 600", "ЯЩИКИ"), "#e7ca90", 5.0)
    kitchen_module_readable(c, bold, v10.DISHWASHER_TOP, ("ПММ", "600"), "#f1d6a0", 5.5)
    kitchen_module_readable(c, regular, v10.TALL_PENAL, (), "#d7b775", 5.0)
    kitchen_module_readable(c, regular, v10.FRIDGE, ("ХОЛОДИЛЬНИК", "600"), "#e7ca90", 4.8)
    kitchen_module_readable(c, regular, v10.PANTRY, ("ВЫКАТ", "ХРАНЕНИЕ 350"), "#ead5a8", 4.7)
    kitchen_module_readable(c, regular, v10.SINK_LEFT, (), "#f1d6a0", 5.0)
    kitchen_module_readable(c, regular, v10.CORNER_FILLER, (), "#f8efd8", 4.2)

    c.setStrokeColor(HexColor("#58717d")); c.setLineWidth(0.22 * mm)
    c.circle(base.qx(300) * mm, base.qy(2545) * mm, base.p(145) * mm, fill=0, stroke=1)
    base.label_model(c, bold, 300, 2695, "МОЙКА 600", 5.4, "#58717d")
    label_lines(c, regular, 300, 2360, ("ВОДА / СЛИВ", "ПО МЕСТУ"), 4.2, "#58717d", 55)

    c.setStrokeColor(HexColor("#65523a")); c.setLineWidth(0.14 * mm)
    for cx, cy in ((780, 3070), (1020, 3070), (780, 3310), (1020, 3310)):
        c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(72) * mm, fill=0, stroke=1)

    base.model_line(c, 1800, 3100, 2400, 3100, "#80653c", 0.16)
    base.model_line(c, 1800, 3300, 2400, 3300, "#80653c", 0.16)
    base.label_model(c, bold, 2100, 3415, "ПЕНАЛ 600", 5.5, "#5b4827")
    base.label_model(c, regular, 2100, 3235, "СВЧ", 5.1, "#5b4827")
    base.label_model(c, regular, 2100, 3040, "ДУХОВКА", 4.9, "#5b4827")
    base.label_model(c, regular, 2100, 2945, "ХРАНЕНИЕ", 4.5, "#5b4827")
    base.label_model(c, regular, 300, 2870, "ДОБОР 50", 4.2, "#6e5a34")
    base.label_model(c, bold, 1200, 3440, "Г-КУХНЯ: 2400 + 1600 ФРОНТОВ", 6.3, "#5b4827")


def draw_round_table(c, regular, bold):
    c.setFillColor(HexColor("#dcebd6")); c.setStrokeColor(HexColor("#506c4d")); c.setLineWidth(0.28 * mm)
    c.circle(base.qx(TABLE_CENTER[0]) * mm, base.qy(TABLE_CENTER[1]) * mm, base.p(TABLE_DIAMETER / 2) * mm, fill=1, stroke=1)
    c.setFillColor(HexColor("#506c4d")); c.circle(base.qx(TABLE_CENTER[0]) * mm, base.qy(TABLE_CENTER[1]) * mm, base.p(55) * mm, fill=1, stroke=0)
    base.label_model(c, bold, TABLE_CENTER[0], 1790, "СТОЛ Ø850", 6.2, "#405d3c")
    base.label_model(c, regular, TABLE_CENTER[0], 1650, "4 МЕСТА", 5.4, "#405d3c")
    for marker, (x1, y1, x2, y2, facing) in CHAIRS.items():
        draw_compact_chair(c, regular, marker, (x1, y1, x2, y2), facing)


def draw_constraints(c, regular):
    dashed_rect(c, ROUTE, GOOD, 0.30)
    base.label_model(c, regular, 4050, 800, "12: МАРШРУТ D2 -> O1 СВОБОДЕН", 5.3, GOOD)
    dashed_rect(c, TOP_WORK, ORANGE, 0.26)
    base.label_model(c, regular, 1200, 2770, "ВЕРХНИЙ РАБОЧИЙ ПОЯС 700", 5.1, ORANGE)
    dashed_rect(c, LEFT_WORK, ORANGE, 0.26)
    base.label_model(c, regular, 950, 2320, "ЛЕВЫЙ РАБОЧИЙ ПОЯС 700", 5.0, ORANGE)
    dashed_rect(c, PMM_DOOR, "#b54a3b", 0.27)
    label_lines(c, regular, 1500, 2540, ("ДВЕРЦА ПММ", "600 ОТКРЫТА"), 5.0, "#b54a3b", 65)
    dashed_rect(c, O1_ROUTE, GOOD, 0.22)
    label_lines(c, regular, 5260, 2220, ("ПРОХОД К O1: 900", "НЕ ШИРИНА ПРОЁМА"), 5.0, GOOD, 65)
    dashed_rect(c, DESK_APPROACH, BLUE, 0.22)
    base.label_model(c, regular, 4810, 2620, "ПОДХОД К КРЕСЛУ 600", 5.0, BLUE)


def dimensions(c, regular):
    # Ø850 and the five decision dimensions requested for this arrangement.
    base.dim_h(c, regular, base.qx(TABLE[0]), base.qx(TABLE[2]), base.qy(1215), "Ø850", "#405d3c")
    base.dim_v(c, regular, base.qx(4000), base.qy(1250), base.qy(1300), "50", GOOD)
    base.dim_v(c, regular, base.qx(4000), base.qy(2150), base.qy(2200), "50", ORANGE)
    base.dim_h(c, regular, base.qx(1300), base.qx(2075), base.qy(2180), "775", ORANGE)
    base.dim_v(c, regular, base.qx(2500), base.qy(2150), base.qy(2300), "150", "#b54a3b")
    base.dim_v(c, regular, base.qx(4020), base.qy(2150), base.qy(2500), "350", "#70585b")
    text(c, regular, 4045, 1265, 4.2, "ДО МАРШРУТА", GOOD)
    text(c, regular, 4045, 2165, 4.2, "ДО РАБОЧЕГО ПОЯСА", ORANGE)
    text(c, regular, 1685, 2210, 4.2, "ОТ ЛЕВОГО РАБОЧЕГО ПОЯСА", ORANGE, center=True)
    text(c, regular, 2520, 2220, 4.2, "ДО ДВЕРЦЫ ПММ", "#b54a3b")
    text(c, regular, 4040, 2340, 4.2, "ДО ЗАКРЫТОГО ДИВАНА", "#70585b")


def draw_numbers(c, regular, bold):
    for number, cx, cy, fill in ZONE_MARKERS:
        zone_marker(c, bold, number, cx, cy, fill)


def sidebar(c, regular, bold):
    x, w = 270, 136
    v9.panel(c, bold, x, 210, w, 58, "ЭЛЕМЕНТЫ 1-7", PALE_GREEN)
    y = 254
    for line in (
        "1 угол / подготовка 600", "2 варка / ящики", "3 ПММ 600", "4 пенал", "5 мойка 600", "6 выкат 350", "7 холодильник 600", "добор 50",
    ):
        text(c, regular, x + 4, y, 6.2, line); y -= 5.9
    v9.panel(c, bold, x, 142, w, 60, "ЭЛЕМЕНТЫ 8-12", PALE_BLUE)
    y = 185
    for line in (
        "8 стол круглый Ø850", "8A-8D стулья 400x400", "9 диван", "10 РМ", "11 ТВ / медиа", "12 маршрут D2 -> O1",
    ):
        text(c, regular, x + 4, y, 6.2, line); y -= 6.4
    v9.panel(c, bold, x, 65, w, 68, "ВЫВОД И УСЛОВИЯ", PALE_ORANGE)
    y = 115
    lines = (
        ("СТАТИКА: БЕЗ ПЕРЕСЕЧЕНИЙ", bold),
        ("50 ММ - НЕ ПРОХОД, А КОНТРОЛЬ", bold),
        ("4 МЕСТА - ОТДЕЛЬНЫЙ РЕЖИМ", bold),
        ("НЕ ОДНОВРЕМЕННО С ГОТОВКОЙ", regular),
        ("ПЕРЕД РАСКЛАДЫВАНИЕМ ДИВАНА", regular),
        ("СТОЛ И СТУЛЬЯ ПЕРЕСТАВИТЬ", regular),
        ("ЦЕНТРАЛЬНАЯ ОПОРА; МАКЕТ 1:1", regular),
    )
    for line, font in lines:
        text(c, font, x + 4, y, 5.9, line, "#80582d"); y -= 6.3


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white); c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 12.7, "TV-011 - КРУГЛЫЙ СТОЛ Ø850, 4 МЕСТА")
    text(c, regular, 14, 274, 6.1, "TV-010 кухня без сдвига; 4 места - отдельный обеденный режим. Масштаб B01 5710x3500; М 1:25.", MUTED)
    text(c, regular, 404, 14, 5.0, "TV-011 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_page(c, regular, bold):
    page_frame(c, regular, bold)
    base.draw_room_shell(c, regular, bold, "TV-011 / КРУГЛЫЙ СТОЛ")
    v9.previous.draw_d2_guard(c, regular)
    draw_constraints(c, regular)
    draw_readable_kitchen(c, regular, bold)
    draw_round_table(c, regular, bold)
    v9.draw_sofa_desk_tv(c, regular, bold)
    dimensions(c, regular)
    draw_numbers(c, regular, bold)
    sidebar(c, regular, bold)
    c.showPage()


def pdftoppm_path() -> str | None:
    found = shutil.which("pdftoppm")
    if found:
        return found
    bundled = Path(r"C:\Users\aidzm\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")
    return str(bundled) if bundled.exists() else None


def render_preview() -> None:
    executable = pdftoppm_path()
    if not executable:
        raise RuntimeError("pdftoppm is required to produce the requested TV-011 PNG preview")
    PREVIEW_PREFIX.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([executable, "-png", "-r", "150", str(OUT_PDF), str(PREVIEW_PREFIX)], check=True)
    if not PREVIEW_PNG.exists() or PREVIEW_PNG.stat().st_size == 0:
        raise AssertionError("TV-011 preview rendering did not produce page 1")
    print(f"PASS TV-011 preview: {PREVIEW_PNG}")


def build() -> None:
    validate_geometry()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-011 - круглый стол 4 места")
    c.setAuthor("Codex")
    draw_page(c, regular, bold)
    c.save()
    TMP_PDF.replace(OUT_PDF)
    if not OUT_PDF.exists() or OUT_PDF.stat().st_size == 0:
        raise AssertionError("TV-011 PDF missing or empty")
    print(f"PASS TV-011 PDF: {OUT_PDF}")
    render_preview()


if __name__ == "__main__":
    build()
