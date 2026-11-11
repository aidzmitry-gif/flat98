# -*- coding: utf-8 -*-
"""KLV-001: four scale-accurate 2D layouts for kitchen-living room B01.

All model coordinates and furniture envelopes are millimetres. Building geometry
is fixed by B01; furniture is a project envelope until a real SKU is selected.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "plans" / "09_Кухня-гостиная_4-варианта_2D_М1_25.pdf"
OUT_PNG = {
    "A": ROOT / "plans" / "09A_Кухня-гостиная_вариант_A.png",
    "B": ROOT / "plans" / "09B_Кухня-гостиная_вариант_B.png",
    "C": ROOT / "plans" / "09C_Кухня-гостиная_вариант_C.png",
    "D": ROOT / "plans" / "09D_Кухня-гостиная_вариант_D.png",
}

ROOM_W = 5710
ROOM_H = 3500
SCALE = 1 / 25
OX = 18.0
OY = 76.0

INK = "#1f2933"
MUTED = "#5b6570"
KITCHEN = "#f2dfba"
DINING = "#dfead9"
LOUNGE = "#e7ddd7"
WORK = "#d5e7f2"
MEDIA = "#ecdce5"
ROUTE = "#d97706"
GOOD = "#2f855a"
BAD = "#b42318"


def p(value: float) -> float:
    """Convert model millimetres to printed millimetres at 1:25."""
    return value * SCALE


def qx(value: float) -> float:
    return OX + p(value)


def qy(value: float) -> float:
    return OY + p(value)


def fonts() -> tuple[str, str]:
    regular = Path(r"C:\Windows\Fonts\arial.ttf")
    bold = Path(r"C:\Windows\Fonts\arialbd.ttf")
    if "KLV" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KLV", str(regular)))
        pdfmetrics.registerFont(TTFont("KLVB", str(bold)))
    return "KLV", "KLVB"


def text(c, font, x, y, size, value, color=INK, center=False, right=False):
    c.setFont(font, size)
    c.setFillColor(HexColor(color))
    if center:
        c.drawCentredString(x * mm, y * mm, value)
    elif right:
        c.drawRightString(x * mm, y * mm, value)
    else:
        c.drawString(x * mm, y * mm, value)


def wrap(value: str, width: int) -> list[str]:
    words = value.split()
    rows: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
        else:
            if current:
                rows.append(current)
            current = word
    if current:
        rows.append(current)
    return rows


def box(c, x, y, w, h, fill="#ffffff", stroke=INK, width=0.25, radius=0):
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke))
    c.setLineWidth(width * mm)
    if radius:
        c.roundRect(x * mm, y * mm, w * mm, h * mm, radius * mm, fill=1, stroke=1)
    else:
        c.rect(x * mm, y * mm, w * mm, h * mm, fill=1, stroke=1)


def model_box(c, x, y, w, h, fill, stroke=INK, width=0.22, radius=0):
    box(c, qx(x), qy(y), p(w), p(h), fill, stroke, width, p(radius))


def model_line(c, x1, y1, x2, y2, color=INK, width=0.18, dash=None):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width * mm)
    c.setDash(*(dash or []))
    c.line(qx(x1) * mm, qy(y1) * mm, qx(x2) * mm, qy(y2) * mm)
    c.setDash()


def label_model(c, font, x, y, value, size=4.3, color=INK, center=True):
    text(c, font, qx(x), qy(y), size, value, color, center=center)


def dim_h(c, font, x1, x2, y, label, color=MUTED):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(0.14 * mm)
    c.line(x1 * mm, y * mm, x2 * mm, y * mm)
    for x in (x1, x2):
        c.line(x * mm, (y - 1.2) * mm, x * mm, (y + 1.2) * mm)
    text(c, font, (x1 + x2) / 2, y + 1.1, 4.8, label, color, center=True)


def dim_v(c, font, x, y1, y2, label, color=MUTED):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(0.14 * mm)
    c.line(x * mm, y1 * mm, x * mm, y2 * mm)
    for y in (y1, y2):
        c.line((x - 1.2) * mm, y * mm, (x + 1.2) * mm, y * mm)
    text(c, font, x + 1.6, (y1 + y2) / 2, 4.5, label, color)


def draw_room_shell(c, regular, bold, variant):
    room_w = p(ROOM_W)
    room_h = p(ROOM_H)
    box(c, OX, OY, room_w, room_h, "#ffffff", "#111827", 0.65)
    text(c, bold, OX + room_w / 2, OY + room_h + 8.0, 7.5,
         f"B01 5710 x 3500 | ВАРИАНТ {variant}", center=True)
    dim_h(c, regular, OX, OX + room_w, OY + room_h + 3.2, "5710 - чистый размер B01")
    dim_v(c, regular, OX - 4.0, OY, OY + room_h, "3500")

    d2_a, d2_b = qy(200), qy(1110)
    c.setFillColor(white)
    c.rect((OX - 2.0) * mm, (d2_a - 1.0) * mm, 5.0 * mm,
           (d2_b - d2_a + 2.0) * mm, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#a85d18")); c.setLineWidth(0.55 * mm)
    c.line(OX * mm, d2_a * mm, OX * mm, d2_b * mm)
    text(c, bold, OX + 1.5, d2_b + 2.0, 4.5, "D2: 910 B01 / 915x2150 контроль", "#a85d18")
    dim_v(c, regular, OX - 8.0, OY, d2_a, "200")
    dim_v(c, regular, OX - 8.0, d2_a, d2_b, "910")
    dim_v(c, regular, OX - 8.0, d2_b, OY + room_h, "2390")

    o1_a, o1_b = qy(600), qy(2200)
    right = OX + room_w
    c.setFillColor(white)
    c.rect((right - 2.0) * mm, (o1_a - 1.0) * mm, 5.0 * mm,
           (o1_b - o1_a + 2.0) * mm, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#087f5b")); c.setLineWidth(0.60 * mm)
    c.line(right * mm, o1_a * mm, right * mm, o1_b * mm)
    text(c, bold, right - 1.8, (o1_a + o1_b) / 2, 4.5,
         "O1 1600 -> ТЕРРАСА", "#087f5b", right=True)
    dim_v(c, regular, right + 5.0, OY, o1_a, "600")
    dim_v(c, regular, right + 10.0, o1_a, o1_b, "1600")
    dim_v(c, regular, right + 15.0, o1_b, OY + room_h, "1300")


def draw_route(c, regular, bottleneck=900, compromised=False):
    color = BAD if compromised else ROUTE
    c.setStrokeColor(HexColor(color)); c.setLineWidth(0.35 * mm); c.setDash(1.8 * mm, 1.0 * mm)
    c.rect(qx(0) * mm, qy(350) * mm, p(5710) * mm, p(900) * mm, fill=0, stroke=1)
    c.rect(qx(4810) * mm, qy(350) * mm, p(900) * mm, p(2100) * mm, fill=0, stroke=1)
    c.setDash()
    label_model(c, regular, 3600, 440,
                f"ПУТЬ D2 -> O1 | факт. узкое место {bottleneck}", 4.2, color)


def draw_kitchen(c, regular, bold, l_branch=True):
    modules = [(0, 950, "ХОЛ.+ПЕНАЛ"), (950, 600, "МОЙКА"), (1550, 300, "ЯЩИКИ"),
               (1850, 600, "ВАРОЧН.+ДУХ."), (2450, 250, "ДОБОР"), (2700, 710, "ХРАНЕНИЕ")]
    for x, width, name in modules:
        model_box(c, x, 2900, width, 600, KITCHEN, "#6e5a34", 0.20)
        label_model(c, regular, x + width / 2, 2975, name, 3.7, "#5b4827")
    model_box(c, 1080, 3050, 340, 250, "#eef3f4", "#60747a", 0.14, 25)
    model_line(c, 1250, 3300, 1250, 3370, "#60747a", 0.18)
    c.setStrokeColor(HexColor("#5b4827")); c.setLineWidth(0.14 * mm)
    for x, y in ((2010, 3100), (2240, 3100), (2010, 3310), (2240, 3310)):
        c.circle(qx(x) * mm, qy(y) * mm, p(70) * mm, fill=0, stroke=1)
    model_line(c, 600, 2900, 600, 3500, "#6e5a34", 0.18)
    model_line(c, 0, 3200, 600, 3200, "#6e5a34", 0.18)
    label_model(c, bold, 1705, 3440, "КУХНЯ 3410 x 600 | ПРОЕКТ", 4.0, "#6e5a34")
    if l_branch:
        model_box(c, 0, 1300, 600, 1600, KITCHEN, "#6e5a34", 0.22)
        for y in (1700, 2100, 2500):
            model_line(c, 0, y, 600, y, "#6e5a34", 0.16)
        label_model(c, regular, 300, 2080, "Г-ВЕТВЬ", 3.8, "#5b4827")
        label_model(c, regular, 300, 1960, "600x1600", 3.8, "#5b4827")


def draw_chair(c, x, y, w=470, h=520, facing="up", fill="#f6f2ed"):
    model_box(c, x, y, w, h, fill, "#6d6258", 0.18, 55)
    if facing == "up":
        model_line(c, x + 55, y + 55, x + w - 55, y + 55, "#6d6258", 0.28)
    elif facing == "down":
        model_line(c, x + 55, y + h - 55, x + w - 55, y + h - 55, "#6d6258", 0.28)
    elif facing == "left":
        model_line(c, x + w - 55, y + 55, x + w - 55, y + h - 55, "#6d6258", 0.28)
    else:
        model_line(c, x + 55, y + 55, x + 55, y + h - 55, "#6d6258", 0.28)
    for px, py in ((x + 70, y + 70), (x + w - 70, y + 70),
                   (x + 70, y + h - 70), (x + w - 70, y + h - 70)):
        c.setFillColor(HexColor("#6d6258"))
        c.circle(qx(px) * mm, qy(py) * mm, p(16) * mm, fill=1, stroke=0)


def draw_rect_dining(c, regular):
    model_box(c, 1450, 1400, 800, 1400, DINING, "#52684a", 0.24, 70)
    model_line(c, 1450, 2100, 2250, 2100, "#70836a", 0.14)
    for y in (1530, 2210):
        draw_chair(c, 930, y, facing="right")
        draw_chair(c, 2250, y, facing="left")
    label_model(c, regular, 1850, 2150, "СТОЛ", 4.2, "#405238")
    label_model(c, regular, 1850, 2020, "1400x800", 4.0, "#405238")
    label_model(c, regular, 1850, 1890, "4 МЕСТА", 3.7, "#405238")


def draw_round_dining(c, regular):
    c.setFillColor(HexColor(DINING)); c.setStrokeColor(HexColor("#52684a")); c.setLineWidth(0.24 * mm)
    c.circle(qx(1700) * mm, qy(2000) * mm, p(550) * mm, fill=1, stroke=1)
    for y in (1450, 2030):
        draw_chair(c, 680, y, facing="right")
        draw_chair(c, 2250, y, facing="left")
    label_model(c, regular, 1700, 2060, "СТОЛ Ø1100", 4.1, "#405238")
    label_model(c, regular, 1700, 1930, "4 МЕСТА", 3.7, "#405238")


def draw_peninsula(c, regular):
    model_box(c, 1600, 1300, 700, 1600, DINING, "#52684a", 0.24, 55)
    for y in (1700, 2100, 2500):
        model_line(c, 1600, y, 2300, y, "#70836a", 0.14)
    draw_chair(c, 1080, 1510, facing="right")
    draw_chair(c, 1080, 2220, facing="right")
    draw_chair(c, 2300, 1510, facing="left")
    draw_chair(c, 2300, 2220, facing="left")
    label_model(c, regular, 1950, 2170, "ПОЛУОСТРОВ", 3.8, "#405238")
    label_model(c, regular, 1950, 2040, "1600x700", 3.8, "#405238")
    label_model(c, regular, 1950, 1910, "4 МЕСТА", 3.6, "#405238")


def draw_banquette_dining(c, regular):
    model_box(c, 5160, 2450, 550, 1050, "#d9e5d3", "#52684a", 0.24, 70)
    model_line(c, 5160, 2975, 5710, 2975, "#70836a", 0.14)
    model_box(c, 4360, 2450, 800, 1050, DINING, "#52684a", 0.24, 65)
    draw_chair(c, 3840, 2450, facing="right")
    draw_chair(c, 3840, 2980, facing="right")
    label_model(c, regular, 4760, 3020, "СТОЛ 1050x800", 3.9, "#405238")
    label_model(c, regular, 4760, 2890, "БАНКЕТКА + 2 СТУЛА", 3.5, "#405238")


def draw_sofa(c, regular, x, y, w=2000, h=850, facing="up"):
    model_box(c, x, y, w, h, LOUNGE, "#665a54", 0.26, 110)
    arm = 150
    model_box(c, x + 35, y + 35, arm, h - 70, "#d7ccc5", "#665a54", 0.14, 55)
    model_box(c, x + w - arm - 35, y + 35, arm, h - 70, "#d7ccc5", "#665a54", 0.14, 55)
    inner_x = x + arm + 55
    inner_w = w - 2 * arm - 110
    for idx in range(3):
        model_box(c, inner_x + idx * inner_w / 3, y + 115, inner_w / 3, h - 230,
                  "#eee7e3", "#8a7d76", 0.12, 50)
    if facing == "down":
        model_line(c, x + arm, y + h - 80, x + w - arm, y + h - 80, "#665a54", 0.30)
    else:
        model_line(c, x + arm, y + 80, x + w - arm, y + 80, "#665a54", 0.30)
    label_model(c, regular, x + w / 2, y + h / 2, f"ДИВАН {w}x{h}", 4.0, "#544943")


def draw_tv(c, regular, x, y, w=1200, h=400, wall="top"):
    model_box(c, x, y, w, h, MEDIA, "#6d5364", 0.20, 40)
    if wall == "top":
        model_box(c, x + 120, y + h - 95, w - 240, 45, "#29333c", "#29333c", 0.10, 12)
    else:
        model_box(c, x + 120, y + 50, w - 240, 45, "#29333c", "#29333c", 0.10, 12)
    label_model(c, regular, x + w / 2, y + h / 2, f"ТВ + МЕДИА {w}x{h}", 3.7, "#624a59")


def draw_task_chair(c, cx, cy, facing="left"):
    c.setFillColor(HexColor("#eff5f8")); c.setStrokeColor(HexColor("#4b6d82")); c.setLineWidth(0.18 * mm)
    c.circle(qx(cx) * mm, qy(cy) * mm, p(255) * mm, fill=1, stroke=1)
    for dx, dy in ((0, 310), (280, 80), (170, -260), (-170, -260), (-280, 80)):
        model_line(c, cx, cy, cx + dx, cy + dy, "#4b6d82", 0.15)
        c.setFillColor(HexColor("#4b6d82")); c.circle(qx(cx + dx) * mm, qy(cy + dy) * mm, p(28) * mm, fill=1, stroke=0)
    if facing == "left":
        model_box(c, cx - 310, cy - 220, 95, 440, "#d5e7f2", "#4b6d82", 0.16, 35)
    elif facing == "right":
        model_box(c, cx + 215, cy - 220, 95, 440, "#d5e7f2", "#4b6d82", 0.16, 35)
    else:
        model_box(c, cx - 220, cy + 215, 440, 95, "#d5e7f2", "#4b6d82", 0.16, 35)


def draw_desk(c, regular, x, y, w, h, orientation, compact=False, shared=False):
    model_box(c, x, y, w, h, WORK, "#4b6d82", 0.24, 35)
    if orientation == "right-wall":
        model_box(c, x + w - 130, y + 270, 70, 460, "#29333c", "#29333c", 0.10, 10)
        model_box(c, x + 250, y + 350, 180, 300, "#f7fafb", "#4b6d82", 0.12, 15)
        for sy in (220, 780):
            c.setFillColor(HexColor("#4b6d82")); c.circle(qx(x + 260) * mm, qy(y + sy) * mm, p(60) * mm, fill=1, stroke=0)
        model_line(c, x + 430, y + 760, x + 260, y + 600, "#4b6d82", 0.18)
        c.setFillColor(HexColor("#29333c")); c.circle(qx(x + 245) * mm, qy(y + 585) * mm, p(32) * mm, fill=1, stroke=0)
        draw_task_chair(c, x - 310, y + h / 2, "right")
    elif orientation == "left-wall":
        model_box(c, x + 60, y + 300, 70, 600, "#29333c", "#29333c", 0.10, 10)
        model_box(c, x + 180, y + 430, 300, 200, "#f7fafb", "#4b6d82", 0.12, 15)
        for sy in (250, 950):
            c.setFillColor(HexColor("#4b6d82")); c.circle(qx(x + 320) * mm, qy(y + sy) * mm, p(60) * mm, fill=1, stroke=0)
        model_line(c, x + 390, y + 940, x + 300, y + 760, "#4b6d82", 0.18)
        c.setFillColor(HexColor("#29333c")); c.circle(qx(x + 290) * mm, qy(y + 740) * mm, p(32) * mm, fill=1, stroke=0)
        draw_task_chair(c, x + w + 320, y + h / 2, "left")
    else:
        model_box(c, x + 280, y + h - 120, 620, 70, "#29333c", "#29333c", 0.10, 10)
        model_box(c, x + 420, y + 150, 360, 180, "#f7fafb", "#4b6d82", 0.12, 15)
        for sx in (180, 1020):
            c.setFillColor(HexColor("#4b6d82")); c.circle(qx(x + sx) * mm, qy(y + 230) * mm, p(60) * mm, fill=1, stroke=0)
        model_line(c, x + 990, y + 310, x + 840, y + 190, "#4b6d82", 0.18)
        c.setFillColor(HexColor("#29333c")); c.circle(qx(x + 825) * mm, qy(y + 180) * mm, p(32) * mm, fill=1, stroke=0)
        draw_task_chair(c, x + w / 2, y - 320, "up")
    suffix = "КОМПАКТ" if compact else "ПРОЕКТ"
    label_model(c, regular, x + w / 2, y + h / 2, f"РМ {max(w, h)}x{min(w, h)} | {suffix}", 3.5, "#355d76")
    audio_label = "КОЛОНКИ + МИК." if w < 900 else "КОЛОНКИ + МИКРОФОН"
    label_model(c, regular, x + w / 2, y + 70, audio_label, 2.8, "#355d76")
    if shared:
        label_model(c, regular, x + w / 2, y + 110, "ЗОНА КРЕСЛА ОБЩАЯ", 3.0, BAD)


def draw_clearance_zone(c, regular, x, y, w, h, label, color="#4d7c98"):
    c.setStrokeColor(HexColor(color)); c.setLineWidth(0.25 * mm); c.setDash(1.4 * mm, 0.9 * mm)
    c.rect(qx(x) * mm, qy(y) * mm, p(w) * mm, p(h) * mm, fill=0, stroke=1)
    c.setDash(); label_model(c, regular, x + w / 2, y + 90, label, 3.4, color)


def draw_family_zone(c, regular, x, y, w, h, area):
    c.setStrokeColor(HexColor(GOOD)); c.setLineWidth(0.30 * mm); c.setDash(2.0 * mm, 1.0 * mm)
    c.rect(qx(x) * mm, qy(y) * mm, p(w) * mm, p(h) * mm, fill=0, stroke=1)
    c.setDash()
    label = f"СВОБ. {area:.1f} м2" if w < 900 else f"СВОБОДНЫЙ ЦЕНТР {area:.1f} м2"
    label_model(c, regular, x + w / 2, y + h / 2, label, 4.0, GOOD)


def variant_a(c, regular, bold):
    draw_route(c, regular, 900); draw_kitchen(c, regular, bold, True); draw_rect_dining(c, regular)
    draw_sofa(c, regular, 2810, 1300, 2000, 850, "up"); draw_tv(c, regular, 3410, 3100, 1000, 400, "top")
    draw_clearance_zone(c, regular, 4410, 2600, 700, 800, "ОТКАТ РМ 700")
    draw_desk(c, regular, 5110, 2500, 600, 1000, "right-wall", compact=True)
    draw_family_zone(c, regular, 2720, 2150, 1490, 450, 0.7)
    label_model(c, regular, 2680, 2840, "100 - стол до фронта кухни", 3.4, BAD)
    return {"title": "A - КЛАССИЧЕСКИЙ БАЛАНС",
            "subtitle": "Г-кухня, обычный стол, диван лицом к ТВ, компактное РМ у O1",
            "metrics": [("Маршрут D2-O1", "900", 4), ("У кухни", "100", 1), ("За стулом", "90", 1),
                        ("Откат РМ", "700", 2), ("Закр. хранение*", "5010", 5), ("Своб. прямоуг.*", "0.7 м2", 1),
                        ("Ребёнок/питомцы*", "2 рег.", 2)],
            "pros": ["Полноценный стол на 4", "Максимум кухонного хранения", "Прямой обзор ТВ"],
            "cons": ["РМ только 1000x600", "100 мм у рабочего фронта", "90 мм и 2 тесные зоны для ребёнка/питомцев"], "recommend": False}


def variant_b(c, regular, bold):
    draw_route(c, regular, 900); draw_kitchen(c, regular, bold, False)
    draw_peninsula(c, regular)
    draw_clearance_zone(c, regular, 3410, 2050, 1200, 850, "ОТКАТ РМ 850")
    draw_desk(c, regular, 3410, 2900, 1200, 600, "top-wall")
    draw_sofa(c, regular, 2810, 1250, 2000, 800, "down"); draw_tv(c, regular, 3410, 0, 1200, 300, "bottom")
    draw_family_zone(c, regular, 2770, 2050, 640, 850, 0.5)
    label_model(c, regular, 2555, 2110, "510 - полуостров до дивана", 3.4, BAD)
    return {"title": "B - КУХНЯ С ПОЛУОСТРОВОМ",
            "subtitle": "Прямая кухня, РМ в верхней линии, полуостров для еды и хранения",
            "metrics": [("Маршрут D2-O1", "900", 4), ("У полуострова", "510", 1), ("За стулом", "40", 1),
                        ("Откат РМ", "850", 4), ("Закр. хранение*", "5010", 5), ("Своб. прямоуг.*", "0.5 м2", 1),
                        ("Ребёнок/питомцы*", "2 рег.", 2)],
            "pros": ["Больше столешницы", "Четыре посадочных места", "РМ шириной 1200"],
            "cons": ["40 мм за правыми стульями", "Стулья конфликтуют с путём ребёнка/питомцев", "Узкий боковой проход 510"], "recommend": False}


def variant_c(c, regular, bold):
    draw_route(c, regular, 900); draw_kitchen(c, regular, bold, True); draw_round_dining(c, regular)
    draw_clearance_zone(c, regular, 3410, 2150, 1200, 750, "ОТКАТ РМ 750")
    draw_desk(c, regular, 3410, 2900, 1200, 600, "top-wall")
    draw_sofa(c, regular, 2810, 1300, 2000, 850, "down"); draw_tv(c, regular, 3410, 0, 1200, 300, "bottom")
    draw_family_zone(c, regular, 2720, 2150, 690, 750, 0.5)
    label_model(c, regular, 1700, 2700, "350 - стулья до фронта кухни", 3.5, BAD)
    return {"title": "C - КРУГЛЫЙ СТОЛ + ВСТРОЕННОЕ РМ",
            "subtitle": "Г-кухня, круглый стол, РМ в общей верхней линии, диван-зонирование",
            "metrics": [("Маршрут D2-O1", "900", 4), ("У кухни", "350", 1), ("За стулом", "90", 1),
                        ("Откат РМ", "750", 3), ("Закр. хранение*", "5010", 5), ("Своб. прямоуг.*", "0.5 м2", 1),
                        ("Ребёнок/питомцы*", "3 рег.", 1)],
            "pros": ["Мягкая круглая геометрия", "РМ 1200x600", "Удобное общение за столом"],
            "cons": ["350 мм у рабочего фронта", "90 мм у дивана; 3 тесные зоны для ребёнка/питомцев", "Откат кресла только 750"], "recommend": False}


def variant_d(c, regular, bold):
    draw_route(c, regular, 900); draw_kitchen(c, regular, bold, False)
    draw_clearance_zone(c, regular, 600, 1500, 900, 1200, "ОТКАТ РМ 900")
    draw_desk(c, regular, 0, 1500, 600, 1200, "left-wall"); draw_banquette_dining(c, regular)
    draw_sofa(c, regular, 2810, 1300, 2000, 850, "down"); draw_tv(c, regular, 3410, 0, 1200, 300, "bottom")
    draw_family_zone(c, regular, 1500, 1250, 1310, 1650, 2.2)
    label_model(c, regular, 3625, 2320, "430 - за отдельными стульями", 3.4, BAD)
    label_model(c, regular, 3110, 2550, "750 - локально кухня-диван", 3.4, BAD)
    return {"title": "D - СЕМЕЙНАЯ БАНКЕТКА",
            "subtitle": "Прямая кухня, РМ слева, банкетка у верхнего простенка O1, свободный центр",
            "metrics": [("Маршрут D2-O1", "900", 4), ("Кухня-диван", "750", 1), ("За стулом", "430", 1),
                        ("Откат РМ", "900", 5), ("Закр. хранение*", "4460", 5), ("Своб. прямоуг.*", "2.2 м2", 3),
                        ("Ребёнок/питомцы*", "1 редк.", 4)],
            "pros": ["Свободный центр для ребёнка/питомцев", "РМ 1200x600 вне маршрута", "Детям удобно на банкетке"],
            "cons": ["Локально кухня-диван 750", "430 мм за отдельными стульями", "Банкетка только на заказ"], "recommend": True}


def score_average(metrics):
    return sum(item[2] for item in metrics) / len(metrics)


def draw_sidebar(c, regular, bold, info):
    x, y, w, h = 270, 76, 134, 192
    box(c, x, y, w, h, "#fbfcfd", "#34414c", 0.28)
    text(c, bold, x + 7, y + h - 12, 9.0, info["title"], GOOD if info["recommend"] else INK)
    yy = y + h - 21
    for row in wrap(info["subtitle"], 44):
        text(c, regular, x + 7, yy, 4.8, row, MUTED); yy -= 6
    total = score_average(info["metrics"])
    box(c, x + 96, y + h - 31, 30, 14, "#e8f4ec" if info["recommend"] else "#f1f3f5",
        GOOD if info["recommend"] else "#77818b", 0.20, 2)
    text(c, bold, x + 111, y + h - 26.5, 7.6, f"{total:.1f}/5", GOOD if info["recommend"] else INK, center=True)
    if info["recommend"]:
        text(c, bold, x + 111, y + h - 30.0, 3.6, "РЕКОМЕНДУЮ", GOOD, center=True)
    yy -= 4; text(c, bold, x + 7, yy, 6.3, "ИЗМЕРИМАЯ ОЦЕНКА"); yy -= 7
    for label, value, score in info["metrics"]:
        color = GOOD if score >= 4 else ("#ad6800" if score == 3 else BAD)
        text(c, regular, x + 7, yy, 4.35, label, MUTED); text(c, bold, x + 92, yy, 4.35, value, INK, right=True)
        box(c, x + 98, yy - 1.5, 8, 5.3, "#ffffff", color, 0.18, 1)
        text(c, bold, x + 102, yy - 0.2, 4.2, str(score), color, center=True); yy -= 7
    text(c, bold, x + 7, yy - 1, 6.0, "ПЛЮСЫ", GOOD); yy -= 8
    for item in info["pros"]:
        for index, row in enumerate(wrap(item, 39)):
            text(c, regular, x + 7, yy, 4.25, ("+ " if index == 0 else "  ") + row, "#345f45"); yy -= 5
    yy -= 2; text(c, bold, x + 7, yy, 6.0, "КОМПРОМИССЫ", BAD); yy -= 7
    for item in info["cons"]:
        for index, row in enumerate(wrap(item, 39)):
            text(c, regular, x + 7, yy, 4.15, ("- " if index == 0 else "  ") + row, "#7a3029"); yy -= 5


def draw_page(c, regular, bold, variant, draw_variant):
    page_w, page_h = landscape(A3)
    c.setFillColor(white); c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, page_w - 16 * mm, page_h - 16 * mm, fill=0, stroke=1)
    text(c, bold, 14, 282, 14.5, f"КУХНЯ-ГОСТИНАЯ | ВАРИАНТ {variant} | М 1:25")
    text(c, regular, 14, 274, 5.4, "B01 и проемы - фактические. Мебель и техника - проектные габаритные конверты до выбора SKU.", MUTED)
    draw_room_shell(c, regular, bold, variant)
    info = draw_variant(c, regular, bold)
    draw_sidebar(c, regular, bold, info)
    c.setStrokeColor(HexColor(INK)); c.setLineWidth(0.45 * mm)
    c.line(18 * mm, 61 * mm, 58 * mm, 61 * mm); c.line(18 * mm, 59.5 * mm, 18 * mm, 62.5 * mm); c.line(58 * mm, 59.5 * mm, 58 * mm, 62.5 * mm)
    text(c, bold, 38, 63.0, 5.0, "1000 мм = 40 мм на листе", center=True)
    notes = [
        "ФАКТ: B01 5710x3500; D2 200+910 (контроль 915x2150); O1 600+1600+1300.",
        "РЕКОМЕНДАЦИИ NKBA, не нормы РБ: проход 914; рабочий проход 1067 для одного; за стулом без транзита 813.",
        "ПРОЕКТ*: откат РМ 900; хранение = кухня + закрытая сторона полуострова/банкетки; свободный прямоугольник считается выше маршрута.",
        "ОЦЕНКА: проходы 5=ориентир; 4=до 50 ниже; 3=51-150; 2=151-250; 1=>250. Хранение: 5>=4000; 4>=3400; 3>=2800; 2>=2200; 1<2200.",
        "СВОБ. ЗОНА*: 5>=4.0; 4>=3.0; 3>=2.2; 2>=1.5; 1<1.5 м2 непрерывного незанятого пола выше маршрута.",
        "СЕМЬЯ*: 5=нет конфликтов; 4=один редкий; 3=один регулярный; 2=два; 1=три и более либо блокировка маршрута ребёнком/питомцем.",
        "КОНТРОЛЬ: вода, E-01, радиаторы и конкретные модели мебели/техники требуют привязки до рабочей документации.",
    ]
    yy = 51
    for row in notes:
        text(c, regular, 18, yy, 4.35, row, MUTED); yy -= 6
    text(c, regular, 404, 14, 4.0, f"KLV-001 | revision 3 | лист {variant}/4 | 20.08.2026", MUTED, right=True)
    c.showPage()


def find_pdftoppm() -> Path:
    found = shutil.which("pdftoppm")
    if found:
        return Path(found)
    bundled = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "native" / "poppler" / "Library" / "bin" / "pdftoppm.exe"
    if bundled.exists():
        return bundled
    raise FileNotFoundError("pdftoppm not found; PDF created but PNG previews cannot be rendered")


def render_pngs() -> list[Path]:
    temp_dir = ROOT / "tmp" / "pdfs" / "klv001"
    temp_dir.mkdir(parents=True, exist_ok=True)
    prefix = temp_dir / "page"
    subprocess.run([str(find_pdftoppm()), "-png", "-r", "150", str(OUT_PDF), str(prefix)], check=True)
    rendered = sorted(temp_dir.glob("page-*.png"))
    if len(rendered) != 4:
        raise RuntimeError(f"Expected 4 rendered pages, got {len(rendered)}")
    outputs: list[Path] = []
    for variant, source in zip("ABCD", rendered):
        target = OUT_PNG[variant]
        if target.exists():
            target.unlink()
        source.replace(target); outputs.append(target)
    return outputs


def build() -> tuple[Path, list[Path]]:
    regular, bold = fonts(); OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT_PDF), pagesize=landscape(A3), pageCompression=1)
    c.setTitle("KLV-001 - четыре варианта кухни-гостиной B01"); c.setAuthor("Codex / KLV-001")
    for variant, drawer in (("A", variant_a), ("B", variant_b), ("C", variant_c), ("D", variant_d)):
        draw_page(c, regular, bold, variant, drawer)
    c.save(); return OUT_PDF, render_pngs()


if __name__ == "__main__":
    pdf, pngs = build(); print(pdf)
    for png in pngs:
        print(png)
