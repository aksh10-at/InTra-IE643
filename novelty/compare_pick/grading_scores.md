# Blind paired grading: Method B crop vs verifier pick (19 of 19 pairs)

| pages | Method B better | verifier better | equally good | both wrong |
|---|---|---|---|---|
| all | 9 | 2 | 8 | 0 |
| IE802 | 2 | 1 | 6 | 0 |
| IE643 + MLT + HLCS | 7 | 1 | 2 | 0 |

Sign test over all pairs with a winner: p = 0.065

Grading: blind AI grader (crops, page and description only; random order; no key). Checked and confirmed by the team on 22 Nov 2026.
Reading: the verifier pick is NOT kept. It mostly swaps in the rough Qwen box (16 of 19), which often
cuts off labels (8 partial crops vs 2 for Method B). The GT IoU gain on IE802 (LE 0.320 -> 0.274) did not
show up in the visual grading there (Method B 2, verifier 1, same 6). The verifier question tolerates
small cut-offs, so it cannot prefer the complete crop.
