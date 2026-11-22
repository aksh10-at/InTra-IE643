# Method B: Surya 2 vs Surya 2.5 (val + test, same Qwen grounding, TAU 0.2)

- Descriptions: 64. Same crop (IoU >= 0.95): 43. Different: 21 (20 pairs in the blind grading page).
- IE802 GT pages (23 descriptions with a GT drawing): mean Localisation Error Surya 2 0.421, Surya 2.5 0.390. Right box (IoU >= 0.5): 14 vs 16.
- Where the crop comes from (2 -> 2.5): Surya box 51 -> 51, Qwen box 8 -> 8, old fallback 5 -> 5.

| page | desc | same | source 2 | source 2.5 | LE 2 | LE 2.5 | description |
|---|---|---|---|---|---|---|---|
| ie643_lec07_page008 | D1 | no | surya | surya | - | - | A wavy curve with an arrow pointing left from a marked point, labeled "step length/learnin |
| ie643_lec07_page020 | D1 | no | fallback A | fallback A | - | - | A hexagonal grid of small circles, each with a dot at its center, arranged in a repeating  |
| ie802_notes_page041 | D2 | no | surya+ | qwen | 0.77 | 0.23 | $S$ and $T$ separated by an arrow, labeled "Separate $S$ from $T$ by a hyperplane... on li |
| ie802_notes_page041 | D5 | no | surya | surya | - | - | A scatter plot of points with a red separating line, labeled "minimize flat hat 2-norm" —  |
| ie802_notes_page041 | D6 | no | surya | qwen | 0.46 | 0.49 | A polygonal region with a red separating line through it, labeled "split cutg..." — "this  |
| ie802_notes_page042 | D1 | no | surya | surya | 0.74 | 0.74 | A set $S$ split into two regions by a vertical line, labeled "S" on the left and "$11$" on |
| ie802_notes_page042 | D3 | no | surya | surya | 1.00 | 1.00 | Two separate sets $S_1$ and $S_2$ each with a line $\alpha x \leq \beta$ through them. |
| ie802_notes_page042 | D4 | no | surya | surya | 0.10 | 0.41 | An oval region split by a red line into two halves, labeled $R_1$ on the left and a shaded |
| ie643_lec03_page002 | D1 | no | fallback A | fallback A | - | - | A perceptron neuron — inputs $x_1, x_2, \dots, x_d$ each with weight $w_1, w_2, \dots, w_d |
| ie643_lec03_page004 | D1 | no | surya | surya | - | - | A line $x_1 - 2x_2 = 3$ (offset/bias) plotted on axes $x_1, x_2$, with a point $(x_1, x_2) |
| ie643_lec09_page013 | D1 | no | qwen | surya | - | - | A column of output neurons $\hat{y}_1, \hat{y}_2, \dots, \hat{y}_C$, each connected to a s |
| ie643_lec09_page014 | D1 | no | fallback A | fallback A | - | - | A chain of fully-connected layers (left) vs. a fully-connected layer feeding into a single |
| ie643_lec09_page015 | D1 | no | qwen | surya | - | - | A chain of neurons labeled $a_1^L, a_2^L, \dots, a_C^L$, each feeding into the next. |
| ie802_notes_page046 | D3 | no | surya | surya | 0.33 | 0.31 | A region with a red cross through it, labeled "current plane", and a note "intersection of |
| ie802_notes_page047 | D1 | no | surya | surya | 0.51 | 0.05 | A polygon with a marked corner point, labeled "basic Gom point", and an arrow labeled "cut |
| ie802_notes_page048 | D1 | no | surya | surya | 0.88 | 0.87 | A shaded region with a cut through it, illustrating the idea of traveling 2 sides of a cor |
| ie802_notes_page052 | D1 | no | surya | surya | 0.21 | 0.06 | A wavy curve with a local minimum marked at the start, and another point further along the |
| mlt_week03_page007 | D1 | no | surya | surya | - | - | A 2D scatter plot showing two clusters — yellow shaded region labeled "Cluster 1 region" o |
| mlt_week03_page011 | D1 | no | surya | surya | - | - | A scatter plot showing three red dots at $(5,9)$, $(8,3)$, and $(10,1)$, two blue dots at  |
| mlt_week09_page003 | D1 | no | surya | surya | - | - | Two scatter plots of data points with a dashed decision boundary line, showing an initial  |
| mlt_week09_page004 | D1 | no | surya | surya | - | - | A line through the origin with a point $(\begin{bmatrix}1\\1/2\end{bmatrix},-1)$ on one si |
