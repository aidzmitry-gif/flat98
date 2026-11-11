"""Dimension callouts on the APT-001 v40 view as a separate SVG document.

The source photo is embedded unchanged. Leader lines identify objects; they are
not physical dimension lines on the perspective image. Unknown interior depths,
heights and actual electrical-board dimensions remain explicitly unknown.
"""
from __future__ import annotations

import base64
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Прихожая"/"77_прихожая_все_размеры_на_виде_v41.svg"
PHOTO=ROOT/"Прихожая"/"75_прихожая_кухня_щит550_v40.png"

assert 25+1050+575+25==1675
assert 550+446+3*18==1050
assert 574+470+3*2==1050
assert 2*284.5+3*2==575
assert 460-35-25==400 and 400-90==310

img=base64.b64encode(PHOTO.read_bytes()).decode("ascii")
X,Y,W=395.0,210.0,1695.0
S=W/1341.0
H=1173*S
parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="2500" height="1910" viewBox="0 0 2500 1910">
<style>
 text{{font-family:Arial,'Segoe UI',sans-serif;fill:#213e39}}
 .eyebrow{{font-size:19px;font-weight:bold;letter-spacing:2px;fill:#397461}}
 .title{{font-size:46px;font-weight:bold}}
 .subtitle{{font-size:23px;fill:#627c73}}
 .cardhead{{font-size:22px;font-weight:bold;fill:#254f40}}
 .body{{font-size:21px;fill:#3c554e}}
 .small{{font-size:18px;fill:#60766e}}
 .number{{font-size:21px;font-weight:bold;fill:white}}
</style>
<rect width="2500" height="1910" fill="#f1f4ef"/>
<text x="40" y="48" class="eyebrow">APT-001 / ПРИХОЖАЯ / ВАРИАНТ C · V41</text>
<text x="40" y="105" class="title">Размеры на виде из кухни</text>
<text x="42" y="150" class="subtitle">Все мебельные размеры — предварительные · ширина вдоль стены · глубина от стены · высота от пола</text>
<rect x="{X-4:.2f}" y="{Y-4:.2f}" width="{W+8:.2f}" height="{H+8:.2f}" rx="12" fill="#fff" stroke="#d1ddd4" stroke-width="2"/>
<image x="{X:.2f}" y="{Y:.2f}" width="{W:.2f}" height="{H:.2f}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{img}"/>
''']


def add(s):parts.append(s+"\n")
def point(px,py):return X+px*S,Y+py*S
def leader(x,y,px,py):
    ex,ey=point(px,py)
    # Two strokes make leaders legible over both the light floor and dark door.
    add(f'<path d="M{x:.2f} {y:.2f} L{ex:.2f} {ey:.2f}" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round"/>')
    add(f'<path d="M{x:.2f} {y:.2f} L{ex:.2f} {ey:.2f}" fill="none" stroke="#34765f" stroke-width="2.5" stroke-linecap="round"/>')
def marker(n,px,py):
    x,y=point(px,py)
    add(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="19" fill="#286f58" stroke="#fff" stroke-width="3"/><text x="{x:.2f}" y="{y+7:.2f}" text-anchor="middle" class="number">{n}</text>')
def card(x,y,w,h,n,title,lines):
    add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="15" fill="#fff" stroke="#d5e2d7" stroke-width="2"/>')
    add(f'<circle cx="{x+29}" cy="{y+31}" r="17" fill="#34765f"/><text x="{x+29}" y="{y+38}" text-anchor="middle" class="number">{n}</text>')
    add(f'<text x="{x+56}" y="{y+39}" class="cardhead">{escape(title)}</text>')
    for j,(line,small) in enumerate(lines):
        cls="small" if small else "body"
        add(f'<text x="{x+18}" y="{y+79+j*34}" class="{cls}">{escape(line)}</text>')


items=[
 (1,370,326,480,120),
 (2,370,605,430,620),
 (3,370,922,560,600),
 (4,2115,326,770,260),
 (5,2115,595,790,760),
 (6,2115,855,730,835),
 (7,2115,1122,790,950),
]
for _,x,y,px,py in items:leader(x,y,px,py)
for n,_,_,px,py in items:marker(n,px,py)

card(28,210,342,245,1,"Шкаф целиком",[
 ("Ширина: 1050 мм",False),
 ("Глубина: 580 мм",False),
 ("Высота: 2700 мм",False),
 ("Габарит корпуса, P.",True),
 ("Глубина с закрытым фасадом.",True),
])
card(28,490,342,260,2,"Отделение щита",[
 ("Внутренняя ширина: 550 мм",False),
 ("Фасад: ≈574 мм*",False),
 ("Внутренние высота и",True),
 ("глубина пока не заданы.",True),
 ("Размер самого щитка — M.",True),
])
card(28,785,342,330,3,"Отделение курток",[
 ("Внутренняя ширина: 446 мм",False),
 ("Фасад: ≈470 мм*",False),
 ("Штанга: h = 1750 мм",False),
 ("Верхняя полка: h = 2150 мм",False),
 ("Нижняя полка: h = 380 мм",False),
 ("Полезные высота и глубина",True),
 ("отделения не заданы.",True),
])
card(2115,210,357,245,4,"Верх над банкеткой",[
 ("Ширина: 575 мм",False),
 ("Глубина: 420 мм",False),
 ("Высота: 550 мм",False),
 ("Низ модуля: h = 2150 мм.",True),
 ("Два фасада ≈284,5 мм*.",True),
])
card(2115,490,357,245,5,"Банкетка",[
 ("Ширина: 575 мм",False),
 ("Глубина: 420 мм",False),
 ("Высота сиденья: 460 мм",False),
 ("Размеры наружные, P.",True),
])
card(2115,770,357,245,6,"Ящик для тапочек",[
 ("Ширина: 250 мм",False),
 ("Глубина: 380 мм",False),
 ("Высота: 90 мм",False),
 ("Наружные габариты, P.",True),
 ("Внутри меньше из-за стенок.",True),
])
card(2115,1050,357,245,7,"Место для обуви",[
 ("Под ящиком: h = 310 мм",False),
 ("Без ящика: h = 400 мм",False),
 ("Вдоль стены всего: 575 мм.",True),
 ("Обувь стоит на полу в один ряд.",True),
])

add('''<rect x="28" y="1725" width="2444" height="150" rx="16" fill="#fff9ef" stroke="#ead4ac" stroke-width="2"/>''')
add('<text x="52" y="1762" class="body">Стена 1675 мм по БТИ; разбивка эскиза: 25 + 1050 + 575 + 25 мм. Потолок в отмеченных точках: 2750 мм.</text>')
add('<text x="52" y="1795" class="body">Размеры мебели P — эскиз. Габарит щитка и его доступ уточнить с электриком; полезные размеры секций — при проектировании.</text>')
add('<text x="52" y="1828" class="small">* Фасады рассчитаны условно при накладных дверцах и зазорах по 2 мм; петли и открывание не проверены.</text>')
add('<text x="52" y="1855" class="small">Высоты h — от пола. Линии связывают размеры с предметами; перспектива изображения не является обмером.</text>')
add('</svg>')
data="".join(parts)
ET.fromstring(data)
OUT.write_text(data,encoding="utf-8")
print("Saved:",OUT,"bytes:",OUT.stat().st_size)
