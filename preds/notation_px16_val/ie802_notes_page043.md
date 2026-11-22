$$\min c^Tx + d^Ty$$
$$\text{st } g_i(x,y) \le 0 \quad i=1,2,\dots,m$$
$$x \in \mathbb{R}^n, \; y \in \mathbb{Z}^p$$

$$S = \{(x,y): x \in \mathbb{R}^n, y \in \mathbb{Z}^p, \; g_i(x,y) \le 0 \; i=1,2,\dots,m\}$$
$$R = \{(x,y): x \in \mathbb{R}^n, y \in \mathbb{R}^p, \; g_i(x,y) \le 0 \; i=1,2,\dots,m\}$$

Find $(x,y)$ st it is valid for $S$ but not $R$

**Step①** *Pick a disjunction (or)*

- es. $y_1 \le 0$ or $y_1 \ge 1$ $\to$ pick this
- es. $y_5 \le 4$ or $y_5 \ge 5$
- es. $y_5+y_6+y_7 \le 1$ or $y_5+y_6+y_7 \ge 2$

**②** $S_1 = \{(x,y): x \in \mathbb{R}^n, y \in \mathbb{Z}^p, g_i(x,y) \le 0 \; i=1,2,\dots,m, y_1 \le 1\}$

$$S_2 = \{\dots, y_1 \ge 2\}$$

$$S = S_1 \cup S_2$$

**Step③** Relax $\to R_1$ and $R_2$

$$R_1 = \{x \in \mathbb{R}^n, y \in \mathbb{R}^p, y_1 \le 1\}$$
$$R_2 = \{y \in \mathbb{R}^p, y_1 \ge 2\}$$