"""One LaTeX notation in the output (step 0 of the maths work).

Our labels write several symbols two ways (`l` / `\\ell`, `\\to` / `\\rightarrow`, `\\frac` /
`\\dfrac`, ...), and the model copies both. This maps each pair to one form, ONLY inside maths
($...$ and $$...$$). Text outside maths is never touched. It does not change what the maths says,
only how it is written, so the PDF uses one symbol per idea.

The rules are the ones in notation_rescore.py (used for the "one notation" scores, step 22).
"""
import re

from notation_rescore import RULES

DISPLAY = re.compile(r"\$\$(.+?)\$\$", re.S)
INLINE = re.compile(r"(?<![\\$])\$(?!\$)([^$\n]+?)(?<!\\)\$(?!\$)")


def _norm(t):
    for a, b in RULES:
        t = re.sub(a, b, t)
    return t


def normalise_math(md):
    """Returns (new markdown, number of maths spans changed)."""
    changed = 0

    def disp(m):
        nonlocal changed
        new = _norm(m.group(1))
        changed += new != m.group(1)
        return "$$" + new + "$$"

    def inl(m):
        nonlocal changed
        new = _norm(m.group(1))
        changed += new != m.group(1)
        return "$" + new + "$"
    parts = []
    last = 0
    for m in DISPLAY.finditer(md):  # inline maths only in the text between display blocks
        parts.append(INLINE.sub(inl, md[last:m.start()]))
        parts.append(disp(m))
        last = m.end()
    parts.append(INLINE.sub(inl, md[last:]))
    out = "".join(parts)
    # text outside maths must be identical
    strip = lambda s: INLINE.sub("", DISPLAY.sub("", s))
    if strip(out) != strip(md):
        raise ValueError("notation normalisation touched text outside maths")
    return out, changed
