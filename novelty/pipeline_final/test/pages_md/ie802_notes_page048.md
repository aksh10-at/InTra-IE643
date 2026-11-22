only convex for $g(x)$ is concave

[Diagram: A shaded region with a cut through it, illustrating the idea of traveling 2 sides of a corner point and cutting all the edge of infeasible region then draw a cut.]

Not a valid cut as it cuts feasible set [egon holes]

- This works for high dim.
  - 3D $\to$ 2 constraints $\to$ move 3 direction to find points $\to$ draw hyperplane that intersect & plane
  - N dim $\to$ N direction $\to$ N points provided constraint is concave if work

$$x^TQ'x\le b_1 \quad \text{if } Q \text{ is PD it is convex}$$
$$\quad \text{if } Q \text{ is ND} \to \text{conex}$$

If neither P or ND

**DCP:** $x^T(Q'^+-Q'^-)\eta\le b_1$
$\downarrow$ diff of convex fn

in $\quad$ ND

also as,
$$x^TQ'^+\eta-w\le b_1 \to \text{convex}$$
concave, $\quad w-x^TQ'^-\eta\le0$

Tangent $\to$ convex
Intersection point $\to$ concave

In practical using simplex of intersection point $\to$ canon plane $\Rightarrow$ many solvers do not use it unless $Q\to$ diagonal..
