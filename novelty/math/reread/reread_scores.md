# Second readings of display equations (rules chosen on val, applied once to test)

| rule | threshold | val NED | val eqMatch | val eqF1 | val eqEdit | equations replaced (val) |
|---|---|---|---|---|---|---|
| keep | 0 | 0.315 | 0.198 | 0.437 | 0.809 | 0 |
| vote | 0.2 | 0.315 | 0.246 | 0.463 | 0.808 | 5 |
| vote | 0.35 | 0.315 | 0.246 | 0.463 | 0.808 | 5 |
| vote | 0.5 | 0.319 | 0.246 | 0.463 | 0.807 | 9 |
| crop | 0.2 | 0.315 | 0.254 | 0.459 | 0.808 | 15 |
| crop | 0.35 | 0.318 | 0.264 | 0.468 | 0.806 | 19 |
| crop | 0.5 | 0.333 | 0.264 | 0.468 | 0.806 | 32 |
| surya | 0.2 | 0.320 | 0.165 | 0.424 | 0.803 | 12 |
| surya | 0.35 | 0.329 | 0.118 | 0.408 | 0.794 | 19 |
| surya | 0.5 | 0.350 | 0.132 | 0.413 | 0.786 | 33 |

Chosen on val (equation F1, then exact match, never a worse NED): ('vote', 0.2)

- test, keep ('keep', 0): NED 0.311, eqMatch 0.137, eqF1 0.338, eqEdit 0.703, CER 0.325, equations replaced 0
- test, chosen ('vote', 0.2): NED 0.311, eqMatch 0.137, eqF1 0.338, eqEdit 0.703, CER 0.325, equations replaced 14
