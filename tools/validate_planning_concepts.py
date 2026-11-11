# -*- coding: utf-8 -*-
"""Release checks for the PLN-001 A3 functional planning concept sheet."""

from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "plans" / "05_Планировочные_концепции_A3_черновик.pdf"
PNG = ROOT / "plans" / "05_Планировочные_концепции_A3_черновик.png"


def main() -> None:
    assert PDF.is_file() and PDF.stat().st_size > 0, "missing planning PDF"
    assert PNG.is_file() and PNG.stat().st_size > 0, "missing planning PNG"
    reader = PdfReader(PDF)
    assert len(reader.pages) == 1, "expected exactly one A3 page"
    page = reader.pages[0]
    width_mm = float(page.mediabox.width) * 25.4 / 72
    height_mm = float(page.mediabox.height) * 25.4 / 72
    assert abs(width_mm - 420.0) < 0.02 and abs(height_mm - 297.0) < 0.02, (width_mm, height_mm)
    text = page.extract_text() or ""
    # Do not assert full Russian labels from a text extractor: embedded TrueType
    # glyph mapping is renderer-dependent.  Stable IDs prove the intended sheet.
    for required in ("PLN-001", "APT-001"):
        assert required in text, f"missing text: {required}"
    source = (ROOT / "tools" / "build_planning_concepts.py").read_text(encoding="utf-8")
    for required in ("РАБОТА 1", "один стол 1200-1400×700", "утверждаются на G1"):
        assert required in source, f"missing approved planning rule: {required}"
    for prohibited in ("ДМИТРИЙ: ГОСТИНАЯ", "ТУМБА + ЭКРАН", "два рабочих места в кухне-гостиной"):
        assert prohibited not in source, f"obsolete two-workplace kitchen-living rule: {prohibited}"
    print(f"OK PLN-001 A3 1 page {width_mm:.2f}x{height_mm:.2f} mm")


if __name__ == "__main__":
    main()
