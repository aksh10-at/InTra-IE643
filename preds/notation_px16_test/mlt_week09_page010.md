# Sigmoid Functions for Modeling Class Probabilities

Linear Separability in terms of Probability:
$$P(y=1/x) = 1 \quad \text{if } w^Tx \ge 0$$
$$= 0 \qquad \text{otherwise}$$

Can we somehow relax this assumption? Can we model probabilities differently?

---

Start with a simple linear model: $z = w^Tx \leftarrow$ feature $x \in \mathbb{R}^d$

[Diagram: A plane with several blue lines (hyperplanes) through the origin at various angles, each representing a threshold $w^Tx=c$. Points $x_1, x_2, x_3, x_4$ are shown near the hyperplanes labeled $\{x:w^Tx=-150\}$, $\{x:w^Tx=-1\}$, $\{x:w^Tx=0\}$, $\{x:w^Tx=100\}$, $\{x:w^Tx=1\}$.]

How to label $\{x_1,x_2,x_3,x_4\}$?

We are going to attach probability for the label to be +1 or -1 to each point.

How to decide the probability? By high or low the "score" of each point is.

The score will be $z = w^Tx$, $z \in [-\infty,\infty]$
- Larger the score ($z=w^Tx$) more the probability of +1