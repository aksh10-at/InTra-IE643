"""How well does the fine-tuned model read maths, and would more maths data help?

No GPU, no new model run: uses the labels and the final_clean predictions already on disk.

  1. Coverage: every LaTeX command in the val + test labels, how often it appears in the train
     labels, and how often the model writes it on the pages whose label has it (per-command recall).
  2. Errors: every display equation in the test labels is matched to the closest predicted display
     equation on the same page and put in one class:
       exact        identical after the project's norm_latex
       notation     identical after a stronger normalisation (fraction vs slash, \\partial forms,
                    \\cdot vs juxtaposition, \\left/\\right, brackets, \\mathrm/\\text, primes)
       near         1-3 token edits left (a wrong or missing symbol)
       structure    more than 3 token edits (layout, matrices, missing terms)
       missing      no predicted equation is close (NED > 0.6)
Usage (from ie643_final/):  python3 novelty/math_coverage.py
Output: novelty/math/math_coverage.md
"""
import json, os, re, sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "05_evaluation"))
from metrics import norm_latex  # noqa: E402

OUT = os.path.join(ROOT, "novelty/math")
CMD = re.compile(r"\\[A-Za-z]+")
DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
ENV = re.compile(r"\\begin\{(\w+\*?)\}")


def strong(s):
    s = norm_latex(s)
    s = re.sub(r"\\(left|right|big|Big|bigg|Bigg)[lr]?", "", s)
    s = re.sub(r"\\(mathrm|text|textbf|mathbf|operatorname|mathit)\{([^{}]*)\}", r"\2", s)
    s = re.sub(r"\\frac\{([^{}]*)\}\{([^{}]*)\}", r"(\1)/(\2)", s)
    s = re.sub(r"\\dfrac|\\tfrac", r"\\frac", s)
    s = s.replace("\\cdot", "").replace("\\times", "*").replace("*", "")
    s = s.replace("\\,", "").replace("\\;", "").replace("~", "")
    s = re.sub(r"[()\[\]{}]", "", s)
    s = s.replace("'", "\\prime").replace("^\\prime", "\\prime")
    return s


def tokens(s):
    return re.findall(r"\\[A-Za-z]+|.", s)


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def main():
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    lab = lambda p: open(os.path.join(ROOT, "data/annotations", p + ".md")).read()

    def pred(p):
        for sp in ("val", "test"):
            f = os.path.join(ROOT, f"preds/final_clean_{sp}", p + ".md")
            if os.path.exists(f):
                return open(f).read()
        return ""

    train = Counter()
    for p in splits["train"]:
        train.update(set(CMD.findall(lab(p))) | {"env:" + e for e in ENV.findall(lab(p))})
    held = splits["val"] + splits["test"]
    pages_with, hit = Counter(), Counter()
    for p in held:
        L, P = lab(p), pred(p)
        lc = set(CMD.findall(L)) | {"env:" + e for e in ENV.findall(L)}
        pc = set(CMD.findall(P)) | {"env:" + e for e in ENV.findall(P)}
        for c in lc:
            pages_with[c] += 1
            hit[c] += c in pc
    rows = sorted(pages_with, key=lambda c: (-pages_with[c], c))
    unseen = [c for c in rows if train[c] == 0]
    rare = [c for c in rows if 0 < train[c] < 3]

    # equation error classes on test
    cls, examples = Counter(), defaultdict(list)
    for p in splits["test"]:
        P = [e for e in DISPLAY.findall(pred(p))]
        for e in DISPLAY.findall(lab(p)):
            if not P:
                cls["missing"] += 1
                continue
            best = min(P, key=lambda q: lev(tokens(norm_latex(e)), tokens(norm_latex(q))) / max(1, len(tokens(norm_latex(e))), len(tokens(norm_latex(q)))))
            a, b = tokens(norm_latex(e)), tokens(norm_latex(best))
            ned = lev(a, b) / max(1, len(a), len(b))
            if ned > 0.6:
                c = "missing"
            elif a == b:
                c = "exact"
            elif strong(e) == strong(best):
                c = "notation"
            elif lev(tokens(strong(e)), tokens(strong(best))) <= 3:
                c = "near"
            else:
                c = "structure"
            cls[c] += 1
            if len(examples[c]) < 6:
                examples[c].append((p, e.strip()[:90], best.strip()[:90]))
    n = sum(cls.values())
    os.makedirs(OUT, exist_ok=True)
    L = ["# Maths coverage of the fine-tuned model (final_clean)", "",
         f"Held-out pages (val + test): {len(held)}. LaTeX commands or environments used in their labels: {len(rows)}. "
         f"Never in the train labels: {len(unseen)}. In fewer than 3 train pages: {len(rare)}.", "",
         "## Display equations on the 76 test pages, by error class", "",
         "| class | equations | share |", "|---|---|---|"]
    for c in ("exact", "notation", "near", "structure", "missing"):
        L.append(f"| {c} | {cls[c]} | {100 * cls[c] / n:.0f}% |")
    L += [f"| all | {n} | |", "",
          "exact + notation = the maths is right, only the way of writing it differs from the label.", "",
          "## Commands in held-out labels: train pages, held-out pages, model recall", "",
          "| command | train pages | held-out pages with it | model wrote it on those pages |", "|---|---|---|---|"]
    for c in rows:
        L.append(f"| `{c}` | {train[c]} | {pages_with[c]} | {hit[c]}/{pages_with[c]} |")
    L += ["", "## Examples per class (label | prediction)", ""]
    for c in ("notation", "near", "structure", "missing"):
        L.append(f"### {c}")
        for p, e, b in examples[c]:
            L.append(f"- {p}: `{e}` | `{b}`")
        L.append("")
    open(os.path.join(OUT, "math_coverage.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L[:14]))
    print("unseen in train:", unseen)
    print("rare in train:", rare)
    low = [(c, hit[c], pages_with[c], train[c]) for c in rows if pages_with[c] >= 2 and hit[c] / pages_with[c] < 0.6]
    print("low recall (held-out pages >= 2):", low)


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


def symbol_level():
    """Per test page: all maths (display + inline) of label vs prediction as a multiset of symbols
    (commands, letters, digits, operators) after the strong normalisation. Grouping into
    equations no longer matters here."""
    INLINE = re.compile(r"(?<![\\$])\$(?!\$)([^$\n]+?)(?<!\\)\$(?!\$)")
    splits = json.load(open(os.path.join(ROOT, "data/splits.json")))["splits"]
    SYN = {"\\to": "\\rightarrow", "\\le": "\\leq", "\\ge": "\\geq", "\\ne": "\\neq", "\\dfrac": "\\frac",
           "\\tfrac": "\\frac", "\\mathcal": "", "\\mathbb": "", "\\boldsymbol": "", "\\vec": "", "\\bar": "",
           "\\hat": "", "\\tilde": "", "\\quad": "", "\\qquad": "", "\\Big": "", "\\big": "", "\\left": "", "\\right": "",
           "\\text": "", "\\mathrm": "", "\\operatorname": "", "\\boxed": "", "\\underbrace": ""}

    def syms(text):
        m = " ".join(DISPLAY.findall(text) + INLINE.findall(DISPLAY.sub(" ", text)))
        toks = [SYN.get(t, t) for t in re.findall(r"\\[A-Za-z]+|[A-Za-z0-9]|[=+\-<>/^_|]", m)]
        return Counter(t for t in toks if t)

    def pred(p):
        f = os.path.join(ROOT, "preds/final_clean_test", p + ".md")
        return open(f).read() if os.path.exists(f) else ""
    tp = fp = fn = 0
    missed, extra = Counter(), Counter()
    for p in splits["test"]:
        a = syms(open(os.path.join(ROOT, "data/annotations", p + ".md")).read())
        b = syms(pred(p))
        inter = a & b
        tp += sum(inter.values()); fn += sum((a - b).values()); fp += sum((b - a).values())
        missed.update(a - b); extra.update(b - a)
    P, Rc = tp / (tp + fp), tp / (tp + fn)
    L = ["", "## Symbol level (test, all maths on each page as a bag of symbols)", "",
         "Decorations (\\mathcal, \\vec, \\tilde, \\hat, \\bar, \\boxed, \\underbrace, \\text) and spacing are ignored,",
         "and \\to = \\rightarrow, \\le = \\leq. So this counts symbols that are read wrong, dropped or invented.", "",
         f"- Symbols in the labels: {tp + fn}. Precision {P:.3f}, recall {Rc:.3f}, F1 {2 * P * Rc / (P + Rc):.3f}.",
         f"- Most often dropped: {', '.join(f'`{k}` {v}' for k, v in missed.most_common(15))}",
         f"- Most often added: {', '.join(f'`{k}` {v}' for k, v in extra.most_common(15))}"]
    open(os.path.join(OUT, "math_coverage.md"), "a").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "symbols":
    symbol_level()
