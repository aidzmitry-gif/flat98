# -*- coding: utf-8 -*-
"""Create the apartment reference DXF from the BTI plan and control measurements.

The plan deliberately keeps two data sources separate:
* A-BTI-* -- vectorised geometry/dimensions visible on S15 (the BTI plan);
* A-CONTROL -- later on-site control measurements.

This is not an automatic raster trace.  Every BTI dimension included below is
readable on S15; missing anchors and conflicting values are marked rather than
estimated.  The output is a plain AC1015/CP1251 DXF, editable in LibreCAD.
"""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "plans" / "02_Сводный_план_БТИ_и_контрольные_обмеры_LibreCAD.dxf"


class DXF:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, code: int, value: object) -> None:
        self.parts.extend((str(code), str(value)))

    def entity(self, kind: str, layer: str) -> None:
        self.add(0, kind)
        self.add(8, layer)

    def line(self, layer: str, x1: float, y1: float, x2: float, y2: float) -> None:
        self.entity("LINE", layer)
        self.add(10, x1)
        self.add(20, y1)
        self.add(30, 0)
        self.add(11, x2)
        self.add(21, y2)
        self.add(31, 0)

    def polyline(self, layer: str, points: list[tuple[float, float]], closed: bool = True) -> None:
        self.entity("LWPOLYLINE", layer)
        self.add(90, len(points))
        self.add(70, 1 if closed else 0)
        for x, y in points:
            self.add(10, x)
            self.add(20, y)

    def rect(self, layer: str, x1: float, y1: float, x2: float, y2: float) -> None:
        self.polyline(layer, [(x1, y1), (x2, y1), (x2, y2), (x1, y2)])

    def arc(self, layer: str, x: float, y: float, radius: float, start: float, end: float) -> None:
        self.entity("ARC", layer)
        self.add(10, x)
        self.add(20, y)
        self.add(30, 0)
        self.add(40, radius)
        self.add(50, start)
        self.add(51, end)

    def circle(self, layer: str, x: float, y: float, radius: float) -> None:
        self.entity("CIRCLE", layer)
        self.add(10, x)
        self.add(20, y)
        self.add(30, 0)
        self.add(40, radius)

    def text(self, layer: str, x: float, y: float, height: float, value: str, rotation: float = 0) -> None:
        self.entity("TEXT", layer)
        self.add(10, x)
        self.add(20, y)
        self.add(30, 0)
        self.add(40, height)
        self.add(1, value)
        self.add(7, "STANDARD")
        self.add(50, rotation)

    def arrow_h(self, layer: str, x: float, y: float, direction: int, size: float = 60) -> None:
        self.line(layer, x, y, x + direction * size, y + size * 0.40)
        self.line(layer, x, y, x + direction * size, y - size * 0.40)

    def dim_h(self, layer: str, x1: float, x2: float, object_y: float, dim_y: float, label: str) -> None:
        self.line(layer, x1, object_y, x1, dim_y)
        self.line(layer, x2, object_y, x2, dim_y)
        self.line(layer, x1, dim_y, x2, dim_y)
        self.arrow_h(layer, x1, dim_y, 1)
        self.arrow_h(layer, x2, dim_y, -1)
        self.text(layer, (x1 + x2) / 2 - len(label) * 32, dim_y + 90, 115, label)

    def dim_v(self, layer: str, y1: float, y2: float, object_x: float, dim_x: float, label: str) -> None:
        self.line(layer, object_x, y1, dim_x, y1)
        self.line(layer, object_x, y2, dim_x, y2)
        self.line(layer, dim_x, y1, dim_x, y2)
        size = 60
        self.line(layer, dim_x, y1, dim_x + size * .40, y1 + size)
        self.line(layer, dim_x, y1, dim_x - size * .40, y1 + size)
        self.line(layer, dim_x, y2, dim_x + size * .40, y2 - size)
        self.line(layer, dim_x, y2, dim_x - size * .40, y2 - size)
        self.text(layer, dim_x - 65, (y1 + y2) / 2 - len(label) * 32, 115, label, 90)

    def content(self) -> str:
        return "\r\n".join(self.parts) + "\r\n"


def header(d: DXF) -> None:
    d.add(0, "SECTION")
    d.add(2, "HEADER")
    for name, code, value in (
        ("$ACADVER", 1, "AC1015"),
        ("$DWGCODEPAGE", 3, "ANSI_1251"),
        ("$INSUNITS", 70, 4),
        ("$MEASUREMENT", 70, 1),
        ("$LTSCALE", 40, 90),
        ("$DIMTXT", 40, 115),
    ):
        d.add(9, name)
        d.add(code, value)
    d.add(0, "ENDSEC")


def tables(d: DXF) -> None:
    layers = [
        ("A-PRINT", 8, "CONTINUOUS"),
        ("A-BTI-WALL", 7, "CONTINUOUS"),
        ("A-BTI-OPENING", 8, "CONTINUOUS"),
        ("A-BTI-DIM", 3, "CONTINUOUS"),
        ("A-BTI-TOPOLOGY", 30, "DASHED"),
        ("A-CONTROL", 5, "DASHED"),
        ("A-CONFLICT", 1, "CONTINUOUS"),
        ("A-CEILING", 6, "DASHED"),
        ("A-TEXT", 7, "CONTINUOUS"),
        ("A-SOURCE", 30, "CONTINUOUS"),
    ]
    d.add(0, "SECTION")
    d.add(2, "TABLES")
    d.add(0, "TABLE")
    d.add(2, "LTYPE")
    d.add(70, 2)
    d.add(0, "LTYPE")
    d.add(2, "CONTINUOUS")
    d.add(70, 0)
    d.add(3, "Solid line")
    d.add(72, 65)
    d.add(73, 0)
    d.add(40, 0)
    d.add(0, "LTYPE")
    d.add(2, "DASHED")
    d.add(70, 0)
    d.add(3, "Dash __ __ __")
    d.add(72, 65)
    d.add(73, 2)
    d.add(40, 1.5)
    d.add(49, 1.0)
    d.add(49, -0.5)
    d.add(0, "ENDTAB")
    d.add(0, "TABLE")
    d.add(2, "LAYER")
    d.add(70, len(layers))
    for name, color, ltype in layers:
        d.add(0, "LAYER")
        d.add(2, name)
        d.add(70, 0)
        d.add(62, color)
        d.add(6, ltype)
    d.add(0, "ENDTAB")
    d.add(0, "TABLE")
    d.add(2, "STYLE")
    d.add(70, 1)
    d.add(0, "STYLE")
    d.add(2, "STANDARD")
    d.add(70, 0)
    d.add(40, 0)
    d.add(41, 1)
    d.add(50, 0)
    d.add(71, 0)
    d.add(42, 2.5)
    d.add(3, "arial.ttf")
    d.add(4, "")
    d.add(0, "ENDTAB")
    d.add(0, "ENDSEC")


def wall_box(d: DXF, x1: float, y1: float, x2: float, y2: float, thickness: float = 130) -> None:
    """Show both faces of a wall box; dimensions refer to the inner contour."""
    d.rect("A-BTI-WALL", x1 - thickness, y1 - thickness, x2 + thickness, y2 + thickness)
    d.rect("A-BTI-WALL", x1, y1, x2, y2)


def room_label(d: DXF, x: float, y: float, number: str, name: str, bti: str, control: str | None = None) -> None:
    d.text("A-TEXT", x, y, 205, f"{number} {name}")
    d.text("A-BTI-DIM", x, y - 235, 130, f"БТИ: {bti}")
    if control:
        d.text("A-CONTROL", x, y - 465, 130, f"контроль: {control}")


def compact_room_label(d: DXF, x: float, y: float, number: str, name: str, bti: str, control: str) -> None:
    """Room data that remains printable in the narrow sanitary-room cells."""
    d.text("A-TEXT", x, y, 155, f"{number} {name}")
    d.text("A-BTI-DIM", x, y - 190, 105, f"БТИ {bti}")
    d.text("A-CONTROL", x, y - 355, 90, f"факт {control}")


def door_h(d: DXF, x: float, y: float, width: float, label: str, note: str, swing_up: bool = True) -> None:
    layer = "A-BTI-OPENING"
    d.line(layer, x, y, x + width, y)
    d.line(layer, x, y - 70, x, y + 70)
    d.line(layer, x + width, y - 70, x + width, y + 70)
    if swing_up:
        d.line(layer, x, y, x, y + width)
        d.arc(layer, x, y, width, 0, 90)
    else:
        d.line(layer, x + width, y, x + width, y - width)
        d.arc(layer, x + width, y, width, 180, 270)
    d.text(layer, x + 80, y + (150 if swing_up else -260), 120, f"{label}: {note}")


def door_v(d: DXF, x: float, y: float, width: float, label: str, note: str, swing_right: bool = True) -> None:
    """Vertical-wall opening; width is the confirmed clear opening, not a wall offset."""
    layer = "A-BTI-OPENING"
    d.line(layer, x, y, x, y + width)
    d.line(layer, x - 70, y, x + 70, y)
    d.line(layer, x - 70, y + width, x + 70, y + width)
    if swing_right:
        d.line(layer, x, y, x + width, y)
        d.arc(layer, x, y, width, 0, 90)
        d.text(layer, x + 120, y + width + 110, 120, f"{label}: {note}")
    else:
        d.line(layer, x, y + width, x - width, y + width)
        d.arc(layer, x, y + width, width, 180, 270)
        d.text(layer, x - width - 120, y - 180, 120, f"{label}: {note}")


def window_h(d: DXF, x: float, y: float, width: float, label: str) -> None:
    d.line("A-BTI-OPENING", x, y - 75, x + width, y - 75)
    d.line("A-BTI-OPENING", x, y + 75, x + width, y + 75)
    d.text("A-BTI-OPENING", x + 80, y + 160, 115, label)


def window_v(d: DXF, x: float, y: float, height: float, label: str, note: str, text_x: float, text_y: float) -> None:
    """Vertical external opening drawn from the explicit BTI opening chain."""
    layer = "A-BTI-OPENING"
    d.line(layer, x - 75, y, x - 75, y + height)
    d.line(layer, x + 75, y, x + 75, y + height)
    d.line(layer, x - 150, y, x + 150, y)
    d.line(layer, x - 150, y + height, x + 150, y + height)
    d.text(layer, text_x, text_y, 105, f"{label}: {note}")


def title_and_legend(d: DXF) -> None:
    d.rect("A-PRINT", 0, 0, 21000, 14850)
    d.rect("A-PRINT", 250, 250, 20750, 14600)
    d.text("A-TEXT", 700, 14000, 275, "APT-001 — СВОДНЫЙ ОБМЕРНЫЙ ПЛАН")
    d.text("A-TEXT", 700, 13660, 210, "БТИ S15 + контрольные обмеры; модель 1:1, мм; печать A3, альбом, М 1:50")
    d.line("A-PRINT", 700, 13280, 20250, 13280)
    d.text("A-TEXT", 700, 12890, 200, "КАК ЧИТАТЬ ЛИСТ")
    legend = [
        ("A-BTI-WALL", "чёрный — контуры/толщины стен по плану БТИ S15"),
        ("A-BTI-DIM", "зелёный — размеры, читаемые на плане БТИ"),
        ("A-CONTROL", "синий пунктир — контрольные обмеры на объекте"),
        ("A-CONFLICT", "красный — расхождение источников, не применять без проверки"),
        ("A-BTI-TOPOLOGY", "серый пунктир — связь зон БТИ; без недостающих привязок"),
    ]
    y = 12560
    for layer, label in legend:
        d.line(layer, 750, y + 55, 1220, y + 55)
        d.text("A-TEXT", 1320, y, 155, label)
        y -= 310
    d.text("A-TEXT", 9000, 12890, 200, "ПРИОРИТЕТ ИСТОЧНИКОВ")
    priority = [
        "1. Контрольные замеры — для заказа, привязок и монтажа.",
        "2. БТИ S15 — для взаимного расположения, стен и базовой топологии.",
        "3. Схемы/фото — только если значение отмечено на соответствующем слое.",
        "Не усреднять разные стороны помещения и не заменять ими замер.",
    ]
    y = 12560
    for line in priority:
        d.text("A-TEXT", 9000, y, 155, line)
        y -= 310
    d.text("A-SOURCE", 700, 10950, 150, "Источник БТИ S15: Фото по помещениям/00_Общие/photo_2026-08-10_20-12-30.jpg")
    d.text("A-SOURCE", 700, 10680, 150, "Контроль: S01–S14, U01 (в т.ч. D1=1140x2150 и D2=915x2150). См. docs/04, docs/07, docs/08, docs/10.")
    d.text("A-SOURCE", 700, 10410, 150, "Статус: сводный рабочий чертёж. Красные позиции требуют контрольного замера до закупки/демонтажа.")
    d.text("A-SOURCE", 700, 10140, 140, "Толщины по БТИ: внутренние 30/130/160 мм; наружные стены показаны контуром, числовая толщина на S15 не читается.")


def draw_plan(d: DXF) -> None:
    # Base follows the measured lower BTI chain: 3840 | 1740 | 2090 | 1730 | 3850.
    x0, y0 = 700, 850
    bedroom = (x0, y0, x0 + 3840, y0 + 2810)
    # User-confirmed room mapping for the lower BTI row:
    # 5 bedroom → 8 wardrobe → 7 toilet → 6 bathroom → 2 child room.
    wardrobe = (x0 + 3970, y0, x0 + 5710, y0 + 1740)
    toilet = (x0 + 5870, y0, x0 + 7960, y0 + 1740)
    bath = (x0 + 8120, y0, x0 + 9850, y0 + 1740)
    child = (x0 + 9980, y0, x0 + 13830, y0 + 2810)

    wall = "A-BTI-WALL"

    # Lower-row wall network. Room coordinates are inner faces. Internal wall
    # bands use the exact BTI gaps: 130 | 160 | 160 | 130 mm. The external wall
    # thickness is not numerically specified on S15, so only its inner contour
    # is drawn and must not be measured as an exterior wall thickness.
    d.line(wall, bedroom[0], y0, child[2], y0)
    d.line(wall, bedroom[0], bedroom[3], bedroom[2], bedroom[3])
    d.line(wall, child[0], child[3], child[2], child[3])

    # Exterior walls split around the two confirmed 1600 mm windows.
    d.line(wall, bedroom[0], y0, bedroom[0], y0 + 610)
    d.line(wall, bedroom[0], y0 + 2210, bedroom[0], bedroom[3])
    d.line(wall, child[2], y0, child[2], y0 + 610)
    d.line(wall, child[2], y0 + 2210, child[2], child[3])

    # Side bands of the three-room block and their corridor openings.
    d.rect(wall, bedroom[2], y0, wardrobe[0], y0 + 1870)       # t=130; P6 above = 940
    d.rect(wall, wardrobe[2], y0, toilet[0], wardrobe[3] + 30) # t=160
    d.rect(wall, toilet[2], y0, bath[0], toilet[3] + 30)       # t=160
    d.rect(wall, bath[2], y0, child[0], y0 + 1900)             # t=130; child opening above = 910

    # 30 mm corridor-side partitions, split by the BTI upper chains.
    service_top = wardrobe[3]
    top_t = 30
    for x1, x2 in (
        (wardrobe[0], wardrobe[0] + 400),
        (wardrobe[0] + 1110, wardrobe[2]),
        (toilet[0], toilet[0] + 760),
        (toilet[0] + 1570, toilet[2]),
        (bath[0], bath[0] + 140),
        (bath[0] + 950, bath[2]),
    ):
        d.rect(wall, x1, service_top, x2, service_top + top_t)

    for x, label in (
        ((bedroom[2] + wardrobe[0]) / 2, "t=130"),
        ((wardrobe[2] + toilet[0]) / 2, "t=160"),
        ((toilet[2] + bath[0]) / 2, "t=160"),
        ((bath[2] + child[0]) / 2, "t=130"),
    ):
        d.text("A-BTI-DIM", x - 45, y0 + 520, 85, label, 90)
    d.text("A-BTI-DIM", wardrobe[0] + 80, service_top + 105, 85, "t=30 по верхней границе блока")

    # Kitchen and terrace occupy the upper/right BTI zone.  Their dimensions are
    # independently visible in S15; the short connecting corridor is kept dashed.
    kitchen = (x0 + 8300, y0 + 3650, x0 + 14010, y0 + 7150)  # 5710 × 3500
    terrace = (kitchen[2] + 130, kitchen[1] + 250, kitchen[2] + 2130, kitchen[1] + 3250)
    entry = (x0 + 6000, y0 + 3000, x0 + 8090, y0 + 4675)  # 2090 × 1675 fragment
    d.rect(wall, *kitchen)
    d.rect(wall, *terrace)
    d.rect(wall, *entry)

    # Corridor 4 is the continuous zone above the three small rooms and between
    # the side openings of bedroom and child room. Its link to entry 3 continues
    # upward; the dashed polygon is a topology zone, not a fabricated wall face.
    corridor_bottom = service_top + top_t
    corridor_top = bedroom[3]
    corridor = [
        (bedroom[2], y0 + 1870),
        (wardrobe[0], y0 + 1870),
        (wardrobe[0], corridor_bottom),
        (bath[2], corridor_bottom),
        (bath[2], y0 + 1900),
        (child[0], y0 + 1900),
        (child[0], corridor_top),
        (bedroom[2], corridor_top),
    ]
    d.polyline("A-BTI-TOPOLOGY", corridor, closed=True)
    corridor_mid_x = (wardrobe[0] + bath[2]) / 2
    d.line("A-BTI-TOPOLOGY", corridor_mid_x, corridor_top, corridor_mid_x, entry[1])
    d.text("A-BTI-TOPOLOGY", wardrobe[0] + 520, corridor_top - 280, 155, "4 КОРИДОР")
    d.text("A-BTI-TOPOLOGY", wardrobe[0] + 520, corridor_top - 490, 105, "к 3, 5, 8, 7, 6 и 2; ширина полного контура н/д")
    d.text("A-BTI-DIM", bedroom[2] + 100, y0 + 2340, 95, "P6: 940 = 2810-1870")
    d.text("A-BTI-DIM", bath[2] - 1300, y0 + 2370, 95, "проём к 2: 910 = 2810-1900")

    d.text("A-CONTROL", bedroom[0] + 660, bedroom[3] + 210, 105, "P6 4-5: проём 940 по БТИ; потолок ниже; отметка потолка н/д")

    room_label(d, bedroom[0] + 450, bedroom[1] + 1700, "5", "СПАЛЬНЯ", "3840x2810", "3870 x 2830/2870")
    d.text("A-CEILING", bedroom[0] + 450, bedroom[1] + 950, 125, "H=2750 вне перехода 4–5; в проёме потолок ниже (отметка н/д)")
    compact_room_label(d, wardrobe[0] + 110, wardrobe[1] + 1190, "8", "ГАРДЕР", "1740x1740", "1739/1745 x1732/1730")
    d.text("A-CEILING", wardrobe[0] + 110, wardrobe[1] + 230, 90, "H=2712–2718; внутр. 1748")
    compact_room_label(d, toilet[0] + 170, toilet[1] + 1190, "7", "ТУАЛЕТ", "2090x1740", "общая цепь н/д")
    d.rect("A-CONTROL", toilet[0] + 680, toilet[1] + 250, toilet[0] + 1136, toilet[1] + 706)
    d.text("A-CONTROL", toilet[0] + 350, toilet[1] + 100, 85, "короб 456/t28; WC~500")
    compact_room_label(d, bath[0] + 130, bath[1] + 1190, "6", "ВАННАЯ", "1730x1740", "1745x1740; стар. 1740x1730")
    d.circle("A-CONFLICT", bath[0] + 1480, bath[1] + 1230, 140)
    d.text("A-CONFLICT", bath[0] + 1430, bath[1] + 1180, 120, "!")
    d.text("A-CONTROL", bath[0] + 130, bath[1] + 220, 90, "S-01: только локально")
    room_label(d, child[0] + 420, child[1] + 1700, "2", "ДЕТСКАЯ", "3850x2810", "сторона 3825/3837; 2-я ось н/д")
    d.text("A-CEILING", child[0] + 420, child[1] + 950, 125, "H=2712–2716; центр 2715; О-01 радиатор/окно — ось н/д")
    room_label(d, kitchen[0] + 470, kitchen[1] + 2270, "1", "КУХНЯ-ГОСТИНАЯ", "5710x3500", "5705x3550; локально H=2530 у D15/D50")
    d.text("A-CEILING", kitchen[0] + 470, kitchen[1] + 1520, 130, "H углы: 2714–2727; центр: 2719")
    d.text("A-CONTROL", kitchen[0] + 470, kitchen[1] + 1200, 120, "Э-01: розетки D15/D50 — координата на плане н/д")
    room_label(d, terrace[0] + 180, terrace[1] + 1700, "9", "ТЕРРАСА", "2000x3000", "3310 x 2110/2130")
    d.circle("A-CONFLICT", terrace[0] + 1630, terrace[1] + 2020, 150)
    d.text("A-CONFLICT", terrace[0] + 1580, terrace[1] + 1970, 130, "!")
    d.text("A-CONFLICT", terrace[0] + 180, terrace[1] + 520, 115, "Сильное расхождение БТИ/контроль: подтверждать контур и тип террасы")
    room_label(d, entry[0] + 180, entry[1] + 950, "3", "ПРИХОЖАЯ", "фрагмент 2090x1675", "D1 1140x2150; Э-02 н/д")

    # Readable BTI dimension chains.
    dim = "A-BTI-DIM"
    d.dim_h(dim, bedroom[0], bedroom[2], bedroom[1], bedroom[1] - 480, "3840")
    d.dim_h(dim, wardrobe[0], wardrobe[2], wardrobe[1], wardrobe[1] - 480, "1740")
    d.dim_h(dim, toilet[0], toilet[2], toilet[1], toilet[1] - 480, "2090")
    d.dim_h(dim, bath[0], bath[2], bath[1], bath[1] - 480, "1730")
    d.dim_h(dim, child[0], child[2], child[1], child[1] - 480, "3850")
    d.dim_v(dim, bedroom[1], bedroom[3], bedroom[0], bedroom[0] - 480, "2810")
    d.dim_v(dim, wardrobe[1], wardrobe[3], wardrobe[0], wardrobe[0] - 400, "1740")
    d.dim_v(dim, child[1], child[3], child[2], child[2] + 480, "2810")
    d.dim_h(dim, kitchen[0], kitchen[2], kitchen[3], kitchen[3] + 440, "5710")
    d.dim_v(dim, kitchen[1], kitchen[3], kitchen[2], kitchen[2] + 480, "3500")
    d.dim_h(dim, terrace[0], terrace[2], terrace[1], terrace[1] - 430, "2000")
    d.dim_v(dim, terrace[1], terrace[3], terrace[2], terrace[2] + 430, "3000")
    d.dim_h(dim, entry[0], entry[2], entry[3], entry[3] + 350, "2090 = 610 + 1010 + 470")
    d.dim_v(dim, entry[1], entry[3], entry[0], entry[0] - 360, "1675")

    # Control bars show the real on-site values without changing the BTI contour.
    d.dim_h("A-CONTROL", kitchen[0], kitchen[0] + 5705, kitchen[1], kitchen[1] - 780, "контроль 5705")
    d.dim_v("A-CONTROL", kitchen[1], kitchen[1] + 3550, kitchen[0], kitchen[0] - 700, "контроль 3550")
    d.dim_h("A-CONTROL", bedroom[0], bedroom[0] + 3870, bedroom[1], bedroom[1] - 800, "контроль 3870")
    d.dim_v("A-CONTROL", bedroom[1], bedroom[1] + 2830, bedroom[0], bedroom[0] - 730, "2830/2870")

    # Openings: location from topology; only D1/D2 have confirmed clear size.
    # D2 is on the common wall of entry/corridor and kitchen-living room, not
    # on the lower kitchen wall. Its offset from the corners is still unknown.
    door_h(
        d,
        entry[0] + 520,
        entry[3],
        1140,
        "D1",
        "контроль 1140x2150; сегмент БТИ 1010; петли/привязка н/д",
    )
    door_v(d, kitchen[0] - 65, kitchen[1], 915, "D2", "915x2150; из прихожей; привязка н/д")
    door_h(d, bath[0] + 140, bath[3] + 30, 810, "D3", "сегмент БТИ 810; чистый проём проверить")
    door_h(d, toilet[0] + 760, toilet[3] + 30, 810, "D4", "сегмент БТИ 810; чистый проём проверить")
    door_h(d, wardrobe[0] + 400, wardrobe[3] + 30, 710, "D5", "сегмент БТИ 710; чистый проём проверить")
    # Windows/openings corrected from the exterior BTI chains.  O1 is the
    # glazed opening to the terrace, not an opening in the upper kitchen wall.
    window_v(d, bedroom[0] - 65, bedroom[1] + 610, 1600, "O3", "окно 1600; низ 610, верх 600 (БТИ)", bedroom[0] + 180, bedroom[1] + 450)
    window_v(d, child[2] + 65, child[1] + 610, 1600, "O2", "окно 1600; низ 610, верх 600 (БТИ)", child[0] + 420, child[1] + 450)
    window_v(d, kitchen[2] + 65, kitchen[1] + 600, 1600, "O1", "витраж/выход на террасу 1600; низ 600, верх 1300 (БТИ)", kitchen[0] + 2100, kitchen[1] + 540)

    # 1000 mm scale bar for printed-scale verification.
    sx, sy = 17800, 1250
    d.line("A-BTI-DIM", sx, sy, sx + 1000, sy)
    for x in (sx, sx + 500, sx + 1000):
        d.line("A-BTI-DIM", x, sy - 80, x, sy + 80)
    d.text("A-BTI-DIM", sx, sy - 270, 120, "0")
    d.text("A-BTI-DIM", sx + 420, sy - 270, 120, "500")
    d.text("A-BTI-DIM", sx + 880, sy - 270, 120, "1000 мм")
    d.text("A-TEXT", sx - 120, sy + 260, 130, "Контроль масштаба М 1:50: 1000 мм = 20 мм на бумаге")


def build() -> Path:
    d = DXF()
    header(d)
    tables(d)
    d.add(0, "SECTION")
    d.add(2, "ENTITIES")
    title_and_legend(d)
    draw_plan(d)
    d.add(0, "ENDSEC")
    d.add(0, "EOF")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(d.content(), encoding="cp1251", newline="")
    return OUT


if __name__ == "__main__":
    print(build())
