"""Shared helpers for the novelty work: ground truth, Surya figures, current pairing, IoU."""
import csv, glob, json, os, re, sys
from PIL import Image

ROOT = os.environ.get("IE643_ROOT", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "04_reconstruction"))
import render_document as R  # align, merge_split_figures, split_blocks, DIAGRAM

VAL = [f"ie802_notes_page{n:03d}" for n in range(41, 45)]
TEST = [f"ie802_notes_page{n:03d}" for n in range(45, 57)]
DEV = [f"ie802_notes_page{n:03d}" for n in (1, 2, 3, 6, 11, 17, 20, 37)]


def load_gt():
    """page -> list of {label, box:[x0,y0,x1,y1] px}, checked against the processed image size."""
    gt = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "novelty/gt/*.csv"))):
        rows = csv.DictReader(open(path))
        if "image_name" not in (rows.fieldnames or []):
            continue  # not a makesense export (e.g. intended_eval.csv)
        for r in rows:
            page = r["image_name"].rsplit(".", 1)[0]
            x, y, w, h = (int(float(r[k])) for k in ("bbox_x", "bbox_y", "bbox_width", "bbox_height"))
            gt.setdefault(page, []).append({"label": r["label_name"], "box": [x, y, x + w, y + h],
                                            "size": (int(r["image_width"]), int(r["image_height"]))})
    return gt


def page_size(page):
    path = os.path.join(ROOT, "data/processed", page + ".jpg")
    if os.path.exists(path):
        with Image.open(path) as im:
            return im.size
    return tuple(json.load(open(os.path.join(ROOT, "data/tags", page + ".json")))["image_size"])


def to_px(b, size):
    w, h = size
    return [b[0] * w / 1000, b[1] * h / 1000, b[2] * w / 1000, b[3] * h / 1000]


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua > 0 else 0.0


def cover(inner, outer):
    """Share of `inner` that lies inside `outer` (1.0 = fully covered)."""
    ix = max(0, min(inner[2], outer[2]) - max(inner[0], outer[0]))
    iy = max(0, min(inner[3], outer[3]) - max(inner[1], outer[1]))
    a = (inner[2] - inner[0]) * (inner[3] - inner[1])
    return ix * iy / a if a > 0 else 0.0


def descriptions(md):
    blocks = R.split_blocks(md)
    return blocks, [k for k, b in enumerate(blocks) if R.DIAGRAM.match(b)]


def current_pairing(page, md):
    """Exactly what render_document.render_unit does: raw Surya figures, merge, order alignment."""
    blocks, desc_idx = descriptions(md)
    nb = max(len(blocks) - 1, 1)
    raw, _ = R.page_figures(page, os.path.join(ROOT, "data"))
    figs = raw
    if len(figs) > len(desc_idx):
        figs = R.merge_split_figures(figs, max(1, len(desc_idx)))
    pairs = R.align([k / nb for k in desc_idx], [f["pos"] for f in figs])
    texts = [R.DIAGRAM.match(blocks[k]).group(1).strip() for k in desc_idx]
    return {"blocks": blocks, "desc_idx": desc_idx, "texts": texts, "raw": raw, "figs": figs,
            "pairs": pairs, "desc_pos": [k / nb for k in desc_idx]}


def pred_md(page):
    """The fine-tuned model's Markdown for a val or test page (None for training pages)."""
    for split in ("val", "test"):
        p = os.path.join(ROOT, f"preds/final_clean_{split}", page + ".md")
        if os.path.exists(p):
            return open(p).read()
    return None


def label_md(page):
    return open(os.path.join(ROOT, "data/annotations", page + ".md")).read()


def load_intended():
    """page -> {desc 'D1': GT label or None} for the model's descriptions on IE802 val/test pages."""
    out = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "novelty/gt/intended_eval.csv"))):
        out.setdefault(f"ie802_notes_page{r['page']}", {})[r["desc"]] = None if r["gt_label"] == "-" else r["gt_label"]
    return out


def load_grounding(page):
    p = os.path.join(ROOT, "novelty/grounding/all", page + ".json")
    return json.load(open(p)) if os.path.exists(p) else None
