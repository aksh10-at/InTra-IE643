Step (4) Find $\alpha x + \gamma y \le \beta$ valid for both $R_1$ and $R_2$

$\hookrightarrow$ Use $R_1, R_2 \dots$ together to get Red line.
$\hookrightarrow$ There are lots of lines like the Red line (infinite)

* Stubb 80 Mehnoova, 1999

Give the convex hull of $R_1 \cup R_2$ under the assumptions...
(i) $y$ is binary
(ii) $R_i$s are bounded
(iii) disjunctions used like $y_i=0$ or $y_i=1$

[Diagram: A red polygonal region formed by the intersection of several shaded regions, with a few labeled points inside.]

- Convex Hull is given by $(x^1,y^1) \in R_1$, $(x^2,y^2) \in R_2$
  $(x,y) = \lambda^1(x^1,y^1) + \lambda^2(x^2,y^2)$ with $\lambda^1+\lambda^2=1$, $\lambda^1\ge0$, $\lambda^2\ge0$

$$M(x^1) = \{(x_1^1,y_1^1), (x_2^1,y_2^1), (\lambda^1,\lambda^2)\}$$

Assuming, $y_1=0$ or $y_1=1$

$$\begin{aligned}
&\forall i: (x^i,y^i)\le0 \to cx \\
&\forall i: (x^i,y^i)\le0 \to cx \\
&x=\lambda^1x^1+\lambda^2x^2 \to ncx \\
&y=\lambda^1y^1+\lambda^2y^2 \to ncx \\
&\lambda^1+\lambda^2=1 \to lcx \\
&\lambda^1,\lambda^2\ge0 \to cx \\
&y_1^1=0 \qquad \{ \to cx \\
&y_1^2=1 \qquad \{ \to cx
\end{aligned}$$

Form new constraints in place of difficult one:
$$x = \bar{x}_1 + \bar{x}_2$$
$$y = \bar{y}_1 + \bar{y}_2$$
Use some trick