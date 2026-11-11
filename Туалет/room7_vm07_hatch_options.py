from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
im=Image.new('RGB',(2400,1480),'#f6f3ed'); d=ImageDraw.Draw(im)
reg='C:/Windows/Fonts/arial.ttf'; bold='C:/Windows/Fonts/arialbd.ttf'
def text(x,y,s,n=24,b=False,c='#26372f'): d.text((x,y),s,font=ImageFont.truetype(bold if b else reg,n),fill=c)
def line(xy,c='#55635a',w=3): d.line(xy,fill=c,width=w)
def arrow(x1,y1,x2,y2,c='#b16c30'):
 import math
 line((x1,y1,x2,y2),c,5); a=math.atan2(y2-y1,x2-x1); L=18
 d.polygon([(x2,y2),(x2-L*math.cos(a-.45),y2-L*math.sin(a-.45)),(x2-L*math.cos(a+.45),y2-L*math.sin(a+.45))],fill=c)
def dashrect(x1,y1,x2,y2,c='#b16c30'):
 for y in range(y1,y2,20): line((x1,y,x1,min(y+10,y2)),c,3);line((x2,y,x2,min(y+10,y2)),c,3)
 for x in range(x1,x2,20): line((x,y1,min(x+10,x2),y1),c,3);line((x,y2,min(x+10,x2),y2),c,3)
text(70,32,'ВМ-07 · ВАРИАНТЫ РЕВИЗИОННОГО ЛЮКА',42,True)
text(70,95,'Вид от двери на унитаз. Схемы условные: высота и положение счётчиков и люка пока неизвестны.',23,c='#62716a')
panels=[(70,'A  РАСПАШНОЙ','Открывается на петле'),(845,'B  СЪЁМНЫЙ','Вынимается на себя'),(1620,'C  СДВИЖНОЙ','Вперёд и вдоль стены')]
for i,(x,title,sub) in enumerate(panels):
 text(x,155,title,30,True);text(x,200,sub,22,c='#62716a')
 # 710 wide footprint diagram - same for all options. Height schematic.
 bx=x+75; by=265; bw=505; bh=700
 d.rectangle((bx,by,bx+bw,by+bh),fill='#e4ddd1',outline='#859087',width=3)
 text(bx+120,by+20,'ВМ-07 · 710 мм',22,True)
 # hypothetical hatch above flush button; nothing is measured.
 hx=bx+110; hy=by+95; hw=285; hh=220
 dashrect(hx,hy,hx+hw,hy+hh)
 text(hx+30,hy+84,'ЛЮК ?',29,True,c='#9e5b2b')
 d.rounded_rectangle((bx+170,by+370,bx+335,by+420),radius=5,fill='#a47b48')
 text(bx+158,by+431,'кнопка смыва',18,c='#655a4a')
 # toilet fixed and front-facing
 d.rounded_rectangle((bx+115,by+493,bx+390,by+625),radius=45,fill='#ffffff',outline='#8c9991',width=3)
 d.ellipse((bx+142,by+548,bx+363,by+666),fill='#fbfaf6',outline='#8c9991',width=3)
 text(bx+225,by+690,'WC',21,True)
 if i==0:
  line((hx,hy,hx,hy+hh),'#ab6b35',8);arrow(hx+hw-40,hy+hh//2,hx+hw+65,hy+hh//2)
  text(x,1005,'Нужен вылет дверцы и место',22);text(x,1040,'для поворота над чашей.',22)
  text(x,1084,'Плюс: простое ежедневное',22);text(x,1119,'открывание, дверца на петле.',22)
 elif i==1:
  arrow(hx+hw//2,hy+hh//2,hx+hw//2+110,hy+hh//2+85)
  text(x,1005,'Панель снимается целиком;',22);text(x,1040,'нужно место для её извлечения.',22)
  text(x,1084,'Страховка от падения и вес',22);text(x,1119,'керамогранита — по паспорту.',22)
 else:
  arrow(hx+hw//2,hy+hh//2,hx+hw+105,hy+hh//2)
  text(x,1005,'Створка сначала выходит вперёд,',22);text(x,1040,'затем сдвигается в сторону.',22)
  text(x,1084,'Нужно свободное место сбоку:',22);text(x,1119,'тумба и стена могут мешать.',22)
text(70,1225,'Счётчики специально не нарисованы: их фактическое положение неизвестно.',25,True,c='#9b512e')
text(70,1270,'Короб 710 × 360 мм — по плану B01; место люка, его высота и размер проёма — не обмерены.',23)
text(70,1315,'Люк должен открываться при установленном WC и позволять снять и заменить счётчики и арматуру.',23)
text(70,1360,'Все три варианта требуют проверки на объекте; штриховая рамка не означает выбранное положение.',23)
out=Path(__file__).with_name('room7_vm07_hatch_options.png');im.save(out);print(out)
