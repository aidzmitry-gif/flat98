"""Draw a preliminary functional kitchen layout and non-positional lighting zones."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'output' / 'visualizations' / 'B01_план_кухни_и_света_v1.png'
W, H = 5710, 3500
# Coordinates in mm, origin at the lower left of earlier B01 plans.
MODULES = [
    ('1', (0, 1300, 600, 1900)),
    ('2', (0, 1900, 600, 2350)),
    ('3', (0, 2350, 600, 2900)),
    ('4', (0, 2900, 600, 3500)),
    ('5', (600, 2900, 1350, 3500)),
    ('6', (1350, 2900, 1800, 3500)),
    ('7', (1800, 2900, 2400, 3500)),
]
SOFA = (2485, 2300, 4455, 3500)
DESK = (4510, 2900, 5710, 3500)
TABLE = (2770, 1500, 4170, 2300)
MEDIA = (2070, 0, 4870, 450)
SHELF = (4870, 0, 5470, 300)
assert 600 + 450 + 550 == 1600
assert 600 + 750 + 450 + 600 == 2400
for _, (x1, y1, x2, y2) in MODULES:
    assert 0 <= x1 < x2 <= W and 0 <= y1 < y2 <= H
for i, (_, a) in enumerate(MODULES):
    for _, b in MODULES[i+1:]:
        assert not (max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3]))

img = Image.new('RGB', (2400, 1640), '#f6f4ef')
d = ImageDraw.Draw(img)
def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf', size)
d.text((65, 28), 'B01  |  план кухни и предварительная схема освещения', font=font(43, True), fill='#1d3336')
d.text((65, 91), 'КУХНЯ УСТАРЕЛА: получен новый эскиз владельца 03 · световые зоны предварительные', font=font(24, True), fill='#a22920')
scale = .171

def panel(x0, title, lighting=False):
    y0 = 275
    def pt(x, y): return (x0 + x*scale, y0 + (H-y)*scale)
    def box(r, fill, border='#526467', width=2):
        a, b = pt(r[0], r[3]), pt(r[2], r[1])
        d.rectangle((*a, *b), fill=fill, outline=border, width=width)
    def tag(r, text, fill='#25383a', size=21):
        d.text(pt((r[0]+r[2])/2, (r[1]+r[3])/2), text, font=font(size, True), anchor='mm', fill=fill)
    d.text((x0, 188), title, font=font(29, True), fill='#1d3336')
    box((0, 0, W, H), '#ffffff', '#263a3e', 5)
    for index, rect in MODULES:
        box(rect, '#e7dcd0' if index not in ('1','7') else '#cfbeb1')
        if not lighting: tag(rect, index, size=25)
    box(SOFA, '#ded5c8'); tag(SOFA, 'ДИВАН', size=18)
    box(DESK, '#d7e3df'); tag(DESK, 'РАБОТА', size=17)
    box(TABLE, '#c8d5bb'); tag(TABLE, 'СТОЛ*', size=19)
    box(MEDIA, '#cbbda7'); tag(MEDIA, 'ТУМБА / ЭКРАН', size=17)
    box(SHELF, '#bc9b79'); tag(SHELF, 'КНИГИ', size=14)
    for x, y1, y2 in [(0,200,1110),(W,600,2200)]:
        d.line((*pt(x,y1), *pt(x,y2)), fill='#198891', width=9)
    if lighting:
        # Labels are functional zones, intentionally not luminaire positions.
        zones = [(1100,2200,'A'),(3450,1650,'B'),(5050,2350,'C'),(3200,800,'D'),(1200,650,'E')]
        for x,y,letter in zones:
            px,py=pt(x,y); d.ellipse((px-22,py-22,px+22,py+22), fill='#e5b865', outline='#765723', width=2)
            d.text((px,py),letter,font=font(20,True),anchor='mm',fill='#3c3021')
    d.text((x0, 915), 'D2 вход слева   ·   O1 терраса справа   ·   база 5710 × 3500', font=font(19), fill='#546767')

panel(75, '1  МЕБЕЛЬ И ТЕХНИКА')
panel(1325, '2  СВЕТОВЫЕ ЗОНЫ', True)
d.text((70, 970), 'КУХНЯ · предварительная раскладка', font=font(27, True), fill='#1d3336')
rows = [
    '1  Холодильник — зона 600   |   2  ПММ — зона 450   |   3  Мойка / сервис — зона 550',
    '4  Общий угол 600 × 600   |   5  Подготовка — зона 750   |   6  Варка — зона 450',
    '7  Пенал духовка + СВЧ — зона 600. Угол, доборы, фасады и совместимость приборов не рассчитаны.',
    'Верх: 600 + 750 + 450 + 600 = 2400; боковая часть вне угла: 600 + 450 + 550 = 1600.',
]
for i,line in enumerate(rows): d.text((70, 1017+i*41), line, font=font(22), fill='#34464a')
d.text((70, 1200), 'СВЕТ · буквы обозначают зоны, а не координаты приборов', font=font(27, True), fill='#1d3336')
light = [
    'A  кухня: общий + рабочая подсветка   |   B  стол и гостиная: общий регулируемый свет',
    'C  работа: регулируемый локальный свет   |   D  кино: мягкий фон без засветки экрана',
    'E  ночная навигация: расположить после проверки маршрута с убранным столом и раскрытым диваном',
    'Физическое управление; сцены согласовать с SH-006. Точки, схемы линий и приборы определяются проектом.',
    '* Стол 1400 × 800 условный, ночью убирается. Проёмы, техника и фактические проходы требуют замеров.'
]
for i,line in enumerate(light): d.text((70, 1245+i*41), line, font=font(22), fill='#34464a')
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUTPUT)
print(f'OK: {OUTPUT}, 7 non-overlapping zones, both footprint chains verified')
