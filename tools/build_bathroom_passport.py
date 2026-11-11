from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "03_Ванная_паспорт_обмеров.docx"
BLUE, DARK, HEADER, CAUTION = "2E74B5", "1F4D78", "E8EEF5", "FFF4CE"

def shade(cell, color):
    p = cell._tc.get_or_add_tcPr()
    e = OxmlElement("w:shd"); e.set(qn("w:fill"), color); p.append(e)

def cell_margin(cell, top=80, start=120, bottom=80, end=120):
    p = cell._tc.get_or_add_tcPr(); m = p.first_child_found_in("w:tcMar")
    if m is None: m = OxmlElement("w:tcMar"); p.append(m)
    for side, value in (("top",top),("start",start),("bottom",bottom),("end",end)):
        e = m.find(qn(f"w:{side}"))
        if e is None: e = OxmlElement(f"w:{side}"); m.append(e)
        e.set(qn("w:w"), str(value)); e.set(qn("w:type"), "dxa")

def set_widths(table, widths):
    table.autofit = False
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = width
            p = cell._tc.get_or_add_tcPr(); e = p.find(qn("w:tcW"))
            if e is None: e = OxmlElement("w:tcW"); p.append(e)
            e.set(qn("w:w"), str(round(width.inches*1440))); e.set(qn("w:type"), "dxa")

def table(doc, rows, widths):
    t = doc.add_table(rows=1, cols=len(rows[0])); t.alignment = WD_TABLE_ALIGNMENT.LEFT; t.style = "Table Grid"
    for cell, value in zip(t.rows[0].cells, rows[0]): cell.text = value
    for values in rows[1:]:
        for cell, value in zip(t.add_row().cells, values): cell.text = value
    set_widths(t, widths)
    for r, row in enumerate(t.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER; cell_margin(cell)
            for p in cell.paragraphs:
                p.paragraph_format.space_after = Pt(0)
                for run in p.runs: run.font.name = "Calibri"; run.font.size = Pt(10)
            if r == 0:
                shade(cell, HEADER)
                for run in cell.paragraphs[0].runs: run.bold = True
    return t

doc = Document(); s = doc.sections[0]
for attr in ("top_margin","bottom_margin","left_margin","right_margin"): setattr(s, attr, Inches(1))
s.header_distance = Inches(.492); s.footer_distance = Inches(.492)
normal = doc.styles["Normal"]; normal.font.name = "Calibri"; normal.font.size = Pt(11); normal.paragraph_format.space_after = Pt(6); normal.paragraph_format.line_spacing = 1.25
for name,size,color,before,after in [("Heading 1",16,BLUE,18,10),("Heading 2",13,BLUE,14,7)]:
    st=doc.styles[name]; st.font.name="Calibri"; st.font.size=Pt(size); st.font.color.rgb=RGBColor.from_string(color); st.paragraph_format.space_before=Pt(before); st.paragraph_format.space_after=Pt(after)
title=doc.add_paragraph(); title.paragraph_format.space_after=Pt(3); r=title.add_run("Паспорт обмеров — ванная комната"); r.font.name="Calibri"; r.font.size=Pt(22); r.bold=True; r.font.color.rgb=RGBColor.from_string(DARK)
meta=doc.add_paragraph(); meta.paragraph_format.space_after=Pt(12); r=meta.add_run("Проект: ремонт квартиры  |  Актуально на 27.07.2026  |  Версия 0.1"); r.italic=True; r.font.color.rgb=RGBColor(89,89,89)
p=doc.add_paragraph(); p.add_run("Назначение. ").bold=True; p.add_run("Фиксация стартовых обмеров ванной комнаты. Документ подходит для подготовки обмерного плана; финальные рабочие решения принимаются после контрольных измерений коммуникаций и проёмов.")

doc.add_paragraph("1. Габариты помещения", style="Heading 1")
table(doc,[
    ("Параметр","Значение","Статус"),
    ("Ширина ванной", "1740 мм", "Предварительно"),
    ("Глубина ванной", "1745 мм", "Предварительно"),
    ("Размер на прежнем плане", "1740 × 1730 мм", "Требует проверки"),
], [Inches(2.0),Inches(2.8),Inches(1.7)])

doc.add_paragraph("2. Что уже зафиксировано", style="Heading 1")
table(doc,[
    ("Раздел","Данные","Статус"),
    ("Фотоматериалы", "В чате сохранены фотографии ванной комнаты", "Есть"),
    ("Планировочная основа", "Помещение ориентировочно 1740 × 1745 мм", "Предварительно"),
    ("Коммуникации и электрика", "Точные координаты ещё не внесены в реестр", "Требуется обмер"),
], [Inches(1.75),Inches(3.85),Inches(.9)])

doc.add_paragraph("3. Контрольные обмеры для рабочего проекта", style="Heading 1")
for text in [
    "Высота потолка и точные внутренние габариты помещения по чистому полу.",
    "Дверной проём: ширина, высота, толщина стены, направление и сторона открывания.",
    "Окно (если есть): ширина, высота, подоконник от пола и привязки к углам.",
    "Вода и канализация: все выводы — от двух стен и от пола до центра оси.",
    "Вентиляция: размер решётки и привязки к потолку и стенам.",
    "Электрика: щит, розетки, выводы света и кабели — высоты и привязки.",
    "Выступы стояков, коробов и труб; фото каждой стены строго перпендикулярно.",
]:
    p=doc.add_paragraph(style="List Bullet"); p.paragraph_format.space_after=Pt(4); p.add_run(text)

doc.add_paragraph("4. Следующий результат", style="Heading 1")
doc.add_paragraph("После контрольных обмеров будут подготовлены: точный обмерный план, расстановка сантехники и мебели, схема электрики и освещения, а затем раскладка плитки и рабочие чертежи.")
note=doc.add_table(rows=1,cols=1); note.cell(0,0).text="Важно: несоответствие 1745 мм по фактическому замеру и 1730 мм на прежнем плане нужно устранить до разработки мебели и раскладки плитки."; shade(note.cell(0,0),CAUTION); cell_margin(note.cell(0,0),120,140,120,140); set_widths(note,[Inches(6.5)])
footer=s.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT; footer.add_run("Квартира · Ванная · "); field=OxmlElement("w:fldSimple"); field.set(qn("w:instr"),"PAGE"); footer._p.append(field)
OUT.parent.mkdir(parents=True,exist_ok=True); doc.save(OUT); print(OUT)
