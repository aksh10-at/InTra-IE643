"""Method B with Surya 2 vs Method B with Surya 2.5: which crop does each description get?

For every val + test page with [Diagram] lines, arm B is computed twice with the same Qwen
grounding and the same TAU (0.2, chosen on dev in the main study), once with each Surya
version's figure boxes. Crops are cut exactly as the PDFs cut them (crop cleaning on, each with
its own Surya layout).

  build   per-description table (same / changed), Localisation Error on the IE802 GT pages,
          and a blind paired grading page for every changed crop: both crops side by side in a
          random order, the grader picks the better one. The key is written to key.json.
  score   reads grades.json (exported from the page) and key.json: wins for 2 vs 2.5.

Usage (from ie643_final/, no GPU):
  python3 novelty/compare_surya.py build
  (open novelty/compare_surya/grade.html, grade, Export, save as novelty/compare_surya/grades.json)
  python3 novelty/compare_surya.py score
"""
import argparse, base64, html, io, json, os, random
from PIL import Image

from common import ROOT, VAL, TEST, R, iou, page_size, current_pairing, pred_md, load_gt, load_intended
import match_figures as M
import crop_clean as C

OUT = os.path.join(ROOT, "novelty/compare_surya")
TAGS = {"2": os.path.join(ROOT, "data"), "2.5": os.path.join(ROOT, "novelty/surya25/all/data25")}


def boxes_for(version, page, tau):
    orig = R.page_figures
    R.page_figures = lambda p, data_dir=None: orig(p, TAGS[version])
    try:
        md = pred_md(page)
        c = current_pairing(page, md)
        if not c["texts"]:
            return [], []
        b = M.arm_b(c, page_size(page), M.qwen_boxes(page, len(c["texts"])), tau)
        return c["texts"], b
    finally:
        R.page_figures = orig


def cut(version, page, box, img):
    C.TAGS_ROOT = TAGS[version]
    p = C.chosen_params()
    new, info = C.clean(img, box, C.surya_blocks(page), p)
    return C.finish(new, info["dark"])


def uri(img, size=520):
    img = img.convert("RGB")
    img.thumbnail((size, size))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def cmd_build():
    tau = json.load(open(os.path.join(ROOT, "novelty/results/choices_dev.json")))["tau"]
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    pages = [p for s in ("val", "test") for p in splits[s]]
    gt_all, intended = load_gt(), load_intended()
    os.makedirs(OUT, exist_ok=True)
    rows, cards = [], []
    for page in pages:
        if pred_md(page) is None:
            continue
        texts, (b2, how2) = None, ([], [])
        texts, r2 = boxes_for("2", page, tau)
        _, r25 = boxes_for("2.5", page, tau)
        if not texts:
            continue
        (b2, how2), (b25, how25) = r2, r25
        img = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
        gts = {g["label"]: g["box"] for g in gt_all.get(page, [])}
        for i, t in enumerate(texts):
            x, y = b2[i], b25[i]
            same = x is not None and y is not None and iou(x, y) >= 0.95
            target = intended.get(page, {}).get(f"D{i + 1}") if page.startswith("ie802") else None
            le2 = le25 = None
            if target in gts:
                le2 = 1 - iou(x, gts[target]) if x else 1.0
                le25 = 1 - iou(y, gts[target]) if y else 1.0
            rows.append({"page": page, "desc": f"D{i + 1}", "same": same, "how2": how2[i], "how25": how25[i],
                         "le2": le2, "le25": le25, "text": t[:90]})
            if not same and x is not None and y is not None:
                cards.append({"page": page, "desc": f"D{i + 1}", "text": t,
                              "crops": {"2": cut("2", page, x, img), "2.5": cut("2.5", page, y, img)}})
    rnd = random.Random(643)
    rnd.shuffle(cards)
    key, html_cards = {}, []
    for n, c in enumerate(cards, 1):
        cid = f"p{n:02d}"
        order = ["2", "2.5"]
        rnd.shuffle(order)
        key[cid] = {"page": c["page"], "desc": c["desc"], "left": order[0], "right": order[1]}
        page_img = Image.open(os.path.join(ROOT, "data/processed", c["page"] + ".jpg"))
        html_cards.append(f"""<div class=card id={cid}><h3>{cid}: {html.escape(c['page'])} {c['desc']}</h3>
<p class=desc>{html.escape(c['text'])}</p><div class=row>
<figure><img src="{uri(c['crops'][order[0]])}"><figcaption>Left</figcaption></figure>
<figure><img src="{uri(c['crops'][order[1]])}"><figcaption>Right</figcaption></figure>
<figure class=page><img src="{uri(page_img, 420)}"><figcaption>Whole page</figcaption></figure></div>
<div class=btns>{''.join(f'<label><input type=radio name={cid} value={v}> {t}</label>' for v, t in (('left', 'Left better'), ('right', 'Right better'), ('same', 'Equally good'), ('both_bad', 'Both wrong')))}</div></div>""")
    page = f"""<!doctype html><meta charset=utf-8><title>Surya crop comparison</title>
<style>body{{font-family:system-ui;margin:16px;background:#f6f7f6}}.card{{background:#fff;padding:12px;margin:12px 0;border-radius:8px}}
.row{{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-start}}figure{{margin:0}}img{{max-width:520px;max-height:420px;border:1px solid #ccc}}
.page img{{max-width:300px}}.desc{{color:#333}}.btns label{{margin-right:16px}}</style>
<h1>Which crop shows the described drawing better?</h1><p>{len(cards)} pairs. The two crops come from two versions of the
layout model in a random order. Pick the better one for the description, then press Export and save the file as grades.json.</p>
{''.join(html_cards)}<button onclick="exportGrades()">Export</button>
<script>function exportGrades(){{const g={{}};document.querySelectorAll('input:checked').forEach(i=>g[i.name]=i.value);
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(g,null,1)],{{type:'application/json'}}));
a.download='grades.json';a.click();}}</script>"""
    open(os.path.join(OUT, "grade.html"), "w").write(page)
    json.dump(key, open(os.path.join(OUT, "key.json"), "w"), indent=1)
    same = sum(r["same"] for r in rows)
    ie = [r for r in rows if r["le2"] is not None]
    lines = ["# Method B: Surya 2 vs Surya 2.5 (val + test, same Qwen grounding, TAU 0.2)", "",
             f"- Descriptions: {len(rows)}. Same crop (IoU >= 0.95): {same}. Different: {len(rows) - same} "
             f"({len(cards)} pairs in the blind grading page).",
             f"- IE802 GT pages ({len(ie)} descriptions with a GT drawing): mean Localisation Error "
             f"Surya 2 {sum(r['le2'] for r in ie) / len(ie):.3f}, Surya 2.5 {sum(r['le25'] for r in ie) / len(ie):.3f}. "
             f"Right box (IoU >= 0.5): {sum(r['le2'] <= 0.5 for r in ie)} vs {sum(r['le25'] <= 0.5 for r in ie)}.",
             f"- Where the crop comes from (2 -> 2.5): Surya box {sum(r['how2'].startswith('surya') for r in rows)} -> "
             f"{sum(r['how25'].startswith('surya') for r in rows)}, Qwen box {sum(r['how2'] == 'qwen' for r in rows)} -> "
             f"{sum(r['how25'] == 'qwen' for r in rows)}, old fallback {sum(r['how2'] == 'fallback A' for r in rows)} -> "
             f"{sum(r['how25'] == 'fallback A' for r in rows)}.", "",
             "| page | desc | same | source 2 | source 2.5 | LE 2 | LE 2.5 | description |", "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        if r["same"]:
            continue
        f = lambda v: "-" if v is None else f"{v:.2f}"
        lines.append(f"| {r['page']} | {r['desc']} | no | {r['how2']} | {r['how25']} | {f(r['le2'])} | {f(r['le25'])} | "
                     f"{r['text'].replace('|', '/')} |")
    open(os.path.join(OUT, "comparison.md"), "w").write("\n".join(lines) + "\n")
    json.dump(rows, open(os.path.join(OUT, "rows.json"), "w"), indent=1)
    print("\n".join(lines[:6]))


def cmd_score():
    key = json.load(open(os.path.join(OUT, "key.json")))
    grades = json.load(open(os.path.join(OUT, "grades.json")))
    wins = {"2": 0, "2.5": 0, "same": 0, "both_bad": 0}
    for cid, g in grades.items():
        k = key[cid]
        if g in ("left", "right"):
            wins[k[g]] += 1
        else:
            wins[g] += 1
    from math import comb
    n, lo = wins["2"] + wins["2.5"], min(wins["2"], wins["2.5"])
    p = min(1.0, 2 * sum(comb(n, i) for i in range(lo + 1)) / 2 ** n) if n else 1.0
    text = (f"# Blind paired grading: {len(grades)} of {len(key)} pairs graded\n\n"
            f"| Surya 2 better | Surya 2.5 better | equally good | both wrong | sign test p |\n|---|---|---|---|---|\n"
            f"| {wins['2']} | {wins['2.5']} | {wins['same']} | {wins['both_bad']} | {p:.3f} |\n")
    open(os.path.join(OUT, "grading_scores.md"), "w").write(text)
    print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "score"])
    {"build": cmd_build, "score": cmd_score}[ap.parse_args().cmd]()
