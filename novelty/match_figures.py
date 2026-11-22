"""Three ways to choose the crop for each [Diagram: ...] description, and their scores.

  A  current pipeline: Surya figure boxes, merged when there are more boxes than descriptions,
     paired with descriptions by reading order (render_document.align)
  B  "Surya decides where, Qwen decides which": base Qwen gives a rough box per description;
     the Hungarian algorithm pairs descriptions with Surya boxes so that the total overlap
     (IoU with Qwen's box) is as large as possible, one Surya box per description. Other Surya
     boxes lying mostly inside the same Qwen box are added (a drawing Surya split in two).
     If the result overlaps Qwen's box by less than TAU, Qwen's own box is used instead.
  C  Qwen alone: the crop is Qwen's box.
  In B and C, a description whose Qwen box is missing or covers most of the page
  (uninformative) falls back to arm A's choice.

Scores (IE802 pages with hand-drawn GT boxes):
  right box     the crop box has IoU >= 0.5 with the GT drawing the description refers to
  right drawing the GT drawing the crop overlaps most is the one the description refers to
                (correct or partial crop of the right drawing)
  box P / R     detection-style precision and recall at IoU 0.5 against all GT boxes on the page

TAU is chosen on the 8 IE802 training pages (dev) only, then fixed for val + test.

Usage (from ie643_final/):  python3 novelty/match_figures.py
Output: novelty/results/match_scores.md, choices_<set>.json (the box each arm picked)
"""
import argparse, json, os
import numpy as np
from scipy.optimize import linear_sum_assignment

from common import (ROOT, VAL, TEST, DEV, R, load_gt, load_intended, load_grounding, page_size, to_px,
                    iou, cover, current_pairing, pred_md, label_md)

BIG = 0.6       # a Qwen box covering more than this share of the page carries no location information
COVER = 0.6     # a Surya box at least this much inside a Qwen box belongs to the same drawing
TAUS = [0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 1.01]


def union(boxes):
    return [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]


def informative(q, size):
    if q is None:
        return False
    return (q[2] - q[0]) * (q[3] - q[1]) <= BIG * size[0] * size[1]


def arm_a(c, size):
    boxes = [None] * len(c["texts"])
    for i, j in c["pairs"]:
        boxes[i] = to_px(c["figs"][j]["bbox"], size)
    return boxes


def arm_b(c, size, qboxes, tau):
    a_boxes = arm_a(c, size)
    surya = [to_px(f["bbox"], size) for f in c["raw"]]
    n = len(c["texts"])
    boxes, how = [None] * n, [""] * n
    rows = [i for i in range(n) if informative(qboxes[i], size)]
    used = set()
    if rows and surya:
        m = np.array([[iou(qboxes[i], s) for s in surya] for i in rows])
        for r, j in zip(*linear_sum_assignment(-m)):
            if m[r, j] > 0:
                i = rows[r]
                boxes[i], how[i] = surya[j], "surya"
                used.add(j)
    for i in rows:  # add other Surya pieces that sit inside the same Qwen box
        if boxes[i] is None:
            continue
        extra = [s for j, s in enumerate(surya) if j not in used and cover(s, qboxes[i]) >= COVER]
        if extra:
            boxes[i], how[i] = union([boxes[i]] + extra), "surya+"
    for i in rows:  # not good enough: trust Qwen's own box
        if boxes[i] is None or iou(boxes[i], qboxes[i]) < tau:
            boxes[i], how[i] = list(qboxes[i]), "qwen"
    for i in range(n):
        if i not in rows:
            boxes[i], how[i] = a_boxes[i], "fallback A"
    return boxes, how


def arm_c(c, size, qboxes):
    a_boxes = arm_a(c, size)
    return [list(q) if informative(q, size) else a_boxes[i] for i, q in enumerate(qboxes)]


def qwen_boxes(page, n):
    g = load_grounding(page)
    if g is None:
        return [None] * n
    items = sorted(g["items"], key=lambda it: it["index"])
    if len(items) != n:
        raise ValueError(f"{page}: {len(items)} grounding items but {n} descriptions")
    return [it["box"] for it in items]


def detection_pr(boxes, gts, thr=0.5):
    """One-to-one greedy matching by IoU; returns (true positives, predicted, GT)."""
    boxes = [b for b in boxes if b is not None]
    pairs = sorted(((iou(b, g), i, j) for i, b in enumerate(boxes) for j, g in enumerate(gts)), reverse=True)
    bi, gj, tp = set(), set(), 0
    for v, i, j in pairs:
        if v < thr:
            break
        if i not in bi and j not in gj:
            bi.add(i); gj.add(j); tp += 1
    return tp, len(boxes), len(gts)


def evaluate(pages, source, tau, gt_all, intended):
    """Per arm: counts for right box / right drawing over descriptions that refer to a GT drawing."""
    arms = {k: {"right_box": 0, "right_drawing": 0, "n": 0, "tp": 0, "pred": 0, "gt": 0} for k in "ABC"}
    det = {k: {"tp": 0, "pred": 0, "gt": 0} for k in ("Surya", "Qwen")}
    choices, detail = {}, []
    for page in pages:
        md = pred_md(page) if source == "pred" else label_md(page)
        c = current_pairing(page, md)
        gts = gt_all.get(page, [])
        if not c["texts"] and not gts:
            continue
        size = page_size(page)
        q = qwen_boxes(page, len(c["texts"]))
        picks = {"A": arm_a(c, size)}
        picks["B"], how = arm_b(c, size, q, tau)
        picks["C"] = arm_c(c, size, q)
        choices[page] = {k: v for k, v in picks.items()}
        choices[page]["B_how"] = how
        choices[page]["texts"] = c["texts"]
        gt_by = {g["label"]: g["box"] for g in gts}
        ordinal = label_ordinals(md, c) if source == "label" else None
        for i in range(len(c["texts"])):
            target = intended.get(page, {}).get(f"D{i + 1}") if source == "pred" else f"D{ordinal[i]}"
            if target not in gt_by:
                continue
            row = {"page": page[-3:], "desc": f"D{i + 1}", "gt": target, "B_how": how[i]}
            for k in "ABC":
                b = picks[k][i]
                arms[k]["n"] += 1
                if b is None:
                    row[k] = "none"
                    continue
                ious = {lab: iou(b, box) for lab, box in gt_by.items()}
                ok_box = ious[target] >= 0.5
                ok_drawing = ious[target] > 0 and max(ious, key=ious.get) == target
                arms[k]["right_box"] += ok_box
                arms[k]["right_drawing"] += ok_drawing
                row[k] = f"{ious[target]:.2f}" + ("" if ok_drawing else " WRONG")
            detail.append(row)
        gboxes = [g["box"] for g in gts]
        for k in "ABC":
            tp, p, g = detection_pr(picks[k], gboxes)
            arms[k]["tp"] += tp; arms[k]["pred"] += p; arms[k]["gt"] += g
        for name, boxes in (("Surya", [to_px(f["bbox"], size) for f in c["raw"]]),
                            ("Qwen", [b for b in q if informative(b, size)])):
            tp, p, g = detection_pr(boxes, gboxes)
            det[name]["tp"] += tp; det[name]["pred"] += p; det[name]["gt"] += g
    return arms, det, choices, detail


def label_ordinals(md, c):
    """For label Markdown: the position (1-based) of each stand-alone [Diagram] block among ALL
    [Diagram: mentions, including ones written inside a sentence. GT boxes D1, D2 ... follow
    that full order, while the renderer only sees the stand-alone ones."""
    starts = [m.start() for m in __import__("re").finditer(r"\[Diagram:", md)]
    out, pos = [], 0
    for k in c["desc_idx"]:
        at = md.index(c["blocks"][k].strip(), pos)
        pos = at + 1
        out.append(sum(1 for s in starts if s <= at))
    return out


def fmt(x, n):
    return f"{x}/{n} ({100 * x / n:.0f}%)" if n else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "novelty/results"))
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    gt_all, intended = load_gt(), load_intended()
    lines = ["# Figure matching: arms A / B / C", "",
             f"BIG = {BIG} (Qwen box larger than this share of the page is ignored), COVER = {COVER}", ""]

    # 1. choose TAU on the training pages only
    lines += ["## Step 1: choose TAU for arm B on IE802 training pages (dev, descriptions from labels)", "",
              "| TAU | B right box | B right drawing |", "|---|---|---|"]
    best = None
    for tau in TAUS:
        arms, _, _, _ = evaluate(DEV, "label", tau, gt_all, intended)
        b = arms["B"]
        lines.append(f"| {tau} | {fmt(b['right_box'], b['n'])} | {fmt(b['right_drawing'], b['n'])} |")
        key = (b["right_box"], b["right_drawing"], -abs(tau - 0.5))
        if best is None or key > best[0]:
            best = (key, tau)
    tau = best[1]
    lines += ["", f"Chosen TAU = {tau} (most right boxes on dev; ties go to the value nearest 0.5).", ""]

    # 2. report on dev and on val + test with that TAU
    for name, pages, source in (("dev (IE802 train pages 001-037, label descriptions)", DEV, "label"),
                                ("val + test (IE802 pages 041-056, model descriptions)", VAL + TEST, "pred")):
        arms, det, choices, detail = evaluate(pages, source, tau, gt_all, intended)
        lines += [f"## {name}", "",
                  "| Arm | right box (IoU >= 0.5) | right drawing | box precision @0.5 | box recall @0.5 |",
                  "|---|---|---|---|---|"]
        for k, label in (("A", "A: Surya + reading order"), ("B", "B: Surya + Qwen + Hungarian"), ("C", "C: Qwen only")):
            r = arms[k]
            lines.append(f"| {label} | {fmt(r['right_box'], r['n'])} | {fmt(r['right_drawing'], r['n'])} | "
                         f"{fmt(r['tp'], r['pred'])} | {fmt(r['tp'], r['gt'])} |")
        lines += ["", "Detectors alone (all their boxes, no pairing):", "",
                  "| Boxes | precision @0.5 | recall @0.5 |", "|---|---|---|"]
        for k, r in det.items():
            lines.append(f"| {k} | {fmt(r['tp'], r['pred'])} | {fmt(r['tp'], r['gt'])} |")
        lines += ["", "Per description (IoU of the chosen box with the GT drawing it refers to; WRONG = a "
                  "different drawing overlaps more):", "", "| page | desc | GT | A | B | B source | C |",
                  "|---|---|---|---|---|---|---|"]
        for r in detail:
            lines.append(f"| {r['page']} | {r['desc']} | {r['gt']} | {r['A']} | {r['B']} | {r['B_how']} | {r['C']} |")
        lines.append("")
        tag = "dev" if source == "label" else "eval"
        json.dump({"tau": tau, "choices": choices}, open(os.path.join(a.out, f"choices_{tag}.json"), "w"), indent=1)

    open(os.path.join(a.out, "match_scores.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
