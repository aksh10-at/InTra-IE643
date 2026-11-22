# Figure matching: arms A / B / C

BIG = 0.6 (Qwen box larger than this share of the page is ignored), COVER = 0.6

## Step 1: choose TAU for arm B on IE802 training pages (dev, descriptions from labels)

| TAU | B right box | B right drawing |
|---|---|---|
| 0.0 | 14/18 (78%) | 16/18 (89%) |
| 0.2 | 14/18 (78%) | 16/18 (89%) |
| 0.3 | 12/18 (67%) | 16/18 (89%) |
| 0.4 | 12/18 (67%) | 16/18 (89%) |
| 0.5 | 12/18 (67%) | 16/18 (89%) |
| 0.6 | 12/18 (67%) | 16/18 (89%) |
| 0.7 | 12/18 (67%) | 16/18 (89%) |
| 1.01 | 11/18 (61%) | 16/18 (89%) |

Chosen TAU = 0.2 (most right boxes on dev; ties go to the value nearest 0.5).

## dev (IE802 train pages 001-037, label descriptions)

| Arm | right box (IoU >= 0.5) | right drawing | box precision @0.5 | box recall @0.5 |
|---|---|---|---|---|
| A: Surya + reading order | 10/18 (56%) | 12/18 (67%) | 11/16 (69%) | 11/25 (44%) |
| B: Surya + Qwen + Hungarian | 14/18 (78%) | 16/18 (89%) | 14/18 (78%) | 14/25 (56%) |
| C: Qwen only | 11/18 (61%) | 16/18 (89%) | 11/18 (61%) | 11/25 (44%) |

Detectors alone (all their boxes, no pairing):

| Boxes | precision @0.5 | recall @0.5 |
|---|---|---|
| Surya | 18/23 (78%) | 18/25 (72%) |
| Qwen | 11/18 (61%) | 11/25 (44%) |

Per description (IoU of the chosen box with the GT drawing it refers to; WRONG = a different drawing overlaps more):

| page | desc | GT | A | B | B source | C |
|---|---|---|---|---|---|---|
| 001 | D1 | D1 | 0.91 | 0.91 | surya | 0.70 |
| 001 | D2 | D2 | none | 0.00 WRONG | qwen | 0.00 WRONG |
| 002 | D1 | D1 | 0.73 | 0.73 | surya | 0.62 |
| 002 | D2 | D2 | 0.97 | 0.97 | surya | 0.84 |
| 003 | D1 | D1 | 0.00 WRONG | 0.95 | surya | 0.87 |
| 003 | D2 | D2 | 0.00 WRONG | 0.54 | surya | 0.55 |
| 006 | D1 | D1 | 0.24 | 0.51 | surya | 0.88 |
| 011 | D1 | D1 | 0.79 | 0.79 | surya | 0.76 |
| 011 | D2 | D2 | 0.16 WRONG | 0.64 | surya | 0.41 |
| 011 | D3 | D3 | 0.94 | 0.94 | surya | 0.90 |
| 017 | D1 | D2 | 0.90 | 0.90 | surya | 0.31 |
| 017 | D2 | D3 | 0.97 | 0.97 | surya | 0.98 |
| 020 | D1 | D1 | 0.26 | 0.26 | surya | 0.27 |
| 020 | D2 | D2 | 0.50 | 0.50 | surya | 0.43 |
| 020 | D3 | D3 | 0.65 | 0.00 WRONG | qwen | 0.00 WRONG |
| 020 | D4 | D4 | 0.88 | 0.88 | surya | 0.82 |
| 037 | D1 | D2 | 0.20 WRONG | 0.45 | surya | 0.41 |
| 037 | D2 | D3 | none | 0.56 | surya | 0.96 |

## val + test (IE802 pages 041-056, model descriptions)

| Arm | right box (IoU >= 0.5) | right drawing | box precision @0.5 | box recall @0.5 |
|---|---|---|---|---|
| A: Surya + reading order | 10/23 (43%) | 15/23 (65%) | 14/24 (58%) | 14/27 (52%) |
| B: Surya + Qwen + Hungarian | 14/23 (61%) | 21/23 (91%) | 15/24 (62%) | 15/27 (56%) |
| C: Qwen only | 16/23 (70%) | 21/23 (91%) | 16/24 (67%) | 16/27 (59%) |

Detectors alone (all their boxes, no pairing):

| Boxes | precision @0.5 | recall @0.5 |
|---|---|---|
| Surya | 19/27 (70%) | 19/27 (70%) |
| Qwen | 16/24 (67%) | 16/27 (59%) |

Per description (IoU of the chosen box with the GT drawing it refers to; WRONG = a different drawing overlaps more):

| page | desc | GT | A | B | B source | C |
|---|---|---|---|---|---|---|
| 041 | D1 | D1 | 0.42 | 0.42 | surya | 0.41 |
| 041 | D2 | D2 | 0.08 | 0.23 | surya+ | 0.77 |
| 041 | D3 | D3 | 0.00 WRONG | 0.55 | surya | 0.52 |
| 041 | D4 | D4 | 0.00 WRONG | 0.00 WRONG | qwen | 0.00 WRONG |
| 041 | D6 | D5 | 0.54 | 0.54 | surya | 0.51 |
| 042 | D1 | D1 | 0.26 | 0.26 | surya | 0.28 |
| 042 | D2 | D2 | 0.00 WRONG | 0.82 | qwen | 0.82 |
| 042 | D3 | D3 | 0.23 WRONG | 0.00 WRONG | surya | 0.00 WRONG |
| 042 | D4 | D5 | 0.90 | 0.90 | surya | 0.74 |
| 044 | D1 | X | 0.92 | 0.92 | surya | 0.93 |
| 046 | D1 | D1 | 0.95 | 0.95 | surya | 0.88 |
| 046 | D2 | D3 | 0.00 WRONG | 0.41 | surya+ | 0.39 |
| 046 | D3 | D4 | 0.13 WRONG | 0.67 | surya | 0.26 |
| 047 | D1 | D1 | 0.49 | 0.49 | surya | 0.82 |
| 047 | D2 | D2 | 0.00 WRONG | 0.96 | surya | 0.88 |
| 047 | D3 | D3 | 0.00 WRONG | 0.39 | surya | 0.93 |
| 047 | D4 | D4 | 0.89 | 0.89 | surya | 0.93 |
| 047 | D5 | D5 | 0.60 | 0.60 | surya | 0.91 |
| 048 | D1 | D1 | 0.12 | 0.12 | surya | 0.19 |
| 052 | D1 | D1 | 0.79 | 0.79 | surya | 0.89 |
| 052 | D2 | D2 | 0.88 | 0.88 | surya | 0.92 |
| 054 | D1 | D1 | 0.96 | 0.96 | surya | 0.96 |
| 055 | D1 | D1 | 0.57 | 0.57 | surya | 0.56 |

