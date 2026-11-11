"""Create the B01 concept board from the owner's selected references."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
REFERENCES = ROOT / 'кухня гостинная' / 'Выбрано владельцем'
OUTPUT = ROOT / 'output' / 'visualizations' / 'B01_материалы_свет_концепция_v1.png'

def font(size, bold=False):
    name = 'arialbd.ttf' if bold else 'arial.ttf'
    return ImageFont.truetype(f'C:/Windows/Fonts/{name}', size)

canvas = Image.new('RGB', (2200, 1610), '#f3f0ea')
draw = ImageDraw.Draw(canvas)
draw.text((70, 36), 'B01  |  кухня, материалы и свет', font=font(49, True), fill='#263630')
draw.text((70, 100), 'Концепция по выбранным визуализациям  ·  цвета требуют проверки по образцам', font=font(25), fill='#785e4d')
for name, x in [('01_кухня_диван_рабочее_место.png', 70), ('02_компактная_медиастена.png', 1140)]:
    with Image.open(REFERENCES / name) as source:
        preview = ImageOps.contain(source.convert('RGB'), (990, 560))
    canvas.paste(preview, (x + (990-preview.width)//2, 160))
draw.text((70, 760), 'ПАЛИТРА ДЛЯ ПОДБОРА ОБРАЗЦОВ', font=font(29, True), fill='#263630')
swatches = [
    ('M01', 'Фасады', 'тёплый белый', '#e6ded0'),
    ('M02', 'Стены', 'тёплый greige', '#bbae9e'),
    ('M03', 'Столешница', 'светлый камень', '#ded8ca'),
    ('M04', 'Пол', 'светлый тёплый', '#cabda9'),
    ('M05', 'Стеллаж', 'тёплое дерево', '#9a7757'),
    ('M06', 'Текстиль', 'терракота / олива', '#a75937'),
    ('M07', 'Акцент', 'тёплый металл', '#ad8a50'),
]
for i, (code, label, detail, color) in enumerate(swatches):
    x = 70 + i*300
    draw.rounded_rectangle((x, 815, x+270, 925), radius=8, fill=color, outline='#d0c9bd', width=2)
    draw.text((x, 938), f'{code}  {label}', font=font(23, True), fill='#263630')
    draw.text((x, 968), detail, font=font(19), fill='#625e57')
draw.text((70, 1040), 'СЦЕНАРИИ СВЕТА', font=font(29, True), fill='#263630')
scenes = [
    ('ГОТОВКА', 'общий + подсветка\nрабочей поверхности'),
    ('ОБЕД', 'общий свет для стола\nи зоны дивана'),
    ('РАБОТА', 'регулируемый локальный\nсвет у рабочего места'),
    ('КИНО', 'мягкий фон без\nзасветки экрана'),
    ('НОЧЬ', 'ориентирующий свет\nпосле уборки стола'),
]
for i, (title, detail) in enumerate(scenes):
    x=70+i*425
    draw.rounded_rectangle((x, 1090, x+397, 1260), radius=12, fill='#fffdf9', outline='#d7d0c6', width=2)
    draw.text((x+22, 1110), title, font=font(23, True), fill='#856243')
    draw.multiline_text((x+22, 1150), detail, font=font(21), fill='#394841', spacing=9)
draw.text((70, 1320), 'Материалы, приборы и места светильников уточняются по образцам, обмерам и проекту.', font=font(24), fill='#725b4c')
draw.text((70, 1360), 'Стол убирается на ночь. Показанные изображения — выбранные владельцем виды.', font=font(24), fill='#725b4c')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
canvas.save(OUTPUT)
print(f'OK {OUTPUT}')
