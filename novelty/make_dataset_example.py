"""Poster figure: one dataset example, the original page next to its ground-truth Markdown label.

Usage (from ie643_final/):  python3 novelty/make_dataset_example.py [page] [out.png]
"""
import os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
page = sys.argv[1] if len(sys.argv) > 1 else "ie643_lec03_page004"
dest = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "novelty/poster/figures/dataset_example.png")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
fm, fb = ImageFont.truetype(MONO, 27), ImageFont.truetype(BOLD, 40)

img = Image.open(os.path.join(ROOT, "data/raw_scans", page + ".jpg")).convert("RGB")
img.thumbnail((900, 1000))
label = open(os.path.join(ROOT, "data/annotations", page + ".md")).read().strip()
lines = []
for para in label.split("\n"):
    lines += textwrap.wrap(para, 58) or [""]
lines = lines[:34]
line_h = 33
text_w = 58 * 17 + 60
H = max(img.height, len(lines) * line_h + 40) + 90
W = img.width + text_w + 60
out = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(out)
d.text((10, 10), "Input: handwritten page", fill=(20, 40, 90), font=fb)
d.text((img.width + 50, 10), "Ground-truth label (Markdown + LaTeX)", fill=(20, 40, 90), font=fb)
out.paste(img, (10, 80))
x0, y0 = img.width + 40, 80
d.rectangle([x0, y0, W - 10, y0 + len(lines) * line_h + 30], fill=(247, 247, 247), outline=(170, 170, 170), width=3)
in_block = False
for k, ln in enumerate(lines):
    if ln.startswith("[Diagram") or ln.startswith("$$"):
        in_block = True
    elif not ln:
        in_block = False
    colour = (25, 25, 25)
    d.text((x0 + 18, y0 + 14 + k * line_h), ln, fill=colour, font=fm)
out.save(dest, dpi=(200, 200))
print(dest, out.size)
