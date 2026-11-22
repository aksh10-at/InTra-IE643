"""Rebuild the IE802 val and test PDFs with the figure crops chosen by arm B (or C).

Nothing in the original renderer is changed. The renderer reads Surya boxes from
<data>/tags/<page>.json and pairs them with [Diagram] lines by position. This script writes
a separate tags folder in which each page has exactly one figure block per description, at
the same position as its [Diagram] line, holding the box arm B chose. The renderer's own
alignment then pairs every description with its arm-B box, and everything else (crop
cleaning, captions, equations, outline headings, Pandoc + XeLaTeX) is the same code path as
the original run. Drawings with no description are not added in this version.

Usage (GPU machine not needed; needs pandoc + xelatex, from ie643_final/):
  python3 novelty/render_arm.py            # arm B
  python3 novelty/render_arm.py --arm C
Output: novelty/render_<arm>/<split>/ie802_notes/ie802_notes.pdf (+ .md, figures/, report.json)
"""
import argparse, json, os

from common import ROOT, VAL, TEST, R, page_size, current_pairing, pred_md
import match_figures as M


def write_tags(pages, arm, tau, data_dir):
    os.makedirs(os.path.join(data_dir, "tags"), exist_ok=True)
    link = os.path.join(data_dir, "processed")
    if not os.path.exists(link):
        os.symlink(os.path.join(ROOT, "data/processed"), link)
    chosen = {}
    for page in pages:
        md = pred_md(page)
        c = current_pairing(page, md)
        size = page_size(page)
        q = M.qwen_boxes(page, len(c["texts"])) if c["texts"] else []
        boxes = (M.arm_b(c, size, q, tau)[0] if arm == "B" else M.arm_c(c, size, q)) if c["texts"] else []
        w, h = size
        blocks = []
        for k in range(len(c["blocks"])):
            if k in c["desc_idx"] and boxes[c["desc_idx"].index(k)] is not None:
                n = c["desc_idx"].index(k)
                b = boxes[n]
                bbox = [round(b[0] * 1000 / w), round(b[1] * 1000 / h), round(b[2] * 1000 / w), round(b[3] * 1000 / h)]
                blocks.append({"id": f"{arm.lower()}{n + 1}", "type": "figure", "order": k + 1, "bbox": bbox})
            else:  # placeholder so positions line up with the Markdown blocks
                blocks.append({"id": f"t{k + 1}", "type": "text", "order": k + 1, "bbox": [0, 0, 1, 1]})
        json.dump({"image_size": [w, h], "source": f"arm {arm} figure choice (novelty/render_arm.py)",
                   "blocks": blocks}, open(os.path.join(data_dir, "tags", page + ".json"), "w"), indent=1)
        chosen[page] = [None if b is None else [round(v) for v in b] for b in boxes]
    return chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="B", choices=["B", "C"])
    ap.add_argument("--format", default="pdf", choices=["pdf", "md"])
    a = ap.parse_args()
    tau = json.load(open(os.path.join(ROOT, "novelty/results/choices_dev.json")))["tau"]
    base = os.path.join(ROOT, f"novelty/render_{a.arm}")
    for split, pages in (("val", VAL), ("test", TEST)):
        data_dir = os.path.join(base, "data")
        chosen = write_tags(pages, a.arm, tau, data_dir)
        outline_path = os.path.join(ROOT, f"results/reconstruction/outlines_{split}/ie802_notes.json")
        outline = json.load(open(outline_path))["outline"] if os.path.exists(outline_path) else None
        out_root = os.path.join(base, split)
        os.makedirs(out_root, exist_ok=True)
        r = R.render_unit("ie802_notes", pages, os.path.join(ROOT, f"preds/final_clean_{split}"), out_root,
                          a.format, outline, run_id=f"novelty-arm-{a.arm}", data_dir=data_dir)
        json.dump({"arm": a.arm, "tau": tau, "boxes_px": chosen}, open(os.path.join(out_root, "choices.json"), "w"), indent=1)
        pg = r["pages"]
        print(f"{split}: figures matched {sum(x['matched'] for x in pg)}/{sum(x['descriptions'] for x in pg)}, "
              f"blocks kept {r['preservation']['blocks'] - r['preservation']['missing']}/{r['preservation']['blocks']}, "
              f"equations failed {r['math']['failed']}, output {r['output'] or 'md only'}")


if __name__ == "__main__":
    main()
