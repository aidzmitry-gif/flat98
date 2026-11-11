"""B01 lighting coordination sheet. Fixture locations are design positions in mm."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from b01_workplace_geometry import (
    CHAIR_PARKED, CHAIR_RADIUS, D2_PARTS, DINING_PARKED, O1_PARTS, OUTPUT, RADIATOR,
    corners, door_points, footprints, load_model, open_sofa, verify, verify_dining_parking,
)
from draw_b01_whole_room_plan import NIGHT_ROUTE, bounds, route_clearance

DEST = OUTPUT / 'B01_освещение_и_управление_v3.png'
FONT_DIR = Path('C:/Windows/Fonts')
SCALE = .13
INK, SUB, WALL = '#263831', '#54655c', '#8d998d'
PAPER, WHITE, FLOOR = '#f3f0e8', '#fffefa', '#faf8f1'
KITCHEN, CEILING, NIGHT, MEDIA, WORK = '#a85a31', '#ac7a28', '#226e73', '#6a567f', '#527241'

# X starts at the entrance wall. The measuring sheet uses S = 5710 - X.
CEILING_POINTS = ((1050, 1500), (1050, 2550), (3470, 1900), (4650, 1250), (4650, 2450))
KITCHEN_STRIP = ((270, 1790), (270, 3240), (1100, 3240))
WORK_STRIP = ((4570, 3270), (5630, 3270))
MEDIA_STRIP = ((4910, 100), (5430, 100))
NIGHT_STRIP = ((2110, 420), (4830, 420))
ENTRY_NIGHT, SILL_NIGHT = (1380, 0), (5710, 525)
CONTROL_ENTRY, CONTROL_DESK = (1120, 0), (4590, 3500)
# Nominal heights above finished floor for the dimensioned coordination issue.
NIGHT_MARKER_Z, NIGHT_STRIP_Z = 240, 80


def main():
    data = load_model()
    verify(data)
    verify_dining_parking(data)
    w, d = data['room']['width'], data['room']['depth']
    day = footprints(data)
    night = {**day, **DINING_PARKED, 'sofa': open_sofa(day['sofa'])}
    o1, d2 = data['terrace'], data['entrance']
    h1, h2 = (w, o1['end']), (0, d2['start'])
    sash = [door_points(h1, part, math.pi / 2, -1) for part in O1_PARTS]
    entry = [door_points(h2, part, math.pi / 2, 1) for part in D2_PARTS]
    clear = route_clearance(data, night, list(map(bounds, entry)), list(map(bounds, sash)),
                            NIGHT_ROUTE, CHAIR_PARKED)
    assert clear >= 370
    assert CEILING_POINTS[2] == tuple((a + b) / 2 for a, b in zip(day['table'][:2], day['table'][2:]))
    assert all(day['media'][0] < x < day['media'][2] and day['media'][1] < y < day['media'][3]
               for x, y in NIGHT_STRIP)
    # A proposed 50 mm-wide flush marker fits on the fixed media-side pier.
    assert SILL_NIGHT[0] == w
    assert day['books'][3] < SILL_NIGHT[1] - 25 < SILL_NIGHT[1] + 25 < o1['start']
    entry_reach = max(math.hypot(max(n1, 0), t1) for _, _, n1, t1 in D2_PARTS)
    assert CONTROL_ENTRY[0] > entry_reach

    image = Image.new('RGB', (1840, 1125), PAPER)
    draw = ImageDraw.Draw(image)

    def text(pos, value, size=22, color=INK, bold=False, anchor='lt'):
        font = ImageFont.truetype(FONT_DIR / ('segoeuib.ttf' if bold else 'segoeui.ttf'), size)
        draw.text(pos, str(value), font=font, fill=color, anchor=anchor)

    def badge(pos, name, color, width=72):
        x, y = pos
        draw.rounded_rectangle((x, y, x + width, y + 27), radius=6, fill=color)
        text((x + width / 2, y + 13), name, 16, 'white', True, 'mm')

    def dashed(points, color, width=3):
        for a, b in zip(points, points[1:]):
            length = math.dist(a, b)
            for start in range(0, math.ceil(length), 17):
                draw.line([(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                           for t in (start / length, min(start + 10, length) / length)],
                          fill=color, width=width)

    text((54, 40), 'B01  /  Освещение и управление', 51, bold=True)
    text((58, 108), 'Кухня-гостиная 5710 × 3500 мм · размещение и группы света', 24, SUB)
    draw.rounded_rectangle((1473, 52, 1786, 96), radius=9, fill='#e2e8dd')
    text((1629, 74), 'ПЛАНИРОВОЧНАЯ СХЕМА', 17, INK, True, 'mm')

    def panel(card_x, sleep):
        draw.rounded_rectangle((card_x, 165, card_x + 850, 776), radius=16, fill=WHITE, outline='#d5dbd1', width=2)
        title = '02  /  Ночной маршрут' if sleep else '01  /  Кухня, обед и работа'
        text((card_x + 26, 191), title, 28, bold=True)
        draw.line((card_x + 26, 238, card_x + 824, 238), fill='#d5dbd1', width=2)
        ox, oy = card_x + 39, 270

        def point(p):
            return ox + p[0] * SCALE, oy + (d - p[1]) * SCALE

        def polygon(vertices, fill, stroke=None, width=2):
            pts = list(map(point, vertices))
            draw.polygon(pts, fill=fill)
            if stroke:
                draw.line([*pts, pts[0]], fill=stroke, width=width)

        def box(rect, fill, stroke=None):
            polygon(corners(rect), fill, stroke)

        def line(vertices, color, width):
            draw.line(list(map(point, vertices)), fill=color, width=width, joint='curve')

        def mark(p, name, color, above=True):
            x, y = point(p)
            draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color, outline=WHITE, width=2)
            text((x, y - 12 if above else y + 11), name, 14, color, True, 'ms' if above else 'mt')

        box((0, 0, w, d), FLOOR)
        for wall in (
            (-160, 0, 0, d2['start']), (-160, d2['end'], 0, d), (0, d, w + 145, d + 85),
            (0, -85, w + 145, 0), (w, 0, w + 145, o1['start']), (w, o1['end'], w + 145, d),
        ):
            box(wall, '#e1e3d9', WALL)
        box((w - 6, o1['start'], w + 57, o1['split']), '#cadcda', NIGHT)
        for leaf in [*sash, *entry]:
            polygon(leaf, '#c0d9d5', NIGHT)

        layout = night if sleep else day
        fills = {'sofa': '#d4dcc4', 'table': '#ead9be', 'desk': '#e6d7bf', 'media': '#d7c6ab',
                 'books': '#cdb697', 'dishwasher': '#d0dfd7', 'fridge': '#dccab0', 'oven': '#dccab0',
                 'chair-1': '#dfb99b', 'chair-2': '#dfb99b'}
        names = {'fridge': 'ХОЛ. 600', 'dishwasher': 'ПММ 600', 'sink': 'МОЙКА', 'hob': 'ВАРКА',
                 'oven': 'ПЕНАЛ', 'desk': 'РАБОЧИЙ СТОЛ', 'media': 'МЕДИАТУМБА',
                 'sofa': 'ДИВАН-КРОВАТЬ' if sleep else 'ДИВАН',
                 'table': 'СТОЛ НА НОЧЬ' if sleep else 'ОБЕДЕННЫЙ СТОЛ'}
        for key, rect in layout.items():
            x0, y0, x1, y1 = rect
            if sleep and key.startswith('chair'):
                rect = (x0, y0, DINING_PARKED['table'][0], y1)
            box(rect, fills.get(key, '#ece1d1'), '#a7aa96')
            if key in names:
                x, y = (x0 + x1) / 2, (y0 + y1) / 2
                if not sleep and key in ('sink', 'dishwasher'):
                    text(point((475, y)), names[key] if key == 'sink' else 'ПММ', 11, SUB, True, 'mm')
                    if key == 'dishwasher':
                        text(point((475, y - 104)), '600', 11, SUB, False, 'mm')
                else:
                    shift = -255 if not sleep and key == 'table' else 0
                    text(point((x, y + shift)), names[key], 13, SUB, True, 'mm')
        box(RADIATOR, '#e2c4b3', '#9d6248')
        if sleep:
            cx, cy = point(CHAIR_PARKED)
            r = CHAIR_RADIUS * SCALE
            draw.arc((cx - r, cy - r, cx + r, cy + r), 22, 158, fill=WORK, width=2)
            route = list(map(point, NIGHT_ROUTE))
            dashed(route, NIGHT, 3)
            x, y = route[-1]
            draw.polygon(((x + 8, y), (x - 7, y - 6), (x - 7, y + 6)), fill=NIGHT)
            line(NIGHT_STRIP, NIGHT, 6)
            text(point((3440, 556)), 'N2', 15, NIGHT, True, 'mm')
            mark(ENTRY_NIGHT, 'N1', NIGHT)
            sx, sy = point(SILL_NIGHT)
            draw.ellipse((sx - 7, sy - 7, sx + 7, sy + 7), fill=NIGHT, outline=WHITE, width=2)
            text((sx + 13, sy - 2), 'N3', 14, NIGHT, True, 'lm')
            text(point((282, 850)), 'D2', 15, NIGHT, True)
            text(point((5740, 1930)), 'O1', 15, NIGHT, True, 'mm')
        else:
            line(KITCHEN_STRIP, KITCHEN, 6)
            line(WORK_STRIP, WORK, 6)
            line(MEDIA_STRIP, MEDIA, 6)
            for i, p in enumerate(CEILING_POINTS, 1):
                mark(p, f'P{i}', CEILING, above=i != 3)
            mark(CONTROL_ENTRY, 'К1', INK, above=False)
            mark(CONTROL_DESK, 'К2', INK)
            text(point((670, 2060)), 'SW01', 14, KITCHEN, True)
            text(point((5150, 3060)), 'DIM02', 14, WORK, True, 'mm')
            text(point((5170, 363)), 'DIM01', 14, MEDIA, True, 'mm')

    panel(54, False)
    panel(936, True)

    groups = (
        ('SW01', 'Столешница кухни', ('Линия под шкафами', 'Варка со светом вытяжки'), KITCHEN),
        ('SW02', 'Потолочный свет', ('Пять точек P1–P5', 'P3 над обеденным столом'), CEILING),
        ('SW03', 'Ночной маршрут', ('N1 вход · N2 под тумбой', 'N3 простенок со стороны медиа'), NIGHT),
        ('DIM01', 'Мягкий фон для кино', ('Скрытый свет внутри', 'книжного стеллажа'), MEDIA),
        ('DIM02', 'Рабочий стол', ('Линия под открытой полкой', 'с регулировкой яркости'), WORK),
    )
    for i, (code, title, desc, color) in enumerate(groups):
        x = 55 + i * 348
        badge((x, 804), code, color)
        text((x, 842), title, 21, INK, True)
        for j, row in enumerate(desc):
            text((x, 872 + j * 25), row, 18, SUB)

    draw.line((55, 944, 1786, 944), fill='#d4dbd1', width=2)
    text((56, 961), 'К1 у входа · SW01, SW02 и DIM01     К2 у стола со стороны дивана · SW03 и DIM02', 20, INK, True)
    text((56, 997), 'Готовка SW01   ·   Обед SW02 + DIM01 20%   ·   Работа DIM02   ·   Кино DIM01 10%   ·   Ночь SW03', 20, SUB)
    text((56, 1028), 'N3 направлен на внутреннюю кромку порога со стороны закрытой створки.', 19, SUB)
    text((56, 1062), 'Точки предложены для согласования. Высоты и светораспределение уточнить после обмеров и выбора приборов.', 19, SUB)
    image.save(DEST)
    print(f'{DEST.name}\nPASS lighting placement, modelled night route clearance radius {clear:.1f} mm')


if __name__ == '__main__':
    main()
