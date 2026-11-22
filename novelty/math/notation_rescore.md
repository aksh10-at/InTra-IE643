# Final model on test, scored as reported vs with one notation on both sides

Rules: `\\ell(?![A-Za-z])` -> `l`, `\\rightarrow(?![A-Za-z])` -> `\\to`, `\\longrightarrow(?![A-Za-z])` -> `\\to`, `\\leq(?![A-Za-z])` -> `\\le`, `\\geq(?![A-Za-z])` -> `\\ge`, `\\neq(?![A-Za-z])` -> `\\ne`, `\\[dt]frac(?![A-Za-z])` -> `\\frac`, `\\mathcal\{([A-Za-z])\}` -> `\1`, `\\times(?![A-Za-z])` -> `\\cdot`

## as reported

```
scored 76 pages, 0 missing predictions
source     n    CER    WER  textCER  eqMatch
hlcs       4  0.190  0.323    0.190      -  
ie643     34  0.339  0.522    0.290    0.108
ie802     12  0.349  0.597    0.214    0.174
mlt       26  0.317  0.554    0.193    0.159
ALL       76  0.325  0.534    0.227    0.137

extended metrics (higher is better except corpCER, NED; len = prediction/reference length)
source     n corpCER     NED    tokP    tokR   tokF1   BLEU4     len     eqP     eqR    eqF1  eqEdit  diagEx   diagP   diagR   headR
hlcs       4   0.166   0.170   0.882   0.913   0.889   0.803   1.017     -       -       -       -     1.000     -       -     0.625
ie643     34   0.357   0.331   0.883   0.854   0.865   0.733   0.966   0.299   0.287   0.285   0.682   0.882   0.818   0.818   0.591
ie802     12   0.351   0.327   0.816   0.796   0.803   0.611   1.031   0.270   0.265   0.266   0.673   1.000   1.000   1.000     -  
mlt       26   0.323   0.300   0.879   0.850   0.861   0.729   0.974   0.450   0.443   0.436   0.743   0.808   0.944   0.680   0.812
ALL       76   0.332   0.311   0.871   0.847   0.855   0.707   0.982   0.350   0.341   0.338   0.703   0.882   0.930   0.800   0.710
95% CI CER (capped, page mean): 0.286 - 0.363
95% CI NED: 0.275 - 0.348
95% CI token F1: 0.835 - 0.874
95% CI eq edit score: 0.652 - 0.752

```

## one notation

```
scored 76 pages, 0 missing predictions
source     n    CER    WER  textCER  eqMatch
hlcs       4  0.190  0.323    0.190      -  
ie643     34  0.325  0.519    0.290    0.125
ie802     12  0.334  0.597    0.214    0.184
mlt       26  0.310  0.547    0.193    0.220
ALL       76  0.314  0.530    0.227    0.168

extended metrics (higher is better except corpCER, NED; len = prediction/reference length)
source     n corpCER     NED    tokP    tokR   tokF1   BLEU4     len     eqP     eqR    eqF1  eqEdit  diagEx   diagP   diagR   headR
hlcs       4   0.166   0.170   0.882   0.913   0.889   0.803   1.017     -       -       -       -     1.000     -       -     0.625
ie643     34   0.344   0.318   0.884   0.859   0.868   0.741   0.968   0.317   0.302   0.301   0.690   0.882   0.818   0.818   0.591
ie802     12   0.337   0.317   0.819   0.799   0.806   0.615   1.014   0.270   0.265   0.266   0.674   1.000   1.000   1.000     -  
mlt       26   0.317   0.293   0.883   0.858   0.867   0.743   0.984   0.473   0.465   0.458   0.752   0.808   0.944   0.680   0.812
ALL       76   0.322   0.302   0.873   0.852   0.859   0.717   0.983   0.367   0.356   0.354   0.710   0.882   0.930   0.800   0.710
95% CI CER (capped, page mean): 0.273 - 0.353
95% CI NED: 0.264 - 0.339
95% CI token F1: 0.839 - 0.878
95% CI eq edit score: 0.660 - 0.757

```
