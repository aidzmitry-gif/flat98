"""Two reproducible dimension sheets for the APT-001 hallway sketch.

The photo is embedded unchanged; all measurement arrows are on separate, scaled
vector drawings. B01, proposed dimensions, and unknowns are never conflated.
"""
from __future__ import annotations

import base64
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "Прихожая"
PHOTO = OUT / "65_прихожая_C_кухня_открытый_шкаф_v36.png"
PHOTO64 = base64.b64encode(PHOTO.read_bytes()).decode("ascii")
PAGE_A = OUT / "69_прихожая_высота_ширина_глубина_v38.svg"
PAGE_B = OUT / "70_прихожая_размеры_внутри_v38.svg"

assert 25 + 850 + 775 + 25 == 1675
assert 400 + 396 + 3 * 18 == 850
assert 2700 - 18 - 2150 == 532
assert 1750 - 380 == 1370
assert 460 - 35 - 25 == 400 and 400 - 90 == 310
assert 610 + 1010 + 470 == 2090


class Sheet:
    def __init__(self, width=2600, height=1700):
        self.parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M8 0 L0 4 L8 8" fill="none" stroke="#5a786e" stroke-width="1.2"/></marker></defs>
<style>text{{font-family:Arial,'Segoe UI',sans-serif;fill:#213d39}} .eyebrow{{font-size:19px;font-weight:bold;letter-spacing:2px;fill:#387462}} .title{{font-size:47px;font-weight:bold}} .subtitle{{font-size:23px;fill:#657d76}} .head{{font-size:26px;font-weight:bold}} .body{{font-size:21px;fill:#3e5850}} .small{{font-size:18px;fill:#61796f}} .micro{{font-size:16px;fill:#627970}} .dimtxt{{font-size:20px;font-weight:bold;fill:#2f594b}} .dim{{stroke:#5a786e;stroke-width:1.8;marker-start:url(#a);marker-end:url(#a)}} .ext{{stroke:#a0b0a7;stroke-width:1.4}}</style>
<rect width="{width}" height="{height}" fill="#f1f4ef"/>''']

    def raw(self, a): self.parts.append(a + "\n")
    def text(self,x,y,t,cls="body",anchor="start",extra=""):
        self.raw(f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}" {extra}>{escape(t)}</text>')
    def rect(self,x,y,w,h,fill,stroke="none",sw=1,extra=""):
        self.raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
    def line(self,x1,y1,x2,y2,cls="",extra=""):
        self.raw(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="{cls}" {extra}/>')
    def card(self,x,y,w,h,fill="white"):
        self.rect(x,y,w,h,fill,"#dbe4dc",2,'rx="20"')
    def dim_h(self,x1,x2,y,label,above=True):
        self.line(x1,y,x2,y,"dim")
        self.text((x1+x2)/2, y-10 if above else y+25,label,"dimtxt","middle")
    def dim_v(self,x,y1,y2,label):
        self.line(x,y1,x,y2,"dim")
        self.text(x-9,(y1+y2)/2,label,"dimtxt","middle",f'transform="rotate(-90 {x-9:.2f} {(y1+y2)/2:.2f})"')
    def save(self,path):
        data="".join(self.parts)+"</svg>"
        ET.fromstring(data)
        path.write_text(data,encoding="utf-8")
        print("Saved:",path,"bytes:",path.stat().st_size)


def heading(sh,number,title,sub):
    sh.text(55,47,f"APT-001 / ПРИХОЖАЯ / ВАРИАНТ C · V38 / ЛИСТ {number}","eyebrow")
    sh.text(55,106,title,"title")
    sh.text(57,150,sub,"subtitle")


def elevation(sh,x0,floor,s,internal=True):
    """Front elevation; dimensions are placed by the calling sheet."""
    cab=x0+25*s
    cw=850*s
    niche=cab+cw
    nw=775*s
    board=18*s
    top=floor-2700*s
    service=cab+board
    service_w=400*s
    clothes=service+service_w+board
    clothes_w=396*s
    upper=floor-2150*s
    rail=floor-1750*s
    lower=floor-380*s
    seat=floor-460*s
    drawer_top=floor-400*s
    drawer_bottom=floor-310*s
    sh.rect(cab,top,cw,2700*s,"#dbc2a2","#927a62",2)
    sh.rect(service,top+board,service_w,(2700-36)*s,"#eaf2ec","#bdcec0",1)
    sh.rect(service+service_w,top,board,2700*s,"#c1a17e")
    sh.rect(clothes,top+board,clothes_w,(2700-36)*s,"#f9f4ed","#d0c5b8",1)
    sh.rect(cab,floor-80*s,cw,80*s,"#c1a17e")
    sh.rect(clothes,upper,clothes_w,board,"#b99c7c")
    sh.rect(clothes,lower,clothes_w,board,"#b99c7c")
    sh.line(clothes+8,rail,clothes+clothes_w-8,rail,extra='stroke="#485d51" stroke-width="3"')
    if internal:
        sh.rect(service+service_w*.17,floor-1690*s,service_w*.66,590*s,"none","#82a596",2,'stroke-dasharray="6 5"')
        sh.text(service+service_w/2,floor-1410*s,"ЭЩ-03","small","middle")
        sh.text(service+service_w/2,floor-1315*s,"размер M","micro","middle")
        for i,color in enumerate(("#aaa994","#899683","#bba58a")):
            xx=clothes+12+i*(clothes_w-25)/3
            ww=(clothes_w-35)/3
            yy=rail+18
            height=820*s
            sh.raw(f'<path d="M{xx:.2f} {yy:.2f} l-5 12 v{height:.2f} h{ww:.2f} v{-height:.2f} l-5 -12 Z" fill="{color}" stroke="#887e6d" stroke-width="1"/>')
            sh.raw(f'<path d="M{xx-3:.2f} {yy:.2f} l8 -8 l8 8" fill="none" stroke="#5f695c" stroke-width="2"/>')
    sh.rect(niche,top,nw,upper-top,"#dbc2a2","#927a62",2)
    sh.line(niche+nw/2,top,niche+nw/2,upper,extra='stroke="#ad9273" stroke-width="1.4"')
    sh.rect(niche,upper,nw,seat-upper,"#dcebdd","#b5caba",1)
    for k in range(3):
        xx=niche+nw*(.25+.25*k); yy=floor-1500*s
        sh.raw(f'<path d="M{xx:.2f} {yy:.2f} v15 q0 6 6 6" fill="none" stroke="#678371" stroke-width="3"/>')
    sh.rect(niche,seat,nw,35*s,"#e8d6be","#ae987d",1,'rx="3"')
    sh.rect(niche,seat+35*s,nw,25*s,"#be9d79")
    sh.rect(niche,drawer_top,370*s,drawer_bottom-drawer_top,"#d6b996","#ae9274",1)
    for k,h in enumerate((110,110,285)):
        xx=niche+nw*(.12+.28*k); y=floor-h*s
        sh.raw(f'<path d="M{xx:.2f} {y:.2f} h14 v{h*s-7:.2f} h8 q5 1 7 7 h-29 Z" fill="#8d7b67"/>')
    sh.line(cab,floor,niche+nw+3,floor,extra='stroke="#587367" stroke-width="2"')
    return {"x0":x0,"cab":cab,"niche":niche,"end":niche+nw,"fullend":x0+1675*s,"top":top,"floor":floor,
            "service":service,"service_w":service_w,"clothes":clothes,"clothes_w":clothes_w,
            "upper":upper,"rail":rail,"lower":lower,"seat":seat,"drawer_top":drawer_top,"drawer_bottom":drawer_bottom,"s":s}


def page_a():
    sh=Sheet()
    heading(sh,"1","Прихожая: высота, ширина и глубина","Реалистичный вид из кухни и основные размеры мебели · B — БТИ, P — эскиз, M — замерить")
    sh.card(45,185,1048,1062)
    sh.text(70,222,"01  Вид из кухни", "head")
    sh.raw(f'<image x="70" y="240" width="998" height="873" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{PHOTO64}"/>')
    sh.text(72,1160,"Фото — визуализация. Размеры читаются по схемам.","small")
    sh.text(72,1194,"Слева остаётся открытый переход в коридор.","small")
    sh.card(1110,185,820,1062)
    sh.text(1135,222,"02  Вид на мебель спереди", "head")
    sh.text(1137,1230,"Дверцы условно сняты; все размеры в мм", "small")
    v=elevation(sh,1220,1100,.30)
    sh.line(v['x0'],v['top']-7,v['x0'],v['top']-37,"ext")
    sh.line(v['fullend'],v['top']-7,v['fullend'],v['top']-37,"ext")
    sh.dim_h(v['x0'],v['fullend'],v['top']-29,"1675 B")
    sh.dim_v(v['cab']-43,v['top'],v['floor'],"2700 P")
    sh.dim_v(v['end']+38,v['seat'],v['floor'],"460 P")
    sh.dim_h(v['cab'],v['niche'],v['floor']+34,"850 P",False)
    sh.dim_h(v['niche'],v['end'],v['floor']+34,"775 P",False)
    sh.text(1220,1204,"25 + 850 + 775 + 25 = 1675", "small")

    sh.card(1947,185,608,1062)
    sh.text(1972,222,"03  План сверху", "head")
    sh.text(1974,255,"Глубины от левой стены", "small")
    x,y,k=2010.0,343.0,.41
    # The opening to corridor remains open at the bottom of the plan.
    sh.line(x,y,x,y+1675*k,extra='stroke="#334c42" stroke-width="7"')
    sh.rect(x,y+25*k,420*k,775*k,"#dbeadd","#8ca894",2)
    sh.rect(x,y+800*k,580*k,850*k,"#ddc3a0","#a68a6b",2)
    sh.text(x+84*k,y+240*k,"БАНКЕТКА","small")
    sh.text(x+100*k,y+1050*k,"ШКАФ","small")
    sh.dim_h(x+5,x+420*k-5,y+410*k,"420 P")
    sh.dim_h(x+5,x+580*k-5,y+1260*k,"580 P")
    sh.dim_h(x,x+610*k,y-27,"610 B")
    sh.text(x+610*k+12,y-22,"D1 →","small")
    sh.dim_v(x+580*k+58,y+25*k,y+800*k,"775 P")
    sh.dim_v(x+580*k+58,y+800*k,y+1650*k,"850 P")
    sh.text(1992,1085,"610 − 420 = 190 мм", "body")
    sh.text(1992,1117,"Разность по плану, не замер", "small")
    sh.text(1992,1147,"до коробки двери.", "small")
    sh.text(1992,1194,"↓ переход открыт в коридор 4", "small")

    sh.card(45,1265,2510,375,"#fff9ef")
    sh.text(72,1307,"Основа и ограничения размеров", "head")
    sh.text(72,1348,"Стена по B01: 1675 мм. Шкаф: 850 вдоль стены × 580 глубина × 2700 высота P. Банкетка: 775 × 420 × 460 P.", "body")
    sh.text(72,1385,"Потолок: 2750 мм в отмеченных точках; 50 мм разницы с высотой шкафа не подтверждают монтажный зазор.", "body")
    sh.text(72,1422,"Вход D1 по БТИ: 610 + 1010 + 470 = 2090 мм. Отдельный контроль: 1140 × 2150 мм, без привязки к углам.", "body")
    sh.text(72,1459,"Проход и открывание всех створок требуют проверки по фактическим размерам. Дальняя геометрия коридора не восстановлена.", "body")
    sh.text(72,1514,"B — размер плана БТИ · P — эскизное предложение · M — неизвестно, требуется измерить. Высоты — от пола.", "small")
    sh.text(72,1548,"Отделка, плинтус, монтажные зазоры и реальное положение D1/D2 могут изменить размеры мебели.", "small")
    sh.save(PAGE_A)


def bench_section(sh,x,floor,k,drawer):
    """Section looking along the wall. X direction is depth from the wall."""
    depth=420*k
    yseat=floor-460*k
    sh.line(x,floor,x,floor-660*k,extra='stroke="#385448" stroke-width="6"')
    sh.line(x-8,floor,x+depth+15,floor,extra='stroke="#385448" stroke-width="2"')
    sh.rect(x,yseat,depth,35*k,"#e8d6be","#ae987d",1,'rx="3"')
    sh.rect(x,yseat+35*k,depth,25*k,"#bd9d79")
    if drawer:
        sh.rect(x,floor-400*k,380*k,90*k,"#d5b997","#ae9274",1)
        sh.dim_h(x+5,x+380*k-5,floor-350*k,"380 P")
        sh.dim_v(x+depth+30,floor-310*k,floor,"310 P")
        sh.dim_v(x+depth+77,floor-400*k,floor-310*k,"90 P")
    else:
        sh.dim_v(x+depth+30,floor-400*k,floor,"400 P")
        xx=x+180*k; h=290*k
        sh.raw(f'<path d="M{xx:.2f} {floor-h:.2f} h38 v{h-18:.2f} h24 q12 0 17 18 h-79 Z" fill="#8d7b67"/>')
    sh.dim_h(x,x+depth,yseat-27,"420 P")
    sh.dim_v(x-40,yseat,floor,"460 P")


def page_b():
    sh=Sheet()
    heading(sh,"2","Больше размеров: шкаф внутри и обувь","Высоты от пола; внутренние ширины и глубины — предварительное предложение, не раскрой")
    sh.card(45,185,1158,1230)
    sh.text(72,225,"01  Внутреннее наполнение", "head")
    sh.text(74,258,"Передние дверцы условно сняты", "small")
    v=elevation(sh,250,1230,.34)
    sh.dim_h(v['service'],v['service']+v['service_w'],v['top']+27,"400 P")
    sh.dim_h(v['clothes'],v['clothes']+v['clothes_w'],v['top']+27,"396 P")
    sh.dim_v(v['cab']-112,v['top'],v['floor'],"2700 P")
    sh.dim_v(v['cab']-77,v['upper'],v['floor'],"2150 P")
    sh.dim_v(v['cab']-42,v['rail'],v['floor'],"1750 P")
    sh.dim_v(v['clothes']+v['clothes_w']-13,v['lower'],v['floor'],"380 P")
    sh.text(v['niche']+185*v['s'],v['drawer_top']+23,"370 P","small","middle")
    sh.dim_h(v['cab'],v['niche'],v['floor']+33,"850 P",False)
    sh.dim_h(v['niche'],v['end'],v['floor']+33,"775 P",False)
    sh.text(270,1330,"От верха нижней полки до оси штанги: 1750 − 380 = 1370 мм P.","small")
    sh.text(270,1363,"Фактическое место под одежду меньше из-за вешалок и фурнитуры.","small")

    sh.card(1220,185,1335,710)
    sh.text(1250,225,"02  Банкетка сбоку: две части одной ниши", "head")
    sh.text(1290,270,"Со стороны шкафа", "body")
    sh.text(1920,270,"Со стороны входной двери", "body")
    bench_section(sh,1320,735,.67,True)
    bench_section(sh,1920,735,.67,False)
    sh.text(1290,800,"Внешний размер сухого ящика:","body")
    sh.text(1290,832,"370 вдоль стены × 380 глубина × 90 высота P.","body")
    sh.text(1920,800,"Для высокой обуви оставлен", "body")
    sh.text(1920,832,"просвет около 400 мм P.", "body")

    sh.card(1220,913,1335,502)
    sh.text(1250,953,"03  Что ещё означают размеры", "head")
    sh.text(1250,992,"• 400 и 396 мм — ширина отделений внутри, между деталями P.","body")
    sh.text(1250,1028,"• Верхняя полка на h = 2150 мм; над ней около 532 мм P.","body")
    sh.text(1250,1064,"• Штанга на h = 1750 мм; нижняя съёмная полка на h = 380 мм P.","body")
    sh.text(1250,1100,"• 580 мм — наружная глубина шкафа вместе с фасадом P.","body")
    sh.text(1250,1136,"• Ящик указан снаружи; внутри меньше из-за стенок и направляющих.","body")
    sh.text(1250,1172,"• Высота, ширина и ось щита: M; на рисунке габарит условный.","body")
    sh.text(1250,1208,"• Фасады, зеркало, петли, задняя стенка и кабели — после обмера.","body")
    sh.text(1250,1244,"• Обувь стоит на общем полу одним рядом, не на выдвижной полке.","body")
    sh.text(1250,1301,"B — БТИ · P — предложение · M — нужно замерить.","small")
    sh.text(1250,1335,"Щит и трассу переноса проверяет электрик; мебель — после чистового обмера.","small")
    sh.card(45,1434,2510,206,"#fff9ef")
    sh.text(72,1477,"Проверка размерной цепочки", "head")
    sh.text(72,1518,"Стенка: 25 + 850 + 775 + 25 = 1675 мм. Шкаф: 400 + 396 + 3 × 18 = 850 мм. Размеры конструкции — P.","body")
    sh.text(72,1557,"Сиденье: 460 − 35 подушка − 25 основание = 400 мм. В зоне ящика: 400 − 90 = 310 мм P.","body")
    sh.text(72,1591,"До заказа проверить привязки D1/D2, размеры щита, чистовой пол, петли, направляющие и проходы с открытыми створками.","small")
    sh.save(PAGE_B)


if __name__ == "__main__":
    page_a()
    page_b()
