"""Consistent document structure for the reconstructed PDFs.

Problem: Qwen writes the writer's headings in four styles (#, ##, a line that is only bold,
a short line ending with ':'), and the level depends on the page, not on the document. With
an outline, every in-page heading is also demoted. The PDF therefore mixes large green
headings, small black headings and bold lines with no visible order. Headings can also end up
alone at the bottom of a page, and a description without a crop is printed as loose italics.

Fix (deterministic; words are never changed, added or removed):
  1. Per document, heading levels are re-based: the highest level used anywhere in the
     document becomes a section, the next a sub-heading. Deeper levels become sub-headings.
  2. A short line ending with ':' that stands alone ("Upcoming:") is marked bold, like the
     other labels the model writes.
  3. At PDF time a Lua filter (structure_filter.lua) turns short bold-only lines into label
     headings, drops a trailing ':' from headings, keeps every heading with the text below
     it, and turns "*[Diagram: ...]*" into a marked "Drawing not extracted" note.
  4. One heading scale (structure_style.tex): section, sub-heading, label.
Every changed page is checked: same blocks in the same order, same words (markup ignored).

The PDFs are built with the novelty figure method (arm B boxes) and, with --crop-clean, the
crop cleaner. Outlines from results/reconstruction are reused, so Qwen is not needed.

Usage (from ie643_final/, no GPU):
  python3 novelty/structure.py render --split test [--crop-clean]
  python3 novelty/structure.py compare --split test       # before/after page images
Output: novelty/structure/<split>/ (pages_md/, <unit>/<unit>.pdf, check.json, compare/)
"""
import argparse, json, os, re, subprocess, sys, types

from common import ROOT, R, pred_md

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "novelty/structure")
HEAD = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
LABEL = re.compile(r"^[A-Z][^$\n]{0,58}:$")


def words(md):
    """Words of a page with all Markdown markup removed (for the no-change check)."""
    t = re.sub(r"[#*_>`]", " ", md)
    return t.split()


def normalise_unit(pages_md):
    """pages_md: {page: markdown}. Returns ({page: new markdown}, list of changes)."""
    levels = [len(m.group(1)) for md in pages_md.values() for b in R.split_blocks(md)
              if (m := HEAD.match(b.strip())) and "\n" not in b.strip()]
    top = min(levels) if levels else 1
    out, changes = {}, []
    for page, md in pages_md.items():
        blocks = R.split_blocks(md)
        new = []
        for b in blocks:
            s = b.strip()
            m = HEAD.match(s) if "\n" not in s else None
            if m:
                lvl = min(max(len(m.group(1)) - top + 1, 1), 2)
                nb = "#" * lvl + " " + m.group(2)
            elif "\n" not in s and LABEL.match(s) and len(s.split()) <= 6 and "**" not in s:
                nb = "**" + s + "**"
            else:
                nb = b
            if nb != b:
                changes.append({"page": page, "from": b[:80], "to": nb[:80]})
            new.append(nb)
        if len(new) != len(blocks) or words("\n".join(new)) != words("\n".join(blocks)):
            raise SystemExit(f"{page}: normalisation changed the content, refusing")
        out[page] = "\n\n".join(new) + "\n"
    return out, changes


def patch_pandoc():
    """Add our Lua filter and style to the renderer's pandoc call (render_document.py itself is
    not edited)."""
    real = subprocess.run

    def run(cmd, *a, **k):
        if isinstance(cmd, list) and cmd and os.path.basename(cmd[0]) == "pandoc" and "-o" in cmd \
                and cmd[cmd.index("-o") + 1].endswith(".pdf"):
            if not any(x.startswith(("--from", "-f")) for x in cmd):
                cmd = cmd + ["--from", "markdown+lists_without_preceding_blankline"]
            cmd = cmd + ["--lua-filter", os.path.join(HERE, "structure_filter.lua"),
                         "--include-in-header", os.path.join(HERE, "structure_style.tex")]
        return real(cmd, *a, **k)
    R.subprocess = types.SimpleNamespace(run=run, TimeoutExpired=subprocess.TimeoutExpired)


SURYA25_TAGS = os.path.join(ROOT, "novelty/surya25/all/data25")  # Surya 2.5 layout of all 410 pages


def use_surya25():
    """Make every reader of Surya layout (pairing, Method B, crop cleaning) see Surya 2.5.
    Only the default data/ folder is redirected; the per-run tags that Method B writes are not."""
    orig = R.page_figures
    default = os.path.join(ROOT, "data")

    def page_figures(page, data_dir=None):
        if data_dir is None or os.path.abspath(data_dir) == default:
            data_dir = SURYA25_TAGS
        return orig(page, data_dir)
    R.page_figures = page_figures
    import crop_clean as C
    C.TAGS_ROOT = SURYA25_TAGS


PICK_FILES = {"verifier": "picks_val_test.json", "verifier2": "picks2_val_test.json"}


def use_verifier_picks(render_arm, pick="verifier"):
    """Method B's box for each description is replaced by the verifier's pick
    (verifier: verify_pick.py run_all; verifier2: the fixed verifier, verify_pick2.py pick)."""
    picks = json.load(open(os.path.join(ROOT, "novelty/crop_fix", PICK_FILES[pick])))["picks"]
    state = {"page": None}
    orig_cp, orig_b = render_arm.current_pairing, render_arm.M.arm_b

    def current_pairing(page, md):
        state["page"] = page
        return orig_cp(page, md)

    def arm_b(c, size, q, tau):
        boxes, how = orig_b(c, size, q, tau)
        for i in range(len(boxes)):
            p = picks.get(state["page"], {}).get(str(i))
            if p and p["box"] is not None:
                boxes[i], how[i] = p["box"], "verifier:" + p["pick"]
        return boxes, how
    render_arm.current_pairing, render_arm.M.arm_b = current_pairing, arm_b


def use_recovered(render_arm):
    """Add the drawings recovered by recover.py (no description in the notes) as extra figures at
    the end of their page. The renderer captions them 'drawing from the page (no description in
    the notes)'."""
    added = json.load(open(os.path.join(ROOT, "novelty/crop_fix/recovered_val_test.json")))["added"]
    R.MIN_EXTRA_FIGURE_AREA = 0.0
    orig = render_arm.write_tags

    def write_tags(pages, arm, tau, data_dir):
        chosen = orig(pages, arm, tau, data_dir)
        for page in pages:
            extra = [d for d in added if d["page"] == page]
            if not extra:
                continue
            path = os.path.join(data_dir, "tags", page + ".json")
            t = json.load(open(path))
            w, h = t["image_size"]
            n = len(t["blocks"])
            for k, d in enumerate(extra):
                b = d["box"]
                t["blocks"].append({"id": f"r{k + 1}", "type": "figure", "order": n + k + 1,
                                    "bbox": [round(b[0] * 1000 / w), round(b[1] * 1000 / h), round(b[2] * 1000 / w), round(b[3] * 1000 / h)]})
            json.dump(t, open(path, "w"), indent=1)
        return chosen
    render_arm.write_tags = write_tags


def cmd_render(split, crop_clean, surya="2", grounding="per_desc", pick="none", recover=False, out_name=None,
               notation=False):
    import render_arm
    if recover:
        use_recovered(render_arm)
    if pick != "none":
        use_verifier_picks(render_arm, pick)
    tau = json.load(open(os.path.join(ROOT, "novelty/results/choices_dev.json")))["tau"]
    if surya == "2.5":
        use_surya25()
    if grounding != "per_desc":
        import crop_fix
        render_arm.M.load_grounding = crop_fix.grounding_for(grounding)
    if crop_clean:
        import crop_clean as C
        params = C.chosen_params()
        state = {"page": None}
        orig_pf = R.page_figures

        def page_figures(page, data_dir=None):
            state["page"] = page
            return orig_pf(page, data_dir)

        def clean_crop(page_img, bbox, pad=0.01):
            new, info = C.clean(page_img, C.px_box(bbox, page_img.size), C.surya_blocks(state["page"]), dict(params, pad=pad))
            return C.finish(new, info["dark"])
        R.page_figures, R.clean_crop = page_figures, clean_crop
    patch_pandoc()
    name = "novelty/structure" if surya == "2" else "novelty/pipeline_surya25"
    if grounding != "per_desc":
        name += "_" + grounding
    if pick != "none":
        name += "_" + pick
    if out_name:
        name = "novelty/" + out_name
    base = os.path.join(ROOT, name, split)
    md_dir = os.path.join(base, "pages_md")
    data_dir = os.path.join(base, "data")
    os.makedirs(md_dir, exist_ok=True)
    units = R.all_units(split)
    check = {"split": split, "crop_clean": crop_clean, "tau": tau, "surya": surya, "grounding": grounding, "pick": pick, "recover": recover, "notation": notation, "units": {}}
    for unit, pages in sorted(units.items()):
        src = {p: pred_md(p) for p in pages if pred_md(p) is not None}
        new, changes = normalise_unit(src)
        if notation:
            from notation import normalise_math
            new = {p: normalise_math(md)[0] for p, md in new.items()}
        for p, md in new.items():
            open(os.path.join(md_dir, p + ".md"), "w").write(md)
        render_arm.write_tags(list(src), "B", tau, data_dir)  # novelty figure choice for every page
        outline_path = os.path.join(ROOT, f"results/reconstruction/outlines_{split}/{unit}.json")
        outline = json.load(open(outline_path))["outline"] if os.path.exists(outline_path) else None
        r = R.render_unit(unit, pages, md_dir, base, "pdf", outline, run_id="novelty-structure", data_dir=data_dir)
        kept = r["preservation"]["blocks"] - r["preservation"]["missing"]
        check["units"][unit] = {"changes": len(changes), "change_list": changes, "blocks_kept": kept,
                                "blocks": r["preservation"]["blocks"], "pdf": r["output"],
                                "pandoc_errors": r.get("pandoc_errors", "")}
        print(f"{unit:14s} heading/label changes {len(changes):3d} | blocks kept {kept}/{r['preservation']['blocks']} | "
              f"pdf {'ok' if r['output'] else 'FAILED'}")
    json.dump(check, open(os.path.join(base, "check.json"), "w"), indent=1)


def cmd_compare(split):
    import fitz
    from PIL import Image
    base = os.path.join(OUT, split)
    out = os.path.join(base, "compare")
    os.makedirs(out, exist_ok=True)
    for unit in sorted(R.all_units(split)):
        before = os.path.join(ROOT, f"results/reconstruction/pdfs_{split}/{unit}.pdf")
        after = os.path.join(base, unit, unit + ".pdf")
        if not (os.path.exists(before) and os.path.exists(after)):
            continue
        db, da = fitz.open(before), fitz.open(after)
        for i in range(min(3, db.page_count, da.page_count)):
            ims = []
            for d in (db, da):
                pm = d[i].get_pixmap(dpi=80)
                ims.append(Image.frombytes("RGB", (pm.width, pm.height), pm.samples))
            s = Image.new("RGB", (ims[0].width + ims[1].width + 30, max(x.height for x in ims)), (200, 200, 200))
            s.paste(ims[0], (0, 0))
            s.paste(ims[1], (ims[0].width + 30, 0))
            s.save(os.path.join(out, f"{unit}_p{i + 1}.png"))
    print("written:", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["render", "compare"])
    ap.add_argument("--split", default="test", choices=["val", "test"])
    ap.add_argument("--crop-clean", action="store_true")
    ap.add_argument("--surya", default="2", choices=["2", "2.5"],
                    help="layout model; 2.5 writes to novelty/pipeline_surya25/ instead of novelty/structure/")
    ap.add_argument("--grounding", default="per_desc", choices=["per_desc", "hybrid", "dup_only"],
                    help="Qwen boxes for Method B (see crop_fix.py); not per_desc adds _<name> to the folder")
    ap.add_argument("--pick", default="none", choices=["none", "verifier", "verifier2"],
                    help="verifier: use the crop the base Qwen verifier scores highest (verify_pick.py run_all)")
    ap.add_argument("--recover", action="store_true", help="add drawings recovered by recover.py")
    ap.add_argument("--out-name", help="output folder under novelty/ (default: built from the options)")
    ap.add_argument("--notation", action="store_true", help="one LaTeX notation inside maths (notation.py)")
    a = ap.parse_args()
    if a.cmd == "render":
        cmd_render(a.split, a.crop_clean, a.surya, a.grounding, a.pick, a.recover, a.out_name, a.notation)
    else:
        cmd_compare(a.split)
