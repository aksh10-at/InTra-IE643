"""Poster figure: page 047 source detail, old PDF page, new (arm B) PDF page, side by side."""
import os, sys, fitz
from PIL import Image, ImageDraw, ImageFont
R = os.environ.get("IE643_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BOLD, REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
f, fs = ImageFont.truetype(BOLD, 44), ImageFont.truetype(REG, 34)

TIGHT = "--tight" in sys.argv  # crop each PDF page to its figures (for the 2-page report)


def pdf_page(path, n, zoom=3):
    page = fitz.open(path)[n]
    clip = None
    if TIGHT:
        rects = [fitz.Rect(i["bbox"]) for i in page.get_image_info()]
        if rects:
            r = rects[0]
            for x in rects[1:]:
                r |= x
            clip = fitz.Rect(page.rect.x0 + 40, r.y0 - 12, page.rect.x1 - 40, min(page.rect.y1, r.y1 + 34))
    p = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), clip=clip)
    return Image.frombytes("RGB", (p.width, p.height), p.samples)

old = pdf_page(os.path.join(R, "out/reconstruction_test/outlined/ie802_notes/ie802_notes.pdf"), 3)
new = pdf_page(os.path.join(R, "novelty/render_B/test/ie802_notes/ie802_notes.pdf"), 3)
src = Image.open(os.path.join(R, "data/processed/ie802_notes_page047.jpg")).convert("RGB").crop((300, 620, 1420, 1000))
src = src.resize((old.width, round(src.height * old.width / src.width)))
cols = [(src, "Notebook page 047 (detail)", "left sketch = convex set, right = \"can't chop off\""),
        (old, "Before: pairing by reading order", "Surya reads the right sketch first, captions swap"),
        (new, "After: Surya + Qwen grounding + Hungarian", "each caption gets its own sketch")]
top, gap = 150, 20
H = top + old.height + 20
out = Image.new("RGB", (sum(c[0].width for c in cols) + gap * 4, H), "white")
d = ImageDraw.Draw(out)
x = gap
for img, title, sub in cols:
    y = top + (old.height - img.height) // 2
    out.paste(img, (x, y))
    d.rectangle([x, y, x + img.width - 1, y + img.height - 1], outline=(190, 190, 190), width=3)
    d.text((x, 20), title, fill=(20, 40, 35), font=f)
    d.text((x, 80), sub, fill=(80, 80, 80), font=fs)
    x += img.width + gap
args = [a for a in sys.argv[1:] if a != "--tight"]
dest = args[0] if args else os.path.join(R, "novelty/results/page047_before_after.png")
out.save(dest, dpi=(200, 200))
print(dest, out.size)
