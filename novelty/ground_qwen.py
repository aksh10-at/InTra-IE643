"""Ask the base Qwen2.5-VL-7B (no LoRA adapter) WHERE each [Diagram: ...] description is on the page.

This is the "Qwen decides which" half of Fix B. For every description it asks for one box in
Qwen's grounding format ({"bbox_2d": [x1, y1, x2, y2]}, absolute pixels of the image the model
sees) and converts it back to pixels of the processed page, so it can be compared with Surya's
boxes and the hand-drawn ground truth.

The base model is used, not the fine-tuned adapter: fine-tuning taught the model to write
Markdown only, which may have weakened its box output. Same 4-bit NF4 loading as the pipeline.

Sets of pages:
  p047  just page 047 (feasibility check, about 2 minutes including model loading)
  eval  IE802 val + test pages, descriptions from the fine-tuned model's predictions
  dev   IE802 training pages 001-037 with GT boxes, descriptions from the labels
        (no predictions exist for training pages)
  other IE643 and MLT val + test pages with [Diagram] lines (to check nothing gets worse there)
  all   eval + dev + other

Usage (GPU machine, from ie643_final/, environment from ../env.sh; stop the demo first):
  python3 novelty/ground_qwen.py --set p047
Output: novelty/grounding/<set>/<page>.json and <page>.jpg (blue = Qwen box, green = GT).
Existing page files are never overwritten (delete or use --out to re-run).
"""
import argparse, json, os, re, sys, time

from common import ROOT, VAL, TEST, DEV, R, load_gt, page_size, descriptions, pred_md, label_md

sys.path.insert(0, os.path.join(ROOT, "03_recognition"))
MODEL_ID = "Qwen/Qwen2.5-VL-7B-Instruct"
PROMPT = ('This is a photo of a handwritten lecture-notes page. Locate the hand-drawn sketch that '
          'matches this description: "{desc}". Output its bounding box in JSON format as '
          '[{{"bbox_2d": [x1, y1, x2, y2], "label": "sketch"}}]. The box must cover the whole sketch, '
          'including its labels and arrows, and no other sketch.')
BOX = re.compile(r'"bbox_2d"\s*:\s*\[\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*,\s*([-\d.]+)\s*\]')


def pages_for(name):
    if name == "p047":
        return [("ie802_notes_page047", "pred")]
    if name == "eval":
        return [(p, "pred") for p in VAL + TEST]
    if name == "dev":
        return [(p, "label") for p in DEV]
    if name == "other":
        splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
        return [(p, "pred") for sp in ("val", "test") for p in splits[sp]
                if p.startswith(("ie643_", "mlt_"))]
    if name == "all":
        return pages_for("eval") + pages_for("dev") + pages_for("other")
    raise SystemExit(f"unknown set {name}")


def load_model():
    import torch
    from transformers import AutoProcessor, BitsAndBytesConfig, Qwen2_5_VLForConditionalGeneration
    dtype = torch.bfloat16
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True,
                             bnb_4bit_compute_dtype=dtype)
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        MODEL_ID, quantization_config=bnb, dtype=dtype, device_map={"": 0}, attn_implementation="sdpa")
    model.eval()
    processor = AutoProcessor.from_pretrained(MODEL_ID, min_pixels=4 * 28 * 28, max_pixels=1_000_000)
    return model, processor


def ask(model, processor, image, desc):
    import torch
    messages = [{"role": "user", "content": [{"type": "image"},
                                             {"type": "text", "text": PROMPT.format(desc=desc)}]}]
    text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = processor(text=[text], images=[[image]], return_tensors="pt").to(model.device)
    start = inputs["input_ids"].shape[1]
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=128, do_sample=False)
    return processor.batch_decode(out[:, start:], skip_special_tokens=True)[0]


def overlay(page, items, gt, out_path):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.open(os.path.join(ROOT, "data/processed", page + ".jpg")).convert("RGB")
    d = ImageDraw.Draw(img)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except OSError:
        f = ImageFont.load_default()
    for g in gt:
        d.rectangle(g["box"], outline=(0, 150, 60), width=6)
        d.text((g["box"][0] + 6, g["box"][3] - 36), "G:" + g["label"], fill=(0, 120, 50), font=f)
    for it in items:
        if it["box"]:
            d.rectangle(it["box"], outline=(30, 80, 230), width=6)
            d.text((it["box"][0] + 6, it["box"][1] + 4), "Q:D%d" % (it["index"] + 1), fill=(30, 80, 230), font=f)
    img.thumbnail((1400, 1400))
    img.save(out_path, quality=85)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="p047", choices=["p047", "eval", "dev", "other", "all"])
    ap.add_argument("--out")
    a = ap.parse_args()
    out = a.out or os.path.join(ROOT, "novelty/grounding", "all" if a.set != "p047" else "p047")
    os.makedirs(out, exist_ok=True)
    from qwen_data import load_page_image
    gt_all = load_gt()
    model = processor = None
    for page, source in pages_for(a.set):
        dest = os.path.join(out, page + ".json")
        if os.path.exists(dest):
            print(f"{page}: already done, skipped")
            continue
        md = pred_md(page) if source == "pred" else label_md(page)
        if md is None:
            print(f"{page}: no prediction file, skipped")
            continue
        blocks, idx = descriptions(md)
        if not idx:
            continue
        if model is None:
            t0 = time.time()
            model, processor = load_model()
            print(f"model loaded in {time.time() - t0:.0f} s")
        W, H = page_size(page)
        image = load_page_image(os.path.join(ROOT, "data/processed", page + ".jpg"), 1_000_000)
        w, h = image.size
        items = []
        for n, k in enumerate(idx):
            desc = R.DIAGRAM.match(blocks[k]).group(1).strip()
            t0 = time.time()
            raw = ask(model, processor, image, desc)
            m = BOX.search(raw)
            box = None
            if m:
                x0, y0, x1, y1 = (float(v) for v in m.groups())
                box = [round(x0 * W / w), round(y0 * H / h), round(x1 * W / w), round(y1 * H / h)]
                box = [max(0, min(W, box[0])), max(0, min(H, box[1])), max(0, min(W, box[2])), max(0, min(H, box[3]))]
                if box[2] <= box[0] or box[3] <= box[1]:
                    box = None
            items.append({"index": n, "text": desc, "raw": raw, "box": box})
            print(f"{page} D{n + 1}: {box}  ({time.time() - t0:.1f} s)")
        json.dump({"page": page, "descriptions_from": source, "processed_size": [W, H], "model_input_size": [w, h],
                   "model": MODEL_ID + " (base, 4-bit, no adapter)", "prompt": PROMPT, "items": items},
                  open(dest, "w"), indent=1)
        overlay(page, items, gt_all.get(page, []), os.path.join(out, page + ".jpg"))
    print("done:", out)


if __name__ == "__main__":
    main()
