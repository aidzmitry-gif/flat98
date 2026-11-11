# -*- coding: utf-8 -*-
"""Build D+/E+ kitchen-living layouts and a new combined KLV-001 PDF.

All model coordinates are millimetres in the clear B01 shell 5710 x 3500.
The final PDF keeps the already-issued A-D and E pages unchanged, then inserts
four new scale-accurate pages. Furniture is conceptual until engineering axes,
D2 swing and real products are measured.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base
import build_kitchen_variant_e as old_e


ROOT = Path(__file__).resolve().parents[1]
SOURCE_AD = ROOT / "plans" / "09_Кухня-гостиная_4-варианта_2D_М1_25.pdf"
SOURCE_E = ROOT / "output" / "pdf" / "KLV-001_вариант_E_двухрежимный_М1-25.pdf"
TMP_DIR = ROOT / "tmp" / "pdfs" / "klv001_dplus_eplus"
PLUS_PDF = TMP_DIR / "KLV-001_Dplus_Eplus_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "KLV-001_все_варианты_A-E_с_Dplus_Eplus_М1-25.pdf"
QA_DIR = TMP_DIR / "rendered"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
LOUNGE = base.LOUNGE
WORK = base.WORK
MEDIA = base.MEDIA
GOOD = base.GOOD
BAD = base.BAD


def overlaps(a, b) -> bool:
    """Positive-area rectangle overlap; touching edges is allowed."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return max(ax1, bx1) < min(ax2, bx2) and max(ay1, by1) < min(ay2, by2)


def check_mode(mode: str, objects: dict[str, tuple[int, int, int, int]]) -> None:
    route = ((0, 350, 5710, 1250), (4810, 350, 5710, 2450))
    d2_guard = (0, 0, 1200, 1300)
    for name, rect in objects.items():
        x1, y1, x2, y2 = rect
        if not (0 <= x1 < x2 <= 5710 and 0 <= y1 < y2 <= 3500):
            raise AssertionError(f"{mode}/{name} outside B01: {rect}")
        if overlaps(rect, d2_guard):
            raise AssertionError(f"{mode}/{name} enters D2 guard: {rect}")
        for index, protected in enumerate(route, start=1):
            if overlaps(rect, protected):
                raise AssertionError(f"{mode}/{name} enters protected route {index}: {rect}")


def check_pairwise(mode: str, objects: dict[str, tuple[int, int, int, int]],
                   allowed: set[frozenset[str]] | None = None) -> None:
    allowed = allowed or set()
    names = list(objects)
    for index, left in enumerate(names):
        for right in names[index + 1:]:
            if frozenset((left, right)) in allowed:
                continue
            if overlaps(objects[left], objects[right]):
                raise AssertionError(
                    f"{mode}: unintended overlap {left} / {right}: "
                    f"{objects[left]} / {objects[right]}"
                )


def validate_geometry() -> None:
    dplus_common = {
        "kitchen": (600, 2900, 2900, 3500),
        "desk": (0, 1300, 600, 2500),
        "desk chair": (600, 1440, 1200, 2060),
        "sofa": (3000, 1500, 4780, 2300),
        "side table": (2660, 1800, 2960, 2100),
        "dining chair 1": (3910, 2475, 4310, 2975),
        "dining chair 2": (3910, 3000, 4310, 3500),
        "dining table": (4310, 2450, 5160, 3500),
        "dining bench": (5160, 2450, 5710, 3500),
        "media console": (3150, 0, 4630, 300),
    }
    dplus_social = {
        **dplus_common,
        "pouf 1": (1450, 1350, 1850, 1750),
        "pouf 2": (2150, 1350, 2550, 1750),
    }
    check_mode("D+ daily", dplus_common)
    check_mode("D+ social", dplus_social)
    check_pairwise("D+ daily", dplus_common)
    check_pairwise("D+ social", dplus_social)

    if 3910 - 2900 != 1010:
        raise AssertionError("D+ kitchen-to-chair clearance drift")
    if 4810 - 4780 != 30:
        raise AssertionError("D+ sofa-to-O1 route clearance drift")
    if 1500 - 1250 != 250:
        raise AssertionError("D+ sofa-to-horizontal-route clearance drift")
    if 2900 - 2060 != 840:
        raise AssertionError("D+ work-chair-to-kitchen clearance drift")

    eplus_common = {
        "kitchen": (0, 2900, 2200, 3500),
        "desk": (4510, 2900, 5710, 3500),
        "desk chair": (4855, 2505, 5365, 3015),
        "banquette": (4000, 1325, 4400, 2975),
        "media rail": (100, 1320, 160, 2820),
    }
    eplus_daily = {
        **eplus_common,
        "table": (2850, 1500, 3650, 2700),
        "chair 1": (2300, 1550, 2850, 2100),
        "chair 2": (2300, 2150, 2850, 2700),
    }
    eplus_guest = {
        **eplus_common,
        "table": (2850, 1325, 3650, 2975),
        "chair 1": (2300, 1325, 2850, 1875),
        "chair 2": (2300, 1875, 2850, 2425),
        "chair 3": (2300, 2425, 2850, 2975),
    }
    allowed = {frozenset(("desk", "desk chair"))}
    check_mode("E+ daily", eplus_daily)
    check_mode("E+ guest", eplus_guest)
    check_pairwise("E+ daily", eplus_daily, allowed)
    check_pairwise("E+ guest", eplus_guest, allowed)

    if 2300 - 2200 != 100:
        raise AssertionError("E+ kitchen-to-dining side clearance drift")
    if 4000 - 3650 != 350:
        raise AssertionError("E+ table-to-banquette gap drift")
    if 4810 - 4400 != 410:
        raise AssertionError("E+ banquette-to-O1 route clearance drift")
    if 2505 - 2450 != 55:
        raise AssertionError("E+ chair-to-O1 route clearance drift")


def dashed_model_box(c, x, y, w, h, color, label, regular, label_y=None):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(0.20 * mm)
    c.setDash(1.5 * mm, 0.9 * mm)
    c.rect(base.qx(x) * mm, base.qy(y) * mm,
           base.p(w) * mm, base.p(h) * mm, fill=0, stroke=1)
    c.setDash()
    base.label_model(c, regular, x + w / 2, label_y or (y + h / 2), label, 3.0, color)


def draw_kitchen_dplus(c, regular, bold):
    modules = (
        (600, 600, "ХОЛ.+ПЕНАЛ"),
        (1200, 600, "МОЙКА+ПММ"),
        (1800, 500, "ПОДГОТОВКА"),
        (2300, 600, "ВАРОЧН.+ДУХ."),
    )
    for x, width, label in modules:
        base.model_box(c, x, 2900, width, 600, KITCHEN, "#6e5a34", 0.20)
        base.label_model(c, regular, x + width / 2, 2975, label, 3.3, "#5b4827")
    base.model_box(c, 1440, 3050, 330, 240, "#eef3f4", "#60747a", 0.14, 25)
    for x, y in ((2470, 3100), (2690, 3100), (2470, 3310), (2690, 3310)):
        c.setStrokeColor(HexColor("#5b4827"))
        c.setLineWidth(0.14 * mm)
        c.circle(base.qx(x) * mm, base.qy(y) * mm, base.p(65) * mm, fill=0, stroke=1)
    dashed_model_box(c, 0, 2900, 600, 600, "#7f6a42", "НАВЕСНОЕ ХРАНЕНИЕ", regular, 3300)
    base.label_model(c, bold, 1750, 3435, "АКТИВНАЯ КУХНЯ 2300x600", 3.9, "#6e5a34")
    base.label_model(c, regular, 300, 2990, "НЕ ПОЛОВОЙ МОДУЛЬ", 2.8, BAD)


def draw_dplus_dining(c, regular, bold):
    base.model_box(c, 5160, 2450, 550, 1050, "#d9e5d3", "#52684a", 0.24, 70)
    base.model_line(c, 5160, 2975, 5710, 2975, "#70836a", 0.14)
    base.model_box(c, 4310, 2450, 850, 1050, DINING, "#52684a", 0.24, 55)
    base.model_line(c, 4310, 2975, 5160, 2975, "#70836a", 0.14)
    base.draw_chair(c, 3910, 2475, 400, 500, "right")
    base.draw_chair(c, 3910, 3000, 400, 500, "right")
    base.label_model(c, bold, 4735, 3060, "СТОЛ 1050x850", 3.7, "#405238")
    base.label_model(c, regular, 4735, 2935, "2 СТУЛА + БАНКЕТКА = 4", 3.2, "#405238")
    base.model_line(c, 2900, 3100, 3910, 3100, "#ad6800", 0.18)
    base.label_model(c, regular, 3405, 3140, "1010 за стульями", 3.0, "#ad6800")


def draw_dplus_sofa_media(c, regular, bold):
    base.draw_sofa(c, regular, 3000, 1500, 1780, 800, "down")
    base.model_box(c, 2660, 1800, 300, 300, "#f4eee8", "#7e7067", 0.18, 60)
    base.label_model(c, regular, 2810, 1935, "C-СТОЛ", 2.8, "#5e514a")
    base.model_box(c, 3150, 0, 1480, 300, MEDIA, "#6d5364", 0.20, 40)
    base.model_box(c, 3165, 35, 1450, 55, "#29333c", "#29333c", 0.10, 10)
    base.label_model(c, bold, 3890, 185, "ТВ 65\" MAX / 55\" БЕЗОПАСНЕЕ", 3.4, "#624a59")
    base.model_line(c, 3890, 100, 3890, 1950, "#6d5364", 0.20, [base.p(70), base.p(45)])
    base.label_model(c, regular, 4150, 1160, "ОСЬ ГЛАЗ ≈1950", 3.0, "#624a59")
    base.model_line(c, 4780, 1700, 4810, 1700, BAD, 0.20)
    base.label_model(c, regular, 4520, 1740, "30 до O1-маршрута", 2.8, BAD)


def draw_dplus_open_zone(c, regular, social: bool):
    dashed_model_box(c, 1450, 1300, 1200, 1500, GOOD,
                     "СОЦИАЛЬНЫЙ ЦЕНТР" if social else "СВОБОДНО ДЛЯ РЕБЁНКА / ПИТОМЦЕВ",
                     regular, 2560)
    if social:
        for x, label in ((1450, "ПУФ 8"), (2150, "ПУФ 9")):
            base.model_box(c, x, 1350, 400, 400, "#eee4d2", "#8a744e", 0.20, 90)
            base.label_model(c, regular, x + 200, 1540, label, 3.1, "#6b5839")
        base.label_model(c, regular, 2050, 2650, "9 СОЦИАЛЬНЫХ МЕСТ, НЕ 9 ЗА СТОЛОМ", 3.3, BAD)
    else:
        base.label_model(c, regular, 2050, 2440, "≈1.8 м² непрерывной зоны", 3.1, GOOD)


def draw_workstation_dplus(c, regular):
    base.draw_clearance_zone(c, regular, 600, 1300, 900, 1200, "ЗОНА КРЕСЛА 900")
    base.model_box(c, 0, 1300, 600, 1200, WORK, "#4b6d82", 0.24, 35)
    base.model_box(c, 60, 1450, 70, 600, "#29333c", "#29333c", 0.10, 10)
    base.model_box(c, 180, 1650, 300, 200, "#f7fafb", "#4b6d82", 0.12, 15)
    for sy in (1470, 2030):
        c.setFillColor(HexColor("#4b6d82"))
        c.circle(base.qx(320) * mm, base.qy(sy) * mm, base.p(60) * mm, fill=1, stroke=0)
    base.draw_task_chair(c, 920, 1750, "left")
    base.label_model(c, regular, 300, 1900, "РМ 1200x600", 3.5, "#355d76")
    base.label_model(c, regular, 300, 1370, "КОЛОНКИ + МИК.", 2.8, "#355d76")
    base.label_model(c, regular, 300, 2560, "D2: СТОРОНА ПЕТЕЛЬ Н/Д", 2.9, BAD)
    base.model_line(c, 920, 2060, 920, 2900, "#ad6800", 0.18)
    base.label_model(c, regular, 1120, 2470, "840 кресло-кухня", 2.8, "#ad6800")


def draw_tv_eplus(c, regular, bold):
    c.setStrokeColor(HexColor("#6d5364"))
    c.setLineWidth(0.24 * mm)
    c.setDash(1.6 * mm, 0.8 * mm)
    c.rect(base.qx(0) * mm, base.qy(1240) * mm,
           base.p(100) * mm, base.p(1660) * mm, fill=0, stroke=1)
    c.setDash()
    base.model_box(c, 100, 1320, 60, 1500, "#29333c", "#29333c", 0.10, 8)
    base.label_model(c, bold, 610, 2815, "ТВ 75\" / ПРОЕКТОР TBD", 3.7, "#624a59")
    base.label_model(c, regular, 610, 2705, "ЭКРАН ≈1660 ПО СТЕНЕ", 3.0, "#624a59")
    base.model_line(c, 100, 2100, 4050, 2100, "#6d5364", 0.20, [base.p(75), base.p(45)])
    base.label_model(c, regular, 2050, 2140, "≈3950 ДО ГЛАЗ | ВТОРИЧНЫЙ LOUNGE", 3.0, "#624a59")


def draw_kitchen_eplus(c, regular, bold):
    modules = (
        (0, 600, "ХОЛ.+ПЕНАЛ"),
        (600, 600, "МОЙКА+ПММ"),
        (1200, 400, "ЯЩИКИ"),
        (1600, 600, "ВАРОЧН.+ДУХ."),
    )
    for x, width, label in modules:
        base.model_box(c, x, 2900, width, 600, KITCHEN, "#6e5a34", 0.20)
        base.label_model(c, regular, x + width / 2, 2975, label, 3.2, "#5b4827")
    base.model_box(c, 750, 3050, 330, 240, "#eef3f4", "#60747a", 0.14, 25)
    for x, y in ((1740, 3100), (1960, 3100), (1740, 3310), (1960, 3310)):
        c.setStrokeColor(HexColor("#5b4827"))
        c.setLineWidth(0.14 * mm)
        c.circle(base.qx(x) * mm, base.qy(y) * mm, base.p(65) * mm, fill=0, stroke=1)
    base.label_model(c, bold, 1100, 3435, "КОМПАКТНАЯ КУХНЯ 2200x600", 3.9, "#6e5a34")


def draw_eplus_banquette(c, regular):
    base.model_box(c, 4000, 1325, 400, 1650, LOUNGE, "#665a54", 0.24, 70)
    for y in (1875, 2425):
        base.model_line(c, 4000, y, 4400, y, "#8a7d76", 0.14)
    base.model_box(c, 4260, 1370, 90, 1560, "#d7ccc5", "#665a54", 0.13, 35)
    base.label_model(c, regular, 4200, 2170, "БАНКЕТКА", 3.5, "#544943")
    base.label_model(c, regular, 4200, 2050, "1650x400 | 3", 3.2, "#544943")
    base.model_line(c, 3650, 3050, 4000, 3050, "#ad6800", 0.18)
    base.label_model(c, regular, 3825, 3090, "350", 3.0, "#ad6800")
    base.model_line(c, 4400, 1275, 4810, 1275, "#ad6800", 0.18)
    base.label_model(c, regular, 4605, 1315, "410 до O1-зоны", 2.8, "#ad6800")


def draw_eplus_table(c, regular, bold, mode: str):
    if mode == "daily":
        y, length = 1500, 1200
        chairs = ((1550, 550), (2150, 550))
        label = "DAILY 1200x800 | 2+2=4"
    else:
        y, length = 1325, 1650
        chairs = ((1325, 550), (1875, 550), (2425, 550))
        label = "GUEST 1650x800 | 3+3=6"
    base.model_box(c, 2850, y, 800, length, DINING, "#52684a", 0.25, 45)
    segments = (2 if mode == "daily" else 3)
    for index in range(1, segments):
        split = y + length * index / segments
        base.model_line(c, 2850, split, 3650, split, "#70836a", 0.14)
    for chair_y, chair_h in chairs:
        base.draw_chair(c, 2300, chair_y, 550, chair_h, "right")
    base.label_model(c, bold, 3250, y + length / 2 + 70, label, 3.4, "#405238")
    if mode == "guest":
        base.label_model(c, regular, 3250, y + length / 2 - 70, "550 мм/ЧЕЛ. - КОМПАКТНО", 3.0, BAD)
    base.model_line(c, 2200, 2820, 2300, 2820, "#ad6800", 0.18)
    base.label_model(c, regular, 2250, 2860, "100", 2.8, "#ad6800")


def draw_eplus_open_zone(c, regular, guest: bool):
    dashed_model_box(c, 250, 1300, 1900, 1500, GOOD,
                     "ГОСТЕВОЙ РЕЗЕРВ / ДОСТУП К СТУЛЬЯМ" if guest else "СВОБОДНО ДЛЯ ИГРЫ / ДОСТУП К СТУЛЬЯМ",
                     regular, 2520)
    base.label_model(c, regular, 1200, 2400, "≈2.9 м² до мебели", 3.1, GOOD)


def draw_side_panel(c, regular, bold, variant: str, mode: str):
    x, y, w, h = 270, 76, 134, 192
    base.box(c, x, y, w, h, "#fbfcfd", "#34414c", 0.28)
    if variant == "D+":
        title = "D+1 - ЕЖЕДНЕВНО" if mode == "daily" else "D+2 - ГОСТИ / ОБЩЕНИЕ"
        rows = [
            ("Кухня", "2300x600, компакт"),
            ("Рабочее место", "1200x600"),
            ("Диван", "1780x800, 3"),
            ("Стол", "1050x850, 4"),
            ("Путь D2-O1", "900, PASS"),
            ("ТВ", "65 max; ось ≈1950"),
        ] if mode == "daily" else [
            ("За столом", "4"),
            ("На диване", "3"),
            ("Мобильные пуфы", "2"),
            ("Социальная посадка", "до 9"),
            ("Ужин", "только 4"),
            ("Путь D2-O1", "900, PASS"),
        ]
        strengths = [
            "Отдельный мягкий диван, не банкетка",
            "Рабочее кресло имеет резерв 900",
            "1010 за обеденными стульями",
            "Гостевой режим без переноса тяжёлой мебели",
        ]
        compromises = [
            "Кухня 2300 - компактная",
            "Стол на 4; 7-9 только для общения",
            "Локально кресло-кухня 840",
            "До O1-зоны от дивана лишь 30",
        ]
    else:
        title = "E+1 - ЕЖЕДНЕВНО" if mode == "daily" else "E+2 - УЖИН 6"
        rows = [
            ("Кухня", "2200x600, минимум"),
            ("Рабочее место", "1200x600"),
            ("Стол", "1200x800, 4"),
            ("Банкетка", "1650x400"),
            ("Путь D2-O1", "900, PASS"),
            ("Свободная зона", "≈2.9 м²"),
        ] if mode == "daily" else [
            ("Стол", "1650x800"),
            ("Посадка", "3+3 = 6"),
            ("Ширина места", "550, компакт"),
            ("Путь D2-O1", "900, PASS"),
            ("Рабочее место", "остаётся"),
            ("Перевод режима", "<5 минут"),
        ]
        strengths = [
            "Шесть человек за одним столом",
            "Стол глубиной 800, а не 700",
            "Активная кухня не перекрыта стульями",
            "410 до защищённой зоны O1",
        ]
        compromises = [
            "Кухня 2200 - минимальная",
            "Банкетка 400 - не глубокий диван",
            "550 мм/чел. - компактный ужин",
            "Кресло РМ имеет лишь 55 до O1-зоны",
        ]

    base.text(c, bold, x + 7, y + h - 12, 8.0, title, GOOD)
    yy = y + h - 28
    for label, value in rows:
        base.text(c, regular, x + 7, yy, 4.45, label, MUTED)
        base.text(c, bold, x + 126, yy, 4.45, value, INK, right=True)
        yy -= 9.2
    base.text(c, bold, x + 7, yy - 1, 5.8, "ЧТО УЛУЧШЕНО", GOOD)
    yy -= 9
    for item in strengths:
        for index, row in enumerate(base.wrap(item, 42)):
            base.text(c, regular, x + 7, yy, 4.15,
                      ("+ " if index == 0 else "  ") + row, "#345f45")
            yy -= 5.0
    yy -= 2
    base.text(c, bold, x + 7, yy, 5.8, "ЧЕСТНЫЕ ОГРАНИЧЕНИЯ", BAD)
    yy -= 8
    for item in compromises:
        for index, row in enumerate(base.wrap(item, 42)):
            base.text(c, regular, x + 7, yy, 4.1,
                      ("- " if index == 0 else "  ") + row, "#7a3029")
            yy -= 5.0


def draw_page(c, regular, bold, variant: str, mode: str):
    page_w, page_h = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK))
    c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, page_w - 16 * mm, page_h - 16 * mm, fill=0, stroke=1)

    if variant == "D+":
        sheet = "D+1 - ЕЖЕДНЕВНО" if mode == "daily" else "D+2 - СОЦИАЛЬНЫЕ ГОСТИ"
    else:
        sheet = "E+1 - ЕЖЕДНЕВНО" if mode == "daily" else "E+2 - УЖИН 6"
    base.text(c, bold, 14, 282, 13.5, f"КУХНЯ-ГОСТИНАЯ | {sheet} | М 1:25")
    base.text(c, regular, 14, 274, 5.1,
              "B01 и проёмы - фактические. Мебель - проектные конверты. Новых стен нет.", MUTED)
    base.draw_room_shell(c, regular, bold, sheet)
    base.draw_route(c, regular, 900)

    if variant == "D+":
        draw_kitchen_dplus(c, regular, bold)
        draw_workstation_dplus(c, regular)
        draw_dplus_sofa_media(c, regular, bold)
        draw_dplus_dining(c, regular, bold)
        draw_dplus_open_zone(c, regular, mode == "social")
    else:
        draw_kitchen_eplus(c, regular, bold)
        old_e.draw_workstation_e(c, regular, bold)
        draw_tv_eplus(c, regular, bold)
        draw_eplus_banquette(c, regular)
        draw_eplus_table(c, regular, bold, mode)
        draw_eplus_open_zone(c, regular, mode == "guest")
    draw_side_panel(c, regular, bold, variant, mode)

    c.setStrokeColor(HexColor(INK))
    c.setLineWidth(0.45 * mm)
    c.line(18 * mm, 61 * mm, 58 * mm, 61 * mm)
    c.line(18 * mm, 59.5 * mm, 18 * mm, 62.5 * mm)
    c.line(58 * mm, 59.5 * mm, 58 * mm, 62.5 * mm)
    base.text(c, bold, 38, 63.0, 5.0, "1000 мм = 40 мм на листе", center=True)

    common_notes = [
        "ФАКТ: B01 5710x3500; D2 слева 200+910 (контроль 915x2150); O1 справа 600+1600+1300.",
        "P0 PASS: защищённые полосы 900 мм D2-O1 проверены численно; мебель и кресла их не пересекают.",
        "СТАТУС: концепция мебели, не рабочий чертёж и не основание для заказа.",
        "ГЕЙТЫ: сторона петель D2, вода, канализация, вентиляция, E-01, отопление и реальные SKU.",
    ]
    if variant == "D+":
        variant_notes = [
            "D+: кухня 2300; стол 1050x850 на 4; диван 1780x800; РМ 1200x600; ТВ 55-65.",
            "ГОСТИ: 4 за столом + 3 на диване + 2 пуфа = до 9 только для общения, не для общего ужина.",
            "ЗАЗОРЫ: 1010 за обеденными стульями; 840 кресло-кухня; 250 над путём; 30 до зоны O1.",
        ]
    else:
        variant_notes = [
            "E+: кухня 2200; стол 1200->1650x800; банкетка 1650x400; РМ 1200x600.",
            "УЖИН 6: 3 на банкетке + 3 на стульях; 550 мм/чел. - компактный, эпизодический режим.",
            "ЗАЗОРЫ: 100 кухня-стулья по x; 350 стол-банкетка; 410 до O1-зоны; кресло РМ 55 над ней.",
        ]
    yy = 51
    for row in common_notes[:2] + variant_notes + common_notes[2:]:
        base.text(c, regular, 18, yy, 4.15, row, MUTED)
        yy -= 5.5
    page_name = ("1" if mode in ("daily",) else "2")
    base.text(c, regular, 404, 14, 4.0,
              f"KLV-001 | {variant} | лист {page_name}/2 | 22.08.2026", MUTED, right=True)
    c.showPage()


def build_plus_source() -> None:
    validate_geometry()
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    regular, bold = base.fonts()
    c = canvas.Canvas(str(PLUS_PDF), pagesize=landscape(A3), pageCompression=1)
    c.setTitle("KLV-001 - варианты D+ и E+")
    c.setAuthor("Codex / KLV-001")
    draw_page(c, regular, bold, "D+", "daily")
    draw_page(c, regular, bold, "D+", "social")
    draw_page(c, regular, bold, "E+", "daily")
    draw_page(c, regular, bold, "E+", "guest")
    c.save()


def merge_release() -> None:
    for path in (SOURCE_AD, SOURCE_E, PLUS_PDF):
        if not path.exists():
            raise FileNotFoundError(path)
    ad = PdfReader(str(SOURCE_AD))
    e = PdfReader(str(SOURCE_E))
    plus = PdfReader(str(PLUS_PDF))
    if (len(ad.pages), len(e.pages), len(plus.pages)) != (4, 2, 4):
        raise AssertionError("Unexpected source page count")

    writer = PdfWriter()
    page_specs = [
        (ad.pages[0], "A - классический баланс"),
        (ad.pages[1], "B - полуостров"),
        (ad.pages[2], "C - круглый стол"),
        (ad.pages[3], "D - семейная банкетка"),
        (plus.pages[0], "D+1 - ежедневно"),
        (plus.pages[1], "D+2 - социальные гости"),
        (e.pages[0], "E1 - ежедневно"),
        (e.pages[1], "E2 - гости"),
        (plus.pages[2], "E+1 - ежедневно"),
        (plus.pages[3], "E+2 - ужин 6"),
    ]
    for page, title in page_specs:
        writer.add_page(page)
        writer.add_outline_item(title, len(writer.pages) - 1)
    writer.add_metadata({
        "/Title": "KLV-001 - все варианты A-E, D+ и E+",
        "/Author": "Codex / KLV-001",
        "/Subject": "Масштабные 2D-варианты кухни-гостиной B01",
    })
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PDF.open("wb") as stream:
        writer.write(stream)


def validate_release() -> None:
    reader = PdfReader(str(OUT_PDF))
    if len(reader.pages) != 10:
        raise AssertionError(f"Expected 10 pages, got {len(reader.pages)}")
    expected_w, expected_h = landscape(A3)
    for index, page in enumerate(reader.pages, start=1):
        width = float(page.mediabox.width)
        height = float(page.mediabox.height)
        if abs(width - expected_w) > 1 or abs(height - expected_h) > 1:
            raise AssertionError(f"Page {index} is not landscape A3: {width}x{height}")
    required = {
        4: ("D+1", "2300x600"),
        5: ("D+2", "СОЦИАЛЬНЫЕ"),
        8: ("E+1", "1200x800"),
        9: ("E+2", "1650x800"),
    }
    for page_index, tokens in required.items():
        extracted = reader.pages[page_index].extract_text() or ""
        for token in tokens:
            if token not in extracted:
                raise AssertionError(f"Page {page_index + 1} missing token {token!r}")


def find_pdftoppm() -> Path:
    found = shutil.which("pdftoppm")
    if found:
        return Path(found)
    bundled = (Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" /
               "dependencies" / "native" / "poppler" / "Library" / "bin" / "pdftoppm.exe")
    if bundled.exists():
        return bundled
    raise FileNotFoundError("pdftoppm not found")


def render_release() -> list[Path]:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    for old in QA_DIR.glob("all-plus-*.png"):
        old.unlink()
    prefix = QA_DIR / "all-plus"
    subprocess.run(
        [str(find_pdftoppm()), "-png", "-r", "160", str(OUT_PDF), str(prefix)],
        check=True,
    )
    pages = sorted(QA_DIR.glob("all-plus-*.png"))
    if len(pages) != 10:
        raise AssertionError(f"Expected 10 rendered pages, got {len(pages)}")
    return pages


def build() -> tuple[Path, list[Path]]:
    build_plus_source()
    merge_release()
    validate_release()
    return OUT_PDF, render_release()


if __name__ == "__main__":
    pdf, previews = build()
    print(pdf)
    for preview in previews:
        print(preview)
