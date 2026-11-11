from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


root = Path(__file__).resolve().parents[1]
qa = root / "tmp" / "pdfs" / "klv002_storage_use" / "rendered_qa_r1"
pages = sorted(qa.glob("page-*.png"))
if len(pages) != 16:
    raise SystemExit(f"Expected 16 page images, got {len(pages)}")


def build(items: list[Path], target: Path, columns: int = 2, thumb_w: int = 1000) -> None:
    rendered = []
    for path in items:
        with Image.open(path) as source:
            image = source.convert("RGB")
            ratio = thumb_w / image.width
            rendered.append((path.name, image.resize((thumb_w, int(image.height * ratio)), Image.Resampling.LANCZOS)))
    thumb_h = max(image.height for _, image in rendered)
    rows = (len(rendered) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * thumb_w, rows * (thumb_h + 40)), "white")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=24)
    for index, (name, image) in enumerate(rendered):
        col = index % columns
        row = index // columns
        x = col * thumb_w
        y = row * (thumb_h + 40)
        sheet.paste(image, (x, y + 40))
        draw.text((x + 12, y + 8), name, fill="black", font=font)
    sheet.save(target, quality=92)


build(pages[:8], qa / "contact_01_08.jpg")
build(pages[8:10], qa / "contact_09_10.jpg")
build(pages[10:14], qa / "contact_11_14.jpg")
build(pages[14:16], qa / "contact_15_16.jpg")
print("contact sheets: 4")
