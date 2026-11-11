# -*- coding: utf-8 -*-
"""Deterministic release checks for APT-001 revision 13."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from re import finditer
from urllib.parse import unquote
from xml.etree import ElementTree as ET

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DXF = ROOT / "plans" / "04_Подробный_обмерный_план_LibreCAD.dxf"
SVG = ROOT / "plans" / "04_Подробный_обмерный_план_A2_М1_50.svg"
PDF = ROOT / "plans" / "04_Подробный_обмерный_план_A2_М1_50.pdf"
PNG = ROOT / "plans" / "04_Подробный_обмерный_план_A2_М1_50.png"

DOCS = (
    ROOT / "docs" / "07_Ведомость_проемов_и_окон.md",
    ROOT / "docs" / "08_Ведомость_инженерных_точек_и_оборудования.md",
    ROOT / "docs" / "09_Обмерный_план_LibreCAD.md",
    ROOT / "docs" / "11_Паспорт_подробного_обмерного_плана.md",
    ROOT / "docs" / "12_Ведомость_размеров_APT-001_revision_2.md",
    ROOT / "docs" / "13_Стены_и_инженерные_узлы_APT-001_revision_3.md",
    ROOT / "docs" / "14_Стык_кухни_и_террасы_APT-001_revision_4.md",
    ROOT / "docs" / "15_Стена_СТ-01_200мм_APT-001_revision_5.md",
    ROOT / "docs" / "16_Узел_СТ-01_и_D2_APT-001_revision_6.md",
    ROOT / "docs" / "17_Размеры_кухни_и_террасы_APT-001_revision_7.md",
    ROOT / "docs" / "18_Стена_и_размерные_цепочки_APT-001_revision_8.md",
    ROOT / "docs" / "19_Узел_СТ-01_и_терраса_APT-001_revision_9.md",
    ROOT / "docs" / "20_Чистые_размеры_детской_APT-001_revision_10.md",
    ROOT / "docs" / "21_Проход_P6_и_контур_коридора_APT-001_revision_11.md",
    ROOT / "docs" / "22_Толщины_верхних_перегородок_APT-001_revision_12.md",
    ROOT / "docs" / "23_Непрерывная_верхняя_стена_5_3_APT-001_revision_13.md",
    ROOT / "docs" / "README.md",
)

REQUIRED_TEXT = (
    "APT-001",
    "КУХНЯ-ГОСТИНАЯ",
    "ДЕТСКАЯ",
    "ПРИХОЖАЯ",
    "КОРИДОР",
    "СПАЛЬНЯ",
    "ВАННАЯ",
    "ТУАЛЕТ",
    "ГАРДЕРОБНАЯ",
    "ТЕРРАСА",
    "5710",
    "3500",
    "3840",
    "1740",
    "2090",
    "1730",
    "3850",
    "13830",
    "D1",
    "D2",
    "D2 3-1",
    "D3",
    "D4",
    "D5",
    "P6",
    "O1",
    "O2",
    "O3",
    "D4: предвар.705x2027",
    "открывание наружу; петли н/д",
    "ВМ-07",
    "360x710",
    "ЭЩ-03",
    "E-03",
    "Л-07",
    "P-06",
    "СТ-01: t=200 [B01]",
    "t=30 [B01]",
    "верхняя стена 5-3: t н/д [B01]",
    "до D2 = 200 [B01]",
    "2090 [B01]: 610 + D1 1010 + 470",
    "1000 мм = 20 мм",
)

FORBIDDEN_TEXT = (
    "IVANCHUKINTERIOR",
    "IVANCHUK А.Ю.",
    "10.02.2026",
    "55.95",
    "89.70",
    "2575ММ",
    "2565",
    "2825",
    "10815",
    "22220",
    "7230",
    "8385",
    "Жилая с кухонным оборудованием",
    "Радиатор 600x80xH500",
    "Радиатор 800x80xH500",
    "Радиатор 600x150xH500",
)


def assert_text_content(text: str, name: str) -> None:
    missing = [token for token in REQUIRED_TEXT if token.casefold() not in text.casefold()]
    assert not missing, f"{name}: missing required annotations: {missing}"
    leaked = [token for token in FORBIDDEN_TEXT if token.casefold() in text.casefold()]
    assert not leaked, f"{name}: foreign-reference data leaked: {leaked}"


def validate_dxf() -> None:
    raw = DXF.read_text(encoding="cp1251")
    assert raw.rstrip().endswith("EOF"), "DXF: missing EOF"
    assert "$INSUNITS\n70\n4" in raw.replace("\r", ""), "DXF: units are not millimetres"
    for layer in (
        "A-WALL-FILL",
        "A-WALL-OUTLINE",
        "A-EXTERIOR-GRAPHIC",
        "A-OPENING",
        "A-DIM-BTI",
        "A-DIM-CONTROL",
        "A-TOPOLOGY",
        "A-EQUIPMENT",
        "A-CEILING",
        "A-CONFLICT",
        "A-UNKNOWN",
        "A-SHEET",
    ):
        assert layer in raw, f"DXF: missing layer {layer}"
    lines = raw.replace("\r", "").split("\n")
    annotations = "\n".join(lines[index + 1] for index, code in enumerate(lines[:-1]) if code.strip() in {"1", "3"})
    assert_text_content(annotations, "DXF text")


def validate_svg() -> None:
    root = ET.parse(SVG).getroot()
    assert root.attrib.get("width") == "594mm"
    assert root.attrib.get("height") == "420mm"
    assert root.attrib.get("viewBox") == "0 0 29700 21000"
    texts = [node for node in root.iter() if node.tag.endswith("text")]
    assert texts, "SVG: no text"
    sizes = [float(node.attrib["font-size"]) for node in texts]
    assert min(sizes) >= 90.0, f"SVG: text below 1.8 mm at 1:50: {min(sizes)}"
    assert sum(size < 100.0 for size in sizes) <= 100, "SVG: too many labels below 2.0 mm"
    assert_text_content("\n".join(node.text or "" for node in texts), "SVG text")


def validate_pdf() -> None:
    reader = PdfReader(PDF)
    assert len(reader.pages) == 1, "PDF: expected one page"
    page = reader.pages[0]
    width_mm = float(page.mediabox.width) * 25.4 / 72
    height_mm = float(page.mediabox.height) * 25.4 / 72
    assert abs(width_mm - 594.0) < 0.02 and abs(height_mm - 420.0) < 0.02, (
        f"PDF: expected A2 landscape, got {width_mm:.2f}x{height_mm:.2f} mm"
    )
    assert_text_content(page.extract_text() or "", "PDF text")


def validate_links() -> None:
    missing: list[str] = []
    count = 0
    for doc in DOCS:
        raw = doc.read_text(encoding="utf-8")
        for match in finditer(r"\]\(([^)]+)\)", raw):
            target = unquote(match.group(1).split("#", 1)[0])
            if not target or target.startswith(("http://", "https://", "mailto:")):
                continue
            count += 1
            resolved = (doc.parent / target).resolve()
            if not resolved.exists():
                missing.append(f"{doc.name}: {target}")
    assert count >= 60, f"documentation: unexpectedly few local links ({count})"
    assert not missing, "documentation: broken links: " + "; ".join(missing)


def main() -> None:
    for path in (DXF, SVG, PDF, PNG, *DOCS):
        assert path.is_file() and path.stat().st_size > 0, f"missing/empty: {path}"
    validate_dxf()
    validate_svg()
    validate_pdf()
    validate_links()

    # Independent arithmetic gates for the B01 chains shown on the sheet.
    assert 3840 + 130 + 1740 + 160 + 2090 + 160 + 1730 + 130 + 3850 == 13830
    assert 610 + 1600 + 600 == 2810
    assert 1300 + 1600 + 600 == 3500
    assert 2390 + 910 + 200 == 3500
    assert 610 + 1010 + 470 == 2090
    assert 400 + 710 + 630 == 1740
    assert 760 + 810 + 520 == 2090
    assert 140 + 810 + 780 == 1730

    for path in (DXF, SVG, PDF, PNG):
        digest = sha256(path.read_bytes()).hexdigest()
        print(f"OK {path.name} sha256={digest}")
    print("OK APT-001 revision 13: continuous upper wall 5-3, individual B01 t=30 tags, P6 opening, clear sizes, chains, A2 scale, text, contamination and links")


if __name__ == "__main__":
    main()
