# Understanding the Perceptron Update Rule

If mistake, then $w^{t+1} = w^t + x_i y_i$

## Mistake 1
Predicted: +1, Actual: -1, $y_i = -1$
$$w^{t+1} = w^t + x_i y_i$$
$$(w^{t+1})^T x_i = (w^t + x_i y_i)^T x_i = w^T x_i + y_i \|x_i\|^2 \ge 0 \; \text{Negative}$$

## Mistake 2
Predicted: -1, Actual: +1, $y_i = +1$
$$(w^{t+1})^T x_i = w^T x_i + y_i \|x_i\|^2 < 0 \; \text{>0}$$

The update rule pushes $w$ in the right direction for $x_i$.

**Example 1:** $w_{new} = w_{old} + x_i \frac{y_i}{\|y_i\|}$

[Diagram: Two scatter plots of red and green points, separated by an initial decision boundary $w^{ok}$ through the origin. The left shows a new point marked with a dashed arrow toward the origin, labeled "w new". The right shows the same plot with a new, steeper decision boundary $w^{ok}$, with a circle around some new errors.]

- Fixing $w$ for one $x$, might affect decision for other data points.