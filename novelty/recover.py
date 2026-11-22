"""Recover drawings that the notes never describe.

Qwen sometimes writes no [Diagram] line for a drawing (IE802: 042 D4, 046 D2, 047 X, 056 X), so
the PDF has no figure for it. Surya 2.5 often still boxes it. Here every Surya 2.5 figure box that
no chosen crop already covers is a candidate. The base Qwen (4-bit, no adapter) sees the crop and
answers "is this a hand-drawn sketch, not only text or equations?". P(yes) >= T keeps it.
T is chosen on the 8 IE802 dev pages, then fixed.

Scored on the GT pages: a GT drawing counts as "missing" when no chosen crop overlaps it
(IoU < 0.3). recovered = a kept candidate has IoU >= 0.3 with a missing GT drawing.
false = a kept candidate overlaps no GT drawing (IoU < 0.1 with all).

Usage (GPU machine, from ie643_final/):
  python3 novelty/recover.py run     # GPU, 1-2 minutes
  python3 novelty/recover.py pick    # choose T on dev, write recovered_val_test.json
"""
import argparse, json, os
from PIL import Image

from common import ROOT, VAL, TEST, DEV, R, load_gt, load_intended, iou, cover, page_size, current_pairing, pred_md
import match_figures as M
import crop_fix as F

OUT = os.path.join(ROOT, "novelty/crop_fix")
TAGS25 = F.TAGS["2.5"]
THRESHOLDS = [0.3, 0.5, 0.7, 0.9]
MIN_AREA = 0.005  # of the page
SKETCH = ('This image was cut from a page of handwritten lecture notes. Does it show a hand-drawn sketch, '
          'diagram, graph or plot (not only handwritten text or equations)? Answer with one word: Yes or No.')


def chosen_boxes():
    """page -> boxes the final pipeline already uses."""
    out = {}
    orig_pf, orig_lg = R.page_figures, M.load_grounding
    R.page_figures = lambda page, data_dir=None: orig_pf(page, TAGS25)
    M.load_grounding = F.grounding_for("dup_only")
    try:
        _, _, ch, _ = M.evaluate(DEV, "label", 0.2, load_gt(), load_intended())
        for p, v in ch.items():
            out[p] = [b for b in v["B"] if b]
    finally:
        R.page_figures, M.load_grounding = orig_pf, orig_lg
    picks = json.load(open(os.path.join(OUT, "picks2_val_test.json")))["picks"]
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    for p in splits["val"] + splits["test"]:
        out[p] = [d["box"] for d in picks.get(p, {}).values() if d["box"]]
    return out


def candidates():
    used = chosen_boxes()
    items = []
    for page, boxes in used.items():
        figs, size = R.page_figures(page, TAGS25)
        W, H = page_size(page)
        for f in figs:
            b = [f["bbox"][0] * W / 1000, f["bbox"][1] * H / 1000, f["bbox"][2] * W / 1000, f["bbox"][3] * H / 1000]
            if (b[2] - b[0]) * (b[3] - b[1]) < MIN_AREA * W * H:
                continue
            if any(iou(b, u) >= 0.3 or cover(b, u) >= 0.5 for u in boxes):
                continue
            items.append({"page": page, "block": f["block"], "box": [round(v) for v in b]})
    return items, used


def run():
    import torch
    from ground_qwen import load_model
    model, processor = load_model()
    tok = processor.tokenizer
    yes_id, no_id = tok.encode("Yes", add_special_tokens=False)[0], tok.encode("No", add_special_tokens=False)[0]
    items, used = candidates()
    images = {}
    for d in items:
        page = d["page"]
        img = images.setdefault(page, Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB"))
        W, H = page_size(page)
        b = d["box"]
        crop = R.clean_crop(img, [b[0] * 1000 / W, b[1] * 1000 / H, b[2] * 1000 / W, b[3] * 1000 / H])
        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": SKETCH}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[[crop]], return_tensors="pt").to(model.device)
        with torch.inference_mode():
            logits = model(**inputs).logits[0, -1].float()
        d["p_sketch"] = round(torch.softmax(logits[[yes_id, no_id]], dim=0)[0].item(), 4)
        print(page, d["block"], d["box"], d["p_sketch"], flush=True)
    json.dump({"items": items, "used": used}, open(os.path.join(OUT, "recover_scores.json"), "w"), indent=1)


def evaluate(items, used, pages, t):
    gt = load_gt()
    rec, false, missing, kept = 0, 0, 0, 0
    for p in pages:
        gts = [g["box"] for g in gt.get(p, [])]
        miss = [g for g in gts if not any(iou(g, u) >= 0.3 for u in used.get(p, []))]
        missing += len(miss)
        keep = [d["box"] for d in items if d["page"] == p and d["p_sketch"] >= t]
        kept += len(keep)
        rec += sum(any(iou(k, g) >= 0.3 for k in keep) for g in miss)
        false += sum(all(iou(k, g) < 0.1 for g in gts) for k in keep)
    return {"missing": missing, "recovered": rec, "false": false, "kept": kept}


def pick():
    data = json.load(open(os.path.join(OUT, "recover_scores.json")))
    items, used = data["items"], data["used"]
    L = ["# Recovering drawings with no description (Surya 2.5 leftovers + verifier)", "",
         "| T | dev missing | dev recovered | dev false | val+test missing | val+test recovered | val+test false | kept on all val+test pages |",
         "|---|---|---|---|---|---|---|---|"]
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    allvt = splits["val"] + splits["test"]
    res = []
    for t in THRESHOLDS:
        a, b = evaluate(items, used, DEV, t), evaluate(items, used, VAL + TEST, t)
        n_all = sum(d["p_sketch"] >= t for d in items if d["page"] in allvt)
        res.append((t, a, b, n_all))
        L.append(f"| {t} | {a['missing']} | {a['recovered']} | {a['false']} | {b['missing']} | {b['recovered']} | {b['false']} | {n_all} |")
    t = max(res, key=lambda r: (r[1]["recovered"] - r[1]["false"], r[0]))[0]
    keep = [d for d in items if d["page"] in allvt and d["p_sketch"] >= t]
    L += ["", f"Chosen on dev (recovered minus false, higher T on ties): T = {t}. Added on val + test pages: {len(keep)} "
              f"({sum(d['page'].startswith('ie802') for d in keep)} IE802, {sum(not d['page'].startswith('ie802') for d in keep)} other)."]
    json.dump({"T": t, "added": keep}, open(os.path.join(OUT, "recovered_val_test.json"), "w"), indent=1)
    open(os.path.join(OUT, "recover.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["run", "pick"])
    run() if ap.parse_args().action == "run" else pick()
