"""Four-panel diagnostic for figure placement on IE802 val/test pages (no GPU needed).

For every page with drawings it draws one image:
  1. the processed page with ground-truth boxes (green, G:D1..) and Surya figure boxes (orange, b3..)
  2. the model's [Diagram] lines D1..Dn and the box each one was paired with (the current
     order-based matching, recomputed exactly as render_document.py does it)
  3. the crop that was placed for each description, with its hand grade
  4. the PDF page where that crop landed, with its position outlined

It also writes figure_table.csv: one row per placed figure with IoU against every GT box.

Usage (from ie643_final/):  python3 novelty/diagnose_figures.py --out novelty/diagnostic
"""
import argparse, csv, json, os, re, textwrap
import fitz
from PIL import Image, ImageDraw, ImageFont

from common import ROOT, VAL, TEST, R, load_gt, page_size, to_px, iou, cover, current_pairing, pred_md

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
H = 1100  # panel height in pixels


def font(size, bold=False):
    try:
        return ImageFont.truetype(BOLD if bold else FONT, size)
    except OSError:
        return ImageFont.load_default()


def grades():
    g = {}
    for s in ("val", "test"):
        p = os.path.join(ROOT, f"results/crop_review/{s}_grades.json")
        if os.path.exists(p):
            for k, v in json.load(open(p)).items():
                g[os.path.basename(k)] = v
    return g


def pdf_positions():
    """crop file name -> (split, pdf page number, rect in pt) for the IE802 documents."""
    pos = {}
    for s in ("val", "test"):
        base = os.path.join(ROOT, f"out/reconstruction_{s}/outlined/ie802_notes/ie802_notes")
        if not os.path.exists(base + ".pdf"):
            continue
        names = re.findall(r"figures/([^)]+\.png)", open(base + ".md").read())
        doc = fitz.open(base + ".pdf")
        rects = [(pno, info["bbox"]) for pno, page in enumerate(doc) for info in page.get_image_info()]
        if len(rects) != len(names):
            print(f"warning: {s}: {len(rects)} images in PDF but {len(names)} in Markdown; PDF panel skipped")
            continue
        for n, (pno, bbox) in zip(names, rects):
            pos[n] = (s, pno, bbox)
    return pos


def pdf_snapshot(split, pno, bbox, height):
    doc = fitz.open(os.path.join(ROOT, f"out/reconstruction_{split}/outlined/ie802_notes/ie802_notes.pdf"))
    page = doc[pno]
    zoom = height / page.rect.height
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = (v * zoom for v in bbox)
    d.rectangle([x0 - 4, y0 - 4, x1 + 4, y1 + 4], outline=(220, 30, 30), width=4)
    return img


def crop_name(page, fig):
    return f"{page}_{fig['block'].replace('+', '-')}.png"


def wrap(text, width):
    return textwrap.wrap(text, width) or [""]


def draw_page(page, c, gt, size, scale):
    img = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
    img = img.resize((int(size[0] * scale), int(size[1] * scale)))
    d = ImageDraw.Draw(img)
    f = font(18, True)
    for g in gt:
        b = [v * scale for v in g["box"]]
        d.rectangle(b, outline=(0, 150, 60), width=4)
        d.text((b[0] + 4, b[3] - 22), "G:" + g["label"], fill=(0, 120, 50), font=f)
    for fig in c["raw"]:
        b = [v * scale for v in to_px(fig["bbox"], size)]
        d.rectangle(b, outline=(240, 130, 0), width=3)
        d.text((b[0] + 4, b[1] + 2), fig["block"], fill=(210, 100, 0), font=f)
    for fig in c["figs"]:  # merged boxes only
        if "+" in fig["block"]:
            b = [v * scale for v in to_px(fig["bbox"], size)]
            d.rectangle(b, outline=(200, 0, 160), width=3)
            d.text((b[0] + 4, b[1] + 22), "merged " + fig["block"], fill=(170, 0, 140), font=f)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "novelty/diagnostic"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    gt_all, grade, where = load_gt(), grades(), pdf_positions()
    rows = []
    for page in VAL + TEST:
        md = pred_md(page)
        c = current_pairing(page, md)
        gt = gt_all.get(page, [])
        if not c["texts"] and not gt:
            continue
        size = page_size(page)
        scale = H / size[1]
        p1 = draw_page(page, c, gt, size, scale)

        # rows for the table and the right-hand panels
        paired = {i: c["figs"][j] for i, j in c["pairs"]}
        items = []
        for i, text in enumerate(c["texts"]):
            fig = paired.get(i)
            row = {"split": "val" if page in VAL else "test", "page": page[-3:], "desc": f"D{i + 1}",
                   "description": text, "box": fig["block"] if fig else "", "grade": "", "best_gt": "",
                   "best_iou": "", "ious": ""}
            if fig:
                bp = to_px(fig["bbox"], size)
                ious = {g["label"]: iou(bp, g["box"]) for g in gt}
                if ious:
                    best = max(ious, key=ious.get)
                    row.update(best_gt=best, best_iou=f"{ious[best]:.2f}")
                row["ious"] = " ".join(f"{k}:{v:.2f}" for k, v in ious.items())
                row["grade"] = grade.get(crop_name(page, fig), "")
            rows.append(row)
            items.append((row, fig))

        # panel 2: descriptions and pairing
        w2 = 560
        p2 = Image.new("RGB", (w2, H), "white")
        d = ImageDraw.Draw(p2)
        y = 10
        d.text((10, y), f"{page}  ({'val' if page in VAL else 'test'})", fill="black", font=font(22, True)); y += 34
        d.text((10, y), f"model [Diagram] lines: {len(c['texts'])}   label drawings: "
                        f"{sum(g['label'] != 'X' for g in gt)}   Surya figures: {len(c['raw'])}"
                        f"{' -> merged to ' + str(len(c['figs'])) if len(c['figs']) != len(c['raw']) else ''}",
               fill="black", font=font(15)); y += 30
        for row, fig in items:
            colour = {"correct": (0, 120, 50), "partial": (200, 120, 0), "wrong": (200, 0, 0),
                      "not_drawing": (130, 0, 130)}.get(row["grade"], (60, 60, 60))
            head = f"{row['desc']} -> {row['box'] or 'no crop'}   [{row['grade'] or 'ungraded'}]"
            d.text((10, y), head, fill=colour, font=font(18, True)); y += 24
            for line in wrap(row["description"], 62)[:3]:
                d.text((20, y), line, fill="black", font=font(14)); y += 18
            if row["ious"]:
                d.text((20, y), "IoU with GT: " + row["ious"], fill=(90, 90, 90), font=font(13)); y += 18
            y += 10

        # panel 3: crops as placed; panel 4: PDF page of the first crop on this page
        w3 = 360
        p3 = Image.new("RGB", (w3, H), "white")
        d = ImageDraw.Draw(p3)
        page_img = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
        y, slot = 10, max(120, (H - 20) // max(1, len(items))) - 10
        for row, fig in items:
            d.text((10, y), row["desc"], fill="black", font=font(16, True))
            if fig:
                crop = R.clean_crop(page_img, fig["bbox"])
                crop.thumbnail((w3 - 60, slot - 6))
                p3.paste(crop, (50, y))
                d.rectangle([50, y, 50 + crop.width, y + crop.height], outline=(180, 180, 180))
            y += slot + 10
        snaps = [where[crop_name(page, f)] for _, f in items if f and crop_name(page, f) in where]
        p4 = pdf_snapshot(*snaps[0], H) if snaps else Image.new("RGB", (400, H), "white")

        panel = Image.new("RGB", (p1.width + w2 + w3 + p4.width + 30, H + 40), (235, 235, 235))
        x = 0
        hdr = ImageDraw.Draw(panel)
        for img, title in ((p1, "1. page: GT green, Surya orange, merged purple"), (p2, "2. Markdown [Diagram] -> box"),
                           (p3, "3. crop placed"), (p4, "4. PDF page (first crop outlined)")):
            panel.paste(img, (x, 40))
            hdr.text((x + 6, 10), title, fill="black", font=font(18, True))
            x += img.width + 10
        panel.save(os.path.join(a.out, f"{page}.jpg"), quality=88)

    with open(os.path.join(a.out, "figure_table.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} placed descriptions; panels and figure_table.csv in {a.out}")


if __name__ == "__main__":
    main()
