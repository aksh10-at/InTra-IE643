"""Confidence flag by self-verification: does the crop show the drawing its caption describes?

Why: geometric agreement (IoU between Qwen's and Surya's boxes) did not predict which crops
humans graded as failures (see NOTES step 9). The failures it misses have well-placed boxes
whose content does not match the description. So the check has to look at the content.

How: the base Qwen2.5-VL-7B (4-bit, no adapter) sees one crop and the description used as its
caption and is asked a yes/no question. The score is P(yes) from the next-token logits of
"Yes" and "No", so every crop gets a number between 0 and 1 without sampling.
A crop is flagged for review when P(yes) < 0.5. The threshold is fixed in advance, not tuned.

Test set: the 64 crops of the blind re-grade (arms A, B, C), each with a human grade.
A crop counts as a failure when the human grade is wrong, not_drawing (severity 1).

Usage (from ie643_final/):
  python3 novelty/verify_crops.py run      # GPU, about 2-3 minutes; writes results/verify/scores.json
  python3 novelty/verify_crops.py score    # no GPU; prints and writes results/verify/verify_scores.md
"""
import argparse, json, os
from PIL import Image

from common import ROOT, R, page_size

OUT = os.path.join(ROOT, "novelty/results/verify")
QUESTION = ('This image was cut from a page of handwritten lecture notes. Does it show the hand-drawn '
            'sketch described as: "{desc}"? Answer Yes if it shows that sketch (even if a small part is '
            'cut off). Answer No if it shows a different sketch, only text or equations, or nothing '
            'recognisable. Answer with one word: Yes or No.')
FAIL = {"wrong", "not_drawing"}


def cards():
    key = json.load(open(os.path.join(ROOT, "novelty/regrade/key.json")))
    for cid, m in key.items():
        if cid.startswith("_"):
            continue
        yield cid, m


def caption(page, desc):
    from common import current_pairing, pred_md
    c = current_pairing(page, pred_md(page))
    return c["texts"][int(desc[1:]) - 1]


def run():
    import torch
    from ground_qwen import load_model  # same 4-bit base model loading as the grounding step
    model, processor = load_model()
    tok = processor.tokenizer
    yes_id = tok.encode("Yes", add_special_tokens=False)[0]
    no_id = tok.encode("No", add_special_tokens=False)[0]
    os.makedirs(OUT, exist_ok=True)
    scores, images = {}, {}
    for cid, m in cards():
        page = m["page"]
        if page not in images:
            images[page] = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
        W, H = page_size(page)
        b = m["box_px"]
        crop = R.clean_crop(images[page], [b[0] * 1000 / W, b[1] * 1000 / H, b[2] * 1000 / W, b[3] * 1000 / H])
        desc = caption(page, m["desc"])
        messages = [{"role": "user", "content": [{"type": "image"},
                                                 {"type": "text", "text": QUESTION.format(desc=desc)}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[[crop]], return_tensors="pt").to(model.device)
        with torch.inference_mode():
            logits = model(**inputs).logits[0, -1].float()
        p_yes = torch.softmax(logits[[yes_id, no_id]], dim=0)[0].item()
        scores[cid] = {"p_yes": round(p_yes, 4), "page": page, "desc": m["desc"], "arms": m["arms"]}
        print(f"{cid} {page} {m['desc']} P(yes) = {p_yes:.3f}")
    json.dump({"question": QUESTION, "model": "Qwen2.5-VL-7B-Instruct base, 4-bit, no adapter",
               "scores": scores}, open(os.path.join(OUT, "scores.json"), "w"), indent=1)


def auc(pos, neg):
    """Probability that a random failure gets a lower P(yes) than a random good crop."""
    if not pos or not neg:
        return float("nan")
    wins = sum((p < n) + 0.5 * (p == n) for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def score():
    s = json.load(open(os.path.join(OUT, "scores.json")))["scores"]
    grades = json.load(open(os.path.join(ROOT, "novelty/regrade/grades.json")))
    rows = [(cid, v["p_yes"], grades[cid]) for cid, v in s.items() if cid in grades]
    fails = [p for _, p, g in rows if g in FAIL]
    goods = [p for _, p, g in rows if g not in FAIL]
    flagged = [(cid, p, g) for cid, p, g in rows if p < 0.5]
    tp = sum(g in FAIL for _, _, g in flagged)
    L = ["# Self-verification as a confidence flag", "",
         f"Test set: {len(rows)} blind-graded crops, {len(fails)} failures (wrong drawing or not a drawing).", "",
         "| Measure | Value |", "|---|---|",
         f"| Crops flagged (P(yes) < 0.5) | {len(flagged)}/{len(rows)} |",
         f"| Failures caught (recall) | {tp}/{len(fails)} |",
         f"| Flagged crops that are failures (precision) | {tp}/{len(flagged) if flagged else 0} |",
         f"| Base rate of failures (precision of random flags) | {len(fails)}/{len(rows)} ({100 * len(fails) / len(rows):.0f}%) |",
         f"| Ranking quality (AUC: a failure scores lower than a good crop) | {auc(fails, goods):.2f} |", "",
         "AUC 0.5 = no better than chance, 1.0 = every failure scores below every good crop.", "",
         "| Card | page | desc | human grade | P(yes) | flagged |", "|---|---|---|---|---|---|"]
    for cid, p, g in sorted(rows, key=lambda r: r[1]):
        v = s[cid]
        L.append(f"| {cid} | {v['page']} | {v['desc']} | {g} | {p:.3f} | {'yes' if p < 0.5 else ''} |")
    open(os.path.join(OUT, "verify_scores.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:12]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["run", "score"])
    a = ap.parse_args()
    run() if a.action == "run" else score()
