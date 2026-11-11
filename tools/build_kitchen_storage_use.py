# -*- coding: utf-8 -*-
"""Build KLV-002 storage-first kitchen-living package and merge all variants.

All plan coordinates are millimetres in the clear B01 shell 5710 x 3500.
The furniture is a planning envelope, not an order drawing. The final output
combines the already issued KLV-001 variants with six new KLV-002 sheets.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ALL = ROOT / "output" / "pdf" / "KLV-001_все_варианты_A-E_с_Dplus_Eplus_М1-25.pdf"
TMP_DIR = ROOT / "tmp" / "pdfs" / "klv002_storage_use"
SOURCE_NEW = TMP_DIR / "KLV-002_storage_use_source.pdf"
OUT_PDF = ROOT / "output" / "pdf" / "KLV-001_002_все_варианты_и_StorageFirst_М1-25.pdf"

INK = base.INK
MUTED = base.MUTED
KITCHEN = base.KITCHEN
DINING = base.DINING
LOUNGE = base.LOUNGE
WORK = base.WORK
MEDIA = base.MEDIA
ROUTE = base.ROUTE
GOOD = base.GOOD
BAD = base.BAD
ORANGE = "#ad6800"
BLUE = "#356d8a"
PALE_BLUE = "#eef6fa"
PALE_GREEN = "#eef7f0"
PALE_RED = "#fff2f0"
PALE_ORANGE = "#fff7e8"

ROOM = (0, 0, 5710, 3500)
D2_GUARD = (0, 0, 1200, 1300)
ROUTES = ((0, 350, 5710, 1250), (4810, 350, 5710, 2450))

FIXED = {
    "kitchen_top": (0, 2900, 2700, 3500),
    "kitchen_return": (0, 1300, 600, 2900),
    "desk": (2800, 2800, 4000, 3500),
    "sofa": (1600, 1300, 2900, 1900),
    "dining_chair_1": (4100, 2550, 4500, 3025),
    "dining_chair_2": (4100, 3025, 4500, 3500),
    "dining_table": (4500, 2550, 5300, 3500),
    "dining_bench": (5300, 2550, 5710, 3500),
    "media": (1600, 0, 3400, 300),
}

DYNAMIC_DAILY = {
    "desk_chair_envelope": (2950, 1900, 3850, 2800),
    "fridge_door": (600, 2300, 1200, 2900),
    "dishwasher_door": (600, 2450, 1150, 2900),
    "oven_door": (600, 1300, 1050, 1750),
}

GUEST_ONLY = {
    "folding_chair_1": (3050, 1300, 3450, 1700),
    "folding_chair_2": (3550, 1300, 3950, 1700),
}


@dataclass(frozen=True)
class StorageItem:
    code: str
    item: str
    clear_mm: str
    factor: float
    litres: int
    category: str
    access: str
    status: str


STORAGE = (
    StorageItem("K00", "Угловая база", "600x560x700", 0.50, 118, "Кастрюли / формы", "Неделя", "Проект"),
    StorageItem("K02", "Пенал с духовкой", "600x560x2100", 0.40, 282, "Сухие продукты / техника", "День+редко", "Проект"),
    StorageItem("K03", "База мойки", "600x520x700", 0.25, 55, "Сортировка / расходники", "День", "Оси н/д"),
    StorageItem("K04", "Ящики 300", "300x500x600", 0.75, 68, "Приборы / доски", "День", "Проект"),
    StorageItem("K06", "Ящики подготовки", "700x500x600", 0.75, 158, "Посуда / контейнеры", "День", "Проект"),
    StorageItem("K07", "База под варкой", "450x500x600", 0.45, 61, "Сковороды / масла", "День", "Вент. н/д"),
    StorageItem("U01", "Верх над мойкой", "900x300x900", 0.75, 182, "Посуда / чай / кофе", "День", "Высота н/д"),
    StorageItem("U02", "Верх над подготовкой", "700x300x900", 0.75, 142, "Бакалея / специи", "День", "Высота н/д"),
    StorageItem("T01", "Антресоль над пеналами", "1200x500x350", 0.65, 137, "Редкая техника", "Редко", "Высота н/д"),
    StorageItem("W01", "Шкаф над РМ", "1200x260x600", 0.75, 140, "Документы / микрофоны", "День", "E-01 н/д"),
    StorageItem("W02", "Тумба РМ", "400x500x600", 0.70, 84, "Гарнитура / зарядки", "День", "Проект"),
    StorageItem("M01", "Медиа-тумба", "1800x260x250", 0.75, 88, "Кабели / приставки", "День", "Вентиляция"),
    StorageItem("D01", "Банкетка", "850x350x300", 0.70, 62, "Игры / текстиль", "Неделя", "Проект"),
    StorageItem("F01", "Pet-секция", "350x250x250", 0.75, 16, "Корм / салфетки", "День", "Защелка"),
)


def overlaps(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return max(ax1, bx1) < min(ax2, bx2) and max(ay1, by1) < min(ay2, by2)


def validate_geometry() -> None:
    for group_name, group in (("fixed", FIXED), ("dynamic", DYNAMIC_DAILY), ("guest", GUEST_ONLY)):
        for name, rect in group.items():
            x1, y1, x2, y2 = rect
            if not (0 <= x1 < x2 <= 5710 and 0 <= y1 < y2 <= 3500):
                raise AssertionError(f"{group_name}/{name} outside B01: {rect}")
            if overlaps(rect, D2_GUARD):
                raise AssertionError(f"{group_name}/{name} enters D2 guard: {rect}")
            for index, route in enumerate(ROUTES, start=1):
                if overlaps(rect, route):
                    raise AssertionError(f"{group_name}/{name} enters route {index}: {rect}")

    fixed_names = list(FIXED)
    for index, left in enumerate(fixed_names):
        for right in fixed_names[index + 1 :]:
            if overlaps(FIXED[left], FIXED[right]):
                raise AssertionError(f"fixed overlap {left}/{right}")

    for name, rect in GUEST_ONLY.items():
        for fixed_name, fixed_rect in FIXED.items():
            if overlaps(rect, fixed_rect):
                raise AssertionError(f"guest overlap {name}/{fixed_name}")
        if overlaps(rect, DYNAMIC_DAILY["desk_chair_envelope"]):
            raise AssertionError(f"guest overlap {name}/desk chair")

    assert 2900 - 1900 == 1000
    assert 1600 - 600 == 1000
    assert 1300 - 1110 == 190
    assert 2550 - 2450 == 100
    assert 2800 - 2700 == 100
    assert 4100 - 4000 == 100
    assert 2950 - 1250 == 1700
    assert sum(item.litres for item in STORAGE) == 1593


def wrapped(c, font, x, y, size, value, width, leading=None, color=INK, bullet=None):
    leading = leading or size * 1.28
    rows = base.wrap(value, width)
    for index, row in enumerate(rows):
        prefix = bullet if index == 0 and bullet else ("  " if bullet else "")
        base.text(c, font, x, y, size, prefix + row, color)
        y -= leading
    return y


def page_frame(c, regular, bold, title, subtitle, sheet):
    page_w, page_h = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK))
    c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, page_w - 16 * mm, page_h - 16 * mm, fill=0, stroke=1)
    base.text(c, bold, 14, 282, 13.0, title)
    base.text(c, regular, 14, 274, 5.2, subtitle, MUTED)
    base.text(c, regular, 404, 14, 4.1, f"KLV-002 | revision 1 | лист {sheet}/6 | 23.08.2026", MUTED, right=True)


def model_dashed_rect(c, x, y, w, h, color, label=None, label_y=None, width=0.22):
    c.setStrokeColor(HexColor(color))
    c.setLineWidth(width * mm)
    c.setDash(1.6 * mm, 0.9 * mm)
    c.rect(base.qx(x) * mm, base.qy(y) * mm, base.p(w) * mm, base.p(h) * mm, fill=0, stroke=1)
    c.setDash()
    if label:
        base.label_model(c, base.fonts()[0], x + w / 2, label_y or y + h / 2, label, 3.0, color)


def storage_badge(c, bold, x, y, code, fill="#355d76"):
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor("#ffffff"))
    c.setLineWidth(0.12 * mm)
    c.circle(base.qx(x) * mm, base.qy(y) * mm, base.p(115) * mm, fill=1, stroke=1)
    base.label_model(c, bold, x, y - 35, code, 2.5, "#ffffff")


def draw_d2_uncertainty(c, regular):
    c.setFillColor(HexColor("#fff4e5"))
    c.setStrokeColor(HexColor(ORANGE))
    c.setLineWidth(0.18 * mm)
    c.setDash(1.2 * mm, 0.8 * mm)
    c.rect(base.qx(0) * mm, base.qy(0) * mm, base.p(1200) * mm, base.p(1300) * mm, fill=1, stroke=1)
    c.setFillAlpha(1)
    r = base.p(910)
    # Two possible hinge arcs remain fully inside the conservative guard.
    c.arc((base.qx(0) - r) * mm, (base.qy(200) - r) * mm,
          (base.qx(0) + r) * mm, (base.qy(200) + r) * mm, 0, 90)
    c.arc((base.qx(0) - r) * mm, (base.qy(1110) - r) * mm,
          (base.qx(0) + r) * mm, (base.qy(1110) + r) * mm, 270, 90)
    c.setDash()
    base.label_model(c, regular, 600, 1160, "D2 GUARD 1200x1300", 3.0, ORANGE)


def draw_shell_and_routes(c, regular, bold, mode):
    base.draw_room_shell(c, regular, bold, mode)
    draw_d2_uncertainty(c, regular)
    base.draw_route(c, regular, 900)
    base.label_model(c, regular, 5260, 2385, "100 до мебели", 2.7, ORANGE)


def draw_kitchen(c, regular, bold, show_dynamic=True):
    top_modules = (
        (0, 600, "K00 УГОЛ"),
        (600, 600, "K01 ХОЛ."),
        (1200, 600, "K02 ПЕНАЛ"),
        (1800, 600, "K03 МОЙКА"),
        (2400, 300, "K04 ЯЩ."),
    )
    for x, width, label in top_modules:
        fill = "#e5c98e" if label.startswith(("K01", "K02")) else KITCHEN
        base.model_box(c, x, 2900, width, 600, fill, "#6e5a34", 0.20)
        base.label_model(c, regular, x + width / 2, 2980, label, 3.0, "#5b4827")
    return_modules = (
        (2450, 450, "K05 ПММ 450"),
        (1750, 700, "K06 ПОДГ. 700"),
        (1300, 450, "K07 ВАРКА 450"),
    )
    for y, height, label in return_modules:
        base.model_box(c, 0, y, 600, height, KITCHEN, "#6e5a34", 0.20)
        base.label_model(c, regular, 300, y + height / 2 - 25, label, 2.8, "#5b4827")
    # Sink and hob symbols.
    base.model_box(c, 1930, 3050, 340, 250, "#eef3f4", "#60747a", 0.14, 25)
    for cx, cy in ((165, 1435), (405, 1435), (165, 1635), (405, 1635)):
        c.setStrokeColor(HexColor("#5b4827"))
        c.setLineWidth(0.13 * mm)
        c.circle(base.qx(cx) * mm, base.qy(cy) * mm, base.p(58) * mm, fill=0, stroke=1)
    base.label_model(c, bold, 1350, 3435, "КУХНЯ 2700 + 1600 | 4300 ПО ФРОНТАМ", 3.6, "#6e5a34")

    # Upper cabinets are projected overhead storage, shown dashed.
    model_dashed_rect(c, 1800, 3190, 900, 260, BLUE, "U01 900", 3335)
    model_dashed_rect(c, 50, 1750, 500, 700, BLUE, "U02 700", 2110)
    model_dashed_rect(c, 600, 3190, 1200, 260, BLUE, "T01", 3335)

    # Work aisles are actual clear rectangles, not extra furniture.
    model_dashed_rect(c, 600, 1900, 2100, 1000, GOOD, "РАБОЧИЙ ПРОХОД 1000", 2820)
    model_dashed_rect(c, 600, 1300, 1000, 1600, GOOD, "1000", 1480)

    if show_dynamic:
        model_dashed_rect(c, 600, 2300, 600, 600, ORANGE, "ХОЛ. ОТКР.", 2360)
        model_dashed_rect(c, 600, 2450, 550, 450, ORANGE, "ПММ ОТКР.", 2520)
        model_dashed_rect(c, 600, 1300, 450, 450, ORANGE, "ДУХ. ОТКР.", 1670)


def draw_workstation(c, regular, bold):
    base.model_box(c, 2800, 2800, 1200, 700, WORK, "#4b6d82", 0.24, 35)
    base.model_box(c, 3170, 3270, 460, 70, "#29333c", "#29333c", 0.10, 10)
    base.model_box(c, 3240, 2960, 320, 190, "#f7fafb", "#4b6d82", 0.12, 15)
    for x in (2990, 3810):
        c.setFillColor(HexColor("#4b6d82"))
        c.circle(base.qx(x) * mm, base.qy(2940) * mm, base.p(55) * mm, fill=1, stroke=0)
    base.draw_task_chair(c, 3400, 2350, "up")
    model_dashed_rect(c, 2950, 1900, 900, 900, BLUE, "КРЕСЛО 900", 1970)
    model_dashed_rect(c, 2800, 3240, 1200, 210, BLUE, "W01 ШКАФ", 3370)
    base.label_model(c, bold, 3400, 3160, "РМ 1200x700", 3.6, "#355d76")
    base.label_model(c, regular, 3400, 2875, "2xCAT.6 + питание + USB-C", 2.8, "#355d76")
    storage_badge(c, bold, 3850, 3350, "W")


def draw_compact_sofa(c, regular, bold):
    base.draw_sofa(c, regular, 1600, 1300, 1300, 600, "down")
    base.label_model(c, bold, 2250, 1760, "КОМПАКТ 1300x600 | 2", 2.8, "#544943")
    storage_badge(c, bold, 1700, 1780, "L", "#765c50")


def draw_dining(c, regular, bold):
    base.model_box(c, 5300, 2550, 410, 950, "#d9e5d3", "#52684a", 0.24, 55)
    base.model_line(c, 5300, 3025, 5710, 3025, "#70836a", 0.14)
    base.model_box(c, 4500, 2550, 800, 950, DINING, "#52684a", 0.24, 45)
    base.model_line(c, 4500, 3025, 5300, 3025, "#70836a", 0.14)
    base.draw_chair(c, 4100, 2550, 400, 475, "right")
    base.draw_chair(c, 4100, 3025, 400, 475, "right")
    base.label_model(c, bold, 4900, 3075, "СТОЛ 950x800", 3.3, "#405238")
    base.label_model(c, regular, 4900, 2940, "2 СТУЛА + БАНКЕТКА = 4", 2.8, "#405238")
    base.label_model(c, regular, 5505, 2630, "D01", 2.8, "#405238")
    storage_badge(c, bold, 5525, 3380, "D", "#55704d")


def draw_media(c, regular, bold):
    base.model_box(c, 1600, 0, 1800, 300, MEDIA, "#6d5364", 0.20, 35)
    base.model_box(c, 1700, 45, 1600, 55, "#29333c", "#29333c", 0.10, 8)
    for split in (2200, 2800):
        base.model_line(c, split, 0, split, 300, "#8f7184", 0.12)
    base.label_model(c, bold, 2500, 185, "TV 43-50 + M01", 3.1, "#624a59")
    base.label_model(c, regular, 2500, 90, "микрофоны / кабели / приставки", 2.5, "#624a59")
    base.model_line(c, 2500, 300, 2300, 1450, "#6d5364", 0.18, [base.p(65), base.p(40)])
    base.label_model(c, regular, 2700, 880, "около 1200-1400 до глаз", 2.8, "#624a59")
    base.model_box(c, 3050, 0, 350, 300, "#e7f0e5", "#55704d", 0.16, 25)
    base.label_model(c, regular, 3225, 115, "F01", 2.7, "#405238")
    storage_badge(c, bold, 1680, 150, "M", "#76566b")


def draw_guest_seats(c, regular, bold):
    for index, (x, y) in enumerate(((3050, 1300), (3550, 1300)), start=1):
        base.draw_chair(c, x, y, 400, 400, "up", "#fff0cf")
        base.label_model(c, regular, x + 200, y + 160, f"СКЛ. {index}", 2.7, "#7b5b19")
    base.label_model(c, bold, 3500, 1760, "2 СКЛАДНЫХ МЕСТА ИЗ T01", 2.8, ORANGE)


def draw_plan_side_panel(c, regular, bold, guest=False):
    x, y, w, h = 270, 76, 134, 192
    base.box(c, x, y, w, h, "#fbfcfd", "#34414c", 0.28)
    title = "SF-2 - ГОСТИ / ОБЩЕНИЕ" if guest else "SF-1 - ЕЖЕДНЕВНО"
    base.text(c, bold, x + 7, y + h - 12, 8.2, title, GOOD)
    rows = (
        (("Кухня по фронтам", "4300"), ("Подготовка", "700"), ("Рабочие проходы", "1000"),
         ("РМ", "1200x700"), ("Стол", "950x800 / 4"), ("Соц. посадка", "до 8"),
         ("Хранение", "около 1.59 м3"), ("Путь D2-O1", "900 PASS"))
        if not guest else
        (("За столом", "4"), ("Компакт-диван", "2"), ("Складные стулья", "2"),
         ("Всего социально", "до 8"), ("Ужин", "только 4"), ("Путь D2-O1", "900 PASS"),
         ("O1 до мебели", "100"), ("Перевод режима", "до 3 мин"))
    )
    yy = y + h - 27
    for label, value in rows:
        base.text(c, regular, x + 7, yy, 4.35, label, MUTED)
        base.text(c, bold, x + 126, yy, 4.35, value, INK, right=True)
        yy -= 8.2
    base.text(c, bold, x + 7, yy - 1, 5.8, "КАК ИСПОЛЬЗОВАТЬ", GOOD)
    yy -= 9
    use_items = (
        ("Готовка", "K03 -> K06 -> K07; ПММ у угла"),
        ("Работа", "кресло 900 не входит в кухню"),
        ("Хранение", "ежедневное здесь, сезонное в 8"),
        ("Ребенок", "замки низких ящиков и anti-tip"),
        ("Питомцы", "F01 вне прохода; миски убирать"),
    ) if not guest else (
        ("Прием", "4 стол + 2 диван + 2 складных"),
        ("Сервировка", "K04 и столешница 300"),
        ("Музыка", "колонки на РМ, микрофоны W01"),
        ("Важно", "это не ужин на 6"),
        ("После гостей", "стулья в T01, путь свободен"),
    )
    for label, value in use_items:
        base.text(c, bold, x + 7, yy, 4.15, label, INK)
        yy = wrapped(c, regular, x + 33, yy, 4.05, value, 33, 4.8, MUTED)
        yy -= 1.5
    base.text(c, bold, x + 7, yy, 5.6, "ЧЕСТНЫЕ ОГРАНИЧЕНИЯ", BAD)
    yy -= 8
    limits = (
        "Варочная 450 и ПММ 450 - осознанный компромисс ради хранения и проходов.",
        "Диван 1300x600 компактный; 65-75 дюймов и проектор эта схема не поддерживает.",
        "Вода, вентиляция, E-01, петли D2/O1 и высота шкафов пока не замкнуты.",
    )
    for item in limits:
        yy = wrapped(c, regular, x + 7, yy, 4.0, item, 44, 4.8, "#7a3029", "- ")
        yy -= 1.2


def draw_plan_page(c, regular, bold, guest=False):
    title = "КУХНЯ-ГОСТИНАЯ | STORAGE-FIRST | ГОСТИ" if guest else "КУХНЯ-ГОСТИНАЯ | STORAGE-FIRST | ЕЖЕДНЕВНО"
    subtitle = "М 1:25. B01 и проемы - фактические; мебель, техника и полезные объемы - проектные конверты."
    page_frame(c, regular, bold, title, subtitle, "2" if guest else "1")
    draw_shell_and_routes(c, regular, bold, "SF-G" if guest else "SF-D")
    draw_kitchen(c, regular, bold, show_dynamic=not guest)
    draw_workstation(c, regular, bold)
    draw_compact_sofa(c, regular, bold)
    draw_dining(c, regular, bold)
    draw_media(c, regular, bold)
    if guest:
        draw_guest_seats(c, regular, bold)
    draw_plan_side_panel(c, regular, bold, guest)

    c.setStrokeColor(HexColor(INK))
    c.setLineWidth(0.45 * mm)
    c.line(18 * mm, 61 * mm, 58 * mm, 61 * mm)
    c.line(18 * mm, 59.5 * mm, 18 * mm, 62.5 * mm)
    c.line(58 * mm, 59.5 * mm, 58 * mm, 62.5 * mm)
    base.text(c, bold, 38, 63, 5.0, "1000 мм = 40 мм на листе", center=True)
    notes = (
        "ФАКТ: B01 5710x3500; D2 200+910 (контроль 915x2150); O1 600+1600+1300.",
        "PASS: фиксированная мебель и показанные динамические конверты не входят в D2 guard и путь D2-O1.",
        "PASS: рабочая полоса кухни 1000 по двум фронтам; кресло РМ имеет конверт 900.",
        "КОНЦЕПТ: перед заказом закрыть G1-G6 на листе 6. Ужин на 6 в эту расстановку не заявлен.",
        "ХРАНЕНИЕ: около 1.59 м3 полезного объема без холодильника, допуск ±20 процентов до выбора SKU.",
    )
    yy = 51
    for note in notes:
        base.text(c, regular, 18, yy, 4.35, note, MUTED)
        yy -= 6
    c.showPage()


def elev_box(c, x, y, w, h, fill, stroke="#5b4827", label=None, font=None, size=4.2):
    base.box(c, x, y, w, h, fill, stroke, 0.22)
    if label:
        base.text(c, font, x + w / 2, y + h / 2 - 1.5, size, label, stroke, center=True)


def draw_elevation_page(c, regular, bold):
    page_frame(c, regular, bold, "KLV-002 | КУХНЯ - МОДУЛИ И ВЫСОТЫ",
               "Фасады - проектная схема. Ширины модулей фиксированы в концепте; высоты и инженерные оси не для заказа.", "3")

    # Top-run elevation at 1:20.
    sx, sy, sc = 20, 112, 0.05
    base.text(c, bold, 20, 258, 7.6, "ФАСАД A - ВЕРХНИЙ ФРОНТ 2700 | М 1:20")
    ceiling_low = sy + 2530 * sc
    ceiling_high = sy + 2712 * sc
    c.setStrokeColor(HexColor(BAD)); c.setLineWidth(0.18 * mm); c.setDash(1.8 * mm, 0.8 * mm)
    c.line(sx * mm, ceiling_low * mm, (sx + 2700 * sc) * mm, ceiling_low * mm)
    c.setStrokeColor(HexColor(MUTED))
    c.line(sx * mm, ceiling_high * mm, (sx + 2700 * sc) * mm, ceiling_high * mm)
    c.setDash()
    base.text(c, regular, sx + 138, ceiling_low - 1, 4.1, "локально H=2530", BAD)
    base.text(c, regular, sx + 138, ceiling_high - 1, 4.1, "контрольная H=2712", MUTED)

    widths = ((600, "K00\nУГОЛ"), (600, "K01\nХОЛ."), (600, "K02\nПЕНАЛ"), (600, "K03\nМОЙКА"), (300, "K04\nЯЩ."))
    cursor = sx
    for width, label in widths:
        w = width * sc
        fill = "#e5c98e" if label.startswith(("K01", "K02")) else KITCHEN
        elev_box(c, cursor, sy, w, 900 * sc, fill, label=label.replace("\n", " "), font=regular, size=3.8)
        base.dim_h(c, regular, cursor, cursor + w, sy - 5, str(width))
        cursor += w
    # Upper cabinets and safe project body.
    elev_box(c, sx, sy + 900 * sc, 2700 * sc, 1500 * sc, "#f8edcf", "#6e5a34")
    for split in (600, 1200, 1800, 2400):
        c.setStrokeColor(HexColor("#6e5a34")); c.setLineWidth(0.15 * mm)
        c.line((sx + split * sc) * mm, (sy + 900 * sc) * mm,
               (sx + split * sc) * mm, (sy + 2400 * sc) * mm)
    base.text(c, bold, sx + 67.5, sy + 105, 4.4, "ВЕРХ / АНТРЕСОЛЬ: проект до H=2400", "#6e5a34", center=True)
    base.dim_v(c, regular, sx - 6, sy, sy + 900 * sc, "h900 проект")
    base.dim_v(c, regular, sx - 12, sy, sy + 2400 * sc, "h2400 max")

    # Return elevation.
    rx, ry = 20, 45
    base.text(c, bold, rx, 101, 7.0, "ФАСАД B - ВОЗВРАТ 1600 | М 1:20")
    cursor = rx
    for width, label in ((450, "K05 ПММ"), (700, "K06 ПОДГОТОВКА"), (450, "K07 ВАРКА")):
        w = width * sc
        elev_box(c, cursor, ry, w, 900 * sc, KITCHEN, label=label, font=regular, size=3.7)
        base.dim_h(c, regular, cursor, cursor + w, ry - 5, str(width))
        cursor += w
    c.setStrokeColor(HexColor(BLUE)); c.setLineWidth(0.16 * mm); c.setDash(1.2 * mm, 0.7 * mm)
    c.line((rx + 450 * sc) * mm, 94 * mm, (rx + 1150 * sc) * mm, 94 * mm)
    c.setDash()
    base.text(c, regular, rx + 40, 96, 3.7, "U02 над K06 - высота н/д", BLUE, center=True)
    base.text(c, regular, rx, 34, 4.4, "Непрерывная подготовка 700; варочная 450; ПММ 450.", MUTED)

    # Module schedule.
    tx, ty, tw, th = 185, 42, 218, 218
    base.box(c, tx, ty, tw, th, "#fbfcfd", "#34414c", 0.28)
    base.text(c, bold, tx + 7, ty + th - 12, 8.0, "МОДУЛЬНАЯ ВЕДОМОСТЬ")
    headers = ("ID", "Ширина", "Функция", "Статус")
    cols = (tx + 7, tx + 28, tx + 58, tx + 151)
    yy = ty + th - 25
    for col, header in zip(cols, headers):
        base.text(c, bold, col, yy, 4.3, header, MUTED)
    yy -= 7
    schedule = (
        ("K00", "600", "угол, крупная посуда", "проект"),
        ("K01", "600", "холодильник", "SKU н/д"),
        ("K02", "600", "пенал, духовка, СВЧ", "SKU н/д"),
        ("K03", "600", "мойка + сортировка", "вода н/д"),
        ("K04", "300", "приборы / посадочная", "проект"),
        ("K05", "450", "посудомоечная", "SKU н/д"),
        ("K06", "700", "ящики + подготовка", "проект"),
        ("K07", "450", "3-зонная варка", "вент. н/д"),
        ("U01", "900", "верх над мойкой", "H н/д"),
        ("U02", "700", "верх подготовки", "H н/д"),
        ("T01", "1200", "верх над пеналами", "H н/д"),
    )
    for code, width, function, status in schedule:
        base.text(c, bold, cols[0], yy, 4.2, code, INK)
        base.text(c, regular, cols[1], yy, 4.2, width, INK)
        base.text(c, regular, cols[2], yy, 4.2, function, INK)
        color = BAD if "н/д" in status else GOOD
        base.text(c, regular, cols[3], yy, 4.2, status, color)
        yy -= 7.1

    base.text(c, bold, tx + 7, yy - 1, 5.8, "ПОЧЕМУ НЕ D+/E+")
    yy -= 9
    for item in (
        "2200-2300 мм не вмещают отдельные мойку, ПММ, подготовку, варку и продуктовый пенал.",
        "Блок 'мойка+ПММ 600' из прошлых листов не является реальным модулем и исключен.",
        "Здесь 4300 мм фронтов, отдельные модули и 700 мм непрерывной подготовки.",
    ):
        yy = wrapped(c, regular, tx + 7, yy, 4.25, item, 67, 5.3, MUTED, "- ")
        yy -= 1.2
    c.showPage()


def draw_storage_page(c, regular, bold):
    page_frame(c, regular, bold, "KLV-002 | ВЕДОМОСТЬ ХРАНЕНИЯ",
               "Полезный объем - расчетная внутренняя емкость с коэффициентом наполнения; холодильник и ПММ не считаются.", "4")
    base.text(c, bold, 18, 258, 7.2, "РАСЧЕТНАЯ ПОЛЕЗНАЯ ЕМКОСТЬ: 1593 Л = 1.59 М3 | ДОПУСК ±20 ПРОЦЕНТОВ")
    base.text(c, regular, 18, 250, 4.6,
              "Если верхние шкафы U01/U02/T01 не проходят по вентиляции или высоте, емкость падает на 461 л до 1.13 м3.", BAD)

    tx, top = 18, 238
    widths = (18, 54, 38, 22, 28, 70, 35, 45)
    headers = ("ID", "Элемент", "Чистый конверт", "k", "Литры", "Назначение", "Доступ", "Статус")
    x_positions = [tx]
    for width in widths[:-1]:
        x_positions.append(x_positions[-1] + width)
    row_h = 10.5
    total_w = sum(widths)
    base.box(c, tx, top - row_h, total_w, row_h, "#eaf0f4", "#73808b", 0.20)
    for x, header in zip(x_positions, headers):
        base.text(c, bold, x + 2, top - 7, 4.0, header, INK)
    yy = top - row_h
    for index, item in enumerate(STORAGE):
        fill = "#ffffff" if index % 2 == 0 else "#f7f9fa"
        base.box(c, tx, yy - row_h, total_w, row_h, fill, "#c5cdd3", 0.12)
        values = (item.code, item.item, item.clear_mm, f"{item.factor:.2f}", str(item.litres), item.category, item.access, item.status)
        colors = (INK, INK, MUTED, MUTED, GOOD, INK, MUTED, BAD if "н/д" in item.status else INK)
        for x, value, color in zip(x_positions, values, colors):
            base.text(c, bold if value == str(item.litres) else regular, x + 2, yy - 7, 3.85, value, color)
        yy -= row_h
    base.box(c, tx, yy - 11, total_w, 11, PALE_GREEN, GOOD, 0.22)
    base.text(c, bold, tx + 2, yy - 7.3, 4.8, "ИТОГО БЕЗ ХОЛОДИЛЬНИКА И ПММ")
    base.text(c, bold, tx + total_w - 3, yy - 7.3, 5.0, "1593 Л", GOOD, right=True)

    panel_y, panel_h = 24, 48
    panels = (
        (18, 120, "ЕЖЕДНЕВНО 400-1600", "K03/K04/K06/K07/U01/W02/M01/F01: посуда, продукты, зарядки, корм.", PALE_GREEN, GOOD),
        (146, 120, "РЕДКО / ВЫСОКО", "K02/T01/U02: редкая техника и запасы. Нужна стремянка; ничего тяжелого над рабочим местом.", PALE_ORANGE, ORANGE),
        (274, 128, "НЕ ХРАНИТЬ ЗДЕСЬ", "Сезонное, крупная уборочная техника и архив детских вещей - гардеробная 8. Химия и лекарства - запираемый верх.", PALE_RED, BAD),
    )
    for x, w, title, body, fill, stroke in panels:
        base.box(c, x, panel_y, w, panel_h, fill, stroke, 0.24, 2)
        base.text(c, bold, x + 6, panel_y + panel_h - 10, 5.5, title, stroke)
        wrapped(c, regular, x + 6, panel_y + panel_h - 20, 4.2, body, int(w / 2.8), 5.3, INK)
    c.showPage()


def mini_plan(c, regular, bold, x, y, w, h, title, active, notes):
    base.box(c, x, y, w, h, "#ffffff", "#87939d", 0.22, 2)
    base.text(c, bold, x + 5, y + h - 9, 5.7, title, INK)
    px, py, pw, ph = x + 6, y + 18, w - 12, h - 34
    scale = min(pw / 5710, ph / 3500)
    ox = px + (pw - 5710 * scale) / 2
    oy = py + (ph - 3500 * scale) / 2

    def rect(model, fill, stroke, width=0.15, dash=False):
        x1, y1, x2, y2 = model
        c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor(stroke)); c.setLineWidth(width * mm)
        if dash: c.setDash(1.2 * mm, 0.7 * mm)
        c.rect((ox + x1 * scale) * mm, (oy + y1 * scale) * mm,
               ((x2 - x1) * scale) * mm, ((y2 - y1) * scale) * mm, fill=1, stroke=1)
        c.setDash()

    rect(ROOM, "#ffffff", "#111827", 0.30)
    rect(ROUTES[0], "#fff8e8", ROUTE, 0.12, True)
    rect(ROUTES[1], "#fff8e8", ROUTE, 0.12, True)
    rect(D2_GUARD, "#fff4e5", ORANGE, 0.12, True)
    color_map = {
        "kitchen": (KITCHEN, "#6e5a34"), "work": (WORK, BLUE), "sofa": (LOUNGE, "#665a54"),
        "dining": (DINING, "#52684a"), "media": (MEDIA, "#6d5364"), "guest": ("#fff0cf", ORANGE),
    }
    rect(FIXED["kitchen_top"], *(color_map["kitchen"] if "kitchen" in active else ("#f3f4f5", "#9aa3aa")))
    rect(FIXED["kitchen_return"], *(color_map["kitchen"] if "kitchen" in active else ("#f3f4f5", "#9aa3aa")))
    rect(FIXED["desk"], *(color_map["work"] if "work" in active else ("#f3f4f5", "#9aa3aa")))
    rect(DYNAMIC_DAILY["desk_chair_envelope"], "#ffffff", BLUE if "work" in active else "#aab2b8", 0.12, True)
    rect(FIXED["sofa"], *(color_map["sofa"] if "sofa" in active else ("#f3f4f5", "#9aa3aa")))
    for key in ("dining_chair_1", "dining_chair_2", "dining_table", "dining_bench"):
        rect(FIXED[key], *(color_map["dining"] if "dining" in active else ("#f3f4f5", "#9aa3aa")))
    rect(FIXED["media"], *(color_map["media"] if "media" in active else ("#f3f4f5", "#9aa3aa")))
    if "guest" in active:
        for model in GUEST_ONLY.values(): rect(model, *color_map["guest"])
    base.text(c, regular, x + 5, y + 7, 4.0, notes, MUTED)


def draw_scenarios_page(c, regular, bold):
    page_frame(c, regular, bold, "KLV-002 | СЦЕНАРИИ ОДНОВРЕМЕННОГО ИСПОЛЬЗОВАНИЯ",
               "Мини-схемы повторяют те же координаты B01. Цветом выделены активные зоны; маршрут всегда остается пустым.", "5")
    mini_plan(c, regular, bold, 18, 151, 190, 105, "A. ГОТОВКА + РАБОТА", {"kitchen", "work"},
              "PASS: два кухонных прохода 1000; кресло 900 отдельно.")
    mini_plan(c, regular, bold, 212, 151, 190, 105, "B. СЕМЕЙНЫЙ УЖИН 4", {"kitchen", "dining"},
              "PASS: кухня и стол не пересекаются; O1 имеет резерв 100.")
    mini_plan(c, regular, bold, 18, 34, 190, 105, "C. ГОСТИ / ОБЩЕНИЕ ДО 8", {"sofa", "dining", "guest", "media"},
              "PASS: 4 стол + 2 диван + 2 складных; это не ужин 6.")
    mini_plan(c, regular, bold, 212, 34, 190, 105, "D. УБОРКА + ПИТОМЦЫ", {"media"},
              "PASS: F01 у медиа; робот и пылесос остаются в гардеробной 8.")
    c.showPage()


def draw_acceptance_page(c, regular, bold):
    page_frame(c, regular, bold, "KLV-002 | ПРИЕМКА, РИСКИ И СЛЕДУЮЩИЕ ШАГИ",
               "Этот лист отделяет проверенное от проектного и не дает использовать концепт как чертеж заказа.", "6")
    base.text(c, bold, 18, 258, 7.0, "ПРОВЕРЯЕМАЯ МАТРИЦА")
    rows = (
        ("B01 / D2 / O1", "5710x3500; 915 контроль; O1 1600", "PASS", GOOD),
        ("Путь D2-O1", "900 во всех показанных режимах", "PASS", GOOD),
        ("D2 guard", "1200x1300; обе возможные дуги внутри", "PASS*", ORANGE),
        ("Кухонные проходы", "1000 по верхнему и левому фронту", "PASS", GOOD),
        ("РМ", "1200x700; конверт кресла 900", "PASS", GOOD),
        ("ПММ / духовка / холодильник", "динамика показана, мебель не пересекает", "PASS*", ORANGE),
        ("Семейный стол", "950x800; 4 места компактно", "PASS", GOOD),
        ("Прием гостей", "до 8 социальных мест", "PASS", GOOD),
        ("Ужин 6", "без блокировки пути / кухни не помещается", "НЕ ЗАЯВЛЕН", BAD),
        ("Хранение", "1593 л ±20 процентов; без холодильника", "ПРОЕКТ", ORANGE),
        ("TV", "43-50; около 1200-1400 до глаз", "ПОДБОР SKU", ORANGE),
        ("65-75 / проектор", "требует другой медиа-компоновки", "FAIL ЗДЕСЬ", BAD),
    )
    tx, top, row_h = 18, 247, 11
    widths = (62, 210, 72)
    for index, (test, evidence, result, color) in enumerate(rows):
        yy = top - index * row_h
        fill = "#ffffff" if index % 2 == 0 else "#f7f9fa"
        base.box(c, tx, yy - row_h, sum(widths), row_h, fill, "#c5cdd3", 0.12)
        base.text(c, bold, tx + 3, yy - 7.2, 4.2, test, INK)
        base.text(c, regular, tx + widths[0] + 3, yy - 7.2, 4.2, evidence, MUTED)
        base.text(c, bold, tx + widths[0] + widths[1] + 3, yy - 7.2, 4.2, result, color)

    base.text(c, bold, 18, 102, 7.0, "ОТКРЫТЫЕ ВОРОТА ДО ЗАКАЗА")
    gates = (
        ("G1", "Вода / канализация", "две оси, диаметры, h центра"),
        ("G2", "Вентиляция / вытяжка", "ось, сечение, маршрут воздуховода"),
        ("G3", "E-01", "две привязки и высота розеток"),
        ("G4", "D2 и O1", "петли, профиль, фактическая дуга"),
        ("G5", "Потолок", "граница локального H=2530 и все 5 точек"),
        ("G6", "SKU", "реальные габариты и открывание техники/мебели"),
    )
    for index, (code, subject, close) in enumerate(gates):
        col = index % 3
        row = index // 3
        x = 18 + col * 128
        y = 63 - row * 39
        base.box(c, x, y, 120, 32, PALE_ORANGE, ORANGE, 0.22, 2)
        base.text(c, bold, x + 6, y + 21, 5.4, f"{code} - {subject}", ORANGE)
        wrapped(c, regular, x + 6, y + 12, 4.0, close, 36, 4.8, INK)

    base.text(c, bold, 18, 13, 4.6,
              "РЕШЕНИЕ: утвердить геометрию SF как базу только после G1-G5; затем подобрать SKU и повторить динамическую проверку G6.", GOOD)
    c.showPage()


def build_new_pdf() -> Path:
    regular, bold = base.fonts()
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(SOURCE_NEW), pagesize=landscape(A3), pageCompression=1)
    c.setTitle("KLV-002 - storage-first kitchen-living package")
    c.setAuthor("Codex / KLV-002")
    draw_plan_page(c, regular, bold, guest=False)
    draw_plan_page(c, regular, bold, guest=True)
    draw_elevation_page(c, regular, bold)
    draw_storage_page(c, regular, bold)
    draw_scenarios_page(c, regular, bold)
    draw_acceptance_page(c, regular, bold)
    c.save()
    return SOURCE_NEW


def merge_all(new_pdf: Path) -> Path:
    if not SOURCE_ALL.exists():
        raise FileNotFoundError(f"Missing issued KLV-001 source: {SOURCE_ALL}")
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    for source in (SOURCE_ALL, new_pdf):
        reader = PdfReader(str(source))
        for page in reader.pages:
            writer.add_page(page)
    writer.add_metadata({
        "/Title": "KLV-001/002 - all kitchen-living variants and storage-first recommendation",
        "/Author": "Codex / apartment project",
        "/Subject": "Scale layouts, storage map, scenarios and acceptance gates",
    })
    with OUT_PDF.open("wb") as stream:
        writer.write(stream)
    return OUT_PDF


def main() -> None:
    validate_geometry()
    source = build_new_pdf()
    output = merge_all(source)
    reader = PdfReader(str(output))
    if len(reader.pages) != 16:
        raise AssertionError(f"Expected 16 pages, got {len(reader.pages)}")
    print(output)
    print(f"pages={len(reader.pages)} storage_l={sum(item.litres for item in STORAGE)}")


if __name__ == "__main__":
    main()
