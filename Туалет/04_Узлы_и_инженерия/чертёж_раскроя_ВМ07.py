from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BG, INK, MUTED = '#f5f3ed', '#222e2b', '#56635e'
GRAY, TILE, LINE, BRONZE = '#c5c7c0', '#e3d4bd', '#646e67', '#826139'
GREEN, RED = '#306955', '#97583a'
image = Image.new('RGB', (2180, 1400), BG)
draw = ImageDraw.Draw(image)
fonts = Path('C:/Windows/Fonts')


def text(x, y, content, size=28, color=INK, bold=False):
    font = ImageFont.truetype(str(fonts / ('arialbd.ttf' if bold else 'arial.ttf')), size)
    draw.text((x, y), content, fill=color, font=font)


def box(bounds, fill, outline=LINE, width=3):
    draw.rectangle(bounds, fill, outline, width)


def line(points, fill=LINE, width=3):
    draw.line(points, fill, width)


def dim(x1, x2, y, label, label_y):
    line((x1, y, x2, y), GREEN)
    for x in (x1, x2):
        line((x - 5, y + 7, x + 5, y - 7), GREEN)
    text(x1 + 5, label_y, label, 24, GREEN, True)


text(65, 42, 'ВМ-07  /  ДВЕ СТВОРКИ И РАСКРОЙ ОТДЕЛКИ', 49, bold=True)
text(65, 111, 'Комната № 7  ·  710 × 360 мм по B01  ·  высота проёма и положение счётчиков требуют обмера', 28, MUTED)
line((65, 169, 2115, 169))
text(65, 215, 'ФАСАД', 32, bold=True)
text(780, 215, 'РАЗРЕЗ СБОКУ', 32, bold=True)
text(1450, 215, 'РАСКРОЙ PATAGONIA', 32, bold=True)

# Front view showing the lower edge of the hatch at the finish junction.
box((115, 335, 530, 916), GRAY)
box((115, 615, 530, 916), TILE)
fold = (136, 418, 509, 615)
box(fold, '#b7bab3', GREEN, 4)
line((322, 418, 322, 615), GREEN, 4)
text(160, 454, 'левая', 25)
text(365, 454, 'правая', 25)
text(151, 345, 'Декор Desert Rose 05', 24, bold=True)
text(154, 536, 'Один стык створок', 26, GREEN, True)
line((115, 770, 530, 770), BRONZE)
box((256, 656, 401, 702), BRONZE, BRONZE)
text(136, 716, 'Patagonia Classic', 24, bold=True)
draw.rounded_rectangle((216, 797, 433, 890), radius=28, fill='#fbfaf6', outline=LINE, width=3)
text(293, 823, 'WC', 25, bold=True)
dim(115, 530, 310, '710 мм · короб', 275)
text(66, 953, 'Низ створок можно совместить', 27)
text(66, 990, 'со стыком материалов.', 27)
text(66, 1035, 'Положение проёма условное.', 25, RED, True)

# Section, with a continuous frame behind the hinge and representative WC.
box((820, 338, 1028, 916), '#deded4')
box((1020, 338, 1036, 615), GRAY)
box((1020, 615, 1036, 916), TILE)
box((864, 425, 1036, 615), '#eaf0e8', GREEN)
line((1036, 426, 1036, 615), GREEN, 6)
text(874, 465, 'ЗОНА', 22, GREEN, True)
text(872, 496, 'РЕВИЗИИ', 22, GREEN, True)
text(1065, 446, 'Доступ рукой', 25, bold=True)
text(1065, 479, 'и инструментом', 25, bold=True)
line((1075, 534, 1000, 534), GREEN, 4)
draw.polygon([(1000, 534), (1015, 525), (1015, 543)], fill=GREEN)
draw.rounded_rectangle((1037, 747, 1270, 829), radius=25, fill='#fbfaf6', outline=LINE, width=3)
text(1060, 846, 'Унитаз на месте', 25)
dim(820, 1036, 309, '360 мм · короб', 274)
text(780, 953, 'Полезный проём меньше рамы.', 27)
text(780, 990, 'Учитывать бачок, трубы и петли.', 27)
text(780, 1035, 'Высоты показаны условно.', 25, RED, True)

# One horizontal course blank and its reusable offcut shown to scale in width.
start, cut, end = 1450, 1817, 2070
box((start, 369, cut, 678), TILE)
box((cut, 369, end, 678), '#e9e9db')
line((cut, 369, cut, 678), BRONZE, 5)
dim(start, end, 332, '1200 мм · номинал плитки', 291)
text(1477, 451, 'Деталь ряда', 28, bold=True)
text(1477, 496, '≈710 мм', 29, BRONZE, True)
text(1855, 451, 'Остаток', 28, bold=True)
text(1855, 496, '≈490 мм*', 29, GREEN, True)
text(1450, 702, 'Высота заготовки 600 мм', 25)
text(1450, 752, 'При высоте облицовки в два ряда', 26)
text(1450, 787, 'суммарно более 600 мм нужны 2 плитки.', 26)
text(1450, 840, 'Остатки можно учесть в душевой', 26)
text(1450, 875, 'после раскладки плитки по стенам.', 26)
text(1450, 942, '* До учёта швов и ширины реза.', 24, MUTED)
text(1450, 979, 'Формат сверить по партии.', 24, MUTED)

line((65, 1108, 2115, 1108))
text(65, 1140, 'КРИТЕРИЙ ПРИЁМКИ', 31, bold=True)
text(65, 1192, 'При установленном унитазе обе створки открываются полностью, а съём счётчика и работа ключом проходят свободно.', 27)
text(65, 1238, 'Проверить доступ ко всем кранам и соединениям, габарит самого большого снимаемого узла и проход инструмента.', 27)
text(65, 1294, 'Схема для примерки. Размер рамки, зазоры и крепление облицовки зависят от фактического проёма и выбранных петель.', 24, MUTED)

image.save(Path(__file__).with_name('ВМ-07 — фасад, разрез и раскрой.png'))
