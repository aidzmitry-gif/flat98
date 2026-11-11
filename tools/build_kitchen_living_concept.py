# -*- coding: utf-8 -*-
"""Draft 01: open kitchen-living arrangement, derived from B01 geometry only."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "plans" / "06_Кухня-гостиная_открытая_схема_01.pdf"

def font():
    reg, bold = Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")
    if "KLArial" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("KLArial", str(reg)))
    if "KLArialB" not in pdfmetrics.getRegisteredFontNames(): pdfmetrics.registerFont(TTFont("KLArialB", str(bold)))
    return "KLArial", "KLArialB"

def text(c, f, x, y, size, s, color="#26374a", center=False):
    c.setFont(f, size); c.setFillColor(HexColor(color))
    (c.drawCentredString if center else c.drawString)(x*mm, y*mm, s)

def box(c, x, y, w, h, fill, label="", f=None, size=5.1):
    c.setFillColor(HexColor(fill)); c.setStrokeColor(HexColor("#44515c")); c.setLineWidth(.25*mm)
    c.rect(x*mm,y*mm,w*mm,h*mm,fill=1,stroke=1)
    if label: text(c,f,x+w/2,y+h/2-1,size,label,"#26374a",True)

def dim(c, x1,y1,x2,y2, label, f):
    c.setStrokeColor(HexColor("#66717c")); c.setLineWidth(.18*mm); c.line(x1*mm,y1*mm,x2*mm,y2*mm)
    if abs(x2-x1) > abs(y2-y1):
        for x in (x1,x2): c.line(x*mm,(y1-1.6)*mm,x*mm,(y1+1.6)*mm)
        text(c,f,(x1+x2)/2,y1+1.5,5,label,"#5d6770",True)
    else:
        for y in (y1,y2): c.line((x1-1.6)*mm,y*mm,(x1+1.6)*mm,y*mm)
        text(c,f,x1+2.2,(y1+y2)/2,5,label,"#5d6770")

def build():
    normal,bold=font(); c=canvas.Canvas(str(OUT),pagesize=landscape(A3)); pw,ph=landscape(A3)
    c.setFillColor(white); c.rect(0,0,pw,ph,fill=1,stroke=0)
    c.setStrokeColor(HexColor("#1f2933")); c.setLineWidth(.35*mm); c.rect(8*mm,8*mm,pw-16*mm,ph-16*mm,fill=0,stroke=1)
    text(c,bold,14,283,17,"PLN-001 | КУХНЯ-ГОСТИНАЯ: ОТКРЫТАЯ СХЕМА 01")
    text(c,normal,14,275,6.2,"Начинаем заново: без перегородок, без мебели в маршруте вход - терраса. Мебель пока не заказывается.","#4d5864")

    # B01 shell: scale 0.042 mm on sheet per 1 m of room (5710 x 3500).
    sx,sy,sc=18,72,.042
    W,H=5710*sc,3500*sc
    c.setFillColor(HexColor("#fbfbfb")); c.setStrokeColor(HexColor("#202020")); c.setLineWidth(.65*mm); c.rect(sx*mm,sy*mm,W*mm,H*mm,fill=1,stroke=1)
    text(c,bold,sx+W/2,sy+H+7,8,"1 КУХНЯ-ГОСТИНАЯ — B01 5710×3500",center=True)
    dim(c,sx,sy+H+3,sx+W,sy+H+3,"5710",normal); dim(c,sx-4,sy,sx-4,sy+H,"3500",normal)

    # Source-confirmed apertures: D2 remains symbolical because its axis is not fixed; terrace opening has B01 offsets.
    c.setFillColor(white); c.rect((sx-1)*mm,(sy-1)*mm,(915*sc+2)*mm,5*mm,fill=1,stroke=0)
    c.setStrokeColor(HexColor("#ba6a18")); c.setLineWidth(.35*mm); c.setDash(2*mm,1*mm); c.line(sx*mm,sy*mm,(sx+915*sc)*mm,sy*mm); c.setDash()
    text(c,bold,sx+915*sc/2,sy-6,5.2,"ВХОД ИЗ ПРИХОЖЕЙ: D2 915, ось н/д","#a75c16",True)
    y_open=sy+600*sc; h_open=1600*sc
    c.setFillColor(white); c.rect((sx+W-2)*mm,(y_open-1)*mm,5*mm,(h_open+2)*mm,fill=1,stroke=0)
    c.setStrokeColor(HexColor("#16805f")); c.setLineWidth(.55*mm); c.line((sx+W)*mm,y_open*mm,(sx+W)*mm,(y_open+h_open)*mm)
    text(c,bold,sx+W+4,y_open+h_open/2,5.2,"ВЫХОД НА ТЕРРАСУ 1600","#16805f")

    # Furniture zones. Exact kitchen run must be moved only after water/vent axes are locked.
    def p(mm_x,mm_y): return sx+mm_x*sc, sy+mm_y*sc
    def furniture(mm_x,mm_y,mm_w,mm_h,fill,label,size=5.1):
        x,y=p(mm_x,mm_y); box(c,x,y,mm_w*sc,mm_h*sc,fill,label,normal,size)
    furniture(650,2820,3650,600,"#f6e5cd","ПРЯМАЯ КУХНЯ 3600-3900: оси воды/вент. уточнить",4.8)
    furniture(700,1770,1400,700,"#dcecf6","АНАСТАСИЯ: СТОЛ РЯДОМ С КУХНЕЙ",4.6)
    furniture(2350,1770,1400,700,"#dcecf6","ДМИТРИЙ: ВТОРОЙ СТОЛ, ТА ЖЕ ЛИНИЯ",4.6)
    furniture(3900,1370,1250,800,"#f5eadc","СТОЛ 4-6",5.0)
    furniture(1700,350,2350,850,"#ece2db","ДИВАН / МЕДИА",5.2)
    furniture(4300,300,700,300,"#f1dce6","КОЛОНКИ",4.8)
    furniture(950,350,500,600,"#e7eef5","НИЗКОЕ\nХРАНЕНИЕ",4.3)

    # Open route that must survive the final furniture fit.
    c.setStrokeColor(HexColor("#c8761e")); c.setLineWidth(.45*mm); c.setDash(3*mm,1.5*mm)
    c.line((sx+460*sc)*mm,(sy+380*sc)*mm,(sx+5050*sc)*mm,(sy+380*sc)*mm)
    c.line((sx+5050*sc)*mm,(sy+380*sc)*mm,(sx+5050*sc)*mm,(sy+1400*sc)*mm); c.setDash()
    text(c,bold,sx+2750*sc,sy+540*sc,5.4,"СВОБОДНЫЙ МАРШРУТ: ВХОД - ТЕРРАСА","#a75c16",True)

    # Right-side decision panel.
    box(c,272,181,132,74,"#fbfcfd",f=normal)
    text(c,bold,278,245,9,"ПРИНЦИП РАССТАНОВКИ")
    lines=[
        "1. Прямая кухня лучше угловой: не забирает вход и оставляет выход на террасу.",
        "2. Оба стола стоят одной линией рядом с кухней, без стены и без экрана.",
        "3. Стол и диван - в гостиной части; колонки на медиа-тумбе, не на столах.",
        "4. Кухню нельзя окончательно ставить до осей воды, вентиляции и радиатора.",
        "5. Схема показывает функции и проходы, а не размеры заказной мебели."
    ]
    yy=235
    for line in lines: text(c,normal,280,yy,5.5,line,"#374151"); yy-=10
    box(c,272,72,132,94,"#fffaf4",f=normal)
    text(c,bold,278,155,8,"ЧТО ПРОВЕРЯЕМ ДАЛЬШЕ","#8a4b22")
    checklist=["точную стену кухни и мойки;","фактические радиатор и подоконник;","открывание D2 и зону входа;","глубину дивана и стола;","проходы минимум 900 мм."]
    yy=145
    for q in checklist: text(c,normal,280,yy,5.5,"• "+q,"#374151"); yy-=10
    text(c,normal,18,52,5.1,"Источник геометрии: БТИ B01 5710×3500; выход на террасу 1600 с отступами 600/1300. Позиция D2 показана схемно.","#5d6770")
    text(c,normal,18,43,5.1,"Следующий лист: уточнённая кухня с настоящими фасадами, техникой и розетками - после подтверждения точки воды и входного узла.","#5d6770")
    text(c,normal,404,14,4.2,"PLN-001 | черновик 01 | 15.08.2026","#606870",True)
    c.save(); return OUT
if __name__=="__main__": print(build())
