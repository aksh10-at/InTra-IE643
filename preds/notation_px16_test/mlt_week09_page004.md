- We need more careful argument for convergence.

## Example 2

[Diagram: A line through the origin with points $(\begin{bmatrix}-1\\1\end{bmatrix}, -1)$, $(\begin{bmatrix}0\\1\end{bmatrix}, +1)$, $(\begin{bmatrix}0\\-1\end{bmatrix}, +1)$, $(\begin{bmatrix}-1\\0\end{bmatrix}, -1)$ — "Is this a linearly separable dataset?"]

$$\begin{cases} \begin{bmatrix}0\\1\end{bmatrix}, +1 \\ \begin{bmatrix}0\\-1\end{bmatrix}, +1 \\ \begin{bmatrix}-1\\0\end{bmatrix}, -1 \end{cases}$$

Is there a $w \in \mathbb{R}^2$ st $w^Tx_1 \ge 0 \Rightarrow y_1 = +1$, $w^Tx_1 < 0 \Rightarrow y_1 = -1$

**There is**

[Diagram: Same line through the origin with the same points, now showing a separating vector $w$.]

$$w^0 = \begin{bmatrix}0\\0\end{bmatrix}, \quad w^0{}^Tx_1 = 0, \; w^0{}^Tx_2 = 0, \; w^0{}^Tx_3 = 0, \; \hat{y}_1 = +1, \; \hat{y}_2 = +1, \; \hat{y}_3 = +1$$

$$w^1 = w^0 + x_3y_3 = \begin{bmatrix}0\\0\end{bmatrix} + \begin{bmatrix}-1\\1\end{bmatrix}^{x^{-1}}$$

**Perceptron**