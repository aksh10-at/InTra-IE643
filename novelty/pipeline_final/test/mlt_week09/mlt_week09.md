---
title: "MLT Week 9"
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


<!-- page: mlt_week09_page001 -->

# Perceptron Learning Algorithm

## Discriminative Model for Classification

How to model $P(y=1/x)$?

Simplest assumption: $P(y=1/x) = \begin{cases} 1 & \text{if } w^Tx \ge 0 \\ 0 & \text{otherwise} \end{cases}$

$\therefore$ Data is Linearly Separable.

![Two scatter plots — one with a clear linear separator (left, "Linear separate exists"), the other with overlapping clusters (right, "No linear separator").](figures/mlt_week09_page001_b1.png){width=55.0000%}

Can we develop algorithms with the assumption that the data is linearly separable?

**Goal:** $\min_{h \in H_{\text{linear}}} \sum_{i=1}^{n} I(h(x_i) \ne y_i)$

$$H_{\text{linear}} = \{ h_w : h_w(w) = \text{sign}(w^Tx) \}$$

assuming "Linear Separability"

---

## Perceptron Algorithm

Input: $\{(x_1,y_1),\dots,(x_n,y_n)\}, \quad x_i \in \mathbb{R}^d, \quad y_i \in \{+1,-1\}$

<!-- page: mlt_week09_page002 -->

$i=1,\dots,D$, $(x_1,y_1),\dots,(x_n,y_n)$, $w_i \in \mathbb{R}$

Iteration: $w^0 = 0 \in \mathbb{R}^d$

$$Y_i \in \{+1,-1\}, \qquad [0 \; 0 \; 0 \; \dots \; 0]$$

until convergence,
- Pick $(x_i, y_i)$ pair from the dataset
- If $\text{sign}(w^T x_i) = \text{sign}(y_i)$, do nothing
else, $w^{t+1} = w^t + x_i y_i$ &nbsp;&nbsp;&nbsp;← update rule

<!-- page: mlt_week09_page003 -->

# Understanding the Perceptron Update Rule

If mistake, then $w^{t+1} = w^t + x_i y_i$

### Mistake 1
Predicted: +1, Actual: -1, $y_i = -1$
$$w^{t+1} = w^t + x_i y_i$$
$$(w^{t+1})^T x_i = (w^t + x_i y_i)^T x_i = w^T x_i + y_i \|x_i\|^2 \ge 0 \; (>0) \to \text{Negative}$$

### Mistake 2
Predicted: -1, Actual: +1, $y_i = +1$
$$(w^{t+1})^T x_i = w^T x_i + y_i \|x_i\|^2 < 0 \; (>0)$$

The update rule pushes $w$ in the right direction for $x_i$.

**Example 1:** $w^{new} = w^{old} + x_i \frac{y_i}{y}$

![Two scatter plots of data points with a dashed decision boundary line, showing an initial misclassified point near the origin being corrected by the update rule, resulting in a new, more accurate boundary.](figures/mlt_week09_page003_b1.png){width=55.0000%}

- Fixing $w$ for one $x$, might affect decision for other data points.

<!-- page: mlt_week09_page004 -->

# Proof of Convergence of Perceptron Algorithm

We need more careful argument for convergence.

### Example 2

![A line through the origin with a point $(\begin{bmatrix}1\\1/2\end{bmatrix},-1)$ on one side labeled $+1$, and $(\begin{bmatrix}-1\\0\end{bmatrix},+1)$, $(\begin{bmatrix}0\\-1\end{bmatrix},+1)$ on the other side.](figures/mlt_week09_page004_b1.png){width=55.0000%}

Is this a linearly separable dataset?

$$\left\{\begin{bmatrix}0\\1\end{bmatrix},+1 \; ; \; \begin{bmatrix}0\\-1\end{bmatrix},+1 \; ; \; \begin{bmatrix}-1\\1/2\end{bmatrix},-1\right\}$$

Is there a $w\in\mathbb{R}^2$ st $w^Tx_i>0\Rightarrow y_i=+1$, $w^Tx_i<0\Rightarrow y_i=-1$?

**There is**

![Same line through the origin, but now with a point $(\begin{bmatrix}1\\1/2\end{bmatrix},-1)$ on the "wrong" side (below the line) labeled $+1$, and $(\begin{bmatrix}-1\\0\end{bmatrix},+1)$, $(\begin{bmatrix}0\\-1\end{bmatrix},+1)$ still on the "correct" side above the line.](figures/mlt_week09_page004_b2.png){width=55.0000%}

---

![A scatter plot of points $\begin{bmatrix}0\\1\end{bmatrix}$, $\begin{bmatrix}-1\\1/2\end{bmatrix}$, $\begin{bmatrix}-1\\-1\end{bmatrix}$, $\begin{bmatrix}1\\-1\end{bmatrix}$, all labeled $+1$. A separating line through the origin is shown, with an arrow from $\begin{bmatrix}-1\\1/2\end{bmatrix}$ to $\begin{bmatrix}1\\1/2\end{bmatrix}=w^*$, and another arrow from $\begin{bmatrix}-1\\-1\end{bmatrix}$ to $\begin{bmatrix}1\\-1\end{bmatrix}=w^*$.](figures/mlt_week09_page004_b3.png){width=49.4891%}

**Perceptron**

$$w^0 = \begin{bmatrix}0\\0\end{bmatrix}, \quad w^0{}^T x_1 = 0, \quad w^0{}^T x_2 = 0, \quad w^0{}^T x_3 = 0, \quad \hat{y}_1 = +1, \quad \hat{y}_2 = +1, \quad \hat{y}_3 = +1$$

$$w^1 = w^0 + x_3 y_3 = \begin{bmatrix}0\\0\end{bmatrix} + \begin{bmatrix}-1\\1/2\end{bmatrix} \cdot -1$$

<!-- page: mlt_week09_page005 -->

$$w^1 = w^0 + x_3y_3 = \begin{bmatrix}0\\0\end{bmatrix}+\begin{bmatrix}-1\\1/2\end{bmatrix}\cdot1 = \begin{bmatrix}-1\\1/2\end{bmatrix}$$

$$w^2 = w^1+x_1y_1 = \begin{bmatrix}-1/2\\1/2\end{bmatrix}+\begin{bmatrix}0\\1\end{bmatrix}\cdot1 = \begin{bmatrix}-1/2\\1/2\end{bmatrix}$$

$$w^3 = w^2+x_2y_2 = \begin{bmatrix}1\\0\end{bmatrix}+\begin{bmatrix}0\\1\end{bmatrix}\cdot1 = \begin{bmatrix}1\\1\end{bmatrix}$$

$$w^3 = \begin{bmatrix}1\\-1/2\end{bmatrix} = w^1$$

We see that we are right back where we started. The algorithm is unable to provide a $w$ which can correctly classify all the data points correctly. It just won't converge. Let's modify our assumption.

---

### Assumption

**Linear Separability with $\delta$-Margin**

![Two overlapping green and yellow regions separated by a margin band, labeled $\{x:w^Tx\ge\gamma\}$ and $\{x:w^Tx\le-\gamma\}$, with a separating line $w$ through the origin, and a shaded gap between them.](figures/mlt_week09_page005_b1.png){width=51.0495%}

A dataset $\{(x_1,y_1),\dots(x_n,y_n)\}$ is linearly separable with $\gamma$-margin if $\exists w\in\mathbb{R}^d$ st $(w^Tx_i)y_i\ge\gamma\; \forall i$, some $\gamma>0$.

<!-- page: mlt_week09_page006 -->

### Proof of Convergence of Perceptron Algorithm

### Radius Assumption
$\forall i \in$ Dataset, $\|x\|_2 < R$, for some $R > 0$

![A circle of radius $R$ centered at the origin with several data points (green crosses and red dots) inside it, each labeled with an arrow pointing from the origin.](figures/mlt_week09_page006_b1.png){width=43.7460%}

Without loss of generality, assume $\|w^*\| = 1$

![A dot product decision boundary around the origin — a circle of radius $y'/\|w^*\|$ — with a green vector $w^*$ inside it, and two sets of data points ($+$'s and $-$'s) on either side of the boundary.](figures/mlt_week09_page006_b2.png){width=55.0000%}


```latex
\{x: w^*^Tx = y'\} \qquad \{x: w^Tx = y\}
```

*Warning: equation could not be typeset; shown as written.*



```latex
\frac{w^*^Tx}{\|w^*\|} = \frac{y}{\|w^*\|}, \qquad y' = \frac{y}{\|w^*\|}
```

*Warning: equation could not be typeset; shown as written.*


$$\boxed{(w^*)^Tx = y'} \qquad \boxed{(w^*)^Tx = y}$$

---

### Analysis of "Mistakes" of Perceptron

- Observe that an update happens only when a mistake occurs.
- Let $w^l$ be the current $w$ & a mistake occurs in wrt $(x,y)$
  $$\therefore w^{l+1} = w^l + x \cdot y$$

<!-- page: mlt_week09_page007 -->

$$\|w^{l+1}\|^2 = \|w^l + xy\|^2 = (w^l + xy)^T(w^l + xy) = \|w^l\|^2 + 2(w^Tx)y + \|x\|^2y^2 \le 0 \text{ because mistake}$$

$$\|w^{l+1}\|^2 \le \|w^l\|^2 + R^2$$
$$\|w^{l+1}\|^2 \le (\|w^{l-1}\|^2 + R^2) + R^2$$
$$\vdots$$
$$\|w^{l+1}\|^2 \le \|w^0\|^2 + lR^2$$

$$\boxed{\|w^{l+1}\|^2 \le lR^2} \quad \text{(no of mistakes)} \tag{①}$$

$$(w^{l+1})^Tw^* = (w^l + xy)^Tw^* = w^Tw^* + (w^{*T}x)y \ge \gamma$$

$$(w^{l+1})^Tw^* \ge w^Tw^* + \gamma$$
$$\ge (w^{l-1}w^* + \gamma) + \gamma$$

<!-- page: mlt_week09_page008 -->

$$(w^{l+1})^Tw^* \ge (w^*)^Tw^* + l\delta$$

$$\boxed{(w^{l+1})^Tw^* \ge l\delta}$$

---

For any $(x,y)$,

![A point $y$ on the axis with a dashed line to an off-axis point labeled $x$, and a dot at the origin.](figures/mlt_week09_page008_b1.png){width=55.0000%}

$$\left\|\frac{x^Ty}{\|y\|^2}y\right\|^2 \le \|x\|^2 \quad \text{[Pythagoras]}$$

$$(x^Ty)^2 \frac{\|y\|^2}{\|y\|^4} \le \|x\|^2$$

**Cauchy-Schwarz Inequality**

$$(x^Ty)^2 \le \|x\|^2\|y\|^2$$

From ②:
$$l^2 \le (w^{l+1})^Tw^*$$
$$\Rightarrow l^2 \le ((w^{l+1})^Tw^*)^2 \le \|w^{l+1}\|^2\|w^*\|^2 \quad \text{[from C-S]}$$

$$\Rightarrow \|w^{l+1}\|^2 \ge l^2$$

<!-- page: mlt_week09_page009 -->

$$\|w^{t+1}\|^2 \le l R^2 \quad \text{from (3)}$$

$\Rightarrow \|w^{t+1}\|^2 \le l R^2$

$\Rightarrow \boxed{l \le \frac{R^2}{\gamma^2}} \leftarrow$ Radius Margin Bound

Since $\gamma^2 > 0$, no. of mistakes is finite

$\therefore$ **PERCEPTRON CONVERGES**

<!-- page: mlt_week09_page010 -->

# Sigmoid Functions for Modeling Class Probabilities

Linear Separability in terms of Probability:
$$P(y=1/x) = 1 \quad \text{if } w^Tx \ge 0$$
$$= 0 \quad \text{otherwise}$$

Can we somehow relax this assumption? Can we model probabilities differently?

---

Start with a simple linear model.
$$z = w^Tx \leftarrow \text{feature } x \in \mathbb{R}^d$$

![A 2D plot showing a line through the origin (normal vector $w$) with several points $x_1, x_2, x_3, x_4$ marked on either side, labeled $\{x:w^Tx=-15\}$, $\{x:w^Tx=-5\}$, $\{x:w^Tx=0\}$, $\{x:w^Tx=1\}$, $\{x:w^Tx=100\}$, illustrating the decision boundary.](figures/mlt_week09_page010_b1.png){width=55.0000%}

How to label $\{x_1,x_2,x_3,x_4\}$?
We are going to attach probability for the label to be +1 or -1 to each point.

How to decide the probability? By high or low the "score" of each point is.
The score will be $z=w^Tx$, $z \in [-\infty,\infty]$

- Larger the score ($z=w^Tx$) more the probability of +1

<!-- page: mlt_week09_page011 -->

**Nice versa**

Link Function

- $g(z) = 0 \text{ if } z=0$ (point lying on the separator)
- $g(z) \to +1 \text{ if } z \to \infty$
- $g(z) \to -1 \text{ if } z \to -\infty$

$$g(z) = \frac{1}{1+e^{-z}} \quad \text{(Sigmoid/logistic function)}$$

![A sigmoid curve labeled $g(z)=1/e^{z^2}$, with asymptotes at $y=0$ and $y=1$, crossing through $(0,0.5)$, and increasing steeply from left to right.](figures/mlt_week09_page011_b1.png){width=55.0000%}

<!-- page: mlt_week09_page012 -->

# Logistic Regression

$$P(y=1/x) = \frac{1}{1+e^{-w^Tx}} \quad \text{Dataset: } \{(x_1,y_1),\dots,(x_n,y_n)\}$$

How to find $w$: **Maximum Likelihood**

$$L(w; \text{Data}) = \prod_{i=1}^{n} (g(w^Tx_i))^{y_i}(1-g(w^Tx_i))^{(1-y_i)}$$

$$\log L(w; \text{Data}) = \sum_{i=1}^{n} y_i \log(g(w^Tx_i)) + (1-y_i) \log(1-g(w^Tx_i))$$

$$= \sum_{i=1}^{n} y_i \log\left(\frac{1}{1+e^{-w^Tx_i}}\right) + (1-y_i) \log\left(\frac{e^{-w^Tx_i}}{1+e^{-w^Tx_i}}\right)$$

$$\log L(w) = \sum_{i=1}^{n} \left[(1-y_i)(-w^Tx_i) - \log(1+e^{-w^Tx_i})\right]$$

**Goal:** $\max_w \sum_{i=1}^{n} (1-y_i)(-w^Tx_i) - \log(1+e^{-w^Tx_i})$

No closed form expression — can perform gradient descent (ascent)

$$\nabla \log L(w) = \left[(1-y_i)(-x_i) - \left(\frac{e^{-w^Tx_i}}{1+e^{-w^Tx_i}}\right)(-x_i)\right]$$

$$= \left[-x_i + y_ix_i + x_i\frac{e^{-w^Tx_i}}{1+e^{-w^Tx_i}}\right]$$

<!-- page: mlt_week09_page013 -->

$$= \sum_{i=1}^{n} \left[ -x_i + y_i x_i + x_i \frac{e}{1+e^{-w^T x_i}} \right]$$

$$= \sum_{i=1}^{n} \left[ y_i x_i - x_i \left( \frac{1}{1+e^{-w^T x_i}} \right) \right]$$

$$\nabla \log L(w) = \sum_{i=1}^{n} \left[ x_i \left( y_i - \frac{1}{1+e^{-w^T x_i}} \right) \right]$$

**Gradient update rule**

$$w_{t+1} = w_t + \eta_t \nabla \log L(w)$$
$$= w_t + \eta_t \left( \sum_{i=1}^{n} \left[ x_i (y_i - \frac{1}{1+e^{-w_t^T x_i}}) \right] \right)$$

![A green box containing $x_i$, an arrow to $y_i$, an arrow to $\theta_i \in \mathbb{R}^d$, an arrow back to the green box via $g(w_t^T x_i)$, with a label $\{0,1\}$ near $y_i$.](figures/mlt_week09_page013_b1.png){width=55.0000%}

### Regularized Version

$$\min_w \sum_{i=1}^{n} \left[ \log(1+e^{-w^T x_i}) + y_i x_i (1-y_i) \right] + \frac{\lambda}{2} \|w\|^2$$

cross validate hyperparameters. Regularized.
