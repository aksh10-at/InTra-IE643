"""Score the final model with one notation on both sides (label and prediction).

Finding (math_coverage.md): many "maths errors" are notation that our own labels write two ways,
e.g. training labels write `l` 131 times and `\\ell` 15 times, the hand-checked test labels write
`\\ell` 50 times and `l` 4 times. The rules below map each such pair to one form in BOTH the label
and the prediction, then the usual evaluate.py runs. This shows how much of the error is notation.
No model is retrained. Rules are fixed in advance and listed here.

Usage (from ie643_final/):  python3 novelty/notation_rescore.py
Output: novelty/math/notation_rescore.md, novelty/math/norm/ (normalised copies)
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "novelty/math")
RULES = [(r"\\ell(?![A-Za-z])", "l"), (r"\\rightarrow(?![A-Za-z])", r"\\to"), (r"\\longrightarrow(?![A-Za-z])", r"\\to"),
         (r"\\leq(?![A-Za-z])", r"\\le"), (r"\\geq(?![A-Za-z])", r"\\ge"), (r"\\neq(?![A-Za-z])", r"\\ne"),
         (r"\\[dt]frac(?![A-Za-z])", r"\\frac"), (r"\\mathcal\{([A-Za-z])\}", r"\1"), (r"\\times(?![A-Za-z])", r"\\cdot")]


def norm(t):
    for a, b in RULES:
        t = re.sub(a, b, t)
    return t


def main():
    os.makedirs(os.path.join(OUT, "norm/pred"), exist_ok=True)
    src = os.path.join(ROOT, "data/test.jsonl")
    dst = os.path.join(OUT, "norm/test.jsonl")
    with open(src) as f, open(dst, "w") as g:
        for line in f:
            r = json.loads(line)
            for m in r["messages"]:
                if m["role"] == "assistant":
                    for c in (m["content"] if isinstance(m["content"], list) else []):
                        if c.get("type") == "text":
                            c["text"] = norm(c["text"])
                    if isinstance(m["content"], str):
                        m["content"] = norm(m["content"])
            g.write(json.dumps(r) + "\n")
    pdir = os.path.join(ROOT, "preds/final_clean_test")
    for f in os.listdir(pdir):
        if f.endswith(".md"):
            open(os.path.join(OUT, "norm/pred", f), "w").write(norm(open(os.path.join(pdir, f)).read()))
    # evaluate.py reads references from data/annotations/ relative to its working folder, so the
    # normalised run uses a separate folder holding normalised copies of the labels
    nroot = os.path.join(OUT, "norm/root")
    os.makedirs(os.path.join(nroot, "data/annotations"), exist_ok=True)
    for f in os.listdir(os.path.join(ROOT, "data/annotations")):
        if f.endswith(".md"):
            open(os.path.join(nroot, "data/annotations", f), "w").write(norm(open(os.path.join(ROOT, "data/annotations", f)).read()))
    res = {}
    for name, pred, split, cwd in (("as reported", pdir, src, ROOT), ("one notation", os.path.join(OUT, "norm/pred"), dst, nroot)):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "05_evaluation/evaluate.py"), "--pred", pred, "--split", split, "--full"],
                           capture_output=True, text=True, cwd=cwd)
        res[name] = r.stdout
        print("=====", name); print(r.stdout[-2500:]); print(r.stderr[-800:])
    open(os.path.join(OUT, "notation_rescore.md"), "w").write(
        "# Final model on test, scored as reported vs with one notation on both sides\n\nRules: "
        + ", ".join(f"`{a}` -> `{b}`" for a, b in RULES) + "\n\n" + "\n".join(f"## {k}\n\n```\n{v}\n```\n" for k, v in res.items()))


if __name__ == "__main__":
    main()
