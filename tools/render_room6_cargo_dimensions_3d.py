"""R05 axonometric measurements, dimension lines anchored in model coordinates."""
from __future__ import annotations

import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import render_room6_cargo_motion_r05 as m  # noqa: E402

OUT = ROOT / 'output/visuals/room6-cargo-dimensions-3d-r05.png'
ANIMATION = ROOT / 'output/visuals/room6-cargo-dimensions-3d-r05.gif'
W, H = 2400, 1750

# The same orthographic model as the movement animation, re-scaled for print.
m.SCALE = .43
m.XC = 875 - (max(m.ux) + min(m.ux)) * m.SCALE / 2
m.YC = 880 + (max(m.uy) + min(m.uy)) * m.SCALE / 2
travel = 300
robot_y = 1026
assert m.CARGO_Z - m.ROBOT_H == 616
assert m.M4_FRONT - travel == 890
assert m.CARGO_W == 264 and m.ROBOT_R * 2 == 350
assert m.DOOR_LEFT == 780 and m.W == 1730 and m.D == 1740

COLORS = {'ink': '#293C34', 'green': '#397E68', 'orange': '#B66E3D',
          'blue': '#477C92', 'muted': '#697B70', 'line': '#D0DED4'}

def font(size, bold=False):
    return ImageFont.truetype(m.FONT_BOLD if bold else m.FONT_REG, size)

def text_width(draw, text, f):
    b=draw.textbbox((0,0),text,font=f)
    return b[2]-b[0], b[3]-b[1]

def pill(draw, text, center, color, size=27):
    f=font(size,True)
    tw, th=text_width(draw,text,f)
    x,y=center
    rect=(x-tw/2-11,y-th/2-11,x+tw/2+11,y+th/2+12)
    draw.rounded_rectangle(rect, radius=9, fill='white', outline=color, width=2)
    draw.text((x-tw/2,y-th/2-5),text,font=f,fill=color)
    return rect

def arrow_head(draw, tip, other, color, length=15, half=6):
    dx,dy=other[0]-tip[0],other[1]-tip[1]
    dist=max(math.hypot(dx,dy),1)
    ux,uy=dx/dist,dy/dist
    nx,ny=-uy,ux
    draw.polygon([tip,(tip[0]+ux*length+nx*half,tip[1]+uy*length+ny*half),
                  (tip[0]+ux*length-nx*half,tip[1]+uy*length-ny*half)],fill=color)

def dimension(draw, a, b, text, label, color='green', size=27):
    pa,pb=m.proj(a),m.proj(b)
    col=COLORS[color]
    draw.line((pa,pb),fill=col,width=3)
    arrow_head(draw,pa,pb,col)
    arrow_head(draw,pb,pa,col)
    pill(draw,text,label,col,size)

def leader(draw, point, elbow, label, text, color='green', size=25):
    point=m.proj(point)
    col=COLORS[color]
    draw.line((point,elbow,label),fill=col,width=3)
    r=4
    draw.ellipse((point[0]-r,point[1]-r,point[0]+r,point[1]+r),fill=col)
    pill(draw,text,label,col,size)

def para(draw, xy, text, *, size=25, color='ink', max_w=740, leading=11, bold=False):
    f=font(size,bold); x,y=xy
    words=text.split(); line=''
    for word in words:
        trial=(line+' '+word).strip()
        if line and text_width(draw,trial,f)[0] > max_w:
            draw.text((x,y),line,font=f,fill=COLORS.get(color,color)); y+=size+leading; line=word
        else:
            line=trial
    if line:
        draw.text((x,y),line,font=f,fill=COLORS.get(color,color)); y+=size+leading
    return y

def box(draw, xy, fill='#F5F8F4', border='#D4E0D6'):
    draw.rounded_rectangle(xy,radius=20,fill=fill,outline=border,width=2)

def render(travel=300, robot_y=1026):
    im=Image.new('RGB',(W,H),'#FAFBF8')
    d=ImageDraw.Draw(im)
    d.text((55,33),'ПРАЧЕЧНАЯ  /  ПОМЕЩЕНИЕ 06  /  ЭСКИЗ R05',font=font(23,True),fill=COLORS['green'])
    d.text((55,77),'Размеры корзины и робота в объёме',font=font(43,True),fill=COLORS['ink'])
    d.text((55,138),'Вид от входа. Корзина выдвигается, робот выезжает; доска слева сложена.',font=font(23),fill=COLORS['muted'])
    d.line((55,185,W-55,185),fill=COLORS['line'],width=2)

    m.scene_at(travel,robot_y).render(d)

    # Room dimensions and opening offset: scaled 3D lines follow real model axes.
    dimension(d,(0,-160,0),(1730,-160,0),'1730 мм B',(771,1508),'blue',29)
    dimension(d,(-140,0,0),(-140,1740,0),'1740 мм B',(300,1164),'blue',29)
    dimension(d,(0,70,8),(780,70,8),'780 мм',(574,1344),'orange',27)

    # Rack opening and hypothetical stroke, placed above the corresponding edges.
    moving_front=m.M4_FRONT-travel
    dimension(d,(978,moving_front-30,1390),(1242,moving_front-30,1390),'проём 264 P',(875,677),'green',24)
    if travel >= 5:
        dimension(d,(1300,1190,1430),(1300,moving_front,1430),
                  f'вылет {round(travel)} P',(1175,641),'orange',24)

    # Elevation and vertical clearance in the plane of the path, both assumptions.
    if travel >= 250:
        dimension(d,(1320,840,0),(1320,840,720),'низ +720 P',(1040,1080),'orange',24)
        dimension(d,(1510,740,104),(1510,740,720),'зазор 616 P',(1220,1132),'green',24)

    # Product dimensions are anchored to the simulated robot; cabinet/rail model is schematic.
    rx,ry=m.proj((1238,robot_y,104))
    leader(d,(1238,robot_y,104),(rx+48,ry+40),(rx+205,ry+92),'Ø350 × 104 мм','green',23)
    leader(d,(1451,1640,280),(1260,960),(1390,965),'станция','muted',23)
    m.draw_arrow(d,m.proj((m.DOCK_AXIS,820,14)),m.proj((m.DOCK_AXIS,180,14)),COLORS['green'],5,15)

    # Explanatory panel never asserts the cabinet is ready for manufacturing.
    bx,by,bw,bh=1545,236,800,1130
    box(d,(bx,by,bx+bw,by+bh))
    x=bx+38; y=by+35
    d.text((x,y),'ЧТО ОЗНАЧАЮТ РАЗМЕРЫ',font=font(27,True),fill=COLORS['green']); y+=60
    d.text((x,y),'B  —  ПО ДАННЫМ ПЛАНА',font=font(23,True),fill=COLORS['blue']); y+=42
    y=para(d,(x,y),'Комната 1730 × 1740 мм. Фактическую геометрию после отделки нужно обмерить.',size=24); y+=14
    y=para(d,(x,y),'780 мм — от левой стены до входного проёма по вашему уточнению. Чистая ширина двери не подтверждена.',size=24); y+=25
    d.line((x,y,x+bw-76,y),fill=COLORS['line'],width=2); y+=28
    d.text((x,y),'P  —  РАСЧЁТНОЕ ПОЛОЖЕНИЕ',font=font(23,True),fill=COLORS['orange']); y+=42
    y=para(d,(x,y),'Карго: проём 264 × 350 × 600 мм. Ширина самой корзины по вашему фото — 220 мм снаружи.',size=24); y+=13
    y=para(d,(x,y),'Вылет 300 мм принят для модели: фактический ход продавец пока не подтвердил.',size=24); y+=13
    y=para(d,(x,y),'720 мм — предполагаемая нижняя точка карго от пола. Она должна включать все направляющие и крепления.',size=24); y+=26
    d.line((x,y,x+bw-76,y),fill=COLORS['line'],width=2); y+=28
    d.text((x,y),'РОБОТ И СТАНЦИЯ',font=font(23,True),fill=COLORS['green']); y+=42
    y=para(d,(x,y),'Робот Dreame X40 Master: 350 × 350 × 103,8 мм; в расчёте высота округлена до 104 мм.',size=24); y+=13
    y=para(d,(x,y),'616 мм = 720 − 104. Это высотный запас только при отсутствии деталей карго ниже +720 мм.',size=24); y+=13
    y=para(d,(x,y),'Станция 426 × 485 × 280 мм показана упрощённо. Порог, опоры, люк и маршрут требуется проверить.',size=24)
    assert y < by+bh-20, (y,by+bh)

    box(d,(55,1572,W-55,1690),fill='#FFF7EF',border='#E8D3C0')
    d.text((78,1593),'СХЕМА ДЛЯ ПРОВЕРКИ, НЕ ЧЕРТЁЖ ДЛЯ ЗАКАЗА',font=font(23,True),fill=COLORS['orange'])
    d.text((78,1631),'Уточнить ход корзины, нижнюю точку креплений, проём двери и допустимость станции в помещении.',
           font=font(24),fill=COLORS['ink'])
    d.text((55,1715),'B  исходный план   •   P  проектное / расчётное значение   •   размеры в миллиметрах',
           font=font(19),fill=COLORS['muted'])
    return im

def main():
    for p in (OUT,ANIMATION):
        if p.exists():
            raise FileExistsError(p)
    OUT.parent.mkdir(parents=True,exist_ok=True)
    render().save(OUT,optimize=True)
    frames=[]
    for i in range(30):
        if i < 10:
            travel=300*m.smooth(i/9)
            robot_y=1350
        else:
            travel=300
            robot_y=1350-850*m.smooth((i-10)/15)
        image=render(travel,robot_y).resize((1600,1167),Image.Resampling.LANCZOS)
        frames.append(image.convert('P',palette=Image.Palette.ADAPTIVE,colors=160))
    frames[0].save(ANIMATION,save_all=True,append_images=frames[1:],
                   duration=200,loop=0,optimize=True,disposal=2)
    print(OUT)
    print(ANIMATION)

if __name__ == '__main__':
    main()
