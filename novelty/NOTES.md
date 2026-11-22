# Novelty work log: figure localisation on IE802 notebook pages

Running record for the poster and the 2-page novelty report. Each step says what we did, why,
and what we found. Numbers are counts on the pages named. Scripts are in this folder.

## Summary for the report (read this first)
- Problem: on dense notebook pages (IE802) the old pipeline placed the wrong drawing under a
  figure caption 9 times out of 24, because it paired Qwen's `[Diagram]` descriptions with
  Surya's boxes by reading order only.
- Diagnosis: a four-panel view per page traced every failure to one stage. Matching (pairing)
  caused most of them (8), then localisation (4) and recognition (1). Placement in the PDF
  caused none.
- Fix: the base Qwen2.5-VL grounds each description to a rough box, and the Hungarian algorithm
  pairs descriptions with Surya boxes by overlap with those boxes. "Surya decides where, Qwen
  decides which." One threshold was tuned on 8 IE802 training pages only.
- Evaluation: hand-drawn GT boxes on 24 IE802 pages, an automatic Localisation Error, and a
  blind human re-grade of 64 crops with a Figure Error Score.
- Result on IE802 val + test (24 descriptions): Figure Error Score 0.42 -> 0.17, failed figures
  9 -> 4, matching failures 8 -> 2. On IE643 + MLT, 32 of 40 descriptions are unchanged and the
  8 that change go from 1 correct to 6 correct (5 of them had no figure before).
- Honest limits: small sample (24 IE802 descriptions), Qwen sometimes gives two similar
  descriptions the same box, one IE643/MLT document got slightly worse (mlt_week09), and
  Qwen-only (C) ties B in the human grades.

## Who does what (final pipeline with the novelty)

| Stage | Model or tool | Trained by us? | Role |
|---|---|---|---|
| Preprocessing | OpenCV rules | no | find page, resize to 2000 px, flatten light, CLAHE, denoise |
| Recognition | Qwen2.5-VL-7B + our QLoRA adapter | yes (fine-tuned) | page image to Markdown, one `[Diagram: description]` line per drawing |
| Layout | Surya (pretrained, frozen) | no | boxes for figures, text and equations, in reading order |
| Grounding (new) | Qwen2.5-VL-7B base, adapter off | no | one rough box per `[Diagram]` description |
| Matching (new) | Hungarian algorithm (scipy) | no | pair descriptions with Surya boxes by overlap with the Qwen box |
| Cropping | `render_document.py` | no | 1% padding, chalkboard inversion, trim to ink |
| Outline | Qwen2.5-VL-7B base, text only | no | section headings |
| Rendering | Pandoc + XeLaTeX | no | Markdown + crops to PDF, figures pinned in place |

## Why this work
- The intensive evaluation asked us to fix figure localisation on IE802 pages and to show where
  the errors come from (detection, matching or placement).
- In the old pipeline Qwen writes a `[Diagram: ...]` line for each drawing but does not say
  where it is. Surya finds drawing boxes but does not know which description they belong to.
  The renderer paired them by reading order only. This worked on slides (32/34 figures) but
  not on dense notebook pages (10/24 by the old grades).

## Step 0. Environment
- The old Qwen environment had been deleted. We rebuilt it in `workspace/envs/qwen` with the
  versions in the report: PyTorch 2.11 (CUDA 12.8), transformers 4.57.6, PEFT 0.21.2,
  bitsandbytes 0.50.2. Script: `workspace/envs/make_qwen_env.sh`. Activate with
  `source workspace/ie643_final_env.sh`.
- A one-page smoke test ran the full pipeline (adapter, Surya, PDF) in 111 s.

## Step 1. Ground-truth boxes
- What: we drew one box per `[Diagram]` line of the label file on the processed images
  (makesense.ai, labels D1, D2 ... in label order, X for a real drawing the label does not
  describe). Files: `gt/*.csv` (pixels of `data/processed/`).
- Pages: IE802 val + test 041-056 (24 described drawings + 3 X) and 8 IE802 training pages for
  development (001, 002, 003, 006, 011, 017, 020, 037).
- Why processed images: Surya's boxes are in the pixels of the processed page, so the
  ground truth has to be too.
- Why training pages: any threshold we tune must be tuned on pages we do not report on.

## Step 2. Diagnosis (no GPU)
- What: `diagnose_figures.py` rebuilds the old pairing exactly as `render_document.py` does
  and draws a four-panel image per page: the page with GT (green) and Surya (orange) boxes,
  the `[Diagram]` lines and the box each was paired with, the crop that was placed, and the PDF
  page where it landed. Output: `diagnostic/`.
- Each of the 24 placed figures was classified by hand, for the old method only, by the stage
  that caused the error (`diagnostic/stage_classification.csv`). Step 8 repeats this
  automatically for all methods.

| Outcome | Stage | Count |
|---|---|---|
| correct | - | 11 |
| wrong drawing | matching | 8 |
| partial crop | detection | 4 |
| wrong drawing | recognition (extra description) | 1 |
| misplaced in PDF | placement | 0 |

- Plus 2 drawings Qwen never described (recognition) and 1 small sketch both models missed.
- Matching errors have three causes: Surya reads the page in a different order than Qwen
  (page 047), a split Surya box takes a slot and shifts every later pairing (page 041), and
  the merge rule glues different drawings together when Qwen wrote fewer lines than Surya
  found boxes (pages 042, 046).
- Placement is not a problem: figures are pinned with `\floatplacement{figure}{H}` and every
  crop appears where its description is.
- The old hand grades disagree with the panels on several figures (for example 046 D1 and
  047 D4 are correct but were graded wrong, 047 D2 is wrong but was graded correct). We
  therefore re-grade the old method and the new one together, blind.

## Step 3. Grounding with the base Qwen (GPU, about 2 s per description)
- What: `ground_qwen.py` asks the base Qwen2.5-VL-7B (4-bit, no LoRA adapter) for one box
  per description in Qwen's grounding format (`bbox_2d`, pixels of the model input image),
  then rescales the box to the processed page. Output: `grounding/all/`.
- Why the base model: fine-tuning trained the model to write Markdown only, which may weaken
  its box output. The base model was pretrained on grounding.
- Page 047 check: all 5 boxes landed on the right sketch (IoU with GT 0.82 to 0.93),
  including the two the old method swapped.
- Problems seen: on some chalkboard pages Qwen returns the whole page, and twice it gave the
  same box to two similar descriptions (041 D3/D4, 042 D2/D3).

## Step 4. Three ways to choose each crop (`match_figures.py`)
- A (old): Surya boxes, merged when there are more boxes than descriptions, paired by
  reading order.
- B (new): Qwen gives a rough box per description. The Hungarian algorithm
  (`scipy.optimize.linear_sum_assignment`) pairs descriptions with Surya boxes so that the
  total overlap with Qwen's boxes is largest, one Surya box per description. Surya pieces that
  lie mostly (60%) inside the same Qwen box are joined, which repairs drawings Surya split.
  If the result overlaps Qwen's box by less than TAU, Qwen's own box is used.
  "Surya decides where, Qwen decides which."
- C (ablation): Qwen's box alone.
- In B and C a Qwen box that is missing or covers more than 60% of the page is ignored and
  the old choice is kept.
- Why Hungarian: it finds the best one-to-one pairing for the whole page at once, so two
  descriptions cannot take the same box and the reading order no longer matters.
- TAU was chosen on the 8 training pages only: 0.2 (14/18 right boxes, best of the values
  tried). It was then fixed for val + test.

Results on IE802 val + test (23 descriptions that refer to a real drawing):

| Arm | right box (IoU >= 0.5 with the intended drawing) | right drawing |
|---|---|---|
| A old | 10/23 | 15/23 |
| B new | 14/23 | 21/23 |
| C Qwen only | 16/23 | 21/23 |

On the training pages B was best (14/18 right boxes vs 10/18 for A and 11/18 for C), so B is
the method we chose. C is reported as an ablation. Full tables: `results/match_scores.md`.

- The 2 remaining wrong drawings in B are both cases where Qwen gave two descriptions the
  same box.
- IoU is measured against our GT boxes, which include labels and arrows. A crop of the right
  drawing that leaves out a label can score below 0.5, so the blind re-grade decides the final
  figure quality.
- On IE643 and MLT val + test (40 descriptions) B changes 8 crops: 6 descriptions that had no
  crop now get one, and 2 merged boxes are replaced. These go into the blind re-grade to check
  that nothing got worse.

## Step 5. Blind re-grade (`regrade.py`)
- Why: IoU against our boxes is strict about labels and arrows, and the old hand grades were
  unreliable. A person judging the actual crops is the final measure of figure quality.
- What: every distinct crop the arms place is cut exactly as the renderer cuts it (1% padding,
  chalkboard inversion, trim to ink). Cards are shuffled with a fixed seed and never say which
  arm made them. A crop shared by two arms (IoU >= 0.95) appears once and its grade counts for
  both. The card-to-arm key is kept in `regrade/key.json`, which graders do not open.
- Cards: 64 in total. IE802 val + test: all 24 descriptions for arms A, B and C (54 distinct
  crops). IE643 + MLT val + test: only the 8 descriptions where B's crop differs from A's
  (10 crops), to check nothing got worse.
- Grades: correct, loose crop, partial crop, wrong drawing, not a drawing. "Loose crop" was
  added during grading after we found a crop that showed the right drawing complete but also
  took in several lines of handwritten text. That text is already transcribed in the Markdown,
  so it would appear twice in the PDF. The earlier grade scale had no place for this and
  counted it as correct. A description where
  an arm places no crop is counted as "no crop" for that arm.

## Step 6. Before/after PDFs (`render_arm.py`)
- What: rebuilds the IE802 val and test documents with arm B's crops through the unchanged
  renderer. The script writes a separate tags folder with one figure block per description, at
  the same position as its `[Diagram]` line, so the renderer's own alignment picks arm B's box.
  Crop cleaning, captions, equations, outline headings and Pandoc + XeLaTeX are the original
  code. Output: `render_B/<split>/ie802_notes/ie802_notes.pdf`.
- Check: 11/11 (val) and 13/13 (test) descriptions get a crop, all content blocks kept
  (39/39, 147/147). On page 047 the two swapped figures are now correct.
- Honest trade-off: TAU = 0.2 (chosen on training pages) keeps Surya's box when it overlaps
  Qwen's box at least a little. On page 047 D1 this keeps Surya's half box, while Qwen's own box
  would have been complete (IoU 0.82). Raising TAU after seeing this would mean tuning on the
  test pages, so we keep 0.2 and report the case.
- Not included: drawings without a description are not added in this version.

## Step 7. Blind re-grade results (64 crops, all graded)

| Pages | Arm | Descriptions | correct | loose | partial | wrong | no crop |
|---|---|---|---|---|---|---|---|
| IE802 val + test | A old | 24 | 13 | 1 | 1 | 9 | 0 |
| IE802 val + test | B new | 24 | 20 | 0 | 0 | 4 | 0 |
| IE802 val + test | C Qwen only | 24 | 20 | 0 | 0 | 4 | 0 |
| IE643 + MLT, crops B changes | A old | 8 | 1 | 1 | 0 | 0 | 6 |
| IE643 + MLT, crops B changes | B new | 8 | 6 | 0 | 1 | 1 | 0 |

- IE802: correct crops rise from 13 to 20 of 24 and wrong drawings fall from 9 to 4. B fixes
  8 descriptions (041 D2, D3, D4, 042 D2, 046 D2, D3, 047 D2, D3) and breaks 1 (042 D3, where
  Qwen gave two descriptions the same box).
- B's 4 wrong: 041 D5 is the extra description (no right answer exists), 042 D1 and 047 D4
  are wrong for every arm, 042 D3 is the duplicate-box case.
- B and C get the same grades. B was chosen on the training pages before grading, so B stays
  the method. C shows that Qwen's grounding does most of the work. Surya still gives tighter
  boxes, which matters for the IoU score (B 14/23 vs C 16/23 is within noise).
- IE643 + MLT: the other 32 of 40 descriptions keep exactly the old crop. Of the 8 that change,
  5 get a correct crop where the old method placed none, 1 loose crop becomes correct
  (ie643_lec03_page010, where the old merge rule had glued text blocks onto the drawing, card
  c003), 1 correct crop becomes partial (mlt_week09_page003) and 1 description gets a wrong
  crop where the old method placed none (mlt_week09_page013).
- Grading was blind: cards shuffled with a fixed seed, method hidden, key opened only after
  all 64 grades were exported.
- The new IE802 count for the old method (13/24) differs from the old Table 12 (10/24). The
  old grades disagreed with the crops on several figures, so both methods were re-graded under
  the same blind protocol and only those numbers are compared.

## Step 8. Error metrics and before/after comparison (`compare_arms.py`)
Two metrics, both per `[Diagram]` description and both 0 = perfect:
- Figure Error Score (FES), from the blind grades: correct 0, loose or partial 0.5, wrong /
  not a drawing / no crop 1, averaged. It measures what the reader of the PDF sees. Failure
  rate = share of descriptions scored 1.
- Localisation Error (LE), automatic: 1 - IoU(chosen box, GT box of the intended drawing).
  It needs no person, so it can be re-run after any change, and it names the failing stage
  (recognition, matching, localisation).

| Pages | Arm | FES | failure rate | mean LE |
|---|---|---|---|---|
| IE802 val + test (24) | A before | 0.42 | 9/24 | 0.58 |
| IE802 val + test (24) | B after | 0.17 | 4/24 | 0.42 |
| IE802 val + test (24) | C Qwen only | 0.17 | 4/24 | 0.37 |
| IE643 + MLT, 8 changed | A before | 0.81 | 6/8 | - |
| IE643 + MLT, 8 changed | B after | 0.19 | 1/8 | - |

- Matching failures on IE802 (automatic stage) fall from 8 to 2.
- Per document: ie802_notes test FES 0.35 -> 0.08, ie802_notes val 0.50 -> 0.27, ie643_lec09
  (4 changed) 1.00 -> 0.00, ie643_lec03 (1 changed) 0.50 -> 0.00, mlt_week06 (1 changed)
  1.00 -> 0.00, mlt_week09 (2 changed) 0.50 -> 0.75. ie643_lec07 and mlt_week03 are unchanged.
- 6 of 72 arm-description pairs get different verdicts from the two metrics (listed in
  `results/comparison/comparison.md`), which is why both are reported.
- Outputs: `results/comparison/comparison.md`, `outcome_chart.png` and one before/after image for
  each of the 12 affected pages.

## Step 9. Confidence flag: which figures should a person check?
- Idea: flag figures that are likely wrong, so a reader reviews only those.
- First attempt, geometry (no GPU): flag a figure when Qwen's box and the chosen box overlap
  little (IoU < 0.5) or when Qwen gave the same box to two descriptions. On IE802 this flags 9 of
  24 figures and catches 2 of B's 4 failures. Random flags would be right 4 times in 24, so this
  is barely better than chance. The two missed failures have well-placed boxes whose content
  does not match the description, which geometry cannot see. We report this as a negative
  result.
- Second attempt, self-verification (`verify_crops.py`, GPU about 2-3 minutes): the base Qwen sees
  the crop and its caption and answers Yes or No to "does this image show the sketch described
  as ...?". The score is P(Yes) from the next-token logits. A crop is flagged when P(Yes) < 0.5,
  a threshold fixed in advance. It is tested on the 64 blind-graded crops, where 15 are failures.
  Measures: recall (failures caught), precision (flags that are failures) against the 23% base
  rate, and AUC (chance = 0.5).
- Results on all 64 graded crops (15 failures): 8 flagged, 5 of them real failures (precision
  5/8 = 63% against a 23% base rate), 5 of 15 failures caught, AUC 0.82 (chance 0.5).
- By method:
  - A (old): 9 failures, 6 flagged, 5 caught. The swapped drawings get P(Yes) near 0
    (041 D2 0.004, 047 D2 0.005, 042 D2 0.014, 041 D3 0.033). The verifier sees exactly the
    matching errors the new method removes.
  - B (new): 5 failures, 4 flagged, 1 caught (041 D5, the extra description), 3 false alarms
    on correct crops. B's remaining failures are subtle (two similar drawings, descriptions that
    fit two sketches, crops wrong for every method), and the verifier mostly misses them.
  - C: 4 failures, none flagged.
- Reading: as an audit, self-verification independently confirms the human finding that the
  old method's errors were swapped drawings. As a flag on top of B it adds little, because B
  already removed the errors it is good at seeing. Both outcomes are reported.
- Caveat: the verifier is the same base Qwen used for grounding, so it is not fully independent
  of method B. The human grades remain the reference.

## Step 10. Textbook footnotes with source attribution (secondary novelty, `book_notes.py`)
- Why: the instructor's secondary suggestion was textbook explanations as footnotes. The aim is
  a footnote a student can check against its cited source.
- Book: Aston Zhang, Zachary C. Lipton, Mu Li and Alexander J. Smola, *Dive into Deep Learning*,
  Cambridge University Press, 2023 (https://d2l.ai). Its text is licensed CC BY-SA 4.0, which
  allows adapting it with attribution. The Goodfellow book is free to read online but not openly
  licensed, so we used D2L.
- Index (`book_index.py`): only conceptual chapters (preliminaries, linear regression, linear
  classification, MLPs, optimisation, maths appendix). Code-only pages and exercise lists are
  skipped. 673 passages of about 120-220 words, each tagged with its page and section.
- Scope: the IE643 test lectures only (lec03, lec09), 25 sections after skipping announcements.
- Retrieval: BM25 keyword search (pure Python, nothing installed). Query = section heading
  (counted twice) + section text + figure captions, with LaTeX commands removed. Two generic
  fixes were made after one look at the results: hyphenated words also count as one word
  ("soft-max" matches "softmax"), and exercise lists were removed from the index. Retrieval
  was then frozen (`books/retrieval.json`).
- Generation: the base Qwen writes one or two plain sentences using ONLY the top passage, or
  answers NONE when the passage is about something else. Greedy decoding.
- Output: each footnote hangs on a small "Book note" label after the section's first text
  paragraph (a mark right after inline maths looked like an exponent) and ends with its source
  section. A "Book reference" section with the licence is added at the end.
- Evaluation: a grading page asks for each footnote whether it is relevant to the section
  (yes / partly / no) and whether every claim is supported by the passage (yes / no). The
  number of NONE answers is also reported.
- Generation run: 25 sections, 21 footnotes, 4 NONE (Perceptron Prediction, Linear separability
  assumption, Vanishing/Exploding Grad, Feedforward Neural Network).
- Rendering fix: the model sometimes wrote LaTeX (for example \(\mathbf{w}\)) despite the
  prompt, and one footnote broke the lec03 PDF. Footnote text is now cleaned before rendering:
  \( \) and \[ \] become $...$, and LaTeX commands left outside maths are removed. Both PDFs
  then build (11 and 10 footnotes).
- Results (21 footnotes, graded by us):

| Measure | Count |
|---|---|
| Relevant: yes / partly / no | 18 / 2 / 1 |
| Supported by the passage: yes / no | 19 / 2 |
| Relevant and supported | 18/21 (86%) |
| Sections where the model answered NONE | 4/25 |

- The 3 that fall short: "Decision Rule" (lec03) retrieved a passage on fairness in deployed
  systems and the model wrote about ethics instead of answering NONE (not relevant, not
  supported). "Soft-max function" (lec09) restated the lecture's hard vs soft assignment idea,
  which the passage does not contain (partly relevant, not supported). "Logistic Regression"
  (lec09) is supported but only partly relevant, because retrieval found a covariate-shift
  passage that mentions logistic regression.
- Reading: when retrieval finds the right passage, the footnotes are almost always good. Both
  real failures start from a wrong passage, and the NONE rule caught 4 such cases but not all.
- Caveat: graded by the team, not blind (there is only one method), so the numbers describe
  quality, not a comparison.

## Update 22 Nov 2026 (evening): better crops and cleaner PDFs

Steps 11 to 16 below were added after the report was written. They are not in the 2-page report.
Short version, on the 23 IE802 val + test descriptions that point at a GT drawing:

| Pipeline | right drawing | right box (IoU >= 0.5) | mean LE | blind check |
|---|---|---|---|---|
| A old (reading order) | 15 | 10 | 0.58 | - |
| B as in the report (Surya 2) | 21 | 14 | 0.421 | 20/24 correct |
| B with Surya 2.5 (step 13) | 21 | 16 | 0.390 | beats Surya 2 by 10 to 2 |
| + whole-page grounding for shared boxes (step 14) | 23 | 18 | 0.320 | automatic only |
| + fixed verifier (step 15) | 23 | 19 | 0.296 | 3 better, 0 worse |

Current best pipeline: Surya 2.5 -> Method B with the shared-box fix -> fixed verifier -> crop
cleaning -> structure clean-up, plus recovered drawings and the new figure layout (steps 17, 19).
PDFs in `pipeline_final/<split>/`.
All 13 val + test documents build and keep every content block.

All blind checks in steps 13 and 15 were graded by an AI grader that saw only the two crops, the page
and the description (random left/right order, no page names, no key). The team then checked every
grade against the crops and confirmed them.

## Step 11. Crop cleaning (`crop_clean.py`)
- Why: the renderer cuts the chosen box plus 1% padding. Handwriting that sits inside the box or the
  padding stays in the figure, so the PDF shows it twice.
- What: find the ink pieces in the crop and remove the ones that lie mostly in a Surya text, equation
  or heading box outside the figure box, but only when the piece is cut by the crop edge. Pieces that
  lie fully in the padding band are also removed. A piece holding 40% or more of the ink is never
  removed, and if more than 35% of the ink would go the original crop is kept.
- Settings were chosen on the 8 dev pages, then fixed.
- Measured against the GT boxes (IE802 val + test, 21 crops): foreign ink 6.7% -> 5.7%, drawing
  ink kept 98.9% (worst crop 90.6%), 10 of 21 crops changed.
- Finding: the crops with the most noise have boxes that are simply too big, and Surya marks no
  text inside them. Cleaning cannot fix that. It is a box problem (steps 13 to 15).
- Output: `crop_clean/` (tune_dev.md, measure_eval.md, sheets/ with before / after / removed in red).

## Step 12. Consistent structure in the PDF (`structure.py`, `structure_filter.lua`, `structure_style.tex`)
- Why: Qwen writes headings four ways (#, ##, a bold-only line, a short line ending in ':'). In val +
  test there are 22 `#`, 48 `##`, 37 bold-only lines and 12 colon labels, and the outline step demotes
  every in-page heading. Headings also ended up alone at the bottom of a page, and a list written
  right under "Upcoming:" was printed as one run-on line.
- What, without changing any word: heading levels are re-based per document, short bold or colon
  lines become one label style, trailing colons are dropped from headings, every heading keeps room
  for the text below it, lists directly under a line are recognised, and a description with no crop
  becomes a marked "Drawing not extracted" note. Three heading sizes only.
- Check: each page keeps the same blocks in the same order and the same words (markup ignored).
  13/13 PDFs build, every block kept. Before/after page images in `structure/<split>/compare/`.

## Step 13. Surya 2.5 instead of Surya 2 (`surya25.py`, `compare_surya.py`)
- Setup: surya-ocr 0.24.0 in a new env `ie643_layout_envs/surya0240`, checkpoint
  datalab-to/surya-ocr-2.5, served by the existing vllm0320 env on port 8002. data/tags is untouched.
  Surya 2.5 tags for all 410 pages are in `surya25/all/data25/`.
- Speed, all 410 pages after one warm-up page: Surya 2 136 s, Surya 2.5 127 s (about 7% faster on
  our GPU), 0 failed pages each.
- Figure count against the labels, all 410 pages: precision 0.733 -> 0.826 (gain interval
  [+0.044, +0.150]), recall 0.931 -> 0.869 (interval [-0.098, -0.030]), exact count 326 -> 336
  (McNemar p = 0.18), total count error 112 -> 86. Running Surya 2 again changed the count on only 1
  page, so this is the model, not noise.
- Inside Method B (IE802 val + test): right box 14 -> 16, mean LE 0.421 -> 0.390, right drawing 21 both.
- Blind paired check of the 20 crops that change: Surya 2.5 better 10, Surya 2 better 2, same 7,
  both wrong 1 (sign test p = 0.039). Per crop, Surya 2 had 8 partial crops, Surya 2.5 had 1. It also
  fixes the 047 D1 half box from step 6.
- Reading: Surya 2.5 finds fewer drawings but gives cleaner boxes. Method B covers the misses with
  Qwen's box, so the switch is safe and the crops get better. Files: `surya25/STUDY.md`,
  `compare_surya/`.

## Step 14. No shared boxes: whole-page grounding (`ground_page.py`, `crop_fix.py`)
- Why: Qwen grounds each description on its own, so two similar descriptions can get the same box.
  That caused B's only real IE802 error (042 D3) and 041 D4.
- What: one extra prompt per page lists every description and says each one is a different sketch.
  Whole-page grounding alone was worse than one description at a time, so it is used only where two
  descriptions got nearly the same box (IoU >= 0.7). About 2 s per page.
- Two ways to use it, compared on the dev pages first:
  - hybrid: the whole page switches to the page-prompt boxes. Chosen before looking at val + test.
    On val + test with Surya 2.5: right drawing 22/23, right box 16/23, LE 0.347.
  - dup_only: only the two descriptions that shared a box take the new boxes. It ties hybrid on dev,
    but it was designed after seeing one val + test case (042 D4 broken by hybrid), so it is a
    post-hoc refinement. Val + test: right drawing 23/23, right box 18/23, LE 0.320.
- Fixed: 042 D3 (0.00 -> 0.93), 041 D4 (0.00 -> 0.67). Output: `grounding/page_all/`,
  `crop_fix/grounding_scores.md`.

## Step 15. Let the verifier choose the crop (`verify_pick.py`, `verify_pick2.py`, `compare_pick.py`)
- Idea: in step 9 the verifier only flagged crops. Here it chooses between candidate boxes: B with
  Surya 2.5, Qwen's own box, B with Surya 2 (and their union in the second version).
- First version (max P(yes) for "does it show the sketch"): on the GT boxes it looked best (LE 0.320
  -> 0.274), but it lost the blind check of the 19 crops it changed: Method B better 9, verifier better
  2, same 8. It mostly swapped in Qwen's rough box, which cut off labels (9 partial crops against 2).
  The question accepts small cut-offs, so it cannot prefer the complete crop. Dropped.
- Lesson: overlap with our GT boxes alone can mislead. A tighter crop of the right drawing can score
  well on IoU and still cut off labels. The visual check is needed.
- Fixed version: a candidate is allowed only if it contains B's box (90% or more) and is at most 2.5
  times its area, it must still pass "is this the described sketch" (P >= 0.5), and it is judged on
  completeness ("the WHOLE sketch, nothing cut off?"). It switches only when it beats B by a margin,
  chosen on dev (0.05).
- Result: val + test right box 18 -> 19, LE 0.320 -> 0.296. 11 of 64 descriptions switch, 7 crops
  change visibly. Blind check: fixed verifier better 3, Method B better 0, same 4 (p = 0.25, too few
  pairs for significance). It completes 047 D3, 048 D1 and mlt_week09_page001.
- Output: `crop_fix/verify_pick*.md`, `crop_fix/picks2_val_test.json`, `compare_pick/`, `compare_pick2/`.

## Step 16. Growing boxes along the ink (`grow_box.py`), small gain, not used
- Finding first: after step 14 most remaining bad crops are too SMALL (the box holds 13% to 45% of the
  drawing), not too big. Shrinking big boxes was therefore not worth building.
- What: add every ink piece that crosses the box edge, unless it is very large or sits in a Surya text
  box. Settings chosen on dev.
- Result on val + test: LE 0.320 -> 0.303, right box unchanged, 3 boxes better and 2 worse. Too small
  to keep. Output: `crop_fix/grow_scores.md`.

## Step 17. Recovering drawings the notes never describe (`recover.py`)
- Why: Qwen writes no [Diagram] line for some drawings, so they never reach the PDF.
- What: every Surya 2.5 figure box that no chosen crop already covers is a candidate. The base Qwen
  answers "is this a hand-drawn sketch, not only text or equations?". P(yes) >= T keeps it, and it is
  added at the end of its page with the caption "drawing from the page (no description in the notes)".
  T chosen on dev (0.9).
- Result: dev 5 of 9 missing drawings recovered, 0 false. Val + test 1 of 6 recovered (042 D4),
  0 false. Only 2 drawings are added on all val + test pages. The other missing drawings were never
  boxed by Surya, so there is nothing to recover.

## Step 18. Higher-resolution grounding (`ground_hr.py`), no gain, not used
- Qwen saw the page at about 2 million pixels instead of 1 million for both grounding prompts.
- Surya 2.5 + dup_only: dev right box 12 -> 13, LE 0.355 -> 0.336, but val + test right drawing
  23 -> 21, right box 18 -> 16, LE 0.320 -> 0.361. One description at a time got worse on both.
  No consistent gain, so we keep 1 million pixels (cheaper, same as every other step).

## Step 19. Figure layout and a renderer bug (`structure_filter.lua`, `structure_style.tex`)
- Most figures were drawn at the maximum size with a long caption under them, which left large white
  gaps. Each figure is now one block with the drawing on the left and its caption beside it.
  Pages: lec09 9 -> 8, IE802 test 13 -> 12, mlt_week09 11 -> 9. Every block kept.
- Bug found: the renderer loads `float` with `\floatplacement{figure}{H}`, `fvextra` and `cancel`
  through the YAML header-includes, but pandoc drops header-includes when `--include-in-header` is
  also given, and the renderer gives it. So figures in the earlier PDFs were not pinned in place, and
  `\cancel` was not loaded. Tested with a minimal file. `structure_style.tex` now loads them.
  Step 2 found no placement errors by looking at the PDFs, so that finding still stands, but the
  reason given there ("figures are pinned") was not true for the earlier PDFs.
- All improvements together (steps 11 to 15, 17, 19): `pipeline_final/<split>/<unit>/<unit>.pdf`.

## Step 20. How well does the model read maths? (`math_coverage.py`, output `math/math_coverage.md`)
- Symbol level (test, all maths on a page as a bag of symbols, decorations ignored): precision 0.884,
  recall 0.906, F1 0.895. The biggest single error is a convention: labels write `\ell`, the model
  writes `l`.
- Equation level, most remaining errors are grouping (two label equations written as one block or the
  reverse) and labelling conventions (`\mathcal`, `\underbrace`, `\boxed`), not misread symbols.
- Only 4 commands in held-out labels never occur in training (`\Phi`, `\Theta`, `\ni`, `\notin`).
- Public handwritten-maths data (MathWriting, CROHME, HME100K) would mainly help those rare symbols.
  Cheaper first step: consistent label notation and metric synonyms. A targeted external-data run is
  planned for after the assessment. Details and plan in `math/math_coverage.md`.

## Step 21. Demo and user study
- The demo start script used the old `ie643_env.sh`, whose Python was deleted. `START_INTERFACE.sh`
  now sources `ie643_final_env.sh` and adds `~/.local/bin` (cloudflared) to PATH. `manage.py doctor`
  passes with the rebuilt env. A copy is in `ie643_final/START_INTERFACE.sh`.
- The interface still uses the first-version pipeline (Surya 2, reading-order pairing). Moving it to
  the novelty pipeline needs grounding inside the recognition worker (adapter switched off for one
  call per description). Planned after the submission, in a copy so the working demo stays.
- User study (promised in the report): `user_study/STUDY_FORM.md` and the four PDFs (lec03 and lec09,
  with and without footnotes). Each participant reads one lecture with footnotes and the other
  without, groups A and B alternate. To run on 23 or 25 Nov.

## Step 22. Maths: how much of the error is notation? (`notation_rescore.py`, output `math/notation_rescore.md`)
- The `\ell` "error" from step 20 is a labelling inconsistency between our own splits: training
  labels write `l` 131 times and `\ell` 15 times, the hand-checked test labels write `\ell` 50 times
  and `l` 4 times. `\to` and `\rightarrow` are mixed in every split (training 117 vs 155).
- Rescoring the final model with one notation on BOTH label and prediction (fixed rules: `\ell`->`l`,
  `\rightarrow`->`\to`, `\leq`->`\le`, `\dfrac`->`\frac`, `\mathcal{X}`->`X`, `\times`->`\cdot`, ...):
  NED 0.311 -> 0.302, exact equation match 0.137 -> 0.168, equation F1 0.338 -> 0.354,
  CER 0.325 -> 0.314.
- So notation explains a small, real part of the maths error. Retraining on consistent labels could
  at best match this, so it was not run. External maths data stays a later experiment (step 20).
- Note: evaluate.py reads references from `data/annotations/` relative to its working folder, so the
  normalised run uses normalised label copies in `math/norm/root/`.

## Step 23. Interface v2 with the novelty pipeline (`06_interface_v2/`, `START_INTERFACE_V2.sh`)
- A copy of the interface. v1 (`06_interface/`, port 7860, Surya 2 on 8001) is unchanged and stays
  the fallback. v2 uses port 7861, Surya on 8002, `out/interface_service_v2/`, `out/upload_jobs_v2/`.
- Layout: Surya 2.5 (surya0240 client env, same vllm0320 server env).
- The persistent Qwen worker answers three new requests with the adapter switched off (so it is the
  base Qwen, no second model in memory): per-description grounding, whole-page grounding, and a
  yes/no score. `figures_v2.py` then runs Method B with the shared-box fix, the fixed verifier and the
  recovered drawings, and builds the PDF with crop cleaning, the structure clean-up, the side-caption
  figure layout and the missing LaTeX packages. Every decision goes to `figure_choice.json` in the job.
- New for uploads only: a `[Diagram: ...]` written inside a sentence is moved into its own block right
  after it (no word changed), so it becomes a figure with a caption. On page 047 this gave every one of
  the 4 descriptions the right drawing (before: 2 drawings were "no description" and one caption got
  the wrong drawing).
- Checks: 26/26 interface unit tests pass (one test updated for the new Surya version), `manage.py
  doctor` passes, the web service starts on 7861 and answers. Command-line runs: 047 + 042 in 78 s,
  26/26 blocks kept, lec09 p002 + mlt_week09 p004 in 74 s, 17/17 blocks kept, 0 equation failures.
- Start: `bash ~/workspace/ie643_final/START_INTERFACE_V2.sh`. Run only one of v1 and v2 at a time.
- The demo start script for v1 also pointed to the deleted env and was fixed (step 21).

## Step 24. Improving the maths (`notation.py`, `eq_reread.py`, `retrain_notation.py`)
- Option 0, one notation in the output: inside $...$ and $$...$$ only, each symbol that our labels
  write two ways is written one way (rules of notation_rescore.py). Text outside maths is checked to
  be unchanged. Used in `pipeline_final/` (`structure.py --notation`) and always in interface v2.
- Options 1 and 2, second readings of display equations:
  - Surya 2.5 full-page OCR on all val + test pages (49 s, 213 equation blocks, LaTeX in <math> tags).
  - The final model re-reads each Surya equation block, cut out and enlarged up to 3x (about 6 min).
  - Rules compared on the 31 val pages: replace the page equation with the crop reading, with
    Surya's reading, or only when crop and Surya agree with each other ("vote").
  - Surya alone made things worse at every threshold. The crop reading helped exact match on val but
    raised NED at looser thresholds. The vote was chosen on val (exact equation match 0.198 -> 0.246,
    equation F1 0.437 -> 0.463, NED unchanged, 5 equations replaced).
  - On test the vote replaced 14 equations: 4 became right, 4 that were right became wrong (all 4 on
    MLT pages, which the model already reads well), the rest stayed wrong. Scores unchanged
    (NED 0.311, exact match 0.137, equation F1 0.338). No reliable gain, so it is not used.
    Output: `math/reread/reread_scores.md`.
- Option 3, retrain with one notation in all labels and 1.6 million pixels input (run name
  `notation_px16`, same settings otherwise, labels rewritten only in copies under
  `math/retrain_data/`). Pilot: 42 s per step, peak GPU 11.9 GB, about 1.3 h for 3 epochs.
  Started 22 Nov 20:05. Compare with `python3 novelty/score_retrain.py` (both models and the labels
  in one notation, paired bootstrap). Result: see `math/retrain_scores.md` once it has run.
- Option 3 result (22 Nov 21:50, `math/retrain_scores.md`): both models and the labels in one notation.
  Val NED 0.315 -> 0.294 (paired -0.022, CI -0.054 to +0.010). Test NED 0.302 -> 0.307 (paired +0.005,
  CI -0.010 to +0.021, better on 38 pages, worse on 35). Test exact equation match 0.168 -> 0.231,
  equation F1 0.354 -> 0.360, but equation edit score 0.710 -> 0.676 and text CER 0.227 -> 0.253.
  Mixed, no significant overall gain, so final_clean stays the model. The new adapter is kept in
  `runs/notation_px16/` (nothing else was overwritten).

## Reproduce steps 11 to 16 (from ie643_final/, after `source ../ie643_final_env.sh`)
1. `python3 novelty/crop_clean.py tune`, then `measure`, then `sheet`
2. Surya 2.5 layout: start the vLLM server for datalab-to/surya-ocr-2.5 on port 8002 (command in
   `surya25/SUMMARY.md`), run `ie643_layout_envs/surya0240/bin/surya_layout` on `surya25/all/processed`,
   stop the server, then `python3 novelty/surya25.py convert_all` and `study`
3. `python3 novelty/ground_page.py --set all` (GPU, about 2 minutes), then `python3 novelty/crop_fix.py`
4. `python3 novelty/verify_pick2.py run` (GPU, about 4 minutes), then `pick`
5. `python3 novelty/structure.py render --split val --crop-clean --surya 2.5 --grounding dup_only --pick verifier2`
   (and `--split test`)
6. Blind checks: `python3 novelty/compare_surya.py build` and
   `python3 novelty/compare_pick.py build --picks picks2_val_test.json --out compare_pick2`, grade, then `score`

## Limitations
- Small sample: 24 IE802 descriptions and 8 changed IE643/MLT descriptions. Differences of one or
  two figures (for example B vs C) are within noise.
- Qwen grounds each description on its own, so two similar descriptions can get the same box
  (041 D3/D4, 042 D2/D3). One of these is B's only real error on IE802.
- Recognition errors are out of reach of this fix: an extra description (041 D5) and drawings
  with no description (042 GT D4, 046 GT D2) stay wrong for every method.
- The GT box for page 048 D1 includes the text lines beside the drawing, so every method scores
  a low IoU there. The human grade is not affected.
- Drawings without any description are not added in the arm-B PDFs.

## Future work
- Ground all descriptions of a page in one prompt, so Qwen cannot give two of them the same box.
- Compare Qwen's grounding with a dedicated grounding model such as NVIDIA LocateAnything-3B
  (3B parameters, non-commercial research licence). With Qwen-only already tying B on 24
  descriptions, a gain of one or two figures would not be measurable on this test set.
- TikZ redrawing by distillation: a large model writes TikZ for training crops, only code that
  compiles and looks like the crop is kept, then Qwen gets a QLoRA adapter for crop -> TikZ. The
  small model still learns by gradient descent. No large model sets its weights directly.
- Use leftover Surya figure boxes to recover drawings Qwen never described.
- Put grounding into the web interface (switch the adapter off for one call per description).
- Fine-tune a drawing detector on the GT boxes (the dev and val/test boxes are a start).
- TikZ redrawing of simple diagrams, and textbook explanations as footnotes.

## How to reproduce (from ie643_final/, after `source ../ie643_final_env.sh`)
1. `python3 novelty/diagnose_figures.py` - four-panel diagnostic, no GPU.
2. `python3 novelty/ground_qwen.py --set all` - Qwen boxes, GPU, about 5 minutes.
3. `python3 novelty/match_figures.py` - arms A / B / C, TAU chosen on dev, IoU scores.
4. `python3 novelty/regrade.py build`, grade `regrade/regrade_v2.html`, then
   `python3 novelty/regrade.py score`.
5. `python3 novelty/render_arm.py` - IE802 PDFs with arm B.
6. `python3 novelty/compare_arms.py` - error metrics, per-document table, before/after images.
7. `python3 novelty/make_poster_fig047.py` - poster figure for page 047.
8. `python3 novelty/verify_crops.py run` then `score` - self-verification confidence flag.
9. `python3 novelty/book_notes.py generate`, `render`, `build`, then grade and `score` - footnotes.

## Files for the poster and report
- `results/comparison/outcome_chart.png` - main results chart.
- `results/page047_before_after.png` - worked example.
- `diagnostic/ie802_notes_page047.jpg` - four-panel diagnostic example.
- `results/comparison/comparison.md` - every table and every affected description.
- `render_B/test/ie802_notes/ie802_notes.pdf` - PDF after the fix.
- `results/page047_before_after_tight.png` - page 047 example cropped to the figures (used in the report).
- `report/InTra_IE643_NoveltyAssessment_report.pdf` - the 2-page novelty report (LaTeX source alongside,
  build with `xelatex InTra_IE643_NoveltyAssessment_report.tex` in that folder).
- `pipeline_surya25_dup_only_verifier2/<split>/<unit>/<unit>.pdf` - PDFs from the current best pipeline (steps 11 to 15).
- `structure/test/compare/` - before/after page images for the structure clean-up.
- `books/ie643_lec03/ie643_lec03.pdf`, `books/ie643_lec09/ie643_lec09.pdf` - lectures with book footnotes.
