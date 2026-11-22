# Fixed verifier pick (only larger crops that contain Method B's box, judged on completeness)

| margin M | dev right box | dev right drawing | dev LE | dev switched | val+test right box | val+test right drawing | val+test LE | switched |
|---|---|---|---|---|---|---|---|---|
| keep Method B | 12/18 | 18/18 | 0.355 | 0 | 18/23 | 23/23 | 0.320 | 0 |
| 0.05 | 12/18 | 18/18 | 0.352 | 4 | 19/23 | 23/23 | 0.296 | 8 |
| 0.1 | 12/18 | 18/18 | 0.355 | 1 | 19/23 | 23/23 | 0.296 | 4 |
| 0.2 | 12/18 | 18/18 | 0.355 | 0 | 18/23 | 23/23 | 0.317 | 1 |
| 0.3 | 12/18 | 18/18 | 0.355 | 0 | 18/23 | 23/23 | 0.317 | 1 |

Chosen on dev: M = 0.05. Applied to every val + test description: 11 switched away from Method B.
