"""Surya 2 vs Surya 2.5 for layout (figure boxes), on the pages the novelty work uses.

Surya 2.5 (surya-ocr 0.24.0, checkpoint datalab-to/surya-ocr-2.5, 689M parameters) was run
zero-shot on the processed images of all val + test pages and the 8 IE802 dev pages:
  separate client env  ~/workspace/ie643/envs/surya0240 (the old surya0221 is untouched)
  server               the existing vllm0320 env, port 8002, bf16, max_pixels 6291456
  raw output           novelty/surya25/raw/processed/results.json (88 s for 115 pages)
Nothing in data/tags or data/crops is changed. Surya 2.5 tags go to novelty/surya25/data/.

Commands (from ie643_final/, no GPU):
  convert  results.json -> novelty/surya25/data/tags/*.json (same format as data/tags)
  counts   figure count vs the labels' [Diagram] lines (as experiment E5), Surya 2 vs 2.5
  match    arms A / B / C of match_figures.py with Surya 2.5 boxes (TAU chosen on dev again)
"""
import argparse, json, os, re, sys
from collections import defaultdict

from common import ROOT, R

BASE = os.path.join(ROOT, "novelty/surya25")
DATA = os.path.join(BASE, "data")
sys.path.insert(0, os.path.join(ROOT, "02_layout"))


def cmd_convert(raw_path=None, data=None, source="surya-ocr 0.24.0 / datalab-to/surya-ocr-2.5 zero-shot; unverified"):
    from PIL import Image
    from surya_to_tags import convert_page
    raw_path = raw_path or os.path.join(BASE, "raw/processed/results.json")
    DATA_ = data or DATA
    raw = json.load(open(raw_path))
    os.makedirs(os.path.join(DATA_, "tags"), exist_ok=True)
    os.makedirs(os.path.join(DATA_, "crops"), exist_ok=True)
    fixed = 0
    for key, entries in sorted(raw.items()):
        page = os.path.splitext(os.path.basename(key))[0]
        item = entries[0]
        if item.get("error"):
            raise SystemExit(f"{page}: Surya error")
        img = os.path.join(ROOT, "data/processed", page + ".jpg")
        with Image.open(img) as im:
            w, h = im.size
        W, H = item["image_bbox"][2], item["image_bbox"][3]
        if (round(W), round(H)) != (w, h):
            if abs(W - w) > 2 or abs(H - h) > 2:
                raise SystemExit(f"{page}: Surya saw {W}x{H}, image is {w}x{h}")
            item["image_bbox"] = [0, 0, w, h]  # Surya 2.5 reports the last pixel index + 1 rounding
            fixed += 1
        tags, warn = convert_page(page, item, img, os.path.join(DATA_, "crops"))
        if warn:
            raise SystemExit(f"{page}: {warn}")
        tags["source"] = source
        json.dump(tags, open(os.path.join(DATA_, "tags", page + ".json"), "w"), indent=1)
    print(f"converted {len(raw)} pages ({fixed} with a 1 px size rounding fix) -> {DATA_}/tags")


FIG = {"figure", "table"}


def count_rows(tags_dir, pages):
    rows = []
    for page in pages:
        label = open(os.path.join(ROOT, "data/annotations", page + ".md")).read()
        ref = len(re.findall(r"\[Diagram:", label, re.I))
        tags = json.load(open(os.path.join(tags_dir, page + ".json")))
        found = sum(b["type"] in FIG for b in tags["blocks"])
        rows.append((page.split("_")[0], ref, found))
    return rows


def cmd_counts():
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    out = ["| pages | source | Surya | label drawings | regions | exact count | precision | recall |",
           "|---|---|---|---|---|---|---|---|"]
    for split in ("val", "test"):
        for name, d in (("2", os.path.join(ROOT, "data/tags")), ("2.5", os.path.join(DATA, "tags"))):
            rows = count_rows(d, splits[split])
            groups = defaultdict(list)
            for r in rows:
                groups[r[0]].append(r); groups["ALL"].append(r)
            for src in sorted(groups, key=lambda s: (s == "ALL", s)):
                g = groups[src]
                ref, found = sum(r[1] for r in g), sum(r[2] for r in g)
                hit = sum(min(r[1], r[2]) for r in g)
                exact = sum(r[1] == r[2] for r in g)
                out.append(f"| {split} | {src} | {name} | {ref} | {found} | {exact}/{len(g)} | "
                           f"{hit / found:.3f} | {hit / ref:.3f} |" if found and ref else
                           f"| {split} | {src} | {name} | {ref} | {found} | {exact}/{len(g)} | - | - |")
    text = "# Figure count check (as E5): Surya 2 vs Surya 2.5\n\n" + "\n".join(out) + "\n"
    open(os.path.join(BASE, "counts.md"), "w").write(text)
    print(text)


def cmd_match():
    """Same script as the main result, with Surya 2.5 figure boxes swapped in."""
    orig = R.page_figures
    R.page_figures = lambda page, data_dir=None: orig(page, DATA)
    import match_figures as M
    out = os.path.join(BASE, "results")
    sys.argv = ["match_figures.py", "--out", out]
    M.main()


ALL25 = os.path.join(BASE, "all/data25")      # Surya 2.5, all 410 pages
ALL2R = os.path.join(BASE, "all/data2_rerun")  # Surya 2 re-run today, all 410 pages (run-to-run check)


def cmd_convert_all():
    cmd_convert(os.path.join(BASE, "raw_all/processed/results.json"), ALL25)
    cmd_convert(os.path.join(BASE, "raw_all_s2/processed/results.json"), ALL2R,
                "surya-ocr 0.22.1 / datalab-to/surya-ocr-2 zero-shot re-run 22 Nov; unverified")


def page_counts(tags_dir, pages):
    out = {}
    for page in pages:
        label = open(os.path.join(ROOT, "data/annotations", page + ".md")).read()
        ref = len(re.findall(r"\[Diagram:", label, re.I))
        tags = json.load(open(os.path.join(tags_dir, page + ".json")))
        out[page] = (ref, sum(b["type"] in FIG for b in tags["blocks"]))
    return out


def stats(c, pages):
    ref = sum(c[p][0] for p in pages); found = sum(c[p][1] for p in pages)
    hit = sum(min(*c[p]) for p in pages)
    return {"pages": len(pages), "exact": sum(c[p][0] == c[p][1] for p in pages), "ref": ref, "found": found,
            "precision": hit / found if found else float("nan"), "recall": hit / ref if ref else float("nan"),
            "abs_err": sum(abs(c[p][0] - c[p][1]) for p in pages)}


def mcnemar(b, c):
    """Exact two-sided McNemar test on discordant pairs b (only A right) and c (only B right)."""
    from math import comb
    n, k = b + c, min(b, c)
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def boot_diff(c1, c2, pages, key, n=2000, seed=0):
    import random
    rnd = random.Random(seed)
    d = []
    for _ in range(n):
        s = [rnd.choice(pages) for _ in pages]
        a, b = stats(c1, s)[key], stats(c2, s)[key]
        if a == a and b == b:
            d.append(b - a)
    d.sort()
    return d[int(0.025 * len(d))], d[int(0.975 * len(d)) - 1]


def cmd_study():
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    allp = sorted(p for s in splits.values() for p in s)
    c2 = page_counts(os.path.join(ROOT, "data/tags"), allp)
    c2r = page_counts(os.path.join(ALL2R, "tags"), allp)
    c25 = page_counts(os.path.join(ALL25, "tags"), allp)
    groups = {"all 410": allp}
    for s in ("train", "val", "test"):
        groups[s] = splits[s]
    for src in ("ie643", "mlt", "ie802", "hlcs"):
        groups[src] = [p for p in allp if p.startswith(src)]
    lines = ["# Surya 2 vs Surya 2.5 on all 410 pages: figure count vs the labels", "",
             "Surya 2 = the regions in data/tags that every reported result uses. Surya 2 (re-run) = the same "
             "model run again today with the pipeline's settings, to show run-to-run variation.", "",
             "| pages | n | label drawings | Surya 2 regions | 2 re-run | 2.5 regions | exact count 2 / 2 re-run / 2.5 | "
             "precision 2 / 2.5 | recall 2 / 2.5 | abs. count error 2 / 2.5 |", "|---|---|---|---|---|---|---|---|---|---|"]
    for name, pages in groups.items():
        a, r, b = stats(c2, pages), stats(c2r, pages), stats(c25, pages)
        lines.append(f"| {name} | {a['pages']} | {a['ref']} | {a['found']} | {r['found']} | {b['found']} | "
                     f"{a['exact']} / {r['exact']} / {b['exact']} | {a['precision']:.3f} / {b['precision']:.3f} | "
                     f"{a['recall']:.3f} / {b['recall']:.3f} | {a['abs_err']} / {b['abs_err']} |")
    only2 = sum(c2[p][0] == c2[p][1] and c25[p][0] != c25[p][1] for p in allp)
    only25 = sum(c2[p][0] != c2[p][1] and c25[p][0] == c25[p][1] for p in allp)
    lines += ["", "## Paired comparison over the same 410 pages", "",
              f"- Pages where only Surya 2 gets the exact count: {only2}. Only Surya 2.5: {only25}. "
              f"Exact McNemar test p = {mcnemar(only2, only25):.4f}.",
              f"- Precision difference (2.5 minus 2), 95% bootstrap interval over pages: "
              f"[{boot_diff(c2, c25, allp, 'precision')[0]:+.3f}, {boot_diff(c2, c25, allp, 'precision')[1]:+.3f}].",
              f"- Recall difference (2.5 minus 2): [{boot_diff(c2, c25, allp, 'recall')[0]:+.3f}, "
              f"{boot_diff(c2, c25, allp, 'recall')[1]:+.3f}].",
              f"- Run-to-run: Surya 2 re-run gives a different region count than data/tags on "
              f"{sum(c2[p][1] != c2r[p][1] for p in allp)} of 410 pages."]
    open(os.path.join(BASE, "study_counts.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["convert", "counts", "match", "convert_all", "study"])
    a = ap.parse_args()
    {"convert": cmd_convert, "counts": cmd_counts, "match": cmd_match, "convert_all": cmd_convert_all,
     "study": cmd_study}[a.cmd]()
