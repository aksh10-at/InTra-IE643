"""Grounding at a higher input resolution (2 million pixels instead of 1 million).

The remaining wrong boxes after the shared-box fix are mostly too small (041 D1, 042 D1). A sharper
page may give Qwen tighter boxes. Same prompts and model as ground_qwen.py / ground_page.py; only
the image size changes (load_page_image and the processor's max_pixels).

Usage (GPU machine, from ie643_final/):
  python3 novelty/ground_hr.py per_desc   -> novelty/grounding/all_2m/
  python3 novelty/ground_hr.py page       -> novelty/grounding/page_all_2m/
Then score with crop_fix.py (variants per_desc_2m / dup_only_2m).
"""
import os, sys
from common import ROOT
import ground_qwen as G
sys.path.insert(0, os.path.join(ROOT, "03_recognition"))
import qwen_data

MP = 2_000_000
_orig_load = qwen_data.load_page_image
qwen_data.load_page_image = lambda path, max_pixels=None: _orig_load(path, MP)
_orig_model = G.load_model


def load_model():
    from transformers import AutoProcessor
    model, _ = _orig_model()
    return model, AutoProcessor.from_pretrained(G.MODEL_ID, min_pixels=4 * 28 * 28, max_pixels=MP)


G.load_model = load_model

if __name__ == "__main__":
    which = sys.argv[1]
    if which == "per_desc":
        sys.argv = ["ground_qwen.py", "--set", "all", "--out", os.path.join(ROOT, "novelty/grounding/all_2m")]
        G.main()
    else:
        import ground_page as P
        sys.argv = ["ground_page.py", "--set", "all", "--out", os.path.join(ROOT, "novelty/grounding/page_all_2m")]
        P.main()
