**Topics to be discussed:**
- Intersection Cuts
- Cut for non-convex quadratics
- Heuristics

## Intersection Cuts:

$$\min c^T y \quad A y \le b, \quad y \in \mathbb{Z}^p$$

[Diagram: A polygon with labeled "corner point" at one vertex.]

(i) Solve LP relaxation → where we will be at corners.

(ii) If we drop other constraints which are not active, we end up only 2 constraints.
[Diagram: A set of lines intersecting at a single point, labeled "we still get same point".]

(iii) If we look at integer points present, it is translation of cone. This is relaxation of original set.

We can chop off some points by looking at cone.

[Diagram: A set of points on a plane with a line through the origin, labeled "has to get new cut", "valid cut for original problem too".]

We create a disjunction as all points on one of these sides leak out the points, no feasible lb hand line can int $\to$ below or above. We reach from corner to corner on point red lines.

[Diagram: A region with a red "cutting plane" through its interior, labeled "Interior of this region does not have any feasible points".]