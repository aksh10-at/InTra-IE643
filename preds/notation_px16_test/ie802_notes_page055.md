## Local Branching (Improvement)

Let $(\hat{x}, \hat{y})$ be a known solution

[Diagram: A branching tree — root splits into 3 children, each of which splits further until a leaf node labeled "26" is reached, with a note "not useful".]

$$P: \sum_{i=1}^{n}|x_i-\hat{x}| \le 5 \quad G: \text{cardinality constraint}$$

**LOCAL JUMP:** Solving LPs takes too long.

**Idiot Crash:**

$$\min \; Ax \le b, \quad x \in \mathbb{Z}^p$$

$$\min \sum w_i(b_i-a'y)^+$$

**Initial/Construction:**
$$3y_1+y_2-y_3 \le 7 \to y_1 \text{ should be small}$$
$$-y_1+2y_2+y_3 \ge 9 \to y_1 \text{ should be small}$$
$$y_2+y_3+y_4 = 5$$
$$y_3-y_4+y_6 \le 8$$
$$0 \le y \le 10$$

Set $y=0$