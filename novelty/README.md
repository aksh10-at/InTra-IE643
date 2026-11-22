# Novelty phase: getting the figures right

After the intensive assessment we were asked to fix figure placement on dense notebook pages
(IE802) and to show where the errors come from. This folder holds everything from that phase:
the diagnosis, the new figure pipeline, the evaluation, the side studies, the poster and the report.
The full step-by-step log, with every number, is [`NOTES.md`](NOTES.md) (steps 0 to 24).

- Poster: [`poster/InTra_IE643_CourseProject_Poster.pdf`](poster/InTra_IE643_CourseProject_Poster.pdf)
- 2-page report: [`report/InTra_IE643_NoveltyAssessment_report.pdf`](report/InTra_IE643_NoveltyAssessment_report.pdf)
- Web demo with this pipeline: [`../06_interface_v2/`](../06_interface_v2/)

## Main result

IE802 validation and test pages, 23 descriptions that refer to a hand-drawn ground-truth box:

| Figure choice | right drawing | box IoU ≥ 0.5 | localisation error ↓ |
|---|---|---|---|
| A: reading order (old) | 15 | 10 | 0.58 |
| B: Qwen grounding + Hungarian pairing | 21 | 14 | 0.42 |
| B + Surya 2.5 | 21 | 16 | 0.39 |
| B + Surya 2.5 + shared-box re-grounding | 23 | 18 | 0.32 |
| + completeness check (final) | **23** | **19** | **0.30** |

Blind human grade of all 64 distinct crops of arms A, B and C (24 descriptions): Figure Error
Score 0.42 → 0.17, failed figures 9 → 4. On IE643 and MLT pages, 32 of 40 descriptions keep the
same crop and the 8 that change go from 1 to 6 correct.

## What we did, and where the code is

| Step | What | Scripts | Results |
|---|---|---|---|
| Ground truth | Hand-drawn boxes on IE802 pages 041–056 and 8 training pages | — | [`gt/`](gt/) |
| Diagnosis | Four-panel view per page, every failure assigned to one stage | `diagnose_figures.py` | [`diagnostic/`](diagnostic/) |
| Method B | Base Qwen (adapter off) boxes each `[Diagram]` line, Hungarian pairing with Surya boxes | `ground_qwen.py`, `match_figures.py`, `common.py` | [`results/`](results/) |
| Blind re-grade | 64 crops shuffled, method hidden | `regrade.py`, `compare_arms.py`, `render_arm.py` | [`regrade/`](regrade/) |
| Surya 2.5 | Figure precision 0.73 → 0.83 on all 410 pages, recall 0.93 → 0.87 | `surya25.py`, `compare_surya.py` | [`compare_surya/`](compare_surya/) |
| Shared boxes | Whole-page grounding when two descriptions share a box | `ground_page.py`, `crop_fix.py` | [`crop_fix/`](crop_fix/) |
| Completeness check | Only a larger, more complete crop may replace B's crop | `verify_pick2.py`, `compare_pick.py` | [`crop_fix/`](crop_fix/), [`compare_pick2/`](compare_pick2/) |
| Recovered drawings | Surya boxes Qwen never described, kept if Qwen calls them a sketch (training pages: 5 of 9, 0 false) | `recover.py` | [`crop_fix/recover.md`](crop_fix/recover.md) |
| Crop cleaning | Remove text and equation pieces that fall inside a crop | `crop_clean.py` | [`crop_clean/`](crop_clean/) |
| PDF structure | One heading scale, real lists, side captions, fixed LaTeX header | `structure.py`, `structure_filter.lua`, `structure_style.tex` | [`pipeline_final/`](pipeline_final/) |
| Self-check | Qwen's P(yes) for "does this crop show the sketch?" (AUC 0.82) | `verify_crops.py` | [`results/verify/`](results/verify/) |
| Textbook footnotes | One cited sentence per section from *Dive into Deep Learning* with BM25 (18 of 21 relevant and supported) | `book_index.py`, `book_notes.py` | [`user_study/`](user_study/) |
| Maths study | Symbol F1 0.895, notation clean-up, second readers, retrain (not adopted) | `math_coverage.py`, `notation.py`, `notation_rescore.py`, `eq_reread.py`, `retrain_notation.py`, `score_retrain.py` | [`math/`](math/) |
| Tried, not used | Growing boxes along the ink, higher-resolution grounding, a verifier that could also shrink crops | `grow_box.py`, `ground_hr.py`, `verify_pick.py` | [`crop_fix/`](crop_fix/) |
| Poster figures | Dataset example, page 041 before/after | `make_dataset_example.py`, `make_poster_fig041.py`, `make_poster_fig047.py` | [`poster/figures/`](poster/figures/) |

Thresholds (τ = 0.2, shared-box IoU 0.7, completeness margin 0.05) were chosen on the 8 IE802
training pages before any validation or test result was seen.

## Running the scripts

Run from the repo root on the GPU machine, for example `python3 novelty/match_figures.py`. Each
script's docstring says what it reads and writes. Large generated outputs (Surya 2.5 layout dumps,
per-page grounding answers and images, re-rendered PDFs of intermediate arms, the D2L text) are
not in git, see [`.gitignore`](.gitignore). They are rebuilt by the scripts above. The JSON files
the web demo needs (`crop_clean/tune_dev.json`, `crop_fix/*.json`, `results/choices_dev.json`)
are included.
