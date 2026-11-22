# Nature of clusters produced by K-Means

Let $K=2$. Lloyd's algorithm will produce 2 clusters with means: $\mu_1$ & $\mu_2$

What can we say about the points assigned to cluster 1?

$\to$ By the algorithm's convergence, each data point in cluster 1 is now closer to $\mu_1$ than $\mu_2$: $\|x-\mu_1\|^2 \le \|x-\mu_2\|^2$

$$= \|x\|^2 + \|\mu_1\|^2 - 2x^T\mu_1 \le \|x\|^2 + \|\mu_2\|^2 - 2x^T\mu_2$$
$$= \|\mu_2\|^2 - \|\mu_1\|^2 \ge 2x^T(\mu_2-\mu_1)$$
$$= x^T(\mu_2-\mu_1) \le \frac{\|\mu_2\|^2-\|\mu_1\|^2}{2} \quad \boxed{\forall x \text{ in cluster 1}}$$

[Diagram: A 2D scatter plot showing two clusters — yellow shaded region for "Cluster 1 region" (points closer to $\mu_1$), green shaded region for "Cluster 2 region" (points closer to $\mu_2$). A dashed line through the origin represents $x^T(\mu_2-\mu_1)=0$, with an orange arrow pointing right labeled "$x^T(\mu_2-\mu_1)$", and a blue arrow pointing left labeled "$(u_2-u_1)$".]

What happens when $K=3$?