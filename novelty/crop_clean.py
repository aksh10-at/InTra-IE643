"""Crop cleaning: remove other content (text lines, equation pieces, cut-off strokes) from a
figure crop, without ever drawing anything new.

Problem: render_document.clean_crop cuts the chosen box plus 1% padding and only trims empty
margins. Handwriting that sits inside the box or its padding stays in the figure, so the PDF
shows it twice (once as typed text, once inside the picture).

Method (deterministic, uses Surya's own layout of the page):
  1. Find the ink in the padded crop (Otsu threshold, chalkboards inverted first).
  2. Split the ink into connected pieces (strokes joined by a small dilation).
  3. Foreign regions = Surya text / equation / heading / list / header / footer boxes, and
     other Surya figure boxes, that lie mostly OUTSIDE the figure box. Text boxes INSIDE the
     figure box also count when they are wide (a sentence across the box, not a label).
  4. A piece is removed when most of its ink lies in foreign regions (and it is not the
     main drawing), or when it touches the crop edge and lies (almost) entirely outside the figure box
     (a fragment of a neighbour in the padding band).
  5. Safety rule: if more than MAX_REMOVED of the ink would go, the original crop is kept.
Removed pixels are painted white. Then the usual chalkboard inversion, contrast stretch and
whitespace trim run exactly as before.

Measured against the hand-drawn GT boxes (IE802), per description:
  foreign ink   share of the crop's ink that lies outside the GT box of the intended drawing
  drawing kept  ink inside the GT box after cleaning / before (must stay near 100%)
Settings are chosen on the 8 IE802 training pages (dev) only, then fixed for val + test.

Usage (from ie643_final/, no GPU):
  python3 novelty/crop_clean.py tune       # dev pages: try settings, pick one
  python3 novelty/crop_clean.py measure    # val + test with the chosen setting
  python3 novelty/crop_clean.py sheet      # before/after images for every crop
  python3 novelty/crop_clean.py render     # IE802 val/test PDFs with arm B boxes + cleaning
Output: novelty/crop_clean/ (never overwrites anything outside it)
"""
import argparse, json, os, sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageOps, ImageStat

from common import ROOT, VAL, TEST, DEV, R, load_gt, load_intended, page_size, iou, cover
import match_figures as M

OUT = os.path.join(ROOT, "novelty/crop_clean")
TEXTLIKE = {"text", "equation", "heading", "list", "page_header", "page_footer", "caption", "footnote", "other"}
DEFAULT = {"pad": 0.01, "outside": 0.5, "foreign_frac": 0.6, "wide_text": 0.0, "main": 0.4,
           "edge": 0.95, "max_removed": 0.35, "foreign_edge": False}
# edge: a piece touching the crop edge is removed when at least this share of it lies outside
# the figure box (1.01 = rule off). wide_text: a text box inside the figure box counts as
# foreign when it is at least this share of the figure box's width (0 = rule off).
GRID = [dict(DEFAULT, outside=o, foreign_frac=f, wide_text=wt, edge=e)
        for o in (0.5, 0.7) for f in (0.5, 0.7) for wt in (0.0, 0.4) for e in (0.95, 1.01)]
GRID += [dict(g, foreign_edge=True) for g in GRID]  # foreign text removed only where it is cut by the crop edge


# ---- geometry helpers ---------------------------------------------------------------

def px_box(b, size):
    w, h = size
    return [b[0] * w / 1000, b[1] * h / 1000, b[2] * w / 1000, b[3] * h / 1000]


TAGS_ROOT = os.path.join(ROOT, "data")  # structure.py --surya 2.5 points this at the Surya 2.5 tags


def surya_blocks(page):
    """Original Surya layout blocks of the page, boxes in pixels of the processed image."""
    path = os.path.join(TAGS_ROOT, "tags", page + ".json")
    if not os.path.exists(path):
        return []
    t = json.load(open(path))
    size = t["image_size"]
    return [{"type": b["type"], "box": px_box(b["bbox"], size)} for b in t["blocks"]]


def foreign_boxes(blocks, core, p):
    """Surya boxes whose content is not part of this drawing."""
    out = []
    core_area = max(1.0, (core[2] - core[0]) * (core[3] - core[1]))
    for b in blocks:
        inside = cover(b["box"], core)  # share of the block inside the figure box
        if inside <= 0:
            continue
        area = (b["box"][2] - b["box"][0]) * (b["box"][3] - b["box"][1])
        if b["type"] == "figure":
            if inside < p["outside"]:
                out.append(b["box"])  # a neighbouring drawing reaching into the crop
        elif b["type"] in TEXTLIKE:
            if inside < p["outside"]:
                out.append(b["box"])
            elif p["wide_text"] and (b["box"][2] - b["box"][0]) >= p["wide_text"] * (core[2] - core[0]):
                out.append(b["box"])  # a sentence running across a loose figure box, not a label
    return out


# ---- cleaning -----------------------------------------------------------------------

def padded(box, size, pad):
    w, h = size
    return (max(0, int(box[0] - pad * w)), max(0, int(box[1] - pad * h)),
            min(w, int(box[2] + pad * w)), min(h, int(box[3] + pad * h)))


def ink_mask(gray):
    """gray: uint8 array, dark ink on light paper. Returns bool array."""
    thr, _ = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thr = min(max(thr, 60), 200)
    return gray < thr


def clean(page_img, box, blocks, p=DEFAULT):
    """page_img: PIL RGB processed page. box: figure box in pixels.
    Returns (cleaned RGB crop before trimming, info dict with masks in crop coordinates)."""
    size = page_img.size
    P = padded(box, size, p["pad"])
    crop = page_img.crop(P)
    gray = np.array(ImageOps.grayscale(crop))
    dark = gray.mean() < 100
    g = 255 - gray if dark else gray
    ink = ink_mask(g)
    total = int(ink.sum())
    info = {"crop_box": P, "dark": bool(dark), "ink_before": ink, "removed": np.zeros_like(ink),
            "reverted": False, "pieces_removed": 0}
    if total == 0:
        return crop, info
    hh, ww = ink.shape
    # regions in crop coordinates
    def local(b):
        return (max(0, int(b[0] - P[0])), max(0, int(b[1] - P[1])),
                min(ww, int(b[2] - P[0])), min(hh, int(b[3] - P[1])))
    foreign = np.zeros_like(ink)
    for b in foreign_boxes(blocks, box, p):
        x0, y0, x1, y1 = local(b)
        if x1 > x0 and y1 > y0:
            foreign[y0:y1, x0:x1] = True
    core = np.zeros_like(ink)
    x0, y0, x1, y1 = local(box)
    core[y0:y1, x0:x1] = True
    # pieces: strokes joined by a small dilation, labels mapped back to real ink pixels
    joined = cv2.dilate(ink.astype(np.uint8), np.ones((5, 5), np.uint8))
    n, lab = cv2.connectedComponents(joined, connectivity=8)
    lab = np.where(ink, lab, 0)
    removed = np.zeros_like(ink)
    count = 0
    for k in range(1, n):
        piece = lab == k
        m = int(piece.sum())
        if m == 0:
            continue
        if m >= p["main"] * total:
            continue  # the main drawing is never removed
        in_foreign = (piece & foreign).sum() / m
        outside_core = (piece & ~core).sum() / m
        ys, xs = np.nonzero(piece)
        touches = xs.min() == 0 or ys.min() == 0 or xs.max() == ww - 1 or ys.max() == hh - 1
        foreign_hit = in_foreign >= p["foreign_frac"] and (touches or not p.get("foreign_edge"))
        if foreign_hit or (touches and outside_core >= p["edge"]):
            removed |= piece
            count += 1
    share = removed.sum() / total
    if share > p["max_removed"]:
        info.update(reverted=True, removed_share=float(share))
        return crop, info
    arr = np.array(crop)
    # paint removed ink and its immediate halo white (anti-aliased stroke edges)
    # the faint grey edge of a stroke is not "ink" for the threshold, so whiten a band around
    # each removed piece too (but never a kept stroke), or ghost letters stay visible
    halo = cv2.dilate(removed.astype(np.uint8), np.ones((9, 9), np.uint8)).astype(bool)
    keep = cv2.dilate((ink & ~removed).astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    halo &= ~keep
    arr[halo] = 0 if dark else 255
    info.update(removed=removed, pieces_removed=count, removed_share=float(share))
    return Image.fromarray(arr), info


def finish(crop, dark):
    """The renderer's own steps after the cut: inversion, contrast stretch, trim."""
    gray = ImageOps.grayscale(crop)
    if dark or ImageStat.Stat(gray).mean[0] < 100:
        crop = ImageOps.autocontrast(ImageOps.invert(gray), cutoff=1).convert("RGB")
    else:
        crop = ImageOps.autocontrast(crop, cutoff=1)
    return R.trim_whitespace(crop)


# ---- evaluation ---------------------------------------------------------------------

def items(which, tau):
    """(page, desc index, chosen arm-B box px, intended GT box px) for descriptions that
    point at a real GT drawing."""
    gt_all, intended = load_gt(), load_intended()
    pages, source = (DEV, "label") if which == "dev" else (VAL + TEST, "pred")
    _, _, choices, detail = M.evaluate(pages, source, tau, gt_all, intended)
    out = []
    for r in detail:
        page = next(p for p in pages if p.endswith(r["page"]))
        i = int(r["desc"][1:]) - 1
        b = choices[page]["B"][i]
        g = {x["label"]: x["box"] for x in gt_all.get(page, [])}.get(r["gt"])
        if b is not None and g is not None and iou(b, g) > 0:
            out.append((page, i, b, g))
    return out


def score(its, p, images):
    rows = []
    for page, i, b, g in its:
        img = images.setdefault(page, Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB"))
        _, info = clean(img, b, surya_blocks(page), p)
        P = info["crop_box"]
        ink = info["ink_before"]
        after = ink & ~info["removed"]
        hh, ww = ink.shape
        gm = np.zeros_like(ink)
        m = 0.01 * max(img.size)  # GT boxes are hand-drawn; allow a small margin
        x0, y0 = max(0, int(g[0] - m - P[0])), max(0, int(g[1] - m - P[1]))
        x1, y1 = min(ww, int(g[2] + m - P[0])), min(hh, int(g[3] + m - P[1]))
        gm[y0:y1, x0:x1] = True
        fb = (ink & ~gm).sum() / max(1, ink.sum())
        fa = (after & ~gm).sum() / max(1, after.sum())
        kept = (after & gm).sum() / max(1, (ink & gm).sum())
        rows.append({"page": page, "desc": f"D{i + 1}", "foreign_before": fb, "foreign_after": fa,
                     "drawing_kept": kept, "reverted": info["reverted"], "pieces": info["pieces_removed"]})
    return rows


def summary(rows):
    n = len(rows)
    return {"n": n,
            "foreign_before": float(np.mean([r["foreign_before"] for r in rows])),
            "foreign_after": float(np.mean([r["foreign_after"] for r in rows])),
            "drawing_kept_mean": float(np.mean([r["drawing_kept"] for r in rows])),
            "drawing_kept_min": float(np.min([r["drawing_kept"] for r in rows])),
            "crops_below_98pct_kept": sum(r["drawing_kept"] < 0.98 for r in rows),
            "crops_changed": sum(r["pieces"] > 0 for r in rows),
            "reverted": sum(r["reverted"] for r in rows)}


def tau_frozen():
    return json.load(open(os.path.join(ROOT, "novelty/results/choices_dev.json")))["tau"]


def cmd_tune():
    its, images, res = items("dev", tau_frozen()), {}, []
    for p in GRID:
        s = summary(score(its, p, images))
        res.append((p, s))
    # rule: drawing ink must be kept (no crop below 98%), then least foreign ink
    ok = [(p, s) for p, s in res if s["crops_below_98pct_kept"] == 0] or res
    best = min(ok, key=lambda ps: (ps[1]["foreign_after"], -ps[1]["drawing_kept_mean"]))
    os.makedirs(OUT, exist_ok=True)
    json.dump({"chosen": best[0], "grid": [{"params": p, **s} for p, s in res]},
              open(os.path.join(OUT, "tune_dev.json"), "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    lines = ["| outside | foreign_frac | wide_text | edge | foreign only at edge | foreign before | foreign after | drawing kept (mean / min) | crops <98% kept | changed |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for p, s in res:
        lines.append(f"| {p['outside']} | {p['foreign_frac']} | {p['wide_text']} | {p['edge']} | {p['foreign_edge']} | {s['foreign_before']:.3f} | "
                     f"{s['foreign_after']:.3f} | {s['drawing_kept_mean']:.3f} / {s['drawing_kept_min']:.3f} | "
                     f"{s['crops_below_98pct_kept']} | {s['crops_changed']}/{s['n']} |")
    print("\n".join(lines))
    print("chosen:", best[0])
    open(os.path.join(OUT, "tune_dev.md"), "w").write("\n".join(lines) + f"\n\nChosen: {best[0]}\n")


def chosen_params():
    path = os.path.join(OUT, "tune_dev.json")
    if not os.path.exists(path):
        sys.exit("run `tune` first")
    return json.load(open(path))["chosen"]


def cmd_measure():
    p = chosen_params()
    rows = score(items("eval", tau_frozen()), p, {})
    s = summary(rows)
    lines = [f"# Crop cleaning on IE802 val + test (arm B boxes, settings from dev: {p})", "",
             "| measure | before | after |", "|---|---|---|",
             f"| foreign ink share (mean over {s['n']} crops) | {s['foreign_before']:.3f} | {s['foreign_after']:.3f} |",
             f"| drawing ink kept (mean / min) | 1.000 | {s['drawing_kept_mean']:.3f} / {s['drawing_kept_min']:.3f} |",
             f"| crops changed | - | {s['crops_changed']}/{s['n']} |",
             f"| crops kept as original by the safety rule | - | {s['reverted']} |", "",
             "| page | desc | foreign before | foreign after | drawing kept | pieces removed | reverted |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['page'][-3:]} | {r['desc']} | {r['foreign_before']:.3f} | {r['foreign_after']:.3f} | "
                     f"{r['drawing_kept']:.3f} | {r['pieces']} | {r['reverted']} |")
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "measure_eval.md"), "w").write("\n".join(lines) + "\n")
    json.dump({"params": p, "summary": s, "rows": rows}, open(os.path.join(OUT, "measure_eval.json"), "w"),
              indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
    print("\n".join(lines))


def cmd_sheet():
    """Before | after | removed (red) for every IE802 val/test arm-B crop and every IE643/MLT
    val/test crop the current pipeline places."""
    from common import current_pairing, pred_md
    p = chosen_params()
    tau = tau_frozen()
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    other = [x for s in ("val", "test") for x in splits[s] if x.startswith(("ie643_", "mlt_"))]
    out = os.path.join(OUT, "sheets")
    os.makedirs(out, exist_ok=True)
    n_changed = 0
    for page in VAL + TEST + other:
        md = pred_md(page)
        if md is None:
            continue
        c = current_pairing(page, md)
        if not c["texts"]:
            continue
        size = page_size(page)
        if page.startswith("ie802"):
            boxes = M.arm_b(c, size, M.qwen_boxes(page, len(c["texts"])), tau)[0]
        else:
            boxes = M.arm_a(c, size)
        img = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
        blocks = surya_blocks(page)
        for i, b in enumerate(boxes):
            if b is None:
                continue
            raw, info = clean(img, b, blocks, dict(p, foreign_frac=2.0, edge=1.01))  # nothing removed
            new, info2 = clean(img, b, blocks, p)
            if info2["pieces_removed"] == 0 and not info2["reverted"]:
                continue
            n_changed += 1
            before, after = finish(raw, info["dark"]), finish(new, info2["dark"])
            red = raw.copy()
            arr = np.array(red)
            arr[info2["removed"]] = (220, 30, 30)
            red = Image.fromarray(arr)
            panels = [before, after, red]
            hmax = max(x.height for x in panels)
            sheet = Image.new("RGB", (sum(x.width for x in panels) + 40, hmax + 40), "white")
            x = 0
            d = ImageDraw.Draw(sheet)
            for t, im in zip(("before", "after", "removed in red" + (" (REVERTED)" if info2["reverted"] else "")), panels):
                sheet.paste(im, (x, 30))
                d.text((x + 4, 4), t, fill=(0, 0, 0))
                x += im.width + 20
            sheet.thumbnail((1800, 900))
            sheet.save(os.path.join(out, f"{page}_D{i + 1}.jpg"), quality=85)
    print(f"{n_changed} crops changed; sheets in {out}")


def cmd_render():
    """IE802 val/test PDFs with arm B boxes and cleaned crops. Same path as render_arm.py; the
    renderer's clean_crop is swapped for this cleaner while the script runs (the renderer file
    is not edited). Output: novelty/crop_clean/render/<split>/."""
    import render_arm
    p = chosen_params()
    tau = tau_frozen()
    state = {"page": None}
    orig_pf = R.page_figures

    def page_figures(page, data_dir=None):
        state["page"] = page
        return orig_pf(page, data_dir)

    def clean_crop(page_img, bbox, pad=0.01):
        box = px_box(bbox, page_img.size)
        new, info = clean(page_img, box, surya_blocks(state["page"]), dict(p, pad=pad))
        return finish(new, info["dark"])

    R.page_figures, R.clean_crop = page_figures, clean_crop
    base = os.path.join(OUT, "render")
    for split, pages in (("val", VAL), ("test", TEST)):
        data_dir = os.path.join(base, "data")
        render_arm.write_tags(pages, "B", tau, data_dir)
        outline_path = os.path.join(ROOT, f"results/reconstruction/outlines_{split}/ie802_notes.json")
        outline = json.load(open(outline_path))["outline"] if os.path.exists(outline_path) else None
        out_root = os.path.join(base, split)
        os.makedirs(out_root, exist_ok=True)
        r = R.render_unit("ie802_notes", pages, os.path.join(ROOT, f"preds/final_clean_{split}"), out_root,
                          "pdf", outline, run_id="novelty-arm-B-cropclean", data_dir=data_dir)
        print(split, "output:", r["output"], "blocks kept",
              r["preservation"]["blocks"] - r["preservation"]["missing"], "/", r["preservation"]["blocks"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["tune", "measure", "sheet", "render"])
    a = ap.parse_args()
    {"tune": cmd_tune, "measure": cmd_measure, "sheet": cmd_sheet, "render": cmd_render}[a.cmd]()
