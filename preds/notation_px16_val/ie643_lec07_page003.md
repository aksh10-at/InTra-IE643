## Supervised Learning

$$D = \{(x^i, y^i)\}_{i=1}^{N}$$
$$x \ni x^i \in \mathbb{R}^d$$
$$y \ni y^i \in \{+1,-1\}$$

$$h: X \to Y$$ (MLP weights)

train a multilayered perceptron to find $h_{MLP}$

$$\min E = \sum_{i=1}^{N} e(y^i, \hat{y}^i)$$

[Diagram: A wavy error curve with a local minimum marked at some point $(w_1, w_2)$, labeled "NP-hard" — the curve has a sharp dip followed by a plateau, then rises again.]

local minimum
minimization is over weights of MLP.