"""Build the passage index for textbook footnotes from Dive into Deep Learning (D2L).

Book: Aston Zhang, Zachary C. Lipton, Mu Li and Alexander J. Smola. Dive into Deep Learning.
Cambridge University Press, 2023. https://d2l.ai. Text licensed CC BY-SA 4.0, which allows
quoting and adapting with attribution. Source: https://github.com/d2l-ai/d2l-en (markdown).

Only conceptual chapters are indexed. Code-only sections (scratch / concise implementations,
dataset loaders, Kaggle) are skipped. Code blocks and d2l markup are removed. Each section
(## or ### heading) becomes one passage, long sections are split at paragraph boundaries into
passages of about 120-220 words.

Usage: python3 book_index.py <path to d2l-en> <output json>
"""
import json, os, re, sys

CHAPTERS = ["chapter_preliminaries", "chapter_linear-regression", "chapter_linear-classification",
            "chapter_multilayer-perceptrons", "chapter_optimization",
            "chapter_appendix-mathematics-for-deep-learning"]
SKIP = re.compile(r"(scratch|concise|implementation|dataset|kaggle|oo-design|index|lookup|pandas|autograd|ndarray)")


def clean(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)              # code blocks
    text = re.sub(r"^%%.*$", " ", text, flags=re.M)                  # notebook tab markers
    text = re.sub(r":(label|eqlabel|width|begin_tab|end_tab)[^\n]*", " ", text)
    text = re.sub(r":(numref|eqref|cite|citet|citep):`([^`]*)`", r"\2", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", text)                # images
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)             # links -> text
    text = re.sub(r"\b(sec|subsec|eq|fig|tab|chap)_[A-Za-z0-9_-]+", "", text)  # leftover cross-reference ids
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_long(paras, lo=120, hi=220):
    out, cur = [], []
    for p in paras:
        cur.append(p)
        if sum(len(x.split()) for x in cur) >= lo:
            out.append("\n\n".join(cur))
            cur = []
    if cur:
        if out and sum(len(x.split()) for x in cur) < lo // 2:
            out[-1] += "\n\n" + "\n\n".join(cur)
        else:
            out.append("\n\n".join(cur))
    return [o for o in out if len(o.split()) >= 30][:12] if out else []


def main(root, dest):
    passages = []
    for ch in CHAPTERS:
        folder = os.path.join(root, ch)
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".md") or SKIP.search(name):
                continue
            raw = clean(open(os.path.join(folder, name), encoding="utf-8").read())
            title = re.search(r"^# (.+)$", raw, flags=re.M)
            title = title.group(1).strip() if title else name
            parts = re.split(r"^(#{2,3} .+)$", raw, flags=re.M)
            sections = [(title, parts[0])] + [(parts[k].lstrip("# ").strip(), parts[k + 1])
                                              for k in range(1, len(parts) - 1, 2)]
            for sec, body in sections:
                if re.match(r"(exercises|discussions?)$", sec.strip(), re.I):
                    continue  # question lists, not explanations
                paras = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
                for n, chunk in enumerate(split_long(paras)):
                    passages.append({"id": f"{name[:-3]}#{len(passages)}", "chapter": ch.replace("chapter_", ""),
                                     "page_title": title, "section": sec, "part": n + 1,
                                     "url": f"https://d2l.ai/{ch}/{name[:-3]}.html", "text": chunk})
    meta = {"book": "Aston Zhang, Zachary C. Lipton, Mu Li and Alexander J. Smola. Dive into Deep Learning. "
                    "Cambridge University Press, 2023. https://d2l.ai",
            "license": "CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/)",
            "source": "https://github.com/d2l-ai/d2l-en", "chapters": CHAPTERS, "passages": passages}
    json.dump(meta, open(dest, "w"), indent=1)
    print(f"{len(passages)} passages from {len(set(p['url'] for p in passages))} pages -> {dest}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
