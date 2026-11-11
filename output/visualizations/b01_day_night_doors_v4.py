from PIL import Image, ImageDraw, ImageFont
import math

ROOT = r'D:\6 Проекты\Квартира\output\visualizations'
W,H=2300,1580
img=Image.new('RGB',(W,H),'#f8f6f0'); d=ImageDraw.Draw(img)
fa='C:/Windows/Fonts/arial.ttf'; fb='C:/Windows/Fonts/arialbd.ttf'
def text(x,y,s,size=25,col='#263c38',bold=False,anchor=None):
    d.multiline_text((x,y),s,font=ImageFont.truetype(fb if bold else fa,size),fill=col,anchor=anchor,align='center',spacing=4)
text(75,38,'B01 · ДЕНЬ И НОЧЬ: ДВЕРИ И КУХНЯ',43,bold=True)
text(75,100,'Предварительная геометрическая примерка · размеры в мм · не для заказа',26,col='#a74935')
scale=.162; top=290; oy=top+3500*scale
def panel(ox,night=False):
    def X(x):return ox+x*scale
    def Y(y):return oy-y*scale
    def rect(x1,y1,x2,y2,fill,lab='',sz=19, outline='#58665d'):
        box=(X(x1),Y(y2),X(x2),Y(y1));d.rectangle(box,fill=fill,outline=outline,width=2)
        if lab:text((box[0]+box[2])/2,(box[1]+box[3])/2,lab,sz,bold=True,anchor='mm')
    def line(x1,y1,x2,y2,fill='#386c69',w=5):d.line((X(x1),Y(y1),X(x2),Y(y2)),fill=fill,width=w)
    d.rectangle((X(0),Y(3500),X(5710),Y(0)),fill='#ffffff',outline='#354b46',width=4)
    line(0,200,0,1110,'#138589',9);line(5710,600,5710,2200,'#138589',9)
    rect(0,2900,600,3500,'#d9d0bf','УГОЛ\n600',18)
    rect(600,2900,1100,3500,'#ebe4d9','500',19)
    rect(1100,2900,1600,3500,'#ebe4d9','ВАРКА\n500',18)
    rect(1600,2900,1800,3500,'#f3d9ad','200',16)
    rect(1800,2900,2400,3500,'#d5c1a9','ПЕНАЛ\n600',18)
    rect(0,2330,600,2900,'#e7e3d2','МОЙКА\n570',18)
    rect(0,1730,600,2330,'#c8dfd8','ПММ\n600',18)
    rect(0,1130,600,1730,'#d5c1a9','ХОЛ.\n600',18)
    rect(4500,2900,5700,3500,'#d3e1df','РАБОТА\n1200 × 600',19)
    rect(2070,0,4870,450,'#cbbba6','МЕДИАТУМБА 2800 × 450',19)
    rect(4870,0,5470,300,'#b69773','КНИГИ',16)
    if night:
        rect(2485,1270,4455,3500,'#e2b2a6','ДИВАН-КРОВАТЬ\n1970 × 2230',24)
        line(3450,450,3450,1270,'#a14330',4)
        for y in (450,1270):line(3380,y,3520,y,'#a14330',4)
        text(X(3550),Y(860),'820',22,'#a14330',True,anchor='mm')

    else:
        rect(2485,2300,4455,3500,'#d8cbbb','ДИВАН\n1970 × 1200',21)
        rect(2770,1500,4170,2300,'#bcd1b6','СТОЛ\n1400 × 800*',20)
        rect(2880,1100,3280,1500,'#d99a78','СТУЛ',16)
        rect(3600,1100,4000,1500,'#d99a78','СТУЛ',16)
        for a,b in [(2880,3280),(3600,4000)]:
            box=(X(a),Y(1200),X(b),Y(800));d.rectangle(box,outline='#b14c3b',width=3)
        line(3400,450,3400,800,'#a14330',4)
        text(X(3470),Y(625),'350',20,'#a14330',True,anchor='mm')
    def swing(hx,hy,L,dx,dy,color):
        pts=[(X(hx+dx*L*math.sin(math.pi*i/180)), Y(hy+dy*L*math.cos(math.pi*i/180))) for i in range(91)]
        d.line(pts,fill=color,width=3)
        line(hx,hy,hx+dx*L,hy,color,5)
        d.ellipse((X(hx)-5,Y(hy)-5,X(hx)+5,Y(hy)+5),fill=color)
    swing(0,200,910,1,1,'#b34230')
    swing(600,1130,600,1,1,'#3672b8')
    swing(5710,2200,800,-1,-1,'#b34230')
    text(X(0)-10,Y(655),'D2',19,'#138589',True,anchor='rm')
    text(X(5710)+10,Y(1400),'O1',19,'#138589',True,anchor='lm')
    text((X(0)+X(5710))/2,Y(0)+32,'5710 мм · по исходному плану',20,anchor='mt')
    text(X(0),Y(0)+70,'Вход D2 слева · терраса O1 справа',19,anchor='lt')
text(95,205,'ДЕНЬ · СТОЛ И 2 СТУЛА',31,bold=True)
text(1220,205,'НОЧЬ · СТОЛ И СТУЛЬЯ УБРАНЫ',31,bold=True)
panel(105,False);panel(1235,True)
text(80,990,'ПРОВЕРКА ПО РАСЧЁТНЫМ КОНТУРАМ',30,bold=True)
lines=[
'КРАСНЫЙ: вход D2 и левая створка O1 открыты внутрь на условные 90°. СИНИЙ: холодильник.',
'D2: петли со стороны медиастены; O1: левая створка, петли у края. Холодильник: петли у входа.',
'На мансарде створка условно 800 мм из проёма 1600 мм: фактический размер и рама неизвестны.',
'НОЧЬ: от изножья до медиатумбы 820 мм; при открытой условной створке локально до дивана 455 мм.',
'ДЕНЬ: от условного стула до тумбы 650 мм; при сдвиге стула на 300 мм остаётся 350 мм.',
'ПММ 600: до края входного проёма расчётно 20 мм без коробки и мебельных доборов; наличника нет.',
'Все показанные положения — геометрическая примерка: реальные створки, ручки, кресло, человек,',
'ящики, двери техники, перемещение стола и траектория раскладывания дивана не проверены.'
]
for i,s in enumerate(lines):text(80,1045+i*48,s,25,col='#a14330' if i in (0,6,7) else '#263c38')
out=ROOT+'\\B01_день_ночь_двери_ПММ600_v4.png';img.save(out);print(out)
