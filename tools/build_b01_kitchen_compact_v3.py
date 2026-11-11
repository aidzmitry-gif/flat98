"""Conceptual B01 compact kitchen and conditional appliance opening envelopes."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output' / 'visualizations' / 'B01_компактная_кухня_проверка_v3.png'
ROOM = (0, 0, 5710, 3500)
FRIDGE = (0, 1280, 600, 1880)
PMM = (0, 1880, 600, 2330)
SINK = (0, 2330, 600, 2900)
CORNER = (0, 2900, 600, 3500)
PREP = (600, 2900, 1100, 3500)
HOB = (1100, 2900, 1600, 3500)
OTHER = (1600, 2900, 1800, 3500)
TOWER = (1800, 2900, 2400, 3500)
SOFA = (2485, 2300, 4455, 3500)
DESK = (4510, 2900, 5710, 3500)
TABLE = (2770, 1500, 4170, 2300)
CHAIRS = [(2880, 1100, 3280, 1500), (3600, 1100, 4000, 1500)]
MEDIA = (2070, 0, 4870, 450)
SHELF = (4870, 0, 5470, 300)
PMM_OPEN = (600, 1880, 1250, 2330)
OVEN_OPEN = (1800, 2300, 2400, 2900)
FRIDGE_SWEEP_BOX = (600, 1280, 1200, 1880)

def intersects(a,b):
    return max(a[0],b[0]) < min(a[2],b[2]) and max(a[1],b[1]) < min(a[3],b[3])

assert 600+570+450+600 == 2220
assert 2390-2220 == FRIDGE[1]-1110 == 170
assert not intersects(PMM_OPEN, TABLE) and not intersects(PMM_OPEN, SOFA)
assert not intersects(OVEN_OPEN, TABLE) and not intersects(OVEN_OPEN, SOFA)
assert not intersects(FRIDGE_SWEEP_BOX, TABLE)
assert TABLE[0]-PMM_OPEN[2] == 1520

image=Image.new('RGB',(2450,1590),'#f6f4ef')
draw=ImageDraw.Draw(image)
def font(size,bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',size)
draw.text((65,32),'B01  |  компактная кухня у входа · рабочая примерка v3',font=font(43,True),fill='#213b38')
draw.text((65,97),'Условные размеры и зоны открывания · габариты техники и проёма требуют обмера',font=font(25,True),fill='#a53529')
scale=.215; ox=95; oy=235; height=3500
def point(x,y):return (ox+x*scale,oy+(height-y)*scale)
def box(rect,fill,outline='#52635f',width=2):
    a,b=point(rect[0],rect[3]),point(rect[2],rect[1])
    draw.rectangle((*a,*b),fill=fill,outline=outline,width=width)
def label(rect,text,size=17,color='#243936'):
    draw.multiline_text(point((rect[0]+rect[2])/2,(rect[1]+rect[3])/2),text,font=font(size,True),fill=color,anchor='mm',align='center')
box(ROOM,'#fff','#273e3b',5)
for r,c,t in [(FRIDGE,'#d1beae','ХОЛ.\n600*'),(PMM,'#a7c6d5','ПММ\n450*'),
              (SINK,'#d8e8e3','МОЙКА\n570*'),(CORNER,'#e1d7c9','УГОЛ\n600*'),
              (PREP,'#eae0d4','500*'),(HOB,'#eae0d4','ВАРКА\n500*'),
              (OTHER,'#ecd5a7','200*'),(TOWER,'#d1beae','ПЕНАЛ\n600*'),
              (SOFA,'#ddd5c9','ДИВАН'),(DESK,'#d9e8e3','РАБОТА'),
              (TABLE,'#c9d9bd','СТОЛ*'),(MEDIA,'#cbbca9','ТУМБА / ЭКРАН'),
              (SHELF,'#bea080','КНИГИ')]:
    box(r,c);label(r,t,15 if r in (OTHER,SHELF) else 18)
for chair in CHAIRS:box(chair,'#d19a7a')
box(PMM_OPEN,'#b9dce9','#4583a0',3);label(PMM_OPEN,'ДВЕРЦА ПММ\n650*',16)
box(OVEN_OPEN,'#f0ccbc','#ab684d',3);label(OVEN_OPEN,'ДВЕРЦА\nДУХОВКИ 600*',15)
box(FRIDGE_SWEEP_BOX,'#eee2b2','#b48c30',3);label(FRIDGE_SWEEP_BOX,'ЗОНА ХОЛ.\n600 × 600*',15)
for x,y1,y2 in [(0,200,1110),(5710,600,2200)]:
    draw.line((*point(x,y1),*point(x,y2)),fill='#178d96',width=10)
px,py=point(0,1195);draw.ellipse((px-9,py-9,px+9,py+9),fill='#c34d32')
draw.text((90,1020),'D2 слева · O1 справа · мебель в расчётном положении',font=font(20),fill='#5e706a')
draw.text((1430,245),'ЗОНА У ВХОДА',font=font(29,True),fill='#213b38')
notes=[
 'Вдоль стены, от угла к входу:',
 'угол 600 + мойка 570 + ПММ 450',
 '+ холодильник 600 = 2220 мм*.',
 '',
 '2390 по B01 − 2220 = 170 мм*',
 'до геометрического края D2,',
 'без коробки, наличника и отделки.',
 '',
 'Границы 570 и 600 на эскизе',
 'и реальный угол не подтверждены.',
 '',
 'Зона холодильника 600 × 600 —',
 'условное поле 90° открывания;',
 'петли, фасад и ручка неизвестны.',
 '',
 'Дверца ПММ 650 и духовки 600 —',
 'условные вылеты для проверки.',
]
for i,line in enumerate(notes):draw.text((1430,300+i*37),line,font=font(22),fill='#3a4c47')
draw.text((65,1100),'ЧТО ПРОВЕРЕНО В МОДЕЛИ И ЧТО ОСТАЁТСЯ ОТКРЫТЫМ',font=font(28,True),fill='#213b38')
lines=[
 '• Условные открытые дверцы ПММ и духовки не пересекают закрытые контуры стола и дивана.',
 '• Между ПММ в показанном открытом положении и левым краем стола по X — 1520 мм; это локальный расчёт.',
 '• Выдвижение корзин, человек, ручки, дверь D2 и одновременное открывание ещё не проверены.',
 '• Угол, доборы, фасады, подключение воды, слив и вентиляция — по замеру и монтажным картам конкретной техники.',
 '• Стол на ночь убирается. Место хранения и непрерывный маршрут ко входу и террасе требуют натурной проверки.'
]
for i,line in enumerate(lines):draw.text((65,1158+i*58),line,font=font(23),fill='#344a44')
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
image.save(OUTPUT)
print(f'OK: {OUTPUT}; wall gap 170; PММ-to-table local 1520; intersections checked')
