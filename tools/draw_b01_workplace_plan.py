"""Draw two equal-scale details from the same geometry as the workplace render."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from b01_workplace_geometry import (
    CHAIR_RADIUS, CHAIR_TRAVEL, CHAIR_WORK_Y, CHAIR_X, D2_PARTS, FRIDGE_PARTS, O1_PARTS,
    OUTPUT, PLAN_IMAGE, RADIATOR, RADIATOR_HEIGHT, corners, door_points, footprints, load_model,
    verify,
)

INK = '#263933'
SUB = '#52645d'
PAPER = '#f3f1eb'
LINE = '#dadfd5'
OLIVE = '#64774d'
GLASS = '#2b696d'
AMBER = '#8a552e'
RUST = '#a0422d'
SCALE = .20
FONTS = Path('C:/Windows/Fonts')


def main():
    data = load_model()
    sizes = verify(data)
    rects = footprints(data)
    sheet = Image.new('RGB', (1770, 1058), PAPER)
    draw = ImageDraw.Draw(sheet)

    def label(pos, value, size=23, *, color=INK, bold=False, anchor='lt'):
        face = 'segoeuib.ttf' if bold else 'segoeui.ttf'
        draw.text(pos, str(value), fill=color, font=ImageFont.truetype(FONTS / face, size), anchor=anchor)

    def plan_point(origin, point):
        ox, oy, min_x, max_y = origin
        x, y = point
        return ox + (x - min_x) * SCALE, oy + (max_y - y) * SCALE

    def poly(origin, vertices, fill, stroke=None, width=2):
        points = [plan_point(origin, p) for p in vertices]
        draw.polygon(points, fill=fill)
        if stroke:
            draw.line(points + points[:1], fill=stroke, width=width, joint='curve')

    def box(origin, rect, fill, stroke=None, width=2):
        poly(origin, corners(rect), fill, stroke, width)

    def swing(origin, hinge, radius, sign, fill, stroke):
        path = [
            (hinge[0] + sign * radius * math.sin(angle), hinge[1] + sign * radius * math.cos(angle))
            for angle in (math.radians(step) for step in range(91))
        ]
        poly(origin, [hinge, *path], fill)
        draw.line([plan_point(origin, point) for point in path], fill=stroke, width=2)
        hx, hy = plan_point(origin, hinge)
        draw.ellipse((hx - 4, hy - 4, hx + 4, hy + 4), fill=stroke)

    def open_parts(origin, hinge, parts, sign, fill, stroke):
        for part in parts:
            poly(origin, door_points(hinge, part, math.pi / 2, sign), fill, stroke, 2)

    def tag(origin, pos, value, color):
        x, y = plan_point(origin, pos)
        draw.rounded_rectangle((x - 17, y - 12, x + 17, y + 12), radius=5, fill=color)
        label((x, y - 1), value, 15, color='white', bold=True, anchor='mm')

    def metric(x, y, key, title, lines, color):
        draw.rounded_rectangle((x, y - 2, x + 32, y + 23), radius=6, fill=color)
        label((x + 16, y + 10), key, 15, color='white', bold=True, anchor='mm')
        label((x + 42, y), title, 20, bold=True)
        for index, line in enumerate(lines):
            label((x, y + 36 + index * 27), line, 20, color=SUB)

    def horizontal_dim(x0, x1, y, value):
        draw.line((x0, y, x1, y), fill=SUB, width=2)
        for x in (x0, x1):
            draw.line((x, y - 6, x, y + 6), fill=SUB, width=2)
        label(((x0 + x1) / 2, y - 8), value, 17, color=SUB, anchor='ms')

    label((52, 34), 'B01  /  Рабочее место и вход', 49, bold=True)
    label((54, 101), 'Два фрагмента плана в одном масштабе · размеры в миллиметрах', 24, color=SUB)
    draw.rounded_rectangle((1413, 51, 1718, 94), 10, fill='#e2e9de')
    label((1565, 72), 'ПЛАНИРОВОЧНАЯ ПРИМЕРКА', 17, bold=True, anchor='mm')
    for x in (52, 893):
        draw.rounded_rectangle((x, 158, x + 825, 939), 18, fill='#fffefa', outline=LINE, width=2)
        draw.line((x + 28, 237, x + 796, 237), fill=LINE, width=2)
    label((81, 187), 'А  /  Рабочее место у мансарды', 28, bold=True)
    label((922, 187), 'Б  /  Входная дверь и холодильник', 28, bold=True)

    work = (92, 296, 4100, 3500)
    box(work, (4100, 550, 5710, 3500), '#f8f5ee')
    box(work, (4100, 3500, 5855, 3570), '#e1e0d9', '#a7ada3')
    box(work, (5710, 2200, 5855, 3500), '#e1e0d9', '#a7ada3')
    box(work, (5710, 550, 5855, 600), '#e1e0d9', '#a7ada3')
    sx = rects['sofa'][2]
    box(work, (4100, 2300, sx, 3500), '#e2e7d7', '#8b997a')
    label(plan_point(work, (4277, 3050)), 'Диван', 17, color=OLIVE, bold=True, anchor='mm')
    desk = rects['desk']
    box(work, desk, '#e8d7bd', '#ac9473')
    start, end = plan_point(work, (desk[0], 3500))[0], plan_point(work, (desk[2], 3500))[0]
    horizontal_dim(start, end, 276, str(desk[2] - desk[0]))
    tag(work, (5090, 3250), '01', AMBER)
    box(work, RADIATOR, '#e3c3b3', RUST)
    tag(work, (5480, 2550), '02', RUST)
    o1 = data['terrace']
    h1 = (data['room']['width'], o1['end'])
    swing(work, h1, o1['end'] - o1['split'], -1, '#e7f2f0', '#77a6a1')
    box(work, (5703, o1['start'], 5755, o1['split']), '#b7d9d6', GLASS)
    open_parts(work, h1, O1_PARTS, -1, '#b7d9d6', GLASS)
    tag(work, (5300, 2080), '04', GLASS)
    label(plan_point(work, (5655, 940)), 'Правая закрыта', 16, color=GLASS, anchor='rm')

    radius = CHAIR_RADIUS * SCALE
    for actual, cy in ((False, CHAIR_WORK_Y), (True, CHAIR_WORK_Y - CHAIR_TRAVEL)):
        x, y = plan_point(work, (CHAIR_X, cy))
        bounds = (x - radius, y - radius, x + radius, y + radius)
        if actual:
            draw.ellipse(bounds, outline=OLIVE, width=3)
        else:
            for start in range(0, 360, 24):
                draw.arc(bounds, start, start + 13, fill=OLIVE, width=2)
    x, y0 = plan_point(work, (CHAIR_X, CHAIR_WORK_Y))
    _, y1 = plan_point(work, (CHAIR_X, CHAIR_WORK_Y - CHAIR_TRAVEL))
    draw.line((x, y0, x, y1), fill=OLIVE, width=2)
    draw.polygon([(x - 5, y1 - 8), (x + 5, y1 - 8), (x, y1)], fill=OLIVE)
    tag(work, (5125, 2495), '03', OLIVE)
    for args in (
        (282, '01', 'Рабочий стол', ['1200 × 600 мм', 'Посадка смещена к дивану.'], AMBER),
        (400, '02', 'Вертикальный радиатор',
         [f'{RADIATOR[3] - RADIATOR[1]} × {RADIATOR_HEIGHT} мм, выступ до {RADIATOR[2] - RADIATOR[0]} мм',
          f'{sizes["radiator_to_sash_sweep"]} мм по стене до зоны створки',
          f'{sizes["radiator_to_desk"]} мм до переднего края стола'], RUST),
        (551, '03', 'Кресло без подлокотников',
         [f'Габарит Ø{CHAIR_RADIUS * 2} мм, отъезд {CHAIR_TRAVEL} мм',
          f'{sizes["chair_to_sofa"]} мм до боковины дивана',
          f'Около {sizes["chair_to_sash_pulled"]:.0f} мм до ручки створки',
          'Пунктиром показана посадка.'], OLIVE),
        (731, '04', 'Левая створка O1',
         ['Открыта внутрь на 90°.', 'Ширина 800 мм принята в модели.'], GLASS),
    ):
        metric(478, *args)

    entry = (931, 300, -170, 2350)
    d2 = data['entrance']
    fridge = rects['fridge']
    h2, h3 = (0, d2['start']), (fridge[2], fridge[1])
    box(entry, (0, 0, 1470, 2350), '#f8f5ee')
    for ya, yb in ((0, d2['start']), (d2['end'], 2350)):
        box(entry, (-160, ya, 0, yb), '#e1e0d9', '#a7ada3')
    box(entry, (0, -72, 1470, 0), '#e1e0d9', '#a7ada3')
    swing(entry, h2, D2_PARTS[0][3], 1, '#e4efed', '#77a6a1')
    swing(entry, h3, FRIDGE_PARTS[0][3], 1, '#f1e7d7', '#bd986e')
    box(entry, fridge, '#e6d5be', AMBER)
    box(entry, rects['dishwasher'], '#e9e4d8', '#a3957f')
    label(plan_point(entry, (300, 2025)), 'ПММ 600', 17, bold=True, anchor='mm')
    label(plan_point(entry, (300, 1495)), 'Холодильник', 16, color=AMBER, bold=True, anchor='mm')
    label(plan_point(entry, (300, 1365)), '600 × 600', 16, color=AMBER, anchor='mm')
    open_parts(entry, h2, D2_PARTS, 1, '#b7d9d6', GLASS)
    open_parts(entry, h3, FRIDGE_PARTS, 1, '#e8d6bc', AMBER)
    tag(entry, (460, 107), '05', GLASS)
    tag(entry, (1055, 1225), '06', AMBER)

    xx, y0 = plan_point(entry, (770, fridge[1]))
    _, y1 = plan_point(entry, (770, d2['start'] - D2_PARTS[-1][0]))
    draw.line((xx, y0, xx, y1), fill=GLASS, width=2)
    for yy in (y0, y1):
        draw.line((xx - 6, yy, xx + 6, yy), fill=GLASS, width=2)
    label((xx + 8, (y0 + y1) / 2), f'{sizes["both_doors_at_90"]} мм', 18, color=GLASS, bold=True, anchor='lm')
    gx, gy = plan_point(entry, (0, (fridge[1] + d2['end']) / 2))
    draw.line((gx - 6, gy, gx + 7, gy), fill=RUST, width=4)
    draw.line((gx - 6, gy, gx - 25, gy + 24, gx - 25, gy + 67), fill=RUST, width=2)
    tag(entry, (-125, 705), '07', RUST)

    for args in (
        (282, '05', 'Входная D2 · вариант Б',
         ['Без наличника. Петли у медиастены.', 'Внутрь на 90° в модели.'], GLASS),
        (409, '06', 'Холодильник 600 × 600',
         ['Петли с торца у входа.',
          'Обе двери показаны открытыми.',
          f'{sizes["both_doors_at_90"]} мм по линии на плане.'], AMBER),
        (563, '07', 'Примыкание к проёму',
         [f'{sizes["fridge_to_jamb"]} мм от торца холодильника',
          'до границы проёма по плану БТИ.',
          'Уточнить коробку и фасад по месту.'], RUST),
    ):
        metric(1286, *args)
    label((925, 817), 'В расчёте учтены условные габариты полотен и ручек.', 20, color=SUB)
    label((925, 850), 'При повороте до 90° в модели пересечений у входа нет.', 20, color=SUB)

    label((53, 975), 'Геометрия по БТИ и обмерному эскизу. Углы, створки, ручки и мебель приняты для примерки.', 21, color=SUB)
    horizontal_dim(1616, 1716, 1004, '500 мм')
    dest = OUTPUT / PLAN_IMAGE
    sheet.save(dest)
    print(f'{dest.name}\n{sizes}')


if __name__ == '__main__':
    main()
