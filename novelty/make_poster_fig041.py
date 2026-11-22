"""Poster figure: page 041, old reading-order crops vs the final pipeline's crops (D2 and D3).

Left: the processed page with the old boxes (red) and the final boxes (green). Right: for each
description, the description text, the crop the old method placed and the crop the final pipeline
places (Surya 2.5 + Method B + shared-box fix + completeness verifier), both cut exactly as the
PDFs cut them (final crops with crop cleaning).

Usage (from ie643_final/):  python3 novelty/make_poster_fig041.py [out.png]
"""
import json, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, R, current_pairing, pred_md, page_size
import match_figures as M
import crop_clean as C

PAGE = sys.argv[2] if len(sys.argv) > 2 else "ie802_notes_page041"
DESCS = [int(x) for x in sys.argv[3].split(",")] if len(sys.argv) > 3 else [1, 2]  # 0-based
BEFORE_LABEL = sys.argv[4] if len(sys.argv) > 4 else "wrong drawing"
BOLD, REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
fb, fr, fs = ImageFont.truetype(BOLD, 46), ImageFont.truetype(REG, 36), ImageFont.truetype(BOLD, 40)


def old_crop(img, box):
    W, H = img.size
    return R.clean_crop(img, [box[0] * 1000 / W, box[1] * 1000 / H, box[2] * 1000 / W, box[3] * 1000 / H])


def new_crop(img, box):
    C.TAGS_ROOT = os.path.join(ROOT, "novelty/surya25/all/data25")
    new, info = C.clean(img, box, C.surya_blocks(PAGE), C.chosen_params())
    return C.finish(new, info["dark"])


def main():
    img = Image.open(os.path.join(ROOT, "data/processed", PAGE + ".jpg")).convert("RGB")
    c = current_pairing(PAGE, pred_md(PAGE))  # old method: Surya 2 boxes, reading order
    old = M.arm_a(c, page_size(PAGE))
    picks = json.load(open(os.path.join(ROOT, "novelty/crop_fix/picks2_val_test.json")))["picks"][PAGE]
    new = {i: picks[str(i)]["box"] for i in DESCS}
    texts = c["texts"]
    # page with boxes
    page = img.copy()
    d = ImageDraw.Draw(page)
    for i in DESCS:
        for box, col, tag in ((old[i], (215, 40, 40), "before"), (new[i], (20, 150, 70), "after")):
            d.rectangle(box, outline=col, width=9)
            d.text((box[0] + 8, box[1] + 6), f"D{i + 1}", fill=col, font=fs)
    ys = [b[1] for i in DESCS for b in (old[i], new[i])] + [b[3] for i in DESCS for b in (old[i], new[i])]
    top, bot = max(0, int(min(ys) - 0.06 * img.height)), min(img.height, int(max(ys) + 0.06 * img.height))
    page = page.crop((0, top, img.width, bot))
    page.thumbnail((900, 1600))
    rows, cell = [], 420
    for i in DESCS:
        a, b = old_crop(img, old[i]), new_crop(img, new[i])
        for x in (a, b):
            x.thumbnail((cell, cell))
        rows.append((i, a, b))
    W = page.width + 60 + 620 + 2 * (cell + 60)
    H = max(page.height + 140, 140 + len(rows) * (cell + 80))
    out = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(out)
    out.paste(page, (20, 120))
    dr.rectangle([20, 120, 20 + page.width, 120 + page.height], outline=(180, 180, 180), width=3)
    dr.text((20, 30), PAGE.replace("_notes", "").replace("_", " ").replace("page", "page "), fill=(20, 40, 35), font=fb)
    x0 = page.width + 60
    dr.text((x0, 30), "Description", fill=(20, 40, 35), font=fb)
    dr.text((x0 + 620, 30), "Before (old)", fill=(215, 40, 40), font=fb)
    dr.text((x0 + 620 + cell + 60, 30), "After (ours)", fill=(20, 150, 70), font=fb)
    y = 120
    for i, a, b in rows:
        desc = texts[i].replace("$", "")
        dr.text((x0, y), f"D{i + 1}", fill=(20, 40, 35), font=fb)
        dr.multiline_text((x0, y + 60), "\n".join(textwrap.wrap(desc, 30)[:6]), fill=(60, 60, 60), font=fr, spacing=6)
        for k, (im, col, lab) in enumerate(((a, (215, 40, 40), BEFORE_LABEL), (b, (20, 150, 70), "right drawing"))):
            x = x0 + 620 + k * (cell + 60)
            out.paste(im, (x, y + 50))
            dr.rectangle([x - 2, y + 48, x + im.width + 2, y + 52 + im.height], outline=col, width=5)
            dr.text((x, y), lab, fill=col, font=fs)
        y += cell + 80
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "novelty/results/page041_before_after.png")
    out.save(dest, dpi=(200, 200))
    print(dest, out.size, "old boxes", [old[i] for i in DESCS], "new", [new[i] for i in DESCS])


if __name__ == "__main__":
    main()
