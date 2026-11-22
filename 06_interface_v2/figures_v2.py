"""v2 figure choice and PDF style for uploads: the novelty pipeline (novelty/NOTES.md steps 11-19).

For every uploaded page with [Diagram] lines:
  1. Qwen (adapter off) gives a rough box per description. Where two descriptions get nearly the
     same box (IoU >= 0.7), those two are grounded again with the whole-page prompt (step 14).
  2. Method B: Hungarian pairing of descriptions with Surya 2.5 boxes by overlap with Qwen's boxes,
     split pieces joined, Qwen's box if the overlap is below TAU 0.2 (steps 3-4, 13).
  3. Fixed verifier: switch to a larger candidate (Qwen box, or union) that contains Method B's box
     only if Qwen finds it more complete by 0.05 and still the described sketch (step 15).
  4. Surya figure boxes no chosen crop covers are added if Qwen says they are sketches (step 17).
Then the PDF is built by the unchanged renderer with: crop cleaning (step 11), structure clean-up
and the side-caption figure layout (steps 12, 19), and the missing LaTeX packages (step 19).
Every decision is written to figure_choice.json in the job folder.
"""
import json
import os
import re
import subprocess
import types
from pathlib import Path

from PIL import Image

import render_document as R
import match_figures as M
import crop_clean as C
import structure as S
import verify_crops as V
import verify_pick as VP
import recover as RC
from common import iou, cover

TAU = 0.2
DUP = 0.7
MARGIN = 0.05
MAX_AREA = 2.5
SKETCH_T = 0.9
HERE = Path(__file__).resolve().parent
NOVELTY = HERE.parent / 'novelty'

_state = {'page': None, 'tags_root': None}
_patched = False


def _install_patches():
    """Crop cleaning and the PDF style are switched in by wrapping two renderer functions and its
    pandoc call (render_document.py itself is not edited)."""
    global _patched
    if _patched:
        return
    orig_pf = R.page_figures

    def page_figures(page, data_dir=None):
        _state['page'] = page
        return orig_pf(page, data_dir)

    def clean_crop(page_img, bbox, pad=0.01):
        C.TAGS_ROOT = _state['tags_root']
        params = C.chosen_params()
        new, info = C.clean(page_img, C.px_box(bbox, page_img.size), C.surya_blocks(_state['page']), dict(params, pad=pad))
        return C.finish(new, info['dark'])

    real = subprocess.run

    def run(cmd, *a, **k):
        if isinstance(cmd, list) and cmd and os.path.basename(cmd[0]) == 'pandoc' and '-o' in cmd \
                and cmd[cmd.index('-o') + 1].endswith('.pdf'):
            cmd = [x + '+lists_without_preceding_blankline' if x.startswith('--from=') else x for x in cmd]
            if not any(x.startswith('--from') for x in cmd):
                cmd += ['--from', 'markdown+lists_without_preceding_blankline']
            cmd += ['--lua-filter', str(NOVELTY / 'structure_filter.lua'),
                    '--include-in-header', str(NOVELTY / 'structure_style.tex')]
        return real(cmd, *a, **k)
    R.page_figures, R.clean_crop = page_figures, clean_crop
    R.subprocess = types.SimpleNamespace(run=run, TimeoutExpired=subprocess.TimeoutExpired)
    _patched = True


def _area(b):
    return (b[2] - b[0]) * (b[3] - b[1])


def _plain_crop(page_img, box):
    """Same cut the verifier saw in the offline experiments (renderer's original clean_crop)."""
    from PIL import ImageOps, ImageStat
    W, H = page_img.size
    b = [box[0] * 1000 / W, box[1] * 1000 / H, box[2] * 1000 / W, box[3] * 1000 / H]
    x0, y0, x1, y1 = (b[0] * W / 1000, b[1] * H / 1000, b[2] * W / 1000, b[3] * H / 1000)
    pad = 0.01
    c = page_img.crop((max(0, int(x0 - pad * W)), max(0, int(y0 - pad * H)), min(W, int(x1 + pad * W)), min(H, int(y1 + pad * H))))
    g = ImageOps.grayscale(c)
    c = ImageOps.autocontrast(ImageOps.invert(g), cutoff=1).convert('RGB') if ImageStat.Stat(g).mean[0] < 100 \
        else ImageOps.autocontrast(c, cutoff=1)
    return R.trim_whitespace(c)


def split_inline_diagrams(md):
    """'a) text [Diagram: X] more' -> 'a) text more' + a separate '[Diagram: X]' block right after.
    The renderer only turns stand-alone [Diagram] blocks into figures, so a description written
    inside a sentence would otherwise get no crop. No word is changed (checked by the caller)."""
    out = []
    for b in R.split_blocks(md):
        if R.DIAGRAM.match(b) or '[Diagram:' not in b or '$$' in b:
            out.append(b)
            continue
        text, found, i = '', [], 0
        while True:
            j = b.find('[Diagram:', i)
            if j < 0:
                text += b[i:]
                break
            depth, k = 0, j
            while k < len(b):
                depth += b[k] == '['
                depth -= b[k] == ']'
                if depth == 0:
                    break
                k += 1
            if k >= len(b):  # unbalanced: leave the block as it is
                text, found = b, []
                break
            text += b[i:j].rstrip(' *') + ' '
            found.append(b[j:k + 1])
            i = k + 1
            if i < len(b) and b[i] == '*':
                i += 1
        out.append(re.sub(r'[ \t]+\n', '\n', re.sub(r'(?<=\S) {2,}', ' ', text)).rstrip() if found else b)
        out.extend(found)
    return '\n\n'.join(o for o in out if o.strip()) + '\n'


def choose_and_render(data, pages, pred_dir, output, ask, title, source_pages, progress):
    """data: job data folder (processed/, tags/ from Surya 2.5). ask(request) -> worker answer.
    Returns the renderer's report plus a figure summary."""
    _install_patches()
    data, output = Path(data), Path(output)
    work = output / 'figure_checks'; work.mkdir(exist_ok=True)
    data2 = output / 'data_v2'; (data2 / 'tags').mkdir(parents=True)
    os.symlink(data / 'processed', data2 / 'processed')
    md_dir = output / 'predictions_v2'; md_dir.mkdir()
    texts_md = {p: (Path(pred_dir) / (p + '.md')).read_text() for p in pages}
    normalised, changes = S.normalise_unit(texts_md)
    inline = 0
    for p, md in list(normalised.items()):
        new = split_inline_diagrams(md)
        if S.words(new) != S.words(md):
            raise ValueError(f'{p}: moving inline diagram descriptions changed the text')
        inline += sum(1 for b in R.split_blocks(new) if R.DIAGRAM.match(b)) - \
            sum(1 for b in R.split_blocks(md) if R.DIAGRAM.match(b))
        normalised[p] = new
    from notation import normalise_math  # one LaTeX notation inside maths (novelty/notation.py)
    notation_changes = 0
    for p in list(normalised):
        normalised[p], n_changed = normalise_math(normalised[p])
        notation_changes += n_changed
    for p, md in normalised.items():
        (md_dir / (p + '.md')).write_text(md)
    log = {'tau': TAU, 'dup_iou': DUP, 'verifier_margin': MARGIN, 'sketch_threshold': SKETCH_T,
           'structure_changes': len(changes), 'inline_descriptions_moved': inline,
           'maths_spans_renotated': notation_changes, 'pages': {}}
    for n, page in enumerate(pages, 1):
        md = normalised[page]
        blocks = R.split_blocks(md)
        desc_idx = [k for k, b in enumerate(blocks) if R.DIAGRAM.match(b)]
        texts = [R.DIAGRAM.match(blocks[k]).group(1).strip() for k in desc_idx]
        img_path = data / 'processed' / (page + '.jpg')
        page_img = Image.open(img_path).convert('RGB')
        W, H = page_img.size
        raw, _ = R.page_figures(page, str(data))
        entry = {'descriptions': len(texts)}
        boxes = []
        if texts:
            progress(f'Placing drawings on page {n} of {len(pages)}')
            nb = max(len(blocks) - 1, 1)
            figs = raw if len(raw) <= len(desc_idx) else R.merge_split_figures(raw, max(1, len(desc_idx)))
            pairs = R.align([k / nb for k in desc_idx], [f['pos'] for f in figs])
            c = {'texts': texts, 'raw': raw, 'figs': figs, 'pairs': pairs}
            q = ask({'kind': 'ground', 'image': str(img_path), 'descs': texts})['boxes']
            dup = {i for i in range(len(q)) for j in range(len(q))
                   if i != j and q[i] and q[j] and iou(q[i], q[j]) >= DUP}
            if dup:
                qp = ask({'kind': 'ground_page', 'image': str(img_path), 'descs': texts})['boxes']
                for i in dup:
                    q[i] = qp[i]
            boxes, how = M.arm_b(c, (W, H), q, TAU)
            picks = []
            for i, b in enumerate(boxes):
                if b is None:
                    picks.append('none'); continue
                cands = {'B': b}
                if q[i] and M.informative(q[i], (W, H)):
                    cands['Q'] = q[i]
                    cands['U'] = [min(b[0], q[i][0]), min(b[1], q[i][1]), max(b[2], q[i][2]), max(b[3], q[i][3])]
                ok = {k: v for k, v in cands.items() if k == 'B' or (cover(b, v) >= 0.9 and _area(v) <= MAX_AREA * _area(b))}
                if len(ok) == 1 or all(iou(v, b) >= 0.95 for v in ok.values()):
                    picks.append('B'); continue
                scores = {}
                for k, v in ok.items():
                    path = str(work / f'{page}_d{i + 1}_{k}.png')
                    _plain_crop(page_img, v).save(path)
                    scores[k] = {'p_match': ask({'kind': 'p_yes', 'image': path, 'question': V.QUESTION.format(desc=texts[i])})['p_yes'],
                                 'p_complete': ask({'kind': 'p_yes', 'image': path, 'question': VP.COMPLETE.format(desc=texts[i])})['p_yes']}
                best = max((k for k in scores if k != 'B' and scores[k]['p_match'] >= 0.5),
                           key=lambda k: scores[k]['p_complete'], default=None)
                if best and scores[best]['p_complete'] >= scores['B']['p_complete'] + MARGIN:
                    boxes[i] = ok[best]; how[i] = 'verifier:' + best
                picks.append(how[i])
            entry.update({'qwen_boxes': q, 'shared_box_regrounded': sorted(dup), 'chosen': boxes, 'source': picks})
        # drawings with no description
        used = [b for b in boxes if b]
        extra = []
        for f in raw:
            b = [f['bbox'][0] * W / 1000, f['bbox'][1] * H / 1000, f['bbox'][2] * W / 1000, f['bbox'][3] * H / 1000]
            if _area(b) < 0.005 * W * H or any(iou(b, u) >= 0.3 or cover(b, u) >= 0.5 for u in used):
                continue
            path = str(work / f'{page}_{f["block"]}_sketch.png')
            _plain_crop(page_img, b).save(path)
            p = ask({'kind': 'p_yes', 'image': path, 'question': RC.SKETCH})['p_yes']
            if p >= SKETCH_T:
                extra.append(b)
        entry['recovered_drawings'] = len(extra)
        # tags for the renderer: one figure block per description at its own position, then extras
        tag_blocks = []
        for k in range(len(blocks)):
            if k in desc_idx and boxes and boxes[desc_idx.index(k)] is not None:
                b = boxes[desc_idx.index(k)]
                tag_blocks.append({'id': f'd{desc_idx.index(k) + 1}', 'type': 'figure', 'order': k + 1,
                                   'bbox': [round(b[0] * 1000 / W), round(b[1] * 1000 / H), round(b[2] * 1000 / W), round(b[3] * 1000 / H)]})
            else:
                tag_blocks.append({'id': f't{k + 1}', 'type': 'text', 'order': k + 1, 'bbox': [0, 0, 1, 1]})
        for j, b in enumerate(extra):
            tag_blocks.append({'id': f'r{j + 1}', 'type': 'figure', 'order': len(blocks) + j + 1,
                               'bbox': [round(b[0] * 1000 / W), round(b[1] * 1000 / H), round(b[2] * 1000 / W), round(b[3] * 1000 / H)]})
        (data2 / 'tags' / (page + '.json')).write_text(json.dumps({'image_size': [W, H], 'blocks': tag_blocks}))
        log['pages'][page] = entry
    (output / 'figure_choice.json').write_text(json.dumps(log, indent=2))
    R.MIN_EXTRA_FIGURE_AREA = 0.0
    _state['tags_root'] = str(data)  # crop cleaning uses the real Surya layout of the upload
    progress('Checking equations and building searchable PDF')
    report = R.render_unit('upload_notes', pages, str(md_dir), str(output / 'documents'), 'pdf',
                           data_dir=str(data2), document_title=title, secure_input=True, source_pages=source_pages)
    return report, log
