from PIL import Image, ImageDraw, ImageFont
import math
OUT=r'D:\6 Проекты\Квартира\output\visualizations\B01_мансарда_вариант_А_ночь_v2.png'
im=Image.new('RGB',(2300,1600),'#f8f6f0');d=ImageDraw.Draw(im)
def t(x,y,s,z=24,c='#263d37',b=False,a=None):
 d.multiline_text((x,y),s,font=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if b else 'C:/Windows/Fonts/arial.ttf',z),fill=c,anchor=a,align='center',spacing=4)
t(65,35,'B01 · ЛЕВАЯ СТВОРКА МАНСАРДЫ · НОЧНОЙ РЕЖИМ',40,b=True)
t(65,100,'Левая створка открывается внутрь · петли на краю проёма · вариант А подтверждён',27,'#a3432f')
k=.16; top=310; bottom=top+3500*k
def panel(ox,edge):
 def X(x):return ox+k*x
 def Y(y):return bottom-k*y
 def line(x,y,x2,y2,c,w=4):d.line((X(x),Y(y),X(x2),Y(y2)),fill=c,width=w)
 def box(x,y,x2,y2,col,s,z=18):
  q=(X(x),Y(y2),X(x2),Y(y));d.rectangle(q,fill=col,outline='#54665f',width=2)
  if s:t((q[0]+q[2])/2,(q[1]+q[3])/2,s,z,b=True,a='mm')
 d.rectangle((X(0),Y(3500),X(5710),Y(0)),fill='white',outline='#354b44',width=4)
 for x,y,x2,y2,c,s in [(0,2900,600,3500,'#ded1bd','УГОЛ\n600'),(600,2900,1100,3500,'#ede6da','500'),(1100,2900,1600,3500,'#ede6da','ВАРКА\n500'),(1600,2900,1800,3500,'#f0d7a7','200'),(1800,2900,2400,3500,'#dac3a8','ПЕНАЛ\n600'),(0,2330,600,2900,'#e4e3d0','МОЙКА\n570'),(0,1730,600,2330,'#b8ded6','ПММ\n600'),(0,1130,600,1730,'#d9c4aa','ХОЛ.\n600'),(2485,1270,4455,3500,'#e0b5aa','ДИВАН РАСКРЫТ\n1970 × 2230'),(4500,2900,5700,3500,'#d5e3df','РАБОТА'),(2070,0,4870,450,'#cbbba7','МЕДИАТУМБА'),(4870,0,5470,300,'#b49c7c','')]:box(x,y,x2,y2,c,s)
 line(0,200,0,1110,'#168587',7);line(5710,600,5710,2200,'#168587',8)
 # Left leaf from inside assumed in upper half of drawing; equal half width is a hypothesis.
 hinge=2200 if edge else 1400; sign=-1 if edge else 1
 pts=[(X(5710-800*math.sin(math.pi*i/180)),Y(hinge+sign*800*math.cos(math.pi*i/180))) for i in range(91)]
 d.line(pts,fill='#a43e2d',width=3);line(5710,hinge,4910,hinge,'#a43e2d',6)
 d.ellipse((X(5710)-6,Y(hinge)-6,X(5710)+6,Y(hinge)+6),fill='#a43e2d')
 # Local horizontal clearance from open edge to bed, at the door's hinge coordinate.
 line(4455,hinge-105,4910,hinge-105,'#a43e2d',3)
 t(X(4682),Y(hinge-105)-12,'455*',19,'#a43e2d',True,a='mm')
 t(X(0)-15,Y(655),'D2',20,'#168587',True,a='rm');t(X(5710)+12,Y(1400),'O1',20,'#168587',True,a='lm')
 t((X(0)+X(5710))/2,Y(0)+28,'5710 × 3500 мм · расчётная база',20,a='mt')
t(430,205,'ВАРИАНТ А · ПЕТЛИ НА КРАЮ ПРОЁМА',27,b=True)
panel(500,True)
t(70,970,'КРАСНЫМ — ОТКРЫВАНИЕ ЛЕВОЙ СТВОРКИ ПО ВАРИАНТУ А',27,'#a3432f',True)
lines=['Предположено: весь проём 1600 мм, левая створка 800 мм, открывание на 90°. Рамы и фактические размеры не известны.',
'455 мм — только локальный расчёт от края тонкой открытой створки до боковой грани дивана,',
'если она шириной 800 мм: 5710 − 800 − 4455 = 455. Это не подтверждение прохода.',
'В данной примерке дуга не пересекает контур дивана; фактическая ширина и рама створки не установлены.',
'Стол и стулья убраны. Рабочее кресло, ручки, коробки, шторы, радиатор и человек не моделировались.',
'Траектория раскладывания дивана и входная дверь в этом листе не проверяются.',
'Для точной схемы нужны ширина створки, положение рамы и реальные габариты мебели.']
for i,s in enumerate(lines):t(70,1020+i*57,s,24,'#a3432f' if i in (0,1,2,3,6) else '#263d37')
im.save(OUT);print(OUT)
