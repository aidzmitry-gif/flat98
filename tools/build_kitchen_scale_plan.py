# -*- coding: utf-8 -*-
"""Scale furniture fit test for kitchen-living B01; all geometry is in millimetres."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "plans" / "07_Кухня-гостиная_мебель_М1_25_черновик.pdf"
SCALE = 1 / 25

def setup_fonts():
    r, b = Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")
    if "K25" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("K25", str(r)))
    if "K25B" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("K25B", str(b)))
    return "K25", "K25B"

def pt(v): return v * SCALE
def write(c, f, x, y, size, s, color="#1f2933", center=False):
    c.setFont(f, size); c.setFillColor(HexColor(color))
    (c.drawCentredString if center else c.drawString)(x * mm, y * mm, s)

def rect(c, x, y, w, h, fill, stroke="#3e4852", line=.25):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor(stroke)); c.setLineWidth(line * mm)
    c.rect(x * mm, y * mm, w * mm, h * mm, fill=1, stroke=1)

def dim_h(c, f, x1, x2, y, label):
    c.setStrokeColor(HexColor("#59636e")); c.setLineWidth(.16 * mm); c.line(x1*mm,y*mm,x2*mm,y*mm)
    for x in (x1,x2): c.line(x*mm,(y-1.5)*mm,x*mm,(y+1.5)*mm)
    write(c, f, (x1+x2)/2, y+1.2, 5.2, label, "#59636e", True)

def dim_v(c, f, x, y1, y2, label):
    c.setStrokeColor(HexColor("#59636e")); c.setLineWidth(.16 * mm); c.line(x*mm,y1*mm,x*mm,y2*mm)
    for y in (y1,y2): c.line((x-1.5)*mm,y*mm,(x+1.5)*mm,y*mm)
    write(c, f, x+2, (y1+y2)/2, 5.2, label, "#59636e")

def build():
    n, b = setup_fonts(); c = canvas.Canvas(str(OUT), pagesize=landscape(A3))
    pw, ph = landscape(A3); c.setFillColor(white); c.rect(0,0,pw,ph,fill=1,stroke=0)
    c.setStrokeColor(HexColor("#1f2933")); c.setLineWidth(.35*mm); c.rect(8*mm,8*mm,pw-16*mm,ph-16*mm,fill=0,stroke=1)
    write(c,b,14,283,16,"КУХНЯ-ГОСТИНАЯ | МЕБЕЛЬНЫЙ ТЕСТ М 1:25")
    write(c,n,14,275,6.1,"Внутренний контур B01 5710×3500. Мебель из присланного эскиза наложена в миллиметрах; красные зоны требуют проверки до заказа.","#4b5563")

    ox, oy = 18, 77
    W, H = pt(5710), pt(3500)
    # Shell: external wall thickness has no numeric B01 evidence, so only graphic band.
    rect(c,ox,oy,W,H,"#ffffff","#111827",.65)
    write(c,b,ox+W/2,oy+H+7,8,"1 КУХНЯ-ГОСТИНАЯ: 5710×3500",center=True)
    dim_h(c,n,ox,ox+W,oy+H+3,"5710")
    dim_v(c,n,ox-4,oy,oy+H,"3500")

    # Confirmed opening geometry: coordinate origin is the lower-left inner room corner.
    # D2 left: B01 200 then 910; control clean width 915. O1 right: 600 + 1600 + 1300.
    d2_y1, d2_y2 = oy+pt(200), oy+pt(1110)
    c.setFillColor(white); c.rect((ox-2)*mm,(d2_y1-1)*mm,5*mm,(d2_y2-d2_y1+2)*mm,fill=1,stroke=0)
    c.setStrokeColor(HexColor("#a85d18")); c.setLineWidth(.45*mm); c.line(ox*mm,d2_y1*mm,ox*mm,d2_y2*mm)
    write(c,b,ox-2,d2_y2+4,5,"D2: 910 B01 / 915 контроль","#a85d18")
    write(c,n,ox-2,d2_y1-7,4.7,"ось и открывание н/д","#a85d18")
    o1_y1, o1_y2 = oy+pt(600), oy+pt(2200)
    c.setFillColor(white); c.rect((ox+W-2)*mm,(o1_y1-1)*mm,5*mm,(o1_y2-o1_y1+2)*mm,fill=1,stroke=0)
    c.setStrokeColor(HexColor("#087f5b")); c.setLineWidth(.55*mm); c.line((ox+W)*mm,o1_y1*mm,(ox+W)*mm,o1_y2*mm)
    write(c,b,ox+W+3,(o1_y1+o1_y2)/2,5,"O1 ТЕРРАСА 1600","#087f5b")
    dim_v(c,n,ox+W+9,oy,oy+pt(600),"600")
    dim_v(c,n,ox+W+14,o1_y1,o1_y2,"1600")
    dim_v(c,n,ox+W+19,o1_y2,oy+H,"1300")

    # Unblocked movement bands: derive from confirmed openings, 900 mm target shown as a non-furniture zone.
    c.setStrokeColor(HexColor("#e07a16")); c.setLineWidth(.35*mm); c.setDash(2*mm,1.2*mm)
    c.rect((ox+pt(0))*mm,(oy+pt(0))*mm,pt(1200)*mm,pt(1300)*mm,fill=0,stroke=1)
    c.rect((ox+pt(4810))*mm,(oy+pt(350))*mm,pt(900)*mm,pt(2100)*mm,fill=0,stroke=1); c.setDash()
    write(c,b,ox+pt(600),oy+pt(1170),4.8,"ВХОДНАЯ ЗОНА БЕЗ МЕБЕЛИ","#b86510",True)
    write(c,b,ox+pt(5260),oy+pt(2310),4.7,"ПРОХОД К ТЕРРАСЕ ≥900","#b86510",True)

    def furn(x,y,w,h,label,fill="#dcecf6",fs=5.0):
        X,Y,WW,HH=ox+pt(x),oy+pt(y),pt(w),pt(h); rect(c,X,Y,WW,HH,fill)
        write(c,n,X+WW/2,Y+HH/2-1,fs,label,"#26374a",True)
        return X,Y,WW,HH

    # Reference kitchen modules: exact source-module chain is 950+600+300+600+250+710 = 3410.
    furn(0,2900,950,600,"ПЕНАЛ 950","#f4e3c5")
    furn(950,2900,600,600,"600","#f4e3c5")
    furn(1550,2900,300,600,"300","#f4e3c5")
    furn(1850,2900,600,600,"600","#f4e3c5")
    furn(2450,2900,250,600,"250","#f4e3c5")
    furn(2700,2900,710,600,"710","#f4e3c5")
    dim_h(c,n,ox,ox+pt(3410),oy+H-3,"950+600+300+600+250+710 = 3410")
    furn(0,1300,600,600,"МОЙКА / ПММ","#f4e3c5",4.4)
    furn(0,1900,600,1000,"НИЖНИЙ РЯД","#f4e3c5")
    furn(1550,1900,1250,1000,"ПОЛУОСТРОВ 1250*\nглубина уточнить","#f4e3c5",4.5)
    # Reference loose furniture: these dimensions are explicitly readable on the supplied plan.
    furn(3100,1350,1620,950,"РАСКЛАДНОЙ СТОЛ 1620×950\nдо 2220","#e8efe4",4.8)
    furn(2400,100,2300,900,"ДИВАН 2300*","#e9e1dc")
    furn(1950,300,400,400,"СТОЛИК 400","#e9e1dc",4.4)
    furn(4790,100,700,450,"МЕДИА / КОЛОНКИ","#f1dce6",4.5)

    # Chairs/working clearances deliberately show what must stay free, not furniture dimensions.
    c.setStrokeColor(HexColor("#7e8a94")); c.setLineWidth(.18*mm); c.setDash(1*mm,1*mm)
    c.rect((ox+pt(3000))*mm,(oy+pt(750))*mm,pt(1820)*mm,pt(2150)*mm,fill=0,stroke=1); c.setDash()
    write(c,n,ox+pt(3910),oy+pt(780),4.5,"зона стульев/проходов\nуточнить по факту","#6b7280",True)

    # Notes and exact source boundary.
    rect(c,270,170,134,84,"#fbfcfd")
    write(c,b,277,242,9,"ЧТО УЖЕ СОБЛЮДЕНО")
    lines=(
        "• комната 5710×3500 по B01;",
        "• D2 в левой стене: 200 + 910;",
        "• O1 справа: 600 + 1600 + 1300;",
        "• стол 1620×950, диван 2300,",
        "  кухонная цепь 3410 — из эскиза;",
        "• мебели нет в зоне D2 и O1."
    )
    yy=232
    for s in lines: write(c,n,278,yy,5.5,s,"#374151"); yy-=9
    rect(c,270,75,134,80,"#fff7ed")
    write(c,b,277,143,8.2,"ЧТО НЕ МОЖНО ВЫДУМЫВАТЬ","#9a4e16")
    notes=(
        "• реальную стену кухни и оси воды;",
        "• ось D2 и направление открывания;",
        "• глубину полуострова и кухни;",
        "• посадку/стулья у стола и ширины проходов;",
        "• рабочие места: в этот набор мебели",
        "  два постоянных стола не помещаются без компромисса."
    )
    yy=133
    for s in notes: write(c,n,278,yy,5.25,s,"#4b5563"); yy-=8
    write(c,n,18,50,5,"* Размеры с присланного эскиза, не подтверждённые B01. Никакой размер не переносится в заказ без контрольной привязки к стене/проёму.","#5c6570")
    write(c,n,18,42,5,"Следующий шаг: выбрать приоритет — большой раскладной стол, два постоянных рабочих места или полуостров. Все три функции в полном размере конфликтуют в 19,99 м².","#5c6570")
    write(c,n,404,14,4.2,"PLN-001 | черновик 02 | 15.08.2026","#606870",True)
    c.save(); return OUT
if __name__ == "__main__": print(build())
