"""Day and night B01 circulation plans from the same millimetre model."""
import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from b01_workplace_geometry import (
    CHAIR_PARKED, CHAIR_RADIUS, CHAIR_TRAVEL, CHAIR_WORK_Y, CHAIR_X, D2_PARTS, DINING_PARKED, DOMO_OPEN_DEPTH,
    DOMO_SLEEP_LENGTH, DOMO_SLEEP_WIDTH, O1_PARTS, OUTPUT, RADIATOR, RADIATOR_HEIGHT, corners,
    door_points, footprints, load_model, open_sofa, rect_distance, rect_gap, verify,
    verify_chair_parking, verify_dining_parking,
)

DEST = OUTPUT / 'B01_план_проходов_с_радиатором_v1.png'
NIGHT_DEST = OUTPUT / 'B01_ночной_план_проходов_Domo_PRO_180_v1.png'
PARKED_DEST = OUTPUT / 'B01_ночной_план_кресло_под_столом_v1.png'
DINING_DEST = OUTPUT / 'B01_ночная_расстановка_обеденный_стол_v1.png'
FONTS = Path('C:/Windows/Fonts')
INK, SUB = '#263933', '#52645d'
TEAL, OLIVE, CLAY = '#296e70', '#5a714d', '#8c4f34'
PAPER, FLOOR, WALL = '#f4f2ec', '#fcfaf4', '#8a9489'
SCALE = .192
ORIGIN = (99, 218)
ROUTE = (
    (-135, 675), (1480, 675), (2000, 775), (4530, 775), (5010, 1000),
    (5250, 1250), (5310, 1570), (5380, 1780), (5920, 1780),
)
NIGHT_ROUTE = (
    (-135, 675), (1480, 675), (2000, 860), (4682, 860), (4970, 1080),
    (5150, 1360), (5320, 1640), (5380, 1780), (5920, 1780),
)
DESK_APPROACH = ((4682, 860), (4682, 1990))
DESK_ROUTE_WITHOUT_CHAIR = ((4682, 860), (4682, 2470), (5150, 2510), (5260, 2665))
PARKED_DESK_ROUTE = ((4682.5, 860), (4682.5, 2490), (5350, 2490), (5350, 2660))


def route_clearance(data, rects, entry, sash, route, chair_center):
    w, d = data['room']['width'], data['room']['depth']
    a, b = data['entrance']['start'], data['entrance']['end']
    o1 = data['terrace']
    # Outer profile of the closed right leaf and the 36 mm fixed jamb at the open end.
    obstacles = [
        *rects.values(), RADIATOR, *entry, *sash,
        (-160, 0, 0, a), (-160, b, 0, d),
        (w, 0, w + 145, o1['split']), (w, o1['end'] - 36, w + 145, d),
    ]
    minimum = math.inf
    for start, end in zip(route, route[1:]):
        if start[0] == end[0] or start[1] == end[1]:
            segment = bounds((start, end))
            minimum = min(minimum, segment[1], d - segment[3], *(rect_gap(segment, r) for r in obstacles))
            if chair_center is not None:
                minimum = min(minimum, rect_distance(chair_center, segment) - CHAIR_RADIUS)
            continue
        steps = max(1, math.ceil(math.dist(start, end) / 10))
        for index in range(steps + 1):
            t = index / steps
            p = (start[0] + t * (end[0] - start[0]), start[1] + t * (end[1] - start[1]))
            # The gap can fall by at most 5 mm between adjacent samples.
            minimum = min(minimum, p[1] - 5, d - p[1] - 5, *(rect_distance(p, r) - 5 for r in obstacles))
            if chair_center is not None:
                minimum = min(minimum, math.dist(p, chair_center) - CHAIR_RADIUS - 5)
    return minimum


def bounds(points):
    x, y = zip(*points)
    return min(x), min(y), max(x), max(y)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--night', action='store_true')
    parser.add_argument('--park-chair', action='store_true')
    parser.add_argument('--store-dining', action='store_true')
    options = parser.parse_args()
    night, parked, stored = options.night, options.park_chair, options.store_dining
    if parked and not night:
        parser.error('--park-chair requires --night')
    if stored and not parked:
        parser.error('--store-dining requires --night and --park-chair')
    data = load_model()
    sizes = verify(data)
    rects = footprints(data)
    w, d = data['room']['width'], data['room']['depth']
    o1, d2 = data['terrace'], data['entrance']
    h1, h2 = (w, o1['end']), (0, d2['start'])
    sash = [door_points(h1, part, math.pi / 2, -1) for part in O1_PARTS]
    entry = [door_points(h2, part, math.pi / 2, 1) for part in D2_PARTS]
    sash_bounds, entry_bounds = list(map(bounds, sash)), list(map(bounds, entry))
    chair_center = CHAIR_PARKED if parked else (CHAIR_X, CHAIR_WORK_Y - CHAIR_TRAVEL)
    tip_x = w - (o1['end'] - o1['split'])
    route_mm = NIGHT_ROUTE if night else ROUTE
    if night:
        if stored:
            dining = verify_dining_parking(data)
            rects.update(DINING_PARKED)
        else:
            for item in ('table', 'chair-1', 'chair-2'):
                del rects[item]
        bed = rects['sofa'] = open_sofa(rects['sofa'])
        foot_gap = bed[1] - rects['media'][3]
        desk_gap = tip_x - bed[2]
        aperture = o1['end'] - 36 - o1['split']
        assert (foot_gap, desk_gap, aperture) == (820, 455, 764)
        if parked:
            parking = verify_chair_parking(data)
            desk_clear = route_clearance(data, rects, entry_bounds, sash_bounds, PARKED_DESK_ROUTE, chair_center)
            assert math.isclose(2 * desk_clear, desk_gap)
        else:
            chair_to_leaf = min(rect_distance(chair_center, r) for r in sash_bounds) - CHAIR_RADIUS
            chair_to_bed = rect_distance(chair_center, bed) - CHAIR_RADIUS
            assert chair_to_bed == 35 and 36 < chair_to_leaf < 38
            assert route_clearance(data, rects, entry_bounds, sash_bounds, DESK_ROUTE_WITHOUT_CHAIR, None) >= 220
    else:
        chair_gap = rects['chair-1'][1] - rects['media'][3]
        table_gap = tip_x - rects['table'][2]
        assert (chair_gap, table_gap) == (650, 740)
    clear = route_clearance(data, rects, entry_bounds, sash_bounds, route_mm, chair_center)
    assert clear >= (370 if night else 300), clear

    image = Image.new('RGB', (1750, 1010), PAPER)
    draw = ImageDraw.Draw(image)

    def point(p):
        return (ORIGIN[0] + p[0] * SCALE, ORIGIN[1] + (d - p[1]) * SCALE)

    def label(p, value, size=21, color=INK, bold=False, anchor='lt'):
        font = ImageFont.truetype(FONTS / ('segoeuib.ttf' if bold else 'segoeui.ttf'), size)
        draw.text(p, str(value), fill=color, font=font, anchor=anchor)

    def poly(vertices, fill, stroke=None, width=2):
        vertices = list(map(point, vertices))
        draw.polygon(vertices, fill=fill)
        if stroke:
            draw.line([*vertices, vertices[0]], fill=stroke, width=width, joint='curve')

    def box(rect, fill, stroke=None):
        poly(corners(rect), fill, stroke)

    def dimension(p0, p1, value, color=SUB, label_y=0):
        a, b = point(p0), point(p1)
        horizontal = abs(a[1] - b[1]) < 1
        draw.line((a, b), fill=color, width=2)
        for x, y in (a, b):
            ends = (x, y - 6, x, y + 6) if horizontal else (x - 6, y, x + 6, y)
            draw.line(ends, fill=color, width=2)
        cx, cy = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2 + label_y
        width = 62 if len(str(value)) > 3 else 47
        draw.rounded_rectangle((cx - width / 2, cy - 13, cx + width / 2, cy + 13), 5, fill=PAPER)
        label((cx, cy - 1), value, 18, color, True, 'mm')

    def dashed(points, color, width=3, dash=11, space=7):
        for start, end in zip(points, points[1:]):
            length = math.dist(start, end)
            for k in range(0, math.ceil(length), dash + space):
                interval = (k / length, min(length, k + dash) / length)
                draw.line([(start[0] + (end[0] - start[0]) * t, start[1] + (end[1] - start[1]) * t)
                           for t in interval], fill=color, width=width)

    def legend(x, y, number, title, rows, color):
        draw.rounded_rectangle((x, y, x + 33, y + 25), 6, fill=color)
        label((x + 16, y + 12), number, 15, 'white', True, 'mm')
        label((x + 45, y + 2), title, 22, INK, True)
        for index, line in enumerate(rows):
            label((x, y + 39 + 29 * index), line, 20, SUB)

    label((56, 41), 'B01  /  Кухня-гостиная целиком', 48, bold=True)
    subtitle, dest = 'Дневная расстановка', DEST
    if stored:
        subtitle, dest = 'Режим сна · обеденный стол убран к кухне', DINING_DEST
    elif parked:
        subtitle, dest = 'Режим сна · кресло задвинуто под стол', PARKED_DEST
    elif night:
        subtitle, dest = 'Режим сна · обеденный стол и стулья убраны', NIGHT_DEST
    label((59, 107), f'{subtitle} · вид сверху · размеры в миллиметрах', 25, SUB)
    draw.line((57, 151, 1694, 151), fill='#d7dbd0', width=2)

    box((0, 0, w, d), FLOOR)
    for wall in (
        (-160, 0, 0, d2['start']), (-160, d2['end'], 0, d),
        (0, d, w + 145, d + 85), (0, -85, w + 145, 0),
        (w, 0, w + 145, o1['start']), (w, o1['end'], w + 145, d),
    ):
        box(wall, '#dbded4', WALL)

    for hinge, radius, sign in ((h1, o1['end'] - o1['split'], -1), (h2, D2_PARTS[0][3], 1)):
        arc = [
            point((hinge[0] + sign * radius * math.sin(a), hinge[1] + sign * radius * math.cos(a)))
            for a in (math.radians(v) for v in range(0, 91, 5))
        ]
        draw.line(arc, fill='#a0bdb6', width=2)
    box((w - 2, o1['start'], w + 61, o1['split']), '#b7d9d5', TEAL)
    for outline in [*sash, *entry]:
        poly(outline, '#b7d9d5', TEAL)

    fills = {
        'fridge': '#d8c2a6', 'dishwasher': '#c7dbd2', 'sink': '#e8dfcf',
        'sofa': '#cbd4ba', 'desk': '#ead8bd', 'table': '#ede1cf', 'chair-1': '#ddb295',
        'chair-2': '#ddb295', 'media': '#d9c4a8', 'books': '#cdb398', 'oven': '#d8c2a6',
    }
    texts = {
        'corner': ('УГОЛ', '600'), 'prep': ('500',), 'hob': ('ВАРКА', '500'), 'pullout': ('200',),
        'oven': ('ПЕНАЛ', '600'), 'fridge': ('ХОЛОД.', '600'), 'dishwasher': ('ПММ', '600'),
        'sink': ('МОЙКА', '570'), 'sofa': ('ДИВАН DOMO PRO 180', '1970 × 1200'),
        'desk': ('РАБОЧИЙ СТОЛ', '1200 × 600'), 'table': ('ОБЕДЕННЫЙ СТОЛ', '1400 × 800'),
        'media': ('МЕДИАТУМБА · 2800 × 450',), 'books': ('СТЕЛЛАЖ', '600'),
    }
    if night:
        texts['sofa'] = ('ASKONA DOMO PRO 180', f'1970 × {DOMO_OPEN_DEPTH}', 'габарит в разложенном виде')
    if stored:
        texts['table'] = ('СТОЛ НА НОЧЬ', '1400 × 800')
    for key, rect in rects.items():
        if stored and key in ('chair-1', 'chair-2'):
            x0, y0, x1, y1 = rect
            edge = DINING_PARKED['table'][0]
            box((x0, y0, edge, y1), fills[key], '#9b9e8b')
            hidden = corners((edge, y0, x1, y1))
            dashed(list(map(point, [*hidden, hidden[0]])), '#ac826b', width=1, dash=6, space=4)
            continue
        box(rect, fills.get(key, '#eee4d6'), '#9b9e8b')
        x0, y0, x1, y1 = rect
        center = point(((x0 + x1) / 2, (y0 + y1) / 2))
        if parked and key == 'desk':
            center = (center[0], center[1] - 34)
        if night and key == 'sofa':
            mid_x = (x0 + x1) / 2
            bed_left, bed_right = mid_x - DOMO_SLEEP_WIDTH / 2, mid_x + DOMO_SLEEP_WIDTH / 2
            head = y0 + DOMO_SLEEP_LENGTH
            box((bed_left, y0, bed_right, head), '#eae2d0', '#9b9e8b')
            for pillow_center in (mid_x - 450, mid_x + 450):
                box((pillow_center - 315, head - 455, pillow_center + 315, head - 64), '#f6eddb', '#c5b69c')
        names = texts.get(key, ())
        for index, name in enumerate(names):
            label((center[0], center[1] + (index - (len(names) - 1) / 2) * 20),
                  name, 18 if key in ('sofa', 'desk', 'table', 'media') else 14, INK, index == 0, 'mm')

    box(RADIATOR, '#e3c3b3', CLAY)
    cx, cy = point(chair_center)
    radius = CHAIR_RADIUS * SCALE
    circle = (cx - radius, cy - radius, cx + radius, cy + radius)
    if parked:
        angle = math.degrees(math.asin((chair_center[1] - rects['desk'][1]) / CHAIR_RADIUS))
        draw.arc(circle, angle, 180 - angle, fill=OLIVE, width=3)
        for start, end in ((0, angle), (180 - angle, 360)):
            for theta in range(math.ceil(start), math.ceil(end), 21):
                draw.arc(circle, theta, min(theta + 12, end), fill=OLIVE, width=2)
        label((cx, cy + 35), 'Ø520', 16, OLIVE, True, 'mm')
    else:
        draw.ellipse(circle, fill='#e0e7d5', outline=OLIVE, width=3)
        label((cx, cy), 'Ø520', 17, OLIVE, True, 'mm')

    route = list(map(point, route_mm))
    dashed(route, TEAL)
    end_x, end_y = route[-1]
    draw.polygon(((end_x + 8, end_y), (end_x - 6, end_y - 7), (end_x - 6, end_y + 7)), fill=TEAL)
    label(point((215, 825)), 'ВХОД D2', 16, TEAL, True)
    label((end_x, end_y - 27), 'O1', 18, TEAL, True, 'mt')
    label(point((w - 25, 1035)), 'Правая закрыта', 15, TEAL, False, 'rm')
    label(point((5460, 2080)), 'Левая открыта', 15, TEAL, True, 'mm')

    dimension((0, d + 164), (w, d + 164), w)
    dimension((-245, 0), (-245, d), d)
    if night:
        approach = list(map(point, PARKED_DESK_ROUTE if parked else DESK_APPROACH))
        dashed(approach, CLAY)
        x, y = approach[-1]
        if parked:
            draw.polygon(((x, y - 8), (x - 6, y + 5), (x + 6, y + 5)), fill=CLAY)
        else:
            draw.line((x - 8, y, x + 8, y), fill=CLAY, width=3)
        dimension((3130, rects['media'][3]), (3130, bed[1]), foot_gap, TEAL)
        dimension((bed[2], h1[1]), (tip_x, h1[1]), desk_gap, CLAY, label_y=21)
        if stored:
            dimension((rects['dishwasher'][2], 1760), (rects['chair-2'][0], 1760), dining['aisle'], OLIVE)
    else:
        dimension((3130, rects['media'][3]), (3130, rects['chair-1'][1]), chair_gap, TEAL)
        dimension((rects['table'][2], h1[1]), (tip_x, h1[1]), table_gap, CLAY, label_y=21)

    draw.rounded_rectangle((1277, 189, 1694, 881), 18, fill='#fffefa', outline='#d7dbd0', width=2)
    label((1307, 224), 'Проходы и рабочая зона', 29, INK, True)
    if night:
        legend(1307, 298, '01', 'Путь на мансарду',
               [f'{foot_gap} мм от изножья до медиатумбы.',
                f'Около {round(aperture, -1)} мм в проёме по модели.',
                'Левая створка открыта на 90°.'], TEAL)
        if stored:
            legend(1307, 450, '02', 'Обеденный комплект',
                   [f'{dining["aisle"]} мм до кухонных фасадов.',
                    'Два стула задвинуты под длинную',
                    'сторону столешницы.',
                    f'{desk_gap} мм в узком подходе к столу.'], OLIVE)
            legend(1307, 623, '03', 'Двери и техника',
                   ['Вход и холодильник до 90° без помех.',
                    f'Открытая ПММ в {dining["pmm_open_gap"]:.0f} мм от стула.',
                    'Стол занимает зону дверцы духовки.'], CLAY)
        elif parked:
            legend(1307, 462, '02', 'Подход к рабочему столу',
                   [f'{desk_gap} мм в узком месте у створки.',
                    'Маршрут идёт вдоль дивана',
                    'к правой части столешницы.'], CLAY)
            legend(1307, 618, '03', 'Кресло под столом',
                   ['Спинка перед кромкой столешницы.',
                    f'Основание выступает до {parking["base_in_front"]} мм.',
                    'Пунктиром показана часть под столом.'], OLIVE)
        else:
            legend(1307, 462, '02', 'Подход к рабочему столу',
                   [f'{desk_gap} мм между диваном и створкой.',
                    'Выдвинутое кресло перекрывает',
                    'подход к столу. Зазоры вокруг кресла',
                    f'{chair_to_bed:.0f} мм до дивана и {chair_to_leaf:.0f} мм до ручки.'], CLAY)
            legend(1307, 651, '03', 'Положение мебели',
                   [f'Кресло отодвинуто на {CHAIR_TRAVEL} мм.',
                    'Радиатор на простенке у мансарды.'], OLIVE)
        dashed([(1307, 832), (1353, 832)], CLAY)
        label((1365, 831), 'Подход к рабочему месту', 19, SUB, False, 'lm')
    else:
        legend(1307, 298, '01', 'За обеденными стульями',
               [f'{chair_gap} мм до медиатумбы в модели.',
                f'{chair_gap - 300} мм, если отодвинуть их на 300 мм.'], TEAL)
        legend(1307, 437, '02', 'У открытой створки',
               [f'{table_gap} мм от торца обеденного стола',
                'до края створки при повороте на 90°.',
                'Ширина створки 800 мм условна.'], CLAY)
        legend(1307, 601, '03', 'Рабочее место',
               [f'Кресло Ø{CHAIR_RADIUS * 2}, отодвинуто на {CHAIR_TRAVEL} мм.',
                f'{sizes["chair_to_sofa"]} мм до дивана, около {sizes["chair_to_sash_pulled"]:.0f} мм до ручки.',
                f'Радиатор {RADIATOR[3] - RADIATOR[1]} × {RADIATOR_HEIGHT} мм,',
                f'выступ до {RADIATOR[2] - RADIATOR[0]} мм.'], OLIVE)
    dashed([(1307, 798), (1353, 798)], TEAL)
    label((1365, 797), 'Маршрут при открытых D2 и O1', 19, SUB, False, 'lm')

    if stored:
        label((55, 927), 'Переставлять стол при сложенном диване и закрытых дверцах техники.', 20, SUB)
        label((55, 957), 'Зазоры рассчитаны для столешницы 1400 × 800, стульев 400 × 400 и условных дверец.', 20, SUB)
    else:
        label((55, 937), 'Зазоры по контурам модели. Фактический проход O1 зависит от рамы, створки и ручки.', 20, SUB)
    x0, x1, y = 1582, 1582 + SCALE * 500, 946
    draw.line((x0, y, x1, y), fill=SUB, width=2)
    for x in (x0, x1):
        draw.line((x, y - 5, x, y + 5), fill=SUB, width=2)
    label(((x0 + x1) / 2, y - 7), '500 мм', 16, SUB, False, 'ms')
    image.save(dest)
    gaps = (foot_gap, desk_gap) if night else (chair_gap, table_gap)
    print(f'{dest.name}\nPASS route radius bound {clear:.1f} mm; local gaps {gaps} mm')
    if parked:
        print(f'PASS parked chair, back-to-top gap {parking["back_to_top"]:.2f} mm, desk route width {2 * desk_clear:.1f} mm')
    if stored:
        print(f'PASS dining move, parking and door zones {dining}')


if __name__ == '__main__':
    main()
