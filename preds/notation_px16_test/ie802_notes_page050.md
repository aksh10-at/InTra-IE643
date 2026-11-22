Finding good upper bounds:

$$\min f(x,y) \quad \text{st. } g_i(x,y)\le0, i=1,2\dots m$$

$$x\in\mathbb{R}^n, y\in\mathbb{Z}^p$$

* Upper bound → find a feasible point as fast as possible (as low obj. value as possible) — Heuristic

**Good upper bound**
- prune the tree easily
- give a good solution in limited time

* Gurobi may have 60-70 heuristics.

## Heuristics

$\hookrightarrow$ KLA construction heuristics (Don't need a feasible point to start)
$\hookrightarrow$ Starting Heuristics (try to construct a soln from scratch)

$\hookrightarrow$ Improvement Heuristics (start with given a feasible soln $\to$ find better solns)

**MINLOs:**

$\hookrightarrow$ Heuristic for unconstrained models
$\hookrightarrow$ For model with many feasible solutions.
$\hookrightarrow$ For models with few solutions (difficult task)

> another way to classify

Heuristic $\hookrightarrow$ General purpose (structure independent)
$\hookrightarrow$ Class specific (only Quadratic, Contin. Non Convex Quadratic, conv. MIQP, conic integer models)
$\hookrightarrow$ Application Specific (portfolio opt., power flow problems, cutting stock, VRP, packing, Quad. assignment..)