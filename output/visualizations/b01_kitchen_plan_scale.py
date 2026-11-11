from PIL import Image, ImageDraw, ImageFont

P = r'D:\6 Проекты\Квартира\output\visualizations\B01_кухня_размерная_схема_v4.png'
im = Image.new('RGB', (1800, 1450), '#f7f5ef')
d = ImageDraw.Draw(im)
regular = 'C:/Windows/Fonts/arial.ttf'
bold = 'C:/Windows/Fonts/arialbd.ttf'
def f(size, b=False): return ImageFont.truetype(bold if b else regular, size)
def label(x, y, value, size=28, color='#273b36', b=False, anchor=None):
    d.text((x, y), value, font=f(size, b), fill=color, anchor=anchor, align='center', spacing=6)

label(90, 42, 'B01 · КУХНЯ ПО РАЗМЕРНОЙ ПРИМЕРКЕ', 44, b=True)
label(90, 105, 'Вид сверху · размеры в мм · предварительная компоновка', 27)
label(90, 145, 'ПММ 450 мм — допущение; размеры угла и привязки требуют обмера', 25, '#a43c29')

ox, oy, scale = 265, 270, .39
def X(n): return ox + round(n*scale)
def Y(n): return oy + round(n*scale)
def rect(x1,y1,x2,y2,c):
    d.rectangle((X(x1),Y(y1),X(x2),Y(y2)), fill=c, outline='#3e5149', width=3)
def center(x1,y1,x2,y2,t,size=24): label((X(x1)+X(x2))//2,(Y(y1)+Y(y2))//2,t,size,anchor='mm',b=True)

rect(0,0,600,600,'#dfd2be'); center(0,0,600,600,'УГОЛ\n600 × 600')
rect(600,0,1100,600,'#eee8dc'); center(600,0,1100,600,'РАБОТА\n500')
rect(1100,0,1600,600,'#eee8dc'); center(1100,0,1600,600,'ВАРКА\n500')
rect(1600,0,1800,600,'#f2d9a7'); center(1600,0,1800,600,'200',22)
rect(1800,0,2400,600,'#d9c5ae'); center(1800,0,2400,600,'ПЕНАЛ\n600')
rect(0,600,600,1170,'#e5e1ce'); center(0,600,600,1170,'МОЙКА\n570')
rect(0,1170,600,1620,'#cbe1d9'); center(0,1170,600,1620,'ПММ\n450*')
rect(0,1620,600,2220,'#d9c5ae'); center(0,1620,600,2220,'ХОЛОДИЛЬНИК\n600',23)

# Parallel dimensions, annotated outside the scaled kitchen diagram.
d.line((X(0),Y(0)-20,X(2400),Y(0)-20),fill='#25483d',width=3)
for n in (0,600,1100,1600,1800,2400): d.line((X(n),Y(0)-29,X(n),Y(0)-10),fill='#25483d',width=3)
label((X(0)+X(2400))//2,Y(0)-57,'ОБЩИЙ ОХВАТ 2400*',27,b=True,anchor='mm')
d.line((X(0)-40,Y(0),X(0)-40,Y(2220)),fill='#25483d',width=3)
for n in (0,600,1170,1620,2220): d.line((X(0)-50,Y(n),X(0)-30,Y(n)),fill='#25483d',width=3)
label(70, 642,'ОХВАТ\n2220*',25,b=True)

# D2 is a wall-opening edge, not a door swing.
d.line((X(0)-5,Y(2220),X(0)-5,Y(2390)),fill='#bf4f36',width=6)
d.line((X(0)-22,Y(2390),X(0)+110,Y(2390)),fill='#277d83',width=7)
label(X(0)+130,Y(2390)-18,'КРАЙ ПРОЁМА D2 ПО ПЛАНУ',23,'#277d83',True)
label(X(0)+130,Y(2390)+16,'170 мм* до края проёма',23,'#a43c29',True)
label(90, 1300,'* Величины — расчётная примерка. Дверная коробка, наличники, торцы и зазоры не учтены.',24,'#a43c29')
label(90, 1340,'Направление открывания D2 и размеры техники не подтверждены.',24,'#a43c29')

label(1280, 290, 'РАССТАНОВКА', 29, b=True)
for i,line in enumerate(['От входа к углу:', 'холодильник → ПММ → мойка', '', 'От угла по второй стене:', 'работа → варка → пенал', '', 'Глубина 600 мм — принято', 'для этой условной модели.', '', '2220 = 600 + 570 + 450 + 600', '2400 = 600 + 500 + 500 + 200 + 600']):
    label(1280,350+i*47,line,23)
im.save(P)
print(P, im.size)
