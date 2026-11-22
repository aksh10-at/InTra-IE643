Gradient descent to solve

$$\min_{x \in \mathbb{R}^d} f(x) \qquad f: \mathbb{R}^d \to \mathbb{R}$$

**local minimum**
**saddle points**

$\to$ Start at $x^0 \in \mathbb{R}^d$

$\to$ for $k=0,1,2,\dots$

find a descent direction $u^k$
1) find step length $\alpha_k$
$x^{k+1} \leftarrow x^k + \alpha_k u^k$

[Diagram: A downward arrow from "ve gradient" (negative gradient) pointing to an oval labeled "local minimum" with a question mark next to it.]