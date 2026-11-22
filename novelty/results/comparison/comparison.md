# Figure placement: before (A) vs after (B)

Metrics (0 = perfect for both):

- **Figure Error Score (FES)** from blind human grades: correct 0, loose or partial 0.5, wrong / not a drawing / no crop 1, averaged over descriptions. **Failure rate** = share scored 1.
- **Localisation Error (LE)** from the GT boxes: 1 - IoU(chosen box, intended drawing), averaged. Each description is also assigned the stage that decides its outcome.

Arm B uses TAU = 0.2, chosen on IE802 training pages before any val/test result was seen.

## 1. Summary (blind human grades)

| Pages | Arm | Descriptions | correct | degraded (loose/partial) | failed | FES | failure rate |
|---|---|---|---|---|---|---|---|
| IE802 val + test (all) | A before | 24 | 13 | 2 | 9 | 0.42 | 9/24 (38%) |
| IE802 val + test (all) | B after | 24 | 20 | 0 | 4 | 0.17 | 4/24 (17%) |
| IE802 val + test (all) | C Qwen only | 24 | 20 | 0 | 4 | 0.17 | 4/24 (17%) |
| IE643 + MLT (8 changed) | A before | 8 | 1 | 1 | 6 | 0.81 | 6/8 (75%) |
| IE643 + MLT (8 changed) | B after | 8 | 6 | 1 | 1 | 0.19 | 1/8 (12%) |

IE643 + MLT: the remaining 32 of 40 descriptions keep the identical crop, so their error is unchanged and is not re-graded.

## 2. Localisation Error and failing stage (IE802 val + test, automatic, GT boxes)

| Arm | mean LE | ok (IoU >= 0.5) | localisation | matching | recognition |
|---|---|---|---|---|---|
| A | 0.58 (n=23) | 10 | 5 | 8 | 1 |
| B | 0.42 (n=23) | 14 | 7 | 2 | 1 |
| C | 0.37 (n=23) | 16 | 5 | 2 | 1 |

Recognition misses (drawings with no [Diagram] line, the same for every arm): 042 GT D4, 046 GT D2, 056 X (also missed by Surya).

## 3. Per document (val/test files)

| Document | split | descriptions | changed by B | FES before | FES after | failures before | failures after |
|---|---|---|---|---|---|---|---|
| ie643_lec03 | test | 4 | 1 | 0.50 (over the 1 changed) | 0.00 | 0 | 0 |
| ie643_lec07 | val | 9 | 0 | unchanged | unchanged | unchanged | unchanged |
| ie643_lec09 | test | 7 | 4 | 1.00 (over the 4 changed) | 0.00 | 4 | 0 |
| ie802_notes | test | 13 | 4 | 0.35 | 0.08 | 4 | 1 |
| ie802_notes | val | 11 | 5 | 0.50 | 0.27 | 5 | 3 |
| mlt_week03 | test | 6 | 0 | unchanged | unchanged | unchanged | unchanged |
| mlt_week06 | val | 2 | 1 | 1.00 (over the 1 changed) | 0.00 | 1 | 0 |
| mlt_week09 | test | 12 | 2 | 0.50 (over the 2 changed) | 0.75 | 1 | 1 |

## 4. Every affected page and description

| Page | Desc | Description (short) | before (A) | after (B) | LE before | LE after | stage before | stage after |
|---|---|---|---|---|---|---|---|---|
| ie643_lec03_page010 | D1 | A scatter plot of overlapping "+" and "-" data points with m... | loose | correct | - | - | - | - |
| ie643_lec09_page002 | D1 | A chain of nodes $a_j^{l-1}$ feeding into $z_i^l$, which fee... | no crop | correct | - | - | - | - |
| ie643_lec09_page006 | D1 | A column of $C$-dimensional vectors, each with a single 1 in... | no crop | correct | - | - | - | - |
| ie643_lec09_page013 | D1 | A column of output neurons $\hat{y}_1, \hat{y}_2, \dots, \ha... | no crop | correct | - | - | - | - |
| ie643_lec09_page015 | D1 | A chain of neurons labeled $a_1^L, a_2^L, \dots, a_C^L$, eac... | no crop | correct | - | - | - | - |
| ie802_notes_page041 | D2 | $S$ and $T$ separated by an arrow, labeled "Separate $S$ fro... | wrong | correct | 0.92 | 0.77 | localisation | localisation |
| ie802_notes_page041 | D3 | A wavy line graph with two labeled regions $S1$ (above) and ... | wrong | correct | 1.00 | 0.45 | matching | ok |
| ie802_notes_page041 | D4 | Two overlapping "S1" regions, each with a red separating lin... | partial | correct | 1.00 | 1.00 | matching | matching |
| ie802_notes_page042 | D2 | Two overlapping sets $S_1$ and $S_2$. | wrong | correct | 1.00 | 0.18 | matching | ok |
| ie802_notes_page042 | D3 | Two separate sets $S_1$ and $S_2$ each with a line $\alpha x... | correct | wrong | 0.77 | 1.00 | matching | matching |
| ie802_notes_page046 | D2 | A cone with several "x" points inside and a few outside, an ... | wrong | correct | 1.00 | 0.59 | matching | localisation |
| ie802_notes_page046 | D3 | A region with a red cross through it, labeled "current plane... | loose | correct | 0.87 | 0.33 | matching | ok |
| ie802_notes_page047 | D2 | A square containing a smaller circle — a convex set. | wrong | correct | 1.00 | 0.04 | matching | ok |
| ie802_notes_page047 | D3 | An irregular shape with a small circle inside, labeled "we c... | wrong | correct | 1.00 | 0.61 | matching | localisation |
| mlt_week06_page003 | D1 | A row of boxes labeled $F_1, F_2, \dots, F_k$, with a line t... | no crop | correct | - | - | - | - |
| mlt_week09_page003 | D1 | Two scatter plots of data points with a dashed decision boun... | correct | partial | - | - | - | - |
| mlt_week09_page013 | D1 | A green box containing $x_i$, an arrow to $y_i$, an arrow to... | no crop | wrong | - | - | - | - |

Before/after images for the 12 affected pages: `ie643_lec03_page010.png, ie643_lec09_page002.png, ie643_lec09_page006.png, ie643_lec09_page013.png, ie643_lec09_page015.png, ie802_notes_page041.png, ie802_notes_page042.png, ie802_notes_page046.png, ie802_notes_page047.png, mlt_week06_page003.png, mlt_week09_page003.png, mlt_week09_page013.png`.

## 5. Where the two metrics disagree (IE802)

A human grade of correct with an automatic stage of matching, or a human grade of wrong with an automatic ok. These show the limits of each metric.

| Page | Desc | Arm | human grade | automatic stage | IoU with intended GT |
|---|---|---|---|---|---|
| 041 | D4 | B | correct | matching | 0.00 |
| 041 | D4 | C | correct | matching | 0.00 |
| 042 | D3 | A | correct | matching | 0.23 |
| 047 | D4 | A | wrong | ok | 0.89 |
| 047 | D4 | B | wrong | ok | 0.89 |
| 047 | D4 | C | wrong | ok | 0.93 |

6 of 72 arm-description pairs disagree. On these pages: 041 D4's description (two S1 regions with a red line) also fits the neighbouring S1/S2 drawing, so the grader accepted it. 042 D3 (A) is a merged box of three drawings that the grader judged as showing the right one (arguably loose). 047 D4 overlaps its GT drawing with IoU 0.89 but was graded wrong for every arm, which suggests the description does not match how the grader read the sketch. Neither metric alone is final, so the poster reports both.

