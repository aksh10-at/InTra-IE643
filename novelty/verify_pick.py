"""Let the verifier choose the crop: repair instead of only flagging.

For every description with a GT drawing (8 IE802 dev pages, 24 val/test pages) there are up to
three candidate boxes:
  B25   Method B with Surya 2.5 boxes and dup_only grounding (the new pipeline)
  Q     the Qwen box itself (dup_only grounding)
  B2    Method B with Surya 2 boxes and dup_only grounding
Candidates that are nearly the same box (IoU >= 0.9) are merged.

The base Qwen (4-bit, no adapter, same as verify_crops.py) sees each candidate crop with the
description and gives two scores from the next-token logits:
  p_match     "Does it show the sketch described as ...?" (verify_crops.py question)
  p_complete  "Does it show the WHOLE sketch, nothing cut off?"
Selection rules are compared on dev only; the chosen rule is reported on val + test.
Scored with IoU against the hand-drawn GT box of the intended drawing.

Usage (GPU machine, from ie643_final/):
  python3 novelty/verify_pick.py run     # GPU, a few minutes
  python3 novelty/verify_pick.py pick    # no GPU
  python3 novelty/verify_pick.py run_all # GPU: the chosen rule (max_match) on every val + test description
                                         # -> picks_val_test.json, used by structure.py --pick verifier
Output: novelty/crop_fix/verify_pick_scores.json, verify_pick.md
"""
import argparse, json, os
from PIL import Image

from common import ROOT, VAL, TEST, DEV, R, load_gt, load_intended, iou, page_size
import match_figures as M
import crop_fix as F
import verify_crops as V

OUT = os.path.join(ROOT, "novelty/crop_fix")
COMPLETE = ('This image was cut from a page of handwritten lecture notes. Does it show the WHOLE hand-drawn '
            'sketch described as: "{desc}", with all of its parts and labels and nothing cut off at the edges? '
            'Answer No if part of the sketch is missing or if it shows a different sketch. Answer with one word: Yes or No.')


def candidates():
    out = []
    gt, inte = load_gt(), load_intended()
    per = {}
    for surya in ("2.5", "2"):
        orig_pf, orig_lg = R.page_figures, M.load_grounding
        R.page_figures = lambda page, data_dir=None, s=surya: orig_pf(page, F.TAGS[s])
        M.load_grounding = F.grounding_for("dup_only")
        try:
            for name, pages, src in (("dev", DEV, "label"), ("eval", VAL + TEST, "pred")):
                _, _, ch, det = M.evaluate(pages, src, 0.2, gt, inte)
                for r in det:
                    page = next(x for x in pages if x.endswith(r["page"]))
                    i = int(r["desc"][1:]) - 1
                    key = (name, page, i)
                    d = per.setdefault(key, {"set": name, "page": page, "i": i, "desc": r["desc"], "gt": r["gt"],
                                             "text": ch[page]["texts"][i], "cands": {}})
                    d["cands"]["B" + surya.replace(".", "")] = ch[page]["B"][i]
                    if surya == "2.5":
                        d["cands"]["Q"] = M.qwen_boxes(page, len(ch[page]["texts"]))[i]
        finally:
            R.page_figures, M.load_grounding = orig_pf, orig_lg
    for d in per.values():
        g = {x["label"]: x["box"] for x in gt[d["page"]]}
        d["gt_box"] = g[d["gt"]]
        d["others"] = [b for lab, b in g.items() if lab != d["gt"]]
        out.append(d)
    return out


def run():
    import torch
    from ground_qwen import load_model
    model, processor = load_model()
    tok = processor.tokenizer
    yes_id, no_id = tok.encode("Yes", add_special_tokens=False)[0], tok.encode("No", add_special_tokens=False)[0]

    def p_yes(img, q):
        messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": q}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[[img]], return_tensors="pt").to(model.device)
        with torch.inference_mode():
            logits = model(**inputs).logits[0, -1].float()
        return round(torch.softmax(logits[[yes_id, no_id]], dim=0)[0].item(), 4)

    items, images = candidates(), {}
    for d in items:
        page = d["page"]
        img = images.setdefault(page, Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB"))
        W, H = page_size(page)
        d["scores"] = {}
        for name, b in d["cands"].items():
            if b is None:
                continue
            crop = R.clean_crop(img, [b[0] * 1000 / W, b[1] * 1000 / H, b[2] * 1000 / W, b[3] * 1000 / H])
            d["scores"][name] = {"p_match": p_yes(crop, V.QUESTION.format(desc=d["text"])),
                                 "p_complete": p_yes(crop, COMPLETE.format(desc=d["text"]))}
        print(d["set"], page[-3:], d["desc"], d["scores"], flush=True)
    json.dump(items, open(os.path.join(OUT, "verify_pick_scores.json"), "w"), indent=1)


def all_candidates():
    """Candidates for every val + test description (no GT needed)."""
    from common import current_pairing, pred_md
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    pages = [p for sp in ("val", "test") for p in splits[sp] if pred_md(p) is not None]
    per = {}
    for surya in ("2.5", "2"):
        orig_pf, orig_lg = R.page_figures, M.load_grounding
        R.page_figures = lambda page, data_dir=None, s=surya: orig_pf(page, F.TAGS[s])
        M.load_grounding = F.grounding_for("dup_only")
        try:
            for page in pages:
                c = current_pairing(page, pred_md(page))
                if not c["texts"]:
                    continue
                q = M.qwen_boxes(page, len(c["texts"]))
                boxes = M.arm_b(c, page_size(page), q, 0.2)[0]
                for i, t in enumerate(c["texts"]):
                    d = per.setdefault((page, i), {"page": page, "i": i, "text": t, "cands": {}})
                    d["cands"]["B" + surya.replace(".", "")] = boxes[i]
                    if surya == "2.5":
                        d["cands"]["Q"] = q[i] if q[i] and M.informative(q[i], page_size(page)) else None
        finally:
            R.page_figures, M.load_grounding = orig_pf, orig_lg
    return list(per.values())


def run_all():
    import torch
    from ground_qwen import load_model
    model, processor = load_model()
    tok = processor.tokenizer
    yes_id, no_id = tok.encode("Yes", add_special_tokens=False)[0], tok.encode("No", add_special_tokens=False)[0]
    images, out = {}, {}
    for d in all_candidates():
        page = d["page"]
        img = images.setdefault(page, Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB"))
        W, H = page_size(page)
        scores = {}
        for name, b in d["cands"].items():
            if b is None:
                continue
            crop = R.clean_crop(img, [b[0] * 1000 / W, b[1] * 1000 / H, b[2] * 1000 / W, b[3] * 1000 / H])
            messages = [{"role": "user", "content": [{"type": "image"}, {"type": "text", "text": V.QUESTION.format(desc=d["text"])}]}]
            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = processor(text=[text], images=[[crop]], return_tensors="pt").to(model.device)
            with torch.inference_mode():
                logits = model(**inputs).logits[0, -1].float()
            scores[name] = round(torch.softmax(logits[[yes_id, no_id]], dim=0)[0].item(), 4)
        if not scores:
            continue
        best = max(scores, key=lambda c: (scores[c], c == "B25"))  # ties keep Method B with Surya 2.5
        out.setdefault(page, {})[str(d["i"])] = {"pick": best, "box": d["cands"][best], "scores": scores,
                                                  "cands": d["cands"], "text": d["text"]}
        print(page, d["i"] + 1, best, scores, flush=True)
    json.dump({"rule": "max p_match over B25, Q, B2 (ties keep B25)", "picks": out},
              open(os.path.join(OUT, "picks_val_test.json"), "w"), indent=1)


def choose(d, rule):
    s = d["scores"]
    base = "B25"
    if rule == "keep" or base not in s:
        return base
    if rule in ("max_match", "max_complete"):
        k = "p_match" if rule == "max_match" else "p_complete"
        return max(s, key=lambda c: (s[c][k], c == base))
    k, t, m = rule  # switch away from B25 only when it scores below t and another beats it by m
    if s[base][k] >= t:
        return base
    best = max(s, key=lambda c: s[c][k])
    return best if s[best][k] >= s[base][k] + m else base


def score(items, rule):
    rows = []
    for d in items:
        c = choose(d, rule)
        b = d["cands"].get(c)
        v = iou(b, d["gt_box"]) if b else 0.0
        wrong = b is None or any(iou(b, o) > v for o in d["others"])
        rows.append((v, wrong, c))
    n = len(rows)
    return {"n": n, "right_box": sum(v >= 0.5 for v, _, _ in rows), "right_drawing": sum(not w and v > 0 for v, w, _ in rows),
            "le": sum(1 - v for v, _, _ in rows) / n, "switched": sum(c != "B25" for _, _, c in rows)}


def pick():
    items = json.load(open(os.path.join(OUT, "verify_pick_scores.json")))
    dev = [d for d in items if d["set"] == "dev"]
    ev = [d for d in items if d["set"] == "eval"]
    rules = ["keep", "max_match", "max_complete"] + [(k, t, m) for k in ("p_match", "p_complete")
                                                    for t in (0.3, 0.5, 0.7) for m in (0.1, 0.3)]
    L = ["# Verifier picks the crop (candidates: B with Surya 2.5, Qwen box, B with Surya 2)", "",
         "| rule | dev right box | dev right drawing | dev LE | dev switched | val+test right box | val+test right drawing | val+test LE | switched |",
         "|---|---|---|---|---|---|---|---|---|"]
    res = []
    for r in rules:
        a, b = score(dev, r), score(ev, r)
        res.append((r, a, b))
        L.append(f"| {r} | {a['right_box']}/{a['n']} | {a['right_drawing']}/{a['n']} | {a['le']:.3f} | {a['switched']} | "
                 f"{b['right_box']}/{b['n']} | {b['right_drawing']}/{b['n']} | {b['le']:.3f} | {b['switched']} |")
    best = min(res, key=lambda x: (-x[1]["right_drawing"], x[1]["le"], x[1]["switched"]))
    L += ["", f"Chosen on dev: {best[0]}. On val + test: right box {best[2]['right_box']}/{best[2]['n']}, "
              f"right drawing {best[2]['right_drawing']}/{best[2]['n']}, LE {best[2]['le']:.3f} "
              f"(keep B: {res[0][2]['right_box']}/{res[0][2]['n']}, {res[0][2]['right_drawing']}/{res[0][2]['n']}, {res[0][2]['le']:.3f})."]
    open(os.path.join(OUT, "verify_pick.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["run", "pick", "run_all"])
    {"run": run, "pick": pick, "run_all": run_all}[ap.parse_args().action]()
