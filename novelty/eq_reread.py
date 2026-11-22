"""Second readings of the display equations (maths work, options 1 and 2).

Readers for every display equation on a val/test page:
  page   the final model reading the whole page (preds/final_clean_<split>, the reported output)
  surya  Surya 2.5 full-page OCR, equation blocks (<math> LaTeX), zero-shot
         (novelty/surya25/ocr/vt_out/vt/results.json, 49 s for 107 pages)
  crop   the final model reading each Surya equation block, cut out and enlarged (zoom)
Each page equation is matched to the closest reading of each other reader (token edit distance
after norm_latex). Rules that may replace the page equation are compared on the 31 val pages,
the chosen rule is applied once to the 76 test pages and scored with evaluate.py.

Usage (GPU machine, from ie643_final/):
  python3 novelty/eq_reread.py crops      # GPU, final model on each equation crop
  python3 novelty/eq_reread.py combine    # no GPU: rules on val, chosen rule on test
Output: novelty/math/reread/
"""
import argparse, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "05_evaluation"))
sys.path.insert(0, os.path.join(ROOT, "06_interface"))
from metrics import norm_latex  # noqa: E402

OUT = os.path.join(ROOT, "novelty/math/reread")
OCR = os.path.join(ROOT, "novelty/surya25/ocr/vt_out/vt/results.json")
DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
MATH_TAG = re.compile(r"<math[^>]*>(.*?)</math>", re.S)


def splits():
    s = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    return s["val"], s["test"]


def eq_blocks():
    """page -> [(block index, bbox px, surya latex list)] for Surya equation blocks."""
    r = json.load(open(OCR))
    out = {}
    for k, v in r.items():
        page = os.path.splitext(os.path.basename(k))[0]
        for i, b in enumerate(v[0]["blocks"]):
            if b["label"] == "Equation":
                out.setdefault(page, []).append((i, b["bbox"], [m.strip() for m in MATH_TAG.findall(b.get("html", ""))]))
    return out


def cmd_crops():
    from PIL import Image
    from pipeline import CleanRecognizer
    os.makedirs(os.path.join(OUT, "crops"), exist_ok=True)
    rec = CleanRecognizer(os.path.join(ROOT, "runs/final_clean/final_adapter"), 1_000_000, 512)
    res = {}
    for page, blocks in sorted(eq_blocks().items()):
        img = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
        W, H = img.size
        for i, b, _ in blocks:
            pad = 0.01 * max(W, H)
            box = (max(0, int(b[0] - pad)), max(0, int(b[1] - pad)), min(W, int(b[2] + pad)), min(H, int(b[3] + pad)))
            crop = img.crop(box)
            s = min(3.0, (800_000 / max(1, crop.width * crop.height)) ** 0.5)  # zoom small regions up to 3x
            if s > 1:
                crop = crop.resize((int(crop.width * s), int(crop.height * s)), Image.LANCZOS)
            path = os.path.join(OUT, "crops", f"{page}_b{i}.png")
            crop.save(path)
            text, _ = rec.predict(path)
            res.setdefault(page, {})[str(i)] = text
            print(page, i, text[:80].replace("\n", " "), flush=True)
    json.dump(res, open(os.path.join(OUT, "crop_readings.json"), "w"), indent=1)


def toks(s):
    return re.findall(r"\\[A-Za-z]+|\S", norm_latex(s))


def ned(a, b):
    a, b = toks(a), toks(b)
    if not a and not b:
        return 0.0
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1] / max(len(a), len(b))


def maths_of(text):
    """Display equations of a reading; if there are none, the inline maths."""
    d = [m.strip() for m in DISPLAY.findall(text)]
    if d:
        return d
    return [m.strip() for m in re.findall(r"(?<!\$)\$([^$\n]+)\$(?!\$)", text)]


def best(eq, cands):
    if not cands:
        return None, 1.0
    c = min(cands, key=lambda x: ned(eq, x))
    return c, ned(eq, c)


def apply_rule(page_md, surya_eqs, crop_eqs, rule):
    kind, t = rule
    n = 0

    def rep(m):
        nonlocal n
        eq = m.group(1).strip()
        s, ds = best(eq, surya_eqs)
        c, dc = best(eq, crop_eqs)
        new = None
        if kind == "vote" and s and c and ds <= t and dc <= t and ned(s, c) <= 0.1 and dc > 0:
            new = c  # the two second readers agree with each other and differ from the page reading
        elif kind == "crop" and c and 0 < dc <= t:
            new = c
        elif kind == "surya" and s and 0 < ds <= t:
            new = s
        if new is None:
            return m.group(0)
        n += 1
        return "$$" + new + "$$"
    return DISPLAY.sub(rep, page_md), n


def score(pred_dir, split):
    r = subprocess.run([sys.executable, os.path.join(ROOT, "05_evaluation/evaluate.py"), "--pred", pred_dir,
                        "--split", os.path.join(ROOT, f"data/{split}.jsonl"), "--full"], capture_output=True, text=True, cwd=ROOT)
    allrows = [l for l in r.stdout.splitlines() if l.startswith("ALL")]
    head = [l for l in r.stdout.splitlines() if l.startswith("source")]
    vals = dict(zip(head[1].split()[2:], allrows[1].split()[2:])) if len(allrows) > 1 else {}
    vals.update(dict(zip(head[0].split()[2:], allrows[0].split()[2:])))
    return vals


def cmd_combine():
    val, test = splits()
    blocks = eq_blocks()
    crops = json.load(open(os.path.join(OUT, "crop_readings.json")))
    rules = [("keep", 0)] + [(k, t) for k in ("vote", "crop", "surya") for t in (0.2, 0.35, 0.5)]
    L = ["# Second readings of display equations (rules chosen on val, applied once to test)", "",
         "| rule | threshold | val NED | val eqMatch | val eqF1 | val eqEdit | equations replaced (val) |", "|---|---|---|---|---|---|---|"]
    res = []
    for rule in rules:
        d = os.path.join(OUT, f"val_{rule[0]}_{rule[1]}")
        os.makedirs(d, exist_ok=True)
        n_total = 0
        for p in val:
            md = open(os.path.join(ROOT, "preds/final_clean_val", p + ".md")).read()
            s_eqs = [x for _, _, ls in blocks.get(p, []) for x in ls]
            c_eqs = [x for t in crops.get(p, {}).values() for x in maths_of(t)]
            new, n = (md, 0) if rule[0] == "keep" else apply_rule(md, s_eqs, c_eqs, rule)
            n_total += n
            open(os.path.join(d, p + ".md"), "w").write(new)
        v = score(d, "val")
        res.append((rule, v, n_total))
        L.append(f"| {rule[0]} | {rule[1]} | {v.get('NED')} | {v.get('eqMatch')} | {v.get('eqF1')} | {v.get('eqEdit')} | {n_total} |")
    base = res[0][1]
    ok = [r for r in res if float(r[1]["NED"]) <= float(base["NED"])] or res[:1]
    chosen = max(ok, key=lambda r: (float(r[1]["eqF1"]), float(r[1]["eqMatch"]), -float(r[1]["NED"])))
    rule = chosen[0]
    L += ["", f"Chosen on val (equation F1, then exact match, never a worse NED): {rule}", ""]
    for name, rr in (("keep", ("keep", 0)), ("chosen", rule)):
        d = os.path.join(OUT, f"test_{rr[0]}_{rr[1]}")
        os.makedirs(d, exist_ok=True)
        n_total = 0
        for p in test:
            md = open(os.path.join(ROOT, "preds/final_clean_test", p + ".md")).read()
            s_eqs = [x for _, _, ls in blocks.get(p, []) for x in ls]
            c_eqs = [x for t in crops.get(p, {}).values() for x in maths_of(t)]
            new, n = (md, 0) if rr[0] == "keep" else apply_rule(md, s_eqs, c_eqs, rr)
            n_total += n
            open(os.path.join(d, p + ".md"), "w").write(new)
        v = score(d, "test")
        L.append(f"- test, {name} {rr}: NED {v.get('NED')}, eqMatch {v.get('eqMatch')}, eqF1 {v.get('eqF1')}, "
                 f"eqEdit {v.get('eqEdit')}, CER {v.get('CER')}, equations replaced {n_total}")
    open(os.path.join(OUT, "reread_scores.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["crops", "combine"])
    {"crops": cmd_crops, "combine": cmd_combine}[ap.parse_args().cmd]()
