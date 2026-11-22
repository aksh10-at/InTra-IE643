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


<!-- page: ie802_notes_page041 -->

# Separation Problem

![A squiggly "S" shape with "$S$ not possible" below.](figures/ie802_notes_page041_b1.png){width=55.0000%}

![$S$ and $T$ separated by an arrow, labeled "Separate $S$ from $T$ by a hyperplane... on linear."](figures/ie802_notes_page041_b2.png){width=46.3698%}

### Separation Problem

![A wavy line graph with two labeled regions $S1$ (above) and $S2$ (below), with a red separating line through the middle.](figures/ie802_notes_page041_b3.png){width=44.7932%}

relax into two parts

![Two overlapping "S1" regions, each with a red separating line through them.](figures/ie802_notes_page041_b4.png){width=30.1953%}

![A scatter plot of points with a red separating line, labeled "minimize flat hat 2-norm" — "split cutg..." — "not necessary" — "no good" — "too big of separation" — "using convex hulls" — "shrink" — "and convex hull".](figures/ie802_notes_page041_b5.png){width=55.0000%}

![A polygonal region with a red separating line through it, labeled "split cutg..." — "this has been done before" — "(shrinkage needs more research)".](figures/ie802_notes_page041_b6.png){width=42.1185%}

<!-- page: ie802_notes_page042 -->

# Split inequalities:

If $\beta^* \le \beta$

$\Rightarrow$ Then it is valid for $S$ ($\forall x \in S$)

![A set $S$ split into two regions by a vertical line, labeled "S" on the left and "$11$" on the right.](figures/ie802_notes_page042_b1.png){width=49.1559%}

$\hookrightarrow \forall x \in B$: To check the inequality is valid for $S$, find $\beta^* = \max_{x \in S} \alpha x$ st. $x \in S$

Let $S = S_1 \cup S_2$

![Two overlapping sets $S_1$ and $S_2$.](figures/ie802_notes_page042_b2.png){width=49.8332%}

Suppose $\alpha x \le \beta$ is valid for both $S_1$ and $S_2$.

Then $\alpha x \le \beta$ is valid for $S$.

![Two separate sets $S_1$ and $S_2$ each with a line $\alpha x \le \beta$ through them.](figures/ie802_notes_page042_b3-r1.png){width=36.4170%}

$\hookrightarrow$ how to find cutting planes?

$\hookrightarrow$ Split in different ways

![An oval region split by a red line into two halves, labeled $R_1$ on the left and a shaded region on the right.](figures/ie802_notes_page042_b4.png){width=55.0000%}

$\hookrightarrow$ And inequality valid for both half

<!-- page: ie802_notes_page043 -->

$$\min c^Tx+d^T\theta$$
$$\text{st } g_i(x,\theta)\le0 \quad i=1,2\dots m$$
$$x\in\mathbb{R}^n, \quad \theta\in\mathbb{Z}^p$$

$$S = \{(x,\theta): x\in\mathbb{R}^n, \theta\in\mathbb{Z}^p, g_i(x,\theta)\le0, i=1,2\dots m\}$$

$$R = \{(x,y): x\in\mathbb{R}^n, y\in\mathbb{R}^p, g_i(x,y)\le0, i=1,2\dots m\}$$

Find $(x,\theta)$ st it is valid for $S$ but not $R$

**Step ①** *Pick a disjunction (OR)*

- $y_1\le0$ or $y_1\ge1$
- $y_5\le4$ or $y_5\ge5$
- $y_5+y_6+y_3\le1$ or $y_5+y_6+y_4\ge2$

**②**
$$S_1 = \{(x,y): x\in\mathbb{R}^n, y\in\mathbb{Z}^p, g_i(x,y)\le0, i=1,2\dots m, y_1\le1\}$$
$$S_2 = \{\dots, y_1\ge2\}$$
$$S = S_1\cup S_2$$

**Step③** Relax $\to R_1$ and $R_2$
$$R_1 = \{(x,y): x\in\mathbb{R}^n, y\in\mathbb{R}^p, \dots, y_1\le1\}$$
$$R_2 = \{y\in\mathbb{R}^p, y_1\ge2\}$$

<!-- page: ie802_notes_page044 -->

# Convex Hull

Step (4) And $\alpha x + \gamma y \le \beta$, valid for both R1 and R2

G use R1, R2 ... together to Red line.
$\Rightarrow$ There are lots of lines like the Red line (infinite)

* Stuber & Mehrotra, 1999
  Give the convex hull of $R_1 \cup R_2$ under the assumptions:
(i) $y$ = binary
(ii) $R_i$s are bounded
(iii) disjunctions used like $y_i=0$ or $y_i=1$

- Convex hull is given by $(x^1,y^1) \in R_1$, $(x^2,y^2) \in R_2$
  $(x,y) = \lambda^1(x^1,y^1) + \lambda^2(x^2,y^2)$ with $\lambda^1+\lambda^2=1$, $\lambda^1\ge0$, $\lambda^2\ge0$

![A red line (convex hull boundary) through a set of marked points on an oval curve, illustrating the convex hull concept.](figures/ie802_notes_page044_b1.png){width=55.0000%}

$$M(x^1)$$
$$m = \begin{bmatrix} x_1^1 \\ x_1^2 \\ y_1^1 \\ y_1^2 \\ \lambda_1^1 \\ \lambda_1^2 \end{bmatrix}, \quad \text{assuming } y_1=0 \text{ or } y_1=1$$

Form new constraints in place of difficult set:
$$x = \bar{x}_1 + \bar{x}^2, \quad y = \bar{y}_1 + \bar{y}_2$$

difficult posn $\to$ base posn

$$\exists i(x^i,y^i)\le0 \to cx$$
$$\exists i(x^2,y^2)\le0 \to cx$$
$$x=\lambda^1x^1+\lambda^2x^2 \to ncx$$
$$y=\lambda^1y^1+\lambda^2y^2 \to ncx$$
$$\lambda^1+\lambda^2=1 \to cx$$
$$x^1,x^2\ge0 \to cx$$
$$y_1^1=0, y_1^2=1 \to cx$$
