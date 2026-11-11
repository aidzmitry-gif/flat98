# -*- coding: utf-8 -*-
"""KLV-001: scale-accurate two-mode variant E for room B01.

The building shell and protected route are inherited from revision 3.  All
coordinates are millimetres.  Furniture is a project envelope until a real
product and the D2 swing are measured.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import build_kitchen_one_workplace as base


ROOT = Path(__file__).resolve().parents[1]
OUT_PDF = ROOT / "output" / "pdf" / "KLV-001_вариант_E_двухрежимный_М1-25.pdf"
QA_DIR = ROOT / "tmp" / "pdfs" / "klv001_variant_e"

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


def draw_kitchen_e(c, regular, bold):
    """2700 active base run + 710 mm shallow closed storage."""
    modules = [
        (0, 950, "ХОЛ.+ПЕНАЛ"),
        (950, 600, "МОЙКА"),
        (1550, 300, "ЯЩИКИ"),
        (1850, 600, "ВАРОЧН.+ДУХ."),
        (2450, 250, "ДОБОР"),
    ]
    for x, width, label in modules:
        base.model_box(c, x, 2900, width, 600, KITCHEN, "#6e5a34", 0.20)
        base.label_model(c, regular, x + width / 2, 2975, label, 3.6, "#5b4827")
    base.model_box(c, 2700, 3150, 710, 350, "#ead7ae", "#6e5a34", 0.20)
    base.label_model(c, regular, 3055, 3265, "НЕГЛУБ. ХРАНЕНИЕ", 3.2, "#5b4827")
    base.label_model(c, regular, 3055, 3168, "710x350", 3.1, "#5b4827")

    base.model_box(c, 1080, 3050, 340, 250, "#eef3f4", "#60747a", 0.14, 25)
    base.model_line(c, 1250, 3300, 1250, 3370, "#60747a", 0.18)
    for x, y in ((2010, 3100), (2240, 3100), (2010, 3310), (2240, 3310)):
        c.setFillColor(HexColor("#ffffff"))
        c.setStrokeColor(HexColor("#5b4827"))
        c.setLineWidth(0.14 * mm)
        c.circle(base.qx(x) * mm, base.qy(y) * mm, base.p(70) * mm, fill=0, stroke=1)
    base.label_model(c, bold, 1350, 3440, "АКТИВНЫЙ ФРОНТ 2700x600", 3.9, "#6e5a34")
    base.label_model(c, regular, 3055, 3060, "низ не ставить", 3.0, BAD)


def draw_workstation_e(c, regular, bold):
    """Built-in 1200x600 desk; actual chair body remains above O1 route."""
    x, y, w, h = 4510, 2900, 1200, 600
    base.model_box(c, x, y, w, h, WORK, "#4b6d82", 0.24, 35)
    base.model_box(c, x + 290, y + h - 125, 620, 75, "#29333c", "#29333c", 0.10, 10)
    base.model_box(c, x + 430, y + 150, 340, 180, "#f7fafb", "#4b6d82", 0.12, 15)
    for sx in (180, 1020):
        c.setFillColor(HexColor("#4b6d82"))
        c.circle(base.qx(x + sx) * mm, base.qy(y + 230) * mm, base.p(58) * mm, fill=1, stroke=0)
    base.model_line(c, x + 990, y + 315, x + 845, y + 195, "#4b6d82", 0.18)
    c.setFillColor(HexColor("#29333c"))
    c.circle(base.qx(x + 830) * mm, base.qy(y + 182) * mm, base.p(32) * mm, fill=1, stroke=0)
    base.draw_task_chair(c, 5110, 2760, "up")
    base.label_model(c, bold, 5110, 3415, "РМ 1200x600", 3.9, "#355d76")
    base.label_model(c, regular, 5110, 3310, "МИКРОФОН + 2 КОЛОНКИ", 3.0, "#355d76")
    base.model_line(c, 4855, 2505, 5365, 2505, "#4b6d82", 0.20)
    base.label_model(c, regular, 5110, 2470, "55 до границы O1-маршрута", 3.0, BAD)


def draw_vertical_sofa(c, regular):
    """Compact upright sofa used as the upholstered side of the dining group."""
    x, y, w, h = 3410, 1250, 800, 1650
    base.model_box(c, x, y, w, h, LOUNGE, "#665a54", 0.26, 90)
    base.model_box(c, x + w - 150, y + 45, 105, h - 90, "#d7ccc5", "#665a54", 0.14, 45)
    base.model_box(c, x + 65, y + 40, w - 235, 125, "#d7ccc5", "#665a54", 0.14, 45)
    base.model_box(c, x + 65, y + h - 165, w - 235, 125, "#d7ccc5", "#665a54", 0.14, 45)
    inner_y = y + 185
    inner_h = h - 370
    for idx in range(3):
        base.model_box(c, x + 95, inner_y + idx * inner_h / 3, w - 285, inner_h / 3,
                       "#eee7e3", "#8a7d76", 0.12, 42)
    base.model_line(c, x + w - 82, y + 160, x + w - 82, y + h - 160, "#665a54", 0.30)
    base.label_model(c, regular, 3785, 2075, "ДИВАН-БАНКЕТКА", 3.6, "#544943")
    base.label_model(c, regular, 3785, 1965, "1650x800 | 3", 3.5, "#544943")


def draw_tv_wall(c, regular, bold):
    # 75 inch 16:9 screen is approximately 1660 x 930 mm; only its plan depth
    # and wall-span are represented here.
    # The screen is wall-mounted above the floor route, so it is drawn as an
    # overhead dashed element rather than as floor-standing furniture.
    c.setStrokeColor(HexColor("#6d5364"))
    c.setLineWidth(0.24 * mm)
    c.setDash(1.6 * mm, 0.8 * mm)
    c.rect(base.qx(0) * mm, base.qy(1240) * mm,
           base.p(100) * mm, base.p(1660) * mm, fill=0, stroke=1)
    c.setDash()
    base.model_box(c, 100, 1320, 60, 1500, "#29333c", "#29333c", 0.10, 8)
    base.label_model(c, bold, 600, 2815, "ТВ 75\" | ШИРИНА 1660", 3.8, "#624a59")
    base.label_model(c, regular, 600, 2705, "ВЫСОТА ЭКРАНА ≈930", 3.2, "#624a59")
    base.model_line(c, 100, 2070, 3770, 2070, "#6d5364", 0.22, [base.p(75), base.p(50)])
    base.label_model(c, regular, 1850, 2105, "≈3670 до глаз | общий просмотр", 3.1, "#624a59")


def draw_table_daily(c, regular, bold):
    x, y, w, h = 2710, 1250, 700, 1200
    base.model_box(c, x, y, w, h, DINING, "#52684a", 0.24, 45)
    base.model_line(c, x, y + h / 2, x + w, y + h / 2, "#70836a", 0.14)
    base.label_model(c, bold, x + w / 2, y + 665, "СТОЛ DAILY", 3.7, "#405238")
    base.label_model(c, regular, x + w / 2, y + 550, "1200x700", 3.5, "#405238")
    base.label_model(c, regular, x + w / 2, y + 440, "2 + 2 = 4", 3.4, "#405238")
    base.draw_chair(c, 2110, 1300, 600, 525, "right")
    base.draw_chair(c, 2110, 1900, 600, 525, "right")
    base.label_model(c, regular, 3055, 2555, "450 до неглуб. хранения", 3.0, "#ad6800")


def draw_table_guest(c, regular, bold):
    x, y, w, h = 2710, 1250, 700, 1650
    base.model_box(c, x, y, w, h, DINING, "#52684a", 0.26, 45)
    for split in (y + 550, y + 1100):
        base.model_line(c, x, split, x + w, split, "#70836a", 0.14)
    base.label_model(c, bold, x + w / 2, y + 935, "СТОЛ GUEST", 3.7, "#405238")
    base.label_model(c, regular, x + w / 2, y + 820, "1650x700", 3.5, "#405238")
    base.label_model(c, regular, x + w / 2, y + 705, "3 + 3 = 6", 3.4, "#405238")
    for chair_y in (1250, 1800, 2350):
        base.draw_chair(c, 2110, chair_y, 600, 550, "right")
    base.label_model(c, regular, 3055, 2960, "250 до неглуб. хранения", 3.0, BAD)
    base.label_model(c, regular, 3055, 1140, "550 мм/чел. - компактно", 3.0, BAD)


def draw_open_zone(c, regular, guest=False):
    x, y, w, h = 250, 1300, 1760, 1550
    c.setStrokeColor(HexColor(GOOD))
    c.setLineWidth(0.30 * mm)
    c.setDash(2.0 * mm, 1.0 * mm)
    c.rect(base.qx(x) * mm, base.qy(y) * mm, base.p(w) * mm, base.p(h) * mm, fill=0, stroke=1)
    c.setDash()
    label = "ГОСТЕВОЙ / ИГРОВОЙ РЕЗЕРВ" if guest else "СВОБОДНО ДЛЯ РЕБЁНКА / ПИТОМЦЕВ"
    base.label_model(c, regular, x + w / 2, y + h / 2 + 70, label, 3.5, GOOD)
    base.label_model(c, regular, x + w / 2, y + h / 2 - 70, "≈2.7 м² чистого прямоугольника", 3.3, GOOD)


def draw_side_panel(c, regular, bold, mode):
    x, y, w, h = 270, 76, 134, 192
    base.box(c, x, y, w, h, "#fbfcfd", "#34414c", 0.28)
    title = "E1 - ЕЖЕДНЕВНЫЙ РЕЖИМ" if mode == "daily" else "E2 - ГОСТЕВОЙ РЕЖИМ"
    base.text(c, bold, x + 7, y + h - 12, 8.4, title, GOOD)
    rows = (
        [
            ("Стол", "1200x700, 4 места"),
            ("Диван", "1650x800, прямой"),
            ("ТВ", "75\", ось ≈3670"),
            ("Рабочее место", "1200x600"),
            ("Путь D2-O1", "900, свободен"),
            ("Свободный центр", "≈2.7 м²"),
        ]
        if mode == "daily"
        else [
            ("Стол", "1650x700"),
            ("Посадка", "3 диван + 3 стула"),
            ("Ширина на гостя", "550 - компактно"),
            ("Путь D2-O1", "900, свободен"),
            ("Рабочее место", "остаётся на месте"),
            ("Кухня", "активные 2700 доступны"),
        ]
    )
    yy = y + h - 28
    for label, value in rows:
        base.text(c, regular, x + 7, yy, 4.5, label, MUTED)
        base.text(c, bold, x + 126, yy, 4.5, value, INK, right=True)
        yy -= 10

    base.text(c, bold, x + 7, yy - 1, 6.0, "ПОЧЕМУ ЭТО СИЛЬНЕЕ D", GOOD)
    yy -= 10
    strengths = [
        "ТВ развёрнут по длинной оси комнаты",
        "Один стол обслуживает 4 и 6 человек",
        "Диван работает и как мягкая банкетка",
        "Не перекрываются D2, O1 и путь 900",
    ]
    for item in strengths:
        for index, row in enumerate(base.wrap(item, 42)):
            base.text(c, regular, x + 7, yy, 4.25, ("+ " if index == 0 else "  ") + row, "#345f45")
            yy -= 5.2

    yy -= 3
    base.text(c, bold, x + 7, yy, 6.0, "ЧЕСТНЫЕ КОМПРОМИССЫ", BAD)
    yy -= 8
    compromises = [
        "Нужен прямой диван с посадкой 430-470",
        "6 мест - редкий компактный режим",
        "Выдвижение кресла РМ временно касается пути",
        "Крепление ТВ - только после проверки D2",
    ]
    for item in compromises:
        for index, row in enumerate(base.wrap(item, 42)):
            base.text(c, regular, x + 7, yy, 4.2, ("- " if index == 0 else "  ") + row, "#7a3029")
            yy -= 5.2


def draw_page(c, regular, bold, mode):
    page_w, page_h = landscape(A3)
    c.setFillColor(white)
    c.rect(0, 0, page_w, page_h, fill=1, stroke=0)
    c.setStrokeColor(HexColor(INK))
    c.setLineWidth(0.35 * mm)
    c.rect(8 * mm, 8 * mm, page_w - 16 * mm, page_h - 16 * mm, fill=0, stroke=1)
    sheet = "E1 - ЕЖЕДНЕВНО" if mode == "daily" else "E2 - ГОСТИ"
    base.text(c, bold, 14, 282, 14.0, f"КУХНЯ-ГОСТИНАЯ | ВАРИАНТ E | {sheet} | М 1:25")
    base.text(c, regular, 14, 274, 5.2,
              "B01 и проёмы - фактические. Мебель - проектные габариты. Стены и проёмы не меняются.", MUTED)

    base.draw_room_shell(c, regular, bold, sheet)
    base.draw_route(c, regular, 900)
    draw_kitchen_e(c, regular, bold)
    draw_workstation_e(c, regular, bold)
    draw_vertical_sofa(c, regular)
    draw_tv_wall(c, regular, bold)
    draw_open_zone(c, regular, mode == "guest")
    if mode == "daily":
        draw_table_daily(c, regular, bold)
    else:
        draw_table_guest(c, regular, bold)
    draw_side_panel(c, regular, bold, mode)

    # Scale and audit notes.
    c.setStrokeColor(HexColor(INK))
    c.setLineWidth(0.45 * mm)
    c.line(18 * mm, 61 * mm, 58 * mm, 61 * mm)
    c.line(18 * mm, 59.5 * mm, 18 * mm, 62.5 * mm)
    c.line(58 * mm, 59.5 * mm, 58 * mm, 62.5 * mm)
    base.text(c, bold, 38, 63.0, 5.0, "1000 мм = 40 мм на листе", center=True)
    notes = [
        "ФАКТ: B01 5710x3500; D2 слева 200+910 (контроль 915x2150); O1 справа 600+1600+1300.",
        "ПУТЬ: защищённая проектная полоса 900 мм сохранена; это не заявление о соответствии нормам РБ.",
        "E: активная кухня 2700x600; хранение 710x350; стол 1200->1650x700; диван 1650x800; РМ 1200x600.",
        "ГОСТИ: 6 посадок = 3 на прямом диване + 3 на стульях; 550 мм на человека - допустимо лишь эпизодически.",
        "ТВ: панель 75\" приблизительно 1660x930; дистанция до глаз около 3670; проектор требует отдельного расчёта.",
        "ГЕЙТЫ: сторона D2, наличники, вода, вентиляция, E-01, отопление и реальные SKU должны быть промерены до заказа.",
        "РМ: кресло в рабочем положении не входит в O1-маршрут (запас 55); при откате назад пересечение временно возможно.",
    ]
    yy = 51
    for row in notes:
        base.text(c, regular, 18, yy, 4.25, row, MUTED)
        yy -= 5.8
    page_no = 1 if mode == "daily" else 2
    base.text(c, regular, 404, 14, 4.0,
              f"KLV-001 | вариант E | лист {page_no}/2 | 22.08.2026", MUTED, right=True)
    c.showPage()


def find_pdftoppm() -> Path:
    found = shutil.which("pdftoppm")
    if found:
        return Path(found)
    bundled = (Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" /
               "dependencies" / "native" / "poppler" / "Library" / "bin" / "pdftoppm.exe")
    if bundled.exists():
        return bundled
    raise FileNotFoundError("pdftoppm not found")


def render_for_qa() -> list[Path]:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    for old in QA_DIR.glob("variant-e-*.png"):
        old.unlink()
    prefix = QA_DIR / "variant-e"
    subprocess.run(
        [str(find_pdftoppm()), "-png", "-r", "180", str(OUT_PDF), str(prefix)],
        check=True,
    )
    pages = sorted(QA_DIR.glob("variant-e-*.png"))
    if len(pages) != 2:
        raise RuntimeError(f"Expected two rendered pages, got {len(pages)}")
    return pages


def build() -> tuple[Path, list[Path]]:
    validate_geometry()
    regular, bold = base.fonts()
    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT_PDF), pagesize=landscape(A3), pageCompression=1)
    c.setTitle("KLV-001 - вариант E, ежедневный и гостевой режимы")
    c.setAuthor("Codex / KLV-001")
    draw_page(c, regular, bold, "daily")
    draw_page(c, regular, bold, "guest")
    c.save()
    return OUT_PDF, render_for_qa()


def overlaps(a, b) -> bool:
    """Return True only for a positive-area overlap; touching is allowed."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    return max(ax1, bx1) < min(ax2, bx2) and max(ay1, by1) < min(ay2, by2)


def validate_geometry() -> None:
    """Machine-check the fixed shell, protected route and furniture envelopes."""
    route = [
        (0, 350, 5710, 1250),
        (4810, 350, 5710, 2450),
    ]
    d2_guard = (0, 0, 1200, 1300)
    common_floor = {
        "active kitchen": (0, 2900, 2700, 3500),
        "shallow storage": (2700, 3150, 3410, 3500),
        "workstation": (4510, 2900, 5710, 3500),
        "work chair body": (4855, 2505, 5365, 3015),
        "sofa": (3410, 1250, 4210, 2900),
    }
    modes = {
        "daily": {
            "table": (2710, 1250, 3410, 2450),
            "chair 1": (2110, 1300, 2710, 1825),
            "chair 2": (2110, 1900, 2710, 2425),
        },
        "guest": {
            "table": (2710, 1250, 3410, 2900),
            "chair 1": (2110, 1250, 2710, 1800),
            "chair 2": (2110, 1800, 2710, 2350),
            "chair 3": (2110, 2350, 2710, 2900),
        },
    }
    for mode, extras in modes.items():
        objects = {**common_floor, **extras}
        for name, rect in objects.items():
            x1, y1, x2, y2 = rect
            if not (0 <= x1 < x2 <= 5710 and 0 <= y1 < y2 <= 3500):
                raise AssertionError(f"{mode}/{name} is outside B01: {rect}")
            if overlaps(rect, d2_guard):
                raise AssertionError(f"{mode}/{name} enters D2 guard: {rect}")
            for index, protected in enumerate(route, start=1):
                if overlaps(rect, protected):
                    raise AssertionError(f"{mode}/{name} enters route {index}: {rect}")


if __name__ == "__main__":
    pdf, previews = build()
    print(pdf)
    for preview in previews:
        print(preview)
