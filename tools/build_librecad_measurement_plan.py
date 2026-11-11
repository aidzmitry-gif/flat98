# -*- coding: utf-8 -*-
"""Build the APT-001 measurement plan for LibreCAD.

The file is deliberately written as a plain DXF (AC1015, CP1251): it opens in
LibreCAD without add-ons and every line/text item stays editable.  Geometry on
the CONFIRMED layer has an explicitly measured dimension.  Elements on the
SCHEMATIC layer show topology only and must not be measured in CAD.
"""

from __future__ import annotations

from pathlib import Path


OUT = Path(__file__).resolve().parents[1] / "plans" / "01_Обмерный_план_квартиры_LibreCAD.dxf"


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

    def arrow(self, layer: str, x: float, y: float, direction: int, size: float = 75) -> None:
        """Open dimension arrow. direction: +1 right/up, -1 left/down."""
        if direction in (1, -1):
            self.line(layer, x, y, x + direction * size, y + size * 0.45)
            self.line(layer, x, y, x + direction * size, y - size * 0.45)

    def dim_h(self, x1: float, x2: float, object_y: float, dim_y: float, label: str) -> None:
        layer = "A-DIM"
        self.line(layer, x1, object_y, x1, dim_y)
        self.line(layer, x2, object_y, x2, dim_y)
        self.line(layer, x1, dim_y, x2, dim_y)
        self.arrow(layer, x1, dim_y, 1)
        self.arrow(layer, x2, dim_y, -1)
        self.text(layer, (x1 + x2) / 2 - len(label) * 33, dim_y + 120, 120, label)

    def dim_v(self, y1: float, y2: float, object_x: float, dim_x: float, label: str) -> None:
        layer = "A-DIM"
        self.line(layer, object_x, y1, dim_x, y1)
        self.line(layer, object_x, y2, dim_x, y2)
        self.line(layer, dim_x, y1, dim_x, y2)
        self.line(layer, dim_x, y1, dim_x + 34, y1 + 75)
        self.line(layer, dim_x, y1, dim_x - 34, y1 + 75)
        self.line(layer, dim_x, y2, dim_x + 34, y2 - 75)
        self.line(layer, dim_x, y2, dim_x - 34, y2 - 75)
        self.text(layer, dim_x - 65, (y1 + y2) / 2 - len(label) * 33, 120, label, 90)

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
        ("$LTSCALE", 40, 100),
        ("$DIMTXT", 40, 120),
    ):
        d.add(9, name)
        d.add(code, value)
    d.add(0, "ENDSEC")


def tables(d: DXF) -> None:
    layers = [
        ("A-PRINT", 8, "CONTINUOUS"),
        ("A-WALL-CONFIRMED", 7, "CONTINUOUS"),
        ("A-SCHEMATIC", 30, "DASHED"),
        ("A-OPENINGS-SCHEM", 4, "DASHED"),
        ("A-DIM", 5, "CONTINUOUS"),
        ("A-TEXT", 7, "CONTINUOUS"),
        ("A-CEILING", 3, "CONTINUOUS"),
        ("A-ENGINEERING-SCHEM", 6, "DASHED"),
        ("A-SOURCE", 8, "CONTINUOUS"),
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


def title_block(d: DXF) -> None:
    d.rect("A-PRINT", -1000, -15000, 13850, 6000)
    d.rect("A-PRINT", 8750, -11200, 13250, 4800)
    d.text("A-TEXT", 9000, 4350, 210, "APT-001 - ОБМЕРНЫЙ ПЛАН")
    d.text("A-TEXT", 9000, 3950, 170, "LibreCAD DXF | модель 1:1 | единицы: мм")
    d.text("A-TEXT", 9000, 3600, 170, "Печать: A3, портрет, масштаб 1:50, 100%")
    d.line("A-PRINT", 8950, 3250, 13050, 3250)
    d.text("A-TEXT", 9000, 2920, 210, "СТАТУС ГЕОМЕТРИИ")
    d.text("A-TEXT", 9000, 2570, 160, "Сплошной слой A-WALL-CONFIRMED:")
    d.text("A-TEXT", 9000, 2320, 160, "размер контура численно подтвержден.")
    d.text("A-TEXT", 9000, 1900, 160, "Пунктирные слои: взаимное положение,")
    d.text("A-TEXT", 9000, 1650, 160, "не использовать для заказа материалов.")
    d.text("A-TEXT", 9000, 1150, 210, "ПРОЕМЫ")
    d.text("A-TEXT", 9000, 800, 160, "Д1 вход: 1140 x 2150; привязка н/д")
    d.text("A-TEXT", 9000, 550, 160, "Д2 кухня/прихожая: 915 x 2150; привязка н/д")
    d.text("A-TEXT", 9000, 300, 160, "О1-О3, Д3-Д5 и П6: размеры и привязки н/д")
    d.line("A-PRINT", 8950, -100, 13050, -100)
    d.text("A-TEXT", 9000, -450, 210, "ВЫСОТЫ ПОТОЛКА")
    for y, text in (
        (-800, "1 кухня-гостиная: 2714-2727; центр 2719"),
        (-1050, "2 детская: 2712-2716; центр 2715"),
        (-1300, "3 прихожая: 2750"),
        (-1550, "4 коридор: 2750 вне перехода 4-5"),
        (-1800, "5 спальня: 2750 вне перехода 4-5"),
        (-2050, "8 гардеробная: 2712-2718"),
        (-2300, "Переход 4-5: потолок ниже, отметка н/д"),
    ):
        d.text("A-CEILING", 9000, y, 145, text)
    d.line("A-PRINT", 8950, -2700, 13050, -2700)
    d.text("A-TEXT", 9000, -3050, 210, "ИНЖЕНЕРИЯ - СХЕМАТИЧЕСКИ")
    for y, text in (
        (-3400, "Э-01: розетки кухни D15/D50 - оси н/д"),
        (-3650, "Э-02: щит прихожей - положение/габариты уточнить"),
        (-3900, "О-01/О-02: радиаторы детской и спальни - оси н/д"),
        (-4150, "С-01: ванная - выводы на отдельном обмере"),
        (-4400, "С-02/03/04: туалет, унитаз, короб - см. ведомость"),
        (-4650, "В-01: вентиляция - см. ведомость инженерных точек"),
    ):
        d.text("A-ENGINEERING-SCHEM", 9000, y, 145, text)
    d.line("A-PRINT", 8950, -5100, 13050, -5100)
    d.text("A-SOURCE", 9000, -5450, 160, "Источники: S01-S14, U01 от 10.08.2026")
    d.text("A-SOURCE", 9000, -5700, 160, "Подробности: docs/04, docs/07 и docs/08 проекта")
    d.text("A-SOURCE", 9000, -6150, 145, "Контур стен - без толщин: толщины не обмерены.")


def rooms_and_dimensions(d: DXF) -> None:
    wall = "A-WALL-CONFIRMED"
    provisional = "A-SCHEMATIC"
    opening = "A-OPENINGS-SCHEM"
    text = "A-TEXT"
    ceiling = "A-CEILING"
    eng = "A-ENGINEERING-SCHEM"

    # Confirmed contour: kitchen-living room, 3550 x 5705.
    d.rect(wall, 0, -5705, 3550, 0)
    d.text(text, 250, -650, 235, "1 КУХНЯ-ГОСТИНАЯ")
    d.text(text, 250, -980, 160, "контрольный контур 3550 x 5705")
    d.text(text, 250, -1250, 145, "доп. горизонталь контура: 2749")
    d.text(ceiling, 250, -1510, 145, "H 2714-2727; центр 2719")
    d.text(text, 250, -1770, 130, "локально у розеток: H 2530; D15/D50")
    d.dim_h(0, 3550, 0, 500, "3550")
    d.dim_v(-5705, 0, 0, -450, "5705")

    # Terrace contour: 3310 wide; two recorded depths.
    d.rect(wall, 120, 0, 3430, 2110)
    d.text(text, 320, 1750, 220, "9 ТЕРРАСА")
    d.text(text, 320, 1490, 145, "открытая; высота н/п")
    d.text(text, 320, 1240, 145, "остекление 1655; проем 1298")
    d.dim_h(120, 3430, 2110, 2550, "3310")
    d.dim_v(0, 2110, 120, -250, "2110 / 2130")

    # Relationship rooms: dashed only. Their unknown axes must never receive dimensions.
    d.rect(provisional, 3550, -5705, 7387, 0)
    d.text(text, 3850, -650, 235, "2 ДЕТСКАЯ")
    d.text(text, 3850, -970, 155, "сторона 3825 / 3837")
    d.text(ceiling, 3850, -1230, 145, "H 2712-2716; центр 2715")
    d.text(provisional, 3850, -1510, 130, "глубина и координатная связь н/д")
    d.dim_h(3550, 7387, 0, 500, "3825 / 3837")

    d.rect(provisional, 0, -7585, 3550, -5705)
    d.text(text, 250, -6200, 225, "3 ПРИХОЖАЯ (ВХОД)")
    d.text(ceiling, 250, -6480, 145, "H 2750 (углы/центр)")
    d.text(provisional, 250, -6740, 130, "контур и размерные цепочки н/д")

    # Corridor local fragments: scale-confirmed, but not a whole corridor contour.
    d.rect(wall, 3550, -7585, 4520, -5705)
    d.rect(wall, 3550, -9365, 4510, -7585)
    d.text(text, 3620, -6120, 210, "4 КОРИДОР")
    d.text(text, 3620, -6380, 115, "A: 970 x 1880")
    d.text(text, 3620, -6600, 115, "B: 960 x 1780")
    d.text(text, 3620, -6820, 115, "до балки: 630")
    d.text(ceiling, 3620, -7040, 115, "H 2750*")
    d.dim_h(3550, 4520, -5705, -5350, "970")
    d.dim_v(-7585, -5705, 3550, 3300, "1880")
    d.dim_v(-9365, -7585, 4510, 4740, "1780")

    # Bathroom and toilet stay schematic because full working outlines are absent.
    d.rect(provisional, 4520, -6955, 6260, -5705)
    d.text(text, 4680, -6300, 180, "6 ВАННАЯ")
    d.text(provisional, 4680, -6560, 115, "контур / высота н/д")
    d.rect(provisional, 4520, -8205, 6260, -6955)
    d.text(text, 4680, -7480, 180, "7 ТУАЛЕТ")
    d.text(provisional, 4680, -7740, 115, "контур н/д; короб 456, t=28")

    # Wardrobe and bedroom are confirmed local contours.
    d.rect(wall, 4520, -9935, 6265, -8205)
    d.text(text, 4680, -8650, 210, "8 ГАРДЕРОБНАЯ")
    d.text(text, 4680, -8910, 145, "1739 / 1745 x 1732 / 1730")
    d.text(text, 4680, -9160, 145, "внутренняя отметка: 1748")
    d.text(ceiling, 4680, -9410, 145, "H 2712-2718")
    d.dim_h(4520, 6265, -8205, -7970, "1739 / 1745")
    d.dim_v(-9935, -8205, 6265, 6510, "1732 / 1730")

    d.rect(wall, 3550, -13805, 6420, -9935)
    d.text(text, 3800, -10500, 235, "5 СПАЛЬНЯ")
    d.text(text, 3800, -10780, 155, "2870 / 2830 x 3870")
    d.text(ceiling, 3800, -11040, 145, "H 2750 вне перехода 4-5")
    d.text(provisional, 3800, -11300, 135, "в переходе: потолок ниже; H н/д")
    d.dim_h(3550, 6420, -13805, -14100, "2870 / 2830")
    d.dim_v(-13805, -9935, 6420, 6760, "3870")

    # P6 is an explicitly unknown transition: no invented width, height, or anchors.
    d.line(provisional, 4030, -9365, 4030, -9935)
    d.line(provisional, 3300, -9650, 4030, -9650)
    d.text(provisional, 500, -9670, 125, "П6 4-5: проем, ниже потолок; размеры н/д")

    # Openings. D1/D2 have confirmed clear dimensions only; their anchors are schematic.
    d.line(opening, 1555, -5705, 2470, -5705)
    d.line(opening, 1555, -5625, 1555, -5785)
    d.line(opening, 2470, -5625, 2470, -5785)
    d.text(opening, 1370, -4580, 145, "Д2 915 x 2150; привязка н/д")
    d.line(opening, 0, -6390, 0, -7530)
    d.line(opening, -80, -6390, 80, -6390)
    d.line(opening, -80, -7530, 80, -7530)
    d.text(opening, 240, -7300, 145, "Д1 1140 x 2150; привязка н/д")
    for x, y, label in (
        (800, 0, "О1"),
        (5200, 0, "О2"),
        (4550, -13805, "О3"),
    ):
        d.line(opening, x, y, x + 550, y)
        d.text(opening, x + 140, y + 140, 140, f"{label}: ширина/привязка н/д")
    for y, label in ((-6650, "Д3"), (-7850, "Д4"), (-9000, "Д5")):
        d.line(opening, 4520, y, 4520, y - 500)
        d.line(opening, 4440, y, 4600, y)
        d.line(opening, 4440, y - 500, 4600, y - 500)
        d.text(opening, 4640, y - 260, 110, label)

    # Engineering is a separate non-coordinate layer. Only the kitchen point is
    # shown in the plan; the remaining items are listed in the title block to
    # avoid turning an unknown position into a measurable CAD coordinate.
    d.circle(eng, 1150, -2850, 80)
    d.text(eng, 1280, -2900, 130, "Э-01 розетки D15/D50 - положение н/д")

    # 1000 mm scale bar verifies print scale.
    d.line("A-DIM", 8800, -6900, 9800, -6900)
    d.line("A-DIM", 8800, -6820, 8800, -6980)
    d.line("A-DIM", 9300, -6820, 9300, -6980)
    d.line("A-DIM", 9800, -6820, 9800, -6980)
    d.text("A-DIM", 8800, -7180, 130, "0")
    d.text("A-DIM", 9200, -7180, 130, "500")
    d.text("A-DIM", 9700, -7180, 130, "1000 мм")


def build() -> Path:
    d = DXF()
    header(d)
    tables(d)
    d.add(0, "SECTION")
    d.add(2, "ENTITIES")
    title_block(d)
    rooms_and_dimensions(d)
    d.add(0, "ENDSEC")
    d.add(0, "EOF")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(d.content(), encoding="cp1251", newline="")
    return OUT


if __name__ == "__main__":
    print(build())
