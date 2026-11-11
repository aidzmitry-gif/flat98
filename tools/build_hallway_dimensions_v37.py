"""Dimensioned APT-001 hallway presentation from the current illustrated view.

The source PNG is embedded unchanged in an SVG alongside a separate scaled
elevation. Measurements remain B01 / proposed / unknown as labelled.
"""
from __future__ import annotations

import base64
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "Прихожая"
PHOTO = FOLDER / "65_прихожая_C_кухня_открытый_шкаф_v36.png"
SVG = FOLDER / "67_прихожая_C_вид_и_размеры_v37.svg"

assert 25 + 850 + 775 + 25 == 1675
assert 400 + 396 + 3 * 18 == 850
assert 460 - 35 - 25 == 400
assert 400 - 90 == 310
assert 2700 - 18 - 2150 == 532
assert 610 + 1010 + 470 == 2090

encoded = base64.b64encode(PHOTO.read_bytes()).decode("ascii")
parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1650" viewBox="0 0 2400 1650">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M8 0 L0 4 L8 8" fill="none" stroke="#607b72" stroke-width="1.2"/></marker>
<clipPath id="photo"><rect x="70" y="230" width="1150" height="1006" rx="12"/></clipPath></defs>
<style>
text {{ font-family: Arial, 'Segoe UI', sans-serif; fill:#213d39 }}
.eyebrow {{font-size:18px; font-weight:bold; letter-spacing:2px; fill:#367363}}
.title {{font-size:46px; font-weight:bold}}
.subtitle {{font-size:22px; fill:#657d76}}
.section {{font-size:25px; font-weight:bold}}
.body {{font-size:21px; fill:#415b54}}
.small {{font-size:18px; fill:#667b73}}
.dimtext {{font-size:18px; font-weight:bold; fill:#31594d}}
.interior {{font-size:16px; font-weight:bold; fill:#38584c}}
.dim {{stroke:#607b72; stroke-width:1.7; marker-start:url(#a); marker-end:url(#a)}}
.ext {{stroke:#9aaca3; stroke-width:1.4}}
.badge {{font-size:19px; font-weight:bold; fill:white}}
.card {{fill:#fff; stroke:#dbe4dc; stroke-width:2}}
</style>
<rect width="2400" height="1650" fill="#f1f4ef"/>
<text x="60" y="50" class="eyebrow">APT-001 / ПРИХОЖАЯ / ВАРИАНТ C · V37</text>
<text x="60" y="107" class="title">Открытый шкаф и банкетка: размеры</text>
<text x="62" y="149" class="subtitle">Реалистичный вид из кухни и отдельная развёртка наполнения · все размеры в миллиметрах</text>
<rect x="46" y="185" width="1196" height="1069" rx="20" class="card"/>
<text x="70" y="216" class="section">01  Вид из кухни</text>
<image x="70" y="230" width="1150" height="1006" preserveAspectRatio="xMidYMid meet" clip-path="url(#photo)" href="data:image/png;base64,{encoded}"/>
<rect x="1258" y="185" width="1096" height="1069" rx="20" class="card"/>
<text x="1285" y="221" class="section">02  Развёртка: дверцы условно сняты</text>
<text x="1286" y="256" class="small">Вид от коридора к входной двери D1; показано внутреннее наполнение</text>
''']


def add(s: str):
    parts.append(s + "\n")


def rect(x, y, w, h, fill, stroke="none", sw=1, extra=""):
    add(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')


def line(x1, y1, x2, y2, cls="", extra=""):
    add(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="{cls}" {extra}/>')


def txt(x, y, value, cls="body", anchor="start", extra=""):
    add(f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}" {extra}>{escape(value)}</text>')


def badge(x, y, n):
    add(f'<circle cx="{x}" cy="{y}" r="17" fill="#397665"/><text x="{x}" y="{y+6}" text-anchor="middle" class="badge">{n}</text>')


s = .265
x0, floor = 1320.0, 1080.0
cab = x0 + 25 * s
cab_w, niche_w = 850 * s, 775 * s
niche = cab + cab_w
top = floor - 2700 * s
full_end = x0 + 1675 * s
board = 18 * s
service = cab + board
service_w = 400 * s
clothes = service + service_w + board
clothes_w = 396 * s
upper = floor - 2150 * s
rail = floor - 1750 * s
lower = floor - 380 * s
seat = floor - 460 * s
drawer_top = floor - 400 * s
drawer_bottom = floor - 310 * s

# Dimension chains apply to the elevation, never to the perspective photo.
line(x0, top-16, x0, top-42, "ext")
line(full_end, top-16, full_end, top-42, "ext")
line(x0, top-32, full_end, top-32, "dim")
txt((x0+full_end)/2, top-42, "1675 B", "dimtext", "middle")
line(cab-19, top, cab-39, top, "ext")
line(cab-19, floor, cab-39, floor, "ext")
line(cab-29, top, cab-29, floor, "dim")
txt(cab-41, (top+floor)/2, "2700 P", "dimtext", "middle", f'transform="rotate(-90 {cab-41:.2f} {(top+floor)/2:.2f})"')

# 850 cabinet (two clear widths, three 18 mm components).
rect(cab, top, cab_w, 2700*s, "#dfc8aa", "#947c65", 2)
rect(service, top+board, service_w, (2700-36)*s, "#ecf3ef", "#b9c9be", 1)
rect(service+service_w, top, board, 2700*s, "#c3a586")
rect(clothes, top+board, clothes_w, (2700-36)*s, "#faf5ed", "#d0c5b7", 1)
rect(cab, floor-80*s, cab_w, 80*s, "#c3a586")
rect(clothes, upper, clothes_w, board, "#bc9d7c")
rect(clothes, lower, clothes_w, board, "#bc9d7c")
line(clothes+8, rail, clothes+clothes_w-8, rail, "", 'stroke="#4c6055" stroke-width="3"')

# Simplified clothes and a panel marker. Marker dimensions are deliberately not to scale.
for i, color in enumerate(("#afa995", "#8c9585", "#bda88d")):
    x = clothes + 13 + i*28
    y = rail + 20
    add(f'<path d="M{x:.2f} {y:.2f} l-9 12 v205 h23 v-205 l-9 -12 Z" fill="{color}" stroke="#877f70" stroke-width="1"/>')
    add(f'<path d="M{x-5:.2f} {y:.2f} l8 -9 l8 9" fill="none" stroke="#5a655b" stroke-width="1.5"/>')
rect(service+17, floor-1700*s, service_w-34, 600*s, "none", "#7da595", 2, 'stroke-dasharray="5 4"')
txt(service+service_w/2, floor-1400*s, "ЭЩ-03", "interior", "middle")
txt(service+service_w/2, floor-1300*s, "размер M", "small", "middle")
txt(service+service_w/2, top+36, "400 P", "interior", "middle")
txt(clothes+clothes_w/2, top+36, "396 P", "interior", "middle")

# 775 bench niche, upper cabinet, cushion and one dry slippers drawer.
rect(niche, top, niche_w, upper-top, "#dfc8aa", "#947c65", 2)
line(niche+niche_w/2, top, niche+niche_w/2, upper, "", 'stroke="#ad9273" stroke-width="1.5"')
rect(niche, upper, niche_w, seat-upper, "#dcebdd", "#b4c8b6", 1)
for i in range(3):
    x = niche + 43 + i*60
    y = floor - 1500*s
    add(f'<path d="M{x:.2f} {y:.2f} v16 q0 6 6 6" fill="none" stroke="#678270" stroke-width="3"/>')
rect(niche, seat, niche_w, 35*s, "#e7d4ba", "#ae987d", 1, 'rx="3"')
rect(niche, seat+35*s, niche_w, 25*s, "#bd9c78")
rect(niche, drawer_top, 370*s, drawer_bottom-drawer_top, "#d5b997", "#ae9274", 1)
line(niche+70, drawer_top+11, niche+86, drawer_top+11, "", 'stroke="#8a735d" stroke-width="1.5"')
for j, height in enumerate((110, 110, 285)):
    x = niche + 26 + j*60
    y = floor - height*s
    add(f'<path d="M{x:.2f} {y:.2f} h16 v{height*s-8:.2f} h9 q5 1 7 8 h-32 Z" fill="#8c7b67"/>')
line(cab, floor, niche+niche_w+8, floor, "", 'stroke="#587367" stroke-width="2"')
line(cab, floor+12, cab, floor+40, "ext")
line(niche, floor+12, niche, floor+40, "ext")
line(niche+niche_w, floor+12, niche+niche_w, floor+40, "ext")
line(cab, floor+31, niche, floor+31, "dim")
line(niche, floor+31, niche+niche_w, floor+31, "dim")
txt((cab+niche)/2, floor+57, "850 P", "dimtext", "middle")
txt(niche+niche_w/2, floor+57, "775 P", "dimtext", "middle")
txt(cab, floor+89, "25 + 850 + 775 + 25 = 1675", "small")

# Room-for-room notes: all numeric dimensions are project proposals P.
badge(1832, 346, "1")
txt(1860, 354, "Шкаф", "section")
txt(1860, 388, "850 × 580 × 2700 мм P", "body")
txt(1860, 420, "400 мм — свет отделения щита", "body")
txt(1860, 450, "396 мм — свет отделения курток", "body")
line(1810, 479, 2318, 479, "", 'stroke="#e0e7e0" stroke-width="2"')
badge(1832, 516, "2")
txt(1860, 524, "Штанга и полки", "section")
txt(1860, 558, "Штанга: h = 1750 мм P", "body")
txt(1860, 590, "Верх полки: h = 2150 мм P", "body")
txt(1860, 622, "Нижняя съёмная: h = 380 мм P", "body")
line(1810, 650, 2318, 650, "", 'stroke="#e0e7e0" stroke-width="2"')
badge(1832, 687, "3")
txt(1860, 695, "Банкетка у входа", "section")
txt(1860, 729, "775 × 420 мм P", "body")
txt(1860, 761, "Высота сиденья: 460 мм P", "body")
txt(1860, 793, "Просвет снизу: 310 / 400 мм P", "body")
line(1810, 821, 2318, 821, "", 'stroke="#e0e7e0" stroke-width="2"')
badge(1832, 858, "4")
txt(1860, 866, "Тапочки и обувь", "section")
txt(1860, 900, "Сухой ящик ≈370 × 380 × 90 P", "body")
txt(1860, 932, "Размер ящика внешний.", "small")
txt(1860, 965, "Уличная обувь — один ряд на полу.", "body")
line(1810, 994, 2318, 994, "", 'stroke="#e0e7e0" stroke-width="2"')
txt(1810, 1033, "Щит показан условно: размер M.", "body")
txt(1810, 1064, "Дверцы шкафа сняты на развёртке.", "small")
txt(1810, 1096, "Фурнитура и открывание — проверить.", "small")
txt(1810, 1128, "Толщина деталей принята 18 мм P.", "small")

# Source statuses and an explicit warning about the unknown electrical box.
add('<rect x="46" y="1278" width="2308" height="320" rx="20" fill="#fff9ef" stroke="#ead2a8" stroke-width="2"/>')
txt(72, 1320, "Что подтверждено и что нужно измерить", "section")
txt(72, 1359, "Стена: 1675 мм B01. Высота потолка в отмеченных точках: 2750 мм. Размеры мебели — эскиз P.", "body")
txt(72, 1395, "D1 по БТИ: 610 + 1010 + 470 = 2090 мм. Отдельный контроль проёма: 1140 × 2150 мм; привязка к углам не установлена.", "body")
txt(72, 1431, "400 мм — ширина предложенного отделения, а не размер электрощита. Его габариты и возможность переноса нужно проверить с электриком.", "body")
txt(72, 1467, "До изготовления проверить реальные проёмы, петли, доступ к щиту, розетки и монтажные зазоры. Ящик и мебельные размеры — наружные, если не указано иначе.", "body")
txt(72, 1520, "B — план БТИ · P — предварительное предложение · M — замерить. Фото иллюстративное; размеры приведены на развёртке.", "small")
txt(72, 1553, "Высоты полок и штанги даны от пола. Высоту, конструкцию и распределение секций уточнить после чистового обмера.", "small")
add('</svg>')

svg = "".join(parts)
ET.fromstring(svg)
SVG.write_text(svg, encoding="utf-8")
print("Saved SVG:", SVG, "bytes:", SVG.stat().st_size)
