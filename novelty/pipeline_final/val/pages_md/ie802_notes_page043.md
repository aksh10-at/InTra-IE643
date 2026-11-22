$$\min c^Tx+d^T\theta$$
$$\text{st } g_i(x,\theta)\le0 \quad i=1,2\dots m$$
$$x\in\mathbb{R}^n, \quad \theta\in\mathbb{Z}^p$$

$$S = \{(x,\theta): x\in\mathbb{R}^n, \theta\in\mathbb{Z}^p, g_i(x,\theta)\le0, i=1,2\dots m\}$$

$$R = \{(x,y): x\in\mathbb{R}^n, y\in\mathbb{R}^p, g_i(x,y)\le0, i=1,2\dots m\}$$

Find $(x,\theta)$ st it is valid for $S$ but not $R$

**Step ①** *Pick a disjunction (OR)*

- $y_1\le0$ or $y_1\ge1$
- $y_5\le4$ or $y_5\ge5$
- $y_5+y_6+y_3\le1$ or $y_5+y_6+y_4\ge2$

**②**
$$S_1 = \{(x,y): x\in\mathbb{R}^n, y\in\mathbb{Z}^p, g_i(x,y)\le0, i=1,2\dots m, y_1\le1\}$$
$$S_2 = \{\dots, y_1\ge2\}$$
$$S = S_1\cup S_2$$

**Step③** Relax $\to R_1$ and $R_2$
$$R_1 = \{(x,y): x\in\mathbb{R}^n, y\in\mathbb{R}^p, \dots, y_1\le1\}$$
$$R_2 = \{y\in\mathbb{R}^p, y_1\ge2\}$$
