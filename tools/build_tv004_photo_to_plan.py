# -*- coding: utf-8 -*-
"""TV-004: scale-plan reconstruction of the approved TV-001 visualisation.

The user-supplied perspective image is treated as a composition reference.
The 2D geometry comes only from TV-001/B01 coordinates and its stated
dimensions; a render cannot prove a physical clearance by itself.
"""
from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base
import build_tv001_sofa_top_tv_bottom as tv001


ROOT = Path(__file__).resolve().parents[1]
SOURCE_IMAGE = ROOT / "кухня гостинная" / "кухня_визуализация_TV-001_v25_реальные_размеры_выноски.png"
TMP_PDF = ROOT / "tmp" / "pdfs" / "TV-004_схема_по-визуализации_TV-001_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "TV-004_схема_по-визуализации_TV-001_М1-25.pdf"

INK = base.INK
MUTED = base.MUTED
GOOD = base.GOOD
ORANGE = "#ad6800"
BLUE = "#2f6e8d"
PALE_BLUE = "#eef7fb"
PALE_GREEN = "#eff8f1"
PALE_ORANGE = "#fff6e8"
PALE_RED = "#fff1ef"


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    base.text(c, font, x, y, size, value, color, center=center, right=right)


def wrapped(c, font, x, y, size, value, width, color=INK, leading=None, bullet=None):
    leading = leading or size * 1.28
    for index, row in enumerate(base.wrap(value, width)):
        prefix = (bullet + " ") if bullet and index == 0 else ("  " if bullet else "")
        text(c, font, x, y, size, prefix + row, color)
        y -= leading
    return y


def panel(c, bold, x, y, w, h, title, fill):
    base.box(c, x, y, w, h, fill, "#bdc7ce", 0.20, 2)
    text(c, bold, x + 4, y + h - 7, 4.25, title)


def page_frame(c, regular, bold):
    width, height = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, width, height, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, width - 16 * mm, height - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 13.2, "TV-004 - СХЕМА ПО ВИЗУАЛИЗАЦИИ TV-001")
    text(c, regular, 14, 274, 4.9,
         "Фото задаёт композицию; точные координаты и масштаб - B01 / TV-001. Мебель - габариты до конкретных SKU.", MUTED)
    text(c, regular, 404, 14, 3.8, "TV-004 | лист 1/1 | М 1:25", MUTED, right=True)


def validate() -> None:
    if not SOURCE_IMAGE.exists():
        raise FileNotFoundError(f"Missing source visual: {SOURCE_IMAGE}")
    table = tv001.MEAL_FIXED["meal_table"]
    sofa = tv001.MEAL_FIXED["sofa_closed"]
    kitchen = tv001.MEAL_FIXED["kitchen_top"]
    assert tv001.ROOM == (0, 0, 5710, 3500)
    assert table[2] - table[0] == 1400
    assert table[3] - table[1] == 800
    assert table[0] - kitchen[2] == 70
    assert sofa[1] == table[3]
    assert tv001.ROUTES[0][3] - tv001.ROUTES[0][1] == 900
    assert tv001.DAY_FIXED["desk"][2] - tv001.DAY_FIXED["desk"][0] == 1200
    assert tv001.DAY_FIXED["desk"][3] - tv001.DAY_FIXED["desk"][1] == 600
    assert tv001.DAY_FIXED["tv_media"][2] - tv001.DAY_FIXED["tv_media"][0] == 1600
    assert tv001.DAY_FIXED["tv_media"][3] - tv001.DAY_FIXED["tv_media"][1] == 300
    tv001.validate_geometry()
    print("PASS TV-004: photo labels reconciled with TV-001 / B01 model geometry")


def draw_photo(c, regular, bold):
    panel(c, bold, 255, 172, 151, 94, "ИСТОЧНИК КОМПОЗИЦИИ", PALE_BLUE)
    image = ImageReader(str(SOURCE_IMAGE))
    source_w, source_h = image.getSize()
    target_w, target_h = 143, 83
    scale = min(target_w / source_w, target_h / source_h)
    draw_w, draw_h = source_w * scale, source_h * scale
    x = 259 + (target_w - draw_w) / 2
    y = 177 + (target_h - draw_h) / 2
    c.drawImage(image, x * mm, y * mm, draw_w * mm, draw_h * mm, preserveAspectRatio=True, mask="auto")
    text(c, regular, 259, 174.0, 3.45, "Пользовательская визуализация TV-001; перспектива не заменяет обмеры.", MUTED)


def draw_readout(c, regular, bold):
    panel(c, bold, 255, 115, 151, 49, "ЧТО ПЕРЕНЕСЕНО В ПЛАН", PALE_GREEN)
    rows = (
        ("B01", "5710 x 3500", INK),
        ("кухня", "4000 фронтов; верх 2400 x 600", "#5b4827"),
        ("диван", "2000 x 1000; сон 2000 x 1400", "#544943"),
        ("стол CJ196", "1400 x 800; H 750 по визуализации", "#405d3c"),
        ("РМ / ТВ", "1200 x 600 / 1600 x 300", BLUE),
    )
    yy = 151
    for label, value, color in rows:
        text(c, bold, 259, yy, 3.75, label, color)
        text(c, regular, 288, yy, 3.75, value, color)
        yy -= 6.1


def draw_limits(c, regular, bold):
    panel(c, bold, 255, 68, 151, 39, "ВАЖНО О ПРОХОДЕ 900", PALE_ORANGE)
    yy = 97
    for para in (
        "На фото маршрут выглядит свободным. На плане он действительно 900 мм только пока два стула задвинуты или убраны.",
        "При посадке стулья входят в оранжевую полосу. Это режим ужина, не постоянный свободный коридор.",
    ):
        yy = wrapped(c, regular, 259, yy, 3.55, para, 55, ORANGE, 4.5, "-") - 1.0
    text(c, regular, 259, 72, 3.3, "70 мм у торца кухни - технический зазор, не проход; H 750 - проверить по SKU.", "#8a5610")


def draw_key_dimensions(c, regular, bold):
    # Reader-friendly dimensions that directly correspond to the labels placed
    # on the visualisation.  The full model dimensions are still plotted on
    # the 1:25 plan using TV-001 routines below.
    panel(c, bold, 255, 28, 151, 31, "КЛЮЧ К СХЕМЕ", PALE_RED)
    text(c, regular, 259, 47, 3.45, "Оранжевый - маршрут/техзазор; синий - РМ; зелёный - стол.", INK)
    text(c, regular, 259, 41.5, 3.45, "Красный пунктир - ход стула при посадке; это не свободное место.", INK)
    text(c, regular, 259, 35.5, 3.45, "Показан дневной кадр визуализации, без раскрытой кровати.", INK)


def draw_plan(c, regular, bold):
    base.draw_room_shell(c, regular, bold, "TV-004 / ФОТО -> ПЛАН")
    tv001.draw_d2_guard(c, regular)
    tv001.draw_routes(c, regular)
    tv001.draw_kitchen(c, regular, bold)
    tv001.draw_sofa_day(c, regular, bold)
    tv001.draw_desk(c, regular)
    tv001.draw_tv(c, regular, bold)
    tv001.draw_meal_table(c, regular, bold)
    tv001.dimensions(c, regular, "meal")

    # Clear caption for the exact photo-to-plan correspondence.
    base.label_model(c, bold, 3170, 2285, "РАСПОЛОЖЕНИЕ КАК НА ВИЗУАЛИЗАЦИИ", 3.0, GOOD)
    base.label_model(c, regular, 3170, 2160, "стол упирается в диван; между столом и торцом кухни 70", 2.25, GOOD)


def build() -> None:
    validate()
    TMP_PDF.parent.mkdir(parents=True, exist_ok=True)
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(TMP_PDF), pagesize=landscape(A3))
    c.setTitle("TV-004 - схема по визуализации TV-001")
    c.setAuthor("Codex")
    page_frame(c, regular, bold)
    draw_plan(c, regular, bold)
    draw_photo(c, regular, bold)
    draw_readout(c, regular, bold)
    draw_limits(c, regular, bold)
    draw_key_dimensions(c, regular, bold)
    c.showPage()
    c.save()
    TMP_PDF.replace(OUT_PDF)
    print(f"PASS TV-004 PDF: {OUT_PDF}")


if __name__ == "__main__":
    build()
