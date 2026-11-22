# Retrain with one notation + 1.6M px (notation_px16) vs final_clean

Both predictions and the labels are put in one notation, so notation differences do not count.

## val: final_clean

```
scored 31 pages, 0 missing predictions
source     n    CER    WER  textCER  eqMatch
hlcs       1  0.067  0.197    0.067      -  
ie643     20  0.325  0.504    0.312    0.245
ie802      4  0.534  0.853    0.520    0.045
mlt        6  0.250  0.533    0.169    0.117
ALL       31  0.330  0.545    0.307    0.198

extended metrics (higher is better except corpCER, NED; len = prediction/reference length)
source     n corpCER     NED    tokP    tokR   tokF1   BLEU4     len     eqP     eqR    eqF1  eqEdit  diagEx   diagP   diagR   headR
hlcs       1   0.067   0.067   0.964   0.870   0.914   0.729   0.991     -       -       -       -     1.000     -       -     1.000
ie643     20   0.328   0.311   0.847   0.823   0.832   0.754   1.041   0.426   0.446   0.434   0.798   0.950   0.889   1.000   0.750
ie802      4   0.531   0.511   0.795   0.772   0.782   0.597   0.996   0.570   0.519   0.539   0.859   0.250   0.818   0.900     -  
mlt        6   0.196   0.240   0.899   0.864   0.880   0.806   0.992   0.361   0.394   0.376   0.808   0.667   0.000     -     1.000
ALL       31   0.337   0.315   0.854   0.826   0.838   0.728   1.024   0.433   0.446   0.437   0.809   0.806   0.773   0.944   0.846
95% CI CER (capped, page mean): 0.253 - 0.414
95% CI NED: 0.246 - 0.392
95% CI token F1: 0.770 - 0.887
95% CI eq edit score: 0.744 - 0.871
```

## val: notation_px16

```
scored 31 pages, 0 missing predictions
source     n    CER    WER  textCER  eqMatch
hlcs       1  0.081  0.222    0.081      -  
ie643     20  0.333  0.525    0.276    0.314
ie802      4  0.461  0.873    0.248    0.091
mlt        6  0.222  0.486    0.258    0.117
ALL       31  0.320  0.553    0.261    0.249

extended metrics (higher is better except corpCER, NED; len = prediction/reference length)
source     n corpCER     NED    tokP    tokR   tokF1   BLEU4     len     eqP     eqR    eqF1  eqEdit  diagEx   diagP   diagR   headR
hlcs       1   0.081   0.080   0.967   0.946   0.956   0.716   1.009     -       -       -       -     1.000     -       -     1.000
ie643     20   0.352   0.297   0.874   0.855   0.859   0.756   1.013   0.474   0.493   0.477   0.832   0.900   0.800   1.000   0.625
ie802      4   0.460   0.447   0.833   0.757   0.791   0.600   0.913   0.559   0.537   0.545   0.842   0.500   0.900   0.900     -  
mlt        6   0.168   0.217   0.899   0.871   0.884   0.824   0.984   0.299   0.353   0.322   0.796   0.667   0.000     -     1.000
ALL       31   0.325   0.294   0.877   0.848   0.858   0.734   0.995   0.448   0.469   0.453   0.826   0.806   0.773   0.944   0.769
95% CI CER (capped, page mean): 0.248 - 0.395
95% CI NED: 0.230 - 0.357
95% CI token F1: 0.825 - 0.890
95% CI eq edit score: 0.759 - 0.884
```

## val: paired comparison (final_clean vs notation_px16)

```
scored 31 pages, 0 missing predictions
source     n    CER    WER  textCER  eqMatch
hlcs       1  0.067  0.197    0.067      -  
ie643     20  0.325  0.504    0.312    0.245
ie802      4  0.534  0.853    0.520    0.045
mlt        6  0.250  0.533    0.169    0.117
ALL       31  0.330  0.545    0.307    0.198

paired comparison on 31 pages, NED (lower is better): B - A = -0.022 (95% CI -0.054 to +0.010); B better on 17 pages, worse on 12; B better in 91% of resamples
```

## test: final_clean

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

## test: notation_px16

```
scored 76 pages, 0 missing predictions
source     n    CER    WER  textCER  eqMatch
hlcs       4  0.198  0.314    0.198      -  
ie643     34  0.332  0.534    0.302    0.242
ie802     12  0.355  0.611    0.231    0.163
mlt       26  0.306  0.555    0.236    0.246
ALL       76  0.320  0.542    0.253    0.231

extended metrics (higher is better except corpCER, NED; len = prediction/reference length)
source     n corpCER     NED    tokP    tokR   tokF1   BLEU4     len     eqP     eqR    eqF1  eqEdit  diagEx   diagP   diagR   headR
hlcs       4   0.147   0.165   0.864   0.953   0.900   0.785   1.085     -       -       -       -     1.000     -       -     0.625
ie643     34   0.358   0.319   0.882   0.880   0.877   0.767   0.993   0.328   0.320   0.317   0.690   0.912   0.900   0.818   0.500
ie802     12   0.360   0.344   0.836   0.804   0.820   0.617   1.010   0.350   0.278   0.306   0.603   0.917   1.000   0.929     -  
mlt       26   0.307   0.295   0.895   0.839   0.864   0.711   0.964   0.471   0.431   0.442   0.689   0.769   0.941   0.640   0.781
ALL       76   0.327   0.307   0.878   0.858   0.865   0.712   0.991   0.384   0.354   0.360   0.676   0.868   0.950   0.760   0.661
95% CI CER (capped, page mean): 0.279 - 0.362
95% CI NED: 0.268 - 0.348
95% CI token F1: 0.846 - 0.883
95% CI eq edit score: 0.621 - 0.731
```

## test: paired comparison (final_clean vs notation_px16)

```
scored 76 pages, 0 missing predictions
source     n    CER    WER  textCER  eqMatch
hlcs       4  0.190  0.323    0.190      -  
ie643     34  0.325  0.519    0.290    0.125
ie802     12  0.334  0.597    0.214    0.184
mlt       26  0.310  0.547    0.193    0.220
ALL       76  0.314  0.530    0.227    0.168

paired comparison on 76 pages, NED (lower is better): B - A = +0.005 (95% CI -0.010 to +0.021); B better on 38 pages, worse on 35; B better in 26% of resamples
```

