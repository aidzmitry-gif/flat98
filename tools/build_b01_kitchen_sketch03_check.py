"""B01 kitchen sketch 03: test one explicit interpretation, not construction dimensions."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'visualizations' / 'B01_кухня_эскиз03_проверка_v2.png'
W, H = 5710, 3500
FRIDGE = (0, 1130, 600, 1730)
PMM = (0, 1730, 600, 2180)
RESERVE = (0, 2180, 600, 2330)
SINK = (0, 2330, 600, 2900)
CORNER = (0, 2900, 600, 3500)
PREP = (600, 2900, 1100, 3500)
HOB = (1100, 2900, 1600, 3500)
UNIT200 = (1600, 2900, 1800, 3500)
OVEN = (1800, 2900, 2400, 3500)
SOFA = (2485, 2300, 4455, 3500)
DESK = (4510, 2900, 5710, 3500)
TABLE = (2770, 1500, 4170, 2300)
MEDIA = (2070, 0, 4870, 450)
SHELF = (4870, 0, 5470, 300)
# Hypothetical door projection only. Person, handles, actual door profiles and swing remain unknown.
PMM_OPEN = (600, 1730, 1250, 2180)
OVEN_OPEN = (1800, 2300, 2400, 2900)

def intersect(a, b):
    return max(a[0],b[0]) < min(a[2],b[2]) and max(a[1],b[1]) < min(a[3],b[3])

assert 600 + 600 + 570 == 1770
assert 500 + 500 + 200 + 600 == 1800
assert 600 + 1800 == 2400
assert FRIDGE[1] - 1110 == 20
assert RESERVE[3] - RESERVE[1] == 150
assert all(not intersect(PMM_OPEN, r) for r in [SOFA, TABLE, MEDIA])
assert all(not intersect(OVEN_OPEN, r) for r in [SOFA, TABLE, MEDIA])

img = Image.new('RGB', (2400, 1550), '#f7f5f0')
d = ImageDraw.Draw(img)
def f(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf', size)
d.text((70,35), 'B01  |  кухня по первому эскизу · проверка v2', font=f(44,True), fill='#243735')
d.text((70,100), 'Размерная гипотеза: границы цепочек и модели техники требуют подтверждения', font=f(25,True), fill='#a13225')
scale=.22; ox=110; oy=220
def pt(x,y): return (ox+x*scale,oy+(H-y)*scale)
def box(r,color,stroke='#52605b',width=2):
    a,b=pt(r[0],r[3]),pt(r[2],r[1]);d.rectangle((*a,*b),fill=color,outline=stroke,width=width)
def label(r,text,size=19,color='#263734'):
    d.multiline_text(pt((r[0]+r[2])/2,(r[1]+r[3])/2),text,font=f(size,True),fill=color,anchor='mm',align='center',spacing=2)
box((0,0,W,H),'white','#253d3a',5)
for r,c,t in [(FRIDGE,'#d4c3b6','ХОЛ.\n600'),(PMM,'#a5bfd0','ПММ\n450'),(RESERVE,'#f5d398','150*'),(SINK,'#d8e9e6','МОЙКА\n570*'),(CORNER,'#dfd3c6','УГОЛ\n600*'),(PREP,'#e8dfd1','500'),(HOB,'#e8dfd1','ВАРКА\n500*'),(UNIT200,'#f5d398','200*'),(OVEN,'#d4c3b6','ПЕНАЛ\n600')]:
    box(r,c);label(r,t,17)
box(SOFA,'#ded5c9');label(SOFA,'ДИВАН',19)
box(DESK,'#dce9e4');label(DESK,'РАБОТА',17)
box(TABLE,'#ccdabe');label(TABLE,'СТОЛ 1400 × 800*',18)
box(MEDIA,'#cdbfa9');label(MEDIA,'ТУМБА / ЭКРАН',19)
box(SHELF,'#bb9c7e');label(SHELF,'СТЕЛЛАЖ',14)
box(PMM_OPEN,'#b9d9e6','#327497',4);label(PMM_OPEN,'ДВЕРЦА ПММ\n650*',16)
box(OVEN_OPEN,'#f1c8b8','#ad583b',4);label(OVEN_OPEN,'ДВЕРЦА ДУХОВКИ\n600*',16)
for x, a, b in [(0,200,1110),(W,600,2200)]: d.line((*pt(x,a),*pt(x,b)),fill='#138b91',width=10)
px,py=pt(0,1120);d.ellipse((px-12,py-12,px+12,py+12),fill='#c83324')
d.text((1450,245),'УСЛОВИЯ ПРИМЕРКИ',font=f(28,True),fill='#263734')
notes=[
 'Первый эскиз: холодильник → ПММ → мойка;',
 'на второй ветви — варка и пенал духовки/СВЧ.',
 '',
 '600 + 600 + 570 = 1770 по эскизу.',
 'ПММ 450 в зоне 600; 150 — резерв, не готовый добор.',
 '500 + 500 + 200 + 600 = 1800 по эскизу.',
 'Угол 600 добавлен как гипотеза: 1800 + 600 = 2400.',
 '',
 'Если 1770 отложены ЗА углом, кухня подходит к D2',
 'на 20 мм по цепочке B01. Наличники и открывание',
 'не учтены; границы эскиза проверить на объекте.',
 '',
 'Дверца ПММ 650 и духовки 600 — примеры вылета,',
 'а не размеры выбранной техники. Место человека,',
 'ящики, петли и проход через вход не проверены.',
]
for i,line in enumerate(notes):d.text((1450,305+i*40),line,font=f(22),fill='#374947')
d.text((70,1050),'РЕЗУЛЬТАТ',font=f(29,True),fill='#243735')
lines=[
 '• ПММ расположена между холодильником и мойкой, как согласовано владельцем. Её ширина 450 мм — рабочее допущение.',
 '• При указанных прямоугольниках дверцы не пересекают стол и диван. Пространство для человека и совместная работа не проверены.',
 '• Красная точка — условный зазор 20 мм до проёма: это не чистовой зазор до коробки, наличника или полотна двери.',
 '• Стол ночью убирается. Путь D2–O1 и хранение стола требуют натурной проверки; сценарий света — в предыдущем листе.',
 '* Размеры угла, зон, вылетов, техники и положение размеров эскиза не подтверждены. Для изготовления и монтажа не использовать.'
]
for i,line in enumerate(lines):d.text((70,1105+i*58),line,font=f(23),fill='#354844')
OUT.parent.mkdir(parents=True,exist_ok=True)
img.save(OUT)
print(f'OK {OUT}: arithmetic, two door envelopes and 20 mm model gap checked')
