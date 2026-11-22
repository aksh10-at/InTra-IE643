"""Source-attributed textbook footnotes for the IE643 test lectures (secondary novelty).

Pipeline, one footnote per lecture section at most:
  retrieve  (CPU)  each section of the reconstructed lecture (heading + text + figure captions,
                   LaTeX commands removed) is a query. BM25 keyword search ranks the 718 passages
                   of Dive into Deep Learning (books/d2l_passages.json, built by book_index.py).
  generate  (GPU)  the base Qwen2.5-VL-7B (4-bit, no adapter, text only) writes one or two
                   sentences that explain the section using ONLY the top passage, or answers NONE
                   when the passage is about something else. Greedy decoding.
  render    (CPU)  footnotes are added with Pandoc's ^[...] syntax after the section's first text
                   paragraph, each ending with the book section it came from, and the lecture is
                   rebuilt as PDF with the same Pandoc + XeLaTeX settings as the pipeline.
  build / score    a grading page: for each footnote, is it relevant to the section, and is every
                   claim in it supported by the passage?

Why only the passage: the footnote must be checkable against its cited source. A model writing
from memory could add claims the book does not make.

Book: Aston Zhang, Zachary C. Lipton, Mu Li and Alexander J. Smola. Dive into Deep Learning.
Cambridge University Press, 2023. https://d2l.ai (CC BY-SA 4.0).

Usage (from ie643_final/):
  python3 novelty/book_notes.py retrieve
  python3 novelty/book_notes.py generate      # GPU, about 2 minutes
  python3 novelty/book_notes.py render
  python3 novelty/book_notes.py build         # then grade novelty/books/grade_notes.html
  python3 novelty/book_notes.py score
"""
import argparse, html, json, math, os, re, shutil, subprocess
from collections import Counter

from common import ROOT

UNITS = ["ie643_lec03", "ie643_lec09"]      # IE643 test lectures
SKIP_SECTIONS = re.compile(r"announcement", re.I)
OUT = os.path.join(ROOT, "novelty/books")
INDEX = os.path.join(OUT, "d2l_passages.json")
CITE = "Zhang, Lipton, Li and Smola, *Dive into Deep Learning*"
STOP = set("""a an the of to in on for and or is are be by with as at from that this these those it its
into than then so such we our you your can will may not no if when which what how all any each
one two use used using also more most only other some there their them they have has had was
were been being do does did here let given where while about over under between both same
very just like via per i e g x y n s t""".split())

PROMPT = """You write short footnotes that help a student understand lecture notes.
Use ONLY the information in the book passage. Do not add facts that are not in the passage.

Lecture section "{heading}":
{query}

Book passage from Dive into Deep Learning, "{title}: {section}":
{passage}

Write one or two plain sentences that explain the idea of the lecture section, using only the book passage. Do not use LaTeX. If the passage is not about the same idea as the lecture section, answer exactly: NONE"""


def tokens(text):
    out = []
    for w in re.findall(r"[a-z][a-z\-]+", text.lower()):
        pieces = w.split("-") + (["".join(w.split("-"))] if "-" in w else [])  # soft-max -> soft, max, softmax
        for part in pieces:
            if len(part) > 2 and part not in STOP:
                out.append(part[:-1] if len(part) > 4 and part.endswith("s") and not part.endswith("ss") else part)
    return out


def latex_words(text):
    """Keep words inside \\text{...} and \\mathrm{...}, drop the rest of the math."""
    words = " ".join(re.findall(r"\\(?:text|mathrm|operatorname)\{([^}]*)\}", text))
    text = re.sub(r"\$\$.*?\$\$", " ", text, flags=re.S)
    text = re.sub(r"\$[^$]*\$", " ", text)
    return text + " " + words


def lecture_sections(unit):
    md = open(os.path.join(ROOT, f"out/reconstruction_test/outlined/{unit}/{unit}.md")).read()
    body = md.split("---", 2)[2] if md.startswith("---") else md
    parts = re.split(r"^(#{1,3} .+)$", body, flags=re.M)
    sections = []
    for k in range(1, len(parts) - 1, 2):
        heading = parts[k].lstrip("#").strip().rstrip(":")
        text = re.sub(r"<!--.*?-->", " ", parts[k + 1], flags=re.S)
        caps = " ".join(re.findall(r"!\[([^\]]*)\]", text))
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)(\{[^}]*\})?", " ", text)
        query = re.sub(r"\s+", " ", latex_words(text + " " + caps)).strip()
        query = re.sub(r"[\\{}^_]", " ", query)
        if SKIP_SECTIONS.search(heading):
            continue
        sections.append({"unit": unit, "index": len(sections), "heading": heading,
                         "query": re.sub(r"\s+", " ", query)[:900]})
    return sections


class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs = [tokens(d) for d in docs]
        self.k1, self.b = k1, b
        self.avg = sum(len(d) for d in self.docs) / len(self.docs)
        df = Counter(t for d in self.docs for t in set(d))
        n = len(self.docs)
        self.idf = {t: math.log(1 + (n - f + 0.5) / (f + 0.5)) for t, f in df.items()}
        self.tf = [Counter(d) for d in self.docs]

    def scores(self, query):
        q = tokens(query)
        out = []
        for d, tf in zip(self.docs, self.tf):
            s = 0.0
            for t in q:
                if t in tf:
                    s += self.idf[t] * tf[t] * (self.k1 + 1) / (tf[t] + self.k1 * (1 - self.b + self.b * len(d) / self.avg))
            out.append(s)
        return out


def retrieve():
    book = json.load(open(INDEX))
    passages = book["passages"]
    bm = BM25([f"{p['page_title']} {p['section']} {p['section']} {p['text']}" for p in passages])
    rows = []
    for unit in UNITS:
        for sec in lecture_sections(unit):
            sc = bm.scores(sec["heading"] + " " + sec["heading"] + " " + sec["query"])
            top = sorted(range(len(sc)), key=lambda i: -sc[i])[:3]
            sec["top"] = [{"passage": passages[i]["id"], "score": round(sc[i], 2),
                           "where": f"{passages[i]['page_title']}: {passages[i]['section']}"} for i in top]
            rows.append(sec)
            print(f"{unit} | {sec['heading'][:40]:40s} -> {sec['top'][0]['where'][:60]} ({sec['top'][0]['score']})")
    json.dump(rows, open(os.path.join(OUT, "retrieval.json"), "w"), indent=1)


def generate():
    import torch
    from ground_qwen import load_model
    book = {p["id"]: p for p in json.load(open(INDEX))["passages"]}
    rows = json.load(open(os.path.join(OUT, "retrieval.json")))
    model, processor = load_model()
    for r in rows:
        p = book[r["top"][0]["passage"]]
        prompt = PROMPT.format(heading=r["heading"], query=r["query"][:700], title=p["page_title"],
                               section=p["section"], passage=p["text"][:1800])
        messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], return_tensors="pt").to(model.device)
        with torch.inference_mode():
            out = model.generate(**inputs, max_new_tokens=110, do_sample=False)
        reply = processor.batch_decode(out[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)[0].strip()
        r["note"] = None if reply.upper().startswith("NONE") else reply
        r["raw"] = reply
        print(f"{r['unit']} | {r['heading'][:35]:35s} | {reply[:110]}")
    json.dump(rows, open(os.path.join(OUT, "notes.json"), "w"), indent=1)


def footnote(r, book):
    p = book[r["top"][0]["passage"]]
    text = r["note"].replace("\n", " ").strip()
    # The model sometimes writes LaTeX despite the prompt. Turn \( x \) and \[ x \] into $x$
    # (Pandoc does not read \( as maths), drop square brackets that would end the footnote,
    # and strip any LaTeX command left outside maths so XeLaTeX cannot fail on it.
    text = re.sub(r"\\[(\[](.+?)\\[)\]]", lambda m: "$" + m.group(1).strip() + "$", text)
    text = re.sub(r"[\[\]]", "", text)
    if text.count("$") % 2:
        text = text.replace("$", "")
    pieces = text.split("$")
    for i in range(0, len(pieces), 2):  # outside maths only
        pieces[i] = re.sub(r"\\[A-Za-z]+\{([^}]*)\}", r"\1", pieces[i])
        pieces[i] = re.sub(r"\\[A-Za-z]+", "", pieces[i]).replace("\\", "")
    text = "$".join(pieces)
    return f"^[{text} Source: {CITE}, \"{p['page_title']}: {p['section']}\".]"


def render():
    book = {p["id"]: p for p in json.load(open(INDEX))["passages"]}
    rows = json.load(open(os.path.join(OUT, "notes.json")))
    for unit in UNITS:
        src_dir = os.path.join(ROOT, f"out/reconstruction_test/outlined/{unit}")
        md = open(os.path.join(src_dir, unit + ".md")).read()
        head, body = (md.split("---", 2)[1], md.split("---", 2)[2]) if md.startswith("---") else ("", md)
        parts = re.split(r"^(#{1,3} .+)$", body, flags=re.M)
        notes = {r["heading"]: r for r in rows if r["unit"] == unit and r.get("note")}
        added = 0
        for k in range(1, len(parts) - 1, 2):
            heading = parts[k].lstrip("#").strip().rstrip(":")
            r = notes.get(heading)
            if not r:
                continue
            blocks = parts[k + 1].split("\n\n")
            # A separate "Book note" label carries the footnote mark, so the mark never sits
            # after inline maths (where it reads like an exponent). It goes after the section's
            # first plain text paragraph, or right under the heading if there is none.
            at = 1
            for j, blk in enumerate(blocks):
                s = blk.strip()
                if s and not s.startswith(("$$", "!", "<!--", "|", "#", "\\", "*[Diagram")):
                    at = j + 1
                    break
            blocks.insert(at, "*Book note.*" + footnote(r, book))
            parts[k + 1] = "\n\n".join(blocks)
            added += 1
        out_dir = os.path.join(OUT, unit)
        os.makedirs(out_dir, exist_ok=True)
        new_md = ("---" + head + "---" if head else "") + "".join(parts)
        new_md += ("\n\n# Book reference\n\nFootnotes explain sections using passages from: Aston Zhang, "
                   "Zachary C. Lipton, Mu Li and Alexander J. Smola. *Dive into Deep Learning*. Cambridge "
                   "University Press, 2023. <https://d2l.ai>. Licensed CC BY-SA 4.0. Each footnote was written "
                   "by a model from the cited passage only.\n")
        md_path = os.path.join(out_dir, unit + ".md")
        open(md_path, "w").write(new_md)
        pdf = os.path.join(out_dir, unit + ".pdf")
        rd = os.path.join(ROOT, "04_reconstruction")
        cmd = ["pandoc", md_path, "-o", pdf, "--resource-path", src_dir, "--pdf-engine=xelatex",
               "--lua-filter", os.path.join(rd, "fit_display_math.lua"),
               "--include-in-header", os.path.join(rd, "fit_display_math.tex"),
               "--include-in-header", os.path.join(src_dir, "style_header.tex"),
               "--pdf-engine-opt=-no-shell-escape"]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=out_dir, timeout=600)
        print(f"{unit}: {added} footnotes, PDF {'ok: ' + pdf if r.returncode == 0 else 'FAILED: ' + r.stderr[-800:]}")


def build():
    book = {p["id"]: p for p in json.load(open(INDEX))["passages"]}
    rows = [r for r in json.load(open(os.path.join(OUT, "notes.json"))) if r.get("note")]
    cards = []
    for n, r in enumerate(rows, 1):
        p = book[r["top"][0]["passage"]]
        cid = f"n{n:02d}"
        radios = lambda name, opts: "".join(f'<label><input type="radio" name="{cid}_{name}" value="{v}"> {t}</label>'
                                            for v, t in opts)
        cards.append(f"""<section data-id="{cid}"><h2>{n}. {html.escape(r['unit'])}: {html.escape(r['heading'])}</h2>
<p class="q"><b>Lecture section (text only):</b> {html.escape(r['query'][:600])}</p>
<p class="n"><b>Footnote:</b> {html.escape(r['note'])}</p>
<details><summary>Book passage: {html.escape(p['page_title'])}: {html.escape(p['section'])}</summary><pre>{html.escape(p['text'])}</pre></details>
<div><b>Relevant to the section?</b> {radios('rel', [('yes', 'yes'), ('partly', 'partly'), ('no', 'no')])}</div>
<div><b>Every claim supported by the passage?</b> {radios('sup', [('yes', 'yes'), ('no', 'no')])}</div></section>""")
    page = f"""<!doctype html><meta charset="utf-8"><title>Grade book footnotes</title>
<style>body{{font:15px system-ui;max-width:1000px;margin:24px auto;color:#1f2a26}}section{{border-top:1px solid #ddd;padding:12px 0}}
pre{{white-space:pre-wrap;background:#f6f6f3;padding:10px}}.n{{background:#eef5ef;padding:8px}}label{{margin-right:14px}}
#bar{{position:sticky;top:0;background:#fff;padding:8px 0;border-bottom:1px solid #ccc}}</style>
<div id="bar"><b>{len(cards)} footnotes.</b> Relevant: does it help understand this lecture section?
Supported: is every claim in it stated in the book passage (open the passage)? <button onclick="save()">Export grades</button></div>
{''.join(cards)}
<script>function save(){{const g={{}};document.querySelectorAll('input:checked').forEach(i=>g[i.name]=i.value);
const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(g,null,1)],{{type:'application/json'}}));
a.download='note_grades.json';a.click();}}</script>"""
    open(os.path.join(OUT, "grade_notes.html"), "w").write(page)
    print(f"{len(cards)} footnotes -> {OUT}/grade_notes.html")


def score():
    rows = json.load(open(os.path.join(OUT, "notes.json")))
    made = [r for r in rows if r.get("note")]
    g = json.load(open(os.path.join(OUT, "note_grades.json")))
    rel = Counter(g.get(f"n{n:02d}_rel", "ungraded") for n in range(1, len(made) + 1))
    sup = Counter(g.get(f"n{n:02d}_sup", "ungraded") for n in range(1, len(made) + 1))
    both = sum(g.get(f"n{n:02d}_rel") == "yes" and g.get(f"n{n:02d}_sup") == "yes" for n in range(1, len(made) + 1))
    L = ["# Textbook footnotes: results", "",
         f"Lecture sections: {len(rows)}. Footnotes written: {len(made)}. Model answered NONE: {len(rows) - len(made)}.", "",
         "| Measure | Count |", "|---|---|",
         f"| Relevant: yes / partly / no | {rel['yes']} / {rel['partly']} / {rel['no']} |",
         f"| Supported by the passage: yes / no | {sup['yes']} / {sup['no']} |",
         f"| Relevant and supported | {both}/{len(made)} |"]
    open(os.path.join(OUT, "note_scores.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["retrieve", "generate", "render", "build", "score"])
    a = ap.parse_args()
    {"retrieve": retrieve, "generate": generate, "render": render, "build": build, "score": score}[a.action]()
