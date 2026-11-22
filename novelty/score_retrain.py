"""Compare the retrained model (notation_px16: one notation in labels, 1.6M px input) with the
final model (final_clean), both scored against the SAME labels written in one notation, with
both predictions also put in that notation (so only real reading differences count).
Paired bootstrap on test NED via evaluate.py --compare.

Usage (from ie643_final/):  python3 novelty/score_retrain.py
Output: novelty/math/retrain_scores.md
"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "novelty"))
from notation_rescore import norm  # noqa: E402

NROOT = os.path.join(ROOT, "novelty/math/norm/root")  # one-notation labels (made by notation_rescore.py)
OUT = os.path.join(ROOT, "novelty/math")


def normalised_copy(src, dst):
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        if f.endswith(".md"):
            open(os.path.join(dst, f), "w").write(norm(open(os.path.join(src, f)).read()))
    return dst


def run(args):
    return subprocess.run([sys.executable, os.path.join(ROOT, "05_evaluation/evaluate.py")] + args,
                          capture_output=True, text=True, cwd=NROOT).stdout


def main():
    L = ["# Retrain with one notation + 1.6M px (notation_px16) vs final_clean", "",
         "Both predictions and the labels are put in one notation, so notation differences do not count.", ""]
    for split in ("val", "test"):
        old = normalised_copy(os.path.join(ROOT, f"preds/final_clean_{split}"), os.path.join(OUT, f"norm/final_clean_{split}"))
        new = normalised_copy(os.path.join(ROOT, f"preds/notation_px16_{split}"), os.path.join(OUT, f"norm/notation_px16_{split}"))
        js = os.path.join(ROOT, f"data/{split}.jsonl")
        for name, d in (("final_clean", old), ("notation_px16", new)):
            L += [f"## {split}: {name}", "", "```", run(["--pred", d, "--split", js, "--full"]).strip(), "```", ""]
        L += [f"## {split}: paired comparison (final_clean vs notation_px16)", "", "```",
              run(["--pred", old, "--compare", new, "--split", js]).strip(), "```", ""]
    open(os.path.join(OUT, "retrain_scores.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
