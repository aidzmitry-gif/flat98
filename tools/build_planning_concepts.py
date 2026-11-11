# -*- coding: utf-8 -*-
"""Build PLN-001 functional planning concepts on the B01 room skeleton.

This is a furniture/zoning study only.  It does not alter wet zones, walls,
openings or any unresolved construction dimension from APT-001.
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "plans" / "05_Планировочные_концепции_A3_черновик.pdf"


def fonts() -> tuple[str, str]:
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if regular.exists() and "PLNArial" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("PLNArial", str(regular)))
    if bold.exists() and "PLNArial-Bold" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("PLNArial-Bold", str(bold)))
    return ("PLNArial" if regular.exists() else "Helvetica", "PLNArial-Bold" if bold.exists() else "Helvetica-Bold")


def draw_text(pdf: canvas.Canvas, font: str, x: float, y: float, size: float, text: str, *, color: str = "#222222", center: bool = False) -> None:
    pdf.setFont(font, size)
    pdf.setFillColor(HexColor(color))
    if center:
        pdf.drawCentredString(x * mm, y * mm, text)
    else:
        pdf.drawString(x * mm, y * mm, text)


def fill_rect(pdf: canvas.Canvas, x: float, y: float, w: float, h: float, *, fill: str, stroke: str = "#202020", line: float = 0.30) -> None:
    pdf.setFillColor(HexColor(fill))
    pdf.setStrokeColor(HexColor(stroke))
    pdf.setLineWidth(line * mm)
    pdf.rect(x * mm, y * mm, w * mm, h * mm, fill=1, stroke=1)


def line(pdf: canvas.Canvas, x1: float, y1: float, x2: float, y2: float, *, color: str = "#444444", width: float = 0.25, dashed: bool = False) -> None:
    pdf.setStrokeColor(HexColor(color))
    pdf.setLineWidth(width * mm)
    pdf.setDash(2 * mm, 1.4 * mm) if dashed else pdf.setDash()
    pdf.line(x1 * mm, y1 * mm, x2 * mm, y2 * mm)
    pdf.setDash()


def room(pdf: canvas.Canvas, normal: str, bold: str, origin_x: float, origin_y: float, scale: float, box: tuple[int, int, int, int], label: str) -> None:
    x1, y1, x2, y2 = box
    x = origin_x + x1 * scale
    y = origin_y + y1 * scale
    w = (x2 - x1) * scale
    h = (y2 - y1) * scale
    fill_rect(pdf, x, y, w, h, fill="#fbfbfb", stroke="#202020", line=0.42)
    draw_text(pdf, bold, x + w / 2, y + h / 2 + 1.5, 5.3, label, center=True)


def furniture(pdf: canvas.Canvas, normal: str, origin_x: float, origin_y: float, scale: float, box: tuple[int, int, int, int], label: str, fill: str) -> None:
    x1, y1, x2, y2 = box
    x = origin_x + x1 * scale
    y = origin_y + y1 * scale
    w = (x2 - x1) * scale
    h = (y2 - y1) * scale
    fill_rect(pdf, x, y, w, h, fill=fill, stroke="#5b6470", line=0.18)
    if w > 12 and h > 4:
        draw_text(pdf, normal, x + w / 2, y + h / 2 - 1.2, 3.5, label, center=True)


def draw_variant(pdf: canvas.Canvas, normal: str, bold: str, panel_x: float, title: str, subtitle: str, variant: str) -> None:
    panel_y = 117.0
    panel_w, panel_h = 190.0, 154.0
    fill_rect(pdf, panel_x, panel_y, panel_w, panel_h, fill="#ffffff", stroke="#303030", line=0.40)
    draw_text(pdf, bold, panel_x + 8, panel_y + panel_h - 10, 10, title, color="#26374a")
    draw_text(pdf, normal, panel_x + 8, panel_y + panel_h - 16, 5.3, subtitle, color="#5d6570")

    # B01 geometry, in mm: simplified room skeleton only.
    scale = 0.0117
    ox, oy = panel_x + 11, panel_y + 24
    bedroom = (0, 0, 3840, 2810)
    wardrobe = (3970, 0, 5710, 1740)
    toilet = (5870, 0, 7960, 1740)
    bath = (8120, 0, 9850, 1740)
    child = (9980, 0, 13830, 2810)
    entry = (5870, 3010, 7960, 4685)
    kitchen = (8120, 3010, 13830, 6510)
    rooms = ((bedroom, "5 СПАЛЬНЯ"), (wardrobe, "8 ГАРД."), (toilet, "7 WC"), (bath, "6 ВАННА"), (child, "2 ДЕТСКАЯ"), (entry, "3 ПРИХ."), (kitchen, "1 КУХНЯ-ГОСТ.") )
    for box, label in rooms:
        room(pdf, normal, bold, ox, oy, scale, box, label)

    # Corridor is deliberately a light conceptual zone, not a reconstructed wall contour.
    cx = ox + 5710 * scale
    cy = oy + 1740 * scale
    cw = (9850 - 5710) * scale
    ch = (3010 - 1740) * scale
    pdf.setFillColor(HexColor("#f5f5f5"))
    pdf.setStrokeColor(HexColor("#9a9a9a"))
    pdf.setDash(1.4 * mm, 1.2 * mm)
    pdf.rect(cx * mm, cy * mm, cw * mm, ch * mm, fill=1, stroke=1)
    pdf.setDash()
    draw_text(pdf, normal, cx + cw / 2, cy + ch / 2 - 1.2, 4.1, "4 КОРИДОР: контур н/д", center=True, color="#707070")

    # Permanent common elements.
    furniture(pdf, normal, ox, oy, scale, (4150, 150, 5530, 1580), "ХРАНЕНИЕ", "#e6edf5")
    furniture(pdf, normal, ox, oy, scale, (6050, 120, 7730, 470), "СЧЁТЧИКИ", "#f5eadc")
    furniture(pdf, normal, ox, oy, scale, (320, 250, 1920, 2250), "КРОВАТЬ 160", "#e8e2f1")
    furniture(pdf, normal, ox, oy, scale, (10270, 300, 11920, 1650), "СЕЙЧАС: КРОВАТКА", "#e8f1df")
    furniture(pdf, normal, ox, oy, scale, (12080, 350, 13550, 2450), "БУДУЩЕЕ: 2 СПАЛЬНЫХ МОДУЛЯ", "#edf5e6")
    furniture(pdf, normal, ox, oy, scale, (6200, 3240, 7420, 3850), "ПРИХОЖАЯ / ПИТОМЦЫ", "#f5eadc")
    furniture(pdf, normal, ox, oy, scale, (8320, 5770, 11120, 6370), "КУХНЯ: ОСЬ ВОДЫ УТОЧНИТЬ", "#f6e5cd")

    if variant == "A":
        # Exactly one permanent desk belongs in the kitchen-living room.  The
        # second workplace is deliberately not drawn here: its separate room and
        # furniture scheme are an explicit G1 decision, not an assumption.
        furniture(pdf, normal, ox, oy, scale, (8500, 4200, 10100, 4800), "РАБОТА 1", "#dcecf6")
        furniture(pdf, normal, ox, oy, scale, (11300, 3950, 12900, 4750), "СТОЛ", "#f5eadc")
        furniture(pdf, normal, ox, oy, scale, (11300, 3200, 13200, 3780), "ДИВАН / МЕДИА", "#ece2db")
        furniture(pdf, normal, ox, oy, scale, (13000, 3220, 13650, 3850), "КОЛОНКИ + МИКРОФОНЫ", "#f1dce6")
        draw_text(pdf, bold, panel_x + 12, panel_y + 11, 5.3, "В КУХНЕ-ГОСТИНОЙ: один стол 1200-1400×700; без тумбы-экрана.", color="#1d5f7a")
        draw_text(pdf, normal, panel_x + 12, panel_y + 5, 4.3, "Второе место — вне неё; помещение и схема утверждаются на G1.", color="#48535d")
    else:
        furniture(pdf, normal, ox, oy, scale, (2000, 1600, 3470, 2200), "РАБОТА 2: ТИХАЯ", "#dcecf6")
        furniture(pdf, normal, ox, oy, scale, (8380, 3240, 10000, 3840), "РАБОТА 1", "#dcecf6")
        furniture(pdf, normal, ox, oy, scale, (11100, 3900, 12850, 4750), "СТОЛ", "#f5eadc")
        furniture(pdf, normal, ox, oy, scale, (11100, 3200, 13200, 3780), "ДИВАН / МЕДИА", "#ece2db")
        furniture(pdf, normal, ox, oy, scale, (13000, 3220, 13650, 3850), "КОЛОНКИ + МИКРОФОНЫ", "#f1dce6")
        draw_text(pdf, bold, panel_x + 12, panel_y + 11, 5.3, "СЦЕНАРИЙ: работа 2 в спальне — утвердить на G1; меньше приватности отдыха.", color="#8a4b22")
        draw_text(pdf, normal, panel_x + 12, panel_y + 5, 4.3, "Резерв на интенсивные созвоны; не рекомендован как постоянный сценарий после второго ребёнка.", color="#48535d")


def build() -> Path:
    normal, bold = fonts()
    pdf = canvas.Canvas(str(OUT), pagesize=landscape(A3), pageCompression=1)
    pdf.setTitle("PLN-001 - planning concepts")
    page_w, page_h = landscape(A3)
    pdf.setFillColor(white)
    pdf.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    pdf.setStrokeColor(HexColor("#1f2933"))
    pdf.setLineWidth(0.35 * mm)
    pdf.rect(8 * mm, 8 * mm, page_w - 16 * mm, page_h - 16 * mm, fill=0, stroke=1)

    draw_text(pdf, bold, 12, 284, 17, "PLN-001 | КОНЦЕПЦИИ ПЛАНИРОВКИ", color="#20354b")
    draw_text(pdf, normal, 12, 276, 6.2, "На основе APT-001 B01. Только мебель и функциональное зонирование; не является монтажным проектом.", color="#4d5864")
    # Keep the family note inside the right margin; its width is larger than a panel heading.
    draw_text(pdf, bold, 351, 284, 7.2, "СЕМЬЯ: 2 взрослых, ребёнок, будущее 2-е дитя, кошка, собака", color="#7b4a20", center=True)

    draw_variant(pdf, normal, bold, 12, "ВАРИАНТ A — СЕМЕЙНЫЙ ЦЕНТР", "Рекомендуемый: одно рабочее место в кухне-гостиной", "A")
    draw_variant(pdf, normal, bold, 218, "ВАРИАНТ B — ТИШЕ ДЛЯ ОДНОГО", "Сценарий: второе место в спальне, только после G1", "B")

    fill_rect(pdf, 12, 22, 396, 80, fill="#fbfcfd", stroke="#303030", line=0.35)
    draw_text(pdf, bold, 18, 92, 8.5, "ОБЩИЕ ПРАВИЛА ДО РАБОЧЕГО ПРОЕКТА", color="#26374a")
    rules = (
        ("1", "Не переносить мокрые зоны и не заказывать мебель по незакрытым контурам/проёмам."),
        ("2", "Детская 2: модульная мебель сейчас, два спальных места в будущем; гардеробная 8 остаётся хранением."),
        ("3", "Рабочие места: 2× Cat.6, отдельный свет, питание и кабель-менеджмент; в кухне-гостиной — ровно одно."),
        ("4", "Медиа: колонки/микрофоны, закрытая тумба, мягкие поверхности против эха. Полная студия не нужна."),
        ("5", "Из Китая: низковольтный свет, датчики, шторы, зарядки и органайзеры; силовую защиту — после электропроекта."),
    )
    y = 82
    for number, rule in rules:
        draw_text(pdf, bold, 20, y, 5.5, number, color="#b35a18")
        draw_text(pdf, normal, 27, y, 5.3, rule, color="#2d3740")
        y -= 11

    draw_text(pdf, normal, 12, 14, 4.2, "Принять вариант A/B можно после проверки мебели на реальных осях воды, радиаторов, щита и проёмов.", color="#606870")
    draw_text(pdf, normal, 408, 14, 4.2, "PLN-001 | черновик 1 | 15.08.2026", color="#606870", center=True)
    pdf.showPage()
    pdf.save()
    return OUT


if __name__ == "__main__":
    print(build())
