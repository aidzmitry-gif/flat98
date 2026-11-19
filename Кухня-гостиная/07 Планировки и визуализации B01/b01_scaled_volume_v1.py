from PIL import Image, ImageDraw, ImageFont
import math

OUT=r'D:\6 Проекты\Квартира\output\visualizations\B01_масштабный_план_и_объём_v1.png'
im=Image.new('RGB',(2500,1650),'#f8f6f0'); d=ImageDraw.Draw(im)
def tx(x,y,s,z=25,col='#263d37',bold=False,anchor=None):
 d.multiline_text((x,y),s,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',z),fill=col,anchor=anchor,align='center',spacing=4)
tx(70,35,'B01 · МАСШТАБНЫЙ ПЛАН И ОБЪЁМНАЯ ПРИМЕРКА',42,bold=True)
tx(70,100,'Построено по числовым размерам модели · проектные допущения, не производственный чертёж',25,col='#a34330')
tx(90,205,'1 · ПЛАН СВЕРХУ',29,bold=True);tx(1300,205,'2 · ОБЪЁМНАЯ СХЕМА',29,bold=True)
# Same footprint coordinates used by both views: x from entrance to terrace; y from media wall to sofa.
objects=[
 ('УГОЛ',0,2900,600,3500,0,860,'#e4d7c5'),('РАБОТА',600,2900,1100,3500,0,860,'#eee6db'),
 ('ВАРКА',1100,2900,1600,3500,0,860,'#eee6db'),('200',1600,2900,1800,3500,0,860,'#eed6aa'),
 ('ПЕНАЛ',1800,2900,2400,3500,0,2400,'#d5bfa7'),('МОЙКА',0,2330,600,2900,0,860,'#e2e1d0'),
 ('ПММ',0,1730,600,2330,0,860,'#b8dcd4'),('ХОЛ.',0,1130,600,1730,0,2400,'#d2b89c'),
 ('ДИВАН',2485,2300,4455,3500,0,940,'#aab18d'),('РАБОТА',4500,2900,5700,3500,0,750,'#d2e1db'),
 ('СТОЛ',2770,1500,4170,2300,700,750,'#d8cdb9'),('СТУЛ',2880,1100,3280,1500,0,450,'#c98e69'),
 ('СТУЛ',3600,1100,4000,1500,0,450,'#c98e69'),('ТУМБА',2070,0,4870,450,0,540,'#d9cbb8'),
 ('КНИГИ',4870,0,5470,300,0,2400,'#b39370')]

# plan
px,py,s=145,290,.158
def P(x,y):return (px+x*s,py+(3500-y)*s)
d.rectangle((*P(0,3500),*P(5710,0)),fill='white',outline='#3a5048',width=3)
for name,x1,y1,x2,y2,z1,z2,c in objects:
 a=P(x1,y2); b=P(x2,y1);d.rectangle((*a,*b),fill=c,outline='#53655d',width=2)
 lab={'ХОЛ.':'ХОЛ.\n600×600','ПММ':'ПММ\n600','МОЙКА':'МОЙКА\n570','ДИВАН':'ДИВАН\n1970×1200','СТОЛ':'СТОЛ*\n1400×800','ТУМБА':'ТУМБА 2800×450','ПЕНАЛ':'ПЕНАЛ\n600','РАБОТА':'РАБОТА','КНИГИ':'СТЕЛЛАЖ','СТУЛ':'СТУЛ'}.get(name,name)
 tx((a[0]+b[0])/2,(a[1]+b[1])/2,lab,17,bold=True,anchor='mm')
d.line((*P(0,200),*P(0,1110)),fill='#12888a',width=9);d.line((*P(5710,600),*P(5710,2200)),fill='#12888a',width=9)
tx(px+451,py-30,'5710 мм — по плану',24,bold=True,anchor='mm');tx(px-20,py+280,'3500',23,bold=True,anchor='rm')
tx(px-22,py+450,'D2',20,col='#12888a',bold=True,anchor='rm');tx(px+915,py+345,'O1',20,col='#12888a',bold=True)

# Equal-unit isometric projection; objects are plain bounding boxes, not a photographic render.
q=.13; bx,by=1700,480
def V(x,y,z):return (bx+(x-y)*math.sqrt(3)/2*q,by+(x+y)*.5*q-z*q)
floor=[V(0,0,0),V(5710,0,0),V(5710,3500,0),V(0,3500,0)]
d.polygon(floor,fill='#e8e3d8',outline='#68766f',width=3)
def shade(hexcol,factor):
 vals=[int(hexcol[i:i+2],16) for i in (1,3,5)];return tuple(int(v*factor) for v in vals)
def cuboid(o):
 name,x1,y1,x2,y2,z1,z2,col=o
 a=V(x1,y1,z1);b=V(x2,y1,z1);c=V(x2,y2,z1);e=V(x1,y2,z1)
 A=V(x1,y1,z2);B=V(x2,y1,z2);C=V(x2,y2,z2);E=V(x1,y2,z2)
 d.polygon((a,e,E,A),fill=shade(col,.83),outline='#66746b')
 d.polygon((e,c,C,E),fill=shade(col,.9),outline='#66746b')
 d.polygon((A,B,C,E),fill=col,outline='#66746b')
for o in sorted(objects,key=lambda a:(a[1]+a[2]+a[3]+a[4])/2):cuboid(o)
tx(1280,1080,'Объёмные блоки — габариты мебели, цвет показывает зоны.',23)
tx(1280,1120,'Двери, шторы, ножки, стыки и открывание здесь не моделируются.',23)
tx(80,1210,'ЧТО ЗАДАНО В МОДЕЛИ',30,bold=True)
lines=[
'Комната 5710 × 3500 мм [B]; холодильный блок 600 × 600 мм [P], выступ от стены — 600 мм.',
'Кухня: ветви 2370 × 2400 мм [P], ПММ 600 мм [P]; размер угла и монтажные зазоры не подтверждены.',
'Диван Domo PRO: 1970 × 1200 × 940 мм [из карточки выбранной комплектации].',
'Стол у дивана 1400 × 800 мм [P]: ширина стола 71% ширины дивана; высота 750 мм [P].',
'Высота кухонной базы 860 мм, пеналов и стеллажа 2400 мм, тумбы 540 мм — модельные допущения [P].',
'Створки, открывания и доступ проверяются отдельно: схема двери и текущие размеры — по ссылкам в ответе.'
]
for i,line in enumerate(lines):tx(80,1260+i*51,line,24,col='#a34330' if i in (1,4,5) else '#263d37')
im.save(OUT);print(OUT)
