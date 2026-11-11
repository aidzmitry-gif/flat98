"""Scale-based APT-001 entrance audit: plan and furniture elevation.

P=proposal, B=B01 plan, R=site measurement, M=missing; none of the
conditional lines are a measured usable corridor or a verified door sweep.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET
from hallway_dimensions_v47 import D

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'Прихожая'
assert 610+1010+470==2090
assert 25+575+1050+25==1675
assert 550+446+3*18==1050
assert 562+18==580
assert 2090-580==1510 and 2090-420==1670
assert 2090-580-574==936 and 610-580==30
assert 460-35-25==400 and 400-90==310 and 575-250==325
assert (D.room_width,D.room_depth,D.wardrobe_depth,D.bench_depth)==(2090,1675,580,420)
assert (D.bench_width,D.wardrobe_width,D.panel_clear_width,D.coat_clear_width)==(575,1050,550,446)

STYLE='''<style>
text{font-family:Arial,'Segoe UI',sans-serif;fill:#203b35}
.eyebrow{font-size:20px;font-weight:700;letter-spacing:2px;fill:#387362}
.title{font-size:50px;font-weight:700}.subtitle{font-size:26px;fill:#607970}
.head{font-size:32px;font-weight:700}.body{font-size:26px;fill:#345149}
.small{font-size:22px;fill:#59736a}.tiny{font-size:20px;fill:#687e73}
.label{font-size:25px;font-weight:700;fill:#244c40}.measure{font-size:26px;font-weight:700;fill:#224f42}
.warn{fill:#9a5c10;font-weight:700}.white{fill:#fff;font-weight:700;font-size:24px}
</style><defs>
<marker id="arrow" markerWidth="9" markerHeight="9" refX="4.5" refY="4.5" orient="auto-start-reverse"><path d="M8,1 L1,4.5 L8,8" fill="none" stroke="#416d5e" stroke-width="1.4"/></marker>
<marker id="amber" markerWidth="9" markerHeight="9" refX="4.5" refY="4.5" orient="auto-start-reverse"><path d="M8,1 L1,4.5 L8,8" fill="none" stroke="#b67620" stroke-width="1.4"/></marker>
</defs>'''

class Sheet:
    def __init__(self,w,h,title,subtitle):
        self.w=w;self.h=h;self.s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{STYLE}',f'<rect width="{w}" height="{h}" fill="#f1f4ef"/>']
        self.txt(55,52,'APT-001 / ПРИХОЖАЯ / ПРОВЕРКА ГЕОМЕТРИИ · V47','eyebrow')
        self.txt(55,112,title,'title')
        self.txt(58,153,subtitle,'subtitle')
    def raw(self,s):self.s.append(s)
    def txt(self,x,y,t,cls='body',anchor='start',extra=''):
        self.raw(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}" {extra}>{escape(str(t))}</text>')
    def rect(self,x,y,w,h,fill,stroke='none',sw=1,extra=''):
        assert w>=0 and h>=0,(x,y,w,h)
        self.raw(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
    def line(self,x1,y1,x2,y2,stroke='#35594d',width=3,extra=''):
        self.raw(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}" {extra}/>')
    def dimh(self,x1,x2,y,label,dy=-10):
        self.line(x1,y,x2,y,'#416d5e',2,'marker-start="url(#arrow)" marker-end="url(#arrow)"')
        self.txt((x1+x2)/2,y+dy,label,'measure','middle')
    def dimv(self,y1,y2,x,label):
        self.line(x,y1,x,y2,'#416d5e',2,'marker-start="url(#arrow)" marker-end="url(#arrow)"')
        self.txt(x-15,(y1+y2)/2,label,'measure','middle',f'transform="rotate(-90 {x-15:.1f} {(y1+y2)/2:.1f})"')
    def card(self,x,y,w,h):self.rect(x,y,w,h,'#fff','#dce7dc',2,'rx="20"')
    def save(self,path):
        data=''.join(self.s)+'</svg>';ET.fromstring(data);path.write_text(data,encoding='utf-8');print('Saved',path)

# Page 1: B01 plan and calculated scenarios.
s=Sheet(2600,1700,'Прихожая: план и расстояния','План B01 и мебельное предложение; все размеры в миллиметрах')
s.card(40,180,1510,1320);s.card(1570,180,990,1320)
s.txt(70,225,'01  План сверху','head');s.txt(70,258,'Вход сверху, шкаф слева, кухня справа; фасады закрыты.','small')
ox,oy,sc=275,445,.55
def X(x):return ox+sc*x
def Y(y):return oy+sc*y
def worldrect(x,y,w,h,fill,stroke='#9d8b72',sw=2):s.rect(X(x),Y(y),w*sc,h*sc,fill,stroke,sw)
s.rect(X(0),Y(0),2090*sc,1675*sc,'#f8f9f4')
# Existing wall, D1 segment, D2 and open transition 3 <-> 4.
s.line(X(0),Y(0),X(0),Y(1675),'#263d36',9)
for a,b in ((0,610),(1620,2090)):s.line(X(a),Y(0),X(b),Y(0),'#263d36',9)
s.line(X(610),Y(0),X(1620),Y(0),'#222a28',11)
for a,b in ((0,565),(1475,1675)):s.line(X(2090),Y(a),X(2090),Y(b),'#263d36',9)
s.line(X(2090),Y(565),X(2090),Y(1475),'#bd812a',4,'stroke-dasharray="12 9"')
s.txt((X(610)+X(1620))/2,Y(0)-16,'ВХОДНАЯ ДВЕРЬ D1','label','middle')
s.txt(1470,Y(1010),'D2 910 B','label','middle',f'transform="rotate(90 1470 {Y(1010):.1f})"')
s.txt((X(0)+X(2090))/2,Y(1675)+42,'ОТКРЫТЫЙ ПЕРЕХОД В КОРИДОР 4','label','middle')
# Furniture blocks - body and facade together have exterior depth 580.
worldrect(0,25,420,575,'#dcebd9','#92aa94')
worldrect(0,600,580,464,'#e6d0b0','#aa8e6a')
worldrect(0,1064,580,586,'#d6bd99','#aa8e6a')
worldrect(562,600,18,1050,'#a67d50','#8b704f',1)
s.txt(X(210),Y(170),'БАНКЕТКА','label','middle');s.txt(X(210),Y(235),'575 × 420 P','small','middle')
s.txt(X(280),Y(775),'КУРТКИ','label','middle');s.txt(X(280),Y(835),'глубина 580 P','small','middle')
s.txt(X(280),Y(1250),'ЩИТ','label','middle');s.txt(X(280),Y(1315),'габарит M','small','middle')
# Dimensions above and left of plan.
s.dimh(X(0),X(2090),298,'2090 B')
for x1,x2,label in ((0,610,'610 B'),(610,1620,'1010 B'),(1620,2090,'470 B')):s.dimh(X(x1),X(x2),355,label)
for x in (0,610,1620,2090):s.line(X(x),368,X(x),Y(0)-4,'#8aa296',1)
s.dimv(Y(0),Y(1675),155,'1675 B')
# Gap arrows at positions where the opposite wall exists, not in the D2 opening.
for x1,x2,yy,label in ((420,2090,400,'1670*'),(580,2090,1570,'1510*')):
    xa,xb,y=X(x1),X(x2),Y(yy)
    s.line(xa,y,xb,y,'#326653',4,'marker-start="url(#arrow)" marker-end="url(#arrow)"')
    s.rect((xa+xb)/2-67,y-38,134,36,'#f8f9f4','none',1,'rx="8"')
    s.txt((xa+xb)/2,y-11,label,'measure','middle')
s.txt(70,1465,'* Остатки до плоскости стены B01, без отделки, ручек и открытых створок.','small')

s.txt(1600,225,'02  Расчёты и проверка','head')
s.txt(1610,290,'Глубина шкафа с фасадом','body');s.txt(2520,290,'580 P','measure','end')
s.txt(1610,337,'Глубина банкетки','body');s.txt(2520,337,'420 P','measure','end')
s.line(1610,365,2520,365,'#d9e4d9',2)
s.txt(1610,416,'Закрытый шкаф: 2090 − 580','body');s.txt(2520,416,'1510','measure','end')
s.txt(1610,452,'У банкетки: 2090 − 420','body');s.txt(2520,452,'1670','measure','end')
s.txt(1610,495,'Это номинальная геометрия, не чистый проход.','small')
s.line(1610,530,2520,530,'#d9e4d9',2)
s.txt(1610,580,'Если створка 574 P открыта на 90°:','body')
s.txt(1610,622,'2090 − 580 − 574 = 936 мм','measure')
s.txt(1610,660,'Одна условная створка, без ручки и толщины.','small')
s.txt(1610,694,'Петли и реальный угол пока не определены.','small')
s.line(1610,730,2520,730,'#d9e4d9',2)
s.txt(1610,780,'Если петли D1 у левого края B01:','body')
s.txt(1610,822,'610 − 580 = 30 мм до оси полотна','measure')
s.txt(1610,860,'Только пример открытия внутрь на 90°.','small')
s.txt(1610,894,'Коробка, ручка и фактические петли не учтены.','small')
s.line(1610,930,2520,930,'#d9e4d9',2)
s.txt(1610,980,'Вход D1 — два разных источника','body')
s.txt(1610,1022,'B01: 610 + 1010 + 470 = 2090','measure')
s.txt(1610,1062,'Контроль: 1140 × 2150; привязка M','measure')
s.txt(1610,1100,'Сохранять эти данные раздельно.','small')
s.txt(1610,1160,'До изготовления: обмер D1, D2, щита,','warn')
s.txt(1610,1196,'чистового пола и фактических откосов.','warn')
s.txt(1610,1255,'Полный контур коридора не обмерен;','small')
s.txt(1610,1290,'расстояния до D3–D5 здесь не назначены.','small')
s.rect(40,1525,2520,125,'#fffaf1','#ead7b6',2,'rx="18"')
s.txt(68,1571,'B — план БТИ; P — предложение; M — отсутствует. Размеры фасадов, петель и щита требуют проверки на месте.','small')
s.txt(68,1610,'Схема не подтверждает открывание входной двери, доступ к щиту или безопасную ширину прохода.','small')
s.save(OUT/'112_прихожая_план_и_проходы_v47.svg')

# Page 2: front elevation; both dimensions use the same mm/pixel scale.
s=Sheet(2600,1700,'Шкаф и банкетка: размеры и хранение','Вид из кухни на левую стену; открытый коридор слева, входная дверь справа')
s.card(40,180,1505,1320);s.card(1565,180,995,1320)
s.txt(70,225,'01  Развёртка без фасадов','head')
s.txt(70,258,'Одинаковый масштаб по ширине и высоте; пунктир не задаёт размер щита.','small')
base=1390;ox,sc=360,.39
def X(x):return ox+sc*x
def Z(z):return base-sc*z
# Ceiling line and positive-height boxes.
s.line(X(0)-30,Z(2750),X(1675)+35,Z(2750),'#aabbb0',3)
s.rect(X(25),Z(2700),1050*sc,2700*sc,'#ead8be','#8d7455',3)
# Service bay and coat bay interior: 18 + 550 + 18 + 446 + 18 = 1050.
service_x=25+18;coats_x=25+18+550+18
s.rect(X(service_x),Z(2682),550*sc,(2682-18)*sc,'#ebf3e7','#b7cbb4',2)
s.rect(X(coats_x),Z(2682),446*sc,(2682-18)*sc,'#f7efe3','#d3c2a9',2)
s.line(X(coats_x),Z(2150),X(coats_x+446),Z(2150),'#9e805e',6)
s.line(X(coats_x),Z(380),X(coats_x+446),Z(380),'#9e805e',6)
s.line(X(coats_x+42),Z(1750),X(coats_x+404),Z(1750),'#514e47',5)
for xx in (coats_x+90,coats_x+200,coats_x+310):
    s.line(X(xx),Z(1750),X(xx),Z(1400),'#8c957f',20)
s.txt(X(service_x+275),Z(2050),'СЕКЦИЯ ЩИТА','label','middle')
s.txt(X(service_x+275),Z(1960),'550 P в свету','small','middle')
s.txt(X(service_x+275),Z(1780),'ЩИТ: РАЗМЕР M','small','middle')
s.txt(X(coats_x+223),Z(2400),'ОДЕЖДА','label','middle')
s.txt(X(coats_x+223),Z(2300),'446 P','small','middle')
# Bench: open space below with drawer only on the wardrobe side.
bx=25+1050
s.rect(X(bx),Z(2700),575*sc,550*sc,'#d0b38c','#9e825e',2)
s.rect(X(bx),Z(2150),575*sc,(2150-460)*sc,'#dcebd9','#a7beaa',2)
s.rect(X(bx),Z(460),575*sc,60*sc,'#d9cabb','#9e825e',2)
s.rect(X(bx),Z(400),250*sc,90*sc,'#c4a17a','#9e825e',2)
for xx,h in ((bx+270,280),(bx+390,280)):
    s.rect(X(xx),Z(h),110*sc,h*sc,'#756957','#756957',1,'rx="5"')
s.txt(X(bx+287.5),Z(900),'КРЮЧКИ','small','middle')
s.txt(X(bx+287.5),Z(690),'БАНКЕТКА','label','middle')
s.txt(X(bx+125),Z(350),'ящик','tiny','middle')
s.txt(X(bx+405),Z(55),'обувь','tiny','middle')
# Exterior dimensional indicators.
s.dimv(Z(2750),base,220,'2750 R*')
s.dimv(Z(2700),base,285,'2700 P')
s.dimv(Z(460),base,X(1675)+80,'460 P')
s.dimh(X(25),X(25+1050),1450,'1050 P')
s.dimh(X(bx),X(bx+575),1450,'575 P')
s.txt(80,1490,'* Высота по отмеченным точкам C09; чистовой пол и потолок не учтены.','small')

s.txt(1595,225,'02  Размеры элементов','head')
lines=[
('Общий шкаф','1050 × 580 × 2700 P'),
('Корпус + фасад','562 + 18 = 580 P'),
('Секция щита внутри','550 P; размеры щита M'),
('Секция одежды внутри','446 P; штанга +1750 P'),
('Верх над банкеткой','575 × 420 × 550 P'),
('Сиденье','575 × 420; высота 460 P'),
('Ящик для сухих тапочек','250 × 380 × 90 P, снаружи'),
('До пола без ящика','400 P'),
('До пола под ящиком','310 P'),
('Зона для высокой обуви','325 P до вычета креплений'),
]
for i,(name,value) in enumerate(lines):
    y=285+i*80;s.txt(1610,y,name,'body');s.txt(1610,y+35,value,'measure')
s.line(1610,1108,2520,1108,'#d9e4d9',2)
s.txt(1610,1160,'Под банкеткой обувь стоит на полу,','body')
s.txt(1610,1198,'а не на полке.','body')
s.txt(1610,1250,'Ориентир: 2 пары в один ряд, не гарантия;','warn')
s.txt(1610,1288,'проверить обувь, боковины и крепления.','warn')
s.txt(1610,1360,'Электрощит и его открывание не обмерены.','small')
s.txt(1610,1400,'Внутренняя глубина отделений пока не определена.','small')
s.rect(40,1525,2520,125,'#fffaf1','#ead7b6',2,'rx="18"')
s.txt(68,1571,'P — предварительное предложение; M — измерения отсутствуют. Щит 550 мм не равен размеру самого щита.','small')
s.txt(68,1610,'Перед заказом проверить чистовую высоту, раскрой, доступ к щиту, петли и открывание мебели.','small')
s.save(OUT/'113_прихожая_шкаф_и_банкетка_v47.svg')
