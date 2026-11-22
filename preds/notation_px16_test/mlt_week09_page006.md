# Proof of Convergence of Perceptron Algorithm

## Radius Assumption
$$\forall i \in \text{Dataset}, \; \|x_i\|_2 < R, \; \text{for some } R > 0$$

[Diagram: A circle of radius $R$ centered at the origin, with several data points (green dots) inside it and arrows pointing from each point toward the origin.]

Without loss of generality, assume $\|\omega^*\| = 1$

[Diagram: A red circle of radius 1 centered at the origin, with a green arrow $\omega^+$ pointing outward, labeled $\{\omega^+ x = y'\}$, and a blue arrow $\omega^-$ pointing inward, labeled $\{x: \omega^- x = y\}$.]

$$\frac{\omega^+}{\|\omega^+\|} = \frac{y'}{\|\omega^+\|}, \qquad y' = \frac{y}{\|\omega^+\|}$$

$$\left(\frac{\omega^+}{\|\omega^+\|}\right)^T x = y', \qquad (\omega^*)^T x = y'$$

---

## Analysis of "Mistakes" of Perceptron

- Observe that an update happens only when a mistake occurs.
- Let $w^l$ be the current $w$ & a mistake occurs in wrt $(x,y)$
  $$\therefore w^{l+1} = w^l + x \cdot y$$