"""Before / after comparison of figure placement: old pipeline (A) vs new (B), with C as ablation.

Two error metrics, both per [Diagram: ...] description, both 0 = perfect:

1. Figure Error Score (FES), from the blind human grades (regrade/grades.json):
     severity  0    correct
               0.5  loose crop (right drawing, complete, plus other content)
                    partial crop (right drawing, part cut off)
               1    wrong drawing, not a drawing, or no crop at all
   FES = mean severity over descriptions. Failure rate = share with severity 1.
   Why: it is what a reader of the PDF experiences. A wrong or missing figure misleads or loses
   information (1). A loose or partial crop is still usable but degraded (0.5).

2. Localisation Error (LE), automatic, from the hand-drawn GT boxes (IE802 only):
     LE = 1 - IoU(chosen box, GT box of the drawing the description refers to); no box -> 1.
   Each description is also given the stage that decides its outcome:
     recognition  the description refers to no real drawing (extra line)
     matching     the box overlaps a different GT drawing more than the intended one
     localisation right drawing, but IoU < 0.5 (cut off, or too large)
     ok           IoU >= 0.5
   Why: it needs no human judgement, so it can be re-run on any change, and it shows which
   pipeline stage to blame.

Scope: IE802 val + test, all 24 descriptions (every one was graded blind for A, B and C).
IE643 + MLT val + test: only the 8 descriptions where B's crop differs from A's were graded.
The other descriptions keep the identical crop, so their error is the same before and after.

Usage (from ie643_final/):  python3 novelty/compare_arms.py
Output: novelty/results/comparison/ (comparison.md, outcome_chart.png, one PNG per affected page)
"""
import json, os
from collections import Counter, defaultdict
from PIL import Image, ImageDraw, ImageFont

from common import ROOT, VAL, TEST, R, load_gt, load_intended, page_size, iou, current_pairing, pred_md
import match_figures as M

OUT = os.path.join(ROOT, "novelty/results/comparison")
SEV = {"correct": 0.0, "loose": 0.5, "partial": 0.5, "wrong": 1.0, "not_drawing": 1.0, "no crop": 1.0}
BOLD, REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=False):
    try:
        return ImageFont.truetype(BOLD if bold else REG, size)
    except OSError:
        return ImageFont.load_default()


def unit_of(page):
    return page.rsplit("_page", 1)[0]


def split_of(page, splits):
    return "val" if page in splits["val"] else "test"


def load_grades():
    """(set, page, desc) -> {arm: grade}"""
    key = json.load(open(os.path.join(ROOT, "novelty/regrade/key.json")))
    grades = json.load(open(os.path.join(ROOT, "novelty/regrade/grades.json")))
    out = defaultdict(dict)
    for cid, m in key.items():
        if cid.startswith("_"):
            continue
        for arm in m["arms"]:
            out[(m["set"], m["page"], m["desc"])][arm] = grades[cid]
    for it in key.get("_no_crop", []):
        for arm in it["arms"]:
            out[(it["set"], it["page"], it["desc"])][arm] = "no crop"
    return out


def all_choices(tau):
    """page -> {texts, A, B, C} boxes for every val/test page with descriptions."""
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    pages = VAL + TEST + [p for s in ("val", "test") for p in splits[s] if p.startswith(("ie643_", "mlt_"))]
    res = {}
    for page in pages:
        md = pred_md(page)
        if md is None:
            continue
        c = current_pairing(page, md)
        if not c["texts"]:
            continue
        size = page_size(page)
        q = M.qwen_boxes(page, len(c["texts"]))
        res[page] = {"texts": c["texts"], "A": M.arm_a(c, size), "B": M.arm_b(c, size, q, tau)[0],
                     "C": M.arm_c(c, size, q), "size": size}
    return res, splits


def changed(a, b):
    if a is None and b is None:
        return False
    if a is None or b is None:
        return True
    return iou(a, b) < 0.95


def stage(box, target, gt_by):
    if target is None:
        return "recognition", 1.0
    if box is None:
        return "no crop", 1.0
    ious = {k: iou(box, v) for k, v in gt_by.items()}
    le = 1 - ious[target]
    if max(ious, key=ious.get) != target or ious[target] == 0:
        return "matching", le
    return ("ok" if ious[target] >= 0.5 else "localisation"), le


def page_figure(page, rows, ch, grades, set_name):
    """Left: page with A (red) and B (green) boxes for the changed descriptions.
    Right: one row per changed description: caption, A crop + grade, B crop + grade."""
    img = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
    W, H = ch["size"]
    scale = 900 / H
    thumb = img.resize((round(W * scale), 900))
    d = ImageDraw.Draw(thumb)
    for i in rows:
        for arm, colour, dy in (("A", (208, 59, 59), 0), ("B", (12, 140, 12), 26)):
            b = ch[arm][i]
            if b is None:
                continue
            bb = [v * scale for v in b]
            d.rectangle(bb, outline=colour, width=4)
            d.text((bb[0] + 4, bb[1] + 2 + dy), f"{arm}:D{i + 1}", fill=colour, font=font(20, True))
    cell, cap_w = 300, 380
    row_h = cell + 20
    right = Image.new("RGB", (cap_w + 2 * (cell + 20), 40 + row_h * len(rows)), "white")
    d = ImageDraw.Draw(right)
    d.text((10, 8), "description", fill=(60, 60, 60), font=font(20, True))
    d.text((cap_w + 10, 8), "before (A)", fill=(60, 60, 60), font=font(20, True))
    d.text((cap_w + cell + 30, 8), "after (B)", fill=(60, 60, 60), font=font(20, True))
    for r, i in enumerate(rows):
        y = 40 + r * row_h
        words, line, lines = ch["texts"][i].split(), "", [f"D{i + 1}:"]
        for w in words:
            if len(line) + len(w) > 34:
                lines.append(line); line = w
            else:
                line = (line + " " + w).strip()
        lines.append(line)
        for k, t in enumerate(lines[:9]):
            d.text((10, y + 4 + k * 24), t, fill=(20, 20, 20), font=font(18, k == 0))
        for col, arm in enumerate("AB"):
            x = cap_w + col * (cell + 20)
            g = grades.get((set_name, page, f"D{i + 1}"), {}).get(arm, "?")
            b = ch[arm][i]
            if b is not None:
                crop = R.clean_crop(img, [b[0] * 1000 / W, b[1] * 1000 / H, b[2] * 1000 / W, b[3] * 1000 / H])
                crop.thumbnail((cell, cell - 34))
                right.paste(crop, (x, y + 30))
                d.rectangle([x, y + 30, x + crop.width, y + 30 + crop.height], outline=(200, 200, 200))
            colour = (12, 120, 12) if SEV[g] == 0 else (180, 120, 0) if SEV[g] == 0.5 else (190, 40, 40)
            d.text((x, y + 4), g.replace("_", " "), fill=colour, font=font(20, True))
    out = Image.new("RGB", (thumb.width + right.width + 30, max(thumb.height, right.height) + 60), "white")
    out.paste(thumb, (10, 50)); out.paste(right, (thumb.width + 20, 50))
    ImageDraw.Draw(out).text((10, 10), f"{page}: boxes before (red, A) and after (green, B)",
                             fill=(20, 40, 35), font=font(26, True))
    out.save(os.path.join(OUT, page + ".png"))


def chart(summary, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    bars = [("IE802: A (before)", "IE802", "A"), ("IE802: B (after)", "IE802", "B"), ("IE802: C (Qwen only)", "IE802", "C"),
            ("IE643+MLT changed: A", "IE643+MLT", "A"), ("IE643+MLT changed: B", "IE643+MLT", "B")]
    cats = [("ok", "correct", "#0ca30c"), ("degraded", "loose / partial", "#fab219"),
            ("failed", "wrong / not a drawing / no crop", "#d03b3b")]
    fig, ax = plt.subplots(figsize=(10, 3.6), dpi=200)
    fig.patch.set_facecolor("#fcfcfb"); ax.set_facecolor("#fcfcfb")
    for y, (label, s, arm) in enumerate(bars):
        left = 0
        for key, _, colour in cats:
            v = summary[(s, arm)][key]
            if v:
                ax.barh(y, v, left=left, color=colour, edgecolor="#fcfcfb", linewidth=2, height=0.6)
                ax.text(left + v / 2, y, str(v), ha="center", va="center", fontsize=9,
                        color="#0b0b0b" if colour == "#fab219" else "#ffffff", fontweight="bold")
            left += v
        ax.text(left + 0.3, y, f"FES {summary[(s, arm)]['fes']:.2f}", va="center", fontsize=9, color="#52514e")
    ax.set_yticks(range(len(bars)), [b[0] for b in bars], fontsize=9, color="#0b0b0b")
    ax.invert_yaxis()
    ax.set_xlabel("descriptions (blind human grades)", fontsize=9, color="#52514e")
    ax.set_xlim(0, 27)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7")
    ax.tick_params(axis="x", colors="#52514e", labelsize=8); ax.tick_params(axis="y", length=0)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in cats]
    ax.legend(handles, [l for _, l, _ in cats], loc="lower center", bbox_to_anchor=(0.45, 1.0), ncol=3,
              frameon=False, fontsize=9)
    ax.set_title("Figure outcome per description, before vs after (FES = Figure Error Score, 0 is best)",
                 fontsize=10, color="#0b0b0b", pad=26, loc="left")
    fig.tight_layout()
    fig.savefig(path, facecolor=fig.get_facecolor())


def main():
    os.makedirs(OUT, exist_ok=True)
    tau = json.load(open(os.path.join(ROOT, "novelty/results/choices_dev.json")))["tau"]
    grades = load_grades()
    choices, splits = all_choices(tau)
    gt_all, intended = load_gt(), load_intended()
    L = ["# Figure placement: before (A) vs after (B)", "",
         "Metrics (0 = perfect for both):", "",
         "- **Figure Error Score (FES)** from blind human grades: correct 0, loose or partial 0.5, "
         "wrong / not a drawing / no crop 1, averaged over descriptions. **Failure rate** = share scored 1.",
         "- **Localisation Error (LE)** from the GT boxes: 1 - IoU(chosen box, intended drawing), averaged. "
         "Each description is also assigned the stage that decides its outcome.", "",
         f"Arm B uses TAU = {tau}, chosen on IE802 training pages before any val/test result was seen.", ""]

    # 1. summary from human grades
    summary = {}
    L += ["## 1. Summary (blind human grades)", "",
          "| Pages | Arm | Descriptions | correct | degraded (loose/partial) | failed | FES | failure rate |",
          "|---|---|---|---|---|---|---|---|"]
    for s, arms in (("IE802", "ABC"), ("IE643+MLT", "AB")):
        for arm in arms:
            sev = [SEV[v[arm]] for k, v in grades.items() if k[0] == s and arm in v]
            n = len(sev)
            ok, deg, fail = sev.count(0.0), sev.count(0.5), sev.count(1.0)
            summary[(s, arm)] = {"ok": ok, "degraded": deg, "failed": fail, "fes": sum(sev) / n, "n": n}
            name = {"A": "A before", "B": "B after", "C": "C Qwen only"}[arm]
            scope = "IE802 val + test (all)" if s == "IE802" else "IE643 + MLT (8 changed)"
            L.append(f"| {scope} | {name} | {n} | {ok} | {deg} | {fail} | {sum(sev) / n:.2f} | {fail}/{n} ({100 * fail / n:.0f}%) |")
    L += ["", "IE643 + MLT: the remaining 32 of 40 descriptions keep the identical crop, so their error is "
          "unchanged and is not re-graded.", ""]

    # 2. automatic localisation error and stage on IE802
    L += ["## 2. Localisation Error and failing stage (IE802 val + test, automatic, GT boxes)", "",
          "| Arm | mean LE | ok (IoU >= 0.5) | localisation | matching | recognition |", "|---|---|---|---|---|---|"]
    stage_rows = {}
    for arm in "ABC":
        st, les = Counter(), []
        for page in VAL + TEST:
            if page not in choices:
                continue
            ch, gt_by = choices[page], {g["label"]: g["box"] for g in gt_all.get(page, [])}
            for i in range(len(ch["texts"])):
                target = intended.get(page, {}).get(f"D{i + 1}")
                s_, le = stage(ch[arm][i], target, gt_by)
                st[s_] += 1
                stage_rows[(page, i, arm)] = (s_, le)
                if target is not None:
                    les.append(le)
        L.append(f"| {arm} | {sum(les) / len(les):.2f} (n={len(les)}) | {st['ok']} | {st['localisation']} | "
                 f"{st['matching']} | {st['recognition']} |")
    L += ["", "Recognition misses (drawings with no [Diagram] line, the same for every arm): 042 GT D4, "
          "046 GT D2, 056 X (also missed by Surya).", ""]

    # 3. per document
    L += ["## 3. Per document (val/test files)", "",
          "| Document | split | descriptions | changed by B | FES before | FES after | failures before | failures after |",
          "|---|---|---|---|---|---|---|---|"]
    docs = defaultdict(list)
    for page, ch in choices.items():
        docs[(unit_of(page), split_of(page, splits))].append(page)
    for (unit, sp), pages in sorted(docs.items()):
        set_name = "IE802" if unit == "ie802_notes" else "IE643+MLT"
        n = sum(len(choices[p]["texts"]) for p in pages)
        ch_idx = [(p, i) for p in pages for i in range(len(choices[p]["texts"]))
                  if changed(choices[p]["A"][i], choices[p]["B"][i])]
        graded = [(p, i) for p in pages for i in range(len(choices[p]["texts"]))
                  if "A" in grades.get((set_name, p, f"D{i + 1}"), {})]
        if not graded:
            L.append(f"| {unit} | {sp} | {n} | 0 | unchanged | unchanged | unchanged | unchanged |")
            continue
        fa = [SEV[grades[(set_name, p, f'D{i + 1}')]["A"]] for p, i in graded]
        fb = [SEV[grades[(set_name, p, f'D{i + 1}')]["B"]] for p, i in graded]
        note = "" if set_name == "IE802" else f" (over the {len(graded)} changed)"
        L.append(f"| {unit} | {sp} | {n} | {len(ch_idx)} | {sum(fa) / len(fa):.2f}{note} | {sum(fb) / len(fb):.2f} | "
                 f"{fa.count(1.0)} | {fb.count(1.0)} |")
    L.append("")

    # 4. per affected page and per description
    L += ["## 4. Every affected page and description", "",
          "| Page | Desc | Description (short) | before (A) | after (B) | LE before | LE after | stage before | stage after |",
          "|---|---|---|---|---|---|---|---|---|"]
    affected = []
    for page in sorted(choices):
        ch = choices[page]
        set_name = "IE802" if page.startswith("ie802") else "IE643+MLT"
        rows = [i for i in range(len(ch["texts"])) if changed(ch["A"][i], ch["B"][i])]
        if not rows:
            continue
        affected.append(page)
        for i in rows:
            g = grades.get((set_name, page, f"D{i + 1}"), {})
            sa, la = stage_rows.get((page, i, "A"), ("-", None))
            sb, lb = stage_rows.get((page, i, "B"), ("-", None))
            text = ch["texts"][i][:60] + ("..." if len(ch["texts"][i]) > 60 else "")
            fmt = lambda v: "-" if v is None else f"{v:.2f}"
            L.append(f"| {page} | D{i + 1} | {text} | {g.get('A', '?')} | {g.get('B', '?')} | {fmt(la)} | {fmt(lb)} | {sa} | {sb} |")
        page_figure(page, rows, ch, grades, set_name)
    L += ["", f"Before/after images for the {len(affected)} affected pages: `{', '.join(p + '.png' for p in affected)}`.", ""]

    # 5. where the human and automatic metrics disagree (IE802)
    L += ["## 5. Where the two metrics disagree (IE802)", "",
          "A human grade of correct with an automatic stage of matching, or a human grade of wrong with "
          "an automatic ok. These show the limits of each metric.", "",
          "| Page | Desc | Arm | human grade | automatic stage | IoU with intended GT |", "|---|---|---|---|---|---|"]
    n_dis = 0
    for (page, i, arm), (st_, le) in sorted(stage_rows.items()):
        g = grades.get(("IE802", page, f"D{i + 1}"), {}).get(arm)
        if g is None:
            continue
        if (SEV[g] == 0 and st_ == "matching") or (SEV[g] == 1 and st_ == "ok"):
            n_dis += 1
            L.append(f"| {page[-3:]} | D{i + 1} | {arm} | {g} | {st_} | {1 - le:.2f} |")
    total = sum(1 for (page, i, arm) in stage_rows if ("IE802", page, f"D{i + 1}") in grades)
    L += ["", f"{n_dis} of {total} arm-description pairs disagree. On these pages: 041 D4's description "
          "(two S1 regions with a red line) also fits the neighbouring S1/S2 drawing, so the grader accepted it. "
          "042 D3 (A) is a merged box of three drawings that the grader judged as showing the right one "
          "(arguably loose). 047 D4 overlaps its GT drawing with IoU 0.89 but was graded wrong for every arm, "
          "which suggests the description does not match how the grader read the sketch. "
          "Neither metric alone is final, so the poster reports both.", ""]

    chart(summary, os.path.join(OUT, "outcome_chart.png"))
    open(os.path.join(OUT, "comparison.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
