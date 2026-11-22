$$w^1 = w^0 + x_3y_3 = \begin{bmatrix}0\\0\end{bmatrix} + \begin{bmatrix}-1\\1/2\end{bmatrix}x^{-1} = \begin{bmatrix}-1\\-1/2\end{bmatrix}$$

$$w^3 = w^2 + x_2y_2 = \begin{bmatrix}1\\2\end{bmatrix} + \begin{bmatrix}0\\-1\end{bmatrix}x^1$$
$$w^3 = \begin{bmatrix}-1\\-1/2\end{bmatrix} = w^1$$

$$w^2 = w^1 + x_1y_1 = \begin{bmatrix}-1\\-1/2\end{bmatrix} + \begin{bmatrix}0\\1\end{bmatrix}^1$$
$$w^2 = \begin{bmatrix}1\\1/2\end{bmatrix}$$

We see that we are right back where we started. The algorithm is unable to provide a $w$ which can correctly classify all the data points correctly. It just won't converge. Let's modify our assumption.

---

## Assumption

**Linear Separability with $\gamma$-Margin**

[Diagram: A 2D scatter plot showing two classes of points (green and red) separated by a margin $\gamma$, with a separating hyperplane $w^Tx=\gamma$. The shaded regions between the margin lines represent the "gap" — the region where no points lie, but it can be very small but not zero.]

A dataset $\{(x_1,y_1),\dots(x_n,y_n)\}$ is linearly separable with $\gamma$-margin if $\exists w^*\in\mathbb{R}^d$ st $(w^Tx_i)y_i\ge\gamma$ $\forall i$, some $\gamma>0$.

The gap can be very small but not zero. No points lie on the gap.