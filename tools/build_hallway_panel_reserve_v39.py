"""APT-001 hallway proposal with enlarged unverified electrical service bay.

The sheets separate interior clear widths from external cabinet depths and
identify the distribution board's real W/H/D and door clearance as unknown.
"""
from __future__ import annotations
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"Прихожая"
P1=OUT/"71_прихожая_увеличенный_щит_ширина_глубина_v39.svg"
P2=OUT/"72_прихожая_размеры_модулей_v39.svg"

assert 25+1050+575+25==1675
assert 550+446+3*18==1050
assert 574+470+3*2==1050
assert 2*284.5+3*2==575
assert 575-250==325
assert 460-35-25==400 and 400-90==310
assert 2700-18-2150==532
assert 610+1010+470==2090


class Sheet:
    def __init__(self,w=2600,h=1750):
        self.parts=[f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs><marker id="a" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto-start-reverse"><path d="M8 0 L0 4 L8 8" fill="none" stroke="#567668" stroke-width="1.2"/></marker></defs>
<style>text{{font-family:Arial,'Segoe UI',sans-serif;fill:#203d38}}.eyebrow{{font-size:19px;font-weight:bold;letter-spacing:2px;fill:#377561}}.title{{font-size:46px;font-weight:bold}}.subtitle{{font-size:23px;fill:#627d74}}.head{{font-size:26px;font-weight:bold}}.body{{font-size:21px;fill:#405c52}}.small{{font-size:18px;fill:#627a70}}.dimtext{{font-size:21px;font-weight:bold;fill:#2d5d4b}}.dim{{stroke:#567668;stroke-width:1.8;marker-start:url(#a);marker-end:url(#a)}}.ext{{stroke:#9eb2a5;stroke-width:1.4}}</style>
<rect width="{w}" height="{h}" fill="#f1f4ef"/>''']
    def raw(self,s):self.parts.append(s+"\n")
    def rect(self,x,y,w,h,fill,stroke="none",sw=1,extra=""):
        self.raw(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
    def line(self,x1,y1,x2,y2,cls="",extra=""):
        self.raw(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" class="{cls}" {extra}/>')
    def text(self,x,y,t,cls="body",anchor="start",extra=""):
        self.raw(f'<text x="{x:.2f}" y="{y:.2f}" class="{cls}" text-anchor="{anchor}" {extra}>{escape(t)}</text>')
    def card(self,x,y,w,h,fill="white"):
        self.rect(x,y,w,h,fill,"#dbe4dc",2,'rx="20"')
    def dimh(self,x1,x2,y,label,below=False):
        self.line(x1,y,x2,y,"dim")
        self.text((x1+x2)/2,y+27 if below else y-10,label,"dimtext","middle")
    def dimv(self,x,y1,y2,label):
        self.line(x,y1,x,y2,"dim")
        self.text(x-9,(y1+y2)/2,label,"dimtext","middle",f'transform="rotate(-90 {x-9:.2f} {(y1+y2)/2:.2f})"')
    def save(self,path):
        value="".join(self.parts)+"</svg>"
        ET.fromstring(value)
        path.write_text(value,encoding="utf-8")
        print(path.name, path.stat().st_size)


def heading(sh,n,title,subtitle):
    sh.text(55,47,f"APT-001 / ПРИХОЖАЯ / ВАРИАНТ C · V39 / ЛИСТ {n}","eyebrow")
    sh.text(55,106,title,"title")
    sh.text(57,149,subtitle,"subtitle")


def front(sh,x0,floor,s):
    cab=x0+25*s; cw=1050*s; bench=cab+cw; bw=575*s
    board=18*s; service=cab+board; sw=550*s
    coat=service+sw+board; cw_in=446*s
    top=floor-2700*s; upper=floor-2150*s; rail=floor-1750*s; lower=floor-380*s
    seat=floor-460*s; drawtop=floor-400*s; drawbottom=floor-310*s
    sh.rect(cab,top,cw,2700*s,"#dfc7a7","#927b60",2)
    sh.rect(service,top+board,sw,(2700-36)*s,"#e6f1eb","#afc9b8",1)
    sh.rect(service+sw,top,board,2700*s,"#c0a17f")
    sh.rect(coat,top+board,cw_in,(2700-36)*s,"#f9f4ec","#d0c3b4",1)
    sh.rect(cab,floor-80*s,cw,80*s,"#c0a17f")
    sh.rect(coat,upper,cw_in,board,"#ba9a78")
    sh.rect(coat,lower,cw_in,board,"#ba9a78")
    sh.line(coat+8,rail,coat+cw_in-8,rail,extra='stroke="#4d6255" stroke-width="3"')
    for i,color in enumerate(("#aaa994","#8e9787","#bba58a")):
        xx=coat+14+i*(cw_in-28)/3; ww=(cw_in-36)/3; yy=rail+19; hh=800*s
        sh.raw(f'<path d="M{xx:.2f} {yy:.2f} l-5 12 v{hh:.2f} h{ww:.2f} v{-hh:.2f} l-5 -12 Z" fill="{color}" stroke="#8d8271" stroke-width="1"/>')
        sh.raw(f'<path d="M{xx-3:.2f} {yy:.2f} l8 -8 l8 8" fill="none" stroke="#5c695c" stroke-width="2"/>')
    # Unscaled placeholder: the actual electrical panel size is unknown.
    sh.rect(service+sw*.19,floor-1640*s,sw*.62,570*s,"none","#81a796",2,'stroke-dasharray="7 5"')
    sh.text(service+sw/2,floor-1370*s,"ЭЩ-03","small","middle")
    sh.text(service+sw/2,floor-1280*s,"габарит M","small","middle")
    sh.rect(bench,top,bw,upper-top,"#dfc7a7","#927b60",2)
    sh.line(bench+bw/2,top,bench+bw/2,upper,extra='stroke="#a98e72" stroke-width="1.5"')
    sh.rect(bench,upper,bw,seat-upper,"#daeadd","#b3c8b7",1)
    for k in (.30,.62):
        x=bench+bw*k; y=floor-1500*s
        sh.raw(f'<path d="M{x:.2f} {y:.2f} v14 q0 6 6 6" fill="none" stroke="#65836f" stroke-width="3"/>')
    sh.rect(bench,seat,bw,35*s,"#e9d7bf","#ad967a",1,'rx="3"')
    sh.rect(bench,seat+35*s,bw,25*s,"#bd9d78")
    sh.rect(bench,drawtop,250*s,drawbottom-drawtop,"#d4b796","#ae9274",1)
    for i,height in enumerate((110,285)):
        x=bench+bw*(.18+i*.52); y=floor-height*s
        sh.raw(f'<path d="M{x:.2f} {y:.2f} h15 v{height*s-7:.2f} h9 q5 1 7 7 h-31 Z" fill="#8a7965"/>')
    sh.line(cab,floor,bench+bw+3,floor,extra='stroke="#587469" stroke-width="2"')
    return {"x0":x0,"endwall":x0+1675*s,"cab":cab,"endcab":bench,"endbench":bench+bw,
            "top":top,"floor":floor,"service":service,"sw":sw,"coat":coat,"cw":cw_in,
            "seat":seat,"upper":upper,"rail":rail,"lower":lower,"drawtop":drawtop,"drawbottom":drawbottom,"s":s}


def page1():
    sh=Sheet()
    heading(sh,"1","Больше места для щитка: новая компоновка","Увеличенная секция — предложение до замера щита; все размеры в миллиметрах")
    sh.card(45,185,1260,1125); sh.card(1325,185,1230,1125)
    sh.text(72,226,"01  Ширины и высоты спереди", "head")
    sh.text(74,259,"Коридор слева · входная дверь справа · дверцы условно сняты", "small")
    v=front(sh,215,1230,.34)
    sh.dimh(v['x0'],v['endwall'],v['top']-24,"1675 B")
    sh.dimv(v['cab']-40,v['top'],v['floor'],"2700 P")
    sh.dimh(v['service'],v['service']+v['sw'],v['top']+38,"550 P")
    sh.dimh(v['coat'],v['coat']+v['cw'],v['top']+38,"446 P")
    sh.dimh(v['cab'],v['endcab'],v['floor']+28,"1050 P",True)
    sh.dimh(v['endcab'],v['endbench'],v['floor']+28,"575 P",True)
    sh.text(830,346,"Шкаф общий", "head")
    sh.text(830,381,"1050 × 580 × 2700 P", "body")
    sh.text(830,415,"550 — свет секции щита P", "body")
    sh.text(830,448,"446 — свет секции одежды P", "body")
    sh.text(830,514,"Антресоль у входа", "head")
    sh.text(830,549,"575 × 420 × 550 P", "body")
    sh.text(830,583,"Низ на высоте 2150 P", "body")
    sh.text(830,650,"Банкетка", "head")
    sh.text(830,685,"575 × 420, высота 460 P", "body")
    sh.text(830,718,"Ящик 250 × 380 × 90 P", "body")
    sh.text(830,785,"Место для обуви", "head")
    sh.text(830,820,"Один ряд на полу.", "body")
    sh.text(830,853,"Ориентир: около 2 пар;", "body")
    sh.text(830,886,"зависит от обуви и боковин.", "body")
    sh.text(830,969,"Было: шкаф 850 / место 775.", "small")
    sh.text(830,1001,"Стало: шкаф 1050 / место 575.", "small")
    sh.text(830,1033,"Секция щита: 400 → 550 P.", "small")
    sh.text(830,1097,"Высота шкафа — корпуса;", "small")
    sh.text(830,1129,"размеры фасадов уточняются.", "small")
    sh.text(830,1200,"25 + 1050 + 575 + 25 = 1675", "body")

    sh.text(1352,226,"02  План сверху: ширина и глубина", "head")
    sh.text(1354,259,"Глубины 580 и 420 — наружные, от левой стены", "small")
    x,y,k=1410.0,365.0,.45
    sh.line(x,y,x,y+1675*k,extra='stroke="#355145" stroke-width="7"')
    sh.rect(x,y+25*k,420*k,575*k,"#dbeadd","#8fa998",2)
    sh.rect(x,y+600*k,580*k,1050*k,"#dec4a1","#a78a6a",2)
    # Cabinet internal zones: 18 + 446 + 18 + 550 + 18 = 1050.
    sh.rect(x,y+618*k,580*k,446*k,"#f7f0e5","#c4b9aa",1)
    sh.rect(x,y+1082*k,580*k,550*k,"#e6f1eb","#b8cdbd",1)
    sh.text(x+75*k,y+195*k,"БАНКЕТКА", "body")
    sh.text(x+55*k,y+735*k,"ОДЕЖДА", "body")
    sh.text(x+65*k,y+1265*k,"ЩИТ", "body")
    sh.dimh(x+4,x+420*k-4,y+355*k,"420 P")
    sh.dimh(x+4,x+580*k-4,y+925*k,"580 P")
    sh.dimh(x+4,x+580*k-4,y+1495*k,"580 P")
    sh.dimv(x+580*k+55,y+25*k,y+600*k,"575 P")
    sh.dimv(x+580*k+55,y+600*k,y+1650*k,"1050 P")
    sh.dimh(x,x+610*k,y-32,"610 B")
    sh.text(x+610*k+12,y-27,"D1 →", "small")
    sh.text(1400,1195,"↓ открытый переход в коридор 4", "small")
    sh.text(1920,360,"Глубина каждого элемента", "head")
    sh.text(1920,400,"Секция щита: 580 P с фасадом", "body")
    sh.text(1920,435,"Секция одежды: 580 P с фасадом", "body")
    sh.text(1920,470,"Верх над сиденьем: 420 P", "body")
    sh.text(1920,505,"Банкетка: 420 P", "body")
    sh.text(1920,540,"Ящик для тапочек: 380 P", "body")
    sh.text(1920,606,"Внутренние глубины — M:", "head")
    sh.text(1920,641,"зависят от задней стенки,", "body")
    sh.text(1920,676,"фасадов и прокладки кабелей.", "body")
    sh.text(1920,755,"У D1 по B01: 610 − 420 = 190.", "body")
    sh.text(1920,790,"Это не замер до коробки", "small")
    sh.text(1920,820,"и не проверка открывания.", "small")
    sh.text(1920,900,"Ранее показанный рендер", "body")
    sh.text(1920,935,"относится к ширине 850/775,", "body")
    sh.text(1920,970,"а не к этой новой пропорции.", "body")

    sh.card(45,1327,2510,370,"#fff9ef")
    sh.text(72,1370,"Сначала проверить щит и доступ", "head")
    sh.text(72,1410,"550 мм — предполагаемая внутренняя ширина секции, не размер щита и не гарантия, что он поместится.", "body")
    sh.text(72,1447,"Нужны реальные ширина, высота и глубина щита с рамой, открывание его дверцы, кабельные вводы и доступ для обслуживания.", "body")
    sh.text(72,1484,"Перенос, размещение внутри мебели, материалы, допустимые расстояния и возможность обслуживания проверяются с электриком по месту.", "body")
    sh.text(72,1521,"B — БТИ · P — проектное предложение · M — измерить. Мебельные размеры не являются размерами для изготовления.", "small")
    sh.text(72,1557,"D1: 610 + 1010 + 470 = 2090 по B01; отдельный контроль 1140 × 2150 к углам не привязан.", "small")
    sh.text(72,1593,"Уменьшение банкетки снижает запас для обуви: 2 пары — ориентир, а не подтверждённая вместимость.", "small")
    sh.save(P1)


def section(sh,x,floor,k,drawer):
    depth=420*k; seat=floor-460*k
    sh.line(x,floor,x,floor-650*k,extra='stroke="#385648" stroke-width="6"')
    sh.line(x-8,floor,x+depth+15,floor,extra='stroke="#385648" stroke-width="2"')
    sh.rect(x,seat,depth,35*k,"#e8d6be","#af987b",1,'rx="3"')
    sh.rect(x,seat+35*k,depth,25*k,"#bd9d79")
    if drawer:
        sh.rect(x,floor-400*k,380*k,90*k,"#d6b995","#a88c6e",1)
        sh.dimh(x+5,x+380*k-5,floor-350*k,"380 P")
        sh.dimv(x+depth+34,floor-310*k,floor,"310 P")
        sh.dimv(x+depth+80,floor-400*k,floor-310*k,"90 P")
    else:
        sh.dimv(x+depth+34,floor-400*k,floor,"400 P")
        sh.raw(f'<path d="M{x+180*k:.2f} {floor-290*k:.2f} h38 v{290*k-18:.2f} h24 q12 0 17 18 h-79 Z" fill="#8c7a66"/>')
    sh.dimh(x,x+depth,seat-27,"420 P")
    sh.dimv(x-40,seat,floor,"460 P")


def page2():
    sh=Sheet()
    heading(sh,"2","Ширина каждого модуля и хранение","Все размеры мебели — предварительные; глубины шкафов указаны снаружи, в свету пока неизвестны")
    sh.card(45,185,1200,1125); sh.card(1265,185,1290,680); sh.card(1265,883,1290,427)
    sh.text(72,226,"01  Внутренние ширины и высоты", "head")
    sh.text(74,258,"400 мм для щита заменены предложением 550 мм P", "small")
    v=front(sh,195,1220,.33)
    sh.dimh(v['service'],v['service']+v['sw'],v['top']+35,"550 P")
    sh.dimh(v['coat'],v['coat']+v['cw'],v['top']+35,"446 P")
    sh.dimv(v['cab']-112,v['top'],v['floor'],"2700 P")
    sh.dimv(v['cab']-77,v['upper'],v['floor'],"2150 P")
    sh.dimv(v['cab']-42,v['rail'],v['floor'],"1750 P")
    sh.dimh(v['cab'],v['endcab'],v['floor']+28,"1050 P",True)
    sh.dimh(v['endcab'],v['endbench'],v['floor']+28,"575 P",True)
    sh.text(855,430,"ЩИТ", "head")
    sh.text(855,465,"550 мм внутри P", "body")
    sh.text(855,500,"Высота/глубина", "body")
    sh.text(855,535,"самого щита: M", "body")
    sh.text(855,615,"КУРТКИ", "head")
    sh.text(855,650,"446 мм внутри P", "body")
    sh.text(855,685,"Штанга h1750 P", "body")
    sh.text(855,720,"Верх полки h2150 P", "body")
    sh.text(855,755,"Нижняя h380 P", "body")
    sh.text(855,835,"БАНКЕТКА", "head")
    sh.text(855,870,"575 × 420 P", "body")
    sh.text(855,905,"h сиденья 460 P", "body")
    sh.text(855,970,"250 — ящик вдоль стены", "body")
    sh.text(855,1005,"325 — оставшийся участок", "body")
    sh.text(855,1040,"до учёта боковин и зазоров", "small")
    sh.text(855,1110,"Панель: 550 + 446 +", "body")
    sh.text(855,1145,"3 × 18 = 1050 P", "body")

    sh.text(1292,226,"02  Две части банкетки сбоку", "head")
    sh.text(1320,268,"Со стороны шкафа", "body")
    sh.text(1920,268,"Со стороны входной двери", "body")
    section(sh,1340,690,.62,True)
    section(sh,1935,690,.62,False)
    sh.text(1320,755,"Ящик снаружи: 250 вдоль стены", "body")
    sh.text(1320,788,"× 380 в глубину × 90 в высоту P.", "body")
    sh.text(1920,755,"Просвет для высокой обуви", "body")
    sh.text(1920,788,"до сиденья около 400 мм P.", "body")
    sh.text(1320,830,"Внутренний размер ящика меньше; примерить тапочки.", "small")

    sh.text(1292,924,"03  Ширина фасадов — только предварительная", "head")
    sh.text(1292,964,"Два фасада шкафа: ≈574 и 470 мм P, если они накладные и все три зазора по 2 мм.", "body")
    sh.text(1292,1000,"Два фасада антресоли: ≈284,5 мм каждый P при тех же условных зазорах.", "body")
    sh.text(1292,1036,"Фактическая ширина проёма меняется из-за петель; размер дверцы щита неизвестен.", "body")
    sh.text(1292,1072,"Зеркало, петли и направление распахивания определить после измерения и выбора фурнитуры.", "body")
    sh.text(1292,1133,"Для одежды расстояние от верха нижней полки до оси штанги: 1750 − 380 = 1370 мм P.", "body")
    sh.text(1292,1170,"Вешалки занимают часть этой высоты; ширину штанги уменьшат крепления.", "body")
    sh.text(1292,1236,"Размеры B — БТИ; P — предложение; M — неизвестно, необходимо измерить.", "small")

    sh.card(45,1327,2510,370,"#fff9ef")
    sh.text(72,1368,"Проверка и компромисс", "head")
    sh.text(72,1409,"25 + 1050 + 575 + 25 = 1675 мм. Корпус: 550 + 446 + 3 × 18 = 1050 мм.", "body")
    sh.text(72,1446,"575 − 250 = 325 мм — только плановая разность для участка под обувь, до учёта опор, стенок и креплений.", "body")
    sh.text(72,1483,"Для 550 мм необходимо отдельно проверить реальную чистую ширину проёма, открывание дверцы щита и место под кабели.", "body")
    sh.text(72,1520,"Даже увеличенная секция может оказаться мала. До заказа измерить щит и согласовать конструкцию и перенос с электриком.", "body")
    sh.text(72,1573,"Под сиденьем: 460 − 35 подушка − 25 основание = 400; под ящиком 400 − 90 = 310 мм P.", "small")
    sh.text(72,1608,"Обувь — на полу в один ряд; точное число пар зависит от габаритов обуви и конструкции.", "small")
    sh.save(P2)


if __name__=="__main__":
    page1();page2()
