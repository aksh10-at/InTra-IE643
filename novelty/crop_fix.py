"""Getting the right crop: compares ways of producing Qwen's rough box for Method B.

  per_desc   ground_qwen.py: one prompt per description (current Method B)
  page       ground_page.py: one prompt per page with every description (no shared boxes)
  hybrid     per_desc, but on a page where two descriptions got nearly the same box
             (IoU >= DUP), the whole page uses the page-prompt boxes
  dup_only   per_desc, but only the descriptions that share a box take their page-prompt box

Method B itself is unchanged (Hungarian on IoU with Qwen's boxes, join Surya pieces, TAU 0.2).
Run with Surya 2 (data/tags) and Surya 2.5 (novelty/surya25/all/data25) boxes.
Variant choice is made on the 8 IE802 dev pages; val + test is reported.

Usage (from ie643_final/, no GPU):  python3 novelty/crop_fix.py
Output: novelty/crop_fix/grounding_scores.md, choices_<surya>_<variant>.json
"""
import json, os

from common import ROOT, VAL, TEST, DEV, R, load_gt, load_intended, iou
import match_figures as M

OUT = os.path.join(ROOT, "novelty/crop_fix")
TAGS = {"2": os.path.join(ROOT, "data"), "2.5": os.path.join(ROOT, "novelty/surya25/all/data25")}
GDIR = {"per_desc": os.path.join(ROOT, "novelty/grounding/all"),
        "page": os.path.join(ROOT, "novelty/grounding/page_all"),
        "per_desc_2m": os.path.join(ROOT, "novelty/grounding/all_2m"),
        "page_2m": os.path.join(ROOT, "novelty/grounding/page_all_2m")}
DUP = 0.7


def load(dirname, page):
    p = os.path.join(dirname, page + ".json")
    return json.load(open(p)) if os.path.exists(p) else None


def has_duplicates(g):
    boxes = [it["box"] for it in g["items"] if it["box"]]
    return any(iou(a, b) >= DUP for i, a in enumerate(boxes) for b in boxes[i + 1:])


def dup_indices(g):
    boxes = [it["box"] for it in g["items"]]
    out = set()
    for i, a in enumerate(boxes):
        for j in range(i + 1, len(boxes)):
            if a and boxes[j] and iou(a, boxes[j]) >= DUP:
                out |= {i, j}
    return out


def grounding_for(variant):
    def f(page):
        if variant in GDIR:
            return load(GDIR[variant], page)
        if variant in ("dup_only", "dup_only_2m"):
            sfx = "_2m" if variant.endswith("_2m") else ""
            g, gp = load(GDIR["per_desc" + sfx], page), load(GDIR["page" + sfx], page)
            if g is None or gp is None:
                return g
            idx = dup_indices(g)
            g = json.loads(json.dumps(g))
            for it in g["items"]:
                if it["index"] in idx:
                    it["box"] = gp["items"][it["index"]]["box"]
            return g
        g = load(GDIR["per_desc"], page)
        if g is not None and has_duplicates(g):
            return load(GDIR["page"], page) or g
        return g
    return f


def run(surya, variant, tau=0.2):
    orig_pf, orig_lg = R.page_figures, M.load_grounding
    R.page_figures = lambda page, data_dir=None: orig_pf(page, TAGS[surya])
    M.load_grounding = grounding_for(variant)
    try:
        gt, inte = load_gt(), load_intended()
        res = {}
        for name, pages, src in (("dev", DEV, "label"), ("eval", VAL + TEST, "pred")):
            arms, _, choices, detail = M.evaluate(pages, src, tau, gt, inte)
            b = arms["B"]
            le = [1 - float(r["B"].split()[0]) if r["B"] != "none" else 1.0 for r in detail]
            res[name] = {"n": b["n"], "right_box": b["right_box"], "right_drawing": b["right_drawing"],
                         "mean_le": sum(le) / len(le), "detail": detail, "choices": choices}
        return res
    finally:
        R.page_figures, M.load_grounding = orig_pf, orig_lg


def main():
    os.makedirs(OUT, exist_ok=True)
    pages_dup = [p for p in DEV + VAL + TEST if (g := load(GDIR["per_desc"], p)) and has_duplicates(g)]
    lines = ["# Which Qwen boxes give Method B the right crop? (IE802 GT pages, TAU 0.2)", "",
             f"Pages where per-description grounding gave two descriptions the same box (IoU >= {DUP}): "
             f"{', '.join(p[-3:] for p in pages_dup) or 'none'}", "",
             "| Surya | Qwen boxes | dev right box | dev right drawing | dev mean LE | val+test right box | "
             "val+test right drawing | val+test mean LE |", "|---|---|---|---|---|---|---|---|"]
    all_res = {}
    for surya in ("2", "2.5"):
        for variant in ("per_desc", "page", "hybrid", "dup_only", "per_desc_2m", "dup_only_2m"):
            r = run(surya, variant)
            all_res[(surya, variant)] = r
            d, e = r["dev"], r["eval"]
            lines.append(f"| {surya} | {variant} | {d['right_box']}/{d['n']} | {d['right_drawing']}/{d['n']} | "
                         f"{d['mean_le']:.3f} | {e['right_box']}/{e['n']} | {e['right_drawing']}/{e['n']} | {e['mean_le']:.3f} |")
            json.dump(r["eval"]["choices"], open(os.path.join(OUT, f"choices_{surya}_{variant}.json"), "w"), indent=1)
    lines += ["", "Per description, val + test, Surya 2.5 (IoU of B's box with the intended GT drawing; WRONG = "
              "another drawing overlaps more):", "", "| page | desc | per_desc | page | hybrid | dup_only |", "|---|---|---|---|---|---|"]
    rows = {v: all_res[("2.5", v)]["eval"]["detail"] for v in ("per_desc", "page", "hybrid", "dup_only")}
    for k, r in enumerate(rows["per_desc"]):
        cells = [rows[v][k]["B"] for v in ("per_desc", "page", "hybrid", "dup_only")]
        mark = "" if len(set(cells)) == 1 else " **changed**"
        lines.append(f"| {r['page']} | {r['desc']} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]}{mark} |")
    open(os.path.join(OUT, "grounding_scores.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
