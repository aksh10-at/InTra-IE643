"""Blind check of the verifier pick: Method B's crop (Surya 2.5, dup_only) vs the verifier's crop.

Only descriptions where the two boxes differ (IoU < 0.95) are shown, on every val + test page
(IE643, MLT and IE802). Both crops are cut exactly as the PDFs cut them (Surya 2.5 layout,
crop cleaning on), shown side by side in a random order. The key is written to key.json.

Usage (from ie643_final/, no GPU):
  python3 novelty/compare_pick.py build
  (grade novelty/compare_pick/grade.html, Export, save as novelty/compare_pick/grades.json)
  python3 novelty/compare_pick.py score
"""
import argparse, html, json, os, random
from PIL import Image

from common import ROOT, iou
import crop_clean as C
from compare_surya import uri

OUT = os.path.join(ROOT, "novelty/compare_pick")
TAGS25 = os.path.join(ROOT, "novelty/surya25/all/data25")


def cut(page, box, img):
    C.TAGS_ROOT = TAGS25
    new, info = C.clean(img, box, C.surya_blocks(page), C.chosen_params())
    return C.finish(new, info["dark"])


def cmd_build(picks_file="picks_val_test.json"):
    picks = json.load(open(os.path.join(ROOT, "novelty/crop_fix", picks_file)))["picks"]
    cards = []
    for page, d in sorted(picks.items()):
        img = None
        for i, p in sorted(d.items(), key=lambda x: int(x[0])):
            a, b = p["cands"].get("B25"), p["box"]
            if a is None or b is None or iou(a, b) >= 0.95:
                continue
            img = img or Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
            cards.append({"page": page, "desc": f"D{int(i) + 1}", "text": p["text"], "pick": p["pick"],
                          "crops": {"methodB": cut(page, a, img), "verifier": cut(page, b, img)}})
    rnd = random.Random(2026)
    rnd.shuffle(cards)
    key, parts = {}, []
    for n, c in enumerate(cards, 1):
        cid = f"v{n:02d}"
        order = ["methodB", "verifier"]
        rnd.shuffle(order)
        key[cid] = {"page": c["page"], "desc": c["desc"], "left": order[0], "right": order[1], "verifier_source": c["pick"]}
        page_img = Image.open(os.path.join(ROOT, "data/processed", c["page"] + ".jpg"))
        parts.append(f"""<div class=card id={cid}><h3>{cid}</h3><p class=desc>{html.escape(c['text'])}</p><div class=row>
<figure><img src="{uri(c['crops'][order[0]])}"><figcaption>Left</figcaption></figure>
<figure><img src="{uri(c['crops'][order[1]])}"><figcaption>Right</figcaption></figure>
<figure class=page><img src="{uri(page_img, 420)}"><figcaption>Whole page</figcaption></figure></div>
<div class=btns>{''.join(f'<label><input type=radio name={cid} value={v}> {t}</label>' for v, t in (('left', 'Left better'), ('right', 'Right better'), ('same', 'Equally good'), ('both_bad', 'Both wrong')))}</div></div>""")
    page = f"""<!doctype html><meta charset=utf-8><title>Crop choice check</title>
<style>body{{font-family:system-ui;margin:16px;background:#f6f7f6}}.card{{background:#fff;padding:12px;margin:12px 0;border-radius:8px}}
.row{{display:flex;gap:12px;flex-wrap:wrap;align-items:flex-start}}figure{{margin:0}}img{{max-width:520px;max-height:420px;border:1px solid #ccc}}
.page img{{max-width:300px}}.btns label{{margin-right:16px}}</style>
<h1>Which crop shows the described drawing better?</h1><p>{len(cards)} pairs, random order. Press Export at the end.</p>
{''.join(parts)}<button onclick="exportGrades()">Export</button>
<script>function exportGrades(){{const g={{}};document.querySelectorAll('input:checked').forEach(i=>g[i.name]=i.value);
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(g,null,1)],{{type:'application/json'}}));
a.download='grades.json';a.click();}}</script>"""
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "grade.html"), "w").write(page)
    json.dump(key, open(os.path.join(OUT, "key.json"), "w"), indent=1)
    print(f"{len(cards)} pairs; by source of the verifier pick: "
          f"{ {s: sum(c['pick'] == s for c in cards) for s in ('Q', 'B2', 'U', 'B25')} }; "
          f"IE802 {sum(c['page'].startswith('ie802') for c in cards)}, other {sum(not c['page'].startswith('ie802') for c in cards)}")


def cmd_score(grades_file="grades.json"):
    from math import comb
    key = json.load(open(os.path.join(OUT, "key.json")))
    grades = json.load(open(os.path.join(OUT, grades_file)))
    if "grades" in grades:
        grades = grades["grades"]
    w = {"methodB": 0, "verifier": 0, "same": 0, "both_bad": 0}
    by = {"ie802": dict(w), "other": dict(w)}
    for cid, g in grades.items():
        r = key[cid][g] if g in ("left", "right") else g
        w[r] += 1
        by["ie802" if key[cid]["page"].startswith("ie802") else "other"][r] += 1
    n, lo = w["methodB"] + w["verifier"], min(w["methodB"], w["verifier"])
    p = min(1.0, 2 * sum(comb(n, i) for i in range(lo + 1)) / 2 ** n) if n else 1.0
    t = [f"# Blind paired grading: Method B crop vs verifier pick ({len(grades)} of {len(key)} pairs)", "",
         "| pages | Method B better | verifier better | equally good | both wrong |", "|---|---|---|---|---|"]
    for k, v in (("all", w), ("IE802", by["ie802"]), ("IE643 + MLT + HLCS", by["other"])):
        t.append(f"| {k} | {v['methodB']} | {v['verifier']} | {v['same']} | {v['both_bad']} |")
    t += ["", f"Sign test over all pairs with a winner: p = {p:.3f}"]
    open(os.path.join(OUT, "grading_scores.md"), "w").write("\n".join(t) + "\n")
    print("\n".join(t))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "score"])
    ap.add_argument("--grades", default="grades.json")
    ap.add_argument("--picks", default="picks_val_test.json", help="picks2_val_test.json for the fixed verifier")
    ap.add_argument("--out", default="compare_pick", help="output folder name under novelty/")
    a = ap.parse_args()
    OUT = os.path.join(ROOT, "novelty", a.out)
    cmd_build(a.picks) if a.cmd == "build" else cmd_score(a.grades)
