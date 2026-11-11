"""APT-001: dimensioned B01 hallway and one illustrative view through D2.

This is a geometric blockout, not a photorealistic or construction rendering.
Axes in millimetres: X goes from left wall toward kitchen; Y goes from D1 toward
corridor 4; Z is height. The D2 tie and camera are provisional; D2 leaf and
cabinet-door sweeps are deliberately not modelled.
"""
from __future__ import annotations

from math import cos, radians, sin, tan
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Прихожая" / "63_прихожая_C_проверка_вида_из_кухни_v35.png"
VIEW = ROOT / "Прихожая" / "63_прихожая_C_геометрия_вида_v35.png"
W, H = 1200, 1050
CAM = np.array((2350.0, 1020.0, 1600.0))
FOV = 105.0
ANGLE = radians(15.0)  # look towards D1 from the kitchen threshold
PITCH = radians(-11.0)  # include the floor and the tops of the tall doors
HOR = np.array((-cos(ANGLE), -sin(ANGLE), 0.0))
FWD = np.array((HOR[0] * cos(PITCH), HOR[1] * cos(PITCH), sin(PITCH)))
RIGHT = np.array((sin(ANGLE), -cos(ANGLE), 0.0))
UP = np.array((-HOR[0] * sin(PITCH), -HOR[1] * sin(PITCH), cos(PITCH)))
FONT = Path(r"C:\Windows\Fonts\arial.ttf")
BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


def font(size: int, bold: bool = False):
    return ImageFont.truetype(str(BOLD if bold else FONT), size)


def paint_view():
    hh = tan(radians(FOV / 2))
    xx = np.linspace(-hh, hh, W, dtype=np.float32)
    yy = np.linspace(hh * H / W, -hh * H / W, H, dtype=np.float32)
    sx, sy = np.meshgrid(xx, yy)
    rays = np.stack(tuple(FWD[i] + sx * RIGHT[i] + sy * UP[i] for i in range(3)), axis=-1)
    inv = 1.0 / np.where(abs(rays) < 1e-7, np.float32(1e-7), rays)

    depth = np.full((H, W), np.inf, np.float32)
    ids = np.zeros((H, W), np.int16)
    rgb = np.empty((H, W, 3), np.uint8)
    rgb[:] = (214, 232, 228)  # unmodelled space, never a guessed wall

    # A finite colour variation at the floor is only a visual finish, not a
    # claim about the unmeasured far end of the corridor.
    tfloor = -CAM[2] * inv[:, :, 2]
    fx = CAM[0] + tfloor * rays[:, :, 0]
    fy = CAM[1] + tfloor * rays[:, :, 1]
    floor = (tfloor > 1) & (fy > -100) & (fy < 3500) & (fx > -1800) & (fx < 4000)
    depth[floor] = tfloor[floor]
    ids[floor] = 1
    floor_tint = np.where((np.floor(fx / 180) % 2) == 0, 0, 7).astype(np.uint8)
    for c, base in enumerate((205, 190, 169)):
        rgb[:, :, c][floor] = np.clip(base + floor_tint[floor], 0, 255)

    tceil = (2750 - CAM[2]) * inv[:, :, 2]
    cx = CAM[0] + tceil * rays[:, :, 0]
    cy = CAM[1] + tceil * rays[:, :, 1]
    ceiling = (tceil > 1) & (cy > 0) & (cy < 2300) & (cx > -1000) & (cx < 4000) & (tceil < depth)
    depth[ceiling] = tceil[ceiling]
    ids[ceiling] = 2
    rgb[ceiling] = (229, 224, 215)

    def box(lo, hi, color, obj):
        lo = np.asarray(lo, np.float32)
        hi = np.asarray(hi, np.float32)
        lo_t = (lo - CAM) * inv
        hi_t = (hi - CAM) * inv
        near = np.minimum(lo_t, hi_t)
        far = np.maximum(lo_t, hi_t)
        tnear = near.max(axis=2)
        tfar = far.min(axis=2)
        hit = (tfar >= np.maximum(tnear, 0.1)) & (tnear > 0.1) & (tnear < depth)
        if not hit.any():
            return
        axis = near.argmax(axis=2)
        # Different tones for orthogonal faces make shallow objects readable.
        shade = np.choose(axis, (1.00, 0.90, 1.06))
        for channel in range(3):
            color_channel = np.clip(color[channel] * shade, 0, 255).astype(np.uint8)
            rgb[:, :, channel][hit] = color_channel[hit]
        depth[hit] = tnear[hit]
        ids[hit] = obj

    # The B01 entry fragment: do not continue the left wall across 3 -> 4.
    box((-80, 0, 0), (0, 1675, 2750), (211, 204, 193), 3)
    box((0, -80, 0), (610, 0, 2750), (218, 211, 201), 4)
    box((1620, -80, 0), (2090, 0, 2750), (218, 211, 201), 4)
    box((610, -80, 2150), (1620, 0, 2750), (218, 211, 201), 4)
    box((610, -20, 0), (1620, 5, 2150), (45, 45, 43), 5)  # B01 1010 segment

    # Kitchen partition: 910 B01, model tie from B01 drawing, NOT final U01.
    for ya, yb in ((0, 565), (1475, 1675)):
        box((2090, ya, 0), (2250, yb, 2750), (220, 214, 205), 6)
    box((2090, 565, 2150), (2250, 1475, 2750), (220, 214, 205), 6)

    # Proposed closed tall wardrobe: 850 wide along Y, 580 deep, 2700 high.
    box((0, 800, 0), (580, 1650, 2700), (167, 132, 97), 10)
    box((580, 800, 0), (586, 1650, 2700), (183, 150, 112), 11)
    box((586, 1216, 0), (589, 1222, 2700), (104, 82, 65), 12)
    # Mirror on the door nearer to the bench; its shape is not a final design.
    box((589, 830, 120), (596, 1180, 2500), (146, 172, 169), 13)
    box((589, 1480, 880), (602, 1498, 1420), (63, 58, 52), 14)

    # The 775 x 420 bench niche follows directly, next to D1.
    box((0, 25, 460), (32, 800, 2150), (129, 142, 116), 20)
    box((0, 25, 2150), (420, 800, 2700), (190, 158, 120), 21)
    box((420, 410, 2150), (426, 416, 2700), (104, 82, 65), 22)
    box((35, 25, 400), (420, 800, 425), (166, 133, 99), 23)
    box((35, 25, 425), (420, 800, 460), (221, 210, 192), 24)
    box((40, 430, 310), (418, 800, 400), (187, 155, 120), 25)  # dry slippers drawer
    for y in (180, 375, 570):
        box((33, y, 1480), (65, y + 20, 1540), (63, 61, 53), 26)
    # Restrained shoe volumes, directly on the same floor.
    for y, h, col in ((80, 270, (91, 78, 67)), (270, 130, (113, 103, 92)), (495, 120, (131, 119, 105))):
        box((120, y, 0), (365, y + 150, h), col, 27)

    # Test the number of rendered pixels to catch an accidentally missing object.
    counts = {name: int(np.count_nonzero(np.isin(ids, values))) for name, values in {
        "D1": [5], "wardrobe": [10, 11, 12, 13, 14], "bench_niche": [20, 21, 22, 23, 24, 25, 26, 27]
    }.items()}
    assert min(counts.values()) > 400, counts
    print("visible pixels:", counts)
    return Image.fromarray(rgb), counts


def rounded(d, xy, radius=20, fill="white", outline="#dce3dc", width=2):
    d.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def draw_sheet(view):
    im = Image.new("RGB", (1920, 1400), "#f0f3ee")
    d = ImageDraw.Draw(im)
    d.text((55, 34), "APT-001 / ПРИХОЖАЯ / ПРОВЕРКА ВИДА V35", font=font(18, True), fill="#357061")
    d.text((55, 69), "Что видно из кухни по плану", font=font(46, True), fill="#1c3937")
    d.text((57, 128), "B01: фрагмент 2090 × 1675 мм · мебель — эскиз C · камера у открытого D2", font=font(23), fill="#536f6d")
    rounded(d, (45, 183, 752, 1140))
    rounded(d, (770, 183, 1875, 1140))
    d.text((70, 205), "01  План и точка взгляда", font=font(25, True), fill="#1c3937")
    d.text((800, 205), "02  Проверочный объёмный вид", font=font(25, True), fill="#1c3937")
    d.text((800, 240), "Это геометрическая модель, не фотореалистичный проект", font=font(18), fill="#59716d")

    # Compact plan: origin is the left inside corner beside D1.
    ox, oy, scale = 154, 380, .230
    def p(x, y): return (ox + x * scale, oy + y * scale)
    def line(points, fill="#273e3a", width=6): d.line([p(*pt) for pt in points], fill=fill, width=width)
    def rect(box, fill, outline=None, width=1):
        x0,y0,x1,y1=box
        d.rectangle((*p(x0,y0), *p(x1,y1)), fill=fill, outline=outline, width=width)
    rect((0,0,2090,1675), "#f8f8f3")
    rect((0,25,420,800), "#cfdbc9", "#657f70", 2)
    rect((0,800,580,1650), "#cba983", "#876a4d", 2)
    line([(0,0),(0,1675)])
    line([(0,0),(610,0)])
    line([(1620,0),(2090,0)])
    line([(610,0),(1620,0)], "#222627", 8)
    line([(2090,0),(2090,565)])
    line([(2090,1475),(2090,1675)])
    # D2 is an opening, not a closed wall; marks show extent in the B01 model.
    line([(2090,565),(2090,1475)], "#ca8c2e", 3)
    d.text(p(70, 310), "БАНКЕТКА", font=font(15, True), fill="#345c4f")
    d.text(p(70, 410), "775 × 420 P", font=font(14), fill="#345c4f")
    d.text(p(70, 1050), "ШКАФ", font=font(16, True), fill="#604b38")
    d.text(p(70, 1145), "850 × 580 P", font=font(14), fill="#604b38")
    d.text((ox+150, oy-35), "D1 · 1010 B", font=font(17, True), fill="#202b2a")
    d.text((ox+25, oy-73), "610", font=font(15), fill="#445e57")
    d.text((ox+217, oy-73), "1010", font=font(15), fill="#445e57")
    d.text((ox+428, oy-73), "470", font=font(15), fill="#445e57")
    d.text((ox+135, oy-110), "2090 B = 610 + 1010 + 470", font=font(16, True), fill="#345c4f")
    d.text((ox-88, oy+185), "1675 B", font=font(15, True), fill="#345c4f")
    d.text((ox+120, oy+400), "ОТКРЫТЫЙ ПЕРЕХОД В КОРИДОР 4", font=font(15, True), fill="#467263")
    d.text((ox+120, oy+422), "его дальний контур не задан", font=font(14), fill="#6c7b73")
    # Example camera and field of view. D2 is only provisionally tied to wall.
    cp=p(CAM[0], CAM[1])
    central=p(CAM[0]-1100*cos(ANGLE), CAM[1]-1100*sin(ANGLE))
    d.line((cp, central), fill="#287c87", width=4)
    d.ellipse((cp[0]-8,cp[1]-8,cp[0]+8,cp[1]+8), fill="#287c87", outline="white", width=2)
    # A small triangular arrow head near the target is readable at plan scale.
    d.polygon(((central[0]-2,central[1]-8),(central[0]-2,central[1]+8),(central[0]-15,central[1]-3)), fill="#287c87")
    d.text((ox+480, oy+110), "D2", font=font(15, True), fill="#956721")
    d.text((ox+298, oy+495), "● пример точки камеры", font=font(14, True), fill="#287c87")
    d.text((70, 1060), "B — план БТИ · P — эскизная мебель", font=font(17), fill="#59716d")

    # The pinhole projection is generated from the same plan and labelled as a
    # single camera example. It does not claim the real FOV or exact D2 jambs.
    view_img = view.resize((930, 814), Image.Resampling.LANCZOS)
    im.paste(view_img, (856, 279))
    d.rectangle((856, 279, 1786, 1093), outline="#c8d4cb", width=2)
    d.text((810, 1107), "Пример у D2: широкий угол ≈ 105°, камера немного наклонена вниз", font=font(17), fill="#59716d")

    rounded(d, (45, 1160, 1875, 1355), fill="#fff9ef", outline="#ead3ab")
    d.text((72, 1180), "Как читать этот вид", font=font(23, True), fill="#5e4b32")
    d.text((72, 1218), "Слева — шкаф к коридору, рядом банкетка, справа — входная дверь на перпендикулярной стене.", font=font(20), fill="#5f594b")
    d.text((72, 1252), "Фасады закрыты: щит за дверцей не виден. Мятным показана неотрисованная область открытого коридора.", font=font(20), fill="#5f594b")
    d.text((72, 1286), "У D1: 610 B − 420 P = 190 мм — лишь разность на плане, не замер от коробки и не ширина прохода.", font=font(20), fill="#5f594b")
    d.text((72, 1320), "D2 и камера — пример по B01. Реальные привязки проёмов, ракурс и открывание створок ещё проверяются.", font=font(20), fill="#5f594b")
    return im


def main():
    assert 610 + 1010 + 470 == 2090
    assert 25 + 775 + 850 + 25 == 1675
    assert 2090 - 580 == 1510
    assert 565 + 910 + 200 == 1675  # illustrative tie used by the B01 model
    assert 565 < CAM[1] < 1475 and 0 < CAM[2] < 2150

    # In this camera example, the four B01 D1 corners fit the chosen image and
    # their sight lines cross the modelled aperture rather than the D2 pier.
    hh = tan(radians(FOV / 2))
    for x in (610.0, 1620.0):
        for z in (0.0, 2150.0):
            point = np.array((x, 5.0, z))
            q = point - CAM
            axial = q @ FWD
            px = W / 2 * (1 + (q @ RIGHT) / axial / hh)
            py = H / 2 - ((q @ UP) / axial) * W / (2 * hh)
            assert axial > 0 and 0 <= px < W and 0 <= py < H, (point, px, py)
        frac = (CAM[0] - 2090) / (CAM[0] - x)
        through_y = CAM[1] + frac * (5 - CAM[1])
        assert 565 < through_y < 1475, (x, through_y)
    view, counts = paint_view()
    view.save(VIEW)
    draw_sheet(view).save(OUT)
    print("view:", VIEW, "sheet:", OUT, "counts:", counts)


if __name__ == "__main__":
    main()
