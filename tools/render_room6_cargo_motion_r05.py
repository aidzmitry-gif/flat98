"""Dimension-based axonometric R05 laundry illustration and animation.

Coordinates are millimetres: x is left-to-right looking from D3, y runs from
the entrance plane towards the far wall and z is height above finished floor.
The rack stroke and lower-most height are explicitly hypothetical. This is a
geometric scenario, not a checked installation or a robot navigation test.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tmp/pdfs'))
from create_room6_far_wall_r05 import (  # noqa: E402
    BASIN_AXIS, BASIN_W, CARGO_D, CARGO_H, CARGO_W, CARGO_X, CARGO_Z, D,
    DOCK_AXIS, DOOR_LEFT, DOOR_RIGHT, FRONT, M2_W, M2_X, M4_FRONT, W,
)

OUT = ROOT / 'output' / 'visuals'
STILL = OUT / 'room6-cargo-robot-3d-r05.png'
GIF = OUT / 'room6-cargo-robot-3d-r05.gif'
WIDTH, HEIGHT = 1760, 1040
TRAVEL = 300
ROBOT_R, ROBOT_H = 175, 104
DOCK_FRONT, DOCK_BACK, DOCK_HEIGHT = M4_FRONT, M4_FRONT + 485, 280
assert (W, D, DOOR_LEFT, DOOR_RIGHT) == (1730, 1740, 780, 1590)
assert (CARGO_X, CARGO_W, CARGO_D, CARGO_Z, CARGO_H) == (978, 264, 350, 720, 600)
assert M4_FRONT - TRAVEL == 890 and CARGO_Z - ROBOT_H == 616
assert DOOR_LEFT < DOCK_AXIS - ROBOT_R < DOCK_AXIS + ROBOT_R < DOOR_RIGHT

FONT_REG = 'C:/Windows/Fonts/arial.ttf'
FONT_BOLD = 'C:/Windows/Fonts/arialbd.ttf'
def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

def rgba(c):
    c = c.lstrip('#')
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))

def shade(color, factor):
    return tuple(max(0, min(255, round(v * factor))) for v in rgba(color))

def norm(v):
    v = np.asarray(v, dtype=float)
    return v / np.linalg.norm(v)

CAMERA = np.array([2500.0, -5500.0, 4450.0])
TARGET = np.array([870.0, 870.0, 700.0])
FORWARD = norm(TARGET - CAMERA)
RIGHT = norm(np.cross(FORWARD, [0, 0, 1]))
UP = norm(np.cross(RIGHT, FORWARD))

def plane(point):
    p = np.asarray(point, dtype=float) - TARGET
    return float(p @ RIGHT), float(p @ UP)

limits = [plane((x, y, z)) for x in (0, W) for y in (-120, D) for z in (0, 1900)]
ux = [p[0] for p in limits]
uy = [p[1] for p in limits]
SCALE = min(960 / (max(ux) - min(ux)), 690 / (max(uy) - min(uy)))
XC = 544 - (max(ux) + min(ux)) * SCALE / 2
YC = 570 + (max(uy) + min(uy)) * SCALE / 2

def proj(point):
    a, b = plane(point)
    return XC + a * SCALE, YC - b * SCALE

def depth(points):
    return float((np.mean(np.asarray(points, dtype=float), axis=0) - CAMERA) @ FORWARD)

class Scene:
    def __init__(self):
        self.shapes = []

    def poly(self, points, color, edge='#7E887F', width=1, bias=0):
        self.shapes.append((depth(points) + bias, points, color, edge, width))

    def box(self, a, b, color, edge='#8A938A', bias=0):
        x1, y1, z1 = a
        x2, y2, z2 = b
        p000, p100, p010, p110 = (x1,y1,z1), (x2,y1,z1), (x1,y2,z1), (x2,y2,z1)
        p001, p101, p011, p111 = (x1,y1,z2), (x2,y1,z2), (x1,y2,z2), (x2,y2,z2)
        for pts, factor in (([p000,p100,p101,p001], .91),
                            ([p100,p110,p111,p101], .79),
                            ([p010,p110,p111,p011], .84),
                            ([p000,p010,p011,p001], .88),
                            ([p001,p101,p111,p011], 1.08)):
            self.poly(pts, shade(color, factor), edge, bias=bias)

    def cylinder(self, cx, cy, z, radius, height, color, edge='#53645C', n=24):
        base = [(cx+radius*math.cos(2*math.pi*i/n), cy+radius*math.sin(2*math.pi*i/n), z)
                for i in range(n)]
        top = [(x,y,z+height) for x,y,_ in base]
        for i in range(n):
            a = 2 * math.pi * (i + .5) / n
            fac = .83 + .17 * max(0, math.cos(a - 1.4))
            self.poly([base[i], base[(i+1)%n], top[(i+1)%n], top[i]], shade(color, fac), edge)
        self.poly(top, shade(color, 1.10), edge)

    def front_disk(self, cx, y, zc, radius, color, edge):
        pts = [(cx+radius*math.cos(2*math.pi*i/36), y, zc+radius*math.sin(2*math.pi*i/36))
               for i in range(36)]
        self.poly(pts, rgba(color), edge, 2, bias=-35)

    def render(self, draw):
        for _, pts, color, edge, width in sorted(self.shapes, key=lambda q: q[0], reverse=True):
            draw.polygon([proj(p) for p in pts], fill=color, outline=rgba(edge), width=width)

def scene_at(travel, robot_y):
    s = Scene()
    # Cutaway floor and three room boundaries. Entrance wall is cut down to a low curb.
    s.box((0,0,-28), (W,D,0), '#ECE9E0', '#B2B9B0', bias=10000)
    s.box((-18,0,0), (0,D,85), '#C4C6BF')
    s.box((W,0,0), (W+18,D,85), '#C4C6BF')
    s.box((0,D,0), (W,D+18,1900), '#E7E4DC', '#C1C7BE', bias=10000)
    s.box((0,-18,0), (DOOR_LEFT,0,85), '#BEC2BA')
    s.box((DOOR_RIGHT,-18,0), (W,0,85), '#BEC2BA')

    # Left bay: illustrative folded board; no pivot geometry is implied.
    for a,b in (((20,FRONT,0),(38,D,1850)), ((302,FRONT,0),(320,D,1850)),
                ((38,D-18,0),(302,D,1850)), ((38,FRONT,1750),(302,D,1768))):
        s.box(a,b,'#D4BC99','#A78D6B')
    s.box((160,1335,820),(205,1645,1620),'#E3DBCD','#9A9E91')

    # Actual exterior sizes, with the 92 mm frame allowance from the project.
    x1, x2 = M2_X + 22.5, M2_X + 22.5 + 595
    s.box((x1,FRONT,0),(x2,FRONT+583,850),'#F4F5F2','#9CA6A1')
    s.box((x1,FRONT,850),(x2,FRONT+593,942),'#C9D0CA','#899A90')
    s.box((x1,FRONT,942),(x2,FRONT+593,1787),'#F4F5F2','#9CA6A1')
    for center in (410, 1352):
        s.front_disk(640, FRONT-2, center, 218, '#C8D3CE', '#677F77')
        s.front_disk(640, FRONT-4, center, 185, '#566C67', '#D2DCD5')
        s.front_disk(640, FRONT-6, center, 139, '#78928A', '#536A64')

    # Station: front opening remains clear for the 350 mm robot; support shown schematically.
    dock_l, dock_r = DOCK_AXIS-213, DOCK_AXIS+213
    s.box((dock_l,DOCK_FRONT,0),(dock_l+28,DOCK_BACK,DOCK_HEIGHT),'#43534D')
    s.box((dock_r-28,DOCK_FRONT,0),(dock_r,DOCK_BACK,DOCK_HEIGHT),'#43534D')
    s.box((dock_l,DOCK_BACK-60,0),(dock_r,DOCK_BACK,DOCK_HEIGHT),'#43534D')
    s.box((dock_l,DOCK_FRONT,180),(dock_r,DOCK_BACK,DOCK_HEIGHT),'#43534D')

    # Basin envelope and bronze faucet. Services and detailed fixing remain unspecified.
    basin_l, basin_r = BASIN_AXIS-BASIN_W/2, BASIN_AXIS+BASIN_W/2
    s.box((basin_l,1210,730),(basin_r,1530,870),'#FBFCFA','#9AA8A1')
    s.box((basin_l+38,1250,866),(basin_r-38,1494,871),'#D9E4DF','#B1BEB7')
    s.box((1545,1490,870),(1570,1518,1055),'#A47948','#725032')
    s.box((1475,1485,1035),(1570,1518,1055),'#A47948','#725032')

    # One fixed slide on the reinforced cabinet and the two moving trays.
    s.box((CARGO_X, M4_FRONT, 730),(CARGO_X+16,M4_FRONT+CARGO_D,750),'#859C91')
    front = M4_FRONT - travel
    back = front + CARGO_D
    left, right = CARGO_X, CARGO_X+CARGO_W
    s.box((left,front,720),(left+14,front+14,1320),'#5A786C')
    s.box((left,back-14,720),(left+14,back,1320),'#5A786C')
    s.box((right-14,front,720),(right,front+14,1320),'#5A786C')
    s.box((right-14,back-14,720),(right,back,1320),'#5A786C')
    for z in (750, 1040):
        s.box((left+22,front+18,z),(right-22,back-18,z+26),'#78998B')
        s.box((left+22,front+18,z+26),(right-22,front+31,z+84),'#78998B')
        s.box((left+22,back-31,z+26),(right-22,back-18,z+84),'#78998B')
    # Bottles are illustrative and remain within the rack's assumed overall volume.
    for cx, cy, z, r, h, col in ((1043,front+115,776,35,166,'#D6CEAA'),
                                  (1135,front+220,776,30,185,'#ECECE5'),
                                  (1058,front+105,1066,30,146,'#D7E5DD'),
                                  (1147,front+215,1066,29,153,'#F1EEE6')):
        s.cylinder(cx,cy,z,r,h,col,'#879A90',16)

    # Robot dimensions and path are nominal. The simulation is not a navigation test.
    s.cylinder(DOCK_AXIS, robot_y, 0, ROBOT_R, ROBOT_H, '#729A8C', '#456A5E', 32)
    s.cylinder(DOCK_AXIS, robot_y+10, ROBOT_H-6, 64, 6, '#587E71', '#456A5E', 24)
    return s

def rounded(draw, rect, fill, outline, radius=20, width=2):
    draw.rounded_rectangle(rect, radius=radius, fill=fill, outline=outline, width=width)

def draw_arrow(draw, start, end, fill, width=5, head=14):
    draw.line([start,end], fill=fill, width=width)
    dx,dy = end[0]-start[0],end[1]-start[1]
    length=max(math.hypot(dx,dy),1)
    ux,uy=dx/length,dy/length
    px,py=-uy,ux
    draw.polygon([end, (end[0]-ux*head+px*head*.6,end[1]-uy*head+py*head*.6),
                  (end[0]-ux*head-px*head*.6,end[1]-uy*head-py*head*.6)], fill=fill)

def dim_vertical(draw, x, y1, y2, text, color):
    draw.line((x,y1,x,y2), fill=color, width=2)
    draw.line((x-7,y1,x+7,y1), fill=color, width=2)
    draw.line((x-7,y2,x+7,y2), fill=color, width=2)
    draw.text((x+9,(y1+y2)/2-12),text,font=font(20,True),fill=color)

def side_view(draw, travel, robot_y):
    # Same 3D coordinates projected onto a longitudinal vertical plane.
    x0,y0,sc = 1190, 694, .295
    sx=lambda t:x0+t*sc
    sy=lambda t:y0-t*sc
    dark=(49,65,58); green=(58,115,94); brown=(144,101,59)
    draw.text((1098,200),'ТО ЖЕ САМОЕ СБОКУ',font=font(21,True),fill=dark)
    draw.text((1098,231),'Вход слева → дальняя стена справа',font=font(16),fill=(104,116,108))
    draw.line((sx(0),sy(0),sx(D),sy(0)),fill=dark,width=3)
    draw.line((sx(D),sy(0),sx(D),sy(1450)),fill=dark,width=3)
    # Static cabinet face and shelf.
    draw.rectangle((sx(M4_FRONT),sy(1430),sx(D),sy(1410)),fill=(205,180,145),outline=brown,width=2)
    draw.line((sx(M4_FRONT),sy(0),sx(M4_FRONT),sy(1450)),fill=(177,188,180),width=1)
    draw.rectangle((sx(DOCK_FRONT),sy(DOCK_HEIGHT),sx(DOCK_BACK),sy(0)),fill=(56,73,66),outline=dark,width=2)
    draw.text((sx(DOCK_FRONT)+18,sy(185)),'СТАНЦИЯ',font=font(15,True),fill='white')
    # Closed outline and moving rack volume.
    for z in (CARGO_Z,CARGO_Z+CARGO_H):
        dash_line(draw,(sx(M4_FRONT),sy(z)),(sx(M4_FRONT+CARGO_D),sy(z)),(93,135,115),3,7)
    for d in (M4_FRONT,M4_FRONT+CARGO_D):
        dash_line(draw,(sx(d),sy(CARGO_Z)),(sx(d),sy(CARGO_Z+CARGO_H)),(93,135,115),3,7)
    front=M4_FRONT-travel
    draw.rectangle((sx(front),sy(CARGO_Z+CARGO_H),sx(front+CARGO_D),sy(CARGO_Z)),
                   fill=(206,227,214),outline=green,width=3)
    for z in (750,1040):
        draw.rectangle((sx(front+12),sy(z+35),sx(front+CARGO_D-12),sy(z)),fill=(85,134,111))
    draw.text((sx(front)+19,sy(1210)),'КОРЗИНА',font=font(15,True),fill=green)
    draw.rounded_rectangle((sx(robot_y-ROBOT_R),sy(ROBOT_H),sx(robot_y+ROBOT_R),sy(0)),
                           radius=10,fill=(104,148,130),outline=green,width=2)
    draw.text((sx(robot_y)-20,sy(72)),'РОБОТ',font=font(13,True),fill='white')
    # Height dimension refers to assumed lowest rack point, not a physical measurement.
    dim_vertical(draw,sx(1040),sy(CARGO_Z),sy(ROBOT_H),'616 мм*',green)
    draw.text((sx(0),sy(0)+14),'ВХОД',font=font(15,True),fill=dark)
    draw.text((sx(D)-105,sy(0)+14),'ДАЛЬНЯЯ\nСТЕНА',font=font(14,True),fill=dark,spacing=2)
    draw_arrow(draw,(sx(M4_FRONT),sy(1360)),(sx(front),sy(1360)),green,3,10)
    draw.text((sx(front)-10,sy(1435)-25),'300 мм*',font=font(19,True),fill=green)

def dash_line(draw,a,b,color,width=2,step=9):
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=math.hypot(dx,dy)
    if length == 0: return
    count=int(length//(step*2))+1
    for i in range(count):
        t0=min(1,(i*step*2)/length); t1=min(1,(i*step*2+step)/length)
        draw.line((a[0]+dx*t0,a[1]+dy*t0,a[0]+dx*t1,a[1]+dy*t1),fill=color,width=width)

def frame(travel, robot_y, stage):
    im=Image.new('RGB',(WIDTH,HEIGHT),'#FAFBF8')
    d=ImageDraw.Draw(im)
    d.text((44,27),'ПРАЧЕЧНАЯ  /  ПОМЕЩЕНИЕ 06',font=font(19,True),fill='#477667')
    d.text((44,60),'Как корзина выдвигается и робот проезжает под ней',font=font(34,True),fill='#293C34')
    d.text((44,110),'3D-схема по плану R05 • вид от входа • размеры в миллиметрах',font=font(19),fill='#6E7D74')
    d.line((44,150,WIDTH-44,150),fill='#CFD9D2',width=2)
    d.text((54,175),'01   ВИД В ОБЪЁМЕ',font=font(21,True),fill='#3F7764')
    d.text((54,204),stage,font=font(19),fill='#A67843')
    scene_at(travel,robot_y).render(d)

    # Direction arrows in projected 3D space.
    front=M4_FRONT-travel
    if travel > 20:
        draw_arrow(d,proj((CARGO_X+140,M4_FRONT,1390)),
                   proj((CARGO_X+140,front,1390)),'#BF8550',4,12)
    draw_arrow(d,proj((DOCK_AXIS,820,24)),proj((DOCK_AXIS,180,24)),'#37816D',5,13)

    rounded(d,(1080,170,1720,770),'#FFFFFF','#D3DED6',20,2)
    side_view(d,travel,robot_y)
    rounded(d,(1080,794,1720,980),'#F1F6F1','#D3DED6',18,2)
    d.text((1100,810),'РАЗМЕРЫ И ДОПУЩЕНИЯ',font=font(19,True),fill='#3F7764')
    lines=['Корзина: низ не ниже +720 мм*',
           'Робот: Ø350 × 104 мм',
           'Запас по высоте: 720 − 104 = 616 мм*',
           'Выдвижение 300 мм* — для расчёта',
           'От левой стены до D3: 780 мм']
    for i,line in enumerate(lines):
        d.text((1100,842+i*25),line,font=font(18),fill='#344C41')
    d.text((44,930),'* Не обмер: фактический ход и нижнюю точку механизма подтвердить у продавца.',
           font=font(18,True),fill='#9A623B')
    d.text((44,958),'Нужны проверка порога, опор, открытия люка и условий установки станции.',
           font=font(17),fill='#6C7C71')
    return im

def smooth(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

def main():
    for path in (STILL, GIF):
        if path.exists():
            raise FileExistsError(path)
    OUT.mkdir(parents=True, exist_ok=True)
    # Drawer moves first. The robot then drives from the dock towards the entrance.
    frames=[]
    for i in range(36):
        if i < 12:
            travel=TRAVEL*smooth(i/11)
            robot_y=1350
            stage='ШАГ 1  /  КОРЗИНА ВЫДВИГАЕТСЯ'
        else:
            travel=TRAVEL
            robot_y=1350 - 1500*smooth((i-12)/20)
            stage='ШАГ 2  /  РОБОТ ВЫЕЗЖАЕТ К ДВЕРИ'
        image=frame(travel,robot_y,stage)
        if i==18:
            image.save(STILL,optimize=True)
        frames.append(image.convert('P',palette=Image.Palette.ADAPTIVE,colors=160))
    frames[0].save(GIF,save_all=True,append_images=frames[1:],duration=160,loop=0,optimize=True,disposal=2)
    print(STILL)
    print(GIF)

if __name__ == '__main__':
    main()
