"""Fixed verifier pick: only switch to a LARGER crop that the verifier finds more complete.

The first verifier pick (verify_pick.py) lost the blind check 2-9: it mostly swapped in Qwen's
rough box, which cut off labels, because its question accepts small cut-offs. Fixes:
  1. Candidates: B25 (Method B, Surya 2.5, dup_only), Q (Qwen box), B2 (Method B, Surya 2) and
     U = union of B25 and Q.
  2. A candidate is eligible only if it contains Method B's box (at least 90% of B25 inside it)
     and is at most 2.5 times its area. So a switch can add a cut-off part, never remove one.
  3. Score = p_complete ("the WHOLE sketch, nothing cut off?"), plus p_match >= 0.5 (still the
     described sketch).
  4. Switch only when an eligible candidate beats B25's p_complete by a margin M.
M is chosen on the 8 IE802 dev pages (GT IoU), larger M on ties (fewer switches).

Usage (GPU machine, from ie643_final/):
  python3 novelty/verify_pick2.py run    # GPU, a few minutes: scores every candidate
  python3 novelty/verify_pick2.py pick   # no GPU: choose M on dev, write picks2_val_test.json
Output: novelty/crop_fix/verify_pick2_scores.json, verify_pick2.md, picks2_val_test.json
"""
import argparse, json, os
from PIL import Image

from common import ROOT, R, iou, cover, page_size
import verify_pick as P
import verify_crops as V

OUT = os.path.join(ROOT, "novelty/crop_fix")
MARGINS = [0.05, 0.1, 0.2, 0.3]
MAX_AREA = 2.5


def area(b):
    return (b[2] - b[0]) * (b[3] - b[1])


def add_union(d):
    b, q = d["cands"].get("B25"), d["cands"].get("Q")
    if b and q:
        d["cands"]["U"] = [min(b[0], q[0]), min(b[1], q[1]), max(b[2], q[2]), max(b[3], q[3])]
    return d


def eligible(d, c):
    b, x = d["cands"].get("B25"), d["cands"].get(c)
    if c == "B25" or not b or not x:
        return c == "B25" and bool(b)
    return cover(b, x) >= 0.9 and area(x) <= MAX_AREA * area(b)


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

    gt_items = [dict(add_union(d), kind="gt") for d in P.candidates()]
    all_items = [dict(add_union(d), kind="all") for d in P.all_candidates()]
    images = {}
    for d in gt_items + all_items:
        page = d["page"]
        img = images.setdefault(page, Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB"))
        W, H = page_size(page)
        d["scores"] = {}
        for c, b in d["cands"].items():
            if b is None or not eligible(d, c):
                continue
            crop = R.clean_crop(img, [b[0] * 1000 / W, b[1] * 1000 / H, b[2] * 1000 / W, b[3] * 1000 / H])
            d["scores"][c] = {"p_match": p_yes(crop, V.QUESTION.format(desc=d["text"])),
                              "p_complete": p_yes(crop, P.COMPLETE.format(desc=d["text"]))}
        print(d["kind"], page[-14:], d["i"] + 1, d["scores"], flush=True)
    json.dump({"gt": gt_items, "all": all_items}, open(os.path.join(OUT, "verify_pick2_scores.json"), "w"), indent=1)


def choose(d, m):
    s = d.get("scores", {})
    if "B25" not in s:
        return "B25"
    best = max((c for c in s if c != "B25" and s[c]["p_match"] >= 0.5),
               key=lambda c: s[c]["p_complete"], default=None)
    if best and s[best]["p_complete"] >= s["B25"]["p_complete"] + m:
        return best
    return "B25"


def score(items, m):
    v, wrong, sw = [], 0, 0
    for d in items:
        c = choose(d, m)
        b = d["cands"].get(c)
        x = iou(b, d["gt_box"]) if b else 0.0
        v.append(x)
        wrong += b is None or any(iou(b, o) > x for o in d["others"])
        sw += c != "B25"
    n = len(v)
    return {"n": n, "right_box": sum(x >= 0.5 for x in v), "right_drawing": n - wrong, "le": sum(1 - x for x in v) / n, "switched": sw}


def pick():
    data = json.load(open(os.path.join(OUT, "verify_pick2_scores.json")))
    dev = [d for d in data["gt"] if d["set"] == "dev"]
    ev = [d for d in data["gt"] if d["set"] == "eval"]
    L = ["# Fixed verifier pick (only larger crops that contain Method B's box, judged on completeness)", "",
         "| margin M | dev right box | dev right drawing | dev LE | dev switched | val+test right box | val+test right drawing | val+test LE | switched |",
         "|---|---|---|---|---|---|---|---|---|"]
    base_dev, base_ev = score(dev, 99), score(ev, 99)
    L.append(f"| keep Method B | {base_dev['right_box']}/{base_dev['n']} | {base_dev['right_drawing']}/{base_dev['n']} | {base_dev['le']:.3f} | 0 | "
             f"{base_ev['right_box']}/{base_ev['n']} | {base_ev['right_drawing']}/{base_ev['n']} | {base_ev['le']:.3f} | 0 |")
    res = []
    for m in MARGINS:
        a, b = score(dev, m), score(ev, m)
        res.append((m, a, b))
        L.append(f"| {m} | {a['right_box']}/{a['n']} | {a['right_drawing']}/{a['n']} | {a['le']:.3f} | {a['switched']} | "
                 f"{b['right_box']}/{b['n']} | {b['right_drawing']}/{b['n']} | {b['le']:.3f} | {b['switched']} |")
    m = min(res, key=lambda r: (-r[1]["right_drawing"], round(r[1]["le"], 3), -r[0]))[0]
    picks = {}
    for d in data["all"]:
        c = choose(d, m)
        picks.setdefault(d["page"], {})[str(d["i"])] = {"pick": c, "box": d["cands"].get(c), "scores": d.get("scores", {}),
                                                         "cands": d["cands"], "text": d["text"]}
    n_sw = sum(p["pick"] != "B25" for v in picks.values() for p in v.values())
    L += ["", f"Chosen on dev: M = {m}. Applied to every val + test description: {n_sw} switched away from Method B."]
    json.dump({"rule": f"fixed verifier, M = {m}", "picks": picks}, open(os.path.join(OUT, "picks2_val_test.json"), "w"), indent=1)
    open(os.path.join(OUT, "verify_pick2.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["run", "pick"])
    run() if ap.parse_args().action == "run" else pick()
