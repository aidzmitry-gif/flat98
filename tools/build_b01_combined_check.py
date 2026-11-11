"""Preliminary B01 coordination diagram using documented model dimensions."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output' / 'visualizations' / 'B01_совмещенный_план_проверка_v1.png'
W, H = 5710, 3500
KITCHEN = [(0, 2900, 2400, 3500), (0, 1300, 600, 2900)]
SOFA = (2485, 2300, 4455, 3500)
SOFA_OPEN = (2485, 1270, 4455, 3500)
DESK = (4510, 2900, 5710, 3500)
MEDIA = (2070, 0, 4870, 450)
SHELF = (4870, 0, 5470, 300)
TABLE = (2770, 1500, 4170, 2300)
CHAIRS = [(2880, 1100, 3280, 1500), (3600, 1100, 4000, 1500)]
PULLED = [(2880, 800, 3280, 1200), (3600, 800, 4000, 1200)]

def intersection(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    return (x1, y1, x2, y2) if x1 < x2 and y1 < y2 else None

assert intersection(TABLE, SOFA_OPEN) == (2770, 1500, 4170, 2300)
assert not intersection(TABLE, SOFA)
assert CHAIRS[0][1] - MEDIA[3] == 650
assert PULLED[0][1] - MEDIA[3] == 350
assert SOFA_OPEN[1] - MEDIA[3] == 820
assert SOFA_OPEN[1] - 562 == 708
assert all(0 <= r[0] < r[2] <= W and 0 <= r[1] < r[3] <= H
           for r in [*KITCHEN, SOFA, SOFA_OPEN, DESK, MEDIA, SHELF, TABLE, *CHAIRS, *PULLED])

image = Image.new('RGB', (2400, 1580), '#f5f3ee')
draw = ImageDraw.Draw(image)
font_path = 'C:/Windows/Fonts/arial.ttf'
bold_path = 'C:/Windows/Fonts/arialbd.ttf'
def font(size, bold=False):
    return ImageFont.truetype(bold_path if bold else font_path, size)
draw.text((75, 36), 'B01  |  кухня-гостиная + компактная медиастена', font=font(44, True), fill='#172c35')
draw.text((75, 96), 'Предварительная проверка · все размеры в мм · не для заказа и монтажа', font=font(25), fill='#a04836')

scale = 0.172
def panel(x0, title, night=False):
    y0 = 290
    def point(x, y):
        return (x0 + x * scale, y0 + (H-y)*scale)
    def rect(r, fill, outline='#41525a', width=2):
        a, b = point(r[0], r[3]), point(r[2], r[1])
        draw.rectangle((*a, *b), fill=fill, outline=outline, width=width)
    def label(r, text, size=19, color='#1c3038'):
        x=(r[0]+r[2])/2; y=(r[1]+r[3])/2
        draw.multiline_text(point(x,y), text, font=font(size, True), fill=color, anchor='mm', align='center', spacing=3)
    draw.text((x0, 188), title, font=font(28, True), fill='#172c35')
    rect((0,0,W,H), '#ffffff', '#28373e', 5)
    for part in KITCHEN: rect(part, '#e9ddd0')
    label(KITCHEN[0], 'КУХНЯ 2400 × 600', 19)
    label(KITCHEN[1], 'ВЕТВЬ\n1600 × 600', 17)
    rect(DESK, '#cadde1'); label(DESK, 'РАБОЧЕЕ\nМЕСТО', 17)
    rect(MEDIA, '#c9baa0'); label(MEDIA, 'ТУМБА 2800 × 450', 18)
    rect(SHELF, '#c6a37f'); label(SHELF, 'СТЕЛЛАЖ', 12)
    if night:
        rect(SOFA_OPEN, '#e9b9ad', '#a52c26', 4)
        draw.multiline_text(point(3470, 3200), 'ДИВАН-КРОВАТЬ\n1970 × 2230', font=font(20, True), fill='#1c3038', anchor='mm', align='center')
        rect(TABLE, '#be4a3f', '#8e211d', 3)
        label(TABLE, 'КОЛЛИЗИЯ СО СТОЛОМ\n1400 × 800', 18, '#ffffff')
    else:
        rect(SOFA, '#d5cdbf'); label(SOFA, 'ДИВАН 1970 × 1200', 19)
        rect(TABLE, '#b6cda7'); label(TABLE, 'СТОЛ 1400 × 800*', 19)
        for chair, pulled in zip(CHAIRS, PULLED):
            rect(pulled, '#f3c9bc', '#b3523b', 2)
            rect(chair, '#d49269', '#6d4835', 2)
            label(chair, 'СТУЛ*', 14)
    # Openings are shown as measured wall segments; swing is unknown.
    a,b=point(0,200),point(0,1110)
    draw.line((*a,*b), fill='#168691', width=10)
    a,b=point(W,600),point(W,2200)
    draw.line((*a,*b), fill='#168691', width=10)
    draw.text((x0, 930), 'D2 вход слева  ·  O1 терраса справа  ·  открывания уточнить', font=font(19), fill='#32535a')
    draw.text((x0, 962), '5710 × 3500 — расчётная база; контроль ширины 5705 / 5710', font=font(19), fill='#32535a')

panel(100, '1  ДЕНЬ · два стула и диван', False)
panel(1320, '2  НОЧЬ · раскрытие дивана', True)
draw.text((85, 1055), 'РЕЗУЛЬТАТ ПРОВЕРКИ', font=font(29, True), fill='#172c35')
lines = [
    '• Стол 1400 × 800 и стулья 400 × 400 — условные. Два места на диване требуют проверки посадки.',
    '• До тумбы от передней кромки стульев: 650 мм в показанном положении; 350 мм после сдвига на 300 мм.',
    '• Ночью стол убирается. Тумба — раскрытый диван: 820 мм; до условного выступа проектора — 708 мм.',
    '• Стол примыкает к дивану: посадка, ноги, трансформация стола и его перемещение пока не подтверждены.',
    '• Полная ветвь кухни сохранена; раскрытия ПММ, двери, проход D2–O1 и кресло требуют натурной проверки.',
    '* Стол и стулья выбраны для проверки геометрии, модели не утверждены. Положение и размеры сверить на месте.'
]
for i, line in enumerate(lines):
    draw.text((85, 1112 + i*55), line, font=font(24), fill='#34444a')
OUT.parent.mkdir(parents=True, exist_ok=True)
image.save(OUT)
print(f'OK {OUT} | collision 1400x800 | chair gaps 650/350 | sofa gaps 820/708')
