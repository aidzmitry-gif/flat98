from PIL import Image, ImageDraw, ImageFont, ImageOps
from pathlib import Path

base = Path(__file__).parent
sample_lvt = Path('C:/Users/aidzm/.codex/codex-remote-attachments/01a03940-90d5-7db2-8ba3-cbbfb2210fb8/E2206AEF-D5DF-4275-A080-21C8F67125AF/1-Фото-1.jpg')
sample_tile = Path('C:/Users/aidzm/.codex/codex-remote-attachments/01a03940-90d5-7db2-8ba3-cbbfb2210fb8/208A58B3-0E3A-4852-92A8-BB73AE0C546C/1-Фото-1.jpg')
out = base / 'room7_materials_agreed.png'
im = Image.new('RGB',(2200,1640),'#f6f3ed')
d=ImageDraw.Draw(im)
reg='C:/Windows/Fonts/arial.ttf'; bold='C:/Windows/Fonts/arialbd.ttf'
def text(x,y,s,n=24,b=False,c='#333d37'): d.text((x,y),s,font=ImageFont.truetype(bold if b else reg,n),fill=c)
def sample(path, crop, dest):
    a=Image.open(path).convert('RGB'); w,h=a.size
    a=a.crop((int(crop[0]*w),int(crop[1]*h),int(crop[2]*w),int(crop[3]*h)))
    a=ImageOps.fit(a,(dest[2],dest[3]),method=Image.Resampling.LANCZOS)
    im.paste(a,(dest[0],dest[1]))
text(65,30,'КОМНАТА 7  ·  СОГЛАСОВАННЫЕ МАТЕРИАЛЫ',40,True)
text(65,87,'Фотографии реальных образцов; цвет зависит от освещения и партии.',23,c='#687069')
sample(sample_lvt,(.07,.06,.92,.48),(65,145,980,315))
sample(sample_tile,(.10,.57,.85,.91),(1155,145,980,315))
text(65,480,'1  INVICTUS NATIVA DESERT ROSE 05',29,True)
text(65,522,'Клеевой кварцвинил Dryback · пол и сухие стены',23)
text(65,558,'Вертикальный монтаж — после письменного допуска.',22,c='#865337')
text(1155,480,'2  NT CERAMIC PATAGONIA CLASSIC',29,True)
text(1155,522,'Матовый керамогранит 600 × 1200 · зона ванны',23)
text(1155,558,'и нижняя лицевая часть ВМ-07 за унитазом.',23)
text(65,620,'КАК СОЧЕТАЕТСЯ В ИНТЕРЬЕРЕ',30,True)
render=Image.open(base/'room7-storage-patagonia-single-light.png').convert('RGB')
render.thumbnail((2070,850),Image.Resampling.LANCZOS)
im.paste(render,(65,675))
text(65,1534,'Бронза — сатинированная; тумба — светлый дуб. Рисунок плитки на визуализации условный.',22)
text(65,1570,'Доступ к люку ВМ-07 предусмотреть; место и открывание требуют проверки.',22,c='#865337')
im.save(out); print(out)
