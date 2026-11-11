# -*- coding: utf-8 -*-
"""TV-001 rev17: CJ196 800x1400 across the main route - fit check, not approval.

One A3 sheet intentionally records the proposed rotated table together with the
resulting route and sofa-bed conflicts.  It is a measurement/decision sheet,
not a claim that this placement is suitable for permanent installation.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# rev14 is the retained rev15 drawing/model source in this project.
import build_tv001_rev14_table_in_kitchen as rev15


ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "output" / "pdf" / "TV-001_rev17_стол-CJ196_поперек.pdf"
PREVIEW_PREFIX = ROOT / "output" / "preview" / "TV-001_rev17_стол-CJ196_поперек"

INK = rev15.INK
MUTED = rev15.MUTED
GOOD = rev15.GOOD
BAD = rev15.BAD
ORANGE = rev15.ORANGE
BLUE = rev15.BLUE
PALE_BLUE = rev15.PALE_BLUE
PALE_GREEN = rev15.PALE_GREEN
PALE_ORANGE = rev15.PALE_ORANGE
PALE_RED = rev15.PALE_RED

# CJ196 is rotated relative to rev15: 800 mm across X, 1400 mm along Y.
TABLE = (1900, 800, 2700, 2200)
MAIN_ROUTE = rev15.MAIN_ROUTE
ROUTE_CONFLICT = (1900, 800, 2700, 1250)
SOFA_OPEN = rev15.SOFA_OPEN


def overlap(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3])


def intersection(
    a: tuple[int, int, int, int], b: tuple[int, int, int, int]
) -> tuple[int, int, int, int] | None:
    if not overlap(a, b):
        return None
    return max(a[0], b[0]), max(a[1], b[1]), min(a[2], b[2]), min(a[3], b[3])


def assert_in_room(name: str, rect: tuple[int, int, int, int]) -> None:
    x1, y1, x2, y2 = rect
    if not (0 <= x1 < x2 <= rev15.ROOM[2] and 0 <= y1 < y2 <= rev15.ROOM[3]):
        raise AssertionError(f"{name} outside B01: {rect}")


def validate_geometry() -> None:
    """Keep the conflicts explicit; this sheet must never imply acceptance."""
    rev15.validate_geometry()
    assert TABLE == (1900, 800, 2700, 2200)
    assert MAIN_ROUTE == (0, 350, 5710, 1250)
    assert ROUTE_CONFLICT == (1900, 800, 2700, 1250)
    assert TABLE[2] - TABLE[0] == 800
    assert TABLE[3] - TABLE[1] == 1400
    assert_in_room("table", TABLE)
    assert_in_room("main_route", MAIN_ROUTE)
    assert_in_room("route_conflict", ROUTE_CONFLICT)
    assert_in_room("sofa_open", SOFA_OPEN)

    route_conflict = intersection(TABLE, MAIN_ROUTE)
    sofa_open_conflict = intersection(TABLE, SOFA_OPEN)
    assert route_conflict == ROUTE_CONFLICT
    assert sofa_open_conflict == (2430, 2100, 2700, 2200)
    assert route_conflict[2] - route_conflict[0] == 800
    assert route_conflict[3] - route_conflict[1] == 450
    assert sofa_open_conflict[2] - sofa_open_conflict[0] == 270
    assert sofa_open_conflict[3] - sofa_open_conflict[1] == 100

    # The static furniture and all retained rev15 protected fields stay clear.
    for forbidden in (
        rev15.TOP_WORK,
        rev15.LEFT_WORK_SHORT,
        rev15.O1_ROUTE,
        rev15.DESK_APPROACH,
        rev15.SOFA,
    ):
        assert not overlap(TABLE, forbidden), ("unexpected static conflict", forbidden)
    assert rev15.SOFA[1] - TABLE[3] == 300
    assert rev15.KITCHEN_TOP[1] - TABLE[3] == 700
    assert TABLE[0] - rev15.LEFT_WORK_SHORT[2] == 600
    print(
        "PASS rev17 assertions: MAIN_ROUTE 800x450 and SOFA_OPEN 270x100 "
        "conflicts retained; static protected fields clear; sofa gap 300"
    )


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    rev15.text(c, font, x, y, size, value, color, center=center, right=right)


def panel(c, regular, bold, x, y, w, h, title, fill):
    rev15.panel(c, regular, bold, x, y, w, h, title, fill)


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 11.4, "TV-001 rev17 - CJ196 ПОПЕРЕК: ПРОВЕРКА КОЛЛИЗИЙ")
    text(c, regular, 14, 274, 4.7, "B01 5710x3500 | одна примерка 1:1; красные поля - фактические пересечения, не допуски.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-001 rev17 | лист 1/1 | М 1:25", MUTED, right=True)


def draw_table(c, regular, bold):
    x1, y1, x2, y2 = TABLE
    rev15.base.model_box(c, x1, y1, x2 - x1, y2 - y1, rev15.DINING, "#506c4d", 0.34, 34)
    rev15.base.model_line(c, (x1 + x2) / 2, y1, (x1 + x2) / 2, y2, "#6b8665", 0.14)
    text(c, bold, 2300, 1600, 3.1, "CJ196 800x1400", "#405d3c", center=True)
    text(c, regular, 2300, 1490, 2.55, "ВЕРТИКАЛЬНО: x=1900..2700; y=800..2200", "#405d3c", center=True)


def draw_open_sofa(c, regular, bold):
    rev15.route_rect(
        c, regular, SOFA_OPEN, "SOFA_OPEN: контур разложенного дивана", (3450, 2140), BAD, 0.42, PALE_RED
    )
    text(c, regular, 3430, 2050, 2.55, "закрытый диван ниже - без пересечения", MUTED, center=True)


def draw_dimensions(c, regular):
    base = rev15.base
    base.dim_h(c, regular, base.qx(1900), base.qx(2700), base.qy(740), "800")
    base.dim_v(c, regular, base.qx(2760), base.qy(800), base.qy(2200), "1400")
    base.dim_v(c, regular, base.qx(2820), base.qy(800), base.qy(1250), "450", BAD)
    base.dim_v(c, regular, base.qx(2760), base.qy(2200), base.qy(2500), "300", ORANGE)
    base.dim_v(c, regular, base.qx(1840), base.qy(2200), base.qy(2900), "700", GOOD)
    base.dim_h(c, regular, base.qx(1300), base.qx(1900), base.qy(2260), "600", GOOD)
    text(c, regular, 2855, 1050, 2.45, "занято маршрутом", BAD)
    text(c, regular, 2855, 2350, 2.45, "до закрытого дивана", ORANGE)


def draw_plan(c, regular, bold):
    # Full B01, the active short branch, fixed sofa/desk/TV and retained controls.
    rev15.base.draw_room_shell(c, regular, bold, "TV-001 rev17")
    rev15.draw_d2_guard(c, regular)
    rev15.route_rect(
        c, regular, MAIN_ROUTE,
        "MAIN_ROUTE D2 -> O1: требуется 900 мм - НАРУШЕН",
        (3650, 520), BAD, 0.38, PALE_RED,
    )
    rev15.route_rect(c, regular, rev15.TOP_WORK, "рабочий пояс верхней ветви 700", (1400, 2770), ORANGE, 0.28, PALE_ORANGE)
    rev15.route_rect(c, regular, rev15.LEFT_WORK_SHORT, "рабочий пояс левой ветви 700", (955, 2330), ORANGE, 0.28, PALE_ORANGE)
    rev15.route_rect(c, regular, rev15.O1_ROUTE, "900 к O1", (5250, 2380), GOOD, 0.30, PALE_GREEN)
    rev15.route_rect(c, regular, rev15.DESK_APPROACH, "подход к креслу 600", (4810, 2390), BLUE, 0.28, PALE_BLUE)
    rev15.draw_kitchen(c, regular, bold, short_left=True)
    rev15.draw_sofa_desk_tv(c, regular, bold)
    draw_open_sofa(c, regular, bold)
    draw_table(c, regular, bold)

    # Overlay the exact blocked part of the full 900-mm main-route field.
    route_conflict = intersection(TABLE, MAIN_ROUTE)
    assert route_conflict is not None
    rev15.route_rect(c, regular, route_conflict, "ПЕРЕСЕЧЕНИЕ MAIN_ROUTE", (2300, 980), BAD, 0.52, PALE_RED)
    text(c, bold, 2300, 1125, 3.0, "800x450 / ОСТАЁТСЯ 450 мм", BAD, center=True)

    sofa_open_conflict = intersection(TABLE, SOFA_OPEN)
    assert sofa_open_conflict is not None
    rev15.route_rect(c, regular, sofa_open_conflict, "", (0, 0), BAD, 0.50, PALE_RED)
    text(c, bold, 2565, 2145, 2.65, "270x100", BAD, center=True)
    text(c, regular, 2565, 2055, 2.35, "стол × SOFA_OPEN", BAD, center=True)
    draw_dimensions(c, regular)


def sidebar(c, regular, bold):
    panel(c, regular, bold, 255, 213, 151, 57, "ЧТО ПОМЕСТИЛОСЬ / ЧТО НЕ ПОМЕСТИЛОСЬ", PALE_RED)
    y = 252
    for line, color in (
        ("CJ196: 800x1400, x=1900..2700, y=800..2200.", INK),
        ("Статически: верхний/левый пояс 700, O1, РМ и", INK),
        ("закрытый диван не пересечены; до дивана 300 мм.", INK),
        ("Но MAIN_ROUTE пересечён точно на 800x450;", BAD),
        ("остаётся 450 мм. Это не основной маршрут.", BAD),
    ):
        text(c, regular, 259, y, 3.8, line, color); y -= 5.4

    panel(c, regular, bold, 255, 139, 151, 62, "РАСКЛАДЫВАНИЕ ДИВАНА", PALE_RED)
    y = 182
    for line in (
        "SOFA_OPEN = x2430..4430; y2100..3500.",
        "Контур пересекает стол на 270x100 мм.",
        "Разложить диван без перемещения стола нельзя.",
        "Показан отдельный красный контур, а не допуск.",
    ):
        text(c, regular, 259, y, 3.8, line, BAD); y -= 5.5

    panel(c, regular, bold, 255, 75, 151, 51, "ВЕРДИКТ", PALE_RED)
    text(c, bold, 259, 105, 5.1, "ПРИМЕРЕНО, НО НЕ ДЛЯ", BAD)
    text(c, bold, 259, 97, 5.1, "ПОСТОЯННОЙ УСТАНОВКИ", BAD)
    text(c, regular, 259, 86, 3.75, "Нужен макет 1:1 и другое место/размер стола.", INK)
    text(c, regular, 259, 80, 3.75, "Красные пересечения запрещают утверждение планировки.", INK)


def pdftoppm_path() -> str | None:
    found = shutil.which("pdftoppm")
    if found:
        return found
    bundled = Path(r"C:\Users\aidzm\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe")
    return str(bundled) if bundled.exists() else None


def render_preview() -> None:
    executable = pdftoppm_path()
    if not executable:
        raise RuntimeError("pdftoppm is required to produce the requested rev17 PNG preview")
    PREVIEW_PREFIX.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([executable, "-png", "-r", "150", str(OUT_PDF), str(PREVIEW_PREFIX)], check=True)
    preview = PREVIEW_PREFIX.parent / "TV-001_rev17_стол-CJ196_поперек-1.png"
    if not preview.exists() or preview.stat().st_size == 0:
        raise AssertionError("rev17 preview rendering did not produce page 1")
    print(f"PASS rev17 preview: {preview}")


def build() -> None:
    validate_geometry()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = rev15.base.fonts()
    c = canvas.Canvas(str(OUT_PDF), pagesize=landscape(A3))
    c.setTitle("TV-001 rev17 - CJ196 поперек: примерка")
    c.setAuthor("Codex")
    page_frame(c, regular, bold)
    draw_plan(c, regular, bold)
    sidebar(c, regular, bold)
    c.showPage()
    c.save()
    if not OUT_PDF.exists() or OUT_PDF.stat().st_size == 0:
        raise AssertionError("rev17 PDF missing or empty")
    print(f"PASS rev17 PDF: {OUT_PDF}")
    render_preview()


if __name__ == "__main__":
    build()
