---
title: "IE802 Notes"
geometry: margin=2.2cm
papersize: letter
fontsize: 10pt
header-includes:
  - \usepackage{float}
  - \floatplacement{figure}{H}
  - \usepackage{fvextra}
  - \DefineVerbatimEnvironment{Highlighting}{Verbatim}{breaklines,breakanywhere,commandchars=\\\{\}}
  - \usepackage{cancel}
---


<!-- page: ie802_notes_page045 -->

# Projection of M

Projection of M on $(x,y)$ space is convex hull of RI U R2

$$M_{convex} = \left\{ x^1,\bar{x}^1,\bar{x}^2,\bar{y}^1,\bar{y}^2; x,y,\lambda^1,\lambda^2 \right\}$$

$$\lambda^1g_1(\frac{\bar{x}^1}{x^1},\frac{y^1}{x^1})\le0$$
$$\lambda^2g_1(\frac{\bar{x}^2}{x^1},\frac{y^2}{x^1})\le0$$
$$x=\bar{x}^1+\bar{x}^2$$
$$y=\bar{y}^1+\bar{y}^2$$

$\to$ all are convex now.

**perspective function**

$$p(\cdot) = \begin{cases} \lambda^1g_1(\frac{\bar{x}^1}{x^1},\frac{y^1}{x^1}) & \lambda^1>0 \\ 0 & \lambda^1=0 \end{cases}$$

Upcoming:
- Intersection cuts
- Cuts for non-convex Quadratic $\Rightarrow$ Heuristic

Next Thursday
2-3 min per team short presentation
Next to next -> Colorout class

<!-- page: ie802_notes_page046 -->

# Intersection Cuts

**Topics to be discussed:**
- Intersection Cuts
- Cut for non-convex quadratics
- Heuristics

### Intersection Cuts:

$$\min c^Ty \quad A y \le b \quad y \in \mathbb{Z}^p$$

![A polygon with vertices marked by "x"s, one red dot labeled "corner point" at the bottom right.](figures/ie802_notes_page046_b1.png){width=55.0000%}

**(i) Solve LP relaxation where we will be at corner**

**(2) If we drop other constraints which are not active, we end up only 2 constraints.**
[Diagram: A cone with a few "x" points inside, some outside, and an arrow pointing to a point inside the cone labeled "we still get some points".]

**(3) If we look at integer points present, it is translation of cone. This is relaxation of original set.**

We can chop off some points by looking at cone.

![A cone with several "x" points inside and a few outside, an arrow from a point inside the cone to another point outside labeled "yield cut for original problem too", with a note "has to get these cuts".](figures/ie802_notes_page046_b2.png){width=46.7382%}

We create a disjunction as all points on one of these sides leave out the points. No feasible lb hand line, all int $\to$ below or above.

- We reach from corner to corner, or point and line.

![A region with a red cross through it, labeled "current plane", and a note "intersection of tiny region does not have any feasible point".](figures/ie802_notes_page046_b3.png){width=55.0000%}

<!-- page: ie802_notes_page047 -->

- We can choose any corner point initially, but the disjunction should be cutting the corner point (on) the corner point should be *into* the 2 disjunctions to cut-off.
- If the starting point is not a corner of feasible region but infeasible region.

![A polygon with a marked corner point, labeled "basic Gom point", and an arrow labeled "cut off here as much deeper".](figures/ie802_notes_page047_b1.png){width=55.0000%}

This idea can be extended to non-convex too.

$$g_1(x,y)\le0$$

a) When $g_1$ is convex

![A square containing a smaller circle — a convex set.](figures/ie802_notes_page047_b2.png){width=44.2565%}

b) Suppose $g_1$ is concave

- $m_1^2-m_2^2\le-1$
- outside circle

![An irregular shape with a small circle inside, labeled "we cant chop off the palm".](figures/ie802_notes_page047_b3.png){width=55.0000%}

We take relaxation of this case.

- Suppose we have some linear constraints
- Since hand we have concave

- We may get corner point if it is infeasible region then we are done

If not like that we start to remove to extract region

![A rectangle with a red dot marked on one side, labeled "not useful".](figures/ie802_notes_page047_b4.png){width=41.2949%}

How to show the cut is valid, to prove the infeasible is empty (or) not useful

![A shaded region with a marked point, labeled "Valid cut".](figures/ie802_notes_page047_b5.png){width=54.3233%}

Since $g(\cdot)$ is concave

* The part which is infeasible is convex set, using this we can check there is nothing below it..

<!-- page: ie802_notes_page048 -->

only convex for $g(x)$ is concave

![A shaded region with a cut through it, illustrating the idea of traveling 2 sides of a corner point and cutting all the edge of infeasible region then draw a cut.](figures/ie802_notes_page048_b1.png){width=55.0000%}

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

<!-- page: ie802_notes_page049 -->

$$\min x^TQx + c^Tx \qquad 0\le x_i\le1 \to \text{Noninteger}$$

$\hookrightarrow$ Introduce $y_i$ variable.

$$\min \sum Q_{ij}x_ix_j + \sum Q_{ii}y_i + \sum c_ix_i$$
$$x_{ij}=x_1x_2 \; \forall i,j$$
$$y_i=x_i^2 \; \forall i$$
$$0\le x_i\le1$$

$\hookrightarrow$ In case of only boolean $x\in\{0,1\}$, Padberg triangle inequalities.

$$\min \sum Q_{ij}x_ix_j + \sum c_ix_i$$
st $\quad x_{ij}=x_1x_2$
$\qquad x_i\in\{0,1\}\; \forall i$

$\hookrightarrow$ Convex hull of $\to$ is same as convex hull of $x_{ij}=x_1x_2$, $0\le x_i\le1$

Result by Burer and Letchford.

<!-- page: ie802_notes_page050 -->

# Finding Good Upper Bounds

**Finding good upper bounds:**

$$\min f(x,y) \quad \text{st. } g_i(x,y) \le 0, i=1,2,\dots m$$
$$x \in \mathbb{R}^n, y \in \mathbb{Z}^p$$

* Upper bound → find a feasible point as fast as possible, as low obj. value as possible $\to$ **Primal Heuristic**

**Good upper bound**
- Prune the tree easily
- Give a good solution in limited time

* Churobi may have 60-80 heuristics...

### Heuristics

$\hookrightarrow$ Starting Heuristics (Don't need a feasible point to start) $\to$ Kla construction heuristics
$\hookrightarrow$ Try to construct a soln from scratch

$\hookrightarrow$ Improvement Heuristics (start with given a feasible soln $\hookrightarrow$ find better solns)

**MINLOs:**

$\hookrightarrow$ Heuristic for unanchored models
$\hookrightarrow$ For model with many feasible solutions.
$\hookrightarrow$ For models with few solutions (difficult task)

> another way to classify

Heuristic $\hookrightarrow$ General purpose (structure independent)
$\hookrightarrow$ Class specific (only Quadratic, Contin. NonConvex Q, Conv. MIQP, conic integer models)
$\hookrightarrow$ Application Specific (portfolio opt., power flow problems, cutting stock, VRP, packing, Quad. assignment..)

Imp.

<!-- page: ie802_notes_page051 -->

$$\min f(x,y) \quad x \in \mathbb{R}^n, \; y \in \mathbb{Z}^p$$

(1) **Algo-1**
1. Pick a random point $(x,y)$ with $x \in \mathbb{R}^n$ and $y \in \mathbb{Z}^p$
2. Check if it is best
3. Go to 1 (until... value not improves) $\to$ stopping criteria is important works but Not so good... $\to$ we have good idea after many trials

**Neighbourhood search:**

(2) **Algo-2**
1. Solve continuous relaxation
2. Round $y$ to nearest integer $\hookrightarrow$ Good if convex problem relaxation is there

Also couple with Neighbourhood search

1. Try different rounding.

we get: $y = \begin{bmatrix}0.6 \\ 0.4 \\ 0.2 \\ 0.5\end{bmatrix}$

$$\min f(x,y) \qquad \sum_{i=1}^{p} y_i = k, \quad y_i \in \{0,1\}, \; i=1\dots p$$

(1) Algo-1 $\to$ same mostly most soln on $x$.. if 0 or 1 not blu...

<!-- page: ie802_notes_page052 -->

**Continuous Non-convex Quadratic Models:**

$$\min \frac{1}{2}x^TQx + c^Tx$$
$$\text{st } \frac{1}{2}Q_i x^T Q_i x + q_i^T x \le b_i$$
$$l \le x \le u$$

**0 Multistart NLP Heuristic**
- Give it to a local gradient based solver

![A wavy curve with a local minimum marked at the start, and another point further along the curve.](figures/ie802_notes_page052_b1.png){width=55.0000%}

also give them another point, if not good then previous take another point

**0 Under cover heuristic**
- You pick some $x$ values
  suppose p=100
  $\Rightarrow$ pick 90 and fix for some values

$$x_1^2+5x_1x_2+7x_3x_4+x_1x_3-2x_1x_4 \le 1$$

**ISAC Heuristic**
$x_1=2$, $x_3=1$
$\to$ next choose values and solve NLP (take $x_1,x_2$ as anything, change available)

- how to know which variable to pick and what value? $\to$ Trial and error

![A graph with nodes $x_1, x_2, x_3, x_4$ — $x_1$ has edges to $x_2$ and $x_4$, $x_3$ has an edge to $x_4$.](figures/ie802_notes_page052_b2.png){width=55.0000%}

pick smallest node so that every set is covered.
- G find smallest node (edge) cover fan this graph so that every edge is covered.

$(x_1,x_3)$ & $(x_1,x_4)$ Solve..

<!-- page: ie802_notes_page053 -->

# Heuristics for MINLO

### Initial Construction Heuristic

- Feasibility Pump (expensive)
- Rounding (sophisticated)
- Branching
- Local Branching

### MZLP Case: (Pure Binary)

$$\min c^T x \quad Ax \le b \quad x \in \{0,1\}^n$$

**① Solve the LP**

$$\min c^T x \quad Ax \le b \quad 0 \le x \le 1 \quad \Rightarrow \hat{x}$$

$\hookrightarrow$ If fractional $\to$ round it to nearest integer

$\hookrightarrow$ Not always works

Simple rounding of $\hat{x} = \begin{bmatrix} \lceil x_1 \rceil & \text{if } x_1 < 0.5 \\ \vdots \\ \lceil x_k \rceil & \text{on } \lceil x_k \rceil \end{bmatrix}$

$$\min \|x - \hat{x}\|_1, \quad x \in \{0,1\}^n, \; Ax \le b$$

This will always give integers but hard...

**②** $\min_{i=1}^{n} |x_i - \hat{x}_i|$

$$Ax \le b, \quad 0 \le x \le 1 \quad \Rightarrow \hat{x} \to \text{LP relaxation soln}$$

ex: $\hat{x} = \begin{bmatrix} 0 \\ 0.4 \\ 0.6 \\ 0.8 \\ 0.2 \end{bmatrix}$, sound($\hat{x}$) = $\begin{bmatrix} 0 \\ 0 \\ 1 \\ 1 \\ 0 \end{bmatrix}$

$\hookrightarrow$ not working, too bad

becomes: $\min |x_1-0| + |x_2-0| + |x_3-1| + |x_4-1| + |x_5-1| + |x_6-0|$

st $Ax \le b$, $0 \le x \le 1$

$$\min x_1+(1-x_2)+x_3+(1-x_4)+(1-x_5)+x_6$$

st $Ax \le b$, $0 \le x \le 1$

$\star$ if $\hat{x} = \begin{bmatrix} 0.1 \\ 0.9 \\ 0 \\ 0 \\ 0 \end{bmatrix}$, again round off gives same gain $\to$ we have to stop heuristic and flip some variables.

<!-- page: ie802_notes_page054 -->

# Convex MINLO Case (Pure Binary)

$$\min c^Tx+d^Ty$$
$$g_i(x,y)\le0 \quad i=1,\dots,p$$
$$x\in\mathbb{R}^n, \quad y\in\{0,1\}^p \to \text{continuous}$$

① Solve NLP relaxation $\Rightarrow$ get $\hat{x},\hat{y}$ → round of $\Rightarrow$ you can also solve MILP relaxation

② min $\sum_{i=1}^{p}|y^i-\text{round}(\hat{y}^i)|$
st $g_i(x,y)\le0$, $0\le y\le1$

$\Leftrightarrow$ MIP: $\min\sum|y^i-\text{round}(y^i)|$
st $\nabla$ inequalities at $(\hat{x},\hat{y})$, $0\le y\le1$

$$\Rightarrow \begin{bmatrix}\vdots\\\vdots\\\vdots\end{bmatrix}, \qquad y\in\{0,1\}^p$$

**Non-convex MINLO Case (Pure Binary)**

$\Rightarrow$ Leave it...

---

### RINS Heuristic (Relaxed-Induced Nbd Search) → Improvement

**Convex MINLO:** Let $(\hat{x},\hat{y})$ be known solution of MINLO

![A tree with root node branching into two children, each of which branches further.](figures/ie802_notes_page054_b1.png){width=42.7726%}

① Solve NLP relaxation of that node $\Rightarrow (\hat{x},\hat{y})$, $\hat{y}\notin\mathbb{Z}^p$ → if majority of equal, randomly fix ($\hat{y}_i=\bar{y}_i$)

② comp. $\hat{y}$ and $\bar{y}$ → all those same → fix it

③ Solve the smallest MINLO → don't solve fully but time limits, ex. 5 sec., and some other parameters.

<!-- page: ie802_notes_page055 -->

# Local Branching (Improvement)

Let $(\hat{x}, \hat{y})$ be a known solution, $\hat{y} \in \mathbb{Z}^{n_1}$

![A branching tree — root splits into two children, each of which splits further, one branch ending at a node labeled "not useful" with $y=6$, violating cardinality constraint.](figures/ie802_notes_page055_b1.png){width=42.1142%}

$$p \sum_{i=1}^{n_1} y_i - \hat{y}_1 \le 5 \quad \text{(cardinality constraint)}$$

**LOCAL JUMP:** Solving LPs takes too long.

**Idiot Crash:**

$$\min c^T x, Ax \le b, x \in \mathbb{Z}^p$$

$$\min \sum w_i(b_i - a_i y)^+$$

**Initial Construction:**

$$2y_1 + y_2 - y_3 \le 7 \to y_1 \text{ should be small}$$
$$-y_1 + 2y_2 + y_3 \ge 9 \to y_1 \text{ should be small}$$

$$y_2 + y_0 + y_4 = 5$$
$$y_3 - y_4 + y_6 \le 8$$
$$0 \le y \le 10$$

set $y=0$

<!-- page: ie802_notes_page056 -->

# Recall:

**16-04-26**

- Extended cutting plane (convex MINLO)

**convex MINLO**
- ECP
- Queveda Crossmann
- Dusan and Grossmann
- Non-linear branch and bound
- Gurobi

- Separability
- Perspective reformulation $\checkmark$
- Automatic reformulation $\checkmark$

- Bound tightening
- Heuristics
  - Local Bb
  - RINS
  - Res Pump
  - Under Cover

- SDP relaxation
- Boolean Quadratic Polytope

- Cuts → MIR, CG, split cuts

- Secant?
- McCormick Zona
- RL7
- SOCI?
- Loth digl...
