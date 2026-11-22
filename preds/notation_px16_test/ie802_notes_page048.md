only convex for $g'(x)$ is concave

[Diagram: A shaded region with a "cut" line through it that intersects the feasible region, labeled "Not a valid cut as it cuts feasible red."]

→ travel 2 sides of corner point and watch fill the edge of infeasible region then draw a cut.

- This works for high dim.
  - 3D → 2 constraints → move 3 direction to find points where hyperplane that intersect & plane
- N dim → N direction → N points provided constraint is concave if we're $x^TQ'x\le b_1$, if Q is PD it is convex, if Q is ND it is concave

If neither P nor ND

**DCP:** $x^T(Q'^+-Q'^-)x\le b_1$
↓ diff of convex fn

also as, $x^TQ'^+x-w\le b_1 \to$ convex, concave, $w-x^TQ'^-x\le0$

Tangent → convex, intersection point → concave

In practical using simplex of intersection points → on a plane → many solvers do not use it unless $Q\to$ diagonal.

Indefinite symmetric matrix can be decomposed to difference of 2 tv terms $\to$ using eigen value decomp.