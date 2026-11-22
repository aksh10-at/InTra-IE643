"""Complete cut-off drawings: grow the chosen box along the ink that crosses its edge.

Finding (novelty/crop_fix.py diagnostics): after Method B with Surya 2.5 and dup_only grounding,
most remaining bad crops are too SMALL (the box holds 13-45% of the drawing), not too big.
The strokes of the drawing continue past the box edge.

Method (deterministic, page pixels):
  1. Ink mask of the processed page (Otsu, chalkboards inverted), joined by a dilation of
     size K so one drawing is one connected piece.
  2. Every ink piece that has ink inside the chosen box is added to the box, unless the piece
     is huge (bigger than MAX_FACTOR times the box, e.g. a page edge or a whole text column)
     or lies mostly inside a Surya text/equation/heading box that does not touch the chosen box.
  3. If the grown box is more than MAX_FACTOR times the original, keep the original.
Settings (K, MAX_FACTOR) are chosen on the 8 IE802 dev pages, then fixed for val + test.

Usage (from ie643_final/, no GPU):  python3 novelty/grow_box.py
Output: novelty/crop_fix/grow_scores.md, grow_params.json
"""
import json, os
import numpy as np
import cv2
from PIL import Image, ImageOps

from common import ROOT, VAL, TEST, DEV, R, load_gt, load_intended, iou, cover
import match_figures as M
import crop_fix as F

OUT = os.path.join(ROOT, "novelty/crop_fix")
GRID = [{"k": k, "max_factor": f} for k in (5, 9, 15, 25) for f in (1.5, 2.5, 4.0)]
TEXTLIKE = {"text", "equation", "heading", "list", "page_header", "page_footer", "caption", "footnote"}
_cache = {}


def page_pieces(page, k):
    key = (page, k)
    if key not in _cache:
        gray = np.array(ImageOps.grayscale(Image.open(os.path.join(ROOT, "data/processed", page + ".jpg"))))
        if gray.mean() < 100:
            gray = 255 - gray
        thr, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        ink = (gray < min(max(thr, 60), 200)).astype(np.uint8)
        joined = cv2.dilate(ink, np.ones((k, k), np.uint8))
        n, lab, st, _ = cv2.connectedComponentsWithStats(joined, connectivity=8)
        _cache[key] = (lab, st)
    return _cache[key]


def text_boxes(page, tags_root):
    t = json.load(open(os.path.join(tags_root, "tags", page + ".json")))
    w, h = t["image_size"]
    return [[b["bbox"][0] * w / 1000, b["bbox"][1] * h / 1000, b["bbox"][2] * w / 1000, b["bbox"][3] * h / 1000]
            for b in t["blocks"] if b["type"] in TEXTLIKE]


def grow(page, box, p, tags_root):
    lab, st = page_pieces(page, p["k"])
    H, W = lab.shape
    x0, y0, x1, y1 = (max(0, int(box[0])), max(0, int(box[1])), min(W, int(box[2])), min(H, int(box[3])))
    if x1 <= x0 or y1 <= y0:
        return box
    area = (box[2] - box[0]) * (box[3] - box[1])
    ids = np.unique(lab[y0:y1, x0:x1])
    texts = [t for t in text_boxes(page, tags_root) if iou(t, box) == 0]
    out = list(box)
    for i in ids:
        if i == 0:
            continue
        x, y, w, h, _ = st[i]
        pb = [x, y, x + w, y + h]
        if w * h > p["max_factor"] * area or w * h > 0.5 * W * H:
            continue
        if any(cover(pb, t) >= 0.6 for t in texts):
            continue  # a line of text next to the drawing, not part of it
        out = [min(out[0], pb[0]), min(out[1], pb[1]), max(out[2], pb[2]), max(out[3], pb[3])]
    if (out[2] - out[0]) * (out[3] - out[1]) > p["max_factor"] * area:
        return box
    return out


def evaluate(pages, src, p, surya="2.5", grounding="dup_only"):
    orig_pf, orig_lg = R.page_figures, M.load_grounding
    R.page_figures = lambda page, data_dir=None: orig_pf(page, F.TAGS[surya])
    M.load_grounding = F.grounding_for(grounding)
    try:
        gt, inte = load_gt(), load_intended()
        _, _, ch, det = M.evaluate(pages, src, 0.2, gt, inte)
        rows = []
        for r in det:
            page = next(x for x in pages if x.endswith(r["page"]))
            i = int(r["desc"][1:]) - 1
            g = {x["label"]: x["box"] for x in gt[page]}[r["gt"]]
            others = [x["box"] for x in gt[page] if x["label"] != r["gt"]]
            b = ch[page]["B"][i]
            nb = grow(page, b, p, F.TAGS[surya]) if p else b
            v_old, v_new = iou(b, g), iou(nb, g)
            wrong = any(iou(nb, o) > v_new for o in others)
            rows.append({"page": r["page"], "desc": r["desc"], "before": v_old, "after": v_new, "wrong_after": wrong})
        return rows
    finally:
        R.page_figures, M.load_grounding = orig_pf, orig_lg


def summ(rows):
    n = len(rows)
    return {"n": n, "right_box_before": sum(r["before"] >= 0.5 for r in rows), "right_box_after": sum(r["after"] >= 0.5 for r in rows),
            "le_before": sum(1 - r["before"] for r in rows) / n, "le_after": sum(1 - r["after"] for r in rows) / n,
            "worse": sum(r["after"] < r["before"] - 0.05 for r in rows), "better": sum(r["after"] > r["before"] + 0.05 for r in rows),
            "wrong_after": sum(r["wrong_after"] for r in rows)}


def main():
    os.makedirs(OUT, exist_ok=True)
    lines = ["# Growing boxes along the ink (Method B, Surya 2.5, dup_only grounding)", "",
             "## Settings tried on the 8 IE802 dev pages", "",
             "| K | max factor | right box before -> after | mean LE before -> after | better / worse | wrong drawing after |",
             "|---|---|---|---|---|---|"]
    res = []
    for p in GRID:
        s = summ(evaluate(DEV, "label", p))
        res.append((p, s))
        lines.append(f"| {p['k']} | {p['max_factor']} | {s['right_box_before']} -> {s['right_box_after']}/{s['n']} | "
                     f"{s['le_before']:.3f} -> {s['le_after']:.3f} | {s['better']} / {s['worse']} | {s['wrong_after']} |")
    best = min(res, key=lambda ps: (ps[1]["wrong_after"], ps[1]["le_after"], ps[1]["worse"]))[0]
    lines += ["", f"Chosen on dev (fewest wrong drawings, then lowest LE): K = {best['k']}, max factor = {best['max_factor']}", ""]
    rows = evaluate(VAL + TEST, "pred", best)
    s = summ(rows)
    lines += ["## val + test with the chosen setting", "",
              f"- Right box (IoU >= 0.5): {s['right_box_before']} -> {s['right_box_after']} of {s['n']}",
              f"- Mean Localisation Error: {s['le_before']:.3f} -> {s['le_after']:.3f}",
              f"- Boxes better / worse by more than 0.05 IoU: {s['better']} / {s['worse']}. Wrong drawing after: {s['wrong_after']}", "",
              "| page | desc | IoU before | IoU after |", "|---|---|---|---|"]
    for r in rows:
        if abs(r["after"] - r["before"]) > 0.01:
            lines.append(f"| {r['page']} | {r['desc']} | {r['before']:.2f} | {r['after']:.2f}{' WRONG' if r['wrong_after'] else ''} |")
    json.dump(best, open(os.path.join(OUT, "grow_params.json"), "w"))
    open(os.path.join(OUT, "grow_scores.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
