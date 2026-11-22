$$(w^{l+1})^Tw^* \ge (w^*)^Tw^* + l\gamma$$

$$\boxed{(w^{l+1})^Tw^* \ge l\gamma}$$

For any $(x,y)$,

[Diagram: A vector $x$ pointing to a shaded region, with an arrow from the origin to a point on the boundary labeled $\frac{x^Ty}{\|y\|^2}y$, and another arrow from that point to $y$.]

$$\left\|\left(\frac{x^Ty}{\|y\|^2}\right)y\right\|^2 \le \|x\|^2 \quad \text{[Pythagoras]}$$
$$(x^Ty)^2 \frac{\|y\|^2}{\|y\|^2} \le \|x\|^2$$
$$(x^Ty)^2 \le \|x\|^2\|y\|^2 \quad \text{Cauchy-Schwarz Inequality}$$

From ②:
$$l\gamma \le (w^{l+1})^Tw^*$$
$$\Rightarrow l^2\gamma^2 \le (w^{l+1})^Tw^* = \|w^{l+1}\|^2\|w^*\|^2 \quad \text{[from C.S.]}$$

$$\Rightarrow \|w^{l+1}\|^2 \ge l^2\gamma^2 \quad \text{③}$$