$$\min x^TQx + c^Tx \quad 0\le x_i\le1 \to \text{No integer}$$

$\hookrightarrow$ introduce new variables

$$\min \sum Q_{ij}x_{ij} + \sum Q_{i1}y_1 + \sum c_ix_i$$
$$x_{ij}=x_ix_j \; \forall ij$$
$$y_1=x_1^2 \; \forall 1$$
$$0\le x_i\le1$$

$\to$ In case of only boolean $x\in\{0,1\}$, pads by triangle inequalities.

$$\min \sum Q_{ij}x_{ij} + \sum c_ix_i$$
st $\quad x_{ij}=x_ix_j$
$\qquad x_i\in\{0,1\}\; \forall i$

$\hookrightarrow$ convex hull of $\emptyset$ is same as convex hull of $x_{ij}=x_ix_j$, $0\le x_i\le1$

Result by Burer and Letchford.