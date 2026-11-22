# Crop cleaning on IE802 val + test (arm B boxes, settings from dev: {'pad': 0.01, 'outside': 0.5, 'foreign_frac': 0.5, 'wide_text': 0.0, 'main': 0.4, 'edge': 0.95, 'max_removed': 0.35, 'foreign_edge': True})

| measure | before | after |
|---|---|---|
| foreign ink share (mean over 21 crops) | 0.067 | 0.057 |
| drawing ink kept (mean / min) | 1.000 | 0.989 / 0.906 |
| crops changed | - | 10/21 |
| crops kept as original by the safety rule | - | 0 |

| page | desc | foreign before | foreign after | drawing kept | pieces removed | reverted |
|---|---|---|---|---|---|---|
| 041 | D1 | 0.000 | 0.000 | 1.000 | 0 | False |
| 041 | D2 | 0.000 | 0.000 | 1.000 | 0 | False |
| 041 | D3 | 0.000 | 0.000 | 1.000 | 0 | False |
| 041 | D6 | 0.016 | 0.001 | 0.979 | 3 | False |
| 042 | D1 | 0.000 | 0.000 | 1.000 | 0 | False |
| 042 | D2 | 0.000 | 0.000 | 1.000 | 0 | False |
| 042 | D4 | 0.000 | 0.000 | 0.996 | 1 | False |
| 044 | D1 | 0.000 | 0.000 | 1.000 | 0 | False |
| 046 | D1 | 0.000 | 0.000 | 1.000 | 0 | False |
| 046 | D2 | 0.579 | 0.569 | 0.999 | 5 | False |
| 046 | D3 | 0.340 | 0.257 | 1.000 | 10 | False |
| 047 | D1 | 0.000 | 0.000 | 0.931 | 1 | False |
| 047 | D2 | 0.000 | 0.000 | 1.000 | 0 | False |
| 047 | D3 | 0.000 | 0.000 | 0.974 | 1 | False |
| 047 | D4 | 0.000 | 0.000 | 1.000 | 0 | False |
| 047 | D5 | 0.181 | 0.083 | 1.000 | 2 | False |
| 048 | D1 | 0.000 | 0.000 | 0.994 | 1 | False |
| 052 | D1 | 0.000 | 0.000 | 0.906 | 4 | False |
| 052 | D2 | 0.000 | 0.000 | 1.000 | 1 | False |
| 054 | D1 | 0.000 | 0.000 | 1.000 | 0 | False |
| 055 | D1 | 0.297 | 0.297 | 1.000 | 0 | False |
