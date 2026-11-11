"""Compare two conditional B01 kitchen footprints at the D2 opening."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output' / 'visualizations' / 'B01_узел_D2_сравнение_v1.png'
H = 3500
DOOR_END = 1110
BASE = {'fridge': (0,1130,600,1730), 'pmm': (0,1730,600,2180),
        'reserve': (0,2180,600,2330), 'sink': (0,2330,600,2900),
        'corner': (0,2900,600,3500)}
COMPACT = {'fridge': (0,1280,600,1880), 'pmm': (0,1880,600,2330),
           'sink': (0,2330,600,2900), 'corner': (0,2900,600,3500)}
assert BASE['fridge'][1]-DOOR_END == 20
assert COMPACT['fridge'][1]-DOOR_END == 170
assert 600+600+450+570 == 2220
assert 2390-2220 == 170
assert BASE['sink'] == COMPACT['sink']
assert BASE['corner'] == COMPACT['corner']

img=Image.new('RGB',(2200,1540),'#f6f4ef')
d=ImageDraw.Draw(img)
def f(n,b=False):return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf',n)
d.text((70,35),'B01  |  кухня и вход D2 — сравнение вариантов',font=f(43,True),fill='#243b38')
d.text((70,95),'Сравнение по B01 · размеры эскиза условные · изготовление и монтаж после обмера',font=f(24,True),fill='#a03429')
scale=.235
def panel(x0,title,items,gap):
    y0=245
    def pt(x,y):return x0+x*scale,y0+(H-y)*scale
    def box(r,fill):
        a,b=pt(r[0],r[3]),pt(r[2],r[1]);d.rectangle((*a,*b),fill=fill,outline='#566662',width=2)
    def textcenter(r,t,size=20):
        d.multiline_text(pt((r[0]+r[2])/2,(r[1]+r[3])/2),t,font=f(size,True),fill='#263b37',anchor='mm',align='center')
    d.text((x0,175),title,font=f(27,True),fill='#243b38')
    box((0,0,2600,H),'white')
    for key,r in items.items():
        color={'fridge':'#d5c2b2','pmm':'#adc8d6','reserve':'#f1ce91','sink':'#d8e8e3','corner':'#e5dacf'}[key]
        box(r,color)
        textcenter(r,{'fridge':'ХОЛ.\n600','pmm':'ПММ\n450','reserve':'150*','sink':'МОЙКА\n570*','corner':'УГОЛ\n600*'}[key],16 if key=='reserve' else 19)
    for r,t in [((600,2900,1100,3500),'500'),((1100,2900,1600,3500),'ВАРКА\n500*'),((1600,2900,1800,3500),'200*'),((1800,2900,2400,3500),'ПЕНАЛ\n600')]:
        box(r,'#e6dccf');textcenter(r,t,16)
    a,b=pt(0,200),pt(0,1110);d.line((*a,*b),fill='#178c95',width=9)
    a,b=pt(0,DOOR_END),pt(0,items['fridge'][1]);d.line((*a,*b),fill='#b94032' if gap==20 else '#a66c27',width=9)
    ax,ay=pt(650,(DOOR_END+items['fridge'][1])/2)
    d.text((ax,ay),f'{gap} мм*',font=f(23,True),fill='#a33228' if gap==20 else '#8c5d22',anchor='lm')
    d.text((x0,1100),'D2 — проём по B01 910; коробка и открывание не учтены',font=f(20),fill='#526b66')
    d.text((x0,1135),f'Занято по стене до угла: {2370 if gap==20 else 2220} мм*',font=f(20),fill='#526b66')
panel(90,'А  ЭСКИЗ С РЕЗЕРВОМ 150',BASE,20)
panel(1160,'Б  ПММ 450 БЕЗ РЕЗЕРВА',COMPACT,170)
d.text((65,1210),'ВАРИАНТ Б — ОСНОВА ДЛЯ ПРОВЕРКИ С МЕБЕЛЬЩИКОМ',font=f(26,True),fill='#243b38')
notes=[
 '• Порядок холодильник → ПММ → мойка сохранён. 150 мм убраны из условной зоны, а не из размеров приборов.',
 '• 170 мм — только до условного края проёма. Наличник, чистовая отделка и фактические торцы уменьшат этот размер.',
 '• Проверить петли и ручку холодильника, доступ к ПММ и мойке, зазор фасадов, угол и доступность коммуникаций.',
 '• * Цепочка эскиза 600 + 600 + 570 и угол 600 могут иметь иные границы. Нужен обмер и чертёж кухонщика.'
]
for i,line in enumerate(notes):d.text((65,1260+i*55),line,font=f(22),fill='#394d48')
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
img.save(OUTPUT)
print(f'OK {OUTPUT} | 2370/20 vs 2220/170')
