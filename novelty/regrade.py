"""Blind re-grade of figure crops from arms A (old), B (new) and C (Qwen only).

build: cuts every distinct crop the arms place, exactly as the renderer would (clean_crop:
       1% padding, chalkboard inversion, trim to ink), shuffles them with a fixed seed and
       writes one HTML page. A card shows the crop, the description used as its caption and
       the source page. It never says which arm made the crop. Crops that two arms share
       (IoU >= 0.95) appear once and the grade counts for both.
         IE802 val + test: every description, arms A, B and C
         IE643 + MLT val + test: only descriptions where B's crop differs from A's (regression check)
       The key linking cards to arms is written to key.json. Do not open it while grading.
score: reads the grades the page exports plus key.json and prints the table per arm.

Grades: correct (right drawing, complete, little else), loose (right drawing, complete, but the
crop also takes in a lot of other content such as text lines or another drawing), partial (right
drawing, cut off), wrong (a different drawing), not_drawing (text or equation boxed).

Usage (from ie643_final/):
  python3 novelty/regrade.py build
  (grade in a browser: open novelty/regrade/regrade.html, press Export, save as novelty/regrade/grades.json)
  python3 novelty/regrade.py score
"""
import argparse, base64, html, io, json, os, random
from collections import Counter, defaultdict
from PIL import Image

from common import ROOT, VAL, TEST, R, iou, page_size, current_pairing, pred_md
import match_figures as M

OUT = os.path.join(ROOT, "novelty/regrade")
TAU = None  # read from results/choices_dev.json so the grade uses the frozen setting


def data_uri(img, size, quality=80):
    img = img.convert("RGB")
    img.thumbnail((size, size))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=quality)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def norm(box, size):
    w, h = size
    return [box[0] * 1000 / w, box[1] * 1000 / h, box[2] * 1000 / w, box[3] * 1000 / h]


def collect(tau):
    """[(set, page, desc index, text, {arm: box px or None})]"""
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    other = [p for s in ("val", "test") for p in splits[s] if p.startswith(("ie643_", "mlt_"))]
    items = []
    for group, pages, arms in (("IE802", VAL + TEST, "ABC"), ("IE643+MLT", other, "AB")):
        for page in pages:
            md = pred_md(page)
            if md is None:
                continue
            c = current_pairing(page, md)
            if not c["texts"]:
                continue
            size = page_size(page)
            q = M.qwen_boxes(page, len(c["texts"]))
            picks = {"A": M.arm_a(c, size), "B": M.arm_b(c, size, q, tau)[0], "C": M.arm_c(c, size, q)}
            for i, text in enumerate(c["texts"]):
                boxes = {k: picks[k][i] for k in arms}
                if group != "IE802":
                    a, b = boxes["A"], boxes["B"]
                    if (a is None and b is None) or (a is not None and b is not None and iou(a, b) >= 0.8):
                        continue  # B keeps A's crop: nothing to check
                items.append((group, page, i, text, boxes))
    return items


def build():
    tau = json.load(open(os.path.join(ROOT, "novelty/results/choices_dev.json")))["tau"]
    os.makedirs(OUT, exist_ok=True)
    cards, key, pages_seen = [], {}, {}
    for group, page, i, text, boxes in collect(tau):
        size = page_size(page)
        page_img = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
        distinct = []  # [(box, [arms])]
        for arm, box in boxes.items():
            if box is None:
                continue
            for d in distinct:
                if iou(d[0], box) >= 0.95:
                    d[1].append(arm)
                    break
            else:
                distinct.append((box, [arm]))
        for box, arms in distinct:
            crop = R.clean_crop(page_img, norm(box, size))
            cards.append({"crop": data_uri(crop, 560), "caption": text, "page": page,
                          "meta": {"set": group, "page": page, "desc": f"D{i + 1}", "arms": arms,
                                   "box_px": [round(v) for v in box]}})
        missing = [arm for arm, box in boxes.items() if box is None]
        if missing:  # an arm that places no crop for this description
            key.setdefault("_no_crop", []).append({"set": group, "page": page, "desc": f"D{i + 1}", "arms": missing})
        if page not in pages_seen:
            pages_seen[page] = data_uri(page_img, 900, 70)
    random.Random(643).shuffle(cards)
    for n, card in enumerate(cards, 1):
        card["id"] = f"c{n:03d}"
        key[card["id"]] = card["meta"]
    json.dump(key, open(os.path.join(OUT, "key.json"), "w"), indent=1)

    page_js = json.dumps({p: uri for p, uri in pages_seen.items()})
    body = "\n".join(
        f'<section data-id="{c["id"]}"><h2>{n}. card {c["id"]}</h2><div class="row">'
        f'<figure><img src="{c["crop"]}"><figcaption>{html.escape(c["caption"])}</figcaption></figure>'
        f'<details data-page="{c["page"]}"><summary>show source page</summary><img class="pg"></details></div>'
        f'<div class="grades">' + "".join(
            f'<label><input type="radio" name="{c["id"]}" value="{g}"> {t}</label>'
            for g, t in (("correct", "correct"), ("loose", "loose crop"), ("partial", "partial crop"), ("wrong", "wrong drawing"),
                         ("not_drawing", "not a drawing"))) + "</div></section>"
        for n, c in enumerate(cards, 1))
    page = f"""<!doctype html><meta charset="utf-8"><title>Blind crop re-grade</title>
<style>body{{font:15px system-ui;margin:24px auto;max-width:1150px;color:#1f2a26}}
section{{border-top:1px solid #ddd;padding:14px 0}}.row{{display:flex;gap:20px;align-items:flex-start}}
figure{{margin:0;max-width:580px}}figure img{{max-width:100%;border:1px solid #ccc}}
figcaption{{color:#334;margin-top:6px}}details{{flex:1}}.pg{{max-width:100%}}
.grades label{{margin-right:18px}}#bar{{position:sticky;top:0;background:#fff;padding:10px 0;border-bottom:1px solid #ccc;z-index:2}}</style>
<div id="bar"><b>{len(cards)} crops.</b> For each: does the crop show the drawing the caption describes, and is it complete?
Grade from the crop and the source page only. <button onclick="save()">Export grades</button>
<label>Import grades <input type="file" accept=".json" onchange="load(this.files[0])"></label> <span id="n">0 graded</span></div>
<p><b>correct</b> = right drawing, complete, little else &nbsp; <b>loose crop</b> = right drawing, complete, but also a lot of other content (text lines, another drawing) &nbsp; <b>partial crop</b> = right drawing, part cut off &nbsp;
<b>wrong drawing</b> = shows a different drawing &nbsp; <b>not a drawing</b> = text or an equation</p>
{body}
<script>
const PAGES = {page_js};
document.querySelectorAll('details').forEach(d => d.addEventListener('toggle', () => {{
  const img = d.querySelector('img'); if (d.open && !img.src) img.src = PAGES[d.dataset.page]; }}));
function save() {{
  const g = {{}};
  document.querySelectorAll('section').forEach(s => {{ const c = s.querySelector('input[type=radio]:checked'); if (c) g[s.dataset.id] = c.value; }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([JSON.stringify(g, null, 1)], {{type: 'application/json'}}));
  a.download = 'grades.json'; a.click();
}}
function count() {{
  document.getElementById('n').textContent = document.querySelectorAll('input[type=radio]:checked').length + ' of {len(cards)} graded'; }}
function load(file) {{
  file.text().then(t => {{ const g = JSON.parse(t);
    for (const [id, v] of Object.entries(g)) {{ const r = document.querySelector(`input[name="${{id}}"][value="${{v}}"]`); if (r) r.checked = true; }}
    count(); }}); }}
document.addEventListener('change', count);
</script>"""
    open(os.path.join(OUT, "regrade.html"), "w").write(page)
    by = Counter(c["meta"]["set"] for c in cards)
    print(f"{len(cards)} cards ({dict(by)}) -> {OUT}/regrade.html; key in key.json")


def score(path):
    key = json.load(open(os.path.join(OUT, "key.json")))
    grades = json.load(open(path))
    table = defaultdict(Counter)
    missing = [cid for cid in key if not cid.startswith("_") and cid not in grades]
    for cid, meta in key.items():
        if cid.startswith("_") or cid not in grades:
            continue
        for arm in meta["arms"]:
            table[(meta["set"], arm)][grades[cid]] += 1
    for item in key.get("_no_crop", []):
        for arm in item["arms"]:
            table[(item["set"], arm)]["no crop"] += 1
    cols = ["correct", "loose", "partial", "wrong", "not_drawing", "no crop"]
    lines = ["| set | arm | descriptions | " + " | ".join(cols) + " | right drawing (correct + loose + partial) |",
             "|---|---|---|" + "---|" * (len(cols) + 1)]
    for (group, arm) in sorted(table):
        t = table[(group, arm)]
        n = sum(t.values())
        lines.append(f"| {group} | {arm} | {n} | " + " | ".join(str(t[c]) for c in cols)
                     + f" | {t['correct'] + t['loose'] + t['partial']}/{n} |")
    text = "\n".join(lines)
    if missing:
        text += f"\n\n{len(missing)} cards not graded yet: {', '.join(missing[:10])}{' ...' if len(missing) > 10 else ''}"
    open(os.path.join(OUT, "regrade_scores.md"), "w").write(text + "\n")
    print(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["build", "score"])
    ap.add_argument("grades", nargs="?", default=os.path.join(OUT, "grades.json"))
    a = ap.parse_args()
    build() if a.action == "build" else score(a.grades)
