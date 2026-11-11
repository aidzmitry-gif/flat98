"""Render the O1 cutaway from the same millimetre coordinates as the plan.

Run render_b01_o1_two_sashes.cjs first to export the shared geometry.
"""
from dataclasses import dataclass
from pathlib import Path
import json

import numpy as np
from PIL import Image, ImageColor, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
W, H = 1760, 1100


@dataclass
class Solid:
    lo: tuple
    hi: tuple
    color: str
    material: str = 'matte'


def build_scene(data):
    room = data['room']
    width, depth, height = room['width'], room['depth'], room['assumedHeight']
    d2, o1 = data['entrance'], data['terrace']
    solids = []
    furniture = {item['id']: item for item in data['furniture']}

    def box(x0, y0, z0, x1, y1, z1, color, material='matte'):
        solids.append(Solid((x0, y0, z0), (x1, y1, z1), color, material))

    ivory, worktop, oak, plaster = '#e4d4bc', '#e7d9bf', '#b88c5f', '#e6ded1'
    dark, fabric = '#303c3b', '#818264'

    box(0, 0, -108, width, depth, 0, '#bda083', 'floor')
    box(-145, -120, -108, width + 145, 0, height, plaster)
    box(0, depth, -108, width + 145, depth + 115, 105, plaster)
    box(-145, 0, 0, 0, d2['start'], height, plaster)
    box(-145, d2['end'], 0, 0, depth + 115, height, plaster)
    box(-145, d2['start'], d2['height'], 0, d2['end'], height, plaster)
    box(-44, d2['start'] + 13, 0, -6, d2['end'] - 13, d2['height'] - 13, '#c7b69e')
    box(-5, d2['start'] + 70, 997, 26, d2['start'] + 166, 1013, dark)

    # Cut the short wall down on both sides of the opening so the two leaves stay visible.
    box(width, 0, -108, width + 145, o1['start'], 235, plaster)
    box(width, o1['end'], -108, width + 145, depth, 235, plaster)
    a, c, b, top = o1['start'], o1['split'], o1['end'], o1['assumedTop']
    sill = o1['sketchSill']
    box(width, a, -108, width + 145, b, sill, '#bcb09e')
    for y0, y1 in ((a, a + 46), (c - 28, c + 28), (b - 46, b)):
        box(width, y0, sill, width + 45, y1, top, dark)
    box(width, a + 46, sill, width + 45, b - 46, sill + 41, dark)
    box(width, a + 46, top - 46, width + 45, b - 46, top, dark)
    for y0, y1 in ((a + 46, c - 28), (c + 28, b - 46)):
        box(width, y0, sill + 41, width + 19, y1, top - 46, '#94bbc0', 'glass')
    box(width - 15, c + 40, 980, width + 17, c + 52, 1090, dark)
    box(width - 48, a + 9, top + 5, width + 21, b - 9, top + 90, '#c7b69b', 'fabric')

    # The first run follows Y=3500. The other follows X=0 and ends at D2.
    for name in ('corner', 'prep', 'hob', 'pullout', 'sink', 'dishwasher'):
        x0, y0, x1, y1 = furniture[name]['rect']
        box(x0 + 38, y0 + 38, 0, x1 - 15, y1 - 15, 73, '#948779')
        box(x0 + 2, y0 + 2, 73, x1 - 2, y1 - 2, 835, ivory)
        if name in ('sink', 'dishwasher'):
            box(x1 - 15, y0 + 5, 755, x1 + 1, y1 - 5, 768, '#aa9b84')
        elif name != 'corner':
            for z in (352, 598):
                box(x0 + 4, y0 - 1, z, x1 - 4, y0 + 8, z + 4, '#aa9b84')
        if name == 'sink':
            sx0, sy0, sx1, sy1 = x0 + 90, y0 + 84, x1 - 77, y1 - 89
            for lx, ly, rx, ry in ((x0, y0, sx0, y1), (sx1, y0, x1, y1),
                                   (sx0, y0, sx1, sy0), (sx0, sy1, sx1, y1)):
                box(lx, ly, 835, rx, ry, 860, worktop, 'stone')
            box(sx0, sy0, 835, sx1, sy1, 836, '#66625a')
            box(sx0 - 33, (sy0 + sy1) / 2, 860, sx0 - 11, (sy0 + sy1) / 2 + 22, 1120, '#b3925e')
            box(sx0 - 33, (sy0 + sy1) / 2, 1098, sx0 + 114, (sy0 + sy1) / 2 + 22, 1120, '#b3925e')
        else:
            box(x0, y0, 835, x1, y1, 860, worktop, 'stone')
        if name == 'hob':
            box(x0 + 15, y0 + 65, 860, x1 - 15, y1 - 52, 869, '#292b2a', 'hob')

    # The oven tower is on the sofa wall. Appliance fronts face the centre of the room.
    x0, y0, x1, y1 = furniture['oven']['rect']
    box(x0, y0, 0, x1, y1, 2400, ivory)
    for z0, z1 in ((585, 1180), (1215, 1580)):
        box(x0 + 10, y0, z0, x1 - 10, y0 + 1, z1, dark)
        box(x0 + 40, y0, z1 - 108, x1 - 40, y0 + 2, z1 - 86, '#bdb6a8')
    x0, y0, x1, y1 = furniture['fridge']['rect']
    box(x0, y0, 0, x1, y1, 2400, ivory)
    for z in (740, 1950):
        box(x1, y0 + 3, z, x1 + 1, y1 - 3, z + 7, '#978776')

    # Upper cabinets on the uncut end wall. The other upper run is left off the cutaway.
    for name in ('sink', 'dishwasher'):
        _, y0, _, y1 = furniture[name]['rect']
        box(0, y0 + 2, 1460, 325, y1 - 2, 2400, ivory)
        box(5, y0 + 9, 1451, 292, y1 - 9, 1460, '#f3d9a4')

    def table(item, color):
        x0, y0, x1, y1 = item['rect']
        top = item['h']
        box(x0, y0, top - 36, x1, y1, top, color, 'stone')
        for x in (x0 + 70, x1 - 120):
            for y in (y0 + 57, y1 - 107):
                box(x, y, 0, x + 50, y + 50, top - 36, oak)

    table(furniture['table'], worktop)
    table(furniture['desk'], '#d3bd9d')
    for name in ('chair-1', 'chair-2'):
        x0, y0, x1, y1 = furniture[name]['rect']
        for x in (x0 + 31, x1 - 64):
            for y in (y0 + 26, y1 - 68):
                box(x, y, 0, x + 34, y + 34, 425, '#9d744d')
        box(x0, y0 + 9, 402, x1, y1, 455, '#be8764', 'fabric')
        box(x0 + 12, y0, 441, x1 - 12, y0 + 59, 843, '#bd8967', 'fabric')

    x0, y0, x1, y1 = furniture['sofa']['rect']
    box(x0 + 22, y0 + 33, 0, x1 - 22, y1 - 20, 66, '#45433a')
    box(x0, y0, 66, x1, y1, 366, fabric, 'fabric')
    box(x0, y1 - 221, 366, x1, y1, 940, fabric, 'fabric')
    for ax in (x0, x1 - 155):
        box(ax, y0 + 7, 366, ax + 155, y1 - 221, 675, fabric, 'fabric')
    mid = (x0 + x1) / 2
    for cx0, cx1 in ((x0 + 155, mid - 5), (mid + 5, x1 - 155)):
        box(cx0, y0 + 11, 366, cx1, y1 - 212, 491, '#929474', 'fabric')
        box(cx0 + 12, y1 - 370, 491, cx1 - 10, y1 - 211, 903, '#8d906e', 'fabric')

    x0, y0, x1, y1 = furniture['media']['rect']
    box(x0 + 40, y0 + 32, 0, x1 - 40, y1 - 53, 66, '#716554')
    for i in range(5):
        start = x0 + (x1 - x0) * i / 5
        box(start + 2, y0, 66, start + 558, y1, 516, '#ddd0b9')
    box(x0, y0, 516, x1, y1, 540, oak)
    cx = (x0 + x1) / 2
    box(cx - 1119, 2, 850, cx + 1119, 39, 2119, '#303431')
    box(cx - 1107, 39, 862, cx + 1107, 41, 2107, '#7e8a76', 'screen')
    box(cx - 238, 134, 540, cx + 238, 420, 638, dark)

    x0, y0, x1, y1 = furniture['books']['rect']
    box(x0, y0, 0, x1, y0 + 22, 2400, oak)
    for x in (x0, x1 - 22):
        box(x, y0 + 22, 0, x + 22, y1, 2400, oak)
    for z in (480, 855, 1235, 1615, 1995, 2378):
        box(x0 + 22, y0 + 22, z, x1 - 22, y1, z + 22, oak)
        if z < 2378:
            for i, color in enumerate(('#c7ac86', '#a9a58b', '#e0d5b6', '#806f59', '#c1b59b')):
                bx = x0 + 62 + (i * 55 if z % 2 == 0 else 155 + i * 48)
                box(bx, 58, z + 22, bx + 32, 237, z + 204 + i % 3 * 23, color)
    box(x0 + 22, 22, 25, x1 - 22, y1, 480, ivory)
    return solids, furniture


def unit(vector):
    return vector / np.linalg.norm(vector)


def render(solids, furniture, opening):
    near = unit(np.array([.61, .85, 1.27]))
    right = unit(np.array([-near[1], near[0], 0]))
    up = np.cross(near, right)
    basis = np.stack((right, -up, near), axis=1)
    # Include all eight corners when framing an oblique bounding box.
    corners = np.array([[x, y, z] for s in solids for x in (s.lo[0], s.hi[0])
                        for y in (s.lo[1], s.hi[1]) for z in (s.lo[2], s.hi[2])])
    extent = corners @ basis
    lower, upper = extent[:, :2].min(axis=0), extent[:, :2].max(axis=0)
    scale = min(1510 / (upper[0] - lower[0]), 803 / (upper[1] - lower[1]))
    offset = np.array([W / 2, 562]) - scale * (upper + lower) / 2

    def project(points):
        pixels = np.asarray(points, dtype=float) @ basis
        pixels[..., :2] = pixels[..., :2] * scale + offset
        return pixels

    paper = Image.new('RGB', (W, H), '#f2eee5')
    shadow = Image.new('L', (W, H), 0)
    floor = project([(0, 0, -108), (5710, 0, -108), (5710, 3500, -108), (0, 3500, -108)])
    ImageDraw.Draw(shadow).polygon([(x + 8, y + 25) for x, y in floor[:, :2]], fill=170)
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    paper.paste('#b9ad9c', mask=shadow)
    pixels = np.array(paper, dtype=np.float32)
    depths = np.full((H, W), -np.inf, dtype=np.float32)
    light = unit(np.array([1.5, -.4, 2.2]))

    def face(solid, axis):
        lo, hi = np.array(solid.lo, dtype=float), np.array(solid.hi, dtype=float)
        ax1, ax2 = [i for i in range(3) if i != axis]
        p0 = lo.copy()
        p0[axis] = hi[axis]
        p1, p2 = p0.copy(), p0.copy()
        p1[ax1], p2[ax2] = hi[ax1], hi[ax2]
        points = project([p0, p1, p2, p1 + p2 - p0])
        p, uvec, vvec = points[0], points[1] - points[0], points[2] - points[0]
        xa, ya = np.maximum(0, np.floor(points[:, :2].min(axis=0))).astype(int)
        xb, yb = np.minimum([W, H], np.ceil(points[:, :2].max(axis=0))).astype(int)
        if xb <= xa or yb <= ya:
            return
        yy, xx = np.ogrid[ya:yb, xa:xb]
        dx, dy = xx + .5 - p[0], yy + .5 - p[1]
        det = uvec[0] * vvec[1] - uvec[1] * vvec[0]
        u = (dx * vvec[1] - dy * vvec[0]) / det
        v = (dy * uvec[0] - dx * uvec[1]) / det
        depth = p[2] + u * uvec[2] + v * vvec[2]
        d = depths[ya:yb, xa:xb]
        hit = (u >= 0) & (u <= 1) & (v >= 0) & (v <= 1) & (depth >= d)
        if not np.any(hit):
            return
        u, v = u[hit], v[hit]
        pos = p0 + u[:, None] * (p1 - p0) + v[:, None] * (p2 - p0)
        x, y, z = pos.T
        color = np.array(ImageColor.getrgb(solid.color))
        shade = (.80 + .20 * max(0, light[axis])) * (1 + .025 * (x / 5710 + z / 2700))
        material = solid.material
        if material == 'floor' and axis == 2:
            # Four-to-one planks in a seamless 90-degree herringbone pattern.
            s, t = (x + y) / 145, (y - x) / 145
            i, j = np.floor(s), np.floor(t)
            k = (i - j) % 8
            horiz = k < 4
            si, ti = np.where(horiz, i - k, i), np.where(horiz, j, j - (7 - k))
            plank = (np.sin(si * 12.9898 + ti * 78.233) * 43758.5453) % 1
            grain = np.where(horiz, t + .023 * s, s + .023 * t)
            seam = np.where(horiz, (t % 1 < .015) | (s - si < .015),
                            (s % 1 < .015) | (t - ti < .015))
            shade *= .95 + .13 * plank + .014 * np.sin(grain * 92) - .065 * seam
            for name in ('sofa', 'oven', 'fridge', 'media', 'books', 'corner', 'sink'):
                x0, y0, x1, y1 = furniture[name]['rect']
                ddx = np.maximum(np.maximum(x0 - x, x - x1), 0)
                ddy = np.maximum(np.maximum(y0 - y, y - y1), 0)
                shade *= 1 - .19 * np.exp(-(ddx ** 2 + ddy ** 2) / 240 ** 2)
        if material == 'fabric':
            shade *= 1 + .02 * np.sin(x * .22 + z * .15) * np.sin(y * .17 + z * .25)
        if material == 'stone':
            shade *= 1 - .035 * np.maximum(0, np.sin(x * .012 + y * .015 + np.sin(y * .023))) ** 9
        painted = shade[:, None] * color
        if material == 'screen' and axis == 1:
            painted = (1 - v[:, None]) * [179, 156, 119] + v[:, None] * [202, 217, 210]
            for i, tone in enumerate(([120, 137, 117], [86, 113, 95], [55, 87, 72])):
                mountain = .62 - .16 * i + .10 * np.sin(u * 7 + i * 1.8) + .026 * np.sin(u * 24 + i)
                painted[v < mountain] = tone
        if material == 'hob' and axis == 2:
            for cu, cv in ((.28, .28), (.28, .72), (.72, .28), (.72, .72)):
                painted[np.abs(np.hypot(u - cu, v - cv) - .16) < .004] = (126, 124, 115)
        region = pixels[ya:yb, xa:xb]
        if material == 'glass':
            band = np.exp(-((u + .24 * v - .42) * 12) ** 2)
            alpha = .20 + .10 * band[:, None]
            region[hit] = (1 - alpha) * region[hit] + alpha * (painted + 45 * band[:, None])
        else:
            region[hit] = painted
            d[hit] = depth[hit]

    for solid in solids:
        if solid.material != 'glass':
            for axis in (0, 1, 2):
                face(solid, axis)
    for solid in solids:
        if solid.material == 'glass':
            face(solid, 0)

    result = Image.fromarray(np.clip(pixels, 0, 255).astype(np.uint8))
    draw = ImageDraw.Draw(result)

    def text(x, y, value, size, *, bold=False, fill='#203934', anchor='lt'):
        font = ImageFont.truetype(f'C:/Windows/Fonts/arial{"bd" if bold else ""}.ttf', size)
        draw.text((x, y), value, font=font, fill=fill, anchor=anchor)

    def callout(point, elbow, label_x, label_y, title, detail):
        x, y, _ = project(point)
        draw.line(((x, y), elbow), fill='#67817a', width=2)
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill='#006c63')
        text(label_x, label_y, title, 26, bold=True)
        text(label_x, label_y + 36, detail, 19, fill='#5d6e65')

    text(60, 40, 'КУХНЯ-ГОСТИНАЯ B01', 19, bold=True, fill='#006c63')
    text(60, 74, 'Две створки в объёме', 46, bold=True)
    text(60, 135, 'Вид со стороны мансарды · створки закрыты', 23, fill='#5d6e65')
    callout((5755, opening['split'], 1180), (318, 767), 60, 733,
            'O1 · две створки', 'Левая открывается внутрь')
    callout((2210, 3500, 1650), (1440, 609), 1452, 575,
            'Пенал 600 мм', 'На одной стене с диваном')
    text(60, 1025, 'Объём по плану 5710 × 3500 мм. Проём O1 1600 мм по БТИ. Высота и деление створок условны.', 22)
    text(60, 1063, 'Отметка под створками 115 мм по эскизу. Передние стены и часть верхних шкафов срезаны для обзора.', 19, fill='#5d6e65')
    return result


def main():
    data = json.loads((ROOT / 'tmp/b01-o1-two-sashes.json').read_text(encoding='utf-8'))
    solids, furniture = build_scene(data)
    panes = [solid for solid in solids if solid.material == 'glass']
    assert len(panes) == 2 and panes[0].hi[1] < panes[1].lo[1]
    assert panes[0].lo[0] == panes[1].lo[0] == data['room']['width']
    output = ROOT / 'output/visualizations/B01_объём_O1_две_створки_v1.png'
    render(solids, furniture, data['terrace']).save(output)
    print('B01 cutaway: verified two coplanar glazed leaves in the O1 opening.')


if __name__ == '__main__':
    main()
