"""Option 3 of the maths work: retrain with ONE notation in all labels and a larger input image.

Same training script, settings and splits as final_clean (03_recognition/finetune_qwen25vl.py),
with two changes:
  - labels: every label is rewritten with the notation rules of notation_rescore.py (`\\ell`->`l`,
    `\\rightarrow`->`\\to`, ...), so the model sees one form per symbol. Copies only, in
    novelty/math/retrain_data/annotations. data/annotations is not touched.
  - input: max_pixels 1.6 million instead of 1 million (small subscripts).
New run name, so runs/final_clean and preds/final_clean_* are never touched.
Compare with the final model scored under the same notation (notation_rescore.py, step 22).

Usage (GPU machine, from ie643_final/, interface stopped):
  python3 novelty/retrain_notation.py --pilot     # 5 steps: memory and speed
  python3 novelty/retrain_notation.py             # full run + val/test predictions
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "03_recognition"))
sys.path.insert(0, os.path.join(ROOT, "novelty"))
from notation_rescore import norm  # noqa: E402

SHADOW = os.path.join(ROOT, "novelty/math/retrain_data")


def build_shadow():
    os.makedirs(os.path.join(SHADOW, "annotations"), exist_ok=True)
    for name in ("processed", "tags", "splits.json", "train.jsonl", "val.jsonl", "test.jsonl"):
        dst = os.path.join(SHADOW, name)
        if not os.path.lexists(dst):
            os.symlink(os.path.join(ROOT, "data", name), dst)
    src = os.path.join(ROOT, "data/annotations")
    n = 0
    for f in os.listdir(src):
        if f.endswith(".md"):
            t = open(os.path.join(src, f)).read()
            nt = norm(t)
            n += nt != t
            open(os.path.join(SHADOW, "annotations", f), "w").write(nt)
    print(f"labels rewritten with one notation: {n} changed of {len(os.listdir(src))}", flush=True)


if __name__ == "__main__":
    build_shadow()
    import finetune_qwen25vl as F
    F.D = SHADOW
    F.Q.DATA = SHADOW
    pilot = "--pilot" in sys.argv
    sys.argv = ["finetune_qwen25vl.py", "--run-name", "notation_px16" + ("_pilot" if pilot else ""),
                "--max-pixels", "1600000", "--skip-baseline"] + (["--pilot"] if pilot else ["--test"])
    F.main()
