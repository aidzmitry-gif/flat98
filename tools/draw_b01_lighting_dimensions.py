"""Dimension the coordinated B01 lighting positions and the N3 sill detail."""
from functools import lru_cache
import math

from PIL import Image, ImageDraw, ImageFont

from b01_workplace_geometry import D2_PARTS, O1_PARTS, OUTPUT, RADIATOR, door_points, footprints, load_model, verify
from draw_b01_lighting_plan import (
    CEILING, CEILING_POINTS, CONTROL_DESK, CONTROL_ENTRY, ENTRY_NIGHT, FLOOR, FONT_DIR, INK, KITCHEN,
    KITCHEN_STRIP, MEDIA, MEDIA_STRIP, NIGHT, NIGHT_MARKER_Z, NIGHT_STRIP, NIGHT_STRIP_Z, PAPER, SILL_NIGHT,
    SUB, WALL, WHITE, WORK, WORK_STRIP,
)

PLAN = OUTPUT / 'B01_освещение_привязки_высоты_выключатели_v4.png'
DETAIL = OUTPUT / 'B01_узел_N3_у_створки_O1_v1.png'
KITCHEN_Z, MEDIA_Z, WORK_Z, CONTROL_Z = 1470, 2000, 1480, 1000
RULE, MASONRY, FRAME = '#cdd3c8', '#e1e5dc', '#687c73'
FURNITURE, GLAZING, ARC = '#e9ddcb', '#c9dedb', '#809b93'


@lru_cache
def font(size, bold):
    return ImageFont.truetype(FONT_DIR / ('segoeuib.ttf' if bold else 'segoeui.ttf'), size)


class Sheet:
    def __init__(self, size, title, subtitle, index):
        self.image = Image.new('RGB', size, PAPER)
        self.draw = ImageDraw.Draw(self.image)
        self.text((56, 42), title, 49, bold=True)
        self.text((58, 111), subtitle, 23, SUB)
        self.badge((size[0] - 402, 55), 'ПРИМЕРКА   /   ' + index, INK, 344, 40, 20)

    def text(self, pos, value, size=22, color=INK, bold=False, anchor='lt'):
        self.draw.text(pos, str(value), font=font(size, bold), fill=color, anchor=anchor)

    def line(self, pts, color=RULE, width=2):
        self.draw.line(list(pts), fill=color, width=width, joint='curve')

    def box(self, rect, fill, stroke=None, width=2):
        self.draw.rectangle(rect, fill=fill, outline=stroke, width=width)

    def poly(self, pts, fill, stroke=None, width=2):
        pts = list(pts)
        self.draw.polygon(pts, fill=fill)
        if stroke:
            self.line([*pts, pts[0]], stroke, width)

    def card(self, rect):
        self.draw.rounded_rectangle(rect, 15, WHITE, RULE, 2)

    def badge(self, pos, value, color, w=66, h=32, size=18):
        x, y = pos
        self.draw.rounded_rectangle((x, y, x + w, y + h), 7, color)
        self.text((x + w / 2, y + h / 2), value, size, WHITE, True, 'mm')

    def marker(self, pos, color, r=8, square=False):
        x, y = pos
        if square:
            self.box((x - r, y - r, x + r, y + r), color, WHITE)
        else:
            self.draw.ellipse((x - r, y - r, x + r, y + r), fill=color, outline=WHITE, width=2)

    def arrow(self, a, b, color, width=3, head=11):
        self.line((a, b), color, width)
        dx, dy = (b[0] - a[0], b[1] - a[1])
        length = math.hypot(dx, dy)
        ux, uy = dx / length, dy / length
        self.poly([b, (b[0] - head * (ux + .5 * uy), b[1] - head * (uy - .5 * ux)),
                   (b[0] - head * (ux - .5 * uy), b[1] - head * (uy + .5 * ux))], color)

    def dim(self, a, b, at, value, axis='x', side=1, color=SUB, size=20):
        if axis == 'x':
            p, q = (a[0], at), (b[0], at)
            label, anchor = ((p[0] + q[0]) / 2, at - 8), 'ms'
        else:
            p, q = (at, a[1]), (at, b[1])
            label, anchor = (at + 10 * side, (p[1] + q[1]) / 2), 'lm' if side > 0 else 'rm'
        for original, (x, y) in ((a, p), (b, q)):
            self.line((original, (x, y)), RULE)
            self.line(((x - 5, y + 5), (x + 5, y - 5)), color)
        self.line((p, q), color)
        self.text(label, value, size, color, True, anchor)


def box2(sheet, project, rect, fill, stroke=None):
    x0, y0, x1, y1 = rect
    a, b = project((x0, y1)), project((x1, y0))
    sheet.box((*a, *b), fill, stroke)


def swing(sheet, project, hinge, radius, sign):
    def step(degree):
        a = math.radians(degree)
        return project((hinge[0] + sign * radius * math.sin(a), hinge[1] + sign * radius * math.cos(a)))

    for degree in range(0, 90, 6):
        sheet.line((step(degree), step(degree + 4)), ARC)


def lights_plan(data):
    s = Sheet((2310, 1410), 'B01  /  План освещения и выключателей',
              'Кухня-гостиная  ·  Привязки к чистовым плоскостям  ·  Все размеры в мм', '01 / 02')
    w, d = data['room']['width'], data['room']['depth']
    o1, d2 = data['terrace'], data['entrance']
    layout = footprints(data)
    s.card((55, 174, 1459, 1159))
    s.card((1480, 174, 2254, 1159))
    s.text((86, 196), '01  /  Вид сверху', 26, bold=True)
    s.text((1510, 196), '02  /  Ведомость привязок [П]', 26, bold=True)

    def p(point):
        return 206 + point[0] * .19, 327 + (d - point[1]) * .19

    box2(s, p, (0, 0, w, d), FLOOR)
    for rect in (
        (-160, 0, 0, d2['start']), (-160, d2['end'], 0, d), (0, d, w + 145, d + 85),
        (0, -85, w + 145, 0), (w, 0, w + 145, o1['start']), (w, o1['end'], w + 145, d),
    ):
        box2(s, p, rect, MASONRY, WALL)
    box2(s, p, (w, o1['start'], w + 60, o1['split']), GLAZING, ARC)
    for name, rect in layout.items():
        fill = {'sofa': '#d9dfcf', 'desk': '#e4e5d6', 'table': '#eddfc6', 'dishwasher': '#e1e9df'}.get(name, FURNITURE)
        box2(s, p, rect, fill, '#afb5a7')
    box2(s, p, RADIATOR, '#e5cdbb', '#aa7a5f')
    for name, caption in (
        ('fridge', 'Хол. 600'), ('dishwasher', 'ПММ 600'), ('sink', 'Мойка'), ('hob', 'Варка'),
        ('oven', 'Пенал'), ('sofa', 'Диван'), ('desk', 'Рабочий стол'), ('media', 'Медиатумба'),
    ):
        x0, y0, x1, y1 = layout[name]
        x = x0 + (.74 if name in ('dishwasher', 'sink') else .5) * (x1 - x0)
        y = y0 + (.20 if name == 'desk' else .5) * (y1 - y0)
        s.text(p((x, y)), caption, 14 if name == 'dishwasher' else 17, SUB, False, 'mm')
    s.text(p((3470, 1650)), 'Обеденный стол', 17, SUB, False, 'mm')

    hinge_o1, hinge_d2 = (w, o1['end']), (0, d2['start'])
    for hinge, parts, sign, r in ((hinge_o1, O1_PARTS, -1, o1['end'] - o1['split']),
                                  (hinge_d2, D2_PARTS, 1, d2['end'] - d2['start'])):
        swing(s, p, hinge, r, sign)
        for part in parts:
            s.poly(map(p, door_points(hinge, part, math.pi / 2, sign)), GLAZING, ARC)
    s.text(p((590, 920)), 'D2 · Б', 17, SUB, True, 'mm')
    s.text(p((5430, 1610)), 'O1 · А', 17, SUB, True, 'mm')

    for points, code, color, offset in (
        (KITCHEN_STRIP, 'SW01', KITCHEN, (12, -37)),
        (WORK_STRIP, 'DIM02', WORK, (0, 10)),
        (MEDIA_STRIP, 'DIM01', MEDIA, (0, -35)),
        (NIGHT_STRIP, 'N2', NIGHT, (0, -32)),
    ):
        s.line(map(p, points), color, 6)
        a, b = list(map(p, points))[-2:]
        tx, ty = (a[0] + b[0]) / 2 + offset[0], (a[1] + b[1]) / 2 + offset[1]
        s.badge((tx - 34, ty), code, color, 68, 26, 15)
    for i, point in enumerate(CEILING_POINTS, 1):
        x, y = p(point)
        s.marker((x, y), CEILING)
        s.text((x + 15, y - 1), f'P{i}', 19, CEILING, True, 'lm')
    for point, code, color, offset, square in (
        (CONTROL_ENTRY, 'К1', INK, (-9, 31), True), (CONTROL_DESK, 'К2', INK, (0, -33), True),
        (ENTRY_NIGHT, 'N1', NIGHT, (15, -15), False), (SILL_NIGHT, 'N3', NIGHT, (-33, 15), False),
    ):
        x, y = p(point)
        s.marker((x, y), color, 10, square)
        s.text((x + offset[0], y + offset[1]), code, 21, color, True, 'mm')

    s.dim(p((0, d)), p((w, d)), 274, f'{w}  [Б]')
    s.dim(p((w, 0)), p((w, d)), 1404, f'{d}', 'y', size=18)
    for x, at, side, chain in (
        (0, 154, -1, (0, d2['start'], d2['end'], d)),
        (w, 1344, 1, (0, o1['start'], o1['end'], d)),
    ):
        for a, b in zip(chain, chain[1:]):
            s.dim(p((x, a)), p((x, b)), at, str(b - a), 'y', side, size=18)

    ox, oy = p((w, 0))
    s.marker((ox, oy), INK, 5)
    s.arrow((ox, oy + 51), (ox - 209, oy + 51), INK)
    s.arrow((ox - 3, oy + 51), (ox - 3, oy + 16), INK)
    s.text((ox - 222, oy + 51), 'S', 18, bold=True, anchor='rm')
    s.text((ox + 17, oy + 16), 'Y', 18, bold=True, anchor='lm')
    s.text((ox - 6, oy + 66), 'Ноль S/Y у угла медиастены со стороны O1', 18, SUB, anchor='rt')
    s.text((87, 1071), 'S вдоль медиастены к входу  ·  Y от медиастены к дивану', 20, SUB)
    s.text((87, 1107), 'D2 открыта внутрь по Б  ·  O1 открыта левая створка по А', 20, SUB)
    s.line(((817, 1129), (1007, 1129)), SUB, 3)
    for offset, value in ((0, '0'), (95, '500'), (190, '1000 мм')):
        s.line(((817 + offset, 1123), (817 + offset, 1135)), SUB)
        s.text((817 + offset, 1119), value, 14, SUB, anchor='ms')

    def pair(point):
        return f'{w - point[0]} / {point[1]}'

    s.text((1510, 250), 'Точка и группа', 18, SUB, True)
    s.text((1778, 250), 'S / Y', 18, SUB, True)
    s.text((2130, 250), 'Z', 18, SUB, True)
    s.line(((1510, 279), (2225, 279)), RULE)
    rows = [('SW01', 'Кухня', (f'{pair(KITCHEN_STRIP[0])} → {pair(KITCHEN_STRIP[1])}',
                                f'→ {pair(KITCHEN_STRIP[2])}'), f'+{KITCHEN_Z}', KITCHEN)]
    rows.extend((f'P{i}', 'SW02', (pair(point),), '+H*', CEILING) for i, point in enumerate(CEILING_POINTS, 1))
    rows.extend((
        ('N1', 'SW03 · вход', (pair(ENTRY_NIGHT),), f'+{NIGHT_MARKER_Z}', NIGHT),
        ('N2', 'SW03 · под тумбой', (f'{pair(NIGHT_STRIP[0])} → {pair(NIGHT_STRIP[1])}',), f'+{NIGHT_STRIP_Z}', NIGHT),
        ('N3', 'SW03 · у O1', (pair(SILL_NIGHT),), f'+{NIGHT_MARKER_Z}', NIGHT),
        ('DIM01', 'В стеллаже', (f'{pair(MEDIA_STRIP[0])} → {pair(MEDIA_STRIP[1])}',), f'+{MEDIA_Z}', MEDIA),
        ('DIM02', 'Под полкой стола', (f'{pair(WORK_STRIP[0])} → {pair(WORK_STRIP[1])}',), f'+{WORK_Z}', WORK),
    ))
    y = 291
    for code, label, coords, z, color in rows:
        s.badge((1510, y), code, color, 74, 29, 16)
        s.text((1598, y + 4), label, 18, INK, True)
        for i, coord in enumerate(coords):
            s.text((1778, y + 4 + i * 23), coord, 18, SUB)
        s.text((2130, y + 3), z, 20, INK, True)
        y += 56 if len(coords) > 1 else 40
    s.line(((1510, y + 5), (2225, y + 5)), RULE)
    s.text((1510, y + 27), 'Выключатели  ·  Z до центра рамки', 22, bold=True)
    for i, (code, point, desc) in enumerate((
        ('К1', CONTROL_ENTRY, 'У входа   ·   SW01 / SW02 / DIM01'),
        ('К2', CONTROL_DESK, 'У стола   ·   SW03 / DIM02'),
    )):
        row_y = y + 72 + i * 76
        s.badge((1510, row_y), code, INK, 74, 29, 16)
        s.text((1598, row_y + 3), desc, 19, INK, True)
        s.text((1598, row_y + 32), f'S / Y  {pair(point)}', 18, SUB)
        s.text((2130, row_y + 3), f'+{CONTROL_Z}', 20, INK, True)
    s.text((1510, 1055), 'К1 на медиастене, 1120 от угла со стороны D2.', 19, SUB)
    s.text((1510, 1085), 'К2 за столом, 1120 от угла со стороны O1.', 19, SUB)
    s.text((1510, 1115), 'К1 вне дуги D2 в модели. Проверить доступ к К2.', 19, SUB)

    s.line(((56, 1191), (2254, 1191)), RULE)
    s.text((57, 1218), '[Б] Размеры плана для контрольного обмера   ·   [П] Предложение для примерки',
           22, bold=True)
    s.text((57, 1257), '* +H — лицевая плоскость чистового потолка. В модели +2700. Замерить потолок по всем пяти точкам.',
           21, SUB)
    s.text((57, 1292), 'Z от чистого пола до оси маркера или светящей плоскости профиля. SW01 и DIM02 привязать к низу шкафов и полки.',
           21, SUB)
    s.text((57, 1327), 'Размеры 5710 и 3500 по расчётному плану. Проверить ширину 5705/5710, отделку, коробки, высоты мебели и положение стола.',
           21, SUB)
    s.text((57, 1362), 'Схема для разметки при примерке. Монтажные отверстия и подключение уточнить по выбранным приборам.',
           20, SUB)
    s.image.save(PLAN)


def sill_detail(data):
    s = Sheet((2000, 1330), 'B01  /  Узел N3 у створки O1',
              'На внутренней грани простенка со стороны медиастены  ·  Размеры в мм', '02 / 02')
    s.card((55, 174, 985, 1102))
    s.card((1015, 174, 1945, 1102))
    s.text((85, 196), 'А  /  План при открытой створке', 25, bold=True)
    s.text((1045, 196), 'Б  /  Вид на проём из комнаты', 25, bold=True)
    o1 = data['terrace']
    w = data['room']['width']
    a, m, b, top = (o1[key] for key in ('start', 'split', 'end', 'assumedTop'))
    sill = o1['sketchSill']
    y3 = SILL_NIGHT[1]
    scale = .282

    def p(point):
        return 666 + (point[0] - w) * scale, 1030 - point[1] * scale

    box2(s, p, (w - 1600, 0, w, 2540), FLOOR)
    for rect in ((w - 1600, -95, w + 145, 0), (w, 0, w + 145, a), (w, b, w + 145, 2540)):
        box2(s, p, rect, MASONRY, WALL)
    box2(s, p, (w, a, w + 145, b), '#f1e7d8', RULE)
    box2(s, p, (w - 6, a, w + 58, m), GLAZING, FRAME)
    for name, caption in (('media', 'Медиатумба'), ('books', 'Стеллаж')):
        x0, y0, x1, y1 = footprints(data)[name]
        x0 = max(x0, w - 1600)
        box2(s, p, (x0, y0, x1, y1), FURNITURE, WALL)
        s.text(p(((x0 + x1) / 2, (y0 + y1) / 2)), caption, 18, SUB, anchor='mm')
    hinge = (w, b)
    swing(s, p, hinge, b - m, -1)
    for part in O1_PARTS:
        s.poly(map(p, door_points(hinge, part, math.pi / 2, -1)), GLAZING, FRAME)
    s.marker(p(hinge), INK, 6)
    s.text((250, 378), 'Левая открыта внутрь', 22, bold=True)
    s.line(((416, 406), p((w - 760, b + 10))), FRAME)
    s.text((252, 565), 'Дуга 90° [П]', 18, SUB)
    s.line(((385, 580), p((w - 560, b - 565))), ARC)
    s.text((246, 682), 'Правая закрыта', 22, bold=True)
    s.line(((435, 695), p((w + 10, 1200))), FRAME)

    start, target = p(SILL_NIGHT), p((w - 230, 1650))
    s.arrow((start[0] - 3, start[1] - 8), target, NIGHT, 4, 16)
    s.marker(start, NIGHT, 11)
    s.badge((457, 840), 'N3', NIGHT, 61, 32)
    s.line(((518, 856), (595, 856), start), NIGHT, 3)
    s.text((393, 740), 'Свет к порогу', 21, NIGHT, True)
    s.line(((536, 751), (628, 751)), NIGHT)
    s.text((261, 1057), 'МЕДИАСТЕНА   ·   Y = 0', 19, SUB, True)

    for lo, hi, label in ((0, y3, f'{y3} [П]'), (y3, a, f'{a - y3}'),
                           (a, m, f'{m - a} [П]'), (m, b, f'{b - m} [П]')):
        s.dim(p((w, lo)), p((w, hi)), 780, label, 'y', color=NIGHT if hi <= a else SUB, size=18)
    s.dim(p((w, 0)), p((w, a)), 875, f'{a} [Б]', 'y', size=18)
    s.dim(p((w, a)), p((w, b)), 875, f'{b - a} [Б]', 'y', size=18)

    def e(point):
        y, z = point
        return 1771 - y * scale, 1030 - z * scale

    def face(y0, z0, y1, z1, color, edge=None):
        s.box((*e((y1, z1)), *e((y0, z0))), color, edge)

    face(0, 0, 2410, 2590, MASONRY, WALL)
    face(a, sill, b, top, '#f9f5ea', FRAME)
    face(a, sill, m, top, GLAZING, FRAME)
    for y0, y1 in ((a, a + 36), (m - 38, m), (b - 36, b)):
        face(y0, sill, y1, top, FRAME)
    for z0, z1 in ((sill, sill + 31), (top - 36, top)):
        face(a, z0, b, z1, FRAME)
    face(b - 28, sill + 32, b - 8, top - 39, '#405d54')
    s.text(e(((m + b) / 2, 1910)), 'ЛЕВАЯ', 19, INK, True, 'mm')
    s.text(e(((m + b) / 2, 1805)), 'ОТКРЫТА', 19, INK, True, 'mm')
    s.text(e(((a + m) / 2, 1910)), 'ПРАВАЯ', 19, INK, True, 'mm')
    s.text(e(((a + m) / 2, 1805)), 'ЗАКРЫТА', 19, INK, True, 'mm')
    s.line(((1068, 1030), (1797, 1030)), INK, 3)
    s.text((1068, 1055), '±0   ЧИСТОВОЙ ПОЛ', 19, SUB, True)
    s.text((1170, 939), f'Порог {sill} [Б]', 18, SUB)
    s.line(((1214, 964), (1214, e((b, sill))[1])), FRAME)

    center = e((y3, NIGHT_MARKER_Z))
    face(y3 - 25, NIGHT_MARKER_Z - 20, y3 + 25, NIGHT_MARKER_Z + 20, NIGHT, WHITE)
    s.marker(center, NIGHT, 7)
    s.badge((1662, 830), 'N3', NIGHT, 61, 32)
    s.line(((1662, 849), (1636, 849), center), NIGHT, 3)
    s.dim(e((0, 0)), center, 1811, f'+{NIGHT_MARKER_Z} [П]', 'y', color=NIGHT)
    s.dim(e((a, NIGHT_MARKER_Z)), center, 913, f'{a - y3}', color=NIGHT, size=18)
    s.text((1698, 443), 'ПРОСТЕНОК', 17, SUB, True, 'mm')
    s.text((1698, 471), 'СО СТОРОНЫ', 17, SUB, True, 'mm')
    s.text((1698, 499), 'МЕДИАСТЕНЫ', 17, SUB, True, 'mm')

    s.line(((56, 1130), (1944, 1130)), RULE)
    s.text((57, 1154), f'N3 [П]   S0 / Y{y3} / Z+{NIGHT_MARKER_Z}  ·  От чистового угла медиастены вдоль стены O1',
           23, NIGHT, True)
    s.text((57, 1193), f'{a - y3} мм до края проёма по модели. [Б] Цепочка проёма по БТИ. Деление створок и угол [П].',
           21, SUB)
    s.text((57, 1228), 'Направить свет вниз к внутренней кромке порога. Показан условный корпус шириной 50 мм.',
           21, SUB)
    s.text((57, 1263), 'Перед креплением сверить край рамы, высоту пола и порога. Примерить прибор с полностью открытой створкой.',
           21, SUB)
    s.image.save(DETAIL)


def main():
    data = load_model()
    verify(data)
    w, d = data['room']['width'], data['room']['depth']
    rects = footprints(data)
    assert CEILING_POINTS[2] == tuple((a + b) // 2 for a, b in zip(rects['table'][:2], rects['table'][2:]))
    assert all(0 < x < w and 0 < y < d for x, y in CEILING_POINTS)
    d2_reach = max(math.hypot(max(n1, 0), t1) for _, _, n1, t1 in D2_PARTS)
    assert CONTROL_ENTRY[0] > d2_reach and CONTROL_ENTRY[1] == 0
    assert rects['desk'][0] < CONTROL_DESK[0] < rects['desk'][2] and CONTROL_DESK[1] == d
    assert SILL_NIGHT[0] == w and data['terrace']['start'] - SILL_NIGHT[1] == 75
    assert all(rects['media'][0] < x < rects['media'][2] and 0 < y < rects['media'][3] for x, y in NIGHT_STRIP)
    lights_plan(data)
    sill_detail(data)
    print(f'Wrote {PLAN.name} and {DETAIL.name}')
    print(f'D2 sweep projection ends by X={d2_reach:.1f} mm. K1 axis at X={CONTROL_ENTRY[0]} mm.')


if __name__ == '__main__':
    main()
