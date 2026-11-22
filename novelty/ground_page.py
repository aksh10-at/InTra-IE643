"""Whole-page grounding: the base Qwen boxes ALL [Diagram] descriptions of a page in one answer.

Why: ground_qwen.py asks for one description at a time, so Qwen never sees the other
descriptions and can give two similar ones the same box (041 D3/D4, 042 D2/D3). That is
Method B's only real error on IE802 (042 D3). Here Qwen gets the numbered list of every
description on the page and is told that each one is a different sketch.

Same model, loading, image size and box conversion as ground_qwen.py (base Qwen2.5-VL-7B,
4-bit, no adapter). Output has the same format, in novelty/grounding/page_all/, so
match_figures.py can use it unchanged (see novelty/crop_fix.py).

Usage (GPU machine, from ie643_final/, environment from ie643_final_env.sh):
  python3 novelty/ground_page.py --set all
Existing page files are never overwritten.
"""
import argparse, json, os, re, sys, time

from common import ROOT, R, load_gt, page_size, descriptions, pred_md, label_md
import ground_qwen as G

sys.path.insert(0, os.path.join(ROOT, "03_recognition"))
PROMPT = ('This is a photo of a handwritten lecture-notes page. It contains these hand-drawn sketches:\n'
          '{items}\n'
          'Each numbered description refers to a DIFFERENT sketch on the page. For every number, output '
          'the bounding box of its sketch, covering the whole sketch with its labels and arrows and no '
          'other sketch. Two numbers must never get the same box. Answer in JSON format as '
          '[{{"id": 1, "bbox_2d": [x1, y1, x2, y2]}}, {{"id": 2, "bbox_2d": [x1, y1, x2, y2]}}, ...].')
ITEM = re.compile(r'"id"\s*:\s*(\d+)[^{}]*?"bbox_2d"\s*:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]', re.S)


def ask(model, processor, image, descs, n):
    import torch
    items = "\n".join(f"{k + 1}. {d}" for k, d in enumerate(descs))
    messages = [{"role": "user", "content": [{"type": "image"},
                                             {"type": "text", "text": PROMPT.format(items=items)}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[[image]], return_tensors="pt").to(model.device)
    start = inputs["input_ids"].shape[1]
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=60 * n + 64, do_sample=False)
    return processor.batch_decode(out[:, start:], skip_special_tokens=True)[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="all", choices=["p047", "eval", "dev", "other", "all"])
    ap.add_argument("--out", default=os.path.join(ROOT, "novelty/grounding/page_all"))
    a = ap.parse_args()
    out = a.out
    os.makedirs(out, exist_ok=True)
    from qwen_data import load_page_image
    gt_all = load_gt()
    model = processor = None
    for page, source in G.pages_for(a.set):
        dest = os.path.join(out, page + ".json")
        if os.path.exists(dest):
            continue
        md = pred_md(page) if source == "pred" else label_md(page)
        if md is None:
            continue
        blocks, idx = descriptions(md)
        if not idx:
            continue
        if model is None:
            t0 = time.time()
            model, processor = G.load_model()
            print(f"model loaded in {time.time() - t0:.0f} s", flush=True)
        W, H = page_size(page)
        image = load_page_image(os.path.join(ROOT, "data/processed", page + ".jpg"), 1_000_000)
        w, h = image.size
        descs = [R.DIAGRAM.match(blocks[k]).group(1).strip() for k in idx]
        t0 = time.time()
        raw = ask(model, processor, image, descs, len(descs))
        found = {}
        for m in ITEM.finditer(raw):
            k = int(m.group(1)) - 1
            if 0 <= k < len(descs) and k not in found:
                x0, y0, x1, y1 = (float(v) for v in m.groups()[1:])
                box = [round(x0 * W / w), round(y0 * H / h), round(x1 * W / w), round(y1 * H / h)]
                box = [max(0, min(W, box[0])), max(0, min(H, box[1])), max(0, min(W, box[2])), max(0, min(H, box[3]))]
                found[k] = box if box[2] > box[0] and box[3] > box[1] else None
        items = [{"index": k, "text": d, "raw": raw if k == 0 else "(see item 0)", "box": found.get(k)}
                 for k, d in enumerate(descs)]
        print(f"{page}: {sum(b is not None for b in found.values())}/{len(descs)} boxes ({time.time() - t0:.1f} s)", flush=True)
        json.dump({"page": page, "descriptions_from": source, "processed_size": [W, H], "model_input_size": [w, h],
                   "model": G.MODEL_ID + " (base, 4-bit, no adapter), whole-page prompt", "prompt": PROMPT,
                   "items": items}, open(dest, "w"), indent=1)
        G.overlay(page, items, gt_all.get(page, []), os.path.join(out, page + ".jpg"))
    print("done:", out)


if __name__ == "__main__":
    main()
