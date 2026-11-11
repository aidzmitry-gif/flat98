from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "02_Туалет_паспорт_обмеров.docx"

BLUE = "2E74B5"
DARK = "1F4D78"
HEADER_FILL = "E8EEF5"
CAUTION_FILL = "FFF4CE"

def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)

def set_cell_margins(cell, top=80, start=120, bottom=80, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{side}"))
        if node is None:
            node = OxmlElement(f"w:{side}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")

def set_table_widths(table, widths):
    table.autofit = False
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = width
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:w"), str(int(width.inches * 1440)))
            tc_w.set(qn("w:type"), "dxa")

def style_table(table, widths):
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table.style = "Table Grid"
    set_table_widths(table, widths)
    for row_i, row in enumerate(table.rows):
        for cell in row.cells:
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                for run in paragraph.runs:
                    run.font.name = "Calibri"
                    run._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
                    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
                    run.font.size = Pt(10)
            if row_i == 0:
                set_cell_shading(cell, HEADER_FILL)
                for run in cell.paragraphs[0].runs:
                    run.bold = True

def add_heading(doc, text, level):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.keep_with_next = True
    run = p.add_run(text)
    return p

def add_table(doc, rows, widths):
    table = doc.add_table(rows=1, cols=len(rows[0]))
    header = table.rows[0].cells
    for cell, value in zip(header, rows[0]):
        cell.text = value
    for values in rows[1:]:
        cells = table.add_row().cells
        for cell, value in zip(cells, values):
            cell.text = value
    style_table(table, widths)
    return table

def set_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    paragraph.add_run("Квартира · Туалет · ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)

doc = Document()
section = doc.sections[0]
section.top_margin = Inches(1)
section.bottom_margin = Inches(1)
section.left_margin = Inches(1)
section.right_margin = Inches(1)
section.header_distance = Inches(0.492)
section.footer_distance = Inches(0.492)

normal = doc.styles["Normal"]
normal.font.name = "Calibri"
normal._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.25

for name, size, color, before, after in [
    ("Heading 1", 16, BLUE, 18, 10),
    ("Heading 2", 13, BLUE, 14, 7),
    ("Heading 3", 12, DARK, 10, 5),
]:
    st = doc.styles[name]
    st.font.name = "Calibri"
    st._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
    st._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
    st.font.size = Pt(size)
    st.font.color.rgb = RGBColor.from_string(color)
    st.paragraph_format.space_before = Pt(before)
    st.paragraph_format.space_after = Pt(after)

title = doc.add_paragraph()
title.paragraph_format.space_after = Pt(3)
run = title.add_run("Паспорт обмеров — туалет")
run.font.name = "Calibri"
run._element.rPr.rFonts.set(qn("w:ascii"), "Calibri")
run._element.rPr.rFonts.set(qn("w:hAnsi"), "Calibri")
run.font.size = Pt(22)
run.bold = True
run.font.color.rgb = RGBColor.from_string(DARK)

meta = doc.add_paragraph()
meta.paragraph_format.space_after = Pt(12)
meta_run = meta.add_run("Проект: ремонт квартиры  |  Актуально на 26.07.2026  |  Версия 0.1")
meta_run.italic = True
meta_run.font.color.rgb = RGBColor(89, 89, 89)

p = doc.add_paragraph()
p.add_run("Назначение. ").bold = True
p.add_run("Предварительная планировка туалета. До заказа мебели, дверей и материалов обязательна перепроверка всех строк со статусом «предварительно» или «требует уточнения».")

add_heading(doc, "1. Исходные параметры", 1)
add_table(doc, [
    ("Параметр", "Значение", "Статус"),
    ("Высота потолка", "2617 мм от чистого пола", "Подтверждено"),
    ("Дверь", "Открывание наружу", "Подтверждено"),
    ("Сторона петель", "Не определена", "Требует уточнения"),
    ("Дверной проём", "705 × 2027 мм", "Предварительно"),
    ("Размер помещения", "2093 × 1739 мм", "Требует контрольного замера"),
], [Inches(1.8), Inches(3.15), Inches(1.55)])

add_heading(doc, "2. Сантехника и коммуникации", 1)
add_table(doc, [
    ("Элемент", "Привязка", "Статус"),
    ("Ось унитаза", "550 мм от задней стены; 1621 мм от правой стены", "Подтверждено"),
    ("Проход перед унитазом", "824 мм от оси до передней стены", "Подтверждено"),
    ("Кран воды", "620 мм от левой стены; 200 мм от пола (до центра)", "Подтверждено"),
    ("Канализация унитаза", "460–470 мм от левой стены; 80 мм от пола (до центра оси)", "Подтверждено"),
    ("Канализация раковины", "240 мм от пола до центра трубы", "Подтверждено"),
], [Inches(1.65), Inches(4.4), Inches(1.0)])

add_heading(doc, "3. Электрика и вентиляция", 1)
add_table(doc, [
    ("Элемент", "Привязка", "Статус"),
    ("Кабель", "1850 мм от пола; 1030 мм от правой стены; 250 мм от стены, где начинается щит", "Подтверждено"),
    ("Расстояние кабеля до потолка", "Ранее записано 884 мм; по высоте потолка расчётно около 767 мм", "Требует контрольного замера"),
    ("Электрощит", "Нижний край 1150 мм от пола; ширина около 390 мм; высота около 600 мм", "Предварительно"),
    ("Электрощит: отступы", "По 165 мм до углов с обеих сторон", "Требует проверки привязки"),
    ("Вентиляционная решётка", "260 × 260 мм; 40 мм от потолка; 80 мм от левой стены", "Подтверждено"),
], [Inches(1.65), Inches(4.4), Inches(1.0)])

add_heading(doc, "4. Контрольные замеры перед рабочими чертежами", 1)
for item in [
    "Определить сторону петель двери.",
    "Перемерить ширину, высоту и выступ электрощита; уточнить привязку отступов 165 мм.",
    "Перемерить расстояние кабеля до потолка.",
    "Подтвердить внутренние габариты туалета и дверной проём.",
]:
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    p.add_run(item)

note = doc.add_table(rows=1, cols=1)
note.cell(0,0).text = "Важно: документ фиксирует данные из чата и подходит для эскизной планировки. Он не заменяет очный обмер перед заказом мебели и выполнением работ."
set_cell_shading(note.cell(0,0), CAUTION_FILL)
set_cell_margins(note.cell(0,0), 120, 140, 120, 140)
set_table_widths(note, [Inches(6.5)])

footer = section.footer.paragraphs[0]
set_page_number(footer)

OUT.parent.mkdir(parents=True, exist_ok=True)
doc.save(OUT)
print(OUT)
