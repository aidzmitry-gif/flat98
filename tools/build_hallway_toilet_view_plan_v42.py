"""APT-001 B01 orientation diagram for the view from toilet D4.

The plan is a simplified, labelled fragment, not a measured corridor outline.
Coordinates follow the detailed B01 project model; the real D4 clear opening,
camera tie, D1/D2 corner ties and complete corridor contour remain unverified.
"""
from __future__ import annotations
import base64
from html import escape
from math import sin,cos,atan2,radians
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/"Прихожая"
PHOTO=DIR/"80_прихожая_вид_от_туалета_v42.png"
SVG=DIR/"82_прихожая_от_туалета_все_проходы_v42.svg"
img=base64.b64encode(PHOTO.read_bytes()).decode("ascii")

assert 610+1010+470==2090
assert 760+810+520==2090
assert 25+575+1050+25==1675

parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1550" viewBox="0 0 2400 1550">
<defs><clipPath id="plan"><rect x="55" y="275" width="1510" height="850" rx="8"/></clipPath></defs>
<style>text{{font-family:Arial,'Segoe UI',sans-serif;fill:#203e38}}.eyebrow{{font-size:19px;font-weight:bold;letter-spacing:2px;fill:#397761}}.title{{font-size:46px;font-weight:bold}}.subtitle{{font-size:22px;fill:#647e74}}.head{{font-size:27px;font-weight:bold}}.body{{font-size:21px;fill:#415d52}}.small{{font-size:18px;fill:#61796f}}.label{{font-size:19px;font-weight:bold;fill:#315c4c}}.num{{font-size:18px;font-weight:bold;fill:white}}</style>
<rect width="2400" height="1550" fill="#f1f4ef"/>
<text x="45" y="48" class="eyebrow">APT-001 / ПРИХОЖАЯ / ВИД ОТ ТУАЛЕТА · V42</text>
<text x="45" y="106" class="title">От туалета к входной двери: где проходят маршруты</text>
<text x="48" y="149" class="subtitle">Точка у порога D4 — условная; схема показывает связи, не утверждая полный контур коридора</text>
<rect x="40" y="185" width="1540" height="1010" rx="20" fill="white" stroke="#dae4db" stroke-width="2"/>
<rect x="1595" y="185" width="765" height="1010" rx="20" fill="white" stroke="#dae4db" stroke-width="2"/>
<text x="68" y="227" class="head">01  План и пример точки взгляда</text>
<text x="70" y="258" class="small">Широкий угол около 120°; дверные полотна на схеме не показаны</text>
<text x="1623" y="227" class="head">02  Вид от двери туалета</text>
<text x="1625" y="258" class="small">Рендер условный; поворот головы меняет видимые проходы</text>
<image x="1624" y="278" width="706" height="618" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{img}"/>
''']

def raw(s):parts.append(s+"\n")
def txt(x,y,t,cls="body",anchor="start",extra=""):
    raw(f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}" {extra}>{escape(t)}</text>')
def rect(x,y,w,h,fill,stroke="none",sw=1,extra=""):
    raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
def line(x1,y1,x2,y2,color="#314b40",width=5,extra=""):
    raw(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}" {extra}/>')
def circle(x,y,r,fill):raw(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r:.2f}" fill="{fill}"/>')
def bubble(n,x,y,color="#34765f"):
    circle(x,y,17,color)
    txt(x,y+6,str(n),"num","middle")

OX,OY,S=590.0,345.0,.195
def p(x,y):return OX+x*S,OY+y*S
def lworld(a,b,color="#314b40",width=5,extra=""):
    ax,ay=p(*a); bx,by=p(*b); line(ax,ay,bx,by,color,width,extra)
def rw(x,y,w,h,fill,stroke="none",sw=1,extra=""):
    px,py=p(x,y);rect(px,py,w*S,h*S,fill,stroke,sw,extra)

# Shade a connected zone without drawing a fabricated perimeter.
rw(-2030,1675,6140,1270,"#f2f6f2")
rw(0,0,2090,1675,"#f9f9f5")
rw(2250,0,1700,1675,"#f5f2e9","#d7d9d1",1,'stroke-dasharray="6 6"')
txt(*p(2460,700),"КУХНЯ 1","label")

# View cone from a provisional point inside the B01 D4 segment.
cam=(1375.0,2945.0);centre=atan2(1115.0-cam[0],2945.0)
left=centre-radians(60);right=centre+radians(60);radius=8000.0
left_pt=(cam[0]+sin(left)*radius,cam[1]-cos(left)*radius)
right_pt=(cam[0]+sin(right)*radius,cam[1]-cos(right)*radius)
cp=p(*cam);la=p(*left_pt);ra=p(*right_pt)
raw(f'<g clip-path="url(#plan)"><path d="M{cp[0]:.2f} {cp[1]:.2f} L{la[0]:.2f} {la[1]:.2f} L{ra[0]:.2f} {ra[1]:.2f} Z" fill="#70aa98" opacity=".13"/>')
line(cp[0],cp[1],la[0],la[1],"#6f9f8c",2,'stroke-dasharray="10 8"')
line(cp[0],cp[1],ra[0],ra[1],"#6f9f8c",2,'stroke-dasharray="10 8"')
raw('</g>')

# Entry walls D1 and D2; no wall across the entry-to-corridor transition.
lworld((0,0),(0,1675)); lworld((0,0),(610,0)); lworld((1620,0),(2090,0))
lworld((610,0),(1620,0),"#222a27",8)
lworld((2090,0),(2090,565));lworld((2090,1475),(2090,1675))
lworld((2090,565),(2090,1475),"#be8937",3,'stroke-dasharray="10 6"')

# Current proposed furniture. The service bay remains at the corridor end.
rw(0,25,420,575,"#dceadd","#91ae9b",2)
rw(0,600,580,1050,"#d9bd98","#987d5e",2)
lworld((0,1068),(580,1068),"#a1866b",2)
txt(*p(75,230),"БАНКЕТКА","small")
txt(*p(80,850),"ОДЕЖДА","small")
txt(*p(110,1400),"ЩИТ","small")
txt(*p(250,1830),"3 ↔ 4: открыто","small")

# P6 on the bedroom wall and P2 towards the child's room are true openings,
# with local limits derived from B01 chains. No invented upper corridor wall.
lworld((-2030,1675),(-2030,1875));lworld((-2030,2815),(-2030,2945))
lworld((4110,1675),(4110,1875));lworld((4110,2785),(4110,2945))

# Lower room frontage: D5, D4, D3 are gaps in the same wall chain, not extra
# visible doors in the image. Fill only a shallow strip of the rooms for context.
for x,w,label in ((-1900,1740,"ГАРДЕРОБНАЯ 8"),(0,2090,"ТУАЛЕТ 7"),(2250,1730,"ВАННАЯ 6")):
    rw(x,2945,w,610,"#f7f3ec")
    cx,cy=p(x+w/2,3380);txt(cx,cy,label,"label","middle")
for a,b in (((-1900,2945),(-1500,2945)),((-790,2945),(-160,2945)),
            ((0,2945),(760,2945)),((1570,2945),(2090,2945)),
            ((2250,2945),(2390,2945)),((3200,2945),(3980,2945))):lworld(a,b)
lworld((-1500,2945),(-790,2945),"#bd893b",3,'stroke-dasharray="8 6"')
lworld((760,2945),(1570,2945),"#34765f",4,'stroke-dasharray="8 6"')
lworld((2390,2945),(3200,2945),"#bd893b",3,'stroke-dasharray="8 6"')

# Camera location and directly visible features, matching the image labels.
circle(cp[0],cp[1],9,"#237b80")
cx,cy=p(1115,0);bubble(1,cx,cy-28)
cx,cy=p(2090,1020);bubble(2,cx+30,cy)
cx,cy=p(550,1450);bubble(3,cx+12,cy)
txt(200,702,"← P6", "label")
txt(85,728,"спальня 5", "small")
txt(1385,704,"→ P2", "label")
txt(1385,730,"детская 2", "small")
cx,cy=p(-1145,2890);txt(cx,cy,"D5", "small","middle")
cx,cy=p(1120,2890);txt(cx,cy,"D4", "small","middle")
cx,cy=p(2795,2890);txt(cx,cy,"D3", "small","middle")
txt(700,1092,"● камера в проёме D4, пример", "small")
txt(699,1122,"B01: D4 810; контроль 705 × 2027 — отдельно.", "small")
txt(700,1152,"Петли, чистые привязки и контур коридора — уточнить.", "small")

# Corresponding marks in the illustrative photograph.
photo_x,photo_y,photo_w,photo_h=1624.0,278.0,706.0,618.0
def photo_point(x,y):return photo_x+x/1341*photo_w,photo_y+y/1173*photo_h
for n,xy in ((1,(770,500)),(2,(960,480)),(3,(380,460))):
    x,y=photo_point(*xy);bubble(n,x,y)
txt(1625,936,"1  Входная дверь D1 — впереди", "body")
txt(1625,971,"2  Проход в кухню D2 — справа", "body")
txt(1625,1006,"3  Шкаф — слева; банкетка частично за ним", "body")
txt(1625,1060,"D5 и D3 — у стороны туалета, вне кадра.", "body")
txt(1625,1094,"P6 и P2 — в боковых направлениях коридора.", "body")
txt(1625,1137,"Все двери одновременно в такой кадр не попадают.", "small")

rect(40,1213,2320,285,"#fff9ef","#ead4ad",2,'rx="18"')
txt(68,1255,"Как пользоваться схемой", "head")
txt(68,1294,"На рендере видны вход D1 и часть проёма D2. Гардеробная D5 и ванная D3 расположены сбоку/позади наблюдателя.", "body")
txt(68,1332,"К спальне P6 и детской P2 коридор уходит по сторонам: для них нужно повернуть голову или сменить точку съёмки.", "body")
txt(68,1370,"Шкаф 1050 × 580 мм и банкетка 575 × 420 мм — эскиз. Распахивание, доступ к щитку и ширины проходов не проверены.", "body")
txt(68,1408,"D1: 610 + 1010 + 470 = 2090 мм по B01; контроль 1140 × 2150 мм не привязан к углам. Точная геометрия коридора неизвестна.", "small")
txt(68,1444,"Визуализация основана на геометрической модели и снимке F08; боковые неизвестные зоны размыты.", "small")
raw('</svg>')
data="".join(parts);ET.fromstring(data);SVG.write_text(data,encoding="utf-8")
print("Saved:",SVG,"bytes:",SVG.stat().st_size)
