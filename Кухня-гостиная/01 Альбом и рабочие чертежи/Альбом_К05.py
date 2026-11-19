"""B01. Развёртки и аксонометрии из одной параметрической модели.
Координаты объектов: u вдоль стены слева направо при взгляде на неё,
v от чистовой стены внутрь помещения, z от чистого пола. Единицы мм.
"""
from pathlib import Path
from math import sin,cos,pi
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor as Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from PIL import Image
from pypdf import PdfWriter,PdfReader
P=Path(__file__).resolve().parent
ROOM=P.parent
for f,n in [('arial','r'),('arialbd','b')]:pdfmetrics.registerFont(TTFont(n,'C:/Windows/Fonts/'+f+'.ttf'))
out=P/'B01_Развёртки_и_виды_К05.pdf'; c=Canvas(str(out),pagesize=(420*mm,297*mm))
c.setTitle('B01 • Развёртки и виды К05')
ink='#253734'; fine='#71817a'; beige='#e8dfd1'; cream='#f6f2ec'; oak='#d5b78f'; moss='#98a384'; glass='#dce9e7'; metal='#68736f'; red='#a34532'; gr='#267162'
def t(x,y,s,size=3.35,b=False,col=ink,a='left'):
    c.setFont('b' if b else 'r',size);c.setFillColor(Color(col));getattr(c,{'left':'drawString','c':'drawCentredString','right':'drawRightString'}[a])(x,y,str(s))
def l(x,y,X,Y,col=fine,w=.2,ds=False):
    c.setStrokeColor(Color(col));c.setLineWidth(w);c.setDash([1,.8] if ds else []);c.line(x,y,X,Y);c.setDash([])
def poly(pts,col,edge=ink,w=.22):
    p=c.beginPath();p.moveTo(*pts[0])
    for pt in pts[1:]:p.lineTo(*pt)
    p.close();c.setFillColor(Color(col));c.setStrokeColor(Color(edge));c.setLineWidth(w);c.drawPath(p,fill=1,stroke=1)
def box(x,y,w,h,col,edge=ink,lw=.22):poly([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],col,edge,lw)
def circle(x,y,d,col,edge=fine):
    c.setFillColor(Color(col));c.setStrokeColor(Color(edge));c.setLineWidth(.22);c.circle(x,y,d/2,fill=1,stroke=1)
def h(a,b,y,ref,label):
    for q in [a,b]:
        if ref is not None:l(q,ref,q,y+1.1*(1 if y>ref else -1),'#aab2ac',.13)
        l(q-.85,y-.95,q+.85,y+.95,red,.26)
    l(a,y,b,y,red,.18);t((a+b)/2,y+1.15,label,2.85,True,red,'c')
def v(a,b,x,ref,label):
    for q in [a,b]:
        if ref is not None:l(ref,q,x+1.1*(1 if x>ref else -1),q,'#aab2ac',.13)
        l(x-.9,q-1,x+.9,q+1,red,.26)
    l(x,a,x,b,red,.18);c.saveState();c.translate(x-1.2,(a+b)/2);c.rotate(90);t(0,0,label,2.85,True,red,'c');c.restoreState()
def stamp(n,name,subtitle):
    c.scale(mm,mm);c.bookmarkPage(n);c.addOutlineEntry(n+' · '+name,n)
    box(8,8,404,281,'#ffffff',ink,.35);t(15,277,name,7.4,True);t(15,268,subtitle,3.45)
    l(8,263,412,263,ink,.32);l(8,23,412,23,ink,.32);t(14,14,'B01   /   КУХНЯ-ГОСТИНАЯ',3.4,True,gr)
    t(115,14,'П — проект   •   О — обмер   •   Б — БТИ   •   М — уточнить',3)
    l(324,8,324,23);t(329,14,'К05    /    A3',3.4,True);t(403,14,n,4.5,True,gr,'right')
def caption(x,y,s):t(x,y,s,3.45,True,gr)
def end():c.showPage()
def fitimg(file,x,y,w,h,crop=None):
    im=Image.open(ROOM/file)
    if crop:im=im.crop(tuple(round(v*(im.width if i%2==0 else im.height)) for i,v in enumerate(crop)))
    c.drawImage(ImageReader(im),x,y,w,h,preserveAspectRatio=True,anchor='c')
def arrow(x,y,dx,dy,label):
    l(x,y,x+dx,y+dy,gr,.65)
    a,b=x+dx,y+dy;poly([(a,b),(a-.24*dx+.13*dy,b-.24*dy-.13*dx),(a-.24*dx-.13*dy,b-.24*dy+.13*dx)],gr,gr)
    t(x-2,y-1,label,2.7,True,gr,'right')
def key(x,y,width,active=None):
    k=width/5710
    def R(a,b,w,d,col):box(x+a*k,y+b*k,w*k,d*k,col,fine,.15)
    R(0,0,5710,3500,'#f5f5f0');R(0,2900,2400,600,beige);R(0,1130,600,1770,beige);R(2485,2300,1970,1200,moss);R(4500,2900,1200,600,oak);R(2770,1500,1400,800,cream);R(2070,0,2800,450,beige);R(4870,0,600,300,oak)
    l(x+width,y+600*k,x+width,y+2200*k,gr,.7)
    for a,(xx,yy,dx,dy) in {'А':(.42,.68,0,1),'Б':(.82,.5,1,0),'В':(.61,.33,0,-1),'Г':(.22,.43,-1,0)}.items():
        if active is None or active==a:arrow(x+width*xx,y+3500*k*yy,dx*7,dy*7,a)
# Each solid is a faced rectangular envelope with optional facade details.
class Wall:
    def __init__(self,name,w):self.name=name;self.w=w;self.parts=[]
    def add(self,u,z,w,h,d,color,style='',front=0):
        self.parts.append((u,z,w,h,d,color,style,front))
def paintwall(wall,proj,oblique=False):
    W=wall.w
    def face(pts,col,width=.2):poly([proj(*p) for p in pts],col,ink,width)
    def patch(u,z,w,h,d,col):face([(u,d,z),(u+w,d,z),(u+w,d,z+h),(u,d,z+h)],col)
    def edge(u,z,U,Z,d,col=ink,width=.21):l(*proj(u,d,z),*proj(U,d,Z),col,width)
    patch(0,0,W,2700,0,'#f7f4ed')
    for u,z,w,h,depth,col,style,front in sorted(wall.parts,key=lambda p:(p[7]+p[4],p[0],p[1])):
        d=front+depth
        if oblique:
            face([(u,front,z),(u,d,z),(u,d,z+h),(u,front,z+h)],col)
            face([(u,front,z+h),(u+w,front,z+h),(u+w,d,z+h),(u,d,z+h)],cream)
        patch(u,z,w,h,d,col)
        def stripe(zz):edge(u,zz,u+w,zz,d,fine)
        if style=='draw':
            for zz in [z+h*.42,z+h*.75]:stripe(zz)
        if style=='upper':edge(u+16,z+17,u+w-16,z+17,d,fine)
        if style=='fridge':stripe(z+690);stripe(z+2110)
        if style in ['oven','micro']:
            patch(u+23,z+45,w-46,h-132,d+.5,'#465350');edge(u+40,z+h-78,u+w-40,z+h-78,d+1,cream,.5)
            edge(u+60,z+h-40,u+w-60,z+h-40,d+1,graycolor)
        if style=='PMM':stripe(z+h-55)
        if style=='desk':patch(u+22,z-730,30,730,d-55,oak);patch(u+w-52,z-730,30,730,d-55,oak)
        if style=='tv':patch(u+15,z+15,w-30,h-30,d+.3,'#697874')
        if style=='console':
            for i in (1,2,3):edge(u+w*i/4,z,u+w*i/4,z+h,d,fine)
        if style=='shelf':
            for z1,z2 in zip([0,450,940,1420,1910],[450,940,1420,1910,2400]):
                patch(u+22,z1+18,w-44,z2-z1-38,d+.2,'#bd9e78')
                for j in range(3):
                    patch(u+70+j*55,z1+22,43,160+j*22,d+.4,['#e6decc','#9da28a','#b7a792'][j])
        if style=='sofa':
            patch(u+70,z+290,w-140,200,d+.5,'#aab49a')
            edge(u+w/2,z+510,u+w/2,z+h-12,d,fine)
        if style=='rad':
            for j in range(1,9):edge(u+j*w/9,z+22,u+j*w/9,z+h-22,d,fine)
        if style=='fabric':
            for j in range(1,9):edge(u+j*w/9,z+10,u+j*w/9,z+h-10,d,fine)
        if style=='door':edge(u+w-175,z+1030,u+w-75,z+1030,d,ink,.7)
        if style=='glass':
            patch(u+38,z+50,w-76,h-95,d+.2,'#eef4ef');edge(u+90,z+h*.36,u+w*.64,z+h*.68,d,graycolor,.2)
graycolor='#98a8a1'
A=Wall('А',5710);B=Wall('Б',3500);V=Wall('В',5710);G=Wall('Г',3500)
def run_k(wall,seq):
    for u,width,style in seq:
        if style in ['oven','fridge']:
            wall.add(u,0,width,2700,600,beige,'fridge' if style=='fridge' else '')
            if style=='oven':
                for z,ht,kind in [(680,600,'oven'),(1300,430,'micro')]:wall.add(u+25,z,width-50,ht,2,metal,kind,600)
        else:
            wall.add(u,0,width,100,555,'#b3b1a6')
            wall.add(u,100,width,770,590,beige,style)
            wall.add(u,870,width,30,600,cream)
            wall.add(u,1500,width,1200,310,beige,'upper')
run_k(A,[(0,600,''),(600,500,'draw'),(1100,500,'draw'),(1600,200,''),(1800,600,'oven')])
run_k(G,[(1130,600,'fridge'),(1730,600,'PMM'),(2330,570,''),(2900,600,'')])
A.add(2485,0,1970,940,1200,moss,'sofa');A.add(4500,750,1200,25,600,oak,'desk');A.add(4500,1460,1200,20,300,oak)
for u in [4500,5100]:A.add(u,1750,600,950,300,beige,'upper')
G.add(200,0,910,2150,35,'#efebe1','door')
B.add(750,150,400,1600,120,'#dedcd4','rad')
for u in [1300,2100]:B.add(u,115,800,2125,40,glass,'glass')
B.add(2950,10,550,2620,160,'#d9c6ab','fabric')
V.add(240,0,600,2400,300,oak,'shelf');V.add(240,2400,600,300,300,beige)
V.add(840,150,2800,540,450,beige,'console');V.add(1133,1000,2214,1245,50,metal,'tv')
# Face details in both orthographic and oblique views.
def details(name,proj):
    def L(p,q,col=ink,w=.25):l(*proj(*p),*proj(*q),col,w)
    if name=='А':
        poly([proj(s,d,902) for s,d in [(1140,80),(1560,80),(1560,505),(1140,505)]],metal)
        for s,d in [(1260,200),(1450,385)]:
            pts=[proj(s+64*cos(i*pi/12),d+64*sin(i*pi/12),903) for i in range(25)]
            for p,q in zip(pts,pts[1:]):l(*p,*q,cream,.22)
    if name=='Г':
        poly([proj(s,d,902) for s,d in [(2370,65),(2860,65),(2860,535),(2370,535)]],'#c8cfca')
        poly([proj(s,d,903) for s,d in [(2405,130),(2820,130),(2820,497),(2405,497)]],'#a1b1a9')
        for a,b in [((2620,90,900),(2620,90,1130)),((2620,90,1130),(2620,240,1130)),((2620,240,1130),(2620,240,1075))]:L(a,b,'#957951',.65)
def ax(w,x,y,k):
    def iso(u,d,z):return x+(u-.58*d)*k,y+(z*.88-d*.35+u*.16)*k
    paintwall(w,iso,True);details(w.name,iso)
def photo_grid():
    fitimg('B01_итоговая_концепция_2026-11-09.png',14,125,234,132)
    fitimg('B01_штора_полностью_справа_v1.png',255,125,148,132)
    caption(16,118,'01   Вид от террасы к кухне · выбранная палитра и свет')
    caption(256,118,'02   Вид к O1 · штора собрана справа')
stamp('В01','Кухня-гостиная · карта видов','5710 × 3500 Б   /   видовые и размерные листы   /   четыре направления из одной системы координат')
photo_grid();key(22,33,116)
section_list=[('В02','А / кухня, диван и рабочий стол'),('В03','Г / входная дверь и кухонная ветвь'),('В04','В / медиастена и книжный стеллаж'),('В05','Б / терраса, радиатор и скрытая штора'),('В06','Кухня: объёмная схема с маркировкой'),('В07','Мойка, ПММ и доступ к подключениям'),('В08','Дневной и ночной виды')]
section_list.append(('В09','Узел у входа / обе двери 1:10 и остаток 20 мм в масштабе 1:1'))
for i,(n,s) in enumerate(section_list):
    yp=102-i*8.4
    t(162,yp,n,3.6,True,gr);t(178,yp,s,3.6)
    c.linkRect('',n,(159,yp-2,398,yp+5),relative=1,thickness=0)
for i,(col,lab) in enumerate([(beige,'матовые фасады'),(oak,'светлый дуб'),(moss,'оливковый текстиль')]):
    xx=162+i*71;box(xx,31,6,4,col,fine,.15);t(xx+8,31.5,lab,3)
end()

def notes(x,y,items,step=6.2):
    for i,msg in enumerate(items):t(x,y-i*step,msg,3.15)
def tag(x,y,txt):
    w=pdfmetrics.stringWidth(txt,'b',2.95)+4
    box(x-w/2,y-1.3,w,5.1,'#ffffff','#a8b6ae',.14)
    t(x,y,txt,2.95,True,gr,'c')
def elevation(n,w,title,chain,labels,levels,side,bottom):
    stamp(n,title,'Фронтальная проекция 1:20   /   печать A3, 100 %   /   размеры в мм от чистовых плоскостей')
    ox=31 if w.w==5710 else 58
    oy=109;k=.05
    def X(u):return ox+k*u
    def Z(z):return oy+k*z
    proj=lambda u,d,z:(X(u),Z(z))
    paintwall(w,proj);details(w.name,proj)
    l(X(0)-2,oy,X(w.w)+2,oy,ink,.65)
    for a,b,s in chain:h(X(a),X(b),103,oy,s)
    h(X(0),X(w.w),94,oy,str(w.w)+' Б')
    for a,b in zip(levels,levels[1:]):v(Z(a),Z(b),ox-5,ox,str(b-a))
    v(oy,Z(2700),ox-16,ox,'2700 П')
    def pt(u,z,label):
        px,py=X(u),Z(z)
        circle(px,py,2.1,'#ffffff',gr);l(px-2,py,px+2,py,gr,.22);l(px,py-2,px,py+2,gr,.22)
        t(px+2.3,py+1,label,2.7,True,gr)
    def level(u,z,label,dx=9):
        px,py=X(u),Z(z)
        l(px,py,px+dx,py,red,.18);l(px,py,px+1.2,py+1.1,red,.3)
        t(px+dx,py+1,label,2.65,True,red,'right' if dx>0 else 'left')
    for u,z,lab in labels:
        if lab.strip():tag(X(u),Z(z),lab)
    if w is A:
        # Tiny gaps read by an offset dimension figure instead of squeezing digits between ticks.
        for a,b,dx in [(2400,2485,8),(4455,4500,-12),(5700,5710,-11)]:
            xa,xb=X(a),X(b)
            h(xa,xb,251,Z(2700),'')
            mid=(xa+xb)/2
            l(mid,251,mid+dx,255,red,.21);t(mid+dx,256,str(b-a)+' П',2.95,True,red,'c')
        for z,lab in [(775,'+775'),(1480,'+1480'),(1750,'+1750')]:level(4500,z,lab,-12)
        level(4455,940,'+940',-10);pt(4590,1000,'К2')
        for z,lab in [(680,'+680'),(1280,'+1280'),(1300,'+1300'),(1730,'+1730')]:
            if z!=1300:level(2400,z,lab,13)
        l(X(610),Z(1470),X(1100),Z(1470),gr,.55)
    elif w is G:
        h(X(1110),X(3500),256,Z(2700),'2390 Б · от проёма до угла кухни')
        h(X(1130),X(3500),248.5,Z(2700),'2370 П · от торца К8 до угла кухни')
        level(1110,2150,'+2150 М',-16)
        l(X(1119),Z(2200),X(1119)+6,Z(2280),red,.25)
        t(X(1119)+6.5,Z(2280),'20 расч. · см. В09',2.85,True,red)
        for z,lab in [(900,'+900'),(1500,'+1500')]:level(3500,z,lab,12)
    elif w is V:
        h(X(0),X(2240),252,Z(2700),'2240 П · ось поля и тумбы от террасы')
        l(X(2240),Z(2245),X(2240),250,gr,.18,True)
        v(Z(690),Z(1000),X(3480),X(3347),'310')
        h(X(840),X(1133),Z(825),None,'293')
        h(X(1133),X(3347),Z(2350),Z(2245),'2214')
        v(Z(1000),Z(2245),X(3530),X(3347),'1245')
        for z,lab in [(150,'+150'),(690,'+690')]:level(3640,z,lab,12)
        pt(4330,240,'N1');pt(4590,1000,'К1')
    else:
        h(X(2950),X(3500),251,Z(2630),'550 макс.')
        l(X(2900),Z(2240)+1,X(2900),250,red,.14)
        h(X(2900),X(2950),249,None,'');l(X(2925),249,X(2770),254,red,.18)
        t(X(2755),255,'50 расч.',2.9,True,red,'right')
        v(Z(150),Z(1750),X(690),X(750),'1600')
        for z,lab in [(150,'+150 П'),(1750,'+1750 П')]:level(750,z,lab,-13)
        for zz in (155,2190):l(X(1320),Z(zz),X(2060),Z(1165),gr,.18,True)
        pt(2975,240,'N3');level(2900,2240,'+2240 О',-16)
    level(w.w,0,'±0',8)
    sx=325 if w.w==5710 else 253
    for i,(head,rows) in enumerate(side):
        hgt=244-i*43;caption(sx,hgt,head);notes(sx,hgt-7,rows,5.6)
    caption(16,83,'Направление взгляда');key(18,32,73,w.name)
    caption(107,83,'Объём и выступы');ax(w,120,35,.0142 if w.w==5710 else .0168)
    caption(237,83,'Размерные привязки и контроль');notes(237,75,bottom,6.4)
    end()
elevation('В02',A,'Стена А · кухня, диван, рабочий стол',
 [(0,600,'600'),(600,1100,'500'),(1100,1600,'500'),(1600,1800,'200'),(1800,2400,'600'),(2485,4455,'1970'),(4500,5700,'1200')],
 [(300,1770,'К1'),(850,1770,'К2'),(1350,1770,'К3'),(1700,1770,'К4'),(2100,1930,'К5'),(3470,730,'Domo PRO 180'),(5100,1930,'РШ')],[0,900,1500,2700],
 [('Кухонный фронт',['Длина 2400, глубина 600.','Низ навесных шкафов +1500.','Духовка +680…1280 П,','СВЧ +1300…1730 П.']),('Рабочее место',['Стол 1200 × 600, верх +775.','Полка +1460…1480, Г300 П.','Шкаф 1200 × 300 × 950,','от +1750 до потолка.']),('Посадка дивана',['X2485…4455. Г1200 днём,','2230 в ночном положении.','Спинка +940 П.'])],
 ['От пенала до дивана 85. От дивана до стола 45.','От торца рабочего стола до стены Б 10 П.','К2 управления светом у стола X4590, Z+1000 П.','Глубина верхов кухни 310 — предложение К04.','Чистовую высоту промерить по концам каждого корпуса.'])
elevation('В03',G,'Стена Г · вход, холодильник, ПММ и мойка',
 [(0,200,'200'),(200,1110,'910 Б'),(1130,1730,'600'),(1730,2330,'600'),(2330,2900,'570'),(2900,3500,'600')],
 [(650,1450,'D2'),(1430,1780,'К8'),(2030,510,'К7 · ПММ'),(2615,510,'К6'),(3200,510,'К1')],[0,900,1500,2700],
 [('Кромка проёма / торец холодильника',['2390 Б от угла до проёма − 2370 П кухни = 20.','D2 без наличника. На плане ширина 910 Б,','по данным владельца 915. Высота 2115 / 2150 М.']),('Открывание внутрь',['D2 — вариант Б. Холодильник петлями к входу.','Фасад 600, расчётный поворот 90°. Дверца ПММ','выступает на 650 П. План дуг на Р01 и Р02.']),('Размеры по высоте',['Верх рабочей плоскости +900. Низ верхов +1500.','От столешницы до верхов 600. Верх кухни +2700 П.','Толщина столешницы 30 и цоколь 100 — эскиз.'])],
 ['Общий угловой модуль К1 входит в обе цепочки фасадов.','Коробку D2, ручку и угол открывания холодильника снять на месте.','20 мм — геометрический остаток по двум разным источникам.','Осевые выводы и зона доступа к сантехнике на В07.'])
elevation('В04',V,'Стена В · экран, подвесная тумба и стеллаж',
 [(0,240,'240'),(240,840,'600'),(840,3640,'2800'),(3640,5710,'2070')],
 [(234,2530,' '),(2260,1500,'100″ · поле 2214 × 1245'),(2240,365,'тумба')],[0,450,940,1420,1910,2400,2700],
 [('Книжный стеллаж',['600 × 300 × 2400 П.','Открытые полки обращены','к рабочему столу. Верхняя','секция до потолка 300 П.']),('Экран и медиатумба',['Ось экрана U2240 от террасы.','Низ +1000, верх +2245.','Тумба 2800 × 450 × 540.','Низ +150, верх +690 П.']),('База для монтажа',['5710 Б, контрольный 5705 О.','Свободный участок 2070 Б.','Проверить фактическую длину','и стык тумбы со стеллажом.'])],
 ['От края стеллажа до поля экрана 293 П. Поле по оси тумбы.','Разница глубин тумбы и стеллажа 150. Зазор над тумбой 310.','Схема фасадов тумбы — четыре равные зоны по 700 П.','Кронштейн, масса и закладная зависят от экрана и основания.'])
elevation('В05',B,'Стена Б · терраса, радиатор и парковка шторы',
 [(0,750,'750'),(750,1150,'400'),(1150,1300,'150'),(1300,2100,'800 П'),(2100,2900,'800 П'),(2900,3500,'600 Б')],
 [(950,935,'РД'),(1700,1250,'левая'),(2500,1250,'правая'),(3225,1800,'штора')],[0,115,2240,2700],
 [('Остекление O1 · вид из комнаты',['Две створки, ширина проёма 1600 Б / 1598 О.','Левая створка открывается внутрь от левого косяка.','Откос и верхнюю кромку +2240 сверить от пола.']),('Радиатор и штора',['Радиатор 400 × 1600, вынос с арматурой до 120 П.','Низ +150 — предлагаемая отметка, подключение М.','Ширина стоянки ткани до 550 П. Глубина 160 П.']),('Контроль у открытой створки',['Левый косяк в 1300 от стороны рабочего стола.','При вылете створки 800 до дивана остаётся 455.','Ниша карниза и зазор ручки — по мотору и ткани.'])],
 ['За правым косяком 600 Б. После парковки ткани 550 остаётся 50.','N3 привязан к стене Б, Y525 и Z+240 П. Попадает за сборку ткани.','Точное место N3 выбрать вне ткани и хода створки после примерки.','Радиатор расположен между столом и левым откосом, см. Р12.'])


stamp('В06','Угловая кухня · план и аксонометрия','Две ветви и единый угол К1   /   план 1:15   /   аксонометрия со снятыми верхними шкафами')
units=[(0,0,600,600,'К1'),(600,0,500,600,'К2'),(1100,0,500,600,'К3'),(1600,0,200,600,'К4'),(1800,0,600,600,'К5'),(0,600,600,570,'К6'),(0,1170,600,600,'К7'),(0,1770,600,600,'К8')]
def planxy(a,b):return (35+a/15,218-b/15)
def drawtop(proj):
    def surface(x,y,w,d,z,col):
        poly([proj(a,b,z) for a,b in [(x,y),(x+w,y),(x+w,y+d),(x,y+d)]],col)
    surface(1140,80,420,425,902,metal)
    for a,b in [(1260,200),(1450,385)]:
        pts=[proj(a+64*cos(i*pi/12),b+64*sin(i*pi/12),903) for i in range(25)]
        for p,q in zip(pts,pts[1:]):l(*p,*q,cream,.22)
    surface(65,640,470,490,902,'#c8cfca');surface(130,680,367,415,903,'#a1b1a9')
def locplan():
    for a,b,w,d,name in units:
        xx,yy=planxy(a,b+d);box(xx,yy,w/15,d/15,oak if name in ['К8','К5'] else beige)
    drawtop(lambda a,b,z:planxy(a,b))
    for a,b,w,d,name in units:
        x,y=planxy(a+w/2,b+d/2);tag(x,y-1,name)
    for a,b in zip([0,600,1100,1600,1800],[600,1100,1600,1800,2400]):
        h(planxy(a,0)[0],planxy(b,0)[0],225,218,str(b-a))
    h(35,195,234,218,'2400')
    for a,b in zip([0,600,1170,1770],[600,1170,1770,2370]):
        v(planxy(0,b)[1],planxy(0,a)[1],28,35,str(b-a))
    v(60,218,17,35,'2370')
    h(35,75,51,60,'600');v(178,218,200,195,'600')
locplan()
caption(88,155,'Узел D2 / К8 · план 1:25')
# Entry-side detail, X to the right and Y upwards, same orientation as Р01.
def hinge(x,y,r,sign):
    points=[(x+r*sin(i*pi/48),y+sign*r*cos(i*pi/48)) for i in range(25)]
    for p,q in zip(points,points[1:]):l(*p,*q,gr,.2,True)
    l(x,y,x+r,y,gr,.65);circle(x,y,1.55,gr,gr)
xd=101;yd=75
l(xd,yd-3,xd,yd+8,ink,.75);l(xd,yd+44.4,xd,yd+75,ink,.75)
box(xd,yd+45.2,24,24,beige);tag(xd+12,yd+56,'К8')
hinge(xd,yd+8,36.4,1);hinge(xd+24,yd+45.2,24,1)
v(yd+8,yd+44.4,xd-5,xd,'910 Б');h(xd,xd+24,yd+73,yd+69.2,'600')
t(127,yd+29,'D2 открыта на 90°',2.7,True,gr)
t(143,yd+48,'холодильник',2.7,True,gr)
t(89,62,'Петли показаны точками. Контуры дверей условны.',2.85)
caption(35,249,'01    План столешниц и пеналов')
caption(222,249,'02    Объём со стороны комнаты')
def model(a,b,z):return (306+(a-b)*.036,159-(a+b)*.014+z*.033)
def shellblock(a,b,w,d,z0,z1,col):
    a1=a+w;b1=b+d
    for vs,shade in [([(a1,b,z0),(a1,b1,z0),(a1,b1,z1),(a1,b,z1)],col), ([(a,b1,z0),(a1,b1,z0),(a1,b1,z1),(a,b1,z1)],col), ([(a,b,z1),(a1,b,z1),(a1,b1,z1),(a,b1,z1)],cream)]:
        poly([model(*p) for p in vs],shade)
def iso_face(a,b,w,d):
    pts=[(a,b,0),(a+w,b+d,0),(a+w,b+d,2700),(a,b,2700)]
    poly([model(*p) for p in pts],'#f1eee7')
iso_face(0,0,2400,0);iso_face(0,0,0,2370)
for a,b,w,d,name in sorted(units,key=lambda itm:itm[0]+itm[1]):
    ht=2700 if name in ['К8','К5'] else 900
    shellblock(a,b,w,d,0,ht,beige if ht==2700 else '#d6c7b5')
    if name=='К6':
        def sinkpatch(a0,b0,w0,d0,col):poly([model(a1,b1,905) for a1,b1 in [(a0,b0),(a0+w0,b0),(a0+w0,b0+d0),(a0,b0+d0)]],col)
        sinkpatch(65,640,470,490,'#c5d0c9');sinkpatch(130,680,367,415,'#9ea9a3')
    if name=='К3':poly([model(xx,yy,905) for xx,yy in [(1140,80),(1560,80),(1560,505),(1140,505)]],metal)
    if name=='К5':
        for za,hh in [(680,600),(1300,430)]:
            poly([model(aa,601,z) for aa,z in [(1825,za),(2375,za),(2375,za+hh),(1825,za+hh)]],metal)
    px,py=model(a+w*.5,b+d,1850 if ht==2700 else 520) if b==0 else model(a+w,b+d*.5,1850 if ht==2700 else 520)
    tag(px,py,name)
def axdim(p,q,offset,label):
    a=(p[0]+offset[0],p[1]+offset[1]);b=(q[0]+offset[0],q[1]+offset[1])
    for orig,to in [(p,a),(q,b)]:
        l(*orig,*to,fine,.15);l(to[0]-.7,to[1]-.85,to[0]+.7,to[1]+.85,red,.23)
    l(*a,*b,red,.20);t((a[0]+b[0])/2,(a[1]+b[1])/2+1.1,label,2.9,True,red,'c')
for intervals,along_a in [([600,1100,1600,1800,2400],True),([600,1170,1770,2370],False)]:
    for start,stop in zip(intervals,intervals[1:]):
        startpoint=model(start,600,0) if along_a else model(600,start,0)
        endpoint=model(stop,600,0) if along_a else model(600,stop,0)
        axdim(startpoint,endpoint,(0,-4),str(stop-start))
axdim(model(2400,600,0),model(600,600,0),(0,-11),'1800')
axdim(model(600,2370,0),model(600,600,0),(0,-11),'1770')
pv=model(2400,0,0);v(pv[1],model(2400,0,2700)[1],pv[0]+6,pv[0],'2700 П')
caption(216,98,'Модули и рабочие поверхности')
for i,s in enumerate(['К1   Общий угол 600 × 600. Корпус и доступ уточняет изготовитель.','К2   Рабочая зона 500.    К3   Варка, модуль 500.    К4   Выкат 200.','К5   Колонна 600 у дивана.    К6   Мойка в модуле 570.','К7   ПММ в нише 600.    К8   Колонна холодильника 600 у входа.','Глубина обеих ветвей 600 П. Вылеты фасадов и ручек — М.','Контуры чаши и варки условны. Вырезы выполняются по шаблонам.']):
    t(216,88-i*8,s,3.2)
caption(35,38,'Край D2 и торец К8 · крупный план и размер 20 на В09.')
end()

stamp('В07','Мойка и ПММ · сервисный доступ','Фрагмент фасада и разрез 1:10   /   все размеры в мм   /   предлагаемая зона размещения арматуры')
caption(25,248,'01    Вид на стену Г со снятыми фасадами')
x0=38;z0=126;q=.1
def svc(u,z,w,hgt,col):
    box(x0+u*q,z0+z*q,w*q,hgt*q,col)
svc(0,0,1170,100,'#d9d6c9');svc(0,100,600,770,'#dadfda');svc(600,100,570,770,cream);svc(0,870,1170,30,oak)
svc(720,250,330,350,'#dae8df')
# Bowl envelope and schematic trap, intentionally no installation centres.
poly([(101,213),(103,195),(148,195),(150,213)],'#ccd6cf')
for x1,y1,x2,y2 in [(126,195,126,190),(126,190,130,187),(130,187,134,190),(134,190,134,193),(134,193,138,193)]:l(x1,y1,x2,y2,metal,.5)
tag(68,167,'К7 · ПММ');t(126.5,166,'зона доступа',3,True,gr,'c')
for a,b in [(0,600),(600,1170)]:h(x0+a*q,x0+b*q,117,z0,str(b-a))
h(x0,x0+117,109,z0,'1170')
v(z0,z0+90,26,x0,'900');v(z0+25,z0+60,163,143,'350')
h(110,143,145,None,'330')
h(98,110,140,151,'120');h(143,155,140,151,'120')
v(z0,151,171,155,'250');v(z0+10,z0+87,31,38,'770')
h(98,155,222,216,'570 П')
caption(180,246,'02    Разрез')
# One consistent wall section, including upper and countertop at 1:10.
xx=196;zy=60
l(xx,zy,xx,zy+181,ink,.65);l(xx-3,zy,xx+68,zy,ink,.55)
box(xx,zy+10,59,77,beige);box(xx,zy+87,60,3,oak);box(xx,zy,55.5,10,'#cccbc1')
box(xx,zy+150,31,25,beige);l(xx+31,zy+150,xx+31,zy+147,gr,.75)
t(xx+32,zy+152,'L3',2.9,True,gr)
for a,b,xx1,lab in [(0,90,186,'900'),(90,150,186,'600'),(0,10,263,'100')]:v(zy+a,zy+b,xx1,xx if xx1<xx else xx+60,lab)
h(xx,xx+60,52,zy,'600');h(xx,xx+31,zy+179,zy+175,'310 П')
caption(278,235,'Привязки К6 и К7');notes(278,225,[
 'К6 начинается в 2330 от стены В по Y.',
 'Ширина 570, глубина 600, столешница +900.',
 'К7 примыкает со стороны холодильника.',
 'Корпус ПММ в нише 600. Дверь: вылет 650 П.'])
caption(278,183,'Доступ в пределах К6 · предложение');notes(278,173,[
 'Зона 330 × 350. Отступ от левой грани К6 — 120.',
 'Низ зоны +250, верх +600 от чистого пола.',
 'Предусмотреть съёмный доступ из тумбы мойки.',
 'Проверить место при установленной чаше,',
 'сифоне, фильтре и выдвинутых контейнерах.'])
caption(278,124,'Что привязать после выбора изделий');notes(278,114,[
 'Оси ХВС, ГВС и канализации, отметки и диаметры.',
 'Проход шлангов К7 в К6 и радиусы по паспорту.',
 'Доступ к крану ПММ и соединениям из К6.',
 'Розетку ПММ согласовать в доступном сухом месте.',
 'Зону 330 × 350 уточнить после натурной примерки.'])
caption(28,87,'Состав сечения · проектные размеры');notes(28,77,[
 'Цоколь 100, фасадная зона 770, столешница 30.',
 'Низ верхов +1500 П, выход линии L3 на +1470 П.',
 'Глубина низа 600, корпуса верха 310 П.',
 'Глубина чаши, вырезы и детали корпусов — М.'])
end()


def sceneplan(x,y,night):
    k=1/44
    def R(a,b,w,d,col):box(x+a*k,y+b*k,w*k,d*k,col,fine,.18)
    R(0,0,5710,3500,'#f8f6f0')
    for a,b,w,d,name in units:R(a,3500-b-d,w,d,beige)
    R(2485,1270 if night else 2300,1970,2230 if night else 1200,moss);R(4500,2900,1200,600,oak)
    R(2070,0,2800,450,beige);R(4870,0,600,300,oak);R(5590,2350,120,400,metal);R(5550,0,160,550,'#ccbaa1')
    R(*( (1600,1370,800,1400) if night else (2770,1500,1400,800) ),cream)
    for a,b in ([(1500,1560),(1500,2160)] if night else [(2880,1100),(3600,1100)]):R(a,b,400,400,oak)
    cx,cy=(5000,3010) if night else (4750,2730)
    circle(x+cx*k,y+cy*k,520*k,moss)
    def door(a,b,r,dx,dy):
        p=[(x+(a+dx*r*sin(i*pi/48))*k,y+(b+dy*r*cos(i*pi/48))*k) for i in range(25)]
        for p1,p2 in zip(p,p[1:]):l(*p1,*p2,gr,.16,True)
        l(x+a*k,y+b*k,x+(a+dx*r)*k,y+b*k,gr,.6)
    door(0,200,910,1,1);door(5710,2200,800,-1,-1)
    if night:
        v(y+450*k,y+1270*k,x+3400*k,None,'820')
        h(x+4455*k,x+4910*k,y+2100*k,None,'455')
    else:v(y+450*k,y+1100*k,x+3300*k,None,'650')
    h(x+2485*k,x+4455*k,y+3500*k+4,y+3500*k,'1970')
    v(y+(1270 if night else 2300)*k,y+3500*k,x+2650*k,None,'2230' if night else '1200')
    if night:
        h(x+1600*k,x+2400*k,y+1150*k,None,'800')
    else:
        h(x+2770*k,x+4170*k,y+1870*k,None,'1400')
stamp('В08','День и ночь · мебель и проходы','Два положения в одной системе координат   /   планы в одном масштабе 1:44   /   виды показывают характер материалов')
fitimg('B01_общий_вид_шкафы_до_потолка_штора_справа_v1.png',16,147,186,105,(0,0,.85,1))
fitimg('B01_общий_вид_Domo180_разложен_штора_справа_v1.png',218,147,186,105,(0,0,.85,1))
caption(19,141,'01    День · стол вплотную к дивану');caption(220,141,'02    Ночь · стол перенесён к кухне')
sceneplan(26,45,False);sceneplan(229,45,True)
t(26,35,'За придвинутыми стульями 650 П. При выдвижении на 300 остаётся 350.',3.2)
t(225,35,'У изножья 820 П, у створки к столу 455 П. Проверить проход в натуре.',3.2)
end()

stamp('В09','Вход в B01 · дверь D2 и холодильник К8',
      'Вид сверху  /  D2 открывается внутрь к медиастене, вариант Б  /  К8 петлями к входу  /  размеры в мм')
cool='#16697a';warm='#a65729';wash='#e2f0f0';sand='#f8ecdf'
caption(18,250,'01    Обе двери · план 1:10')
caption(210,250,'02    У кромки проёма · деталь А, план 1:1')
l(199,29,199,254,'#c4cec8',.22)
# Global Y increases along the entrance wall from the media wall to the kitchen corner.
X=lambda u:52+u/10
Y=lambda u:54+u/10
wall='#d4dad5'
box(46,Y(0),6,20,wall)
box(46,Y(1110),6,Y(1820)-Y(1110),wall)
l(X(0),Y(0),X(1330),Y(0),ink,.8)
box(X(0),Y(1130),60,60,beige,ink,.45)
t(X(300),Y(1460),'К8',5.2,True,ink,'c');t(X(300),Y(1390),'холодильник',3.3,False,ink,'c')
h(X(0),X(600),235,Y(1730),'600 П · глубина')
v(Y(1130),Y(1730),36,X(0),'600 П')
v(Y(200),Y(1110),36,X(0),'910 Б')
v(Y(0),Y(200),36,X(0),'200 Б')
def swept(a,b,r,col,fill):
    px,py=X(a),Y(b)
    path=[(px+r/10*sin(i*pi/72),py+r/10*cos(i*pi/72)) for i in range(37)]
    poly([(px,py)]+path,fill,fill,.1)
    for p,q in zip(path,path[1:]):l(*p,*q,col,.42)
    l(px,py,px,py+r/10,col,.54,True)
    l(px,py,px+r/10,py,col,1.05)
    # One tangential arrow at 53 degrees identifies the opening direction.
    aa=53*pi/180;xc=px+r/10*sin(aa);yc=py+r/10*cos(aa)
    dx,dy=cos(aa),-sin(aa)
    poly([(xc,yc),(xc-3.4*dx+1.3*dy,yc-3.4*dy-1.3*dx),
          (xc-3.4*dx-1.3*dy,yc-3.4*dy+1.3*dx)],col,col)
    circle(px,py,2.9,'#ffffff',col);circle(px,py,.85,col,col)
swept(0,200,910,cool,wash);swept(600,1130,600,warm,sand)
t(66,118,'D2',6,True,cool);t(66,110,'R910 по проёму БТИ',3.5,False,cool)
t(65,100,'петли к медиастене',3.25,False,cool)
t(114,183,'R600 П',3.6,True,warm);t(120,160,'К8 открыт на 90°',3.45,True,warm)
t(61,67,'D2 открыта на 90°',3.5,True,cool);t(110,48,'стена В · база Y0',3,False,ink)
circle(X(0),Y(1120),7.6,'#ffffff',red)
# Restore actual edges inside the detail marker.
l(X(0)-3,Y(1110),X(0),Y(1110),ink,.55)
l(X(0),Y(1130),X(0)+3,Y(1130),ink,.55)
l(X(0)+2,Y(1120)+3,64,180,red,.22);t(65,179,'А',4,True,red)
t(18,36,'Штрих — закрыто. Сплошная — открыто. Кружок — ось петли.',3.15)
t(18,30,'Радиусы расчётные. Обе створки показаны при повороте в комнату.',3.15)

# The parallel reference edges are exactly 20 paper mm apart at natural scale.
zlo=181;zhi=201;face=246
box(face-12,zlo,12,49,wall,ink,.35)
box(face,zhi,90,29,beige,ink,.43)
l(face-12,zlo,face,zlo,red,.65);l(face,zhi,face+90,zhi,warm,.65)
l(face,zlo,face,zlo-12,cool,.48,True)
t(face+5,218,'К8 · фрагмент корпуса',4,True)
t(face+5,211,'Торец кухни   Y1130 П',3.6,True,warm)
l(face-12,zlo,347,zlo,red,.22,True);l(face+90,zhi,347,zhi,red,.22)
v(zlo,zhi,350,None,'')
t(357,190,'20 мм',6.2,True,red)
t(face+5,zlo-7,'Грань проёма D2   Y1110 Б',3.6,True,red)
t(212,160,'Фрагмент стены у откоса. Коробка без наличника. Положение коробки — М.',3.35)
l(211,152,400,152,'#c4cec8',.23)
caption(212,141,'Как получен размер')
t(212,128,'2390 Б − 2370 П = 20 мм',6.2,True,red)
t(212,117,'2390 от кухонного угла до края проёма D2 по плану БТИ.',3.5)
t(212,110,'2370 от того же угла до торца К8: 600 + 570 + 600 + 600.',3.5)
caption(212,94,'Совместное открывание')
notes(212,85,['В модели до 90° секторы D2 и К8 раздельны. Остаток 20 мм',
              'рассчитан вдоль стены между проёмом и корпусом. Для оценки',
              'траекторий на объекте нужны оси петель, толщина полотен и вылет ручек.'],6.0)
caption(212,59,'Контроль перед заказом')
notes(212,50,['Измерить от чистового кухонного угла до установленной коробки D2.',
              'Сверить ширину проёма 910 Б / 915 по контрольным данным.',
              'Проверить обе ручки, предельный угол и выдвижение ящиков К8.'],6.0)
end()
c.save()
detail_path=P/'B01_В09_Вход_дверь_и_холодильник_К05.pdf'
detail_writer=PdfWriter()
detail_writer.add_page(PdfReader(out).pages[-1])
detail_writer.add_metadata({'/Title':'B01 · К05 · Узел у входа D2 / К8'})
with detail_path.open('wb') as stream:detail_writer.write(stream)
published=P/'B01_Кухня-гостиная_Альбом_К05.pdf'
writer=PdfWriter()
for src,section in [(out,'К05 · развёртки и виды'),(P/'B01_Размерные_чертежи_К03.pdf','К03 · размерные чертежи Р01–Р16'),(P/'B01_Кухня-гостиная_Альбом_К01.pdf','К01 · исходный альбом и спецификации')]:
    writer.append(src,outline_item=section)
writer.add_metadata({'/Title':'B01 · Кухня-гостиная · Альбом К05','/Author':'Проект квартиры • B01'})
with published.open('wb') as stream:writer.write(stream)
print(out.name,len(PdfReader(out).pages),published.name,len(PdfReader(published).pages))

