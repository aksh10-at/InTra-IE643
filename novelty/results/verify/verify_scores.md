# Self-verification as a confidence flag

Test set: 64 blind-graded crops, 15 failures (wrong drawing or not a drawing).

| Measure | Value |
|---|---|
| Crops flagged (P(yes) < 0.5) | 8/64 |
| Failures caught (recall) | 5/15 |
| Flagged crops that are failures (precision) | 5/8 |
| Base rate of failures (precision of random flags) | 15/64 (23%) |
| Ranking quality (AUC: a failure scores lower than a good crop) | 0.82 |

AUC 0.5 = no better than chance, 1.0 = every failure scores below every good crop.

| Card | page | desc | human grade | P(yes) | flagged |
|---|---|---|---|---|---|
| c046 | ie802_notes_page041 | D2 | wrong | 0.004 | yes |
| c019 | ie802_notes_page047 | D2 | wrong | 0.005 | yes |
| c020 | ie802_notes_page042 | D2 | wrong | 0.014 | yes |
| c057 | ie802_notes_page041 | D3 | wrong | 0.033 | yes |
| c035 | ie802_notes_page041 | D5 | wrong | 0.182 | yes |
| c006 | ie802_notes_page047 | D3 | correct | 0.349 | yes |
| c064 | ie802_notes_page052 | D2 | correct | 0.378 | yes |
| c010 | ie802_notes_page041 | D2 | correct | 0.438 | yes |
| c002 | ie802_notes_page047 | D4 | wrong | 0.531 |  |
| c018 | ie802_notes_page047 | D4 | wrong | 0.531 |  |
| c023 | ie802_notes_page047 | D3 | wrong | 0.593 |  |
| c044 | ie643_lec09_page002 | D1 | correct | 0.593 |  |
| c021 | ie802_notes_page042 | D3 | wrong | 0.623 |  |
| c034 | ie802_notes_page042 | D3 | wrong | 0.623 |  |
| c060 | ie802_notes_page047 | D1 | correct | 0.623 |  |
| c041 | ie802_notes_page041 | D5 | wrong | 0.651 |  |
| c053 | ie802_notes_page041 | D1 | correct | 0.706 |  |
| c008 | ie802_notes_page041 | D1 | correct | 0.755 |  |
| c017 | ie802_notes_page046 | D3 | loose | 0.852 |  |
| c014 | ie802_notes_page046 | D2 | wrong | 0.867 |  |
| c049 | ie802_notes_page047 | D2 | correct | 0.881 |  |
| c004 | ie802_notes_page048 | D1 | correct | 0.893 |  |
| c040 | ie802_notes_page054 | D1 | correct | 0.893 |  |
| c050 | ie643_lec09_page006 | D1 | correct | 0.893 |  |
| c001 | ie802_notes_page046 | D3 | correct | 0.905 |  |
| c025 | ie802_notes_page041 | D4 | correct | 0.915 |  |
| c037 | ie802_notes_page041 | D4 | partial | 0.915 |  |
| c051 | ie802_notes_page047 | D3 | correct | 0.915 |  |
| c062 | ie802_notes_page046 | D3 | correct | 0.915 |  |
| c033 | ie802_notes_page048 | D1 | correct | 0.924 |  |
| c063 | ie802_notes_page052 | D1 | correct | 0.932 |  |
| c011 | ie643_lec09_page013 | D1 | correct | 0.940 |  |
| c047 | ie802_notes_page046 | D2 | correct | 0.947 |  |
| c038 | ie802_notes_page041 | D2 | correct | 0.953 |  |
| c031 | ie802_notes_page055 | D1 | correct | 0.958 |  |
| c059 | ie802_notes_page041 | D6 | correct | 0.958 |  |
| c056 | ie802_notes_page042 | D3 | correct | 0.963 |  |
| c030 | mlt_week09_page003 | D1 | partial | 0.967 |  |
| c036 | ie802_notes_page052 | D1 | correct | 0.967 |  |
| c045 | ie802_notes_page046 | D2 | correct | 0.967 |  |
| c052 | ie802_notes_page044 | D1 | correct | 0.967 |  |
| c054 | ie802_notes_page042 | D4 | correct | 0.967 |  |
| c005 | ie802_notes_page041 | D6 | correct | 0.974 |  |
| c007 | ie802_notes_page047 | D2 | correct | 0.980 |  |
| c024 | ie802_notes_page047 | D5 | correct | 0.980 |  |
| c055 | ie802_notes_page042 | D1 | wrong | 0.980 |  |
| c039 | ie802_notes_page042 | D1 | wrong | 0.982 |  |
| c012 | ie802_notes_page047 | D5 | correct | 0.984 |  |
| c016 | ie802_notes_page052 | D2 | correct | 0.984 |  |
| c048 | ie802_notes_page044 | D1 | correct | 0.984 |  |
| c061 | ie802_notes_page042 | D4 | correct | 0.984 |  |
| c022 | mlt_week09_page013 | D1 | wrong | 0.986 |  |
| c027 | ie802_notes_page042 | D2 | correct | 0.989 |  |
| c028 | ie802_notes_page055 | D1 | correct | 0.989 |  |
| c009 | ie643_lec09_page015 | D1 | correct | 0.991 |  |
| c029 | mlt_week09_page003 | D1 | correct | 0.991 |  |
| c032 | mlt_week06_page003 | D1 | correct | 0.991 |  |
| c013 | ie802_notes_page047 | D1 | correct | 0.992 |  |
| c026 | ie802_notes_page041 | D3 | correct | 0.995 |  |
| c058 | ie643_lec03_page010 | D1 | correct | 0.997 |  |
| c015 | ie802_notes_page041 | D3 | correct | 0.998 |  |
| c043 | ie802_notes_page046 | D1 | correct | 0.998 |  |
| c042 | ie802_notes_page046 | D1 | correct | 0.999 |  |
| c003 | ie643_lec03_page010 | D1 | loose | 0.999 |  |
