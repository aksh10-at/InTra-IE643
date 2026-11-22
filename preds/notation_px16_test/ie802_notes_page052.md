## Continuous Non-convex Quadratic Models:

$$\min \frac{1}{2}x^TQx + c^Tx$$
$$\text{st } \frac{1}{2}x^TQ_ix^T + a_i^Tx \le b_i$$
$$l \le x \le u$$

**① Multistart NLP Heuristic**
- Give it to a local gradient based solver

[Diagram: A multi-peaked function with several local minima, labeled "Start" at the left minimum.]

also give them another point, if not good then previous take another point

**② Under cover heuristic**
- You pick some $x$ values
  suppose pc=100 $\to$ pick 90 and fix for some values

$$x_1^2+5x_1x_2+7x_3x_4+x_1x_3-2x_1x_4 \le 1$$

**i SA iteration**
$x_1=2$, $x_3=1$ → next chance values and solve NLP (take $x_1$ as anything, $x_4$ change variable)

- How to know which variable to pick and what values... (trial and error, e.g., graph)

[Diagram: A graph with nodes $x_1, x_2, x_3, x_4$ — $x_1$ has edges to $x_2$ and $x_4$, $x_4$ has an edge to $x_3$.]

- Pick smallest node so that every set is covered.
- Find smallest node (edge) cover fan this graph so that every edge is covered.

$(n_1,n_3)$, $(n_1,n_4)$ solve...