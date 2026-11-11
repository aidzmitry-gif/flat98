# -*- coding: utf-8 -*-
"""Build APT-001 revision 13 as one evidence-bound vector scene.

The same scene is exported to:

* LibreCAD DXF in real millimetres (model 1:1);
* SVG on an A2 landscape sheet at 1:50;
* PDF on a true 594 x 420 mm page.

Only the apartment sources B01/Cxx/U01/T01/V01 are data sources.  The foreign
reference supplied by the user is deliberately absent from this module: it is
used only to define generic graphic hierarchy in docs/11.
"""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
from pathlib import Path
from typing import Any, Iterable

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A2, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
PLANS = ROOT / "plans"
DXF_OUT = PLANS / "04_Подробный_обмерный_план_LibreCAD.dxf"
SVG_OUT = PLANS / "04_Подробный_обмерный_план_A2_М1_50.svg"
PDF_OUT = PLANS / "04_Подробный_обмерный_план_A2_М1_50.pdf"

SCALE = 50.0
PAGE_W = 594.0 * SCALE  # 29700 model mm
PAGE_H = 420.0 * SCALE  # 21000 model mm


@dataclass(frozen=True)
class LayerStyle:
    color: str
    dxf_color: int
    paper_width_mm: float
    dashed: bool = False
    fill: str | None = None


LAYERS: dict[str, LayerStyle] = {
    "A-SHEET": LayerStyle("#222222", 7, 0.18),
    "A-WALL-FILL": LayerStyle("#d8d8d8", 8, 0.00, fill="#d8d8d8"),
    "A-WALL-OUTLINE": LayerStyle("#111111", 7, 0.50),
    "A-EXTERIOR-GRAPHIC": LayerStyle("#777777", 8, 0.70),
    "A-OPENING": LayerStyle("#176c45", 3, 0.35),
    "A-DIM-BTI": LayerStyle("#202020", 7, 0.18),
    "A-DIM-CONTROL": LayerStyle("#1668a9", 5, 0.18, dashed=True),
    "A-TOPOLOGY": LayerStyle("#7a7a7a", 8, 0.18, dashed=True),
    "A-EQUIPMENT": LayerStyle("#587a57", 3, 0.18),
    "A-CEILING": LayerStyle("#72428e", 6, 0.18),
    "A-CONFLICT": LayerStyle("#bf1e2e", 1, 0.25),
    "A-UNKNOWN": LayerStyle("#aa6800", 30, 0.18, dashed=True),
    "A-TEXT": LayerStyle("#202020", 7, 0.18),
    "A-AREA": LayerStyle("#b01d28", 1, 0.18),
    "A-SOURCE": LayerStyle("#5e5e5e", 8, 0.13),
    "A-INSET": LayerStyle("#303030", 7, 0.18),
}


@dataclass
class Primitive:
    kind: str
    layer: str
    data: dict[str, Any]


class Scene:
    def __init__(self) -> None:
        self.items: list[Primitive] = []

    def line(self, layer: str, x1: float, y1: float, x2: float, y2: float) -> None:
        self.items.append(Primitive("line", layer, {"x1": x1, "y1": y1, "x2": x2, "y2": y2}))

    def polyline(self, layer: str, points: Iterable[tuple[float, float]], *, closed: bool = False) -> None:
        self.items.append(Primitive("polyline", layer, {"points": list(points), "closed": closed}))

    def rect(self, layer: str, x1: float, y1: float, x2: float, y2: float) -> None:
        self.items.append(Primitive("rect", layer, {"x1": x1, "y1": y1, "x2": x2, "y2": y2}))

    def circle(self, layer: str, x: float, y: float, radius: float) -> None:
        self.items.append(Primitive("circle", layer, {"x": x, "y": y, "radius": radius}))

    def text(
        self,
        layer: str,
        x: float,
        y: float,
        height: float,
        value: str,
        *,
        rotation: float = 0,
        anchor: str = "start",
        bold: bool = False,
    ) -> None:
        # At 1:50, 100 model millimetres print as 2.0 mm.  Dimension and
        # ceiling-point labels may use 1.8 mm; all other annotations stay at
        # or above the 2.0 mm readability floor defined by the plan passport.
        minimum = 90.0 if layer in {"A-DIM-BTI", "A-DIM-CONTROL", "A-CEILING"} else 100.0
        height = max(height, minimum)
        self.items.append(
            Primitive(
                "text",
                layer,
                {
                    "x": x,
                    "y": y,
                    "height": height,
                    "value": value,
                    "rotation": rotation,
                    "anchor": anchor,
                    "bold": bold,
                },
            )
        )

    def multiline(
        self,
        layer: str,
        x: float,
        y: float,
        height: float,
        lines: Iterable[str],
        *,
        leading: float | None = None,
        bold_first: bool = False,
    ) -> None:
        step = leading or height * 1.42
        for index, value in enumerate(lines):
            self.text(layer, x, y - index * step, height, value, bold=bold_first and index == 0)


class DXFWriter:
    def __init__(self) -> None:
        self.parts: list[str] = []

    def add(self, code: int, value: Any) -> None:
        if isinstance(value, float):
            value = f"{value:.4f}".rstrip("0").rstrip(".")
        self.parts.extend((str(code), str(value)))

    def entity(self, kind: str, layer: str) -> None:
        self.add(0, kind)
        self.add(8, layer)

    def header(self) -> None:
        self.add(0, "SECTION")
        self.add(2, "HEADER")
        for name, code, value in (
            ("$ACADVER", 1, "AC1015"),
            ("$DWGCODEPAGE", 3, "ANSI_1251"),
            ("$INSUNITS", 70, 4),
            ("$MEASUREMENT", 70, 1),
            ("$LTSCALE", 40, 80),
        ):
            self.add(9, name)
            self.add(code, value)
        self.add(0, "ENDSEC")

    def tables(self) -> None:
        self.add(0, "SECTION")
        self.add(2, "TABLES")
        self.add(0, "TABLE")
        self.add(2, "LTYPE")
        self.add(70, 2)
        self.add(0, "LTYPE")
        self.add(2, "CONTINUOUS")
        self.add(70, 0)
        self.add(3, "Solid")
        self.add(72, 65)
        self.add(73, 0)
        self.add(40, 0)
        self.add(0, "LTYPE")
        self.add(2, "DASHED")
        self.add(70, 0)
        self.add(3, "Dash")
        self.add(72, 65)
        self.add(73, 2)
        self.add(40, 150)
        self.add(49, 90)
        self.add(49, -60)
        self.add(0, "ENDTAB")

        self.add(0, "TABLE")
        self.add(2, "LAYER")
        self.add(70, len(LAYERS))
        for name, style in LAYERS.items():
            self.add(0, "LAYER")
            self.add(2, name)
            self.add(70, 0)
            self.add(62, style.dxf_color)
            self.add(6, "DASHED" if style.dashed else "CONTINUOUS")
            self.add(370, max(0, round(style.paper_width_mm * 100)))
        self.add(0, "ENDTAB")

        self.add(0, "TABLE")
        self.add(2, "STYLE")
        self.add(70, 1)
        self.add(0, "STYLE")
        self.add(2, "STANDARD")
        self.add(70, 0)
        self.add(40, 0)
        self.add(41, 1)
        self.add(50, 0)
        self.add(71, 0)
        self.add(42, 2.5)
        self.add(3, "arial.ttf")
        self.add(4, "")
        self.add(0, "ENDTAB")
        self.add(0, "ENDSEC")

    def solid_rect(self, layer: str, x1: float, y1: float, x2: float, y2: float) -> None:
        self.entity("SOLID", layer)
        for code, point in zip((10, 11, 12, 13), ((x1, y1), (x2, y1), (x1, y2), (x2, y2))):
            self.add(code, point[0])
            self.add(code + 10, point[1])
            self.add(code + 20, 0)

    def export(self, scene: Scene, path: Path) -> None:
        self.header()
        self.tables()
        self.add(0, "SECTION")
        self.add(2, "ENTITIES")
        for item in scene.items:
            d = item.data
            if item.kind == "line":
                self.entity("LINE", item.layer)
                for code, value in ((10, d["x1"]), (20, d["y1"]), (30, 0), (11, d["x2"]), (21, d["y2"]), (31, 0)):
                    self.add(code, value)
            elif item.kind in {"polyline", "rect"}:
                if item.kind == "rect":
                    pts = [(d["x1"], d["y1"]), (d["x2"], d["y1"]), (d["x2"], d["y2"]), (d["x1"], d["y2"])]
                    closed = True
                    if LAYERS[item.layer].fill:
                        self.solid_rect(item.layer, d["x1"], d["y1"], d["x2"], d["y2"])
                else:
                    pts = d["points"]
                    closed = d["closed"]
                self.entity("LWPOLYLINE", item.layer)
                self.add(90, len(pts))
                self.add(70, 1 if closed else 0)
                for x, y in pts:
                    self.add(10, x)
                    self.add(20, y)
            elif item.kind == "circle":
                self.entity("CIRCLE", item.layer)
                self.add(10, d["x"])
                self.add(20, d["y"])
                self.add(30, 0)
                self.add(40, d["radius"])
            elif item.kind == "text":
                self.entity("TEXT", item.layer)
                self.add(10, d["x"])
                self.add(20, d["y"])
                self.add(30, 0)
                self.add(40, d["height"])
                self.add(1, d["value"])
                self.add(7, "STANDARD")
                self.add(50, d["rotation"])
                if d["anchor"] == "middle":
                    self.add(72, 1)
                    self.add(73, 2)
                    self.add(11, d["x"])
                    self.add(21, d["y"])
                    self.add(31, 0)
        self.add(0, "ENDSEC")
        self.add(0, "EOF")
        path.write_text("\r\n".join(self.parts) + "\r\n", encoding="cp1251", newline="")


def export_svg(scene: Scene, path: Path) -> None:
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="594mm" height="420mm" viewBox="0 0 {PAGE_W:g} {PAGE_H:g}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]

    def y(value: float) -> float:
        return PAGE_H - value

    for item in scene.items:
        d = item.data
        style = LAYERS[item.layer]
        width = style.paper_width_mm * SCALE
        dash = ' stroke-dasharray="90 60"' if style.dashed else ""
        if item.kind == "line":
            out.append(
                f'<line x1="{d["x1"]}" y1="{y(d["y1"])}" x2="{d["x2"]}" y2="{y(d["y2"])}" '
                f'stroke="{style.color}" stroke-width="{width:g}" fill="none"{dash}/>'
            )
        elif item.kind == "rect":
            fill = style.fill or "none"
            out.append(
                f'<rect x="{d["x1"]}" y="{y(d["y2"])}" width="{d["x2"]-d["x1"]}" height="{d["y2"]-d["y1"]}" '
                f'stroke="{style.color}" stroke-width="{width:g}" fill="{fill}"{dash}/>'
            )
        elif item.kind == "polyline":
            pts = " ".join(f'{x0},{y(y0)}' for x0, y0 in d["points"])
            tag = "polygon" if d["closed"] else "polyline"
            fill = style.fill if d["closed"] and style.fill else "none"
            out.append(f'<{tag} points="{pts}" stroke="{style.color}" stroke-width="{width:g}" fill="{fill}"{dash}/>')
        elif item.kind == "circle":
            out.append(
                f'<circle cx="{d["x"]}" cy="{y(d["y"])}" r="{d["radius"]}" stroke="{style.color}" '
                f'stroke-width="{width:g}" fill="none"{dash}/>'
            )
        elif item.kind == "text":
            anchor = "middle" if d["anchor"] == "middle" else "start"
            weight = "700" if d["bold"] else "400"
            rot = f' transform="rotate({-d["rotation"]} {d["x"]} {y(d["y"])})"' if d["rotation"] else ""
            out.append(
                f'<text x="{d["x"]}" y="{y(d["y"])}" font-family="Arial, sans-serif" font-size="{d["height"]}" '
                f'font-weight="{weight}" text-anchor="{anchor}" fill="{style.color}"{rot}>{escape(d["value"])}</text>'
            )
    out.append("</svg>")
    path.write_text("\n".join(out), encoding="utf-8")


def _register_fonts() -> tuple[str, str]:
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if regular.exists() and "APTArial" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("APTArial", str(regular)))
    if bold.exists() and "APTArial-Bold" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("APTArial-Bold", str(bold)))
    return ("APTArial" if regular.exists() else "Helvetica", "APTArial-Bold" if bold.exists() else "Helvetica-Bold")


def export_pdf(scene: Scene, path: Path) -> None:
    font_regular, font_bold = _register_fonts()
    page_size = landscape(A2)
    pdf = canvas.Canvas(str(path), pagesize=page_size, pageCompression=1)
    pdf.setTitle("APT-001 - detailed control measurement plan")

    def p(value: float) -> float:
        return value / SCALE * mm

    for item in scene.items:
        d = item.data
        style = LAYERS[item.layer]
        pdf.setStrokeColor(HexColor(style.color))
        pdf.setFillColor(HexColor(style.fill or style.color))
        pdf.setLineWidth(style.paper_width_mm * mm)
        pdf.setDash(1.8 * mm, 1.2 * mm) if style.dashed else pdf.setDash()
        if item.kind == "line":
            pdf.line(p(d["x1"]), p(d["y1"]), p(d["x2"]), p(d["y2"]))
        elif item.kind == "rect":
            pdf.rect(
                p(d["x1"]),
                p(d["y1"]),
                p(d["x2"] - d["x1"]),
                p(d["y2"] - d["y1"]),
                stroke=0 if style.fill and style.paper_width_mm == 0 else 1,
                fill=1 if style.fill else 0,
            )
        elif item.kind == "polyline":
            points = d["points"]
            if not points:
                continue
            path_obj = pdf.beginPath()
            path_obj.moveTo(p(points[0][0]), p(points[0][1]))
            for x0, y0 in points[1:]:
                path_obj.lineTo(p(x0), p(y0))
            if d["closed"]:
                path_obj.close()
            pdf.drawPath(path_obj, stroke=1, fill=1 if style.fill and d["closed"] else 0)
        elif item.kind == "circle":
            pdf.circle(p(d["x"]), p(d["y"]), p(d["radius"]), stroke=1, fill=0)
        elif item.kind == "text":
            pdf.saveState()
            pdf.translate(p(d["x"]), p(d["y"]))
            pdf.rotate(d["rotation"])
            font = font_bold if d["bold"] else font_regular
            size = p(d["height"])
            pdf.setFont(font, size)
            value = d["value"]
            offset = -pdfmetrics.stringWidth(value, font, size) / 2 if d["anchor"] == "middle" else 0
            pdf.drawString(offset, 0, value)
            pdf.restoreState()
    pdf.showPage()
    pdf.save()


def wall_rect(scene: Scene, x1: float, y1: float, x2: float, y2: float) -> None:
    scene.rect("A-WALL-FILL", x1, y1, x2, y2)
    scene.rect("A-WALL-OUTLINE", x1, y1, x2, y2)


def graphic_wall_rect(scene: Scene, x1: float, y1: float, x2: float, y2: float) -> None:
    """Show a visible wall where B01 gives its face but not a numeric thickness.

    The fixed display band is outside the measured inner face and deliberately
    is never converted into a numeric construction thickness.  A drawing may
    use a separate ``t н/д`` callout to make that uncertainty visible.
    """
    scene.rect("A-WALL-FILL", x1, y1, x2, y2)
    scene.rect("A-EXTERIOR-GRAPHIC", x1, y1, x2, y2)


def arrow_h(scene: Scene, layer: str, x: float, y: float, direction: int, size: float = 65) -> None:
    scene.line(layer, x, y, x + direction * size, y + size * 0.38)
    scene.line(layer, x, y, x + direction * size, y - size * 0.38)


def dim_h(
    scene: Scene,
    x1: float,
    x2: float,
    object_y: float,
    dim_y: float,
    label: str,
    *,
    layer: str = "A-DIM-BTI",
    height: float = 90,
) -> None:
    scene.line(layer, x1, object_y, x1, dim_y)
    scene.line(layer, x2, object_y, x2, dim_y)
    scene.line(layer, x1, dim_y, x2, dim_y)
    arrow_h(scene, layer, x1, dim_y, 1)
    arrow_h(scene, layer, x2, dim_y, -1)
    scene.text(layer, (x1 + x2) / 2, dim_y + 100, height, label, anchor="middle")


def dim_v(
    scene: Scene,
    y1: float,
    y2: float,
    object_x: float,
    dim_x: float,
    label: str,
    *,
    layer: str = "A-DIM-BTI",
    height: float = 90,
) -> None:
    scene.line(layer, object_x, y1, dim_x, y1)
    scene.line(layer, object_x, y2, dim_x, y2)
    scene.line(layer, dim_x, y1, dim_x, y2)
    size = 65
    scene.line(layer, dim_x, y1, dim_x + size * 0.38, y1 + size)
    scene.line(layer, dim_x, y1, dim_x - size * 0.38, y1 + size)
    scene.line(layer, dim_x, y2, dim_x + size * 0.38, y2 - size)
    scene.line(layer, dim_x, y2, dim_x - size * 0.38, y2 - size)
    scene.text(layer, dim_x - 100, (y1 + y2) / 2, height, label, rotation=90, anchor="middle")


def window_v(scene: Scene, x: float, y1: float, height: float, label: str) -> None:
    scene.line("A-OPENING", x - 55, y1, x - 55, y1 + height)
    scene.line("A-OPENING", x + 55, y1, x + 55, y1 + height)
    scene.line("A-OPENING", x - 130, y1, x + 130, y1)
    scene.line("A-OPENING", x - 130, y1 + height, x + 130, y1 + height)
    scene.text("A-OPENING", x + 145, y1 + height / 2, 85, label, rotation=90, anchor="middle", bold=True)


def opening_h(scene: Scene, x1: float, x2: float, y: float, label: str) -> None:
    # Dashed unknown layer is intentional: the B01 segment is not a verified
    # clear door width and carries no confirmed opening direction.
    scene.line("A-UNKNOWN", x1, y, x2, y)
    scene.line("A-UNKNOWN", x1, y - 55, x1, y + 55)
    scene.line("A-UNKNOWN", x2, y - 55, x2, y + 55)
    scene.text("A-UNKNOWN", (x1 + x2) / 2, y + 110, 75, label, anchor="middle")


def opening_v(scene: Scene, x: float, y1: float, y2: float, label: str) -> None:
    """Show a confirmed gap without inventing a door leaf or swing."""
    scene.line("A-UNKNOWN", x, y1, x, y2)
    scene.line("A-UNKNOWN", x - 55, y1, x + 55, y1)
    scene.line("A-UNKNOWN", x - 55, y2, x + 55, y2)
    scene.text("A-UNKNOWN", x + 135, (y1 + y2) / 2, 75, label, rotation=90, anchor="middle")


def radiator_zone_v(scene: Scene, x: float, y1: float, y2: float, label: str, *, interior_right: bool) -> None:
    """Non-positional radiator zone: presence under the window, axes unknown."""
    inner = 90 if interior_right else -90
    outer = 240 if interior_right else -240
    scene.rect("A-UNKNOWN", x + inner, y1 + 170, x + outer, y2 - 170)
    tx = x + (outer + (135 if interior_right else -135))
    scene.text("A-UNKNOWN", tx, (y1 + y2) / 2, 70, label, rotation=90, anchor="middle")


def ceiling_point(scene: Scene, x: float, y: float, value: str) -> None:
    scene.circle("A-CEILING", x, y, 32)
    scene.text("A-CEILING", x + 58, y - 30, 55, value)


def room_label(
    scene: Scene,
    x: float,
    y: float,
    number: str,
    name: str,
    area: str,
    size: str,
    source: str,
    *,
    compact: bool = False,
) -> None:
    radius = 82 if compact else 105
    scene.circle("A-TEXT", x, y, radius)
    scene.text("A-TEXT", x, y - (26 if compact else 30), 75 if compact else 92, number, anchor="middle", bold=True)
    scene.text("A-TEXT", x, y - 210, 86 if compact else 105, name, anchor="middle", bold=True)
    scene.text("A-AREA", x, y - 350, 72 if compact else 88, area, anchor="middle", bold=True)
    scene.text("A-DIM-BTI", x, y - 480, 68 if compact else 78, size, anchor="middle")
    scene.text("A-SOURCE", x, y - 590, 58 if compact else 68, source, anchor="middle")


def draw_apartment(scene: Scene) -> None:
    """Draw the B01 coordinate skeleton and control overlays."""
    x0, y0 = 2200.0, 8750.0
    bedroom = (x0, y0, x0 + 3840, y0 + 2810)
    wardrobe = (x0 + 3970, y0, x0 + 5710, y0 + 1740)
    toilet = (x0 + 5870, y0, x0 + 7960, y0 + 1740)
    bath = (x0 + 8120, y0, x0 + 9850, y0 + 1740)
    child = (x0 + 9980, y0, x0 + 13830, y0 + 2810)
    service_top = y0 + 1740
    # B01 shows a 360x710 utility box at the lower-right corner of room 7.
    # U02 confirms water meters in room 7; their internal axes remain unknown.
    toilet_meter_box = (toilet[2] - 710, y0, toilet[2], y0 + 360)

    # B01 does not give a universal numeric thickness for the shell.  Revision
    # 3 still shows every visible wall as a light-grey band, outside the
    # measured inner faces, while keeping its numeric thickness explicitly n/d.
    ext = "A-EXTERIOR-GRAPHIC"
    graphic_t = 120.0
    graphic_wall_rect(scene, bedroom[0], y0 - graphic_t, child[2], y0)
    graphic_wall_rect(scene, bedroom[0] - graphic_t, y0, bedroom[0], y0 + 610)
    graphic_wall_rect(scene, bedroom[0] - graphic_t, y0 + 2210, bedroom[0], bedroom[3])
    graphic_wall_rect(scene, child[2], y0, child[2] + graphic_t, y0 + 610)
    graphic_wall_rect(scene, child[2], y0 + 2210, child[2] + graphic_t, child[3])
    graphic_wall_rect(scene, bedroom[0], bedroom[3], bedroom[2], bedroom[3] + graphic_t)
    scene.line(ext, bedroom[0], y0, child[2], y0)
    scene.line(ext, bedroom[0], bedroom[3], bedroom[2], bedroom[3])
    scene.line(ext, child[0], child[3], child[2], child[3])
    scene.line(ext, bedroom[0], y0, bedroom[0], y0 + 610)
    scene.line(ext, bedroom[0], y0 + 2210, bedroom[0], bedroom[3])
    scene.line(ext, child[2], y0, child[2], y0 + 610)
    scene.line(ext, child[2], y0 + 2210, child[2], child[3])
    scene.text("A-UNKNOWN", bedroom[0] + 60, y0 + 3000, 72, "наружные/неразмерённые стены: t н/д [B01]")

    # Exact internal wall bands B01.
    wall_rect(scene, bedroom[2], y0, wardrobe[0], y0 + 1870)
    wall_rect(scene, wardrobe[2], y0, toilet[0], service_top + 30)
    wall_rect(scene, toilet[2], y0, bath[0], service_top + 30)
    wall_rect(scene, bath[2], y0, child[0], y0 + 1900)
    for x1, x2 in (
        (wardrobe[0], wardrobe[0] + 400),
        (wardrobe[0] + 1110, wardrobe[2]),
        (toilet[0], toilet[0] + 760),
        (toilet[0] + 1570, toilet[2]),
        (bath[0], bath[0] + 140),
        (bath[0] + 950, bath[2]),
    ):
        wall_rect(scene, x1, service_top, x2, service_top + 30)

    for x, label in (
        ((bedroom[2] + wardrobe[0]) / 2, "t=130"),
        ((wardrobe[2] + toilet[0]) / 2, "t=160"),
        ((toilet[2] + bath[0]) / 2, "t=160"),
        ((bath[2] + child[0]) / 2, "t=130"),
    ):
        scene.text("A-DIM-BTI", x, y0 + 520, 68, label, rotation=90, anchor="middle")
    # At M 1:50 a 30-mm wall is only 0.6 mm wide on paper.  Three individual
    # leader tags make the B01 thickness traceable to each physical wall band
    # without pretending that a full-size micro-dimension is readable.
    for tag_x in (
        wardrobe[0] + 1425,  # solid 630-mm part of upper wall 8
        toilet[0] + 380,     # solid 760-mm part of upper wall 7
        bath[0] + 1340,      # solid 780-mm part of upper wall 6
    ):
        scene.text("A-DIM-BTI", tag_x, service_top + 120, 100, "t=30 [B01]", anchor="middle")
        scene.line("A-DIM-BTI", tag_x, service_top + 80, tag_x, service_top + 30)

    # Openings in the corridor-side walls.  D3-D5 remain B01 chain segments,
    # not clean door sizes.
    opening_h(scene, wardrobe[0] + 400, wardrobe[0] + 1110, service_top + 15, "D5: B01 710*")
    opening_h(scene, toilet[0] + 760, toilet[0] + 1570, service_top + 15, "D4: B01 810*")
    opening_h(scene, bath[0] + 140, bath[0] + 950, service_top + 15, "D3: B01 810*")
    # P6 is the 940-mm opening between bedroom 5 and corridor 4.  It is not
    # a missing wall.  B01 gives its length but not a door leaf or the lowered
    # ceiling elevation, so draw an opening symbol and a dimensional callout.
    p6_x = (bedroom[2] + wardrobe[0]) / 2
    opening_v(scene, p6_x, y0 + 1870, bedroom[3], "P6")
    dim_v(scene, y0 + 1870, bedroom[3], bedroom[2], bedroom[2] - 265, "940 [B01]", height=66)
    scene.line("A-OPENING", (bath[2] + child[0]) / 2, y0 + 1900, (bath[2] + child[0]) / 2, child[3])
    scene.text("A-OPENING", bath[2] + 150, y0 + 2390, 76, "проход к 2 = 910 [B01]", rotation=90, anchor="middle")

    # Confirmed B01 utility-box footprint.  It is deliberately not drawn as a
    # door or a generic fixture: only its envelope is dimensioned.
    scene.rect("A-WALL-OUTLINE", *toilet_meter_box)
    scene.text("A-UNKNOWN", (toilet_meter_box[0] + toilet_meter_box[2]) / 2, y0 + 115, 64, "ВМ-07", anchor="middle")
    dim_h(scene, toilet_meter_box[0], toilet_meter_box[2], toilet_meter_box[3], toilet_meter_box[3] + 180, "710 [B01]", height=66)
    dim_v(scene, toilet_meter_box[1], toilet_meter_box[3], toilet_meter_box[0], toilet_meter_box[0] - 160, "360 [B01]", height=66)

    # Corridor topology: physical walls and openings are shown above.  Do not
    # close the remaining upper edge with a dashed line: it is an open route
    # to entry 3 in B01, not a wall and not a measured contour.
    scene.text("A-TOPOLOGY", (wardrobe[0] + bath[2]) / 2, y0 + 2570, 110, "4 КОРИДОР", anchor="middle", bold=True)
    scene.text("A-UNKNOWN", (wardrobe[0] + bath[2]) / 2, y0 + 2410, 70, "связи: 3,5,8,7,6,2; P6 — проход, не стена; контур/площадь н/д", anchor="middle")

    # Lower rooms end at their inner upper faces y=2810.  ST-01 is a separate
    # 200-mm wall band above those faces; kitchen and entry start at its upper
    # face.  Keeping the band out of rooms 1/2 makes 600+1600+610=2810 a
    # clear-size chain rather than a size that includes wall thickness.
    st01_t = 200
    kitchen = (bath[0], y0 + 2810 + st01_t, child[2], y0 + 6310 + st01_t)
    terrace = (kitchen[2] + 130, kitchen[1] + 250, kitchen[2] + 2130, kitchen[1] + 3250)
    entry = (toilet[0], y0 + 2810 + st01_t, toilet[2], y0 + 4485 + st01_t)

    # User confirmation: the visible upper wall of bedroom 5 continues to the
    # left wall of entry 3.  It is a single graphic wall chain; B01 does not
    # provide a numeric thickness for this outer/upper segment, so retain t n/d
    # rather than borrowing 30/130/160 mm from other walls.
    graphic_wall_rect(scene, bedroom[2], bedroom[3], entry[0], bedroom[3] + graphic_t)
    graphic_wall_rect(scene, entry[0] - graphic_t, bedroom[3], entry[0], entry[1])
    scene.line(ext, bedroom[2], bedroom[3], entry[0], bedroom[3])
    scene.text("A-UNKNOWN", (bedroom[2] + entry[0]) / 2, bedroom[3] + 260, 72, "верхняя стена 5-3: t н/д [B01]", anchor="middle")

    # At the lower-left kitchen corner B01 shows a continuous composite L:
    # ST-01 is 200 mm thick, while the 200-mm return is the 3/1 partition at
    # t=160.  The earlier 200x200 square was incorrect.  Draw the union once;
    # D2 starts above the 200-mm return.
    partition_t = kitchen[0] - entry[2]  # 160 mm from the B01 coordinate chain.
    st01 = (
        (kitchen[0] - partition_t, kitchen[1] - st01_t),
        (kitchen[2], kitchen[1] - st01_t),
        (kitchen[2], kitchen[1]),
        (kitchen[0], kitchen[1]),
        (kitchen[0], kitchen[1] + st01_t),
        (kitchen[0] - partition_t, kitchen[1] + st01_t),
    )
    scene.polyline("A-WALL-FILL", st01, closed=True)
    scene.polyline("A-WALL-OUTLINE", st01, closed=True)
    dim_v(
        scene,
        kitchen[1] - st01_t,
        kitchen[1],
        kitchen[2] - 360,
        kitchen[2] - 700,
        "СТ-01: t=200 [B01]",
        height=100,
    )

    graphic_wall_rect(scene, kitchen[0], kitchen[3], kitchen[2], kitchen[3] + graphic_t)
    graphic_wall_rect(scene, kitchen[2], kitchen[1], kitchen[2] + graphic_t, kitchen[1] + 600)
    graphic_wall_rect(scene, kitchen[2], kitchen[1] + 2200, kitchen[2] + graphic_t, kitchen[3])
    graphic_wall_rect(scene, entry[0] - graphic_t, entry[1], entry[0], entry[3])
    graphic_wall_rect(scene, entry[0], entry[3], entry[0] + 610, entry[3] + graphic_t)
    graphic_wall_rect(scene, entry[0] + 1620, entry[3], entry[2], entry[3] + graphic_t)

    # Kitchen shell split at D2 and O1.  The left B01 chain is 200+910+2390;
    # U01 gives a 915 clear control opening.
    scene.line(ext, kitchen[0], kitchen[1], kitchen[2], kitchen[1])
    scene.line(ext, kitchen[0], kitchen[3], kitchen[2], kitchen[3])
    scene.line(ext, kitchen[0], kitchen[1], kitchen[0], kitchen[1] + 200)
    scene.line(ext, kitchen[0], kitchen[1] + 1110, kitchen[0], kitchen[3])
    scene.line(ext, kitchen[2], kitchen[1], kitchen[2], kitchen[1] + 600)
    scene.line(ext, kitchen[2], kitchen[1] + 2200, kitchen[2], kitchen[3])
    opening_v(scene, kitchen[0], kitchen[1] + 200, kitchen[1] + 1110, "D2*")
    scene.text("A-DIM-BTI", kitchen[0] + 1120, kitchen[1] + 260, 100, "до D2 = 200 [B01]")
    scene.text("A-DIM-CONTROL", kitchen[0] + 660, kitchen[1] + 500, 72, "D2 3-1; B01=910; U01=915x2150; *сторона н/д")
    window_v(scene, kitchen[2], kitchen[1] + 600, 1600, "O1 1600")

    # Terrace B01 shell.
    scene.rect(ext, *terrace)
    scene.text("A-CONFLICT", terrace[0] + 100, terrace[1] + 350, 72, "B01 2000x3000 / C01 3310x2110/2130", bold=True)

    # Entry is a B01 fragment.  Its lower side is the open 3-4 transition, not
    # a wall; omitting a dashed closure prevents it from being mistaken for an
    # unmeasured partition. D1 is schematic because its corner tie is unknown
    # and the B01 1010 segment conflicts with U01 1140.
    scene.line("A-TOPOLOGY", entry[0], entry[1], entry[0], entry[3])
    scene.text("A-TOPOLOGY", (entry[0] + entry[2]) / 2, entry[1] - 150, 64, "3-4: открыто, стеновой полосы нет", anchor="middle")
    d2_entry_y1 = kitchen[1] + 200
    d2_entry_y2 = min(kitchen[1] + 1110, entry[3])
    # The lower 3/1 segment is the t=160 leg already included in the single
    # ST-01 L polygon.  Only the upper piece is separate around D2.
    if d2_entry_y2 < entry[3]:
        wall_rect(scene, entry[2], d2_entry_y2, kitchen[0], entry[3])
    scene.text("A-TOPOLOGY", (entry[2] + kitchen[0]) / 2, (d2_entry_y1 + d2_entry_y2) / 2, 70, "3-1", rotation=90, anchor="middle", bold=True)
    scene.text("A-DIM-BTI", (entry[2] + kitchen[0]) / 2, entry[3] - 180, 66, "t=160 [B01]", rotation=90, anchor="middle")
    scene.line("A-TOPOLOGY", entry[0], entry[3], entry[0] + 610, entry[3])
    scene.line("A-TOPOLOGY", entry[0] + 1620, entry[3], entry[2], entry[3])
    opening_h(scene, entry[0] + 610, entry[0] + 1620, entry[3], "D1: B01 1010*")
    scene.text("A-DIM-CONTROL", entry[0] + 1045, entry[1] + 190, 75, "D1 U01=1140x2150; *привязка/сторона н/д", anchor="middle")
    # Entry floor meets the corridor's top edge on the same B01 level.

    # Confirmed electrical location in room 3.  F08 identifies the wall and a
    # low group of three outlets, but neither image supplies two global axes.
    panel_zone = (entry[0] + 55, entry[1] + 650, entry[0] + 220, entry[3] - 250)
    scene.rect("A-UNKNOWN", *panel_zone)
    scene.text("A-EQUIPMENT", entry[0] + 390, (panel_zone[1] + panel_zone[3]) / 2, 70, "ЭЩ-03: левая стена у входа [F08]; ось/H/габарит н/д", rotation=90, anchor="middle")
    outlet_y = entry[1] + 300
    for offset in (0, 110, 220):
        scene.circle("A-EQUIPMENT", entry[0] + 135, outlet_y + offset, 32)
    scene.text("A-EQUIPMENT", entry[0] + 290, outlet_y + 110, 64, "E-03: 3 розетки у пола [F08]; ось н/д", rotation=90, anchor="middle")

    # Windows and existing radiator symbols (device sizes are unknown).
    window_v(scene, bedroom[0], y0 + 610, 1600, "O3 1600")
    radiator_zone_v(scene, bedroom[0], y0 + 610, y0 + 2210, "R-05 зона под O3; ось/габарит н/д", interior_right=True)
    window_v(scene, child[2], y0 + 610, 1600, "O2 1600")
    radiator_zone_v(scene, child[2], y0 + 610, y0 + 2210, "R-02 зона под O2; ось/габарит н/д", interior_right=False)

    # Room identity, calculation status and source.
    room_label(scene, bedroom[0] + 1920, y0 + 2470, "5", "СПАЛЬНЯ", "Sрасч.=10,79 м2", "B01 3840x2810", "B01/C02")
    room_label(scene, wardrobe[0] + 870, y0 + 1480, "8", "ГАРДЕРОБНАЯ", "Sрасч.=3,03 м2", "B01 1740x1740", "B01/C07", compact=True)
    room_label(scene, toilet[0] + 1045, y0 + 1480, "7", "ТУАЛЕТ", "Sрасч.=3,64 м2", "B01 2090x1740", "B01/T01", compact=True)
    room_label(scene, bath[0] + 865, y0 + 1480, "6", "ВАННАЯ", "Sрасч.=3,01 м2", "B01 1730x1740", "B01/V01", compact=True)
    room_label(scene, child[0] + 1925, y0 + 2470, "2", "ДЕТСКАЯ", "Sрасч.=10,82 м2", "B01 3850x2810", "B01/C10")
    room_label(scene, kitchen[0] + 2855, kitchen[1] + 3100, "1", "КУХНЯ-ГОСТИНАЯ", "Sрасч.=19,99 м2", "B01 5710x3500", "B01/C03/C12")
    room_label(scene, terrace[0] + 1000, terrace[1] + 2380, "9", "ТЕРРАСА", "Sрасч.B01=6,00 м2", "B01 2000x3000", "B01/C01/C12", compact=True)
    room_label(scene, entry[0] + 1045, entry[1] + 1340, "3", "ПРИХОЖАЯ", "S фрагм.=3,50 м2", "B01 фрагм.2090x1675", "B01/C09/U01", compact=True)

    # C03 locates two kitchen outlets only inside room 1.  Their local wall and
    # chain do not close to two B01 axes, so the symbol is a zone, not a point.
    scene.rect("A-UNKNOWN", kitchen[0] + 520, kitchen[1] + 350, kitchen[0] + 900, kitchen[1] + 560)
    scene.circle("A-EQUIPMENT", kitchen[0] + 620, kitchen[1] + 455, 35)
    scene.circle("A-EQUIPMENT", kitchen[0] + 800, kitchen[1] + 455, 35)
    scene.text("A-EQUIPMENT", kitchen[0] + 980, kitchen[1] + 405, 64, "E-01: D15/D50 [C03]; локальная стена/оси н/д")

    # Point ceiling measurements.  Repeated values are still shown as points to
    # preserve the user's measurement semantics.
    for px, py in ((bedroom[0] + 330, y0 + 330), (bedroom[2] - 330, y0 + 330), (bedroom[0] + 330, bedroom[3] - 330), (bedroom[2] - 330, bedroom[3] - 330), ((bedroom[0] + bedroom[2]) / 2, y0 + 1180)):
        ceiling_point(scene, px, py, "2750")
    for px, py, value in (
        (child[0] + 330, y0 + 330, "2716"),
        (child[2] - 330, y0 + 330, "2712"),
        (child[0] + 330, child[3] - 330, "2716"),
        (child[2] - 330, child[3] - 330, "2712"),
        ((child[0] + child[2]) / 2, y0 + 1180, "2715"),
    ):
        ceiling_point(scene, px, py, value)
    for px, py, value in (
        (wardrobe[0] + 170, y0 + 170, "2716"),
        (wardrobe[2] - 170, y0 + 170, "2715"),
        (wardrobe[0] + 170, service_top - 170, "2716"),
        (wardrobe[2] - 170, service_top - 170, "2712"),
        ((wardrobe[0] + wardrobe[2]) / 2, y0 + 560, "2718"),
    ):
        ceiling_point(scene, px, py, value)
    ceiling_point(scene, (toilet[0] + toilet[2]) / 2, y0 + 470, "2617")
    scene.text("A-CEILING", (toilet[0] + toilet[2]) / 2, y0 + 310, 62, "H [T01]", anchor="middle")
    scene.rect("A-UNKNOWN", bath[0] + 230, y0 + 170, bath[2] - 230, y0 + 610)
    scene.text("A-UNKNOWN", (bath[0] + bath[2]) / 2, y0 + 430, 65, "B-06/V-06: внутри 6; оси/H н/д", anchor="middle")
    scene.text("A-UNKNOWN", (bath[0] + bath[2]) / 2, y0 + 750, 72, "H н/д", anchor="middle")
    scene.text("A-UNKNOWN", (bath[0] + bath[2]) / 2, y0 + 930, 62, "P-06: торец/выступ ~160 [F14]; оси н/д", anchor="middle")
    for px, py, value in (
        (kitchen[0] + 380, kitchen[1] + 380, "2714"),
        (kitchen[2] - 380, kitchen[1] + 380, "2717"),
        (kitchen[0] + 380, kitchen[3] - 380, "2727"),
        (kitchen[2] - 380, kitchen[3] - 380, "2712"),
        ((kitchen[0] + kitchen[2]) / 2, kitchen[1] + 1350, "2719"),
    ):
        ceiling_point(scene, px, py, value)
    scene.text("A-CEILING", kitchen[0] + 560, kitchen[1] + 760, 68, "локально H=2530 у E-01 [C03]")
    scene.text("A-CEILING", entry[0] + 1045, entry[1] + 430, 70, "H1-H5=2750 [C09]", anchor="middle")

    # Primary B01 dimension chains below the lower block.
    inner_rooms = (bedroom, wardrobe, toilet, bath, child)
    for room, label in zip(inner_rooms, ("3840", "1740", "2090", "1730", "3850")):
        dim_h(scene, room[0], room[2], y0, y0 - 380, label)
    for x1, x2, label in (
        (bedroom[2], wardrobe[0], "t=130"),
        (wardrobe[2], toilet[0], "t=160"),
        (toilet[2], bath[0], "t=160"),
        (bath[2], child[0], "t=130"),
    ):
        dim_h(scene, x1, x2, y0, y0 - 760, label, height=72)
    dim_h(scene, bedroom[0], child[2], y0, y0 - 1150, "13830 = полная цепь B01", height=95)

    # Window vertical chains and room depths.
    dim_v(scene, y0, bedroom[3], bedroom[0], bedroom[0] - 1080, "2810")
    dim_v(scene, y0, y0 + 610, bedroom[0], bedroom[0] - 650, "610", height=70)
    dim_v(scene, y0 + 610, y0 + 2210, bedroom[0], bedroom[0] - 650, "1600", height=70)
    dim_v(scene, y0 + 2210, bedroom[3], bedroom[0], bedroom[0] - 650, "600", height=70)
    dim_v(scene, y0, child[3], child[2], child[2] + 1080, "2810")
    dim_v(scene, y0, y0 + 610, child[2], child[2] + 650, "610", height=70)
    dim_v(scene, y0 + 610, y0 + 2210, child[2], child[2] + 650, "1600", height=70)
    dim_v(scene, y0 + 2210, child[3], child[2], child[2] + 650, "600", height=70)
    dim_v(scene, y0, service_top, wardrobe[0], wardrobe[0] - 260, "1740", height=72)

    # Upper segment chains of rooms 8/7/6.
    upper_dim_y = service_top + 420
    for start, segments, labels in (
        (wardrobe[0], (400, 710, 630), ("400", "710", "630")),
        (toilet[0], (760, 810, 520), ("760", "810", "520")),
        (bath[0], (140, 810, 780), ("140", "810", "780")),
    ):
        cursor = start
        for length, label in zip(segments, labels):
            dim_h(scene, cursor, cursor + length, service_top + 30, upper_dim_y, label, height=66)
            cursor += length

    # Kitchen and attached-zone dimensions.
    dim_h(scene, kitchen[0], kitchen[2], kitchen[3], kitchen[3] + 430, "5710 [B01]")
    # The facade chain belongs to kitchen 1, not the terrace.  Keep its
    # dimension lines on the kitchen side of the facade so they cannot cross
    # the separate 2000x3000 terrace dimensions.
    dim_v(scene, kitchen[1], kitchen[3], kitchen[2], kitchen[2] - 780, "3500 [B01]")
    dim_v(scene, kitchen[1], kitchen[1] + 600, kitchen[2], kitchen[2] - 280, "600", height=68)
    dim_v(scene, kitchen[1] + 600, kitchen[1] + 2200, kitchen[2], kitchen[2] - 280, "1600 O1", height=68)
    dim_v(scene, kitchen[1] + 2200, kitchen[3], kitchen[2], kitchen[2] - 280, "1300", height=68)
    dim_v(scene, kitchen[1], kitchen[1] + 200, kitchen[0], kitchen[0] + 320, "200", height=62)
    dim_v(scene, kitchen[1] + 200, kitchen[1] + 1110, kitchen[0], kitchen[0] + 320, "910 B01 / 915 U01", height=62)
    dim_v(scene, kitchen[1] + 1110, kitchen[3], kitchen[0], kitchen[0] + 320, "2390", height=62)
    dim_h(scene, terrace[0], terrace[2], terrace[1], terrace[1] - 550, "2000 [B01]", height=74)
    dim_v(scene, terrace[1], terrace[3], terrace[2], terrace[2] + 360, "3000 [B01]", height=74)
    dim_h(scene, entry[0], entry[0] + 610, entry[3], entry[3] + 430, "610", height=100)
    dim_h(scene, entry[0] + 610, entry[0] + 1620, entry[3], entry[3] + 430, "1010", height=100)
    dim_h(scene, entry[0] + 1620, entry[2], entry[3], entry[3] + 430, "470", height=100)
    dim_h(scene, entry[0], entry[2], entry[3], entry[3] + 760, "2090 [B01]: 610 + D1 1010 + 470", height=100)
    dim_v(scene, entry[1], entry[3], entry[0], entry[0] - 310, "1675 [B01]", height=72)

    # Control overlays that must remain distinct from the B01 contour.
    dim_h(scene, bedroom[0], bedroom[0] + 3870, y0 + 120, y0 + 330, "3870 [C02]", layer="A-DIM-CONTROL", height=72)
    scene.text("A-DIM-CONTROL", bedroom[0] + 1920, y0 + 520, 65, "поперечные 2830/2870 [C02]", anchor="middle")
    scene.text("A-DIM-CONTROL", wardrobe[0] + 870, y0 + 90, 58, "1739/1745 x 1732/1730 [C07]", anchor="middle")
    scene.text("A-DIM-CONTROL", bath[0] + 865, y0 + 90, 58, "1745x1740; стар.1740x1730 [V01]", anchor="middle")
    scene.text("A-DIM-CONTROL", child[0] + 1925, y0 + 520, 65, "сторона 3825/3837; 2-я ось н/д [C10]", anchor="middle")
    dim_h(scene, kitchen[0], kitchen[0] + 5705, kitchen[3], kitchen[3] + 780, "5705 [C12]", layer="A-DIM-CONTROL", height=72)
    scene.text("A-DIM-CONTROL", kitchen[0] + 2855, kitchen[1] + 1040, 68, "~3550 [C03]; доп.2749 [C12]; не усреднять", anchor="middle")


def draw_right_insets(scene: Scene) -> None:
    """Local measured fragments that must not acquire fake global axes."""
    x1, x2 = 19850.0, 29000.0
    scene.rect("A-INSET", x1, 5000, x2, 19000)
    scene.text("A-TEXT", (x1 + x2) / 2, 18700, 150, "ЛОКАЛЬНЫЕ УЗЛЫ / НЕЗАМКНУТЫЕ ДАННЫЕ", anchor="middle", bold=True)
    scene.text("A-UNKNOWN", (x1 + x2) / 2, 18470, 76, "не использовать как глобальные координаты без указанной привязки", anchor="middle")

    # Corridor fragments C06.
    scene.rect("A-INSET", 20200, 15350, 28650, 18150)
    scene.text("A-TEXT", 20450, 17850, 105, "4 КОРИДОР — локальные фрагменты [C06]", bold=True)
    a = (20600, 15850, 21570, 17730)
    b = (22350, 15900, 23310, 17680)
    scene.rect("A-TOPOLOGY", *a)
    scene.rect("A-TOPOLOGY", *b)
    dim_h(scene, a[0], a[2], a[1], a[1] - 220, "970", height=68)
    dim_v(scene, a[1], a[3], a[2], a[2] + 220, "1880", height=68)
    dim_h(scene, b[0], b[2], b[1], b[1] - 220, "960", height=68)
    dim_v(scene, b[1], b[3], b[2], b[2] + 220, "1780", height=68)
    scene.multiline(
        "A-SOURCE",
        23900,
        17480,
        72,
        [
            "H отмеченных точек = 2750",
            "проход до балки = 630",
            "P6=940: H ниже, отметка н/д",
            "полный контур коридора н/д",
        ],
        leading=155,
    )

    # Toilet local data.  A B01 room rectangle is shown, but T01 axes remain a
    # textual local schedule because their global orientation is not closed.
    scene.rect("A-INSET", 20200, 10500, 28650, 15050)
    scene.text("A-TEXT", 20450, 14750, 105, "7 ТУАЛЕТ — локальный узел [B01/T01]", bold=True)
    tx1, ty1 = 20600, 11750
    tx2, ty2 = tx1 + 2090, ty1 + 1740
    scene.rect("A-WALL-OUTLINE", tx1, ty1, tx2, ty2)
    scene.text("A-SOURCE", (tx1 + tx2) / 2, ty2 + 150, 68, "контур B01 2090x1740; ориентация T01 к плану н/д", anchor="middle")
    scene.circle("A-EQUIPMENT", tx1 + 1045, ty1 + 700, 170)
    scene.line("A-EQUIPMENT", tx1 + 1045, ty1 + 400, tx1 + 1045, ty1 + 1000)
    scene.line("A-EQUIPMENT", tx1 + 745, ty1 + 700, tx1 + 1345, ty1 + 700)
    scene.text("A-EQUIPMENT", tx1 + 1045, ty1 + 655, 70, "WC ось", anchor="middle")
    scene.text("A-UNKNOWN", tx1 + 1045, ty1 + 180, 64, "схема осей условна", anchor="middle")
    local_meter_box = (tx2 - 710, ty1, tx2, ty1 + 360)
    scene.rect("A-WALL-OUTLINE", *local_meter_box)
    scene.text("A-UNKNOWN", (local_meter_box[0] + local_meter_box[2]) / 2, ty1 + 115, 64, "ВМ-07", anchor="middle")
    dim_h(scene, local_meter_box[0], local_meter_box[2], local_meter_box[3], local_meter_box[3] + 180, "710 [B01]", height=66)
    dim_v(scene, local_meter_box[1], local_meter_box[3], local_meter_box[0], local_meter_box[0] - 160, "360 [B01]", height=66)
    scene.text("A-UNKNOWN", tx1 + 1045, ty1 + 1020, 66, "ВМ-07: короб 360x710 [B01]", anchor="middle")
    scene.text("A-UNKNOWN", tx1 + 1045, ty1 + 870, 66, "счётчики внутри; оси н/д [U02]", anchor="middle")
    scene.multiline(
        "A-SOURCE",
        23300,
        14230,
        72,
        [
            "H потолка 2617",
            "D4: предвар.705x2027",
            "открывание наружу; петли н/д",
            "WC: 550 от задней; 1621 от правой",
            "проход от оси 824 до передней",
            "вода: 620 от левой; h=200",
            "ВМ-07: короб 360x710 [B01]; оси внутри н/д [U02]",
            "канализация WC: 460-470; h=80",
            "раковина: канализация h=240",
            "кабель: h=1850; 1030/250",
            "вентрешётка 260x260; 40/80",
            "Л-07 щиток/лючок S05: 456; t28; 933/1142/658",
        ],
        leading=150,
    )

    # Terrace control conflict inset.
    scene.rect("A-INSET", 20200, 7800, 28650, 10250)
    scene.text("A-TEXT", 20450, 9950, 105, "9 ТЕРРАСА — конфликт контуров", bold=True)
    cx, cy = 20700, 8100
    scene.rect("A-CONFLICT", cx, cy, cx + 3310, cy + 2110)
    dim_h(scene, cx, cx + 3310, cy, cy - 220, "3310 [C01]", layer="A-DIM-CONTROL", height=68)
    dim_v(scene, cy, cy + 2110, cx, cx - 220, "2110/2130 [C01]", layer="A-DIM-CONTROL", height=68)
    scene.multiline(
        "A-SOURCE",
        24500,
        9520,
        72,
        ["B01: 2000x3000", "C01: 3310x2110/2130", "остекление 1655", "проём 1298 [C12]", "не совмещать без замера"],
        leading=160,
    )

    # Unknown register, kept visible on the drawing rather than hidden in docs.
    scene.rect("A-INSET", 20200, 5250, 28650, 7550)
    scene.text("A-TEXT", 20450, 7250, 105, "НЕОПРЕДЕЛЁННОСТИ / НЕПРИВЯЗАННЫЕ ЭЛЕМЕНТЫ", bold=True)
    scene.line("A-INSET", 24350, 5450, 24350, 7050)
    scene.multiline(
        "A-UNKNOWN",
        20450,
        6950,
        66,
        [
            "1. наружная t стен",
            "2. полный верхний контур/площадь коридора",
            "3. привязки D1/D2 к углам",
            "4. D3/D5 W/H н/д; D4 перепроверить 705x2027",
            "5. H пониженного потолка P6",
            "6. H подоконников и габариты радиаторов",
            "7. H ванной и глобальные оси инженерии",
            "8. ЭЩ-03: габарит/H/ось на стене н/д",
            "9. ВМ-07: оси, H и габарит люка н/д",
            "10. Л-07: тип и связь с ВМ-07 н/д",
        ],
        leading=190,
    )

    # Elements confirmed by photos/notes but lacking a trustworthy global axis.
    # They are scheduled here instead of being falsely inserted into a room.
    sx, sy = 24700.0, 6880.0
    scene.circle("A-EQUIPMENT", sx, sy, 55)
    scene.circle("A-EQUIPMENT", sx + 125, sy, 55)
    scene.line("A-EQUIPMENT", sx - 45, sy - 80, sx + 175, sy + 80)
    scene.text("A-SOURCE", sx + 310, sy - 25, 64, "E-01 кухня: D15/D50; оси/H н/д [C03]")
    scene.rect("A-CONFLICT", sx - 10, sy - 520, sx + 210, sy - 210)
    scene.line("A-CONFLICT", sx - 10, sy - 520, sx + 210, sy - 210)
    scene.line("A-CONFLICT", sx + 210, sy - 520, sx - 10, sy - 210)
    scene.text("A-SOURCE", sx + 310, sy - 410, 64, "ЭЩ-03 прихожая: габарит/H/ось н/д [F08]")
    scene.rect("A-EQUIPMENT", sx - 10, sy - 920, sx + 210, sy - 720)
    for yy in (sy - 870, sy - 820, sy - 770):
        scene.line("A-EQUIPMENT", sx + 10, yy, sx + 190, yy)
    scene.text("A-SOURCE", sx + 310, sy - 850, 64, "E-03: 3 розетки у пола в прихожей [F08]; ось н/д")
    scene.rect("A-EQUIPMENT", sx - 10, sy - 1250, sx + 210, sy - 1050)
    scene.text("A-SOURCE", sx + 310, sy - 1155, 64, "R-02/R-05 под O2/O3; габарит/H н/д")
    scene.circle("A-EQUIPMENT", sx + 100, sy - 1510, 95)
    scene.line("A-EQUIPMENT", sx + 100, sy - 1650, sx + 100, sy - 1370)
    scene.text("A-SOURCE", sx + 310, sy - 1535, 64, "WC: подтверждён; точные локальные оси — узел выше")


def draw_service_strip(scene: Scene) -> None:
    """Legend, room schedule and project title block."""
    bottom, top = 500.0, 4450.0
    scene.rect("A-SHEET", 500, bottom, 29200, top)

    # Legend and source rules.
    lx1, lx2 = 500.0, 7200.0
    scene.line("A-SHEET", lx2, bottom, lx2, top)
    scene.text("A-TEXT", 700, 4160, 120, "УСЛОВНЫЕ ОБОЗНАЧЕНИЯ И ПРАВИЛА", bold=True)
    legend = [
        ("A-WALL-OUTLINE", "внутренние стены B01 с t=30/130/160/200"),
        ("A-EXTERIOR-GRAPHIC", "наружные/неразмерённые стены; t числом н/д"),
        ("A-DIM-BTI", "размеры/цепочки B01"),
        ("A-DIM-CONTROL", "контрольные обмеры Cxx/U01"),
        ("A-OPENING", "проёмы и окна"),
        ("A-EQUIPMENT", "существующее оборудование/зона"),
        ("A-CEILING", "точечные отметки потолка"),
        ("A-CONFLICT", "конфликт источников"),
        ("A-UNKNOWN", "неизвестно / нужна привязка"),
    ]
    yy = 3860
    for layer, label in legend:
        scene.line(layer, 760, yy + 28, 1270, yy + 28)
        scene.text("A-TEXT", 1400, yy, 78, label)
        yy -= 245
    scene.multiline(
        "A-SOURCE",
        700,
        1520,
        72,
        [
            "Приоритет: контроль для заказа; B01 для топологии.",
            "Не усреднять разные стороны и источники.",
            "Sрасч. — геометрический расчёт, не официальная площадь.",
            "* Дуги D1-D5 не показаны; D4 наружу, петли н/д; сегмент B01 не равен чистой W.",
            "R01 (чужой пример) — только графический стиль.",
            "Полная матрица: docs/11_Паспорт_подробного_обмерного_плана.md",
        ],
        leading=175,
    )

    # Room schedule.
    sx1, sx2 = 7200.0, 19600.0
    scene.line("A-SHEET", sx2, bottom, sx2, top)
    scene.text("A-TEXT", (sx1 + sx2) / 2, 4200, 120, "ЭКСПЛИКАЦИЯ ПОМЕЩЕНИЙ / ПОСЛЕ ОБМЕРОВ", anchor="middle", bold=True)
    table_top = 3940.0
    row_h = 330.0
    columns = [sx1, sx1 + 550, sx1 + 3150, sx1 + 5450, sx1 + 6900, sx1 + 8950, sx2]
    for x in columns:
        scene.line("A-SHEET", x, bottom, x, table_top)
    for index in range(11):
        y = table_top - index * row_h
        scene.line("A-SHEET", sx1, y, sx2, y)
    headers = ("№", "Помещение", "B01, мм", "Sрасч.", "H, мм", "Статус")
    for left, right, text in zip(columns[:-1], columns[1:], headers):
        scene.text("A-TEXT", (left + right) / 2, table_top - 245, 82, text, anchor="middle", bold=True)
    rows = [
        ("1", "Кухня-гостиная", "5710x3500", "19,99", "2714/2717/2727/2712; ц.2719", "B01 + контроль"),
        ("2", "Детская", "3850x2810", "10,82", "2712/2716; ц.2715", "B01; 1 ось контроля"),
        ("3", "Прихожая", "фрагм.2090x1675", "3,50*", "2750 (5 точек)", "не полная площадь"),
        ("4", "Коридор", "контур н/д", "н/д", "2750; P6 ниже н/д", "топология + вставки"),
        ("5", "Спальня", "3840x2810", "10,79", "2750 (5 точек)", "B01 + контроль"),
        ("6", "Ванная", "1730x1740", "3,01", "н/д", "конфликт контроля"),
        ("7", "Туалет", "2090x1740", "3,64", "2617 [T01]", "инженерия локально"),
        ("8", "Гардеробная", "1740x1740", "3,03", "2712-2718", "4 контрольные стороны"),
        ("9", "Терраса", "2000x3000", "6,00 B01", "не применяется", "сильный конфликт"),
    ]
    for row_index, row in enumerate(rows, start=1):
        cy = table_top - row_index * row_h - 240
        for left, right, value in zip(columns[:-1], columns[1:], row):
            scene.text("A-TEXT", (left + right) / 2, cy, 73, value, anchor="middle")

    # Neutral APT-001 title block, intentionally not derived from the sample.
    tx1, tx2 = 19600.0, 29200.0
    scene.text("A-TEXT", (tx1 + tx2) / 2, 4130, 155, "APT-001", anchor="middle", bold=True)
    scene.line("A-SHEET", tx1, 3900, tx2, 3900)
    scene.text("A-TEXT", (tx1 + tx2) / 2, 3500, 180, "ПОДРОБНЫЙ ОБМЕРНЫЙ ПЛАН", anchor="middle", bold=True)
    scene.text("A-SOURCE", (tx1 + tx2) / 2, 3200, 82, "БТИ S15 + контрольные обмеры + фото", anchor="middle")
    scene.line("A-SHEET", tx1, 2920, tx2, 2920)
    scene.text("A-TEXT", 19900, 2630, 82, "Лист")
    scene.text("A-TEXT", 21600, 2630, 110, "04", bold=True)
    scene.text("A-TEXT", 23200, 2630, 82, "Масштаб")
    scene.text("A-TEXT", 26500, 2630, 110, "1:50", bold=True)
    scene.line("A-SHEET", tx1, 2400, tx2, 2400)
    scene.text("A-TEXT", 19900, 2110, 82, "Формат")
    scene.text("A-TEXT", 21600, 2110, 95, "A2, альбом")
    scene.text("A-TEXT", 25000, 2110, 82, "Ед.")
    scene.text("A-TEXT", 26500, 2110, 95, "мм")
    scene.line("A-SHEET", tx1, 1880, tx2, 1880)
    scene.text("A-TEXT", 19900, 1580, 82, "Дата")
    scene.text("A-TEXT", 21600, 1580, 95, "11.08.2026")
    scene.text("A-TEXT", 25000, 1580, 82, "Рев.")
    scene.text("A-TEXT", 26500, 1580, 95, "13")
    scene.line("A-SHEET", tx1, 1340, tx2, 1340)
    scene.text("A-SOURCE", (tx1 + tx2) / 2, 1030, 75, "Красные/оранжевые позиции не применять без проверки", anchor="middle")
    scene.text("A-SOURCE", (tx1 + tx2) / 2, 760, 75, "Исходные фото не изменялись; публикация не выполнялась", anchor="middle")


def draw_scale_bar(scene: Scene) -> None:
    x, y = 26700.0, 4750.0
    scene.line("A-DIM-BTI", x, y, x + 1000, y)
    for tick in (x, x + 500, x + 1000):
        scene.line("A-DIM-BTI", tick, y - 80, tick, y + 80)
    scene.text("A-DIM-BTI", x, y - 230, 70, "0", anchor="middle")
    scene.text("A-DIM-BTI", x + 500, y - 230, 70, "500", anchor="middle")
    scene.text("A-DIM-BTI", x + 1000, y - 230, 70, "1000 мм", anchor="middle")
    scene.text("A-TEXT", x + 500, y + 180, 74, "М 1:50: 1000 мм = 20 мм", anchor="middle")


def validate_scene(scene: Scene) -> None:
    """Cheap deterministic gates before any artifact is written."""
    assert PAGE_W == 29700 and PAGE_H == 21000
    assert 3840 + 130 + 1740 + 160 + 2090 + 160 + 1730 + 130 + 3850 == 13830
    assert 610 + 1600 + 600 == 2810
    assert 1300 + 1600 + 600 == 3500
    assert 610 + 1010 + 470 == 2090
    assert 400 + 710 + 630 == 1740
    assert 760 + 810 + 520 == 2090
    assert 140 + 810 + 780 == 1730

    texts = "\n".join(item.data["value"] for item in scene.items if item.kind == "text")
    required = (
        "КУХНЯ-ГОСТИНАЯ",
        "ДЕТСКАЯ",
        "ПРИХОЖАЯ",
        "КОРИДОР",
        "СПАЛЬНЯ",
        "ВАННАЯ",
        "ТУАЛЕТ",
        "ГАРДЕРОБНАЯ",
        "ТЕРРАСА",
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "P6",
        "O1",
        "O2",
        "O3",
        "D4: предвар.705x2027",
        "открывание наружу; петли н/д",
        "t=30",
        "t=130",
        "t=160",
        "13830",
        "наружные/неразмерённые стены: t н/д",
        "ЭЩ-03",
        "E-03",
        "Л-07",
        "P-06",
        "СТ-01: t=200 [B01]",
        "до D2 = 200 [B01]",
        "2090 [B01]: 610 + D1 1010 + 470",
    )
    missing = [value for value in required if value not in texts]
    assert not missing, f"missing required plan labels: {missing}"

    # Text-only guard: raw DXF/SVG coordinates can coincidentally contain the
    # same digits as another drawing, so content contamination is checked only
    # in annotations and extracted PDF text.
    forbidden = (
        "IVANCHUKINTERIOR",
        "IVANCHUK А.Ю.",
        "10.02.2026",
        "55.95",
        "89.70",
        "2575ММ",
        "Жилая с кухонным оборудованием",
        "Радиатор 600x80xH500",
        "Радиатор 800x80xH500",
        "Радиатор 600x150xH500",
    )
    contaminated = [value for value in forbidden if value.casefold() in texts.casefold()]
    assert not contaminated, f"foreign-reference content leaked into plan: {contaminated}"

    for item in scene.items:
        d = item.data
        if item.kind == "line":
            coords = (d["x1"], d["x2"], d["y1"], d["y2"])
        elif item.kind == "rect":
            coords = (d["x1"], d["x2"], d["y1"], d["y2"])
        elif item.kind in {"circle", "text"}:
            coords = (d["x"], d["x"], d["y"], d["y"])
        elif item.kind == "polyline" and d["points"]:
            xs, ys = zip(*d["points"])
            coords = (min(xs), max(xs), min(ys), max(ys))
        else:
            continue
        assert -50 <= min(coords[0], coords[1]) <= PAGE_W + 50
        assert -50 <= max(coords[0], coords[1]) <= PAGE_W + 50
        assert -50 <= min(coords[2], coords[3]) <= PAGE_H + 50
        assert -50 <= max(coords[2], coords[3]) <= PAGE_H + 50


def draw_sheet(scene: Scene) -> None:
    scene.rect("A-SHEET", 0, 0, PAGE_W, PAGE_H)
    scene.rect("A-SHEET", 350, 350, PAGE_W - 350, PAGE_H - 350)
    scene.text("A-TEXT", 700, PAGE_H - 930, 280, "APT-001 | ПОДРОБНЫЙ ПЛАН КОНТРОЛЬНЫХ ОБМЕРОВ", bold=True)
    scene.text("A-SOURCE", 700, PAGE_H - 1250, 115, "B01 БТИ + C01-C07/C09/C10/C12 + U01 + T01/V01; модель 1:1 мм; лист A2; печать М 1:50")
    scene.text("A-CONFLICT", PAGE_W - 3200, PAGE_H - 980, 95, "Чужой референс: только оформление, данные запрещены", anchor="middle", bold=True)
    scene.line("A-SHEET", 700, PAGE_H - 1450, PAGE_W - 700, PAGE_H - 1450)


def build_scene() -> Scene:
    scene = Scene()
    draw_sheet(scene)

    # The detailed geometry and service strip are added below in a separate
    # function block to keep the exporters independent from apartment data.
    draw_apartment(scene)
    draw_right_insets(scene)
    draw_service_strip(scene)
    draw_scale_bar(scene)
    validate_scene(scene)
    return scene


def build() -> tuple[Path, Path, Path]:
    PLANS.mkdir(parents=True, exist_ok=True)
    scene = build_scene()
    DXFWriter().export(scene, DXF_OUT)
    export_svg(scene, SVG_OUT)
    export_pdf(scene, PDF_OUT)
    return DXF_OUT, SVG_OUT, PDF_OUT


if __name__ == "__main__":
    for output in build():
        print(output)
